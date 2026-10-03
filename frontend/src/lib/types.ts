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
export type EvidenceKind = "story" | "text" | "answer" | "image_text";

export type Unknown =
  | "ENTITY_NAME"
  | "REGISTRATION_NUMBER"
  | "PAYMENT_RECIPIENT"
  | "AMOUNT"
  | "RETURN_CLAIM"
  | "CONTACT_CHANNEL"
  | "DOCUMENTATION"
  | "PRODUCT_SOLD";

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
  code: string;
  params: Record<string, string>;
  claim: string;
  source: string;
  source_tier: 1 | 2 | 3 | 4;
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

export interface Explanation {
  language: Language;
  text: string;
  source: "llm" | "template";
  generated_at: string;
}

export interface Assessment {
  level: AssessmentLevel;
  reasons: AssessmentReason[];
  next_steps: string[];
  explanation: Explanation | null;
  assessed_at: string;
}

export type EntityType =
  | "company"
  | "person"
  | "app"
  | "website"
  | "phone"
  | "upi_id"
  | "registration_number"
  | "other";
export type ClaimCategory = "registration" | "returns" | "identity" | "payment" | "documentation" | "product" | "other";

export interface Entity {
  type: EntityType;
  value: string;
  evidence_id: string;
}

export interface Claim {
  text: string;
  category: ClaimCategory;
  evidence_id: string;
  quote: string | null;
}

export interface Facts {
  offer_type: string | null;
  entities: Entity[];
  claims: Claim[];
  money: string[];
  requests: string[];
  unknowns: Unknown[];
  updated_at: string;
}

export type QuestionStatus = "asked" | "answered" | "skipped";

export interface Question {
  id: string;
  text: string;
  objective: string;
  target_unknown: Unknown | null;
  priority: "high" | "medium" | "low";
  reasoning_source: string;
  source: "llm" | "template";
  status: QuestionStatus;
  answer_evidence_id: string | null;
  asked_at: string;
}

export interface Investigation {
  id: string;
  language: Language;
  channel: Channel;
  assessment: Assessment | null;
  finished: boolean;
  created_at: string;
  updated_at: string;
  expires_at: string;
}

export interface InvestigationDetail {
  investigation: Investigation;
  evidence: Evidence[];
  signals: Signal[];
  verifications: VerificationRecord[];
  facts: Facts | null;
  questions: Question[];
  next_question: Question | null;
}

export interface CreateInvestigationRequest {
  story: string;
  language?: Language;
  channel?: Channel;
}

export interface TranscriptResponse {
  transcript: string;
  redacted: boolean;
}

export interface ImageTextResponse {
  text: string;
  redacted: boolean;
  sensitive: boolean;
}

export type SpeechTarget = "question" | "explanation" | "next_steps";

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
