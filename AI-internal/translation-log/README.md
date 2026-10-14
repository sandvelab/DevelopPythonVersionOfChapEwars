# Translation log

Append-only ledgers, the source of the translation record in `AI-generated/translation-record/`.
Entries are appended as work happens and never rewritten; a superseded entry gets a new
entry referring to it.

- `judgment_calls.json` — `JC-NN` entries: call, choice, alternatives, basis, agency.
- `challenges.json` — `CH-NN` entries: challenge, solution, status, details.
