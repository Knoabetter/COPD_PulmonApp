from enum import Enum


class FORMATS:
    class OLD(Enum):
        FULL = "OLD_FULL"
        ONLY_SPIROMETRY_WITH_POST = "OLD_ONLY_SPIROMETRY_WITH_POST"
        ONLY_SPIROMETRY_WITHOUT_POST = "OLD_ONLY_SPIROMETRY_WITHOUT_POST"

    class NEW(Enum):
        FULL_WITH_POST = "NEW_FULL_WITH_POST"
        FULL_WITHOUT_POST = "NEW_FULL_WITHOUT_POST"
        ONLY_SPIROMETRY_WITH_POST = "NEW_ONLY_SPIROMETRY_WITH_POST"
        ONLY_SPIROMETRY_WITHOUT_POST = "NEW_ONLY_SPIROMETRY_WITHOUT_POST"

    class THIRD(Enum):
        FULL = "THIRD_FULL"


BASE_OLD_REGEX_FIELDS = {
    "Last Name": r"Last Name: ([\w\s-]+) Fi",
    "First Name": r"First Name: (\w+)",
    "ID": r"Identification: ([\d/]+)",
    "Date of Birth": r"Date of Birth:\s*([\d/]+)",
    "Sex": r"Sex: (F|M)",
    "Phone": r"Phone: (\b\d{10}\b)",
    "Smoker": r"Smoker: (\w+)? He",
    "Height": r"[Hh]eight:?\s*([\d]{3})\s*(?:cm|in|or)?",
    "Weight": r"[Weight\s:]{5,9} ([\d.,Olt-]+) [kg]",
    "Age": r"[Aa]ge:?\s*([\d]{1,3})\s*[Yy]ears",
    "BMI": r"BMI: ([\d.,Olt-]+)",
    "Operator": r"Operator: ([a-zA-Z-]+)",
    "Spo2": r"[Spo02]{3,6} (\b\d{2,3}\b)",
    "Stage": r"Stage ([\d.,]+)",
    "MVV": r"[\nMVV]{4}\s+[\[\(\{c]{1,2}L/min[\]\)\}J]{1,2}\s+([\d.,Olt-]+)\s+([\d.,Olt-]+)\s+",
}

OLD_FULL_BASE_REGEX_FIELDS = {
    "VC": r"[\nVCE]{3}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+%&3¢]{2}",
    "IC": r"[\nICe]{3}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+%&3¢]{2}",
    "ERV": r"[\nERV]{4}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+%&3¢]{2}",
    "ITGV": r"[\nITGV]{5}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+%&3¢]{2}",
    "RV": r"[\nRV]{3}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+%&3¢]{2}",
    "TLC": r"[\nTLC]{4}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+%&3¢]{2}",
    "RV % TLC": r"[\nRV]{3}[\s+t%&36s]{2}\s+[TLC]{3}\s+[\[\(\{c]%[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+%&3¢]{2}",
    "ITGV % TLC": r"[\nITGV]{5}[\s+t%&36s]{2}\s+[TLC]{3}\s+[\[\(\{c]%[\]\)\}JjBbh]{0,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+%&3¢]{2}",
    "Hb": r"[\nHb]{3}\s+[\[\(\{c]g/100m[l1][\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+",
    "SR tot": r"[\nSR]{3}\s+tot\s+[\[\(\{c]kPa\*s[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+%&3¢]{2}",
    "SG tot": r"[\nSG]{3}\s+tot\s+[\[\(\{c]1/[\s+\[\(\{]+kPa\*s[\s+\]\)\}]+[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+%&3¢]{2}",
    "DLCO SB": r"[\nDLCO]{5}\s+SB\s+[\[\(\{c]{1,2}[mmol/min/kPa\s+]{12,16}[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+%&3¢]{2}",
    "DLCOc SB": r"[\nDLCO]{6}\s+SB\s+[\[\(\{c]{1,2}[mmol/min/kPa\s+]{12,16}[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+%&3¢]{2}",
    "DLCO/VA": r"[\nDLCO/VA]{8}\s+[\[\(\{c]{1,2}[mmol/min/kPa/L\s+]{14,19}[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+%&3¢]{2}",
    "DLCOc/V": r"[\nDLCO/V]{8}\s+[\[\(\{c]{1,2}[mmol/min/kPa/L\s+]{14,19}[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+%&3¢]{2}",
}

