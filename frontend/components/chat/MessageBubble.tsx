import { ChatMessage } from "@/types/chat";

export default function MessageBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={[
          "max-w-[82%] rounded-3xl px-4 py-3 leading-relaxed shadow-sm",
          isUser
            ? "bg-gradient-to-br from-pink-500 to-rose-500 text-white"
            : "bg-white/80 border border-pink-200/40",
        ].join(" ")}
      >
        <div className="text-[15px] whitespace-pre-wrap">{msg.text}</div>
        <div className={`mt-1 text-[11px] ${isUser ? "text-white/70" : "text-black/45"}`}>
          {new Date(msg.ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
        </div>
      </div>
    </div>
  );
}
