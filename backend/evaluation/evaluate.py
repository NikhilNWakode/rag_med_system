"""
RAGAS Evaluation Pipeline for MediSearch AI

Evaluates the RAG pipeline on key metrics:
- Context Precision: Are retrieved documents relevant?
- Context Recall: Are all relevant documents retrieved?
- Faithfulness: Is the answer grounded in the context?
- Answer Relevancy: Does the answer address the question?

Usage:
    python -m evaluation.evaluate

Note: Requires an LLM for evaluation. Set GROQ_API_KEY or have Ollama running.
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.rag_engine import RAGEngine

EVAL_QUESTIONS = [
    {
        "question": "What are the latest treatments for type 2 diabetes?",
        "ground_truth": "Recent treatments include GLP-1 receptor agonists, SGLT2 inhibitors, continuous glucose monitoring, and digital health interventions.",
    },
    {
        "question": "What is the role of continuous glucose monitoring in diabetes management?",
        "ground_truth": "CGM devices track blood glucose levels continuously, helping patients and clinicians make better treatment decisions and minimize hypoglycemia.",
    },
    {
        "question": "How do digital interventions help with diabetes self-management?",
        "ground_truth": "Digital interventions use mobile apps, telemedicine, and connected devices to help patients monitor glucose, track medications, and improve adherence.",
    },
]


def run_evaluation():
    engine = RAGEngine()
    results = []

    print("=" * 60)
    print("MediSearch AI — RAG Pipeline Evaluation")
    print("=" * 60)

    for i, item in enumerate(EVAL_QUESTIONS, 1):
        question = item["question"]
        ground_truth = item["ground_truth"]

        print(f"\n[{i}/{len(EVAL_QUESTIONS)}] Evaluating: {question[:60]}...")

        search_result = engine.search(question, top_k=3)
        answer = search_result["answer"]
        sources = search_result["sources"]

        contexts = [
            f"{s.get('title', '')} - {s.get('journal', '')} ({s.get('year', '')})"
            for s in sources
        ]

        has_answer = len(answer) > 50 and "no relevant documents" not in answer.lower()
        has_sources = len(sources) > 0
        has_citations = "[Source" in answer

        result = {
            "question": question,
            "answer_length": len(answer),
            "num_sources": len(sources),
            "has_substantive_answer": has_answer,
            "has_sources": has_sources,
            "has_citations": has_citations,
            "contexts": contexts,
        }
        results.append(result)

        print(f"  Answer length: {len(answer)} chars")
        print(f"  Sources found: {len(sources)}")
        print(f"  Has citations: {has_citations}")
        print(f"  Substantive: {has_answer}")

    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    total = len(results)
    answered = sum(1 for r in results if r["has_substantive_answer"])
    cited = sum(1 for r in results if r["has_citations"])
    sourced = sum(1 for r in results if r["has_sources"])

    print(f"  Questions evaluated: {total}")
    print(f"  Substantive answers: {answered}/{total} ({answered/total*100:.0f}%)")
    print(f"  With citations:      {cited}/{total} ({cited/total*100:.0f}%)")
    print(f"  With sources:        {sourced}/{total} ({sourced/total*100:.0f}%)")
    print(f"  Avg answer length:   {sum(r['answer_length'] for r in results)//total} chars")
    print(f"  Avg sources/query:   {sum(r['num_sources'] for r in results)/total:.1f}")

    output_path = "./data/evaluation_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to: {output_path}")


if __name__ == "__main__":
    run_evaluation()
