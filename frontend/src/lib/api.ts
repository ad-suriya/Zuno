import { API_BASE_URL } from "./config";
import type {
  ApiErrorBody,
  CreateInvestigationRequest,
  Health,
  InvestigationDetail,
  Readiness,
} from "./types";

const TIMEOUT_MS = 15_000;

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

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init.headers },
      signal: init.signal ?? AbortSignal.timeout(TIMEOUT_MS),
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === "TimeoutError") {
      throw new ApiError("TIMEOUT", "The server took too long to respond. Please try again.", null);
    }
    throw new ApiError("NETWORK_ERROR", "Could not reach the Zuno server. Check that the backend is running.", null);
  }

  const body: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const requestId = response.headers.get("X-Request-ID");
    if (isErrorBody(body)) {
      throw new ApiError(body.error.code, body.error.message, response.status, body.error.request_id ?? requestId);
    }
    throw new ApiError("HTTP_ERROR", `Request failed (${response.status}).`, response.status, requestId);
  }
  return body as T;
}

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
  getInvestigation: (id: string) => request<InvestigationDetail>(`/api/v1/investigations/${encodeURIComponent(id)}`),
  addEvidence: (id: string, content: string) =>
    request<InvestigationDetail>(`/api/v1/investigations/${encodeURIComponent(id)}/evidence`, {
      method: "POST",
      body: JSON.stringify({ content }),
    }),
  assess: (id: string) =>
    request<InvestigationDetail>(`/api/v1/investigations/${encodeURIComponent(id)}/assessment`, { method: "POST" }),
};
