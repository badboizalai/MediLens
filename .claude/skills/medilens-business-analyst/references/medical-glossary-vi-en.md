# Medical Glossary VI – EN (seed)

Extend this list whenever a new term appears. Columns: Vietnamese · common abbreviation in records · English · note for extraction/mapping.

## Contents
1. Document types
2. Common abbreviations
3. Anatomy and laterality
4. Dental
5. Cardiology
6. Oncology
7. Labs and units

## 1. Document types
| Vietnamese | Abbr. | English | Note |
| --- | --- | --- | --- |
| Giấy ra viện | GRV | Discharge summary | Has diagnosis on discharge, treatment summary |
| Phiếu khám bệnh | — | Outpatient consultation form | Chief complaint, diagnosis |
| Bệnh án | BA | Medical record (inpatient) | Multi-page |
| Đơn thuốc | — | Prescription | Not used for dosing advice (BR-023) |
| Phiếu kết quả xét nghiệm | XN | Laboratory result | Observations with reference ranges |
| Kết quả giải phẫu bệnh | GPB | Pathology report | Histology, grade, margins |
| Phiếu chụp X-quang / CT / MRI | XQ, CLVT, CHT | Imaging report | Text report only (no DICOM in v1) |
| Siêu âm | SA | Ultrasound report | Organ, size, findings |
| Phiếu chỉ định | — | Order form | Usually low value |

## 2. Common abbreviations
| Abbr. | Vietnamese | English |
| --- | --- | --- |
| THA | Tăng huyết áp | Hypertension |
| ĐTĐ | Đái tháo đường | Diabetes mellitus |
| BTTMCB | Bệnh tim thiếu máu cục bộ | Ischaemic heart disease |
| NMCT | Nhồi máu cơ tim | Myocardial infarction |
| SPT / STM | Suy tim | Heart failure |
| COPD / BPTNMT | Bệnh phổi tắc nghẽn mạn tính | Chronic obstructive pulmonary disease |
| VPQ | Viêm phế quản | Bronchitis |
| K | Ung thư (carcinoma) | Cancer |
| UT | Ung thư | Cancer |
| TBMMN | Tai biến mạch máu não | Stroke |
| BN | Bệnh nhân | Patient |
| CĐ | Chẩn đoán | Diagnosis |
| TS | Tiền sử | History |
| P / T | Phải / Trái | Right / Left |
| HA | Huyết áp | Blood pressure |
| M | Mạch | Pulse |
| NĐ | Nhiệt độ | Temperature |
| XQ | X-quang | X-ray |

## 3. Anatomy and laterality
| Vietnamese | English | Mapping hint |
| --- | --- | --- |
| Thùy trên phổi phải | Right upper lobe | `lung_r_upper` |
| Thùy giữa phổi phải | Right middle lobe | `lung_r_middle` |
| Thùy dưới phổi trái | Left lower lobe | `lung_l_lower` |
| Gan (thùy phải/trái), hạ phân thùy | Liver (right/left lobe), segment | `liver_seg_<1-8>` |
| Thận phải / trái | Right / left kidney | `kidney_r` / `kidney_l` |
| Đại tràng lên / ngang / xuống / sigma | Ascending / transverse / descending / sigmoid colon | `colon_asc` … |
| Trực tràng | Rectum | `rectum` |
| Hạch cổ / nách / trung thất | Cervical / axillary / mediastinal lymph nodes | `ln_cervical_l` etc. |
| Hai bên | Bilateral | create two findings |

## 4. Dental (FDI notation)
| Vietnamese | English | Note |
| --- | --- | --- |
| Răng 36 | Tooth 36 (lower left first molar) | quadrant 3, position 6 |
| Sâu răng | Dental caries | surface letters O/M/D/B/L |
| Mất răng | Missing tooth | |
| Trám răng | Filling/restoration | material optional |
| Viêm tủy | Pulpitis | |
| Viêm nha chu | Periodontitis | per quadrant or tooth |
| Răng khôn mọc lệch | Impacted wisdom tooth | 18, 28, 38, 48 |
| Cấy ghép implant | Dental implant | |
| Mặt nhai / gần / xa / ngoài / trong | Occlusal / mesial / distal / buccal / lingual | O / M / D / B / L |

## 5. Cardiology
| Vietnamese | English | Region |
| --- | --- | --- |
| Thất trái / phải | Left / right ventricle | `heart_lv` / `heart_rv` |
| Nhĩ trái / phải | Left / right atrium | `heart_la` / `heart_ra` |
| Van hai lá / ba lá / động mạch chủ | Mitral / tricuspid / aortic valve | `valve_mitral` … |
| Động mạch vành phải / liên thất trước / mũ | RCA / LAD / LCx | `coronary_rca` … |
| Phân suất tống máu (EF) | Ejection fraction | Observation, % |
| Hẹp, hở van | Stenosis, regurgitation | severity scale |

## 6. Oncology
| Vietnamese | English | Note |
| --- | --- | --- |
| Khối u nguyên phát | Primary tumour | primary site |
| Di căn | Metastasis | only if stated (BR-021) |
| Giai đoạn | Stage | I–IV |
| Phân loại TNM | TNM classification | T (size/extent), N (nodes), M (metastasis) |
| Độ biệt hóa | Grade/differentiation | G1–G3 |
| Hóa trị / xạ trị / phẫu thuật | Chemotherapy / radiotherapy / surgery | treatment events on timeline |
| Diện cắt | Surgical margin | R0/R1/R2 |

## 7. Labs and units
| Vietnamese | English | LOINC hint | Unit |
| --- | --- | --- | --- |
| Đường huyết lúc đói | Fasting glucose | 1558-6 | mmol/L (VN) / mg/dL |
| HbA1c | Haemoglobin A1c | 4548-4 | % |
| Creatinin | Creatinine | 2160-0 | µmol/L / mg/dL |
| Mức lọc cầu thận (eGFR) | eGFR | 33914-3 | mL/min/1.73m² |
| Cholesterol toàn phần | Total cholesterol | 2093-3 | mmol/L |
| Men gan AST / ALT | AST / ALT | 1920-8 / 1742-6 | U/L |

LOINC codes above are hints to verify against the official LOINC table during data loading.
