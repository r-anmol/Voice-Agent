"use client";

import { ChatMessage } from "@/types/chat";
import MessageBubble from "./MessageBubble";
import { useAutoScroll } from "@/hooks/useAutoScroll";

export default function MessageList({
  messages,
  busy,
}: {
  messages: ChatMessage[];
  busy: boolean;
}) {
  const ref = useAutoScroll<HTMLDivElement>([messages.length, busy]);

  return (
    <div
      ref={ref}
      className="h-[520px] overflow-y-auto px-4 py-5 space-y-3"
    >
      {messages.map((m) => (
        <MessageBubble key={m.id} msg={m} />
      ))}
    </div>
  );
}
