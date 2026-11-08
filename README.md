# Exercise 2 - Ancient History RAG

## Verified Ubuntu run — update 8 November 2026

The student-supplied evaluation dated 7 November completed all 13 selected questions with `llama3.2:1b` and no recorded generation errors. Twelve questions called the LLM; one used a deterministic no-evidence refusal. Source recall@4 was 1.0 on 10 answerable questions. **This is retrieval recall, not answer accuracy.** The review documents incorrect refusals, incomplete answers and citation problems. No same-model 1B baseline comparison is available.

- [Raw evaluation](results/rag_1b_evaluation.json)
- [Answer-by-answer review](docs/RAG_Evaluation_Review.md)

The recovered Ubuntu `rag.py` uses a 600-second timeout and an 80-word instruction. All 14 unit tests passed again on 8 November. `evaluate_safe.py` supports checkpointing and RAG-only runs:

```bash
ollama pull llama3.2:1b
python3 evaluate_safe.py --live --model llama3.2:1b --mode rag --output results/new_1b_evaluation.json
```

The original report and any older pending-review text below are retained as historical documentation; this update and the linked evaluation review supersede their test-status claims. The current archival pass did not rerun Ollama.


A Python question-answering project about Egypt, Mesopotamia and Roman Britain.
Prepared for Okum Udeh, 3 November 2026. Deadline supplied: 10 November 2026, 23:00.

## Ubuntu quick start

Run commands in the folder containing rag.py. Use Python 3.10 or newer.

```bash
python3 rag.py index
python3 rag.py ask "How was papyrus made into a writing surface?" --mode retrieve
```

Install Ollama inside Ubuntu following https://docs.ollama.com/linux . Then run:

```bash
ollama pull llama3.2:3b
python3 rag.py doctor
python3 rag.py chat
python3 -m unittest discover -s tests -v
python3 evaluate.py --live
```

Complete docs/LIVE_REVIEW.md with real model results before submission. The supplied report marks live generation as pending. Keep Python and Ollama in the same Ubuntu VM.

## Start here (Windows / VS Code)

1. Extract the ZIP: right-click it, choose **Extract All**, then open the extracted `ancient-history-rag` folder. Do not run files from inside the ZIP.
2. Open VS Code > File > Open Folder > select `ancient-history-rag`.
3. Select Terminal > New Terminal. You should see `rag.py` if you run `dir`.
4. Check Python: `py -3 --version`. Use Python 3.10 or newer. If the `py` command is missing but Python is installed, replace `py -3` in every command with `python`. If neither works, install Python from https://www.python.org/downloads/windows/ and enable its PATH option, then restart VS Code.
5. Build the index:

```powershell
py -3 rag.py index
```

Expected: `Indexed 6 documents into 11 chunks.`

6. Try retrieval without downloading any model:

```powershell
py -3 rag.py ask "How was papyrus made into a writing surface?" --mode retrieve
```

This deliberately shows passages only. It is NOT a complete LLM demonstration.

7. Install Ollama from https://ollama.com/download/windows and open it. Restart the VS Code terminal after installation. Download the model (internet and several GB of free storage needed):

```powershell
ollama pull llama3.2:3b
py -3 rag.py doctor
```

The model download is approximately 2 GB; running it needs additional memory. Exact speed and memory availability depend on your laptop. If Ollama reports insufficient memory, use the smaller `llama3.2:1b` and pass `--model llama3.2:1b` to the Python commands. This smaller model may follow instructions less reliably. If the service is not running, open Ollama; alternatively run `ollama serve` in a separate terminal. Do not start a second server if one already runs.

8. Run a REAL RAG answer and save the evidence:

```powershell
py -3 rag.py ask "How was papyrus made into a writing surface?" --save results/my_first_rag_answer.json
```

The output must say `MODE: rag | MODEL: llama3.2:3b` and show an answer with passage citations. Check the answer against the displayed evidence. The file stores the answer, passages, model and corpus hash.

9. Start interactive questions:

```powershell
py -3 rag.py chat
```

Or double-click `START_WINDOWS.bat`. Type `exit` to stop. Successful chat results are saved automatically in `results/`.

10. Run validation and the full comparison:

```powershell
py -3 -m unittest discover -s tests -v
py -3 evaluate.py
py -3 evaluate.py --live
```

The last command calls the real model for 13 RAG questions and 13 no-retrieval baseline questions. It may take several minutes. Results appear in `results/live_evaluation.json`. Errors are recorded honestly. Do not describe failed generations as successful answers.

On Linux/macOS, use `python3` in place of `py -3`.

## What is included

