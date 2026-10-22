"""LOINC loader. LIC-003. Expects CSV: loinc_num,long_common_name (check digit validated)."""

from .base import Loader

LOINC = Loader("LIC-003", "LOINC", "loinc_num", ("loinc_num", "long_common_name"))
load_loinc = LOINC.load
