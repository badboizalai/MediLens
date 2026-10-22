# Authorization Patterns

## 1. Principal
`current_user` dependency returns `Principal(user_id, roles, mfa, profile_ids_owned)` from the verified JWT (Cognito JWKS, audience + issuer checked, clock skew ≤ 60 s).

## 2. Policy per resource
```python
class DocumentPolicy:
    async def can_read(self, p: Principal, doc: Document) -> bool:
        if doc.profile_id in p.profile_ids_owned:
            return True
        return await self.shares.has_active_grant(
            grantee=p.user_id,
            profile_id=doc.profile_id,
            scope=("document", doc.id),
            at=self.clock.now(),
        )
```
Service code: load by ID **with** owner scope where possible (`WHERE id=:id AND profile_id = ANY(:allowed)`); if not found → `NotFound` (404).

## 3. Row-Level Security (second layer)
```sql
ALTER TABLE body_findings ENABLE ROW LEVEL SECURITY;
CREATE POLICY owner_or_shared ON body_findings
  USING (profile_id = ANY (string_to_array(current_setting('app.allowed_profiles', true), ',')::uuid[]));
```
The API sets `SET LOCAL app.allowed_profiles = '...'` per transaction from the principal + active shares. The app DB role is not table owner and has no `BYPASSRLS`.

## 4. Sharing checks (BR-030/031)
Grant valid if `revoked_at IS NULL AND expires_at > now()` and scope matches (all | unit | document). Never cache decisions > 60 s.

## 5. Admin and break-glass (BR-006)
Admin endpoints never return clinical content. Break-glass: request with reason → grant for 1 h → alert security channel → every access audited with `break_glass_id`.

## 6. Testing
Generate a matrix from OpenAPI: for each operation with a path ID, test owner (200), stranger (404), expired share (404), valid share (200 where scope allows), admin without break-glass (404/403), unauthenticated (401). Fail CI if a new operation lacks a policy test.
