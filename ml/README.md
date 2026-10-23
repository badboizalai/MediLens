# ml
Synthetic-data scripts, golden set + eval harness (`medilens-ai-ml-engineer`), model registry (`medilens-mlops-engineer`). Never commit real data.

## Prompt registry
`prompts/<version>/` is immutable once released; the directory name is the stored `prompt_version`. Current: `extract-v2` (few-shots per Unit, line-anchored citations). `extract-v1` is kept for golden-set comparison.
