# Upload, processing progress and retake: user stories

Rules: `docs/brd/business-rules.md`. Matrix: `docs/requirements/traceability.csv`.
Test data is synthetic only. Wording illustrates and explains; it never diagnoses (BR-042). <!-- claims-ok -->

## US-007 Upload JPG/PNG/HEIC/PDF within limits (BR-010)
As a patient, I want to upload a photo or PDF of my record, so that MediLens can read it.

```gherkin
Scenario: Upload an accepted file
  Given I have given consent
  When I upload a 3 MB JPG of one page
  Then the upload is accepted
  And I see the processing progress screen
```

## US-033 Wrong file type or too large (BR-010)
```gherkin
Scenario Outline: File is not accepted
  When I upload <file>
  Then the upload is rejected with "<reason>"
  And I see the accepted formats (JPG, PNG, HEIC, PDF), 20 MB per file, 30 pages per document
  And I can choose another file

  Examples:
    | file                | reason                  |
    | a .docx file        | file type not supported |
    | a 21 MB file        | file too large (413)    |
    | a 31-page PDF       | too many pages          |
```

## US-034 Retake a blurry, dark or small photo (BR-011)
```gherkin
Scenario Outline: Photo quality is too low
  When I upload a photo that is <problem>
  Then the upload is rejected with a 422 low-quality-image error
  And I see the tip "<tip>" in plain language
  And I can retake or choose another photo

  Examples:
    | problem                   | tip                                    |
    | blurry                    | Hold still and tap to focus            |
    | too dark                  | Move to a brighter place, avoid shadows|
    | smaller than 1000 px side | Move closer so the page fills the frame|
```

## US-013 Warn on duplicate document (BR-016)
```gherkin
Scenario: Same file uploaded twice
  Given I already uploaded a file
  When I upload the same file again
  Then I see a duplicate warning (409 duplicate-document)
  And no new record is created

Scenario: Same visit date, facility and diagnosis <!-- claims-ok -->
  Given a record exists for a visit date, facility and diagnosis <!-- claims-ok -->
  When another upload reads the same three values
  Then I see a duplicate warning and no new record is created
```

## US-035 See processing progress (BR-013)
```gherkin
Scenario: Progress is shown while reading
  Given my upload was accepted
  When MediLens reads the record
  Then I see the steps "Received", "Reading", "Ready to review"
  And I can leave the page and return later

Scenario: Result is a draft
  When processing finishes
  Then the result is marked "draft, please review"
  And nothing appears on the body viewer until I confirm it
```
