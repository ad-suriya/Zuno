// Shared colour tones, level and severity presentation. Literal class strings so Tailwind can see them.
import type { Icon } from "@phosphor-icons/react";
import {
  InfoIcon,
  MagnifyingGlassIcon,
  ShieldCheckIcon,
  WarningIcon,
  WarningOctagonIcon,
} from "@phosphor-icons/react/ssr";

import type { AssessmentLevel, Severity } from "@/lib/types";

export type Tone = "low" | "verify" | "high" | "neutral";

// Literal class strings so Tailwind can see them.
export const TONE: Record<Tone, { panel: string; mark: string; badge: string; text: string }> = {
  low: { panel: "border-low-line bg-low-bg text-low-fg", mark: "", badge: "bg-low-line", text: "text-low-fg" },
  verify: {
    panel: "border-verify-line bg-verify-bg text-verify-fg",
    mark: "bg-verify-bg decoration-verify-line",
    badge: "bg-verify-line",
    text: "text-verify-fg",
  },
  high: {
    panel: "border-high-line bg-high-bg text-high-fg",
    mark: "bg-high-bg decoration-high-line",
    badge: "bg-high-line",
    text: "text-high-fg",
  },
  neutral: {
    panel: "border-border-strong bg-surface-muted text-fg",
    mark: "bg-surface-muted decoration-fg-muted",
    badge: "bg-fg-muted",
    text: "text-fg-muted",
  },
};

export const LEVEL: Record<AssessmentLevel, { label: string; summary: string; tone: Tone; icon: Icon }> = {
  LOW_CONCERN: {
    label: "Low concern",
    summary: "No major warning signals were identified from the information available.",
    tone: "low",
    icon: ShieldCheckIcon,
  },
  NEEDS_VERIFICATION: {
    label: "Needs verification",
    summary: "Important information is missing or could not be independently verified.",
    tone: "verify",
    icon: MagnifyingGlassIcon,
  },
  HIGH_CONCERN: {
    label: "High concern",
    summary: "Significant warning signals are present, based on the information provided.",
    tone: "high",
    icon: WarningOctagonIcon,
  },
};

export const SEVERITY: Record<Severity, { label: string; tone: Tone; icon: Icon }> = {
  CRITICAL: { label: "Critical", tone: "high", icon: WarningOctagonIcon },
  HIGH: { label: "High", tone: "high", icon: WarningIcon },
  MEDIUM: { label: "Medium", tone: "verify", icon: WarningIcon },
  LOW: { label: "Low", tone: "neutral", icon: InfoIcon },
};
