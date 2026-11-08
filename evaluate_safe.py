"""Reproducible retrieval evaluation and optional live RAG/baseline runs."""
import argparse
import json
import time
from pathlib import Path
from datetime import datetime, timezone
import rag


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--live', action='store_true', help='Actually call Ollama for RAG AND baseline')
    p.add_argument('--model', default=rag.MODEL)
    p.add_argument('--mode', choices=['rag', 'baseline', 'both'], default='both')
    p.add_argument('--question', help='Run one question ID, such as Q08')
    p.add_argument('--limit', type=int, help='Maximum number of questions')
    p.add_argument('--output', default='results/evaluation_checkpoint.json')
    args = p.parse_args()
    if args.limit is not None and args.limit < 1:
        p.error('--limit must be positive')
    index = rag.load_index()
    retriever = rag.Retriever(index['chunks'])
    questions = json.loads((rag.ROOT / 'data/questions.json').read_text(encoding='utf-8'))
    if args.question:
        questions = [q for q in questions if q['id'] == args.question]
        if not questions:
            p.error('Question ID not found')
    if args.limit:
        questions = questions[:args.limit]
    modes = ('rag', 'baseline') if args.mode == 'both' else (args.mode,)
    rows = []
    target = Path(args.output)
    if not target.is_absolute():
        target = rag.ROOT / target
    def checkpoint(complete=False):
        scores = [r['source_recall_at_4'] for r in rows if r['source_recall_at_4'] is not None]
        data = {
            'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'corpus_sha256': index['source_sha256'],
            'live_requested': args.live, 'model': args.model,
            'modes': list(modes), 'complete': complete,
            'selected_question_ids': [q['id'] for q in questions],
            'mean_source_recall_at_4': sum(scores)/len(scores) if scores else None,
            'answerable_questions': len(scores), 'total_questions': len(rows),
            'note': 'Selected development questions only. Retrieval recall is NOT answer accuracy. Pending modes are not successes.',
            'rows': rows,
        }
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(target.suffix + '.tmp')
        temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
        temporary.replace(target)
    checkpoint()

    for q in questions:
        hits = retriever.search(q['question'], 4)
        found = {h['source_id'] for h in hits}
        expected = set(q['expected_sources'])
        recall = len(found & expected) / len(expected) if q['answerable'] and expected else None
        row = {**q, 'retrieved_ids': [h['id'] for h in hits], 'source_recall_at_4': recall,
               'human_correctness': None, 'human_citation_support': None,
               'human_refusal_correct': None}
        rows.append(row)
        checkpoint()
        print(q['id'], q['question'], flush=True)
        if args.live:
            for mode in modes:
                print('  Starting', mode, '(Ctrl+C stops; earlier answers are saved)', flush=True)
                started = time.monotonic()
                try:
                    row[mode] = rag.ask(q['question'], mode, args.model, index=index)
                except KeyboardInterrupt:
                    checkpoint()
                    print('Stopped. Partial results saved:', target, flush=True)
                    return 130
                except RuntimeError as e:
                    row[mode] = {'error': str(e), 'status': 'failed; no result fabricated'}
                row[mode]['elapsed_seconds'] = round(time.monotonic() - started, 3)
                checkpoint()
                print('  Finished', mode, 'ERROR' if 'error' in row[mode] else 'OK', row[mode]['elapsed_seconds'], 'seconds', flush=True)
        print(q['id'], 'recall@4:', recall, 'retrieved:', ', '.join(row['retrieved_ids']))
    checkpoint(complete=True)
    print('Saved:', target, flush=True)
    if args.live:
        failed = sum('error' in r[m] for r in rows for m in modes)
        print('Generation failures:', failed, '| Review successful answers manually.')
        return int(failed > 0)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