OLD_FULL_SPECIFIC_REGEX_FIELDS = {
    "Format": FORMATS.OLD.FULL.value,
    "Date": r"Date (\b\d{6}\b) (\b\d{6}\b)",
    "FVC": r"[\nFVCve ]{3,4}\s+[\[(\{c]{1,2}L[\])\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)[\s+t%&36s]{1,3}",
    "FEV1": r"[\nFEVc]{3,4}\s*[1iI]\s+[\[\(\{c]{1,2}[ILulhbtrJ1%]{1,3}[\]\)\}JjBbh]{0,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)[\s+%]{2}",
    "FEV6": r"[\nFEV6c]{5}\s+[\[\(\{c]{1,2}L[\]\)\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{2}",
    "FEV1 % FEV6": r"[\nFEV1c]{5}[\s+t%&36s]{1,3}[FEV6c]{4}\s+[\[\(\{c]{1,2}[%&]+[\]\)\}JjBbh]{0,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{2}",
    "FEV 1 % FVC": r"[\nFEVcP]{4}\s+1\s+[%3&]\s+[FVCe]{3}\s+[\[\(\{c]{1,2}[%&3¥][\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s;|]+([\d.,Olst~-]+)[\s+t%&36s]{0,3}",
    "PEF": r"[\nPEFc]{4}\s+[\[\(\{c]{1,2}L/s[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+t%&36s]{1,3}([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+t%&36s]{1,3}([\d.,Olst~-]+)[\s+t%&36s]{2}",
    "PIF": r"[\nPIF]{4}\s+[\[\(\{c]{1,2}L/s[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+t%&36s]{2}",
    "MEF 75/25": r"[\nMEFc]{5}\s+[75/2]{5}\s+[\[\(\{c]{1,2}L/s[\]\)\}JjBbh]{0,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+t%&36s]{1,3}([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+t%&36s]{1,3}([\d.,Olst~-]+)[\s+t%&36s]{2}",
    "MEF50": r"[\nMEFc]{4}\s+50\s+[\[\(\{c]{1,2}L/s[\]\)\}JjBbh]{0,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+t%&36s]{1,3}([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+t%&36s]{1,3}([\d.,Olst~-]+)[\s+t%&36s]{2}",
    "MEF25": r"[\nMEFc]{4}\s+25\s+[\[\(\{c]{1,2}L/s[\]\)\}JjBbh]{0,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+t%&36s]{1,3}([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+t%&36s]{1,3}([\d.,Olst~-]+)[\s+t%&36s]{2}",
}

