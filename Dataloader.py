from langchain_community.document_loaders import TextLoader as TL
from langchain_text_splitters import RecursiveCharacterTextSplitter as RS , MarkdownHeaderTextSplitter as MD
from langchain_chroma import Chroma 
from langchain_ollama import OllamaEmbeddings as OE
from pathlib import Path
import shutil

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

root = Path(__file__).resolve().parent  / "incidentgraph_dataset"
def load_documents() :
    docs=[]
    # get the text 
    for folder in ["incidents" , "postmortems" ,"runbooks"] :
        for path in sorted((root/folder).glob("*.md")) :
            for doc in TL(str(path),encoding="utf-8").load():
                doc.metadata["source"] = str(path.relative_to(root))
                doc.metadata["document_type"] = folder
                docs.append(doc)

    # split them into chunk
    # md_text_splitter = MD(headers_to_split_on = headers_to_split_on , strip_headers= False)
    # chunks= []
    # for doc in docs :
    #     md_chunk = md_text_splitter.split_text(doc.page_content)
    #     for chunk in  md_chunk:
    #         chunk.metadata.update(doc.metadata)
    #     chunks.extend(md_chunk)
    # text_splitter = RS(chunk_size = 800, chunk_overlap = 100)
    # chunks = text_splitter.split_documents(chunks)

    text_splitter = RS(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(docs)
    # convert to embeddings
    embeddings = OE(model="nomic-embed-text")
    # store in vector database embedding=embeddings
    db_path = root / "chroma_db"
    if db_path.exists():
        shutil.rmtree(db_path)
    store = Chroma.from_documents(chunks, embedding = embeddings, persist_directory= (str(root/"chroma_db")))
    print(f"Indexed {len(docs)} documents as {len(chunks)} chunks")
    for hit in store.similarity_search("What caused INC-001?", k=3):
        print(hit.metadata, hit.page_content)


load_documents()
