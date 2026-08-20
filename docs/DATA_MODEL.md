# Data Model & Evidence Schema Specification — VisionTalk Retail Intelligence

## 1. Database Entity-Relationship Architecture

The PostgreSQL database enforces clean multi-tenant isolation, storing metadata and relational references, while raw images reside in storage.

```
+----------------+        +----------------+        +----------------+
|   Companies    | 1----* |     Users      |        |     Stores     |
+----------------+        +----------------+        +-------+--------+
        |                                                   |
        +---------------------------------------------------* 1
                                                            |
                                                            v
                                                    +----------------+
                                                    |     Images     |
                                                    +-------+--------+
                                                            |
                                                            v 1
                                                    +----------------+
                                                    | Analysis Runs  |
                                                    +-------+--------+
                                                            |
                 +------------------------------------------+------------------------------------------+
                 |                                          |                                          |
                 v *                                        v *                                        v *
        +----------------+                         +----------------+                         +----------------+
        |   Detections   |                         |  OCR Results   |                         |  Shelf Issues  |
        +----------------+                         +----------------+                         +----------------+
```

---

## 2. PostgreSQL Relational Schemas (SQLAlchemy Models)

### `companies`
- `id`: UUID (Primary Key)
- `name`: VARCHAR(255)
- `created_at`: TIMESTAMP WITH TIME ZONE

### `users`
- `id`: UUID (Primary Key)
- `company_id`: UUID (Foreign Key -> companies.id)
- `email`: VARCHAR(255) (Unique, Indexed)
- `hashed_password`: VARCHAR(255)
- `role`: VARCHAR(50) (`admin`, `auditor`, `manager`)

### `stores`
- `id`: UUID (Primary Key)
- `company_id`: UUID (Foreign Key -> companies.id)
- `store_code`: VARCHAR(50)
- `location_name`: VARCHAR(255)

### `images`
- `id`: UUID (Primary Key)
- `store_id`: UUID (Foreign Key -> stores.id)
- `file_path`: VARCHAR(512)
- `width`: INTEGER
- `height`: INTEGER
- `file_size_bytes`: BIGINT
- `uploaded_at`: TIMESTAMP WITH TIME ZONE

### `analysis_runs`
- `id`: UUID (Primary Key)
- `image_id`: UUID (Foreign Key -> images.id)
- `model_version`: VARCHAR(100)
- `compliance_score`: FLOAT
- `status`: VARCHAR(50) (`pending`, `completed`, `failed`)
- `evidence_json`: JSONB (Complete Layer 2 Evidence dump)
- `created_at`: TIMESTAMP WITH TIME ZONE

### `expected_products` (Planogram Expectations)
- `id`: UUID (Primary Key)
- `store_id`: UUID (Foreign Key -> stores.id)
- `shelf_section`: VARCHAR(100)
- `expected_skus`: JSONB (Array of SKU objects with expected counts, sequence, and pricing)

---

## 3. Layer 2 Evidence JSON Schema Specification

The canonical JSON structure passed between perception and reasoning layers:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "VisionTalkEvidence",
  "type": "object",
  "properties": {
    "image_id": { "type": "string", "format": "uuid" },
    "analysis_id": { "type": "string", "format": "uuid" },
    "timestamp": { "type": "string", "format": "date-time" },
    "model_versions": {
      "type": "object",
      "properties": {
        "detector": { "type": "string" },
        "ocr": { "type": "string" }
      },
      "required": ["detector", "ocr"]
    },
    "image_dimensions": {
      "type": "object",
      "properties": {
        "width": { "type": "integer" },
        "height": { "type": "integer" }
      }
    },
    "objects": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "object_id": { "type": "string" },
          "class_id": { "type": "integer" },
          "class_name": { "type": "string" },
          "confidence": { "type": "number" },
          "bbox": {
            "type": "object",
            "properties": {
              "x1": { "type": "number" },
              "y1": { "type": "number" },
              "x2": { "type": "number" },
              "y2": { "type": "number" }
            },
            "required": ["x1", "y1", "x2", "y2"]
          }
        },
        "required": ["object_id", "class_name", "confidence", "bbox"]
      }
    },
    "ocr": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "ocr_id": { "type": "string" },
          "text": { "type": "string" },
          "confidence": { "type": "number" },
          "bbox": {
            "type": "object",
            "properties": {
              "x1": { "type": "number" },
              "y1": { "type": "number" },
              "x2": { "type": "number" },
              "y2": { "type": "number" }
            }
          }
        }
      }
    }
  },
  "required": ["image_id", "analysis_id", "objects", "ocr"]
}
```
