# Extraction Schemas (v1)

All schemas share the `Field` wrapper so every value carries confidence and source.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://medilens.local/schemas/common.v1.json",
  "$defs": {
    "Source": {
      "type": "object",
      "additionalProperties": false,
      "required": ["page", "quote"],
      "properties": {
        "page": {"type": "integer", "minimum": 1},
        "bbox": {"type": "array", "items": {"type": "number"}, "minItems": 4, "maxItems": 4},
        "quote": {"type": "string", "maxLength": 300}
      }
    },
    "StringField": {
      "type": "object", "additionalProperties": false, "required": ["value", "confidence"],
      "properties": {"value": {"type": ["string", "null"]}, "confidence": {"type": "number", "minimum": 0, "maximum": 1}, "source": {"$ref": "#/$defs/Source"}}
    },
    "NumberField": {
      "type": "object", "additionalProperties": false, "required": ["value", "confidence"],
      "properties": {"value": {"type": ["number", "null"]}, "unit": {"type": ["string", "null"]}, "confidence": {"type": "number", "minimum": 0, "maximum": 1}, "source": {"$ref": "#/$defs/Source"}}
    },
    "DateField": {
      "type": "object", "additionalProperties": false, "required": ["value", "confidence"],
      "properties": {"value": {"type": ["string", "null"], "format": "date"}, "confidence": {"type": "number"}, "source": {"$ref": "#/$defs/Source"}}
    },
    "Encounter": {
      "type": "object", "additionalProperties": false,
      "properties": {"date": {"$ref": "#/$defs/DateField"}, "facility": {"$ref": "#/$defs/StringField"}, "department": {"$ref": "#/$defs/StringField"}}
    }
  }
}
```

## Dental (`dental.schema.v1`)
```json
{
  "type": "object", "additionalProperties": false, "required": ["encounter", "teeth"],
  "properties": {
    "encounter": {"$ref": "common.v1.json#/$defs/Encounter"},
    "dentition": {"type": "string", "enum": ["permanent", "deciduous", "mixed", "unknown"]},
    "teeth": {
      "type": "array",
      "items": {
        "type": "object", "additionalProperties": false, "required": ["fdi", "condition"],
        "properties": {
          "fdi": {"$ref": "common.v1.json#/$defs/StringField"},
          "surfaces": {"type": "array", "items": {"type": "string", "enum": ["O", "M", "D", "B", "L"]}},
          "condition": {"type": "string", "enum": ["caries", "missing", "filling", "crown", "implant", "root_canal", "pulpitis", "periapical_lesion", "impacted", "fracture", "other"]},
          "severity": {"type": ["string", "null"], "enum": ["monitor", "mild", "moderate", "severe", null]},
          "note": {"$ref": "common.v1.json#/$defs/StringField"}
        }
      }
    },
    "periodontal": {
      "type": "array",
      "items": {"type": "object", "additionalProperties": false, "properties": {"quadrant": {"type": "integer", "enum": [1, 2, 3, 4]}, "condition": {"$ref": "common.v1.json#/$defs/StringField"}}}
    }
  }
}
```

## Cardiology (`cardiology.schema.v1`)
```json
{
  "type": "object", "additionalProperties": false, "required": ["encounter", "diagnoses"],
  "properties": {
    "encounter": {"$ref": "common.v1.json#/$defs/Encounter"},
    "diagnoses": {
      "type": "array",
      "items": {
        "type": "object", "additionalProperties": false, "required": ["text"],
        "properties": {
          "text": {"$ref": "common.v1.json#/$defs/StringField"},
          "icd10_candidates": {"type": "array", "items": {"type": "object", "properties": {"code": {"type": "string"}, "score": {"type": "number"}}}},
          "site": {"$ref": "common.v1.json#/$defs/StringField"},
          "laterality": {"type": "string", "enum": ["left", "right", "bilateral", "midline", "unknown"]},
          "severity": {"type": ["string", "null"], "enum": ["monitor", "mild", "moderate", "severe", null]}
        }
      }
    },
    "observations": {
      "type": "array",
      "items": {
        "type": "object", "additionalProperties": false, "required": ["name", "value"],
        "properties": {
          "name": {"$ref": "common.v1.json#/$defs/StringField"},
          "value": {"$ref": "common.v1.json#/$defs/NumberField"},
          "reference_range": {"$ref": "common.v1.json#/$defs/StringField"},
          "loinc_hint": {"type": ["string", "null"]}
        }
      }
    },
    "procedures": {"type": "array", "items": {"$ref": "common.v1.json#/$defs/StringField"}}
  }
}
```

## Oncology (`oncology.schema.v1`)
```json
{
  "type": "object", "additionalProperties": false, "required": ["encounter", "primary"],
  "properties": {
    "encounter": {"$ref": "common.v1.json#/$defs/Encounter"},
    "primary": {
      "type": "object", "additionalProperties": false,
      "properties": {
        "site": {"$ref": "common.v1.json#/$defs/StringField"},
        "laterality": {"type": "string", "enum": ["left", "right", "bilateral", "midline", "unknown"]},
        "histology": {"$ref": "common.v1.json#/$defs/StringField"},
        "size_mm": {"$ref": "common.v1.json#/$defs/NumberField"},
        "grade": {"$ref": "common.v1.json#/$defs/StringField"}
      }
    },
    "tnm": {
      "type": "object", "additionalProperties": false,
      "properties": {"t": {"$ref": "common.v1.json#/$defs/StringField"}, "n": {"$ref": "common.v1.json#/$defs/StringField"}, "m": {"$ref": "common.v1.json#/$defs/StringField"}, "stage": {"$ref": "common.v1.json#/$defs/StringField"}, "edition": {"type": ["string", "null"]}}
    },
    "nodes": {"type": "array", "items": {"type": "object", "properties": {"station": {"$ref": "common.v1.json#/$defs/StringField"}, "involved": {"type": ["boolean", "null"]}}}},
    "metastases": {
      "type": "array",
      "description": "Only sites explicitly stated as metastasis in the record (BR-021).",
      "items": {"type": "object", "additionalProperties": false, "required": ["site"], "properties": {"site": {"$ref": "common.v1.json#/$defs/StringField"}, "stated_as": {"type": "string", "enum": ["confirmed", "suspected"]}}}
    },
    "treatments": {
      "type": "array",
      "items": {"type": "object", "properties": {"type": {"type": "string", "enum": ["surgery", "chemotherapy", "radiotherapy", "immunotherapy", "targeted", "hormonal", "other"]}, "date": {"$ref": "common.v1.json#/$defs/DateField"}, "note": {"$ref": "common.v1.json#/$defs/StringField"}}}
    }
  }
}
```

## Rules for schema changes
- New version file for any change; old versions remain for replay.
- Closed vocabularies as enums; free text only where unavoidable.
- `null` is the correct answer when the record does not say it.
