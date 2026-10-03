"use client";

// Voice (F11). Audio goes to our backend (which calls Sarvam); the API key never reaches the browser.
// Everything degrades to typing: no mic, no permission, or Sarvam down just shows a short message.

import { useCallback, useEffect, useRef, useState } from "react";

import { useErrorText } from "@/components/ErrorNotice";
import { useI18n } from "@/components/I18nProvider";
import { api } from "@/lib/api";
import type { Language, SpeechTarget } from "@/lib/types";

const MAX_RECORDING_MS = 60_000;

type RecState = "idle" | "recording" | "transcribing";

/** Mic button: records up to 60 s, returns the (server-redacted) transcript for the user to review. */
export function VoiceInput({
  language,
  onTranscript,
  disabled,
}: {
  language: Language;
  onTranscript: (text: string) => void;
  disabled?: boolean;
}) {
  const { t } = useI18n();
  const errorText = useErrorText();
  const [state, setState] = useState<RecState>("idle");
  const [message, setMessage] = useState<string | null>(null);
  const recorder = useRef<MediaRecorder | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(
    () => () => {
      if (timer.current) clearTimeout(timer.current);
      recorder.current?.stream.getTracks().forEach((track) => track.stop());
    },
    [],
  );

  async function start() {
    setMessage(null);
    if (typeof window === "undefined" || !navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
      setMessage(t("voice.unsupported"));
      return;
    }
    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      setMessage(t("voice.denied"));
      return;
    }
    const chunks: Blob[] = [];
    const rec = new MediaRecorder(stream);
    rec.ondataavailable = (e) => e.data.size > 0 && chunks.push(e.data);
    rec.onstop = async () => {
      stream.getTracks().forEach((track) => track.stop());
      if (timer.current) clearTimeout(timer.current);
      const audio = new Blob(chunks, { type: rec.mimeType || "audio/webm" });
      setState("transcribing");
      try {
        const result = await api.transcribe(audio, language);
        onTranscript(result.transcript);
        setMessage(t("voice.confirm"));
      } catch (err) {
        setMessage(errorText(err));
      } finally {
        setState("idle");
      }
    };
    recorder.current = rec;
    rec.start();
    setState("recording");
    timer.current = setTimeout(() => rec.state === "recording" && rec.stop(), MAX_RECORDING_MS);
  }

  function stop() {
    if (recorder.current?.state === "recording") recorder.current.stop();
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      <button
        type="button"
        onClick={state === "recording" ? stop : start}
        disabled={disabled || state === "transcribing"}
        aria-pressed={state === "recording"}
        className={`inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-50 ${
          state === "recording"
            ? "border-red-600 bg-red-600 text-white"
            : "border-stone-300 bg-white text-stone-800 hover:bg-stone-100"
        }`}
      >
        <span aria-hidden>{state === "recording" ? "■" : "🎤"}</span>
        {state === "recording" ? t("voice.stop") : t("voice.speak")}
      </button>
      {state !== "idle" && (
        <span className="text-xs text-stone-600" role="status">
          {state === "recording" ? t("voice.recording") : t("voice.transcribing")}
        </span>
      )}
      {state === "idle" && message && (
        <span className="text-xs text-stone-600" role="status">
          {message}
        </span>
      )}
    </div>
  );
}

/** Plays server-generated text (a question, the explanation or the next steps). */
export function useSpeech(investigationId: string) {
  const errorText = useErrorText();
  const [playing, setPlaying] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const audio = useRef<HTMLAudioElement | null>(null);

  useEffect(
    () => () => {
      audio.current?.pause();
    },
    [],
  );

  const play = useCallback(
    async (target: SpeechTarget, questionId?: string) => {
      const key = `${target}:${questionId ?? ""}`;
      audio.current?.pause();
      setError(null);
      setPlaying(key);
      try {
        const blob = await api.synthesize(investigationId, target, questionId);
        const url = URL.createObjectURL(blob);
        const el = new Audio(url);
        audio.current = el;
        el.onended = () => {
          URL.revokeObjectURL(url);
          setPlaying(null);
        };
        await el.play();
      } catch (err) {
        setError(errorText(err));
        setPlaying(null);
      }
    },
    [investigationId, errorText],
  );

  return { play, playing, error };
}

export function SpeakButton({
  label,
  busy,
  onClick,
}: {
  label: string;
  busy: boolean;
  onClick: () => void;
}) {
  const { t } = useI18n();
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={busy}
      className="inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-xs text-stone-600 underline-offset-2 hover:bg-stone-100 hover:text-stone-900 disabled:opacity-60"
      aria-label={label}
    >
      <span aria-hidden>🔊</span>
      {busy ? t("voice.playing") : label}
    </button>
  );
}
