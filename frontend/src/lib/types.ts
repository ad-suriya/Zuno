// Mirrors backend/app/models.py. Keep in sync with the backend contract.

export type Language = "en" | "ta";

export type Channel =
  | "whatsapp"
  | "telegram"
  | "call"
  | "social"
  | "email"
  | "in_person"
  | "referral"
  | "other"
  | "unknown";

export type AssessmentLevel = "LOW_CONCERN" | "NEEDS_VERIFICATION" | "HIGH_CONCERN";
export type SignalKind = "WARNING" | "REASSURING";
export type Severity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
export type SignalSource = "RULE" | "VERIFIED_SOURCE";
export type VerificationStatus = "VERIFIED" | "NOT_VERIFIED" | "CONTRADICTED" | "UNKNOWN" | "NOT_APPLICABLE";
export type SourceTier = 1 | 2 | 3 | 4;
export type EvidenceKind = "story" | "text";

export interface Evidence {
  id: string;
  kind: EvidenceKind;
  content: string;
  redacted: boolean;
  created_at: string;
}

export interface Signal {
  id: string;
  kind: SignalKind;
  code: string;
  severity: Severity;
  source: SignalSource;
  evidence_id: string | null;
  verification_id: string | null;
  matched_text: string | null;
  explanation: string;
  created_at: string;
}

export interface VerificationRecord {
  id: string;
  claim: string;
  source: string;
  source_tier: SourceTier;
  status: VerificationStatus;
  evidence: string;
  explanation: string;
  material: boolean;
  checked_at: string;
}

export interface AssessmentReason {
  rule: string;
  explanation: string;
  signal_ids: string[];
  verification_ids: string[];
}

export interface Assessment {
  level: AssessmentLevel;
  reasons: AssessmentReason[];
  next_steps: string[]; // step codes, rendered via STEP_TEXT in lib/content.ts
  assessed_at: string;
}

export interface Investigation {
  id: string;
  language: Language;
  channel: Channel;
  assessment: Assessment | null;
  created_at: string;
  updated_at: string;
}

export interface InvestigationDetail {
  investigation: Investigation;
  evidence: Evidence[];
  signals: Signal[];
  verifications: VerificationRecord[];
}

export interface CreateInvestigationRequest {
  story: string;
  language?: Language;
  channel?: Channel;
}

export interface Health {
  status: "ok";
  service: string;
  version: string;
  environment: string;
}

export interface Readiness {
  status: "ok" | "degraded";
  checks: { firestore: "ok" | "unavailable" };
}

// Error body returned by every failing backend endpoint (backend/app/errors.py).
export interface ApiErrorBody {
  error: { code: string; message: string; request_id: string | null };
}
