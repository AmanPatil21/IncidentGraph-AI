from Retriever import retrive_context 
import re
from pathlib import Path



def search_incident_documents(query:str) -> list[dict] :
    if not query or not query.strip() :
        raise ValueError("Search Query cannot be empty")
    documents = retrive_context(query.strip())
    results = []
    for doc in documents :
        results.append({
            "source" : doc.metadata.get("source", "unknown"),
            "document_type" : doc.metadata.get("document_type" , "unknown"),
            "content" : doc.page_content
        })
    return results


def get_incident_details(incident_id: str) -> dict :
    incident_id = incident_id.strip().upper()
    root = Path(__file__).resolve().parent.parent
    if not re.fullmatch(r"INC-\d+" , incident_id) :
        raise ValueError("Invalide incident id format") 
    root = Path(__file__).resolve().parent.parent
    incident_path = root / f"incidentgraph_dataset/incidents/{incident_id}.md"
    if not incident_path.is_file() :
        return {
            "incident_id" : incident_id ,
            "found" :  False,
            "content" : None ,
            "source" : None
        }
    content = incident_path.read_text(encoding= "utf-8")
    return {
        "incident_id" : incident_id,
        "found" : True,
        "content" : content ,
        "source" : f"incidents/{incident_id}.md"
    }


def extract_runbook_metadata(content : str) -> dict :
    metadata ={} 
    for line in content.splitlines() :
        if line.startswith("Service") :
            metadata["service"]= line.split(":" , 1)[1].strip()
        elif line.startswith("Trigger") :
            metadata["trigger"] = line.split(":", 1)[1].strip()
        elif line.startswith("# Runbook "):
            metadata["runbook_id"] = line.split(":", 1)[0].replace("# Runbook ", "").strip()
    return metadata


def find_exact_runbook(query:str) -> list[dict] :
    root = Path(__file__).resolve().parent.parent  / "incidentgraph_dataset" / "runbooks" 
    results = []
    normalized_query = query.strip().casefold()

    for path in sorted(root.glob("*.md")) :
        content = path.read_text(encoding="utf-8")
        metadata = extract_runbook_metadata(content)


        if any(normalized_query == field.casefold() for field in metadata.values()) :
            results.append({
                "source" : f"runbooks/{path.name}",
                "content" : content ,
                "metadata" : metadata,
                "match_type" :"exact"
            })
    return results


def get_runbook(query:str) -> list[dict] :
    if not query or not query.strip() :
        raise ValueError("Runbook query cannot be empty") 
    query = query.strip()
    exact_results = find_exact_runbook(query)
    if exact_results :
        return exact_results
    search_query = f"runbook {query}" 
    documents = retrive_context(search_query)
    results = []
    for doc in documents :
        results.append({
            "source" : doc.metadata.get("source" ,"unknow"),
            "content" : doc.page_content ,
            "metadat" : doc.metadata,
            "match_type" : "semantic"
        })
    return results


