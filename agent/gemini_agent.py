import os 
import re
import json
from langchain_core.tools import StructuredTool
from langchain_core.messages import SystemMessage
from agent.tools import get_incident_details,search_incident_documents , get_runbook
from dotenv  import load_dotenv
from langchain_google_genai  import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage , ToolMessage
incident_tool = StructuredTool.from_function(
    func = get_incident_details,
    name="get_incident_details" ,
    description = " Retrieve the full incident report using an exact incident ID such as INC-001..."
)


runbook_tool = StructuredTool.from_function(
    func = get_runbook,
    description = "Find operational runbook using runbook id . service name ,error trigger , or natural-language problem description.",
    name= "get_runbook"
)

search_tool = StructuredTool.from_function(
    func = search_incident_documents,
    name="search_incident_documents",
    description = "Search incident report, postmortems and runbook using semantic similarity. Useful for investigating symptoms, cause and related incidents."
)


tools =[incident_tool, runbook_tool, search_tool]
load_dotenv()

INVESTIGATION_PROMPT = """
You are a readu-only incieent investigation assistant.

Rules:
1. Use the available tools to investigate the users question.
2. Base factual conclusions only on retrieved incident reports, postmortems, and runbooks.
3. Cite the source document path for every important factual claim.
4. Distingguish confirmed root causes from hypotheses.
5. Distinguish actions actually performed from actions recommended by runbooks.
6. If evidence is missing or a tool fails, explicitly acknowegde the limitation.
7. Never claim to have restarted services, deployed fixes, or modified infrastructure.
8. Do not invent incident details , metrics or source citations.
"""
llm = ChatGoogleGenerativeAI(
    model = os.getenv("GEMINI_MODEL" , "gemini-3.8-flash"),
    temperature= 0,
)


llm_with_tools = llm.bind_tools(tools)
tool_map = {
    tool.name : tool for tool in tools
}




def extract_answer(response) -> str :
    if isinstance(response.content , str) : 
        return response.content
    return "\n".join(
        block["text"]
        for block in response.content
        if isinstance(block, dict) and block.get("type") == "text"
    )

def validate_citations(answer: str, retrieved_sources: set) -> dict:
    pattern = r"(?:incidents|postmortems|runbooks)/[\w-]+\.md"

    cited_sources = set(re.findall(pattern, answer))

    return {
        "cited_sources": sorted(cited_sources),
        "unsupported_citations": sorted(cited_sources - retrieved_sources),
        "missing_citations": len(cited_sources) == 0
    }

def investigate(question: str , max_steps : int =3) ->dict :
    messages = [
        SystemMessage(content= INVESTIGATION_PROMPT ),
        HumanMessage(content=question)]
    trace = []
    retrieved_sources = set()
    tool_calls_used = 0
    max_tool_calls = 5
    for step in range(max_steps) :
        response = llm_with_tools.invoke(messages)
        messages.append(response) 
        if not response.tool_calls :
            answer = extract_answer(response)
            citation_validation = validate_citations(answer, retrieved_sources)
            return {
                "answer" : answer ,
                "trace" : trace ,
                "citation_validation": citation_validation,
                "retrieved_sources": sorted(retrieved_sources),
                "status" : "completed"
            }
        

        for tool in response.tool_calls :
            tool_name = tool["name"]
            tool_args = tool["args"]

            selected_tool = tool_map.get(tool_name)

            if tool_calls_used >= max_tool_calls:
                result = {"error": "Tool execution limit reached"}
                status = "blocked"
            else:
                try:
                    if selected_tool is None:
                        raise ValueError(f"Unknown tool: {tool_name}")

                    tool_calls_used += 1
                    result = selected_tool.invoke(tool_args)
                    status = "success"
                except Exception as error:
                    result = {"error": str(error)}
                    status = "error"
            trace.append({
                "step" :step+1 ,
                "tool" :tool_name,
                "arguments" : tool_args ,
                "status" : status
            })

            if status=="success" :
                documents = result if isinstance(result, list)  else [result]

                for document in documents:
                    if isinstance(document, dict) and document.get("source"):
                        retrieved_sources.add(document["source"])

            messages.append(ToolMessage(content=json.dumps(result), tool_call_id=tool["id"]))

    final_llm = llm 
    final_response = final_llm.invoke(
        messages + [HumanMessage(content="The investigation tool-call limit has been reached. Summarize the evidence collected so far, cite document sources, and clearly identify any missing information. DO no invent facts.")]
    )
    answer = extract_answer(response)
    citation_validation = validate_citations(answer, retrieved_sources)


    return {
        "answer" : answer,
        "trace" : trace ,
        "citation_validation": citation_validation,
        "retrieved_sources": sorted(retrieved_sources),
        "status" : "completed_with_limit"
    }   



if __name__ == "__main__" :

    result  = investigate("Investigate Incident INC-001 and explain its root cause.")

    print(f"status :{result['status']}")
    print(f"Answer : {result['answer']}")
    print(f"Trace :{json.dumps(result['trace'], indent=2)}")
    # messages = [HumanMessage(content="Investigate incident INC-001 and explain its root cause.")]
    # response = llm_with_tools.invoke(messages)
    # print("-------------------------------dfsdfsd------------")
    # print(response) 
    # print("-"*60)
    # messages.append(response)
    # for tool in response.tool_calls :
    #     tool_name = tool["name"]
    #     tool_args = tool["args"]
    #     selected_tool = tool_map.get(tool_name)

    #     if not selected_tool :
    #         print(f"unknown tool : {tool_name}")
    #         continue
    #     result = selected_tool.invoke(tool_args)
    #     messages.append(ToolMessage(conten=json.dumps(result) , tool_call_id = tool["id"]))

    # fina_response  = llm_with_tools.invoke(messages)

    # print("-"*40)
    # print(f"reponse :{fina_response.content}")
    # print(f"Additional tool calls: {fina_response.tool_calls}")