export default function TypingIndicator({ text }: { text: string }) {
    return (
      <div className="px-6 pb-3 -mt-2">
        <div className="inline-flex items-center gap-2 rounded-full px-4 py-2 bg-white/65 border border-pink-200/40">
          <span className="text-sm opacity-70">{text}</span>
          <span className="inline-flex gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-pink-400 animate-bounce [animation-delay:-0.2s]" />
            <span className="w-1.5 h-1.5 rounded-full bg-rose-400 animate-bounce [animation-delay:-0.1s]" />
            <span className="w-1.5 h-1.5 rounded-full bg-purple-300 animate-bounce" />
          </span>
        </div>
      </div>
    );
  }
  