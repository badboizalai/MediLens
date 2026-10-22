# Test Design Techniques with MediLens Examples

## Equivalence partitioning & boundary values
| Input | Partitions | Boundaries to test |
| --- | --- | --- |
| File size (BR-010) | ≤ 20 MB valid, > 20 MB invalid | 0 B, 1 B, 20 MB − 1 B, 20 MB, 20 MB + 1 B |
| Pages | 1–30 valid | 1, 30, 31 |
| Confidence (BR-012) | < 0.7 must confirm, ≥ 0.7 auto | 0.69, 0.70, 0.71 |
| Share expiry (BR-030) | 1–90 days | 0, 1, 7 (default), 90, 91 |
| Image short side (BR-011) | ≥ 1000 px | 999, 1000 |
| FDI tooth | valid set | 10, 11, 18, 19, 48, 49, 51, 55, 56, 85, 86 |

## Decision table — share access (BR-030/031)
| Signed in | Grant exists | Revoked | Expired | Scope covers resource | Result |
| --- | --- | --- | --- | --- | --- |
| N | – | – | – | – | 401 → login |
| Y | N | – | – | – | 404 |
| Y | Y | Y | – | – | 404 |
| Y | Y | N | Y | – | 404 |
| Y | Y | N | N | N | 404 |
| Y | Y | N | N | Y | 200 + audit |

## State transition — document
Valid: uploaded→validating→queued→ocr_running→extracting→extracted→in_review→confirmed; validating→rejected; any running→failed/needs_manual. Test every valid edge and representative invalid ones (confirmed→extracting must fail with 409 invalid-state).

## Error guessing list
Rotated photo, photo of a screen, two pages in one photo, handwritten only, non-medical document, password-protected PDF, HEIC from iPhone, duplicate upload, network drop mid-upload, very long record (30 pages), mixed VI/EN, stamps over text, diacritics lost in OCR.

## Abuse cases
Change IDs in URL/body; replay share link after revoke; upload EICAR; script in field correction; prompt injection in question; flood explain endpoint.

## Pairwise (viewer)
Browsers × device class × Unit × severity × 2D/3D — use pairwise tool to reduce combinations while covering each pair.
