import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import rag

class PipelineTests(unittest.TestCase):
    def test_overlap_and_coverage(self):
        text = ' '.join(str(i) for i in range(190))
        chunks = rag.chunk_text(text)
        self.assertEqual(chunks[0].split()[-15:], chunks[1].split()[:15])
        self.assertEqual(set(text.split()), set(' '.join(chunks).split()))
        self.assertTrue(all(len(c.split()) <= 80 for c in chunks))

    def test_invalid_overlap(self):
        with self.assertRaises(ValueError): rag.chunk_text('a', 10, 10)

    def test_empty_text(self):
        self.assertEqual(rag.chunk_text(''), [])

    def test_index_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            index = rag.build_index(index_path=Path(tmp) / 'index.json')
        self.assertEqual(index['documents'], 6)
        self.assertEqual(index['source_sha256'], rag.digest(rag.DATA))
        self.assertEqual(len({c['id'] for c in index['chunks']}), len(index['chunks']))
        self.assertTrue(all(c['url'].startswith('https://') for c in index['chunks']))

    def test_retrieval_relevance(self):
        retriever = rag.Retriever(rag.load_index()['chunks'])
        for q, expected in [('papyrus writing surface', 'EG02'), ('tablet D 714', 'ME02'), ('agger', 'RO02')]:
            with self.subTest(q=q): self.assertEqual(retriever.search(q)[0]['source_id'], expected)

    def test_no_hits_does_not_call_model(self):
        with patch('rag.generate') as generate:
            result = rag.ask('repair car engine')
        generate.assert_not_called()
        self.assertEqual(result['answer'], rag.REFUSAL)
        self.assertFalse(result['used_llm'])

    def test_retrieve_never_calls_model(self):
        with patch('rag.generate') as generate:
            result = rag.ask('papyrus', mode='retrieve')
        generate.assert_not_called()
        self.assertTrue(result['retrieved'])
        self.assertFalse(result['used_llm'])

    def test_prompt_contains_real_evidence(self):
        hits = rag.Retriever(rag.load_index()['chunks']).search('papyrus')
        prompt = json.loads(rag.make_prompt('papyrus?', hits))
        self.assertEqual(prompt['reference_passages'][0]['text'], hits[0]['text'])
        self.assertEqual(prompt['question'], 'papyrus?')

    def test_citation_validation(self):
        hits = [{'id': 'EG01-01'}]
        self.assertEqual(rag.citation_check('Supported. [EG01-01]', hits), [])
        self.assertTrue(rag.citation_check('Unsupported. [XX99-01]', hits))
        self.assertTrue(rag.citation_check('Unsupported. [1]', hits))
        self.assertTrue(rag.citation_check('No citation.', hits))
        self.assertEqual(rag.citation_check(rag.REFUSAL, hits), [])

    def test_model_transport_contract_mock_only(self):
        # This is a MOCK transport check, NOT evidence of a real LLM run.
        mock_json = {'response': 'Test answer [EG01-01]', 'done': True, 'done_reason': 'stop'}
        with patch('rag.urllib.request.urlopen', return_value=io.BytesIO(json.dumps(mock_json).encode())) as opened:
            answer = rag.generate('test question', [{'id': 'EG01-01', 'text': 'test evidence'}])
        request = opened.call_args.args[0]
        payload = json.loads(request.data)
        self.assertFalse(payload['stream'])
        self.assertIn('test evidence', payload['prompt'])
        self.assertEqual(answer, mock_json['response'])

    def test_model_error_not_fabricated(self):
        with patch('rag.urllib.request.urlopen', side_effect=urllib.error.URLError('offline')):
            with self.assertRaises(RuntimeError): rag.generate('papyrus', [])

    def test_baseline_has_no_context(self):
        mock_json = {'response': 'Test baseline', 'done': True}
        with patch('rag.urllib.request.urlopen', return_value=io.BytesIO(json.dumps(mock_json).encode())) as opened:
            rag.generate('question', [{'text': 'secret evidence'}], baseline=True)
        self.assertEqual(json.loads(opened.call_args.args[0].data)['prompt'], 'question')

    def test_blank_question_rejected(self):
        with self.assertRaises(ValueError): rag.ask('   ')

    def test_truncated_response_rejected(self):
        mock_json = {'response': 'partial', 'done': True, 'done_reason': 'length'}
        with patch('rag.urllib.request.urlopen', return_value=io.BytesIO(json.dumps(mock_json).encode())):
            with self.assertRaises(RuntimeError): rag.generate('test', [])

if __name__ == '__main__': unittest.main()
