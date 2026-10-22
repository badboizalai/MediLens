# DSR Completion Checklist — request <id>

| Step | Store | Action | Done | Evidence |
| --- | --- | --- | --- | --- |
| 1 | Identity | Re-auth + MFA verified, request logged (audit) | [ ] | audit id |
| 2 | Sessions | All sessions/refresh tokens revoked | [ ] | |
| 3 | RDS | Profile, documents, extraction, clinical rows deleted or data key crypto-shredded | [ ] | row counts |
| 4 | S3 originals | Objects + all versions deleted | [ ] | list output |
| 5 | S3 pipeline intermediates | Prefix deleted | [ ] | |
| 6 | Analytics | Rows with user_pseudo_id purged (Bronze/Silver/Gold) | [ ] | |
| 7 | Vector store | User-specific chunks (if any) deleted | [ ] | |
| 8 | Caches | Keys for user evicted | [ ] | |
| 9 | Shares | Grants revoked, recipients notified | [ ] | |
| 10 | Backups | Expiry date documented (≤ 1 y) or key shredded | [ ] | |
| 11 | Audit log | Retained (no clinical content) — noted in response | [ ] | |
| 12 | Response | User informed within 30 days | [ ] | date |
