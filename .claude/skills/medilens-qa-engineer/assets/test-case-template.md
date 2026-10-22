# Test Cases — <feature>

| TC | Title | Pre-conditions | Steps | Test data | Expected | BR/US | Level | Auto |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TC-040 | Confirm blocked with unconfirmed low-confidence field | Doc in `extracted`, one field conf 0.65 | Open review → click Confirm | D-03 | Confirm disabled; API returns 422 unconfirmed-fields if forced | BR-012 / US-021 | E2E + API | Yes |
| TC-041 | Field at 0.70 does not require confirmation | Field conf 0.70 | Open review | D-04 | Field not highlighted | BR-012 | Unit | Yes |
| TC-042 | Draft findings not on viewer | Doc extracted, not confirmed | Open viewer | D-03 | No finding shown | BR-013 | E2E | Yes |
