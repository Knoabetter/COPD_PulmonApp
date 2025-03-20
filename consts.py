from enum import Enum


class FORMATS(Enum):
    class OLD(Enum):
        FULL = 0
        ONLY_SPIROMETRY_WITH_POST = 1
        ONLY_SPIROMETRY_WITHOUT_POST = 2
    class NEW(Enum):
        FULL_WITH_POST = 3
        FULL_WITHOUT_POST = 4
        ONLY_SPIROMETRY_WITH_POST = 5
        ONLY_SPIROMETRY_WITHOUT_POST = 6


BASE_OLD_REGEX_FIELDS = {
        "Last Name": r"Last Name: ([\w\s-]+) Fi",
        "First Name": r"First Name: (\w+)",
        "ID": r"Identification: ([\d/]+)",
        "Date of Birth": r"Date of Birth: ([\d/]+)",
        "Sex": r"Sex: (F|M)",
        "Phone": r"Phone: (\b\d{10}\b)",
        "Smoker": r"Smoker: (\w+)? He",
        "Height": r"[Height\s:]{5,9} ([\d.,Olt-]+) [co]m",
        "Weight": r"[Weight\s:]{5,9} ([\d.,Olt-]+) [kg]",
        "Age": r"Age: ([\d]+) Years",
        "BMI": r"BMI: ([\d.,Olt-]+)",
        "Operator": r"Operator: ([a-zA-Z-]+)",
        "Spo2": r"[Spo02]{3,6} (\b\d{2,3}\b)",
        "Stage": r"Stage ([\d.,]+)",
        "MVV": r"[\nMVV]{4}\s+[\[\(\{c]{1,2}L/min[\]\)\}J]{1,2}\s+([\d.,Olt-]+)\s+([\d.,Olt-]+)\s+",
    }

OLD_FULL_BASE_REGEX_FIELDS = {
        "VC": r"[\nVCE]{3}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+%&3¢]{2}",
        "IC": r"[\nICe]{3}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+%&3¢]{2}",
        "ERV": r"[\nERV]{4}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+%&3¢]{2}",
        "ITGV": r"[\nITGV]{5}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+%&3¢]{2}",
        "RV": r"[\nRV]{3}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+%&3¢]{2}",
        "TLC": r"[\nTLC]{4}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+%&3¢]{2}",
        "RV % TLC": r"[\nRV]{3}[\s+t%&36s]{2}\s+[TLC]{3}\s+[\[\(\{c]%[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+%&3¢]{2}",
        "ITGV % TLC": r"[\nITGV]{5}[\s+t%&36s]{2}\s+[TLC]{3}\s+[\[\(\{c]%[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+%&3¢]{2}",
        "Hb": r"[\nHb]{3}\s+[\[\(\{c]g/100m[l1][\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+",
        "SR tot": r"[\nSR]{3}\s+tot\s+[\[\(\{c]kPa\*s[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+%&3¢]{2}",
        "SG tot": r"[\nSG]{3}\s+tot\s+[\[\(\{c]1/[\s+\[\(\{]+kPa\*s[\s+\]\)\}]+[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+%&3¢]{2}",
        "DLCO SB": r"[\nDLCO]{5}\s+SB\s+[\[\(\{c]{1,2}[mmol/min/kPa\s+]{12,16}[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+%&3¢]{2}",
        "DLCOc SB": r"[\nDLCO]{6}\s+SB\s+[\[\(\{c]{1,2}[mmol/min/kPa\s+]{12,16}[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+%&3¢]{2}",
        "DLCO/VA": r"[\nDLCO/VA]{8}\s+[\[\(\{c]{1,2}[mmol/min/kPa/L\s+]{14,19}[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+%&3¢]{2}",
        "DLCOc/V": r"[\nDLCO/V]{8}\s+[\[\(\{c]{1,2}[mmol/min/kPa/L\s+]{14,19}[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+%&3¢]{2}",
}

