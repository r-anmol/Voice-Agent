"use client";

import { useMemo, useRef, useState } from "react";
import ChatHeader from "./ChatHeader";
import MessageList from "./MessageList";
import Composer from "./Composer";
import TypingIndicator from "./TypingIndicator";
import { ChatMessage } from "@/types/chat";
import { chat as chatApi, tts as ttsApi } from "@/lib/api";

function uid() {
  return Math.random().toString(36).slice(2) + Date.now().toString(36);
}

export default function ChatShell() {
  const userId = "Anmol";

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: uid(),
      role: "kavya",
      text: "Hi 😌 Ready when you are. Text me or hit the mic.",
      ts: Date.now(),
    },
  ]);
  const [busy, setBusy] = useState(false);

  // Keep a single Audio instance so we can stop it (important for silent sends)
  const audioRef = useRef<HTMLAudioElement | null>(null);

  function stopAudio() {
    const a = audioRef.current;
    if (!a) return;
    try {
      a.pause();
      a.currentTime = 0;
    } catch {}
    audioRef.current = null;
  }

  async function playBlobAudio(blob: Blob) {
    stopAudio();
    const url = URL.createObjectURL(blob);
    const a = new Audio(url);
    audioRef.current = a;

    a.onended = () => {
      URL.revokeObjectURL(url);
      audioRef.current = null;
    };
    a.onerror = () => {
      URL.revokeObjectURL(url);
      audioRef.current = null;
    };

    await a.play();
  }

  const lastKavya = useMemo(() => {
    const m = [...messages].reverse().find((x) => x.role === "kavya");
    return m?.text ?? "";
  }, [messages]);

  async function sendText(text: string, speak: boolean) {
    const cleaned = text.trim();
    if (!cleaned || busy) return;

    // 🔇 If user chose silent, stop any previously-playing audio immediately
    if (!speak) stopAudio();

    setMessages((m) => [
      ...m,
      { id: uid(), role: "user", text: cleaned, ts: Date.now() },
    ]);

    setBusy(true);
    try {
      const reply = await chatApi(userId, cleaned);

      setMessages((m) => [
        ...m,
        { id: uid(), role: "kavya", text: reply, ts: Date.now() },
      ]);

      // ✅ ONLY speak if speak=true
      if (speak && reply.trim()) {
        const audio = await ttsApi(reply);
        await playBlobAudio(audio);
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="love-noise">
      <div className="mx-auto max-w-4xl px-4 py-10">
        <div className="glass rounded-[28px] shadow-[0_30px_80px_rgba(236,72,153,0.12)] overflow-hidden">
          <ChatHeader subtitle="Love-themed voice + text chat" />

          <MessageList messages={messages} busy={busy} />

          {busy && <TypingIndicator text="Kavya is thinking…" />}

          <Composer
            busy={busy}
            onSend={(text) => sendText(text, true)}        // speak
            onSendSilent={(text) => sendText(text, false)} // silent = no tts
            lastAssistant={lastKavya}
          />
        </div>

        <div className="mt-4 text-center text-sm opacity-70">
          Tip: Enter = send + speak • Shift+Enter = newline • Send silently = no voice
        </div>
      </div>
    </main>
  );
}
