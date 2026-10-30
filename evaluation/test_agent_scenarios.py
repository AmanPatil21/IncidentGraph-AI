
import json
from unittest.mock import MagicMock, patch
from langchain_core.messages import AIMessage, ToolMessage
from agent.gemini_agent import investigate


def tool_request(name, args, call_id):
    return AIMessage(content="", tool_calls=[
        {"name": name, "args": args, "id": call_id}
    ])


def test_known_incident():
    request = tool_request("get_incident_details", {"incident_id": "INC-001"}, "call_1")
    final = AIMessage(content="Connection leak. Source: incidents/INC-001.md")

    tool = MagicMock()
    tool.invoke.return_value = {
        "found": True,
        "source": "incidents/INC-001.md",
        "content": "Root cause: connection leak"
    }

    with patch("agent.gemini_agent.llm_with_tools") as llm, patch.dict("agent.gemini_agent.tool_map", {"get_incident_details": tool}):
        llm.invoke.side_effect = [request, final]
        result = investigate("Investigate INC-001", max_steps=2)

    assert result["status"] == "completed"
    assert result["retrieved_sources"] == ["incidents/INC-001.md"]
    assert result["citation_validation"]["unsupported_citations"] == []
    tool.invoke.assert_called_once()


def test_unknown_incident():
    request = tool_request("get_incident_details", {"incident_id": "INC-999"}, "call_1")
    final = AIMessage(content="INC-999 was not found. Its root cause cannot be determined.")

    tool = MagicMock()
    tool.invoke.return_value = {"incident_id": "INC-999", "found": False}

    with patch("agent.gemini_agent.llm_with_tools") as llm, patch.dict("agent.gemini_agent.tool_map", {"get_incident_details": tool}):
        llm.invoke.side_effect = [request, final]
        result = investigate("Investigate INC-999", max_steps=2)

    assert result["retrieved_sources"] == []
    assert "not found" in result["answer"].lower()
    assert result["citation_validation"]["missing_citations"] is True


def test_tool_failure():
    request = tool_request("search_incident_documents", {"query": "INC-001"}, "call_1")
    final = AIMessage(content="Retrieval failed. I cannot verify the root cause.")

    tool = MagicMock()
    tool.invoke.side_effect = RuntimeError("Vector database unavailable")

    with patch("agent.gemini_agent.llm_with_tools") as llm, patch.dict("agent.gemini_agent.tool_map", {"search_incident_documents": tool}):
        llm.invoke.side_effect = [request, final]
        result = investigate("Investigate INC-001", max_steps=2)
        messages = llm.invoke.call_args_list[1].args[0]

    tool_messages = [m for m in messages if isinstance(m, ToolMessage)]

    assert result["trace"][0]["status"] == "error"
    assert "Vector database unavailable" in tool_messages[0].content
    assert "cannot verify" in result["answer"].lower()


def test_multiple_related_documents():
    request = AIMessage(content="", tool_calls=[
        {"name": "get_incident_details", "args": {"incident_id": "INC-001"}, "id": "call_1"},
        {"name": "get_runbook", "args": {"query": "database connection"}, "id": "call_2"}
    ])
    final = AIMessage(content="Evidence: incidents/INC-001.md. Recommended procedure: runbooks/RB-DB-001.md")

    incident = MagicMock()
    incident.invoke.return_value = {"source": "incidents/INC-001.md", "content": "Connection leak"}

    runbook = MagicMock()
    runbook.invoke.return_value = [{"source": "runbooks/RB-DB-001.md", "content": "Recovery procedure"}]

    fake_tools = {"get_incident_details": incident, "get_runbook": runbook}

    with patch("agent.gemini_agent.llm_with_tools") as llm, patch.dict("agent.gemini_agent.tool_map", fake_tools):
        llm.invoke.side_effect = [request, final]
        result = investigate("Investigate INC-001 and recommend recovery", max_steps=2)

    assert len(result["retrieved_sources"]) == 2
    assert len(result["trace"]) == 2
    assert result["citation_validation"]["unsupported_citations"] == []


def test_investigation_step_limit():
    request = tool_request("get_incident_details", {"incident_id": "INC-001"}, "call_1")

    tool = MagicMock()
    tool.invoke.return_value = {"source": "incidents/INC-001.md", "content": "Connection leak"}

    summary = AIMessage(content="Based on incidents/INC-001.md, a connection leak occurred.")

    with patch("agent.gemini_agent.llm_with_tools") as llm, patch("agent.gemini_agent.llm") as base_llm, patch.dict("agent.gemini_agent.tool_map", {"get_incident_details": tool}):
        llm.invoke.return_value = request
        base_llm.invoke.return_value = summary
        result = investigate("Investigate INC-001", max_steps=1)

    assert result["status"] == "completed_with_limit"
    assert len(result["trace"]) == 1
    assert result["retrieved_sources"] == ["incidents/INC-001.md"]
    base_llm.invoke.assert_called_once()
