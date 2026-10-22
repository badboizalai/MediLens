# MediLens VI–EN Glossary (v1)

Seeded from the BA skill `references/medical-glossary-vi-en.md` plus product terms from the plan. Codes (ICD-10, LOINC) are hints, verified by the Clinical Informaticist at data load. Product/UI wording must stay plain-language and never diagnose, dose or give prognosis (BR-023).

## 1. Product and process terms
| # | Vietnamese | English | Note |
| --- | --- | --- | --- |
| 1 | Hồ sơ sức khỏe | Health profile (PatientProfile) | Self or managed relative |
| 2 | Tài liệu y tế | Medical document | One upload, image or multi-page PDF |
| 3 | Trích xuất | Extraction | OCR + LLM; result is `draft` until confirmed (BR-013) |
| 4 | Bản nháp / Đã xác nhận | Draft / Confirmed | Only confirmed data shows in the viewer |
| 5 | Màn hình rà soát | Review screen | Original left, fields right |
| 6 | Độ tin cậy | Confidence | 0–1; below 0.7 must be confirmed (BR-012) |
| 7 | Chưa ánh xạ | Unmapped | `region = unmapped` (BR-015) |
| 8 | Vùng cơ thể | Body region (`region_code`) | Contract between data, API, assets, viewer |
| 9 | Phân hệ / Đơn vị chuyên khoa | Unit | Dental, Cardiology, Oncology in MVP |
| 10 | Khoa | Department | Level above Unit |
| 11 | Dòng thời gian | Timeline | Before/after comparison (BR-025) |
| 12 | Chia sẻ có thời hạn | Time-limited sharing | Default 7, max 90 days (BR-030) |
| 13 | Truy cập khẩn cấp (break-glass) | Break-glass access | Admin with logged reason (BR-006) |
| 14 | Sự đồng ý | Consent | Explicit, withdrawable (BR-002, BR-034) |
| 15 | Nhật ký kiểm toán | Audit log | Append-only (BR-035) |
| 16 | Bài viết kiến thức | Knowledge article | Sourced, reviewed content (BR-024) |
| 17 | Mức độ nghiêm trọng | Severity | Palette per BR-020 |
| 18 | Mô hình cơ thể 3D / sơ đồ 2D | 3D body model / 2D diagram | Viewer |
| 19 | Minh họa, không thay thế bác sĩ | Illustration, not a substitute for your doctor | Mandatory disclaimer wording |
| 20 | Số cấp cứu 115 | Emergency number 115 | Shown first on emergency intent (BR-023, BR-041) |

## 2. Document types
| # | Vietnamese | English | Note |
| --- | --- | --- | --- |
| 21 | Giấy ra viện (GRV) | Discharge summary | Diagnosis at discharge |
| 22 | Phiếu khám bệnh | Outpatient consultation form | Complaint, diagnosis |
| 23 | Bệnh án (BA) | Medical record (inpatient) | Multi-page |
| 24 | Đơn thuốc | Prescription | Never used for dosing advice (BR-023) |
| 25 | Phiếu kết quả xét nghiệm | Laboratory result | Observations with reference ranges |
| 26 | Kết quả giải phẫu bệnh (GPB) | Pathology report | Histology, grade, margins |
| 27 | Phiếu chụp X-quang / CT / MRI | Imaging report | Text report only in v1 |
| 28 | Siêu âm (SA) | Ultrasound report | Organ, size, findings |

## 3. Clinical abbreviations
| # | Vietnamese | English | Note |
| --- | --- | --- | --- |
| 29 | Bệnh nhân (BN) | Patient | |
| 30 | Chẩn đoán (CĐ) | Diagnosis | |
| 31 | Tiền sử (TS) | History | |
| 32 | Phải / Trái (P / T) | Right / Left | Laterality; "hai bên" = bilateral, create two findings |
| 33 | Huyết áp (HA) | Blood pressure | |
| 34 | Tăng huyết áp (THA) | Hypertension | |
| 35 | Đái tháo đường (ĐTĐ) | Diabetes mellitus | |
| 36 | Nhồi máu cơ tim (NMCT) | Myocardial infarction | |
| 37 | Suy tim | Heart failure | |
| 38 | Tai biến mạch máu não (TBMMN) | Stroke | |
| 39 | Ung thư (UT, K) | Cancer | |

