# Prioritisation Methods

## RICE
Score = Reach × Impact × Confidence ÷ Effort.
- Reach: users affected per quarter (beta: estimate from target MAU).
- Impact: 3 massive, 2 high, 1 medium, 0.5 low, 0.25 minimal.
- Confidence: 100% / 80% / 50%.
- Effort: person-weeks.

| Item | Reach | Impact | Conf | Effort | RICE |
| --- | --- | --- | --- | --- | --- |
| Review screen with bounding boxes | 100 | 3 | 80% | 2 | 120 |
| 3D heart viewer | 40 | 2 | 50% | 3 | 13.3 |
| Share with doctor | 60 | 2 | 80% | 1.5 | 64 |

## WSJF (for enablers / tech debt)
WSJF = (Business value + Time criticality + Risk reduction/opportunity) ÷ Job size, each on Fibonacci 1, 2, 3, 5, 8, 13, 20.
Use for: outbox pattern, multi-account landing zone, eval harness, observability.

## MoSCoW for a release
- Must: release fails without it (legal, safety, core value).
- Should: important, workaround exists.
- Could: nice to have.
- Won't (this time): explicitly excluded.
Rule: Musts ≤ 60% of capacity so Shoulds absorb risk.

## Kano (for UX features)
Basic (expected: login, upload works), Performance (more is better: accuracy, speed), Delighters (3D x-ray mode, timeline animation). Never ship delighters while basics are broken.

## Override ladder
1. Safety and security/privacy MUSTs
2. Gate blockers
3. Committed release scope
4. Score order
