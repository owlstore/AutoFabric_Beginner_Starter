import { useState, useRef } from "react";
import QuarkButton from "../quark/QuarkButton";

export default function ChatInput({ onSend, disabled, placeholder }) {
  const [text, setText] = useState("");
  const taRef = useRef(null);

  const submit = () => {
    const t = text.trim();
    if (!t || disabled) return;
    onSend(t);
    setText("");
    if (taRef.current) taRef.current.style.height = "auto";
  };

  const onKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  const autoGrow = (e) => {
    const el = e.target;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 150) + "px";
  };

  const hasText = text.trim().length > 0;

  return (
    <div className="border-t border-[#1e1e22] bg-[#131316]/80 backdrop-blur-md px-5 py-3">
      <div className="mx-auto max-w-[720px]">
        <div className={`flex items-end gap-2 rounded-2xl border bg-[#1a1a1e] px-4 py-2.5 transition-colors duration-200 ${
          hasText ? "border-[#3b82f6]/40" : "border-[#27272a]"
        } focus-within:border-[#3b82f6]/60`}>
          <textarea
            ref={taRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={onKey}
            onInput={autoGrow}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className="flex-1 resize-none bg-transparent text-[14px] text-white placeholder:text-[#52525b] focus:outline-none disabled:opacity-40 leading-relaxed"
          />
          <QuarkButton
            onClick={submit}
            disabled={disabled || !hasText}
            variant="raw"
            className={`flex-shrink-0 w-8 h-8 rounded-xl flex items-center justify-center transition-all duration-200 ${
              hasText && !disabled
                ? "bg-white text-black hover:bg-gray-200 scale-100"
                : "bg-[#27272a] text-[#52525b] scale-95"
            }`}
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M8 13V3M4 7l4-4 4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </QuarkButton>
        </div>
        <p className="text-[10px] text-[#3a3a3e] text-center mt-2">
          AutoFabric 会自动完成七阶段流水线 · Enter 发送 · Shift+Enter 换行
        </p>
      </div>
    </div>
  );
}
