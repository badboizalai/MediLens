# Research plan

Status: DRAFT for human review. Owner: BA. Reviewers: UX (guide), REG (consent, data handling).

## 1. Goals
1. Learn what patients and caregivers find hard to understand in their medical records.
2. Learn what they would want to see (and not see) in a body viewer.
3. Learn trust and privacy concerns about uploading health data.
4. Learn from clinicians how records are explained today and what would be unsafe or unhelpful.

Outputs feed Product Brief, personas, journey map and BRD v1 (plan §2.6).

## 2. Research questions
- RQ1 How do people keep, read and share their records today?
- RQ2 Which terms, abbreviations or layouts cause confusion; what do they do about it?
- RQ3 What do they want to know that the record does not tell them?
- RQ4 How do they react to seeing findings on a body illustration; what feels helpful, scary or misleading?
- RQ5 What would make them trust, or refuse, an app holding their records?
- RQ6 (clinicians) What explanations do patients ask for most; which wording or visuals risk misleading patients?

## 3. Participants
| Group | Target | Criteria |
| --- | --- | --- |
| Patients / caregivers | 5-8 | Adult, received a medical record in the last 24 months or helped a relative; mix of age and smartphone comfort; not a MediLens team member |
| Clinicians | 1-2 | Practising doctor or dentist; not treating the participant |

Do not recruit minors or people in acute distress. Interviewers must not ask for diagnoses, results or documents (see guide).

## 4. Recruitment channels
Personal network (friends/family of the team, second-degree preferred), community groups where posting is permitted, referral by a clinician contact. Any thank-you gift is decided by the PO. Track in [recruitment-tracker.md](recruitment-tracker.md) using codes only.

## 5. Schedule (within S01)
Relative to S01 working days; exact dates set by the PO.
| When | Activity |
| --- | --- |
| D05-D06 | Kit ready, REG/UX review, pilot the guide with a teammate (not counted) |
| D07-D08 | Recruit and schedule |
| D08-D12 | Interviews, 45 min each + 15 min notes; max 2 per day |
| D12-D13 | De-identify notes, run checklist, delete working copies |
| D13-D14 | Affinity synthesis into personas, journey, pain-point list |

If fewer than 5 patient interviews are done by the end of S01, flag it in the weekly status rather than lowering quality.

## 6. Data-handling plan
- Collected: age band, role, general experience, and whatever the participant volunteers. No names, phone numbers, emails, addresses or record/ID numbers. Participants are not asked to show or bring records.
- Identity: only the facilitator knows the person. The code-to-person key (if any) is kept outside the repo in an access-restricted private store, separate from notes.
- Recording: optional, only with separate explicit consent; audio only. Stored encrypted outside the repo and used solely to complete notes.
- Notes: written in [note-template.md](note-template.md) form, de-identified, and checked with the [checklist](anonymisation-checklist.md) before storage. Only de-identified notes may be committed.
- Retention and deletion: recordings and raw/working notes deleted within 7 days of note completion (no later than the end of S01 synthesis); the key deleted when synthesis is done; de-identified notes kept for the product lifetime. On withdrawal, that participant's recording, raw notes and key are deleted at once, and their de-identified notes are removed from further synthesis where feasible.
- Legal basis: explicit consent per Law 91/2025/QH15 and Decree 356/2025/NĐ-CP; REG confirms before the first interview.

## 7. Validation threshold (PROPOSAL, BA/UX to confirm)
Personas and pain points are hypotheses until the interviews support them. Proposed rule:
- A persona pain point or need is **validated** when at least 3 of 5 patient/caregiver interviews raise it unprompted or confirm it when probed neutrally; with 6-8 interviews, at least 50%.
- For the receiving-clinician persona (P3, [clinician guide](clinician-interview-guide.md)), validated when 2 of 2 clinicians show it; with only 1 clinician it stays "indicative".
- Below the threshold it is "unvalidated" and goes to the backlog as a question, not a requirement; do not drop contradicting evidence.
- Count de-identified notes only; record the count per item in the synthesis. With a sample this small this is a prioritisation aid, not statistical proof.