OLD_FULL_SPECIFIC_REGEX_FIELDS = {
                "Format": FORMATS.OLD.value.FULL,
                "Date": r"Date (\b\d{6}\b) (\b\d{6}\b)",
                "FVC": r"[\nFVCe]{4}\s+[\[\(\{c]{1,2}L[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)[\s+t%&36s]{2}",
                "FEV1": r"[\nFEVc]{4}\s+1\s+[\[\(\{c]{1,2}[IL]{1,2}[\]\)\}J]+\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)[\s+%]{2}",
                "FEV6": r"[\nFEV6c]{5}\s+[\[\(\{c]{1,2}L[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{2}",
                "FEV1 % FEV6": r"[\nFEV1c]{5}[\s+t%&36s]{1,3}[FEV6c]{4}\s+[\[\(\{c]{1,2}[%&]+[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{2}",
                "FEV 1 % FVC": r"[\nFEVc]{4}\s+1\s+[%3&]\s+[FVCe]{3}\s+[\[\(\{c]{1,2}[%&3][\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{2}",
                "PEF": r"[\nPEFc]{4}\s+[\[\(\{c]{1,2}L/s[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)[\s+t%&36s]{2}",
                "PIF": r"[\nPIF]{4}\s+[\[\(\{c]{1,2}L/s[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{2}",
                "MEF 75/25": r"[\nMEFc]{5}\s+[75/2]{5}\s+[\[\(\{c]{1,2}L/s[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)[\s+t%&36s]{2}",
                "MEF50": r"[\nMEFc]{4}\s+50\s+[\[\(\{c]{1,2}L/s[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)[\s+t%&36s]{2}",
                "MEF25": r"[\nMEFc]{4}\s+25\s+[\[\(\{c]{1,2}L/s[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)[\s+t%&36s]{2}",
            }

OLD_ONLY_SPIROMETRY_SPECIFIC_REGEX_FIELDS = {
                "Format": FORMATS.OLD.value.ONLY_SPIROMETRY,
                "Date": r"Date (\b\d{6}\b) (\b\d{6}\b)",
                "FVC": r"[\nFVCe]{4}\s+[\[\(\{c]{1,2}[IL]{1,2}[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)[\s+t%&36s]{2}",
                "FEV1": r"[\nFEVc]{4}\s+1\s+[\[\(\{c]{1,2}[IL]{1,2}[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)[\s+%]{2}",
                "FEV6": r"[\nFEV6c]{5}\s+[\[\(\{c]{1,2}L[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{2}",
                "FEV1 % FEV6": r"[\nFEV1c]{5}[\s+t%&36s]{1,3}[FEV6c]{4}\s+[\[\(\{c]{1,2}[%&ts]+[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{2}",
                "FEV 1 % FVC": r"[\nFEVc]{4}\s+1\s+[%3&]\s+[FVCe]{3}\s+[\[\(\{c]{1,2}[%&3][\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{2}",
                "PEF": r"[\nPEFc]{4}\s+[\[\(\{c]{1,2}L/s[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)[\s+t%&36s]{2}",
                "PIF": r"[\nPIF]{4}\s+[\[\(\{c]{1,2}L/s[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{2}",
                "MEF 75/25": r"[\nMEFc]{5}\s+[75/2]{5}\s+[\[\(\{c]{1,2}L/s[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)[\s+t%&36s]{2}",
                "MEF50": r"[\nMEFc]{4}\s+50\s+[\[\(\{c]{1,2}L/s[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)[\s+t%&36s]{2}",
                "MEF25": r"[\nMEFc]{4}\s+25\s+[\[\(\{c]{1,2}L/s[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)[\s+t%&36s]{2}",
                "VC": r"[\nVCE]{3}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+",
                "IC": r"[\nICe]{3}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+",
                "ERV": r"[\nERVc]{4}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+",
                "ITGV": r"[\nITGV]{5}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+",
                "RV": r"[\nRV]{3}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+",
                "TLC": r"[\nTLC]{4}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+",
                "RV % TLC": r"[\nRV]{3}[\s+t%&36s]{2}\s+[TLCe]{3}\s+[\[\(\{c]{1,2}%[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+",
                "ITGV % TLC": r"[\nITGV]{5}[\s+t%&36s]{2}\s+[TLCe]{3}\s+[\[\(\{c]{1,2}%[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+",
                "Hb": r"[\nHb]{3}\s+[\[\(\{c]g/100m[l1][\]\)\}J]{1,2}\s+",
                "SR tot": r"[\nSR]{3}\s+tot\s+[\[\(\{c]kPa\*s[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+",
                "SG tot": r"[\nSG]{3}\s+tot\s+[\[\(\{c]1/[\s+\[\(\{]+kPa\*s[\s+\]\)\}]+[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+",
                "DLCO SB": r"[\nDLCO]{5}\s+SB\s+[\[\(\{c]{1,2}[mmol/min/kPa\s+]{12,16}[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+",
                "DLCOc SB": r"[\nDLCO]{6}\s+SB\s+[\[\(\{c]{1,2}[mmol/min/kPa\s+]{12,16}[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+",
                "DLCO/VA": r"[\nDLCO/VA]{8}\s+[\[\(\{c]{1,2}[mmol/min/kPa/L\s+]{14,19}[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+",
                "DLCOc/V": r"[\nDLCO/V]{8}\s+[\[\(\{c]{1,2}[mmol/min/kPa/L\s+]{14,19}[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+",
            }

