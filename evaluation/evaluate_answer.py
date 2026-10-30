import csv
import json
import time
from pathlib import Path
from Retriever import ask_question

PROJECT_PATH = Path(__file__).resolve().parents[1]
DATASET_PATH = (PROJECT_PATH /"incidentgraph_dataset"/"evaluation"/"qa_ground_truth.jsonl")

OUTPUT_PATH = PROJECT_PATH/"evaluation/answer_result.csv"

def evaluate_answer() :
    with open(DATASET_PATH , "r" , encoding="utf-8") as file :
        questions = [
            json.loads(line) 
            for line in file 
            if line.strip()
        ]

    results = []


    for index , item in enumerate(questions , start=1) :
        question = item["question"]

        session_id = f"eval-{index}"
        start = time.perf_counter()

        try :
            response = ask_question(question = question , session_id =session_id)
            generated_answer = response["answer"]
            retrieved_sources = response["source"]
            search_question = response["search_question"]
            error =""
        except Exception as exc :
            generated_answer = ""
            retrieved_sources = []
            search_question= ""
            error= str(exc)

        latency = time.perf_counter()-start

        results.append({
            "incident_id": item["incident_id"],
            "question": question,
            "expected_answer": item["expected_answer"],
            "generated_answer": generated_answer,
            "expected_sources": "; ".join(item["expected_sources"]),
            "retrieved_sources": "; ".join(retrieved_sources),
            "search_question": search_question,
            "latency_seconds": round(latency, 2),
            "error": error,
            "correctness": "",
            "faithfulness": ""
        })


        print(
             f"[{index}/{len(questions)}] "
            f"{item['incident_id']} | "
            f"{latency:.2f}s | "
            f"{'ERROR' + error  if error else 'DONE'}"
        )

    OUTPUT_PATH.parent.mkdir(parents = True , exist_ok= True)

    with open(OUTPUT_PATH , "w" , newline="" , encoding= "utf-8")  as file:
        writer = csv.DictWriter(
            file, 
            fieldnames = results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

    successful = [ row for row in results if not row["error"]]
    print("\n---------- ANSWER EVALUATION ----------")
    print(f"Total questions: {len(results)}")
    print(f"Successful generations: {len(successful)}")
    print(f"Errors: {len(results) - len(successful)}")

    if successful :
        average_latency = sum(row["latency_seconds"] for row in successful)/len(successful)
        print(f"Average latency :{average_latency:.2f}s")
    print(f"Results saved to :{OUTPUT_PATH}")

if __name__ == "__main__" :
    evaluate_answer()
