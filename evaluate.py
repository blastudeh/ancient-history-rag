"""Reproducible retrieval evaluation and optional live RAG/baseline runs."""
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
import rag


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--live', action='store_true', help='Actually call Ollama for RAG AND baseline')
    p.add_argument('--model', default=rag.MODEL)
    args = p.parse_args()
    index = rag.load_index()
    retriever = rag.Retriever(index['chunks'])
    questions = json.loads((rag.ROOT / 'data/questions.json').read_text(encoding='utf-8'))
    rows = []
    for q in questions:
        hits = retriever.search(q['question'], 4)
        found = {h['source_id'] for h in hits}
        expected = set(q['expected_sources'])
        recall = len(found & expected) / len(expected) if q['answerable'] and expected else None
        row = {**q, 'retrieved_ids': [h['id'] for h in hits], 'source_recall_at_4': recall,
               'human_correctness': None, 'human_citation_support': None,
               'human_refusal_correct': None}
        if args.live:
            for mode in ('rag', 'baseline'):
                try:
                    row[mode] = rag.ask(q['question'], mode, args.model, index=index)
                except RuntimeError as e:
                    row[mode] = {'error': str(e), 'status': 'failed; no result fabricated'}
        rows.append(row)
        print(q['id'], 'recall@4:', recall, 'retrieved:', ', '.join(row['retrieved_ids']))
    scores = [r['source_recall_at_4'] for r in rows if r['source_recall_at_4'] is not None]
    output = {'timestamp_utc': datetime.now(timezone.utc).isoformat(),
              'corpus_sha256': index['source_sha256'], 'live_requested': args.live,
              'mean_source_recall_at_4': sum(scores) / len(scores),
              'answerable_questions': len(scores), 'total_questions': len(rows),
              'note': 'Small development set, not an independent benchmark. Retrieval recall is NOT answer accuracy.',
              'rows': rows}
    target = rag.ROOT / 'results' / ('live_evaluation.json' if args.live else 'retrieval_evaluation.json')
    rag.save_result(output, target)
    print('Mean source recall@4:', output['mean_source_recall_at_4'])
    print('Saved:', target)
    if args.live:
        failed = sum('error' in r[m] for r in rows for m in ('rag', 'baseline'))
        print('Generation failures:', failed, '| Review successful answers manually.')
        return int(failed > 0)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
