import { API_BASE_URL } from "./config";
import type {
  ApiErrorBody,
  CreateInvestigationRequest,
  Health,
  ImageTextResponse,
  InvestigationDetail,
  Language,
  Readiness,
  SpeechTarget,
  TranscriptResponse,
} from "./types";

// LLM-backed steps (extraction, questions, explanation, image reading) can take a few seconds each.
const TIMEOUT_MS = 30_000;

export class ApiError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly status: number | null,
    public readonly requestId: string | null = null,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function isErrorBody(body: unknown): body is ApiErrorBody {
  return typeof body === "object" && body !== null && "error" in body;
}

async function send(path: string, init: RequestInit = {}): Promise<Response> {
  let response: Response;
  // FormData bodies set their own multipart Content-Type (with boundary).
  const headers = init.body instanceof FormData ? init.headers : { "Content-Type": "application/json", ...init.headers };
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers,
      signal: init.signal ?? AbortSignal.timeout(TIMEOUT_MS),
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === "TimeoutError") {
      throw new ApiError("TIMEOUT", "The server took too long to respond. Please try again.", null);
    }
    throw new ApiError("NETWORK_ERROR", "Could not reach the Zuno server. Check that the backend is running.", null);
  }
  if (!response.ok) {
    const body: unknown = await response.json().catch(() => null);
    const requestId = response.headers.get("X-Request-ID");
    if (isErrorBody(body)) {
      throw new ApiError(body.error.code, body.error.message, response.status, body.error.request_id ?? requestId);
    }
    throw new ApiError("HTTP_ERROR", `Request failed (${response.status}).`, response.status, requestId);
  }
  return response;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await send(path, init);
  return (await response.json().catch(() => null)) as T;
}

const inv = (id: string) => `/api/v1/investigations/${encodeURIComponent(id)}`;
const post = <T>(path: string, body?: unknown) =>
  request<T>(path, { method: "POST", body: body === undefined ? undefined : JSON.stringify(body) });

// Health endpoints answer with a JSON body even when degraded (503), so read it either way.
async function readiness(): Promise<Readiness> {
  try {
    return await request<Readiness>("/health/ready");
  } catch (err) {
    if (err instanceof ApiError && err.status === 503) {
      return { status: "degraded", checks: { firestore: "unavailable" } };
    }
    throw err;
  }
}

export const api = {
  health: () => request<Health>("/health"),
  readiness,
  createInvestigation: (body: CreateInvestigationRequest) =>
    request<InvestigationDetail>("/api/v1/investigations", { method: "POST", body: JSON.stringify(body) }),
  getInvestigation: (id: string) => request<InvestigationDetail>(inv(id)),
  addEvidence: (id: string, content: string, kind: "text" | "image_text" = "text") =>
    post<InvestigationDetail>(`${inv(id)}/evidence`, { content, kind }),
  assess: (id: string) => post<InvestigationDetail>(`${inv(id)}/assessment`),

  // Adaptive questions (F06)
  nextQuestion: (id: string) => post<InvestigationDetail>(`${inv(id)}/questions/next`),
  answer: (id: string, questionId: string, content: string) =>
    post<InvestigationDetail>(`${inv(id)}/questions/${encodeURIComponent(questionId)}/answer`, { content }),
  skip: (id: string, questionId: string) =>
    post<InvestigationDetail>(`${inv(id)}/questions/${encodeURIComponent(questionId)}/skip`),
  finish: (id: string) => post<InvestigationDetail>(`${inv(id)}/finish`),

  // Voice (F11): audio goes to our backend, which calls Sarvam; nothing is stored.
  transcribe: (audio: Blob, language: Language) => {
    const form = new FormData();
    form.append("audio", audio, "speech.webm");
    form.append("language", language);
    return request<TranscriptResponse>("/api/v1/speech/transcribe", { method: "POST", body: form });
  },
  synthesize: async (investigationId: string, target: SpeechTarget, questionId?: string): Promise<Blob> => {
    const response = await send("/api/v1/speech/synthesize", {
      method: "POST",
      body: JSON.stringify({ investigation_id: investigationId, target, question_id: questionId ?? null }),
    });
    return response.blob();
  },

  // Screenshot evidence (F13): returns text for the user to confirm; the image is not stored.
  readImage: (id: string, image: File) => {
    const form = new FormData();
    form.append("image", image);
    return request<ImageTextResponse>(`${inv(id)}/evidence/image`, { method: "POST", body: form });
  },
};
