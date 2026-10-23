// Time-limited sharing (S11-T103, SEC-AR-07). Default deny: anything not permitted here is denied.
// Principal: the caller. Resource: a Share with {grantee, scope, expires_at (epoch s), revoked}.
// context.now is the injected clock (epoch s). There is deliberately no permit for "write".
permit (
  principal,
  action == Action::"read",
  resource
)
when {
  resource.grantee == principal &&
  resource.scope == "findings:read" &&
  !resource.revoked &&
  context.now < resource.expires_at
};