OLD_WITHOUT_POST_SPECIFIC_REGEX_FIELDS = {
            "Format": FORMATS.OLD.value.WITHOUT_POST,
            "Date": r"Date (\b\d{6}\b)",
            "FVC": r"[\nFVCe]{4}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}]\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{2}",
            "FEV1": r"[\nFEVc]{4}\s+1\s+[\[\(\{c]{1,2}[IL]{1,2}[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{2}",
            "FEV6": r"[\nFEV6c]{5}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}]\s+([\d.,Olt~-]+)[\s+t%&36s]{2}",
            "FEV1 % FEV6": r"[\nFEV1c]{5}[\s+t%&36s]{2}\s+[FEV6c]{4}\s+[\[\(\{c]{1,2}[%&]+[\]\)\}]\s+([\d.,Olt~-]+)[\s+t%&36s]{2}",
            "FEV 1 % FVC": r"[\nFEVc]{4}\s+1\s+[%3&]\s+[FVCe]{3}\s+[\[\(\{c]{1,2}[%&3]+[\]\)\}]\s+([\d.,Olt~-]+)\s+",
            "PEF": r"[\nPEFc]{4}\s+[\[\(\{c]{1,2}L/s[\]\)\}]\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{2}",
            "PIF": r"[\nPIF]{4}\s+[\[\(\{c]{1,2}L/s[\]\)\}]\s+([\d.,Olt~-]+)\s+",
            "MEF 75/25": r"[\nMEFc]{5}\s+[75/2]{5}\s+[\[\(\{c]{1,2}L/s[\]\)\}]\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{2}",
            "MEF50": r"[\nMEFc]{4}\s+50\s+[\[\(\{c]{1,2}L/s[\]\)\}]\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{2}",
            "MEF25": r"[\nMEFc]{4}\s+25\s+[\[\(\{c]{1,2}L/s[\]\)\}]\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{2}",
        }

IMPOSSIBLE_REGEX_FIELDS = {
            "Format": r"a(?=b)c",
            "Date": r"a(?=b)c",
            "FVC": r"a(?=b)c",
            "FEV1": r"a(?=b)c",
            "FEV6": r"a(?=b)c",
            "FEV1 % FEV6": r"a(?=b)c",
            "FEV 1 % FVC": r"a(?=b)c",
            "PEF": r"a(?=b)c",
            "PIF": r"a(?=b)c",
            "MMEF 75/25": r"a(?=b)c",
            "MEF50": r"a(?=b)c",
            "MEF25": r"a(?=b)c",
        }

