# Retail Analysis Logic & Compliance Scoring — VisionTalk Retail Intelligence

## 1. Overview

The Retail Analysis Engine executes purely deterministic business logic over Layer 2 Structured Evidence. It eliminates AI guesswork for counting, availability, spatial placement, price matching, and compliance scoring.

---

## 2. Core Deterministic Business Logic Modules

### 2.1 Product Availability & Inventory Counts
- **Total SKU Count**: Calculated directly via set aggregation of YOLO object detections:
  $$\text{Count}(SKU_k) = \sum_{o \in \text{Objects}} \mathbb{I}(\text{class\_name}(o) = SKU_k \land \text{conf}(o) \ge \tau)$$
  where $\tau = 0.50$ (configurable confidence threshold).

- **Missing Products Set**:
  $$\text{Missing} = E_{\text{skus}} \setminus D_{\text{skus}}$$
  where $E_{\text{skus}}$ is the set of expected planogram SKUs, and $D_{\text{skus}}$ is the set of detected SKUs.

- **Extra / Unauthorized Products Set**:
  $$\text{Extra} = D_{\text{skus}} \setminus E_{\text{skus}}$$

---

### 2.2 Placement & Planogram Alignment Logic
- **Spatial Order**: Objects on a shelf rail are sorted horizontally by bounding box centroid $x_c = \frac{x1 + x2}{2}$.
- **Sequence Verification**: Compares detected horizontal SKU order $[S_1, S_2, \dots, S_n]$ against expected planogram order using Longest Common Subsequence (LCS) edit distance.
- **Placement Discrepancies**: Any detected item whose relative index diverges beyond allowable tolerance $\pm \delta$ is flagged as misplaced.

---

### 2.3 Empty Shelf Space Region Detection
- Computes horizontal spatial gaps between adjacent detected product bounding boxes on the same shelf level:
  $$\Delta x = x1_{i+1} - x2_{i}$$
- If $\Delta x > \text{Threshold}_{\text{empty\_space}}$ (where threshold is proportional to average product width), an **Empty Shelf Region** is flagged with bounding box coordinates $(x2_i, y1_i, x1_{i+1}, y2_i)$.

---

### 2.4 Price Tag Verification Logic
- Spatial matching links detected Price Tag OCR boxes to the nearest SKU bounding box directly above it:
  $$\text{NearestSKU}(t) = \arg\min_{o \in \text{Objects}} \text{Distance}(\text{bbox}(t), \text{bbox}(o))$$
- Parsed price text is normalized to numeric floats and compared against expected planogram pricing:
  $$\text{PriceMismatch} = |\text{Price}_{\text{OCR}} - \text{Price}_{\text{Expected}}| > 0.01$$

---

## 3. Explainable Compliance Scoring Index

Compliance is evaluated as a weighted index ($0 \le S_{\text{compliance}} \le 100\%$):

$$S_{\text{compliance}} = w_{\text{avail}} \cdot S_{\text{avail}} + w_{\text{place}} \cdot S_{\text{place}} + w_{\text{price}} \cdot S_{\text{price}} + w_{\text{condition}} \cdot S_{\text{condition}} + w_{\text{quality}} \cdot S_{\text{quality}}$$

### Default Weight Configuration
| Factor | Weight ($w_i$) | Sub-Score Calculation Method ($S_i$) |
|---|---|---|
| **Product Availability** | 0.40 | $\frac{\text{Detected Expected SKUs}}{\text{Total Expected SKUs}} \times 100\%$ |
| **Placement Compliance** | 0.25 | $\frac{\text{Correctly Positioned SKUs}}{\text{Total Detected SKUs}} \times 100\%$ |
| **Price Verification** | 0.15 | $\frac{\text{Matching Price Tags}}{\text{Total Parsed Price Tags}} \times 100\%$ |
| **Shelf Condition** | 0.10 | $100\% - (\text{Empty Gap Penalty} \times \text{Gap Count})$ |
| **Image Quality** | 0.10 | OpenCV sharpness/blur assessment score |

> [!NOTE]
> Weights are fully configurable per company tenant. All sub-scores and intermediate math are logged in the database to guarantee 100% auditability.
