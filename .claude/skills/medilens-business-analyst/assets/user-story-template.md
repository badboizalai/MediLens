# US-xxx — <short title>

**Story:** As a <persona>, I want <capability> so that <benefit>.

| Field | Value |
| --- | --- |
| Unit(s) | |
| Priority | Must / Should / Could |
| Estimate | S / M / L (≤ 3 days) |
| Business rules | BR- |
| Security | SEC- |
| NFR | NFR- |
| Data class | C4 / C3 / C2 / C1 |
| Design link | |

## Acceptance criteria
```gherkin
Feature: <feature>

  Scenario: Happy path
    Given …
    When …
    Then …

  Scenario: Boundary — <rule>
    Given …
    When …
    Then …

  Scenario: Permission denied (abuse case)
    Given I am signed in as user A
    When I request a resource owned by user B
    Then I receive 404
    And an audit event "access_denied" is recorded

  Scenario: Error — <timeout / bad input>
    Given …
    When …
    Then …
```

## Out of scope
-

## Notes / open questions
-