OLD_ONLY_SPIROMETRY_SPECIFIC_REGEX_FIELDS = {
    "Format": FORMATS.OLD.ONLY_SPIROMETRY_WITH_POST.value,
    "Date": r"Date (\b\d{6}\b) (\b\d{6}\b)",
    "FVC": r"[\nFVCe]{3,4}\s+[\[(\{c]{1,2}[IL]{1,2}[\])\}J]{1,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)[\s+t%&36s]{2}",
    "FEV1": r"[\nFEVc]{4}\s+[1iI]\s+[\[\(\{c]{1,2}[ILulhbtrJ1%]{1,3}[\]\)\}JjBbh]{0,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{1,3}([\d.,Olt~-]+)[\s+%]{2}",
    "FEV6": r"[\nFEV6c]{5}\s+[\[\(\{c]{1,2}L[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+t%&36s]{2}",
    "FEV1 % FEV6": r"[\nFEV1c]{5}[\s+t%&36s]{1,3}[FEV6c]{4}\s+[\[\(\{c]{1,2}[%&ts]+[\]\)\}JjBbh]{0,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+t%&36s]{2}",
    "FEV 1 % FVC": r"[\nFEVcP]{4}\s+1\s+[%3&]\s+[FVCe]{3}\s+[\[\(\{c]{1,2}[%&3¥][\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s;|]+([\d.,Olst~-]+)[\s+t%&36s]{0,3}",
    "PEF": r"[\nPEFc]{4}\s+[\[\(\{c]{1,2}L/s[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+t%&36s]{1,3}([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+t%&36s]{1,3}([\d.,Olst~-]+)[\s+t%&36s]{2}",
    "PIF": r"[\nPIF]{4}\s+[\[\(\{c]{1,2}L/s[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+t%&36s]{2}",
    "MEF 75/25": r"[\nMEFc]{5}\s+[75/2]{5}\s+[\[\(\{c]{1,2}L/s[\]\)\}JjBbh]{0,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+t%&36s]{1,3}([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+t%&36s]{1,3}([\d.,Olst~-]+)[\s+t%&36s]{2}",
    "MEF50": r"[\nMEFc]{4}\s+50\s+[\[\(\{c]{1,2}L/s[\]\)\}JjBbh]{0,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+t%&36s]{1,3}([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+t%&36s]{1,3}([\d.,Olst~-]+)[\s+t%&36s]{2}",
    "MEF25": r"[\nMEFc]{4}\s+25\s+[\[\(\{c]{1,2}L/s[\]\)\}JjBbh]{0,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+t%&36s]{1,3}([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+t%&36s]{1,3}([\d.,Olst~-]+)[\s+t%&36s]{2}",
    "VC": r"[\nVCE]{3}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "IC": r"[\nICe]{3}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "ERV": r"[\nERVc]{4}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "ITGV": r"[\nITGV]{5}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "RV": r"[\nRV]{3}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "TLC": r"[\nTLC]{4}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "RV % TLC": r"[\nRV]{3}[\s+t%&36s]{2}\s+[TLCe]{3}\s+[\[\(\{c]{1,2}%[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "ITGV % TLC": r"[\nITGV]{5}[\s+t%&36s]{2}\s+[TLCe]{3}\s+[\[\(\{c]{1,2}%[\]\)\}JjBbh]{0,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "Hb": r"[\nHb]{3}\s+[\[\(\{c]g/100m[l1][\]\)\}J]{1,2}\s+",
    "SR tot": r"[\nSR]{3}\s+tot\s+[\[\(\{c]kPa\*s[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "SG tot": r"[\nSG]{3}\s+tot\s+[\[\(\{c]1/[\s+\[\(\{]+kPa\*s[\s+\]\)\}]+[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "DLCO SB": r"[\nDLCO]{5}\s+SB\s+[\[\(\{c]{1,2}[mmol/min/kPa\s+]{12,16}[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "DLCOc SB": r"[\nDLCO]{6}\s+SB\s+[\[\(\{c]{1,2}[mmol/min/kPa\s+]{12,16}[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "DLCO/VA": r"[\nDLCO/VA]{8}\s+[\[\(\{c]{1,2}[mmol/min/kPa/L\s+]{14,19}[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "DLCOc/V": r"[\nDLCO/V]{8}\s+[\[\(\{c]{1,2}[mmol/min/kPa/L\s+]{14,19}[\]\)\}J]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
}

OLD_WITHOUT_POST_SPECIFIC_REGEX_FIELDS = {
    "Format": FORMATS.OLD.ONLY_SPIROMETRY_WITHOUT_POST.value,
    "Date": r"Date (\b\d{6}\b)",
    "FVC": r"[\nFVCve]{3,4}\s+[\[\(\{c]{1,2}[ILulhbtrJ1]{1,3}[\]\)\}Jy]{0,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{2}",
    "FEV1": r"[\nFEVc]{4}\s+[1iI]\s+[\[\(\{c]{1,2}[ILulhbtrJ1%]{1,3}[\]\)\}JjBbhy]{0,2}\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)\s+([\d.,Olt~-]+)[\s+t%&36s]{2}",
    "FEV6": r"[\nFEV6c]{5}\s+[\[\(\{c]{1,2}[IL]+[\]\)\}]\s+([\d.,Olst~-]+)[\s+t%&36s]{2}",
    "FEV1 % FEV6": r"[\nFEV1c]{5}[\s+t%&36s]{2}\s+[FEV6c]{4}\s+[\[\(\{c]{1,2}[%&]+[\]\)\}JjBbh]{0,2}\s+([\d.,Olst~-]+)[\s+t%&36s]{2}",
    "FEV 1 % FVC": r"[\nFEVcP]{4}\s+1\s+[%3&]\s+[FVCe]{3}\s+[\[\(\{c]{1,2}[%&3¥]+[\]\)\}Js38]{0,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+t%&36s]*",
    "PEF": r"[\nPEFc]{4}\s+[\[\(\{c]{1,2}L/s[\]\)\}]\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+t%&36s]{2}",
    "PIF": r"[\nPIF]{4}\s+[\[\(\{c]{1,2}L/s[\]\)\}]\s+([\d.,Olst~-]+)\s+",
    "MEF 75/25": r"[\nMEFc]{5}\s+[75/2]{5}\s+[\[\(\{c]{1,2}L/s[\]\)\}JjBbh]{0,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+t%&36s]{2}",
    "MEF50": r"[\nMEFc]{4}\s+50\s+[\[\(\{c]{1,2}L/s[\]\)\}JjBbh]{0,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+t%&36s]{2}",
    "MEF25": r"[\nMEFc]{4}\s+25\s+[\[\(\{c]{1,2}L/s[\]\)\}JjBbh]{0,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[\s+t%&36s]{2}",
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
    "ID": r"(?:(?:\n)|[IDfV)l>:]{2,6})\s*([\d]{6,8})\s+[vw]",
    "Date of Birth": r"[Date of birth;:]{9,13} ([\d]{2}[/1][\d]{2}[/1][\d]{4})\s+",
    "Sex": r"[Gender':]{5,8} (F|M)",
    "Height": r"([1lIi]\d{2}|2[0-2]\d)\s*[coe]m",
    "Weight": r"[Weairght: ]{5,8} ([\d.,Olst~-]{2,3}) [kg]",
    "Age": r"[Age:;. ]{3,6} ([\d]+) Y",
    "BMI": r"[BMIl:; ]{3,6} ([\d.,Olst~-]+) k",
    "Ethnicity": r"[Ethnicity: ]{8,11} ([\w\s]+)\n",
    "Date": r"[Dat&eic:]{3,5} ([\d]{2})[/1]([\d]{2})[/1]([\d]{4})\s+",
    "Spo2": r"[po 02=-]{3,6}(\b\d{2,3}\b)",
    "Smoker": r"[Smo 0kecr=-]{6,9}(Yes|No)",
    "Stage": r"[St agec=-]{5,8}(\d+)",
}

NEW_ONLY_SPIROMETRY_WITHOUT_POST_SPECIFIC_REGEX_FIELDS = {
    "Format": FORMATS.NEW.ONLY_SPIROMETRY_WITHOUT_POST.value,
    "FVC": r"[\nFVCex]{3,6}\s+[\[\(\{c]3[\]\)\}J][\s+IL1]{0,3}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "FEV1": r"[\nFEVc1ilI]{4,6}\s+[\[\(\{c]3[\]\)\}J][\s+IL1]{0,3}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "FEV 1 % FVC": r"[\nFEVc1ilIC/]{7,10}\s+[\[\(\{c]3[\]\)\}J][\s+t%&346s]{0,3}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "PEF": r"[\nPEFc]{4}\s+[\[\(\{c][3][\]\)\}J][\s+vi></s]{0,4}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "TEX": r"[\nt7%ex]{4}[\s+s]{0,2}\s+([\d.,Olst~-]+)\s+",
    "MEF25": r"[\nMEFc25sz]{5,7}\s+[\[\(\{c][3][\]\)\}J][\s+vit></s]{0,4}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "MEF50": r"[\nMEFc50so]{5,7}\s+[\[\(\{c][3][\]\)\}J][\s+vti></s]{0,4}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "MEF75": r"[\nMEFc75s]{5,7}\s+[\[\(\{c][3][\]\)\}J][\s+tvi></s]{0,4}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "MEF 75/25": r"[\nMEFc257sz-]{8,10}\s+[\[\(\{c][3][\]\)\}J][\s+tvi></s]{0,4}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
}

NEW_ONLY_SPIROMETRY_WITH_POST_SPECIFIC_REGEX_FIELDS = {
    "Format": FORMATS.NEW.ONLY_SPIROMETRY_WITH_POST.value,
    "FVC": r"[\nFVCex]{3,6}\s+[\[\(\{c]3[\]\)\}J][\s+IL1]{0,3}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)(?:\s+([\d.,Olst~-]+))?(?:\s+([\d.,Olst~-]+))?",
    "FEV1": r"[\nFEVc1ilI]{4,6}\s+[\[\(\{c]3[\]\)\}J][\s+IL1]{0,3}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "FEV 1 % FVC": r"[\nFEVc1ilIC/]{7,10}\s+[\[\(\{c]3[\]\)\}J][\s+t%&346s]{0,3}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)(?:\s+([\d.,Olst~-]+))?(?:\s+([\d.,Olst~-]+))?\s+",
    "PEF": r"[PEFc]{3,4}\s+[\[\(\{c][3][\]\)\}J][\s+vi/s]{0,4}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "TEX": r"[t7%ex]{3,4}[\s+s]{0,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "MEF25": r"[MEFc25sz]{4,7}\s+[\[\(\{c][3][\]\)\}J][\s+tvi<>/s]{0,4}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "MEF50": r"[MEFc50so]{4,7}\s+[\[\(\{c][3][\]\)\}J][\s+tvi></s]{0,4}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "MEF75": r"[MEFc75s]{4,7}\s+[\[\(\{c][3][\]\)\}J][\s+tvi></s]{0,4}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "MEF 75/25": r"[MEFc257sz-]{7,10}\s+[\[\(\{c][3][\]\)\}J][\s+tvi></s]{0,4}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
}

NEW_FULL_WITH_POST_SPECIFIC_REGEX_FIELDS = {
    "Format": FORMATS.NEW.FULL_WITH_POST.value,
    "ERV": r"[\nERV]{3,4}\s+[\[\(\{c]3[\]\)\}J][#\s+IL1]{0,3}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "VC": r"[\nVCE]{3}\s+[\[\(\{c]3[\]\)\}J][\s+IL1]{0,3}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "IC": r"[\nec1il]{2,4}\s+[\[\(\{c]3[\]\)\}J][\s+t#%&346s]{0,4}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "TGV": r"[\nTGV]{3,4}\s+[\[\(\{c][3][\]\)\}J][\s+vil/s]{0,4}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "RV": r"\nRV\s+[\[\(\{c][3][\]\)\}J][\s+vil/s]{0,4}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "TLC": r"\nTLC\s+[\[\(\{c][3][\]\)\}J][\s+tvi/s]{0,4}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "RV % TLC": r"[\nRV]{2,4}[\s+t%&36is]{2,4}[TLCe]{2,4}\s+[\[\(\{c][3][\]\)\}J][\s+t%&36s]{0,4}\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+",
    "TGV % TLC": r"[\nTGV]{3,5}[\s+t%&36is]{2,4}[TLCe]{2,4}\s+[\[\(\{c][3][\]\)\}J][\s+t%&36s]{0,4}\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+",
    "RAW": r"[\nRAW]{3,5}\s+[\[\(\{c][3][\]\)\}J][\s+kpa'wxf_lsi1\(\)\[\]\{\}/]{0,11}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "GAW": r"[\nGAW]{3,5}\s+[\[\(\{c][3][\]\)\}J][\s+k'wpalsi1\(\)\[\]\{\}/]{0,11}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "sRAW": r"[\nsRAW]{5,6}\s+[\[\(\{c][3][\]\)\}J][\s+kpa*#s]{0,7}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "DLCOc": r"[\nTLCO\(\[\{HB\)\]\}]{8,11}\s+[\[\(\{c][3][\]\)\}J][\s+molkp;?'ain14/\+-]{0,15}[\s+>]{1,2}([\d.,Olt-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "DLCOc/VA": r"[\nKCO\(\[\{HB\)\]\}]{7,10}\s+[\[\(\{c][3][\]\)\}J][\s+molkp;?'ain1/]{0,15}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "VA": r"[\nVA]{2,4}\s+[\[\(\{c][25sz]{0,3}[\]\)\}J][\s+ivt1]{0,4}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "VIN": r"[\nVIN1l]{4,6}[\s+li1]{0,4}\s+([\d.,Olst~-]+)\s+",
    "HB": r"[\nHB]{2,4}[\s+gsdl1i/]{0,6}\s+([\d.,Olst~-]+)\s+",
    "tdiff": r"[\n\s+tdif.,:]{6,10}[\s+s5]{0,4}\s+([\d.,Olst~-]+)\s+",
    "co-hb": r"[\ncohb=-]{5,8}[\s+t%&36s]{0,4}\s+([\dOlt~-]+)\s+",
}

NEW_FULL_WITHOUT_POST_SPECIFIC_REGEX_FIELDS = {
    "Format": FORMATS.NEW.FULL_WITHOUT_POST.value,
    "ERV": r"[\nERV]{3,4}\s+[\[\(\{c]3[\]\)\}J][#\s+IL1]{0,3}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "VC": r"[\nVCE]{3}\s+[\[\(\{c]3[\]\)\}J][\s+IL1]{0,3}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "IC": r"[\nec1il]{2,4}\s+[\[\(\{c]3[\]\)\}J][\s+t#%&346s]{0,4}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "TGV": r"[\nTGV]{3,4}\s+[\[\(\{c][3][\]\)\}J][\s+vil/s]{0,4}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "RV": r"\nRV\s+[\[\(\{c][3][\]\)\}J][\s+vil/s]{0,4}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "TLC": r"\nTLC\s+[\[\(\{c][3][\]\)\}J][\s+tvi/s]{0,4}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "RV % TLC": r"[\nRV]{2,4}[\s+t%&36is]{2,4}[TLCe]{2,4}\s+[\[\(\{c][3][\]\)\}J][\s+t%&36s]{0,4}\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+",
    "TGV % TLC": r"[\nTGV]{3,5}[\s+t%&36is]{2,4}[TLCe]{2,4}\s+[\[\(\{c][3][\]\)\}J][\s+t%&36s]{0,4}\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+([\dOlt~-]+)\s+",
    "RAW": r"[\nRAW]{3,5}\s+[\[\(\{c][3][\]\)\}J][\s+kpa'wxf_lsi1\(\)\[\]\{\}/]{0,11}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "GAW": r"[\nGAW]{3,5}\s+[\[\(\{c][3][\]\)\}J][\s+k'wpalsi1\(\)\[\]\{\}/]{0,11}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "sRAW": r"[\nsRAW]{5,6}\s+[\[\(\{c][3][\]\)\}J][\s+kpa*#s]{0,7}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "DLCOc": r"[\nTLCO\(\[\{HB\)\]\}]{8,11}\s+[\[\(\{c][3][\]\)\}J][\s+molkpain14/\+]{0,15}[\s+>]{1,2}([\d.,Olt-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "DLCOc/VA": r"[\nKCO\(\[\{HB\)\]\}]{7,10}\s+[\[\(\{c][3][\]\)\}J][\s+molkpain1/]{0,15}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "VA": r"[\nVA]{2,4}\s+[\[\(\{c][25sz]{0,3}[\]\)\}J][\s+ivt1]{0,4}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+",
    "VIN": r"[\nVIN1l]{4,6}[\s+li1]{0,4}\s+([\d.,Olst~-]+)\s+",
    "HB": r"[\nHB]{2,4}[\s+gdl1i/]{0,6}\s+([\d.,Olst~-]+)\s+",
    "tdiff": r"[\n\s+tdif.,]{6,10}[\s+s5]{0,4}\s+([\d.,Olst~-]+)\s+",
    "co-hb": r"[\ncohb=-]{5,8}[\s+t%&36s]{0,4}\s+([\dOlt~-]+)\s+",
}

TEXT_FIELDS = ["Format", "Last Name", "First Name", "Sex", "Operator", "Smoker"]
NUMERIC_VALIDATE_FIELDS = ["VC", "IC", "ERV", "ITGV", "RV", "TLC", "SR tot", "SG tot", "DLCO SB", "DLCOc SB", "DLCO/VA",
                           "DLCOc/V", "FVC", "FEV1", "PEF", "PIF", "FEV6", "FEV1 % FEV6", "FEV 1 % FVC", "TEX",
                           "MEF 75/25", "MEF50", "MEF25", "RV % TLC", "ITGV % TLC", ]
ONLY_DCHANGE_VALIDATIONS_FIELDS = ["FEV6", "PIF", "FEV1 % FEV6", "FEV 1 % FVC", "TEX"]

NUMERIC_WITH_POST_FIELDS = ["FVC", "FEV1", "PEF", "MEF 75/25", "MEF50", "MEF25", "MEF75", "ERV", "FEV 1 % FVC", "FEV6"]
ROUND_ERROR_LEEWAY = 1.1

EXPAND_PRED_PRE_PERCENT_FIELDS = ["VC", "IC", "ITGV", "RV", "TLC", "SR tot", "SG tot", "DLCO SB", "DLCOc SB",
                                  "DLCO/VA", "DLCOc/V", \
                                  "MVV", "RV % TLC", "ITGV % TLC", "VA", "sRAW", "RAW", "GAW"]

DATABASE_FILE_NAME = "copd_extracted_data_trial.xlsx"

NEW_SPIROMETRY_FULL_IDENTIFIER = r"[\nTLCOk0e\(\[\{HB\)\]\}]{8,11}"
WITH_POST_IDENTIFIER = r"\s+[POST075]{3,6}\s+"
NEW_ONLY_SPIROMETRY_WITHOUT_POST_FORMAT_IDENTIFIER = r"Ref\s+Pre\s+[t%7xRef]{4,6}\s+Z"

NEW_FORMAT_IDENTIFIER = r"[Refct%]{3,5}\s+[Prec]{3,4}"
OLD_FORMAT_IDENTIFIER =r"[Precd]{3,4}\s+[LIN1]{3,4}\s+P"


NEW_NUMERIC_VALIDATE_FIELDS = ["FVC", "FEV1", "PEF", "PIF", "MEF 75/25", "MEF50", "MEF25", "MEF75", "ERV", "VC", "IC", "TGV",
                               "RV", "TLC", "RV % TLC", "TGV % TLC", "RAW", "GAW", "sRAW", "DLCOc", "DLCOc/VA", "VA"]

VALIDATION_FIELDS = {
    FORMATS.OLD.FULL.value: NUMERIC_VALIDATE_FIELDS,
    FORMATS.OLD.ONLY_SPIROMETRY_WITH_POST.value: NUMERIC_VALIDATE_FIELDS,
    FORMATS.OLD.ONLY_SPIROMETRY_WITHOUT_POST.value: NUMERIC_VALIDATE_FIELDS,
    FORMATS.NEW.FULL_WITH_POST.value: NEW_NUMERIC_VALIDATE_FIELDS,
    FORMATS.NEW.FULL_WITHOUT_POST.value: NEW_NUMERIC_VALIDATE_FIELDS,
    FORMATS.NEW.ONLY_SPIROMETRY_WITH_POST.value: NEW_NUMERIC_VALIDATE_FIELDS,
    FORMATS.NEW.ONLY_SPIROMETRY_WITHOUT_POST.value: NEW_NUMERIC_VALIDATE_FIELDS,
    FORMATS.THIRD.FULL.value: NUMERIC_VALIDATE_FIELDS
}

THIRD_FORMAT_IDENTIFIER =r"[Best ]{3,4}\s+[Gr.]{2,3}\s+[%&7P]"
BASE_THIRD_REGEX_FEILDS = {
    "Last Name": r"Last Name: ([\w\s-]+) Ge",
    "First Name": r"First Name: (\w+)",
    "ID": r"Id: ([\d/]+)",
    "Date of Birth": r"Birth Date: (\d\d [A-Za-z,.]{2,4} \d\d\d\d)",
    "Date": r"[Session Date:]{10,15} (\d\d [A-Za-z,.]{2,4} \d\d\d\d)",
    "Sex": r"[Gender':]{5,8} (F|M)",
    "Smoker": r"[Smo 0kecr:=-]{6,9}(Yes|No)",
    "Ethnicity": r"[Ethnicity: ]{8,11} ([\w\s]+) H",
    "Height": r"[Height\s:]{5,9} ([\d.,Olt-]+) [co]m",
    "Weight": r"[Weight\s:]{5,9} ([\d.,Olt-]+) [kg]",
    "Age": r"Age: ([\d]+)",
    "BMI": r"BMI: ([\d.,Olt-]+)",
    "Spo2": r"[Spo02]{3,6} (\b\d{2,3}\b)",
}


THIRD_SPECIFIC_REGEX_FIELDS = {
    "Format": FORMATS.THIRD.FULL.value,
    "FVC": r"[\nFVCe]{4}\s+[L\s+]{0,2}([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+(\w)\s+([\d.,Olst~-]+)[t%&36s]\s+([\d.,Olst~-]+)\s+(\w)\s+([\d.,Olst~-]+)[t%&36s]\s+.{0,4}?([\d.,Olst~-]+)[t%&36s]\s+",
    "FEV1": r"[\nFVCe1I]{5}\s+[L\s+]{0,2}([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+(\w)\s+([\d.,Olst~-]+)[t%&36s]\s+([\d.,Olst~-]+)\s+(\w)\s+([\d.,Olst~-]+)[t%&36s]\s+.{0,4}?([\d.,Olst~-]+)[t%&36s]\s+",
    "FEV6": r"[\nFEV6c]{5}\s+[L\s+]{0,2}([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[t%&36s]\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[t%&36s]\s+.{0,4}?([\d.,Olst~-]+)[t%&36s]\s+",
    "FEV 1 % FVC": r"[\nFVCe1I/]{8,10}\s+[%&3]{1,2}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[t%&36s]\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[t%&36s]\s+.{0,4}?([\d.,Olst~-]+)[t%&36s]\s+",
    "PEF": r"[\nPEFc]{4}\s+[L/isec]{3,7}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[t%&36s]\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[t%&36s]\s+.{0,4}?([\d.,Olst~-]+)[t%&36s]\s+",
    "PIF": r"[\nPIF]{4}\s+[L/isec]{3,7}\s+[-]+\s+([\d.,Olst~-]+)\s+[-]+\s+([\d.,Olst~-]+)\s+[-]+\s+.{0,4}?([\d.,Olst~-]+)[t%&36s]\s+",
    "MEF 75/25": r"[\nMEFc]{4}\s+[752s%&-]{5}\s+[L/isec]{3,7}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[t%&36s]\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[t%&36s]\s+.{0,4}?([\d.,Olst~-]+)[t%&36s]\s+",
    "MEF50": r"[\nMEFc]{4}\s+[50os]{1,2}\s+[L/isec]{3,7}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[t%&36s]\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[t%&36s]\s+.{0,4}?([\d.,Olst~-]+)[t%&36s]\s+",
    "MEF25": r"[\nMEFc]{4}\s+[25s]{1,2}\s+[L/isec]{3,7}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[t%&36s]\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[t%&36s]\s+.{0,4}?([\d.,Olst~-]+)[t%&36s]\s+",
    "MEF75": r"[\nMEFc]{4}\s+[75s%&]{1,2}\s+[L/isec]{3,7}\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[t%&36s]\s+([\d.,Olst~-]+)\s+([\d.,Olst~-]+)[t%&36s]\s+.{0,4}?([\d.,Olst~-]+)[t%&36s]\s+",
}

FIELDS_WITH_GRADES = ["FEV1", "FVC"]