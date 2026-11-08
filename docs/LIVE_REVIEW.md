# Live model verification - complete after running on your laptop

Status: PENDING. No actual local LLM outputs are bundled as completed results.

Run date:
Python version:
Ollama version (`ollama --version`):
Model tag and ID (`ollama list`):
Computer RAM / GPU if known:
Corpus SHA-256 (from saved results):

Run `py -3 evaluate.py --live`. Open `results/live_evaluation.json`.
For each question, check the answer against the retrieved passages and the review criteria.
Use 1 for pass, 0 for fail, and N/A where inappropriate. Do not automatically score a response correct because it contains the expected word.

| Question | RAG correct? | Citations support claims? | Baseline correct? | Refusal appropriate? | Notes |
|---|---|---|---|---|---|
| Q01 | | | | | |
| Q02 | | | | | |
| Q03 | | | | | |
| Q04 | | | | | |
| Q05 | | | | | |
| Q06 | | | | | |
| Q07 | | | | | |
| Q08 | | | | | |
| Q09 | | | | | |
| Q10 | | | | | |
| Q11 | | | | | |
| Q12 | | | | | |
| Q13 | | | | | |

Accuracy = fully correct answers / successfully generated answerable questions.
Report the number of failed generations separately; do not silently omit them.
Refusal success = correct refusals / 3 unsupported questions.
For Q13, related road passages do not supply the requested annual budget.
For Q09, a complete answer must discuss both materials with support for both.

Interpretation:
- Which answers improved with retrieval?
- Which errors remain?
- Does the system refuse questions whose topic is present but whose answer is absent?
- What would you change: corpus, chunking, retrieval, prompt or model?

Attach real screenshots and this completed review to the report before submission.
