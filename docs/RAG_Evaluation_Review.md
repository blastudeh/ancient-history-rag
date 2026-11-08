# Ancient History RAG — Evaluation Review

Model: `llama3.2:1b`  
Run timestamp (UTC): 2026-11-07T00:30:34.810922+00:00  
Evidence: `rag_1b_evaluation.json` supplied by the student. Review performed against the retrieved excerpts stored in that file; this is not an independent audit of the linked websites.

## Results

- All 13 selected questions completed; no generation errors were recorded.
- The LLM was used for 12 questions. Q12 used the application’s deterministic no-evidence refusal.
- Mean source recall@4 was 1.0 for the 10 answerable questions. This means the expected source documents appeared among the retrieved passages; it does not mean the generated answers were 100% correct.
- Q11–Q13 appropriately declined to supply unsupported facts, although their wording/citation handling differed.
- This is a small development set, not an independent benchmark. No single answer-accuracy percentage is claimed because several answers are only partially supported.
- This run contains RAG only. It is not a same-model comparison against a fresh 1B baseline run.

## Answer-by-answer review

| Question | Assessment | Evidence and limitation |
|---|---|---|
| Q01 | Partly supported | Mineral resources are attributed to the Nile, whereas EG01-01 attributes them to the desert. |
| Q02 | Supported; citation missing | The explanation follows EG02-01 but has no passage citation. |
| Q03 | Incorrect refusal | EG02-01 explicitly lists baskets, mats, sandals, ropes and small boats. |
| Q04 | Incomplete; citation errors | Does not clearly define cuneiform. EG02-02 discusses Egyptian papyrus and hieratic, not cuneiform. Records on tablets are supported by ME01-02. |
| Q05 | Overly cautious refusal | ME01-01 links intensive irrigation agriculture with city growth and mentions canal maintenance. The source supports a general answer, although not a detailed causal account specific to Uruk. |
| Q06 | Correct fact; extraneous citation | Sale of land is supported by ME02-01. EG01-01 is not among this question’s retrieved passages. |
| Q07 | Supported | RO01-01 supports the distinction between use of roads and permission to use the cursus publicus. |
| Q08 | Mostly supported | RO02-01 defines the agger as a raised bank of stone or gravel. It explicitly attributes drainage to ditches, so the answer’s additional causal claim is not directly supported by this excerpt. |
| Q09 | Incomplete comparison; incomplete citation support | Compares scripts rather than the physical writing materials. EG02-02 supports only the Egyptian side; evidence for the Mesopotamian side is not cited. |
| Q10 | Supported; citation missing | Cheaper/faster water transport and coastal connections are supported by the retrieved Roman passages, but citations are absent. |
| Q11 | Appropriate refusal; irrelevant citation | Does not invent Cleopatra’s height. Appended EG02-01 concerns papyrus and does not establish her height. |
| Q12 | Appropriate deterministic refusal | No passages were retrieved; the application returned its fixed refusal without calling the LLM. |
| Q13 | Appropriate refusal; wording differs | Correctly says the budget is absent from the passages. The citation checker flags the missing citation because it recognizes only the exact standard refusal phrase. |

## Troubleshooting and implementation changes

The original 3B live evaluation recorded six generation failures: one RAG failure (Q08) and five baseline failures (Q07, Q08, Q10, Q12 and Q13). Other requests did succeed, so the system was not universally broken. A later Ollama log showed model loading/warm-up was still underway when the client cancelled a request. This identifies where that request stalled, not a definitive cause for every earlier failure.

The request timeout was raised from 240 to 600 seconds. This increased the waiting allowance; it did not accelerate inference. An instruction requesting at most 80 words was added. The evaluator was extended to show progress before each call, save checkpoints after answers, select question IDs and modes, and write separate output files. Finally, the smaller 1B model completed the supplied RAG run. These changes do not establish that every performance issue was resolved solely by model size.

Ubuntu was configured with 6 GB RAM after Windows became unresponsive. Disabling VirtualBox 3D acceleration was followed by normal rendering of the previously blank Files window. The evidence does not establish that the display problem and model-loading delay had the same cause.

## Interpretation

Retrieval was stronger than generation on this development set. The retriever found expected sources, but the smaller language model sometimes ignored available evidence, made unsupported inferences, or attached an inappropriate citation. Citation-ID validation alone cannot determine whether a cited passage supports a claim: Q04 and Q09 illustrate this limitation.

The refusal mechanism also needs careful evaluation. Q12 was rejected by application logic without using the model; it should not be presented as proof of the model’s refusal ability. Q03 shows an unnecessary refusal despite sufficient evidence, while Q13 shows a substantively appropriate refusal that the exact-string citation checker flags.

## Suggested report paragraph

“In the final RAG-only run with Llama 3.2 1B, all 13 development questions completed without generation errors. Mean source recall@4 was 1.0 across the 10 answerable questions. However, manual comparison against retrieved passages revealed factual attribution errors, unnecessary refusals, missing citations and citations that did not support the associated statements. Thus, successful execution and high retrieval recall did not imply perfect answer accuracy. The three unsupported or out-of-domain questions were declined; one refusal was produced directly by application logic. These results demonstrate a functioning pipeline and highlight limitations of a small local model and citation-ID-only validation.”

## Next improvements

1. Preserve raw outputs and keep review annotations separate.
2. Check factual support and citation coverage, not just citation-ID membership.
3. Improve prompt wording and evaluate unnecessary refusals on new questions.
4. If comparing RAG and baseline, use the same model and settings and retain the results of both conditions.
5. Use a held-out question set before making general performance claims.

No answers were rewritten or substituted in the original evaluation file. This review records observed limitations rather than treating corrected reference answers as model outputs.
