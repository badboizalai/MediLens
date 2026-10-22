# Screen Spec: Explain (finding detail and chat panel)

| Field | Value |
| --- | --- |
| Route | Panel on /app/viewer (side panel desktop, bottom sheet mobile) |
| Rules | BR-022/023 (approved knowledge + own data only; no doses, no medication changes, no survival prognosis), BR-041 (115 first), BR-042 |
| Primary action | Send question |
| Personas | Patient, caregiver |
| Reviewers | clinical-safety-officer (all copy), business-analyst |

## Purpose
Explain a selected finding in plain language, citing the user's own record and reviewed sources, and help the user prepare questions for their doctor. It explains; it does not diagnose, advise treatment or doses, or predict outcomes.

## Wireframe (desktop side panel)
```
+--------------------------------------+
| Hình minh họa giúp bạn hiểu hồ sơ,   |
| không thay thế ý kiến bác sĩ.        |  <- DisclaimerBar
+--------------------------------------+
| Tooth 36   <! Cần chú ý>   [x close] |
| Hồ sơ của bạn ghi:                   |
|  "Sâu răng mặt nhai 36" (lab_2026 p1)|
| Điều này thường có nghĩa là:         |
|  (plain-language meaning)            |
|  Source: [Reviewed article, 2026-05] |
| Câu hỏi bạn có thể hỏi bác sĩ:       |
|  - ...                               |
|  - ...                               |
+--------------------------------------+
| Chat                                 |
|  You: What does this mean?           |
|  MediLens: ... [source 1]            |
|  (streaming ...)                     |
| {Type a question           } [Send]   |
| This is an illustration, not a       |
| diagnosis.                           |
+--------------------------------------+
```

## Components
| Component | Notes |
| --- | --- |
| DisclaimerBar | `disclaimer.short`, always visible, plus `viewer.illustration` line under the input |
| Finding card | Record quote, meaning, questions for doctor, SourceBadge with review date |
| Chat list | Streaming answer, citations per answer; "Extracted by AI" label |
| Message input | Max length hint; Send via button and Enter |
| Guardrail messages | Refusal for dose/medication/prognosis; emergency banner |
| Fallback card | When no reviewed article exists |

## States
| State | Trigger | What the user sees | Copy key |
| --- | --- | --- | --- |
| Empty | No question yet | Finding card plus suggested questions | explain.suggest |
| Loading | Answer streaming | Typing indicator, Stop button | explain.loading |
| No source | No reviewed article (BR-022) | Fallback message, suggest asking doctor | explain.noSource |
| Dosing/medication | User asks about dose or stopping | Polite refusal, ask prescribing doctor | explain.noDosing |
| Prognosis | User asks about survival or outlook | Refusal, ask treating doctor | explain.noPrognosis |
| Diagnosis | User asks "do I have X" | Restate what the record says, no new diagnosis | explain.noDiagnosis |
| Emergency | Text mentions emergency signs (BR-041) | 115 banner above all content | explain.emergency |
| Error | Service failure or rate limit | Retry, finding card still readable | explain.error |
| Permission denied | Not the owner | Not-found | common.notFound |

## Copy (VI / EN)
| Key | VI | EN |
| --- | --- | --- |
| finding.recordSays | Hồ sơ của bạn ghi: | Your record says: |
| finding.usuallyMeans | Điều này thường có nghĩa là: | This usually means: |
| finding.askDoctor | Câu hỏi bạn có thể hỏi bác sĩ: | Questions you could ask your doctor: |
| explain.noSource | Hiện chưa có thông tin đã được kiểm duyệt cho câu hỏi này. Bạn nên hỏi bác sĩ. | We don't have reviewed information for this yet. Please ask your doctor. |
| explain.noDosing | Mình không thể tư vấn về liều hay ngừng thuốc. Hãy trao đổi với bác sĩ kê đơn. | I can't advise on doses or stopping medicine. Please talk to the prescribing doctor. |
| explain.noPrognosis | Mình không thể dự đoán diễn tiến. Bác sĩ điều trị của bạn là người phù hợp để trao đổi. | I can't predict how things will go. Your treating doctor is the right person to ask. |
| explain.noDiagnosis | Mình chỉ giải thích những gì hồ sơ của bạn ghi, không chẩn đoán. | I can only explain what your record says; I don't diagnose. |
| explain.emergency | Nếu bạn đang đau ngực, khó thở hoặc có nguy hiểm tức thời, hãy gọi 115 ngay. | If you have chest pain, trouble breathing or are in immediate danger, call 115 now. |
| explain.error | Chưa trả lời được lúc này. Hãy thử lại sau ít phút. | I can't answer right now. Please try again in a few minutes. |
| explain.suggest | Gợi ý: "Hồ sơ này ghi gì?", "Mình nên hỏi bác sĩ điều gì?" | Try: "What does this record say?", "What should I ask my doctor?" |
| viewer.illustration | Đây là hình minh họa, không phải chẩn đoán. | This is an illustration, not a diagnosis. |

Wording guard: no "bạn bị / you have", no drug names with amounts, no "sẽ khỏi / thời gian sống / survival". Any new string needs clinical-safety-officer review before build.

## Accessibility
- Focus moves to the panel heading on open and returns to the selected region on close; Esc closes.
- Chat list `role="log"` with `aria-live="polite"`; streaming announces on completion, not per token.
- Emergency banner `role="alert"`.
- Citations are real links with descriptive text; Send and Stop labelled; 44x44 px targets.
- Panel does not obscure focused element (2.4.11); readable at 200% zoom and 320 px reflow.

## Open questions
- Final refusal texts and emergency trigger list (CSO, ai-ml-engineer).
