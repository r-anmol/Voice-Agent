"use client";

import { useRef, useState } from "react";
import { transcribe, chat as chatApi, tts as ttsApi } from "@/lib/api";
import { playBlobAudio } from "@/lib/audio";

export default function MicButton({
  userId,
  busy,
  onUserText,
  onKavyaText,
}: {
  userId: string;
  busy: boolean;
  onUserText: (t: string) => void;
  onKavyaText: (t: string) => void;
}) {
  const [recording, setRecording] = useState(false);
  const [working, setWorking] = useState(false);
  const mrRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);

  const disabled = busy || working;

  async function start() {
    if (disabled) return;
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mr = new MediaRecorder(stream);
    chunksRef.current = [];

    mr.ondataavailable = (e) => {
      if (e.data.size) chunksRef.current.push(e.data);
    };

    mr.onstop = async () => {
      setRecording(false);
      setWorking(true);

      try {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });

        const text = (await transcribe(blob)).trim();
        if (!text) return;

        onUserText(text);

        const reply = await chatApi(userId, text);
        onKavyaText(reply);

        const audio = await ttsApi(reply);
        await playBlobAudio(audio);
      } finally {
        setWorking(false);
        // stop tracks
        stream.getTracks().forEach((t) => t.stop());
      }
    };

    mr.start();
    mrRef.current = mr;
    setRecording(true);
  }

  function stop() {
    mrRef.current?.stop();
  }

  return (
    <button
      type="button"
      className={[
        "rounded-2xl px-4 py-3 font-medium transition active:scale-[0.98]",
        recording
          ? "bg-white/80 border border-pink-300 shadow-[0_18px_35px_rgba(236,72,153,0.14)]"
          : "bg-white/65 border border-pink-200/40 hover:bg-white/80",
        disabled ? "opacity-60 cursor-not-allowed" : "",
      ].join(" ")}
      onClick={recording ? stop : start}
      disabled={disabled}
      title={recording ? "Stop recording" : "Start recording"}
    >
      {recording ? "⏹ Stop" : "🎙️ Mic"}
    </button>
  );
}
