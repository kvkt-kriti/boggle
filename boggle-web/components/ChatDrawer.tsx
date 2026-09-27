"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { CHAT_SUGGESTIONS, mockChatReply } from "@/lib/mock-chat";
import type { Recommendation } from "@/lib/api";

type Message = { role: "user" | "assistant"; text: string };

type Props = {
  open: boolean;
  onClose: () => void;
  majorName: string;
  schoolName: string;
  recommendations: Recommendation[];
  totalCredits: number;
};

export function ChatDrawer({
  open,
  onClose,
  majorName,
  schoolName,
  recommendations,
  totalCredits,
}: Props) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open) endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, open]);

  function ask(question: string) {
    const trimmed = question.trim();
    if (!trimmed) return;
    const reply = mockChatReply(trimmed, {
      majorName,
      schoolName,
      recommendations,
      totalCredits,
    });
    setMessages((prev) => [
      ...prev,
      { role: "user", text: trimmed },
      { role: "assistant", text: reply },
    ]);
    setInput("");
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    ask(input);
  }

  return (
    <>
      <div
        className={`no-print fixed inset-0 z-40 bg-forest/20 transition ${
          open ? "opacity-100" : "pointer-events-none opacity-0"
        }`}
        onClick={onClose}
        aria-hidden={!open}
      />
      <aside
        className={`no-print fixed inset-y-0 right-0 z-50 flex w-full max-w-md flex-col border-l border-forest/10 bg-cream-soft shadow-xl transition-transform duration-300 ${
          open ? "translate-x-0" : "translate-x-full"
        }`}
        aria-hidden={!open}
        aria-label="Ask Boggle"
      >
        <header className="flex items-start justify-between gap-3 bg-forest px-5 py-4 text-cream-soft">
          <div>
            <div className="flex items-center gap-2">
              <span className="flex h-7 w-7 items-center justify-center rounded-full border border-cream-soft/40 font-display text-sm">
                B
              </span>
              <h2 className="font-display text-xl">Ask Boggle</h2>
            </div>
            <p className="mt-2 label-caps text-cream-soft/70">
              {majorName} · {schoolName}
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-full px-2 py-1 text-lg text-cream-soft/80 hover:bg-white/10"
            aria-label="Close chat"
          >
            ×
          </button>
        </header>

        <div className="flex-1 space-y-4 overflow-y-auto px-5 py-5">
          <p className="text-[14px] leading-relaxed text-ink-muted">
            I work only from {schoolName}&apos;s published AP credit chart for{" "}
            {majorName}. Ask me anything about your ranked plan.
          </p>

          {messages.length === 0 ? (
            <div className="space-y-2">
              {CHAT_SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => ask(s)}
                  className="block w-full rounded-xl border border-forest/15 bg-white px-4 py-3 text-left text-[14px] text-ink hover:border-forest/30"
                >
                  {s}
                </button>
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              {messages.map((m, i) => (
                <div
                  key={`${m.role}-${i}`}
                  className={`max-w-[92%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-[14px] leading-relaxed ${
                    m.role === "user"
                      ? "ml-auto bg-forest text-cream-soft"
                      : "bg-white text-ink border border-forest/10"
                  }`}
                >
                  {m.text}
                </div>
              ))}
              <div ref={endRef} />
            </div>
          )}
        </div>

        <form onSubmit={onSubmit} className="border-t border-forest/10 px-4 py-4">
          <div className="flex items-center gap-2 rounded-full border border-forest/15 bg-white px-3 py-1.5">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about your plan…"
              className="min-w-0 flex-1 bg-transparent px-2 py-2 text-[14px] outline-none placeholder:text-ink-faint"
            />
            <button
              type="submit"
              className="flex h-9 w-9 items-center justify-center rounded-full bg-forest text-cream-soft"
              aria-label="Send"
            >
              ↑
            </button>
          </div>
          <p className="mt-3 text-center text-[11px] leading-snug text-ink-faint">
            Grounded in official charts — recommendations, not guarantees. Verify
            before you register.
          </p>
        </form>
      </aside>
    </>
  );
}
