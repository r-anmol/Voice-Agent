const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

export async function chat(userId: string, message: string): Promise<string> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, message }),
  });
  if (!res.ok) throw new Error(`Chat failed (${res.status})`);
  const data = await res.json();
  return data.reply ?? "";
}

export async function transcribe(audioBlob: Blob): Promise<string> {
  const fd = new FormData();
  fd.append("file", audioBlob, "audio.webm");

  const res = await fetch(`${API_BASE}/transcribe`, {
    method: "POST",
    body: fd,
  });
  if (!res.ok) throw new Error(`Transcribe failed (${res.status})`);
  const data = await res.json();
  return data.text ?? "";
}

export async function tts(text: string): Promise<Blob> {
  const res = await fetch(`${API_BASE}/tts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error(`TTS failed (${res.status})`);
  return await res.blob();
}
