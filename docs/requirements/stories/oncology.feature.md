# Oncology content rules: user stories (draft — pending CSO (D99))

Status: **draft — pending CSO (D99)**. Not approved. Rules: `docs/brd/business-rules.md` (BR-046…BR-051). Matrix: `docs/requirements/traceability.csv`.
Test data is synthetic only. Wording follows BR-042 (illustrate and explain only).
Copy examples in quotes are illustrative; final wording belongs to the CSO.

## US-036 Oncology record opens in summary mode (BR-046)
As a patient, I want a calm summary first, so that I am not overwhelmed.

```gherkin
Scenario: Summary is the default
  Given I have a confirmed synthetic oncology record
  When I open it
  Then I see the summary view only
  And no metastasis marker is drawn
  And I see a "Show details" button ("Xem chi tiết")

Scenario: Details only on explicit tap
  Given I am viewing the oncology summary
  When I tap "Show details"
  Then the detail panel opens
```

## US-037 No survival or prognosis statements (BR-047)
```gherkin
Scenario Outline: Outcome question is refused
  Given I am viewing a synthetic oncology record
  When I ask "<question>"
  Then I get no number, duration or outlook
  And I see "<reply>"

  Examples:
    | question                              | reply                                                                                   |
    | What is the 5-year survival?          | I can't predict outcomes. Please ask your care team.                                    |
    | Tôi còn sống được bao lâu?            | Tôi không thể dự đoán kết quả. Bạn hãy hỏi đội ngũ chăm sóc của mình.                   |

Scenario: Generated text has no outcome claims
  When the explanation for any oncology golden-set record is generated
  Then it contains no survival figure, percentage outcome or "good/poor outlook" phrase
```

## US-038 TNM verbatim with letter meanings (BR-048)
```gherkin
Scenario: TNM shown as written
  Given the record states "T2N0M0"
  When I open the detail panel
  Then I see "T2N0M0" exactly as written
  And I see "T = extent of the primary tumour, N = lymph nodes, M = distant spread"
  And I see "Ask your care team what these values mean for you"
  And I do not see any sentence interpreting the values for me

Scenario: VI copy
  Given the language is Vietnamese
  Then I see "T = mức độ khối u nguyên phát, N = hạch bạch huyết, M = di căn xa"
```

## US-039 Neutral, labelled metastasis markers (BR-049)
```gherkin
Scenario: Stated metastasis is neutral and labelled
  Given the record states "M1, liver metastasis"
  And I have tapped "Show details"
  Then a marker appears on the liver with the text "Liver - stated in your record"
  And the marker has no flashing or animation
  And it does not use an alarm-red fill
  And it is distinguishable without colour

Scenario: No marker when not stated
  Given the record does not state any metastasis
  When I tap "Show details"
  Then no metastasis marker is shown
```

## US-040 Reassuring tone, care-team prompts and 115 (BR-050)
```gherkin
Scenario: Care-team prompt and support link
  When I open any oncology detail section
  Then I see "Ask your care team" ("Hãy hỏi đội ngũ chăm sóc của bạn")
  And I see a support link

Scenario: Emergency signs show 115 first
  When I describe "coughing up a lot of blood"
  Then a 115 banner is rendered before any other content
```

## US-041 Oncology articles need a CSO review date (BR-051)
```gherkin
Scenario Outline: CSO review date gate
  When I ingest an oncology KnowledgeArticle with CSO review date "<date>"
  Then the result is "<result>"

  Examples:
    | date                  | result                         |
    | (none)                | rejected                       |
    | within 12 months      | retrievable                    |
    | older than 12 months  | flagged for re-review          |
```
