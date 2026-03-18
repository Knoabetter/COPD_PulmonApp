export type Sex = 'male' | 'female' | 'other' | 'unknown' | string;

export interface PatientInfo {
  id?: string | number;
  age: number;
  sex: Sex;
  height: number;
}

export interface MeasuredValues {
  FEV1?: number;
  FVC?: number;
  ratio?: number;
}

export interface PredictionDetail {
  pred?: number;
  lln?: number;
  measured?: number;
  percent?: number;
}

export interface PredictionValues {
  FEV1?: PredictionDetail;
  FVC?: PredictionDetail;
  ratio?: PredictionDetail;
}

export interface AgreementSummary {
  diagnosis?: string;
  ratioDiff?: number;
  percentDiff?: number;
  clinicalImpact?: string;
}

export interface ValidationResults {
  status?: 'OK' | 'WARN' | 'ERROR' | string;
  errors?: string[];
  warnings?: string[];
}

export interface ClinicalInterpretation {
  [key: string]: unknown;
}

export interface AnalysisResults {
  patient: PatientInfo;
  measured: MeasuredValues;
  murray: PredictionValues;
  gli: PredictionValues;
  agreement?: AgreementSummary;
  validation?: ValidationResults;
  clinical_interpretation?: ClinicalInterpretation;
  rawData?: unknown;
}

export interface DiagnosisSuggestion {
  has_obstruction?: boolean;
  severity?: string;
  criteria?: string;
  message?: string;
  [key: string]: unknown;
}

export type DiagnosisSuggestionsPayload = DiagnosisSuggestion;

export interface BatchResult {
  filename: string;
  pdf_filename?: string;
  success?: boolean;
  error?: string;

  patient_info?: {
    id?: string | number;
    age?: number;
    sex?: Sex;
    height?: number;
  };

  measured_values?: {
    FEV1_PRE?: number;
    FVC_PRE?: number;
    'FEV 1 % FVC_PRE'?: number;
    [key: string]: unknown;
  };

  murray_predictions?: {
    FEV1_Murray_pred?: number;
    FEV1_Murray_LLN?: number;
    FVC_Murray_pred?: number;
    FVC_Murray_LLN?: number;
    FEV1_FVC_Murray_pred?: number;
    FEV1_FVC_Murray_LLN?: number;
    [key: string]: unknown;
  };

  gli_predictions?: {
    FEV1_GLI_pred?: number;
    FEV1_GLI_LLN?: number;
    FVC_GLI_pred?: number;
    FVC_GLI_LLN?: number;
    FEV1_FVC_GLI_pred?: number;
    FEV1_FVC_GLI_LLN?: number;
    [key: string]: unknown;
  };

  clinical_interpretation?: ClinicalInterpretation;
  [key: string]: unknown;
}

export interface BatchAnalysisResponse {
  success: boolean;
  results: BatchResult[];
  total_files?: number;
  successful_analyses?: number;
  summary?: {
    copd_cases?: number;
    normal_cases?: number;
    borderline_cases?: number;
    [key: string]: unknown;
  };
  error?: string;
}

export interface SearchResultRow {
  id: string | number;
  date_pre?: string;
  fev1_pre?: number | null;
  fvc_pre?: number | null;
  fev1_fvc_pre?: number | null;
  diagnosis?: string | null;
  [key: string]: unknown;
}
