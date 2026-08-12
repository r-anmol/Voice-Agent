export default function ChatHeader({
    subtitle,
  }: {
    subtitle?: string;
  }) {
    return (
      <div className="px-6 py-5 border-b border-pink-200/40">
        <div className="flex items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-2xl">💗</span>
              <h1 className="text-xl font-semibold tracking-tight">Kavya</h1>
              <span className="badge-love">online</span>
            </div>
            <p className="mt-1 text-sm opacity-70">{subtitle}</p>
          </div>
  
          <div className="hidden sm:flex items-center gap-2 opacity-70">
            <span className="text-sm">soft mode</span>
            <span>🌸</span>
          </div>
        </div>
      </div>
    );
  }
  