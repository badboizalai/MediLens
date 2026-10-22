# Guardrails and RAG

## Retrieval
- Corpus: approved KnowledgeArticles only (status `published`, reviewed ≤ 18 months).
- Chunking: 300–500 tokens, 50 overlap, keep headings; metadata: article_id, unit, condition codes, region codes, language, reviewed_at.
- Query: user question + IDs/codes of the selected finding; filter by language and unit; top-k 5, MMR λ 0.5.
- User data: the user's confirmed findings fetched by API with `profile_id` filter (never retrieved by vector search across users).

## Intent handling
| Intent | Action |
| --- | --- |
| emergency | Emergency sentence first (115), then brief safe info; log metric (no content) |
| dosing_or_medication_change | Refuse politely, suggest asking prescriber |
| prognosis | Refuse to estimate; explain what stage letters mean only if in sources |
| diagnosis_request | Explain only what the record says; suggest doctor |
| off_topic | Brief redirect |
| prompt_injection | Ignore instruction, answer normally or refuse; log security event |
| normal_question | RAG answer with citations |

## Output checks (post-generation)
1. Every sentence with medical content has a citation `[n]` that exists.
2. No banned patterns (dose units next to drug names, "you will live", "% survival", "stop taking").
3. Language matches user locale.
4. If a check fails → regenerate once with feedback → else fallback sentence.
Optionally use Bedrock Guardrails for denied topics and PII filters as an extra layer.

## Red-team set design (100 items)
- 20 emergency phrasings (VI/EN, indirect forms).
- 20 dosing/medication-change requests.
- 15 prognosis/survival questions.
- 15 diagnosis requests ("do I have cancer?").
- 15 prompt-injection attempts (in question and inside document text).
- 15 benign but tricky questions (should NOT be blocked) for false-block rate.

## Logging
Store intent labels, citation counts, latency, tokens; prompts/responses only redacted, 30 days, restricted access.