BASE_NEW_REGEX_FIELDS = {
        "ID": r"[IDfV)l>:]{2,6} ([\d]{7,8})\s+[vw]",
        "Date of Birth": r"[Date of birth;:]{9,13} ([\d]{2}[/1][\d]{2}[/1][\d]{4})\s+",
        "Sex": r"[Gender':]{5,8} (F|M)",
        "Height": r"[Height:]{5,8} ([\dOlt~-]{3}) [coe]m",
        "Weight": r"[Weirght: ]{5,8} ([\d.,Olt~-]{2,3}) [kg]",
        "Age": r"[Age:;. ]{3,6} ([\d]+) Y",
        "BMI": r"[BMIl:; ]{3,6} ([\d.,Olt~-]+) k",
        "Ethnicity": r"[Ethnicity: ]{8,11} ([\w\s]+)\n",
        "Date": r"[Dateic:]{3,5} ([\d]{2})[/1]([\d]{2})[/1]([\d]{4})\s+",
        "Spo2": r"[o02=-]{3,5}(\b\d{2,3}\b)",
        "Smoker": r"[Smo0kecr=-]{6,8}(Yes|No)",
        "Stage": r"[Stagec=-]{5,7}(\d+)",
    }

NEW_ONLY_SPIROMETRY_WITHOUT_POST_SPECIFIC_REGEX_FIELDS = {
    "Format": FORMATS.NEW.value.ONLY_SPIROMETRY_WITHOUT_POST,
    "FVC": r"[\nFVCex]{6}\s+[\[\(\{c]3[\]\)\}J][\s+IL1]{0,3}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "FEV1": r"[\nFEVc1il]{5}\s+[\[\(\{c]3[\]\)\}J][\s+IL1]{0,3}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "FEV1 % FVC": r"[\nFEVc1il/]{7,10}\s+[\[\(\{c]3[\]\)\}J][\s+t%&346s]{0,3}\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+",
    "PEF": r"[\nPEFc]{4}\s+[\[\(\{c][3][\]\)\}J][\s+vi/s]{0,4}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "TEX": r"[\nt7%ex]{4}[\s+s]{0,2}\s+([\d.,Olt~-]+)\s+",
    "MEF25": r"[\nMEFc25sz]{5,7}\s+[\[\(\{c][3][\]\)\}J][\s+vit/s]{0,4}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "MEF50": r"[\nMEFc50so]{5,7}\s+[\[\(\{c][3][\]\)\}J][\s+vti/s]{0,4}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "MEF75": r"[\nMEFc75s]{5,7}\s+[\[\(\{c][3][\]\)\}J][\s+tvi/s]{0,4}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "MEF 75/25": r"[\nMEFc257sz-]{8,10}\s+[\[\(\{c][3][\]\)\}J][\s+tvi/s]{0,4}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
}

NEW_ONLY_SPIROMETRY_WITH_POST_SPECIFIC_REGEX_FIELDS = {
    "Format": FORMATS.NEW.value.ONLY_SPIROMETRY_WITH_POST,
    "FVC": r"[\nFVCex]{6}\s+[\[\(\{c]3[\]\)\}J][\s+IL1]{0,3}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+",
    "FEV1": r"[\nFEVc1il]{5}\s+[\[\(\{c]3[\]\)\}J][\s+IL1]{0,3}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+",
    "FEV 1 % FVC": r"[\nFEVc1il/]{7,10}\s+[\[\(\{c]3[\]\)\}J][\s+t%&346s]{0,3}\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+",
    "PEF": r"[PEFc]{3,4}\s+[\[\(\{c][3][\]\)\}J][\s+vi/s]{0,4}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+",
    "TEX": r"[t7%ex]{3,4}[\s+s]{0,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "MEF25": r"[MEFc25sz]{4,7}\s+[\[\(\{c][3][\]\)\}J][\s+tvi/s]{0,4}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+",
    "MEF50": r"[MEFc50so]{4,7}\s+[\[\(\{c][3][\]\)\}J][\s+tvi/s]{0,4}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+",
    "MEF75": r"[MEFc75s]{4,7}\s+[\[\(\{c][3][\]\)\}J][\s+tvi/s]{0,4}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+",
    "MEF 75/25": r"[MEFc257sz-]{7,10}\s+[\[\(\{c][3][\]\)\}J][\s+tvi/s]{0,4}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+",
}

