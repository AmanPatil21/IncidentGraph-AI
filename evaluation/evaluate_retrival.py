import json 
import csv 
from pathlib import Path
from Retriever import retrive_context
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASET_PATH = (PROJECT_ROOT/ "incidentgraph_dataset/evaluation/qa_ground_truth.jsonl") 

OUTPUT_PATH  = PROJECT_ROOT / "evaluation" / "retrival_results.csv" 


def normalize_source(source) :
    return str(source).replace("\\" , "/").lower().strip()

def evaluate() :
    results = []

    with open(normalize_source(DATASET_PATH), "r" , encoding= "utf-8") as file :
        questions = [
            json.loads(line)
            for line in file
            if line.strip()
        ]
    print(f"Questnions : {questions}")

    for index , item in enumerate(questions , start= 1) :
        question = item["question"]
        expected = [
            normalize_source(source) 
            for source in item["expected_sources"]
        ]

        documents = retrive_context(question)
        retrived = [
            normalize_source(doc.metadata.get("source",""))
            for doc in documents[:3]
        ]

        def source_matches(actual, expected) :
            return (
                actual== expected or actual.endswith("/"+expected)
            )
        matched_retrived = {
            source 
            for source in expected 
            if any(source_matches(actual, source)  for actual in retrived)
        }

        print(f"Matched Retrived : {matched_retrived}")

        print("-" for i in range(0,20))

        hit = int( len(matched_retrived) >0)

        recall = (
            len(matched_retrived) / len(expected)
            if expected else 0.0
        )

        reciprocal_rank = 0.0

        for rank, actual in enumerate(retrived , start=1 ):
            if any(source_matches(actual, source) for source in expected) :
                reciprocal_rank = 1.0/rank
                break

        results.append({
            "question" : question ,
            "incident_id" : item["incident_id"] ,
            "expected_sources" : ";".join(sorted(expected)),
            "retrived_sources" : ";".join(retrived),
            "hit_at_3": hit,
            "recall_at_3" : recall ,
            "mrr_at_3" : reciprocal_rank,
        })

        print(
            f"[{index}/{len(questions)}] "
            f"Hit@3={hit} | "
            f"Recall@3={recall:.2f} | "
            f"MRR@3={reciprocal_rank:.2f}"
        )

    if not results :
        raise ValueError(" No evaluation question found")

    OUTPUT_PATH.parent.mkdir(parents= True, exist_ok= True)

    with open(OUTPUT_PATH, "w" , newline="" , encoding="utf-8") as file :
        writer = csv.DictWriter(file, fieldnames= results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print("\n------------------Retrival Evaluation---------------")
    print(f"Questions : {len(results)}")

    for metric in ["hit_at_3" , "recall_at_3" , "mrr_at_3"] :
        average = sum(row[metric] for row in results) / len(results)
        print(f"{metric} : {average:.4f}")

    print(f"\nResults saved to : {OUTPUT_PATH}")




if __name__ == "__main__":
    evaluate()
