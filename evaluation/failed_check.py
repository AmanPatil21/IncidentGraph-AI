# # from Retriver import retrive_context

# # question = "What caused INC-010?"

# # docs = retrive_context(question)

# # print("Documents returned:", len(docs))

# # for doc in docs:
# #     print("Source:", doc.metadata.get("source"))
# #     print("Contains INC-010:", "INC-010" in doc.page_content.upper())

# import csv 
# from pathlib import Path
# from Retriver import store

# PROJECT_PATH = Path(__file__).resolve().parents[0]
# print(f"{PROJECT_PATH}")
# OUTPUT_PATH  = PROJECT_PATH/"answer_result.csv"
# with open(OUTPUT_PATH, "r" , encoding= "utf-8") as file:
#     rows = list(csv.DictReader(file))

# # for i, row in enumerate(rows[26:31], start=1) :
# #     print(f"\n{'=' *60}")
# #     print(f"Question{i} : {row['question']}")
# #     print(f"Expected Answer : {row['expected_answer']}")
# #     print(f"Generated : {row['generated_answer']}")
# #     print(f"Source : {row['retrieved_sources']}")

# # for i, doc in enumerate(store.similarity_search("database connection pool" , k=3)) :
# #     print(f"\n Documets :{i}")
# #     print(f"Metadata : {doc.metadata}")
# #     print(f"COntent: {doc.page_content[:150]}")

# # for row in rows:
# #     if "runbook" in row["question"].lower():
# #         print("\n" + "=" * 60)
# #         print("Question:", row["question"])
# #         print("Expected:", row["expected_answer"])
# #         print("Generated:", row["generated_answer"])
# #         print("Sources:", row["retrieved_sources"])

# # for row in rows:
# #     if row["incident_id"] == "INC-008" and "job failed" in row["question"].lower():
# #         print("Question:", row["question"])
# #         print("Expected:", row["expected_answer"])
# #         print("Generated:", row["generated_answer"])
# #         print("Sources:", row["retrieved_sources"])

# # from Retriver import retrive_context, format_context

# # from Retriver import chain

# # question = "What job failed in INC-008 and what was the error code?"

# # documents = retrive_context(question)

# # incident_doc = next(
# #     doc for doc in documents
# #     if doc.metadata.get("document_type") == "incidents"
# # )

# # question = (
# #     "According to the incident document, what are the values "
# #     "of the 'Primary job' and 'Error code' fields?"
# # )

# # response = chain.invoke({
# #     "context": format_context([incident_doc]),
# #     "question": question
# # })

# # print(response)

# from Retriever import ask_question

# response = ask_question(
#     question="What job failed in INC-008 and what was the error code?",
#     session_id="test-primary-job-001"
# )

# print("Answer:", response["answer"])
# print("Sources:", response["source"])


import json
import time
from agent.gemini_agent import investigate

start = time.perf_counter()

result = investigate(
    question="Investigate INC-002. Identify the root cause, impact, and supporting documents.",
    max_steps =3
)


elapsed = time.perf_counter() - start

print("Status:" , result["status"])
print("Latency:" , round(elapsed, 2) , "seconds")
print("ANswer:", result["answer"])
print("Trace:" , json.dumps(result["trace"], indent=2))