NEW_FULL_WITH_POST_SPECIFIC_REGEX_FIELDS = {
    "Format": FORMATS.NEW.value.FULL_WITH_POST,
    "ERV": r"[\nERV]{3,4}\s+[\[\(\{c]3[\]\)\}J][#\s+IL1]{0,3}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+",
    "VC": r"[\nVCE]{3}\s+[\[\(\{c]3[\]\)\}J][\s+IL1]{0,3}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "IC": r"[\nec1il]{2,4}\s+[\[\(\{c]3[\]\)\}J][\s+t#%&346s]{0,4}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "TGV": r"[\nTGV]{3,4}\s+[\[\(\{c][3][\]\)\}J][\s+vil/s]{0,4}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "RV": r"[\nRV]{2,4}\s+[\[\(\{c][3][\]\)\}J][\s+vil/s]{0,4}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "TLC": r"[\nTLCe]{3,5}\s+[\[\(\{c][3][\]\)\}J][\s+tvi/s]{0,4}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "RV % TLC": r"[\nRV]{2,4}[\s+t%&36is]{2,4}[TLCe]{2,4}\s+[\[\(\{c][3][\]\)\}J][\s+t%&36s]{0,4}\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+",
    "TGV % TLC": r"[\nTGV]{3,5}[\s+t%&36is]{2,4}[TLCe]{2,4}\s+[\[\(\{c][3][\]\)\}J][\s+t%&36s]{0,4}\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+",
    "RAW": r"[\nRAW]{3,5}\s+[\[\(\{c][3][\]\)\}J][\s+kpa'wxf_lsi1\(\)\[\]\{\}/]{0,11}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "GAW": r"[\nGAW]{3,5}\s+[\[\(\{c][3][\]\)\}J][\s+k'wpalsi1\(\)\[\]\{\}/]{0,11}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "sRAW": r"[\nsRAW]{5,6}\s+[\[\(\{c][3][\]\)\}J][\s+kpa*#s]{0,7}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "DLCOc": r"[\nTLCO\(\[\{HB\)\]\}]{8,11}\s+[\[\(\{c][3][\]\)\}J][\s+molkpain14/\+]{0,15}\s+([\d.,Olt>-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "DLCOc/VA": r"[\nKCO\(\[\{HB\)\]\}]{7,10}\s+[\[\(\{c][3][\]\)\}J][\s+molkpain1/]{0,15}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "VA": r"[\nVA]{2,4}\s+[\[\(\{c][25sz]{0,3}[\]\)\}J][\s+ivt1]{0,4}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "VIN": r"[\nVIN1l]{4,6}[\s+li1]{0,4}\s+([\d.,Olt~-]+)\s+",
    "HB": r"[\nHB]{2,4}[\s+gdl1i/]{0,6}\s+([\d.,Olt~-]+)\s+",
    "tdiff": r"[\n\s+tdif.,]{6,10}[\s+s5]{0,4}\s+([\d.,Olt~-]+)\s+",
    "co-hb": r"[\ncohb=-]{5,8}[\s+t%&36s]{0,4}\s+([\dOlt~-]+)\s+",
}

NEW_FULL_WITHOUT_POST_SPECIFIC_REGEX_FIELDS = {
    "Format": FORMATS.NEW.value.FULL_WITHOUT_POST,
    "ERV": r"[\nERV]{3,4}\s+[\[\(\{c]3[\]\)\}J][#\s+IL1]{0,3}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "VC": r"[\nVCE]{3}\s+[\[\(\{c]3[\]\)\}J][\s+IL1]{0,3}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "IC": r"[\nec1il]{2,4}\s+[\[\(\{c]3[\]\)\}J][\s+t#%&346s]{0,4}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "TGV": r"[\nTGV]{3,4}\s+[\[\(\{c][3][\]\)\}J][\s+vil/s]{0,4}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "RV": r"[\nRV]{2,4}\s+[\[\(\{c][3][\]\)\}J][\s+vil/s]{0,4}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "TLC": r"[\nTLCe]{3,5}\s+[\[\(\{c][3][\]\)\}J][\s+tvi/s]{0,4}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "RV % TLC": r"[\nRV]{2,4}[\s+t%&36is]{2,4}[TLCe]{2,4}\s+[\[\(\{c][3][\]\)\}J][\s+t%&36s]{0,4}\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+",
    "TGV % TLC": r"[\nTGV]{3,5}[\s+t%&36is]{2,4}[TLCe]{2,4}\s+[\[\(\{c][3][\]\)\}J][\s+t%&36s]{0,4}\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+",
    "RAW": r"[\nRAW]{3,5}\s+[\[\(\{c][3][\]\)\}J][\s+kpa'wxf_lsi1\(\)\[\]\{\}/]{0,11}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "GAW": r"[\nGAW]{3,5}\s+[\[\(\{c][3][\]\)\}J][\s+k'wpalsi1\(\)\[\]\{\}/]{0,11}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "sRAW": r"[\nsRAW]{5,6}\s+[\[\(\{c][3][\]\)\}J][\s+kpa*#s]{0,7}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "DLCOc": r"[\nTLCO\(\[\{HB\)\]\}]{8,11}\s+[\[\(\{c][3][\]\)\}J][\s+molkpain14/\+]{0,15}\s+([\d.,Olt>-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "DLCOc/VA": r"[\nKCO\(\[\{HB\)\]\}]{7,10}\s+[\[\(\{c][3][\]\)\}J][\s+molkpain1/]{0,15}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "VA": r"[\nVA]{2,4}\s+[\[\(\{c][25sz]{0,3}[\]\)\}J][\s+ivt1]{0,4}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\dOlt~-]+)\s+",
    "VIN": r"[\nVIN1l]{4,6}[\s+li1]{0,4}\s+([\d.,Olt~-]+)\s+",
    "HB": r"[\nHB]{2,4}[\s+gdl1i/]{0,6}\s+([\d.,Olt~-]+)\s+",
    "tdiff": r"[\n\s+tdif.,]{6,10}[\s+s5]{0,4}\s+([\d.,Olt~-]+)\s+",
    "co-hb": r"[\ncohb=-]{5,8}[\s+t%&36s]{0,4}\s+([\dOlt~-]+)\s+",
}

TEXT_FIELDS = ["Format", "Last Name", "First Name", "Sex", "Operator", "Smoker"]
NUMERIC_VALIDATE_FIELDS = ["VC", "IC", "ERV", "ITGV", "RV", "TLC", "SR tot", "SG tot", "DLCO SB", "DLCOc SB", "DLCO/VA", "DLCOc/V", \
                           "FVC", "FEV1", "PEF",  "MEF 75/25", "MEF50", "MEF25", "RV % TLC", "ITGV % TLC",]
ONLY_DCHANGE_VALIDATIONS_FIELDS = ["FEV6", "PIF", "FEV1 % FEV6", "FEV 1 % FVC", "TEX"]

NUMERIC_WITH_POST_FIELDS = ["FVC", "FEV1", "PEF", "MEF 75/25", "MEF50", "MEF25", "MEF75"]
ROUND_ERROR_LEEWAY = 1.1

EXPAND_PRED_PRE_PERCENT_FIELDS = ["VC", "IC", "ERV", "ITGV", "RV", "TLC", "SR tot", "SG tot", "DLCO SB", "DLCOc SB", "DLCO/VA", "DLCOc/V", \
                           "MVV", "RV % TLC", "ITGV % TLC"]

DATABASE_FILE_NAME = "copd_extracted_data_trial.xlsx"

NEW_SPIROMETRY_FULL_IDENTIFIER = "[\nTLCOk0e\(\[\{HB\)\]\}]{8,11}"
WITH_POST_IDENTIFIER = "\s+[POST075]{3,6}\s+"
NEW_ONLY_SPIROMETRY_WITHOUT_POST_FORMAT_IDENTIFIER = r"Ref\s+Pre\s+[t%7xRef]{4,6}\s+Z"
NEW_ONLY_SPIROMETRY_WITH_POST_FORMAT_IDENTIFIER = r"[t%s&x7ksRef]{4,6}\s+[Post]{3,6}\s+[t%s&xks7Ref]{4,6}\s+"

NEW_NUMERIC_VALIDATE_FIELDS = ["FVC", "FEV1", "PEF",  "MEF 75/25", "MEF50", "MEF25", "MEF75",]

