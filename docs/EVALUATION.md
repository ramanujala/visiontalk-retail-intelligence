# Model Evaluation & Metrics Strategy — VisionTalk Retail Intelligence

## 1. Overview

VisionTalk Retail Intelligence enforces strict empirical evaluation across Computer Vision (Object Detection), OCR, and Multimodal LLM outputs. Synthetic metrics, fake benchmarks, or unverified claims are strictly prohibited.

---

## 2. Computer Vision (YOLO) Metrics

Object detection accuracy is evaluated on annotated retail validation and test datasets (COCO & custom retail benchmarks).

### 2.1 Primary CV Metrics
- **Intersection over Union (IoU)**:
  $$\text{IoU} = \frac{\text{Area of Overlap}}{\text{Area of Union}}$$
- **Precision**:
  $$\text{Precision} = \frac{TP}{TP + FP}$$
- **Recall**:
  $$\text{Recall} = \frac{TP}{TP + FN}$$
- **Mean Average Precision (mAP@50)**: Mean Average Precision computed at an IoU threshold of 0.50.
- **mAP@50-95**: Mean Average Precision computed across IoU thresholds from 0.50 to 0.95 in steps of 0.05.
- **Inference Latency**: Average bounding box inference time per image in milliseconds (ms).

---

## 3. Optical Character Recognition (OCR) Metrics

OCR extraction quality is evaluated against ground-truth price tag labels:
- **Character Error Rate (CER)**:
  $$\text{CER} = \frac{S + D + I}{N}$$
  where $S$ is Substitutions, $D$ is Deletions, $I$ is Insertions, and $N$ is Total Ground Truth Characters.
- **Price Accuracy Index**: Percentage of price tags where the extracted numerical price exactly matches ground truth.

---

## 4. LLM Groundedness & Hallucination Metrics

Evaluation of generated explanations against structured evidence JSON:
- **Groundedness Score**: Percentage of factual claims in the generated text that directly correspond to facts present in the evidence JSON.
- **Hallucination Rate**: Percentage of generated claims that introduce non-existent SKUs, incorrect counts, or unverified price figures.
- **Answer Completeness**: Measure of whether all detected issues were accurately mentioned in the summary.

---

## 5. Error Analysis Taxonomy

To systematically drive iterative model improvements (Phase 16), all detection errors are categorized into standard failure modes:

| Error Category | Description | Mitigation Strategy |
|---|---|---|
| **Small Object Misses** | Tiny items on far background shelves undetected | High-resolution image slicing / tiling (SAHI) |
| **Severe Occlusion** | Products blocked by shelf rails or neighboring items | Synthetic occlusion data augmentation |
| **Glare & Reflection** | Bright store lighting obscuring price tags | OpenCV CLAHE / contrast preprocessing |
| **Visual Ambiguity** | Similar package designs (e.g., Flavour A vs Flavour B) | Multi-view aggregation & fine-tuned classes |
| **Blur & Motion** | Low-quality smartphone camera uploads | OpenCV sharpness validation & upload rejection |

---

## 6. Continuous Evaluation Workflow

```
Validation Image Dataset -> YOLO / OCR Pipeline -> Generate Evidence -> Compute Metrics -> Generate Confusion Matrix & Error Report -> Model Version Registry Update
```