- `rag.py`: ingestion, chunking, BM25 retrieval, prompt construction, Ollama generation, citation checks and CLI.
- `evaluate.py`: 13-question evaluation; optional real RAG vs baseline comparison.
- `data/sources.json`: six original, short study summaries with full source provenance. These are NOT downloaded full articles or primary ancient texts.
- `data/index.json`: 11 indexed passages, metadata and corpus SHA-256.
- `data/questions.json`: expected source IDs and human-review criteria.
- `tests/test_rag.py`: 14 automated tests; model-transport tests use clearly identified mocks.
- `results/`: actual retrieval evaluation, example output, test transcript and environment check.
- `docs/Exercise_2_Report.pdf`: step-by-step report and explanation.
- `docs/LIVE_REVIEW.md`: checklist for reviewing the real model answers.
- `requirements.txt`: documents that the core Python application has no pip dependencies.

## Design choices

This is **lexical RAG using BM25**, not an embedding/vector-database implementation. The task text supplied does not mandate embeddings, a particular framework or a database. BM25 provides transparent, repeatable retrieval without a heavy installation. RAG means retrieving reference text and supplying it to a generator; the retriever can be lexical or semantic. If your lecturer has additional requirements for vector embeddings, obtain those before submission and extend the retriever accordingly.

BM25 uses lowercase alphanumeric words, a small stopword list, term frequency, inverse document frequency and document-length normalization. Parameters: k1=1.5, b=0.75. No stemming or synonym expansion is implemented. Only passage text is scored; metadata is retained for citations. Up to four positive-scoring passages are sent to the model. BM25 scores are relevance scores, NOT probabilities or confidence percentages.

Documents are split into 80-word windows with a 15-word overlap. This small window suits the short demonstration summaries; it is not a universally optimal setting. The index is rebuilt if the source-file hash changes. The source collection is intentionally small, and Roman coverage is specifically Roman Britain, not the entire empire.

The generator uses local Ollama, default `llama3.2:3b`, temperature 0, seed 42, 4096-token context and a 450-token output cap. Temperature and seed do not guarantee identical answers across all versions/hardware. A truncated or empty response is treated as an error. A zero-hit question gets an explicit refusal without calling the LLM. Topical-but-insufficient matches still reach the model, which must decide whether the actual answer is supported.

Citation validation checks whether IDs exist in the retrieved set. It does NOT establish that every claim is true or that a cited passage entails a claim. Prompt instructions reduce risk; they do not guarantee immunity to hallucination or prompt injection. Keep this local teaching project on your own computer.

## Verification status - read before submitting

Completed here: indexing, 14 automated tests, 13 retrieval evaluations, source-reference checks, one saved retrieval example and PDF review. Mean source recall@4 was 1.00 across the 10 answerable development questions. This is a tiny, deliberately curated development set, NOT evidence of 100% answer accuracy or general historical coverage.

Not completed here: actual Ollama model inference, live answer-quality assessment, Windows-specific execution, or screenshots of a real LLM running on your machine. The environment check records that the local Ollama endpoint was unavailable. Transport mocks validate the request/response contract only. They are not real AI answers.

Finish the live steps above, inspect every answer, and update `docs/LIVE_REVIEW.md` before submitting. The supplied PDF labels live verification as pending; add your completed review and screenshots as an appendix or update the report. Do not submit a claim that live generation was tested unless you have run it.

## Screenshots to take

1. Index command showing 6 documents and 11 chunks.
2. One successful RAG answer with model name, citations and evidence.
3. A cross-civilization comparison using two sources.
4. An unsupported question producing an appropriate refusal.
5. Automated tests and evaluation summary.

On Windows use Win+Shift+S, then save each image. Use your actual output, not an illustrative screenshot. Save images in a new `screenshots` folder in the project.

## Add your own history material

Edit `data/sources.json`. Add an object with a unique ID (letters then digits), title, organization, https URL, access_note and text. Use your own accurate summaries or material you are allowed to distribute. Never claim automatically generated text is a verbatim historical source. Run `py -3 rag.py index` again, add questions in `data/questions.json`, and rerun evaluation. The expected document/chunk counts above apply only to the included corpus.

## Troubleshooting

- `can't open file rag.py`: terminal is in the wrong folder. Open the folder containing `rag.py`, then a new terminal.
- `ollama is not recognized`: install Ollama and restart the terminal.
- Connection refused: start Ollama. `doctor` checks the local service and model availability.
- Model not found: run `ollama pull llama3.2:3b`.
- First answer is slow: the model must load; CPU-only generation may take longer.
- Answer lacks citations or invents facts: review the displayed passages, improve the prompt or use a more capable model, then rerun evaluation. Do not accept it merely because the program ran.
- Sources retrieved but no useful answer: check whether the source actually contains the requested fact. Add appropriate source material if needed.

## Attribution and use

Historical summaries were prepared with AI assistance from the linked educational/museum resources. They are compressed interpretations, not verbatim article copies. Source websites retain rights in their own content. Access date: 3 November 2026. The British Museum item was available as a search-index excerpt; direct access returned 403, which is recorded in the dataset. No external site is scraped at runtime.

This project was prepared with AI assistance. Review the code, learn the explanation, and follow your course's disclosure and submission rules. The report describes what the code does and what was actually tested; it does not claim you personally carried out unperformed steps.