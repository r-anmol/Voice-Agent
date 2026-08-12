"use client";

import { useState } from "react";
import MicButton from "./MicButton";

export default function Composer({
  busy,
  onSend,
  onSendSilent,
  lastAssistant,
}: {
  busy: boolean;
  onSend: (t: string) => void;
  onSendSilent: (t: string) => void;
  lastAssistant: string;
}) {
  const [text, setText] = useState("");

  function submit(speak: boolean) {
    const t = text;
    setText("");
    speak ? onSend(t) : onSendSilent(t);
  }

  return (
    <div className="px-4 py-4 border-t border-pink-200/40">
      <div className="flex gap-2 items-end">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type something sweet…"
          className="input-love min-h-[52px] max-h-[140px] resize-none"
          disabled={busy}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit(true);
            }
          }}
        />

        <div className="flex flex-col gap-2">
          <button
            className="btn-love"
            disabled={busy || !text.trim()}
            onClick={() => submit(true)}
            type="button"
          >
            Send 💌
          </button>

          <button
            className="rounded-2xl px-4 py-2 text-sm border border-pink-200/50 bg-white/55 hover:bg-white/75 transition"
            disabled={busy || !text.trim()}
            onClick={() => submit(false)}
            type="button"
            title="Send without speaking"
          >
            Send silently
          </button>
        </div>
      </div>

      <div className="mt-3 flex items-center justify-between gap-2">
        <span className="text-xs opacity-60">
          Kavya remembers you via mem0. Keep it respectful.
        </span>

        <MicButton
          userId="Anmol"
          busy={busy}
          onUserText={(t) => onSendSilent(t)}
          onKavyaText={async () => {
            /* handled by ChatShell in its own flow */
          }}
        />
      </div>
    </div>
  );
}
