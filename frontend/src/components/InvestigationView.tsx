"use client";

import { useEffect, useRef, useState } from "react";

import { AssessmentResult } from "@/components/AssessmentResult";
import { useErrorText } from "@/components/ErrorNotice";
import { EvidenceTrail } from "@/components/EvidenceTrail";
import { useI18n } from "@/components/I18nProvider";
import { SpeakButton, useSpeech, VoiceInput } from "@/components/Voice";
import { api } from "@/lib/api";
import type { InvestigationDetail, Question } from "@/lib/types";

const AUTOPLAY_KEY = "zuno.autoplay";

export interface Actions {
  answer: (question: Question, content: string) => Promise<void>;
  skip: (question: Question) => Promise<void>;
  finish: () => Promise<void>;
  addEvidence: (content: string, kind: "text" | "image_text") => Promise<void>;
}

function Bubble({ who, children }: { who: "zuno" | "you"; children: React.ReactNode }) {
  const { t } = useI18n();
  const zuno = who === "zuno";
  return (
    <div className={`flex ${zuno ? "justify-start" : "justify-end"}`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm ${
          zuno ? "rounded-tl-sm bg-white text-stone-900 ring-1 ring-stone-200" : "rounded-tr-sm bg-stone-900 text-white"
        }`}
      >
        <p className={`text-[11px] font-semibold uppercase tracking-wide ${zuno ? "text-stone-500" : "text-stone-300"}`}>
          {zuno ? t("inv.zuno") : t("inv.you")}
        </p>
        <div className="mt-0.5 whitespace-pre-wrap break-words">{children}</div>
      </div>
    </div>
  );
}

function AnswerBox({ question, busy, actions, language }: {
  question: Question;
  busy: boolean;
  actions: Actions;
  language: InvestigationDetail["investigation"]["language"];
}) {
  const { t } = useI18n();
  const [answer, setAnswer] = useState("");
  return (
    <form
      onSubmit={async (e) => {
        e.preventDefault();
        await actions.answer(question, answer);
        setAnswer("");
      }}
      className="space-y-2"
    >
      <textarea
        value={answer}
        onChange={(e) => setAnswer(e.target.value)}
        rows={2}
        maxLength={2_000}
        placeholder={t("inv.answer_placeholder")}
        aria-label={question.text}
        className="w-full rounded-md border border-stone-300 bg-white p-2.5 text-base text-stone-900 focus:border-stone-900 focus:outline-none"
      />
      <VoiceInput language={language} disabled={busy} onTranscript={(text) => setAnswer((a) => (a ? `${a} ${text}` : text))} />
      <div className="flex flex-wrap gap-2">
        <button
          type="submit"
          disabled={busy || !answer.trim()}
          className="rounded-md bg-stone-900 px-4 py-2 text-sm font-medium text-white hover:bg-stone-700 disabled:cursor-not-allowed disabled:bg-stone-400"
        >
          {t("inv.send")}
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={() => actions.answer(question, t("inv.dont_know"))}
          className="rounded-md border border-stone-300 bg-white px-3 py-2 text-sm text-stone-800 hover:bg-stone-100 disabled:opacity-50"
        >
          {t("inv.dont_know")}
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={() => actions.skip(question)}
          className="rounded-md border border-stone-300 bg-white px-3 py-2 text-sm text-stone-800 hover:bg-stone-100 disabled:opacity-50"
        >
          {t("inv.skip")}
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={actions.finish}
          className="ml-auto rounded-md px-3 py-2 text-sm text-stone-700 underline underline-offset-2 hover:text-stone-900 disabled:opacity-50"
        >
          {t("inv.finish")}
        </button>
      </div>
    </form>
  );
}

function AddEvidenceForm({ busy, actions, investigationId }: { busy: boolean; actions: Actions; investigationId: string }) {
  const { t, language } = useI18n();
  const errorText = useErrorText();
  const [content, setContent] = useState("");
  const [image, setImage] = useState<{ text: string; sensitive: boolean } | null>(null);
  const [reading, setReading] = useState(false);
  const [imageError, setImageError] = useState<string | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);

  async function onFile(file: File | undefined) {
    if (!file) return;
    setImageError(null);
    setReading(true);
    try {
      const result = await api.readImage(investigationId, file);
      setImage({ text: result.text, sensitive: result.sensitive });
    } catch (err) {
      setImageError(errorText(err));
    } finally {
      setReading(false);
      if (fileInput.current) fileInput.current.value = "";
    }
  }

  return (
    <div className="space-y-3 rounded-lg border border-stone-200 bg-stone-50 p-4">
      {image ? (
        <form
          onSubmit={async (e) => {
            e.preventDefault();
            await actions.addEvidence(image.text, "image_text");
            setImage(null);
          }}
          className="space-y-2"
        >
          <p className="text-sm font-medium text-stone-900">{t("image.confirm")}</p>
          {image.sensitive && (
            <p className="rounded-md bg-amber-100 p-2 text-sm text-amber-900">{t("image.sensitive")}</p>
          )}
          <textarea
            value={image.text}
            onChange={(e) => setImage({ ...image, text: e.target.value })}
            rows={5}
            maxLength={10_000}
            className="w-full rounded-md border border-stone-300 bg-white p-2.5 text-base text-stone-900"
          />
          <div className="flex gap-2">
            <button
              type="submit"
              disabled={busy || !image.text.trim()}
              className="rounded-md bg-stone-900 px-4 py-2 text-sm font-medium text-white hover:bg-stone-700 disabled:bg-stone-400"
            >
              {t("image.add")}
            </button>
            <button
              type="button"
              onClick={() => setImage(null)}
              className="rounded-md border border-stone-300 bg-white px-3 py-2 text-sm text-stone-800 hover:bg-stone-100"
            >
              {t("image.cancel")}
            </button>
          </div>
        </form>
      ) : (
        <form
          onSubmit={async (e) => {
            e.preventDefault();
            await actions.addEvidence(content, "text");
            setContent("");
          }}
          className="space-y-2"
        >
          <label className="block">
            <span className="text-sm font-medium text-stone-900">{t("inv.add_more")}</span>
            <span className="block text-xs text-stone-600">{t("inv.add_more_help")}</span>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={3}
              maxLength={10_000}
              className="mt-1.5 w-full rounded-md border border-stone-300 bg-white p-2.5 text-base text-stone-900 focus:border-stone-900 focus:outline-none"
            />
          </label>
          <p className="text-xs text-stone-600">{t("safety.no_secrets")}</p>
          <VoiceInput language={language} disabled={busy} onTranscript={(text) => setContent((c) => (c ? `${c} ${text}` : text))} />
          <div className="flex flex-wrap items-center gap-2">
            <button
              type="submit"
              disabled={busy || !content.trim()}
              className="rounded-md bg-stone-900 px-4 py-2 text-sm font-medium text-white hover:bg-stone-700 disabled:cursor-not-allowed disabled:bg-stone-400"
            >
              {busy ? t("inv.adding") : t("inv.add")}
            </button>
            <label className="cursor-pointer rounded-md border border-stone-300 bg-white px-3 py-2 text-sm text-stone-800 hover:bg-stone-100">
              {reading ? t("image.reading") : t("image.upload")}
              <input
                ref={fileInput}
                type="file"
                accept="image/png,image/jpeg"
                className="sr-only"
                disabled={busy || reading}
                onChange={(e) => onFile(e.target.files?.[0])}
              />
            </label>
            <span className="text-xs text-stone-500">{t("image.not_stored")}</span>
          </div>
          {imageError && <p className="text-xs text-red-800">{imageError}</p>}
        </form>
      )}
    </div>
  );
}

export function InvestigationView({
  detail,
  busy,
  actions,
}: {
  detail: InvestigationDetail;
  busy: boolean;
  actions: Actions;
}) {
  const { t } = useI18n();
  const inv = detail.investigation;
  const speech = useSpeech(inv.id);
  const [autoplay, setAutoplay] = useState(false);
  const spokenFor = useRef<string | null>(null);
  const pending = detail.next_question;
  const story = detail.evidence.find((e) => e.kind === "story");
  const evidenceById = new Map(detail.evidence.map((e) => [e.id, e]));
  const critical = detail.signals.some((s) => s.kind === "WARNING" && s.severity === "CRITICAL");

  useEffect(() => {
    try {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setAutoplay(window.localStorage.getItem(AUTOPLAY_KEY) === "1");
    } catch {
      // ignore
    }
  }, []);

  useEffect(() => {
    if (autoplay && pending && spokenFor.current !== pending.id) {
      spokenFor.current = pending.id;
      speech.play("question", pending.id);
    }
  }, [autoplay, pending, speech]);

  function toggleAutoplay(on: boolean) {
    setAutoplay(on);
    try {
      window.localStorage.setItem(AUTOPLAY_KEY, on ? "1" : "0");
    } catch {
      // ignore
    }
  }

  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
      <div className="space-y-4">
        <div className="flex items-center justify-between gap-2">
          <h2 className="text-sm font-semibold text-stone-900">{t("inv.conversation")}</h2>
          <label className="flex items-center gap-1.5 text-xs text-stone-600">
            <input type="checkbox" checked={autoplay} onChange={(e) => toggleAutoplay(e.target.checked)} />
            {t("inv.autoplay")}
          </label>
        </div>

        <div className="space-y-3">
          {story && <Bubble who="you">{story.content}</Bubble>}
          {detail.questions.map((q) => {
            const answer = q.answer_evidence_id ? evidenceById.get(q.answer_evidence_id) : undefined;
            return (
              <div key={q.id} className="space-y-3">
                <Bubble who="zuno">
                  {q.text}
                  <div className="mt-1">
                    <SpeakButton
                      label={t("voice.listen")}
                      busy={speech.playing === `question:${q.id}`}
                      onClick={() => speech.play("question", q.id)}
                    />
                  </div>
                </Bubble>
                {answer && <Bubble who="you">{answer.content}</Bubble>}
                {q.status === "skipped" && <Bubble who="you">{t("inv.skipped")}</Bubble>}
              </div>
            );
          })}
          {busy && <p className="text-sm text-stone-500" role="status">{t("inv.thinking")}</p>}
          {!busy && !pending && inv.assessment && (
            <p className="rounded-md bg-stone-100 p-3 text-sm text-stone-700">
              {inv.finished ? t("inv.finished") : critical ? t("inv.done_critical") : t("inv.done")}
            </p>
          )}
        </div>

        {pending && <AnswerBox question={pending} busy={busy} actions={actions} language={inv.language} />}
        {speech.error && <p className="text-xs text-stone-600">{speech.error}</p>}

        <AddEvidenceForm busy={busy} actions={actions} investigationId={inv.id} />
        <EvidenceTrail detail={detail} />
      </div>

      <div className="lg:sticky lg:top-6 lg:self-start">
        <AssessmentResult detail={detail} speech={speech} />
      </div>
    </div>
  );
}
