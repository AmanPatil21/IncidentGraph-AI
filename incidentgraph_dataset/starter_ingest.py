from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

root = Path(__file__).resolve().parent
docs = []
for folder in ["incidents", "runbooks", "postmortems"]:
    for path in sorted((root / folder).glob("*.md")):
        for doc in TextLoader(str(path), encoding="utf-8").load():
            doc.metadata["source"] = str(path.relative_to(root))
            doc.metadata["document_type"] = folder
            docs.append(doc)

chunks = RecursiveCharacterTextSplitter(chunk_size=650, chunk_overlap=100).split_documents(docs)
embeddings = OllamaEmbeddings(model="nomic-embed-text")
store = Chroma.from_documents(chunks, embedding=embeddings, persist_directory=str(root / "chroma_db"))
print(f"Indexed {len(docs)} documents as {len(chunks)} chunks")
for hit in store.similarity_search("What caused INC-001?", k=3):
    print(hit.metadata.get("source"), hit.page_content[:140].replace("\n", " "))
