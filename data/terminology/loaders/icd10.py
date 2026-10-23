"""ICD-10 (MoH Vietnam) loader. LIC-002. Expects CSV: code,title_vi[,title_en]."""

from .base import Loader

ICD10 = Loader("LIC-002", "ICD-10", "code", ("code", "title_vi"))
load_icd10 = ICD10.load
