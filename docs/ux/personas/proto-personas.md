# Proto-personas (HYPOTHESES, not findings)

> **Status: hypotheses.** Built from plan §2.2 and team assumptions only. No interviews have been run yet; nothing here is evidence. Names are fictional. There are no quotes on purpose. Every pain point is tagged `assumption` and points to the interview question that will test it. After the interviews, update each tag to `validated`, `refuted` or `revised`, citing note codes (never names).

**Question key** (from `docs/research/interview-guide.md`): `B2.1` = block 2, question 1, and so on. Block 2 = current behaviour, 3 = pain points, 4 = body viewer concept, 5 = trust and privacy.

## P1. Patient: "Nguyễn Văn An" (fictional)

| | |
| --- | --- |
| Who | 25-65, uses a smartphone daily, no medical background (plan §2.2) |
| Context | Gets paper/PDF/photo records after visits; keeps them in a drawer, phone gallery or chat apps |
| Tech | Comfortable with chat and banking apps; one-handed phone use; may be unfamiliar with 3D |

**Goals**
- Understand what the record says in plain words.
- Know what to ask the doctor at the next visit.
- Keep records in one place and see changes over time.

**Pains**

| Pain | Tag | Validate with |
| --- | --- | --- |
| Jargon and abbreviations make records hard to read | `assumption` | B3.1 |
| Anxiety or misunderstanding while waiting to see the doctor | `assumption` | B3.4 |
| Records are scattered or lost (paper, gallery, chat) | `assumption` | B2.2, B2.4 |
| Cannot picture where the finding is | `assumption` | B3.3, B4.1 |
| Online searching gives scary or unreliable answers | `assumption` | B3.2 |

**Trust and privacy concerns**
- Fear that health data is leaked or sold. `assumption` (B5.1, B5.2)
- Wants to delete data and control who sees it. `assumption` (B5.3)
- Unsure whether to trust AI reading; wants to check the result. `assumption` (B5.4)

## P2. Caregiver: "Trần Thị Bình" (fictional)

| | |
| --- | --- |
| Who | Adult child or spouse helping a relative, often an older parent |
| Context | Attends visits, holds the relative's papers, relays information to other family members |
| Tech | Moderate; may be on a shared or older device; may help the relative operate the phone |

**Goals**
- See the relative's record when the relative permits it.
- Explain it to the family and prepare questions for the doctor.

**Pains**

| Pain | Tag | Validate with |
| --- | --- | --- |
| No clear way to access the relative's records | `assumption` | B2.3 |
| Information is split across people, papers and chats | `assumption` | B2.2, B2.3 |
| Hard to explain findings to an older relative without alarming them | `assumption` | B3.1, B4.4 |
| Unsure how much of the record the relative wants shared | `assumption` | B5.3 |

**Trust and privacy concerns**
- Consent must come from the patient; wants time-limited, clear sharing. `assumption` (B5.3)
- Worry about being blamed if shared data leaks. `assumption` (B5.1)

## P3. Receiving clinician: "BS. Lê Minh Cường" (fictional)

| | |
| --- | --- |
| Who | Doctor a patient shares a summary with (plan §2.2) |
| Context | Short consultations; receives photos, PDFs or nothing structured |
| Tech | Comfortable with hospital systems; wants speed, will not install extra tools casually |

**Goals**
- A quick, accurate summary before or during the visit.
- Ability to see the source and fix a wrong extraction.

**Pains**

| Pain | Tag | Validate with |
| --- | --- | --- |
| Little time; unstructured patient-supplied records | `assumption` | B2.1, B3.1 |
| Extraction errors would waste time or mislead | `assumption` | B5.4 |
| Patients arrive with misunderstandings from online sources | `assumption` | B3.2 |

**Trust and privacy concerns**
- Needs the original document visible next to any summary. `assumption` (B5.4)
- Liability concern about relying on patient-generated data. `assumption` (B5.2)

> The interview guide targets patients and caregivers. Clinician hypotheses need extra questions or a separate short guide; until then every P3 tag is only provisionally mapped to the closest question.

## Validation plan

1. **Interviews** use `docs/research/interview-guide.md`; recruitment via `recruitment-tracker.md`; notes via `note-template.md`, by participant code only, after consent and anonymisation checks.
2. **Tag update:** after each interview, mark the pain `validated`, `refuted` or `revised` with note codes. The threshold for `validated` is set in `research-plan.md`.
3. **Gaps:** add questions for clinicians; add caregiver-specific probes if B2.3 and B5.3 give too little.
4. **Output:** replace proto-personas with evidence-based personas, keeping unvalidated items marked as assumptions.
5. **Safety:** no diagnosis, advice or medical detail is recorded from participants beyond what the notes template allows (BR-042).
6. **Review:** business-analyst reviews the mapping; findings feed user stories only after validation.
