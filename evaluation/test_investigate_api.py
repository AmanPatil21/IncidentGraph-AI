from fastapi.testclient import TestClient
from unittest.mock import patch , MagicMock
from main import app
from agent.gemini_agent import investigate, INVESTIGATION_PROMPT , validate_citations
from langchain_core.messages import SystemMessage, AIMessage
from langchain_google_genai.chat_models import GoogleRateLimitError, GoogleAPIError

client = TestClient(app)

def test_investigate_success() :
    mock_result = {
        "answer": "INC-001 was caused by a database connection leak.",
        "trace": [
            {
                "step": 1,
                "tool": "get_incident_details",
                "arguments": {"incident_id": "INC-001"},
                "status": "success"
            }
        ],
        "status": "completed"
    }

    with patch("main.investigate" , return_value= mock_result) as mock_agent:
        response = client.post("/investigate" , json={"question" : "Investigate INC--001", "max_steps" : 3})

    assert response.status_code ==200
    assert response.json() == mock_result
    mock_agent.assert_called_once_with(question="Investigate INC--001", max_steps=3)

def test_incestigate_invalid_request() :
    with patch("main.investigate" ) as mock_agent :
        response = client.post("/investigate" , json = {"question" :"" , "max_steps" :3})

    assert response.status_code ==422
    mock_agent.assert_not_called()


def test_investigate_rate_limit() :
    with patch("main.investigate" , side_effect= GoogleRateLimitError("Quota Exceeded")) as mock_agent :
        response = client.post("/investigate" , json = {"question" : "Investigate INC-001" , "max_steps" :3})

    assert response.status_code==429
    assert "quota" in response.json()["detail"].lower()
    mock_agent.assert_called_once_with(question="Investigate INC-001", max_steps=3)



def test_investigation_system_prompt() :
    mock_response = AIMessage(content="Investigation completed.")
    with patch("agent.gemini_agent.llm_with_tools") as mock_llm :
        mock_llm.invoke.return_value = mock_response

        result = investigate("Investigate INC-001")
        messages = mock_llm.invoke.call_args.args[0]

    assert isinstance(messages[0], SystemMessage)
    assert messages[0].content == INVESTIGATION_PROMPT
    assert result["status"] == "completed"
    assert result["answer"] == "Investigation completed."

def test_investigate_service_unavailable():
    error = GoogleAPIError(
        "503 UNAVAILABLE",
        {"error": {"code": 503, "status": "UNAVAILABLE"}}
    )
    with patch("main.investigate", side_effect=error) as mock_agent:
        response = client.post("/investigate", json={"question": "Investigate INC-002", "max_steps": 3})

    assert response.status_code == 503
    assert "temporarily unavailable" in response.json()["detail"].lower()
    mock_agent.assert_called_once_with(question="Investigate INC-002", max_steps=3)

def test_investigation_tool_budget() :
    tool_requests = AIMessage(
        content="" ,
        tool_calls =[
            {
                "name" : "get_incident_details",
                "args" : {"incident_id": "INC-001"},
                "id" : f"call_{i}"
            }

            for i in range(6)
        ]
    )

    response = AIMessage(content="Investigation completed.")

    fake_tool = MagicMock()
    fake_tool.invoke.return_value = {
        "incident_id": "INC-001",
        "found": True,
        "source": "incidents/INC-001.md"
    }

    with patch("agent.gemini_agent.llm_with_tools") as mock_llm, patch.dict("agent.gemini_agent.tool_map" , {"get_incident_details": fake_tool}) :
        mock_llm.invoke.side_effect=[tool_requests, response]
        result = investigate("Investigate INC_001" , max_steps=2)


    assert fake_tool.invoke.call_count==5
    assert len(result["trace"]) == 6
    assert sum(item["status"]=="blocked" for item in result["trace"]) == 1
    assert result["status"] == "completed"

def test_investigation_source_collection():
    tool_requests = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "get_incident_details",
                "args": {"incident_id": "INC-001"},
                "id": "call_001"
            },
            {
                "name": "search_incident_documents",
                "args": {"query": "INC-001 root cause"},
                "id": "call_002"
            }
        ]
    )

    final_response = AIMessage(content="Investigation completed.")

    fake_incident_tool = MagicMock()
    fake_incident_tool.invoke.return_value = {
        "incident_id": "INC-001",
        "found": True,
        "source": "incidents/INC-001.md",
        "content": "Database connection leak."
    }

    fake_search_tool = MagicMock()
    fake_search_tool.invoke.return_value = [
        {
            "source": "postmortems/PM-001.md",
            "content": "Root cause analysis."
        },
        {
            "source": "incidents/INC-001.md",
            "content": "Incident timeline."
        }
    ]

    fake_tools = {
        "get_incident_details": fake_incident_tool,
        "search_incident_documents": fake_search_tool
    }

    with patch("agent.gemini_agent.llm_with_tools") as mock_llm, patch.dict("agent.gemini_agent.tool_map", fake_tools):
        mock_llm.invoke.side_effect = [tool_requests, final_response]
        result = investigate("Investigate INC-001", max_steps=2)

    assert result["status"] == "completed"
    assert result["retrieved_sources"] == [
        "incidents/INC-001.md",
        "postmortems/PM-001.md"
    ]
    assert len(result["trace"]) == 2
    assert all(item["status"] == "success" for item in result["trace"])
    fake_incident_tool.invoke.assert_called_once_with({"incident_id": "INC-001"})
    fake_search_tool.invoke.assert_called_once_with({"query": "INC-001 root cause"})



def test_citation_validation():
    retrieved_sources = {
        "incidents/INC-001.md",
        "postmortems/PM-001.md"
    }

    valid = validate_citations(
        "Root cause: connection leak. Source: incidents/INC-001.md",
        retrieved_sources
    )
    assert valid["unsupported_citations"] == []
    assert valid["missing_citations"] is False

    invalid = validate_citations(
        "Source: incidents/INC-007.md",
        retrieved_sources
    )
    assert invalid["unsupported_citations"] == ["incidents/INC-007.md"]

    missing = validate_citations(
        "The incident was caused by a connection leak.",
        retrieved_sources
    )
    assert missing["missing_citations"] is True


def test_investigation_citation_integration() :
    tool_request = AIMessage(
        content="",
        tool_calls=[
            {
                "name" : "get_incident_details" ,
                "args" : {"incident_id" : "INC-001"},
                "id" : "call_001"
            }
        ]
    )

    final_response = AIMessage(content = "Root cause : connection leak. Source : incidents/INC-007.md")

    fake_tool = MagicMock()
    fake_tool.invoke.return_value ={
        "incident_id" : "INC-001" ,
        "found" : True,
        "source" : "incidents/INC-001.md",
        "content" : "Database connection leak."
    }

    with patch("agent.gemini_agent.llm_with_tools") as mock_llm , patch.dict("agent.gemini_agent.tool_map" , {"get_incident_details" : fake_tool}) :
        mock_llm.invoke.side_effect= [tool_request, final_response]
        result = investigate("Investigate INC-001" , max_steps=2)

    assert result["status"] == "completed"
    assert result["retrieved_sources"] == ["incidents/INC-001.md"]
    assert result["citation_validation"]["cited_sources"] == ["incidents/INC-007.md"]
    assert result["citation_validation"]["unsupported_citations"] == ["incidents/INC-007.md"]
    assert result["citation_validation"]["missing_citations"] is False