## 4. Dental (FDI)
| # | Vietnamese | English | Note |
| --- | --- | --- | --- |
| 40 | Răng 36 | Tooth 36 (lower left first molar) | FDI quadrant 3, position 6 |
| 41 | Sâu răng | Dental caries | Surfaces O/M/D/B/L |
| 42 | Mất răng | Missing tooth | |
| 43 | Trám răng | Filling / restoration | |
| 44 | Viêm tủy | Pulpitis | |
| 45 | Viêm nha chu | Periodontitis | |
| 46 | Răng khôn mọc lệch | Impacted wisdom tooth | 18, 28, 38, 48 |
| 47 | Cấy ghép implant | Dental implant | Device glyph in viewer |
| 48 | Mặt nhai / gần / xa / ngoài / trong | Occlusal / mesial / distal / buccal / lingual | O / M / D / B / L |

## 5. Cardiology
| # | Vietnamese | English | Note |
| --- | --- | --- | --- |
| 49 | Thất trái / thất phải | Left / right ventricle | `heart_lv` / `heart_rv` |
| 50 | Nhĩ trái / nhĩ phải | Left / right atrium | `heart_la` / `heart_ra` |
| 51 | Van hai lá / ba lá / động mạch chủ | Mitral / tricuspid / aortic valve | `valve_mitral` … |
| 52 | Động mạch vành | Coronary artery | RCA / LAD / LCx |
| 53 | Phân suất tống máu (EF) | Ejection fraction | Observation, % |
| 54 | Hẹp van / hở van | Valve stenosis / regurgitation | Severity scale |
| 55 | Đặt stent | Stent placement | Device glyph |

## 6. Oncology
| # | Vietnamese | English | Note |
| --- | --- | --- | --- |
| 56 | Khối u nguyên phát | Primary tumour | |
| 57 | Di căn | Metastasis | Only if the record states it (BR-021) |
| 58 | Giai đoạn | Stage | I–IV |
| 59 | Phân loại TNM | TNM classification | T, N, M |
| 60 | Độ biệt hóa | Grade / differentiation | G1–G3 |
| 61 | Hạch bạch huyết | Lymph node | `ln_*` regions |
| 62 | Hóa trị / xạ trị / phẫu thuật | Chemotherapy / radiotherapy / surgery | Timeline events |
| 63 | Diện cắt | Surgical margin | R0/R1/R2 |

## 7. Labs and units
| # | Vietnamese | English | Note |
| --- | --- | --- | --- |
| 64 | Đường huyết lúc đói | Fasting glucose | LOINC 1558-6; mmol/L or mg/dL (BR-025) |
| 65 | HbA1c | Haemoglobin A1c | LOINC 4548-4; % |
| 66 | Creatinin | Creatinine | LOINC 2160-0 |
| 67 | Mức lọc cầu thận (eGFR) | eGFR | LOINC 33914-3 |
| 68 | Cholesterol toàn phần | Total cholesterol | LOINC 2093-3 |
| 69 | Men gan AST / ALT | AST / ALT | LOINC 1920-8 / 1742-6 |

## 8. Anatomy
| # | Vietnamese | English | Note |
| --- | --- | --- | --- |
| 70 | Thùy trên phổi phải | Right upper lobe | `lung_r_upper` |
| 71 | Thận phải / trái | Right / left kidney | `kidney_r` / `kidney_l` |
| 72 | Gan | Liver | `liver_seg_<1-8>` for segments |
| 73 | Trực tràng | Rectum | `rectum` |
