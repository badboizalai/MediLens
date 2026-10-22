# Usability Test Script: Prototype Round 1 [S2-T10]

Humans run this test; this file is the script and recording sheet. Based on the skill template `usability-test-plan.md`.

- **Goal:** Can first-time users go from upload to understanding a finding, and share it, using the low-fi/clickable prototype?
- **Participants:** 3 (suggested mix: 1 aged 45+, 1 caregiver, 1 low digital literacy). Screen-reader or low-vision user if possible as a 4th optional.
- **Material:** clickable prototype of the 8 screens; synthetic records only (e.g. D-01 dental). No real patient data.
- **Method:** moderated, think-aloud, about 30 minutes, remote or in person. Facilitator + note-taker.
- **Language:** run in Vietnamese; this script gives VI prompts with EN.

## 1. Before the session (5 min checklist)
- Prototype open on Consent screen, reset to start state.
- Consent for the session itself obtained; recording only with permission; no personal data collected beyond age band and role.
- Prepare the synthetic record (printed or on device).

## 2. Introduction (read aloud)
VI: "Chúng tôi đang thử nghiệm sản phẩm, không phải thử nghiệm bạn. Không có câu trả lời đúng hay sai. Hãy nói to những gì bạn nghĩ. Bạn có thể dừng bất cứ lúc nào. Đây là bản mẫu và dùng dữ liệu giả."
EN: "We are testing the product, not you. There are no right or wrong answers. Please think aloud. You can stop at any time. This is a prototype with fake data."

Warm-up: "Bạn đã bao giờ xem hồ sơ bệnh án của mình hoặc người thân chưa? Bạn thấy khó ở đâu?" / "Have you looked at your own or a relative's medical record? What was hard?"

## 3. Tasks

| # | Task prompt (VI / EN) | Screens | Success criteria | Max time |
| --- | --- | --- | --- | --- |
| T1 (main) | "Hãy tải hồ sơ nha khoa này lên và xác nhận kết quả." / "Upload this dental record and confirm the results." | Consent, Upload, Review, Viewer | Agrees to consent, uploads, confirms all flagged fields, reaches Viewer with confirmed findings | 5 min |
| T2 | "Tìm xem răng nào có vấn đề và điều đó có nghĩa là gì." / "Find which tooth has a problem and what it means." | Viewer, Explain | Names tooth 36 and "sâu răng" (per record) and finds the "this is an illustration, not a diagnosis" notice | 2 min |
| T3 | "Chia sẻ hồ sơ nha khoa với bác sĩ trong 7 ngày." / "Share the dental record with a doctor for 7 days." | Share | Share created with Dental scope and 7-day expiry | 3 min |

Facilitator rules: do not lead or explain the UI; if stuck for 1 minute ask "Bạn đang nghĩ gì?"; after 2 more minutes give a neutral hint and mark "assisted"; stop at max time and mark "fail".

## 4. Comprehension questions (after T2)
1. Vị trí này ở đâu trên cơ thể? / Where in the body is this?
2. Hồ sơ ghi mức độ như thế nào? Bạn biết điều đó từ đâu? / What does the record say about it, and how do you know?
3. Bạn sẽ hỏi bác sĩ điều gì? / What would you ask your doctor?
4. Hình này có phải là chẩn đoán không? / Is this picture a diagnosis? (Expected: no, an illustration.)

Safety probe (note, do not coach): Did any participant read the screen as a diagnosis, a treatment instruction, or an outlook? Record verbatim; report to clinical-safety-officer.

## 5. Post-task
- Emotional response, 1 (calm) to 5 (anxious), after T2.
- SUS (10 items) at the end.
- Open: "Điều gì khó hiểu nhất? Điều gì làm bạn yên tâm?" / "What was most confusing? What reassured you?"

## 6. Measures and pass criteria

| Measure | How | Target |
| --- | --- | --- |
| Main-task completion (T1) | Completed unassisted, per participant | at least 2 of 3 participants (acceptance) |
| T2 and T3 completion | As above | at least 2 of 3 each (target, not gate) |
| Time on task | Stopwatch | within max time |
| Errors / hints | Count | recorded |
| Comprehension | Questions 1-4 correct | at least 2 of 3 participants, all 4 answered, Q4 "illustration" correct |
| SUS | Mean | 68 or higher (reference) |
| Anxiety | Mean 1-5 | at most 3 |

Round passes if T1 is completed unassisted by at least 2 of 3 participants and no participant reads the Viewer or Explain as a diagnosis.

## 7. Recording sheet (one per participant)

| Field | Value |
| --- | --- |
| Participant ID (P1-P3, no names) | |
| Age band / role | |
| Date, facilitator, note-taker | |

| Task | Complete (Y / assisted / N) | Time | Errors | Quotes |
| --- | --- | --- | --- | --- |
| T1 | | | | |
| T2 | | | | |
| T3 | | | | |

SUS score: ___  Anxiety: ___  Comprehension Q1-Q4: ___

## 8. Report template

| Issue | Task | Severity (1-4) | Evidence | Recommendation |
| --- | --- | --- | --- | --- |

Severity: 1 cosmetic, 2 minor, 3 major (task slowed or failed), 4 blocker (safety or misreading as diagnosis). Severity 4 items go to clinical-safety-officer and block build of that screen.

## 9. Privacy and ethics
- Synthetic data only; no real records brought by participants.
- Store notes with participant IDs only; delete recordings after analysis.
