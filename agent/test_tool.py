from agent.tools import get_incident_details
from agent.tools import get_runbook
from agent.tools import extract_runbook_metadata
from agent.tools import find_exact_runbook
from pathlib import Path
# print(get_incident_details("inc-002")["found"])
# print(get_incident_details("INC-999")["found"])

# try:
#     get_incident_details("INC-ABC")
# except ValueError as e:
#     print("Validation passed:", e)

# root = Path(__file__).resolve().parent.parent  / "incidentgraph_dataset" / "runbooks" 

# print("Runbook directory:", root)
# print("Files found:", list(root.glob("*.md")))
# test = [
#     "DB_CONNECTION_POOL_EXHAUSTED",
#     "settlement-worker",
#     "RB-DB-001",
#     "database connection pool is exhausted"
# ]

# for query in test :
#     results = get_runbook(query)

#     print(f"\n Query : {query}") 
#     print(f"Matches :{len(results)}")

#     for result  in results :
#         print(f"source : ",result["source"])
#         print(f"content : " ,result["content"])
#         print(f"match type :",result["match_type"])
#         print("-"* 40)


# content = Path("incidentgraph_dataset/runbooks/RB-DB-001.md").read_text(encoding="utf-8")

# metadata = extract_runbook_metadata(content)

# print(metadata)
# print(repr(metadata.get("runbook_id")))


results = find_exact_runbook("RB-DB-001")

print(len(results))
print(results[0]["metadata"] if results else "No exact match")