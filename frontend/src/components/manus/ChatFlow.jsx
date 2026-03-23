import { useEffect, useRef } from "react";
import UserBubble from "./UserBubble";
import StageBubble from "./StageBubble";
import ClarificationBubble from "./ClarificationBubble";

function renderMessage(msg, idx) {
  const delay = Math.min(idx * 60, 400);
  const style = { animationDelay: `${delay}ms` };

  if (msg.role === "user") {
    return (
      <div key={msg.id} className="anim-bubble-right" style={style}>
        <UserBubble message={msg} />
      </div>
    );
  }
  if (msg.type === "stage_clarification") {
    return (
      <div key={msg.id} className="anim-bubble-left" style={style}>
        <ClarificationBubble message={msg} />
      </div>
    );
  }
  return (
    <div key={msg.id} className="anim-bubble-left" style={style}>
      <StageBubble message={msg} />
    </div>
  );
}

export default function ChatFlow({ messages, loading, stageName }) {
  const bottomRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    // Smooth scroll to bottom
    const el = containerRef.current;
    if (el) {
      el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
    }
  }, [messages, loading]);

  return (
    <main ref={containerRef} className="flex-1 overflow-y-auto">
      <div className="mx-auto max-w-[720px] px-5 py-8 space-y-3">
        {/* Empty state */}
        {messages.length === 0 && !loading && (
          <div className="flex flex-col items-center justify-center py-32 anim-bubble-in">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-600/20 to-purple-600/20 border border-[#1e1e28] flex items-center justify-center mb-5">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="#60a5fa" strokeWidth="1.5" strokeLinejoin="round" strokeLinecap="round"/>
              </svg>
            </div>
            <p className="text-[15px] text-[#a1a1aa] font-medium mb-1.5">AutoFabric</p>
            <p className="text-[13px] text-[#52525b] text-center max-w-xs leading-relaxed">
              描述你的项目需求，AI 将自动完成需求分析、原型设计、编排执行到交付的全流程
            </p>
          </div>
        )}

        {/* Messages */}
        {messages.map((msg, i) => renderMessage(msg, i))}

        {/* Loading indicator */}
        {loading && (
          <div className="anim-bubble-in flex items-start gap-3 pl-1 py-2">
            <div className="w-7 h-7 rounded-lg bg-[#1e1e28] flex items-center justify-center shrink-0">
              <div className="w-3 h-3 rounded-full border-2 border-blue-500 border-t-transparent animate-spin" />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[12px] text-[#71717a]">
                  {stageName || "正在处理"}
                </span>
                <div className="dot-pulse flex gap-1">
                  <span /><span /><span />
                </div>
              </div>
              <div className="h-2 w-32 rounded-full bg-[#1e1e22] overflow-hidden">
                <div className="h-full rounded-full bg-gradient-to-r from-blue-600 to-purple-600 anim-shimmer" style={{ width: "60%" }} />
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </main>
  );
}
