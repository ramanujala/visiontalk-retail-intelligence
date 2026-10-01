from typing import Dict, Any, List
import json


def build_grounded_llm_context(
    image: Any,
    evidence_data: Optional[Dict[str, Any]] = None,
    expected_actual_data: Optional[Dict[str, Any]] = None,
    compliance_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Constructs a clean, structured context dictionary from authoritative backend analysis models.
    Removes raw binary payload data and isolates untrusted text strings.
    """
    # 1. Image metadata
    context: Dict[str, Any] = {
        "image": {
            "image_id": str(image.id),
            "original_filename": image.original_filename,
            "quality_score": image.quality_score,
            "quality_flags": image.quality_flags or [],
            "width": image.width,
            "height": image.height,
        },
        "observations": {
            "product_count": 0,
            "detected_products": [],
            "ocr_snippets": [],
        },
        "inventory_comparison": {
            "summary": {},
            "missing_products": [],
            "unexpected_products": [],
            "observed_products": [],
        },
        "compliance": {
            "summary": {},
            "findings": [],
        },
    }

    # 2. Canonical Evidence Data (Phase 6)
    if evidence_data:
        detections = evidence_data.get("detections", [])
        context["observations"]["product_count"] = len(detections)
        for det in detections:
            context["observations"]["detected_products"].append({
                "detection_id": det.get("id"),
                "class_name": det.get("class_name"),
                "confidence": round(det.get("confidence", 0.0), 3),
                "bounding_box": det.get("bbox"),
                "associated_text": det.get("associated_text"),
            })

        ocr_items = evidence_data.get("ocr_results", [])
        for ocr in ocr_items:
            # Wrap OCR text safely as untrusted content
            context["observations"]["ocr_snippets"].append({
                "ocr_id": ocr.get("id"),
                "untrusted_extracted_text": ocr.get("detected_text"),
                "confidence": round(ocr.get("confidence", 0.0), 3),
            })

    # 3. Expected vs Actual Inventory Data (Phase 7)
    if expected_actual_data:
        context["inventory_comparison"]["summary"] = {
            "total_expected_skus": expected_actual_data.get("total_expected_skus", 0),
            "total_expected_units": expected_actual_data.get("total_expected_units", 0),
            "total_observed_units": expected_actual_data.get("total_observed_units", 0),
            "missing_count": expected_actual_data.get("missing_count", 0),
            "low_stock_count": expected_actual_data.get("low_stock_count", 0),
            "excess_count": expected_actual_data.get("excess_count", 0),
            "unexpected_count": expected_actual_data.get("unexpected_count", 0),
        }
        for item in expected_actual_data.get("items", []):
            item_summary = {
                "product_code": item.get("product_code"),
                "product_name": item.get("product_name"),
                "expected_quantity": item.get("expected_quantity"),
                "observed_quantity": item.get("observed_quantity"),
                "status": item.get("status"),
            }
            if item.get("status") == "MISSING":
                context["inventory_comparison"]["missing_products"].append(item_summary)
            elif item.get("status") == "UNEXPECTED":
                context["inventory_comparison"]["unexpected_products"].append(item_summary)
            else:
                context["inventory_comparison"]["observed_products"].append(item_summary)

    # 4. Compliance Findings (Phase 8)
    if compliance_data:
        context["compliance"]["summary"] = compliance_data.get("summary", {})
        for finding in compliance_data.get("findings", []):
            context["compliance"]["findings"].append({
                "finding_id": finding.get("id"),
                "rule_name": finding.get("rule_name"),
                "rule_type": finding.get("rule_type"),
                "status": finding.get("status"),
                "severity": finding.get("severity"),
                "message": finding.get("message"),
                "details": finding.get("details", {}),
            })

    return context
