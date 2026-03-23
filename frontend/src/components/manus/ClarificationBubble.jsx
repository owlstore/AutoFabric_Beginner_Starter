import { useState } from "react";
import { STAGE_LABELS } from "../../constants/stages";
import QuarkButton from "../quark/QuarkButton";

export default function ClarificationBubble({ message }) {
  const data = message.content || {};
  const questions = (data.questions_json || data.questions || []).map((item) =>
    typeof item === "string" ? item : item?.question || JSON.stringify(item),
  );
  const answers = data.answers_json || data.answers || [];
  const resolved = data.status === "resolved" || message.status === "completed";
  const [drafts, setDrafts] = useState(() => questions.map((_, i) => answers[i] || ""));
  const [submitting, setSubmitting] = useState(false);

  const canSubmit = drafts.every((d) => d.trim()) && !submitting;

  const handleReply = async () => {
    if (!message.onReply || !canSubmit) return;
    setSubmitting(true);
    try {
      await message.onReply(data.id, drafts);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex justify-start">
      <div className="max-w-[88%] flex items-start gap-2.5">
        {/* Avatar */}
        <div className="w-7 h-7 rounded-lg bg-[#1e1e28] flex items-center justify-center shrink-0">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <circle cx="7" cy="7" r="5.5" stroke="#fbbf24" strokeWidth="1"/>
            <path d="M7 4v3M7 9v.5" stroke="#fbbf24" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
        </div>

        {/* Card */}
        <div className="rounded-2xl rounded-tl-md border border-[#2a2520] bg-[#16161a] px-4 py-3 shadow-lg shadow-black/10 w-full max-w-[480px]">
          {/* Header */}
          <div className="flex items-center gap-2 mb-3">
            <span className="stage-pill-clarification inline-flex items-center rounded-md px-2 py-0.5 text-[11px] font-medium">
              {STAGE_LABELS.clarification}
            </span>
            <span className={`text-[11px] ${resolved ? "text-green-400" : "text-amber-400"}`}>
              {resolved ? "✓ 已解决" : "● 需要回复"}
            </span>
          </div>

          {/* Q&A */}
          <div className="space-y-3">
            {questions.map((q, i) => (
              <div key={i}>
                <p className="text-[12px] text-[#a1a1aa] mb-1.5 flex items-start gap-1.5">
                  <span className="text-amber-500 font-mono text-[11px] shrink-0 mt-px">Q{i + 1}</span>
                  <span>{q}</span>
                </p>
                {resolved || answers[i] ? (
                  <div className="ml-5 rounded-lg bg-[#1e1e22] px-3 py-1.5 text-[12px] text-[#d4d4d8]">
                    {answers[i] || drafts[i] || "-"}
                  </div>
                ) : (
                  <input
                    type="text"
                    value={drafts[i]}
                    onChange={(e) => {
                      const next = [...drafts];
                      next[i] = e.target.value;
                      setDrafts(next);
                    }}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && i === questions.length - 1 && canSubmit) {
                        handleReply();
                      }
                    }}
                    placeholder="输入回复..."
                    className="ml-5 w-[calc(100%-20px)] text-[12px] bg-[#1a1a1e] border border-[#27272a] rounded-lg px-3 py-1.5 text-[#d4d4d8] placeholder:text-[#3a3a3e] focus:border-amber-500/50 focus:outline-none transition-colors"
                  />
                )}
              </div>
            ))}
          </div>

          {/* Submit */}
          {!resolved && message.onReply && (
            <QuarkButton
              onClick={handleReply}
              disabled={!canSubmit}
              variant="raw"
              className="mt-3 w-full rounded-xl bg-gradient-to-r from-amber-600 to-orange-600 px-4 py-2 text-[12px] font-medium text-white hover:from-amber-500 hover:to-orange-500 disabled:opacity-30 disabled:cursor-not-allowed transition-all duration-200"
            >
              {submitting ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-3 h-3 rounded-full border-2 border-white border-t-transparent animate-spin" />
                  提交中...
                </span>
              ) : (
                "提交回复并继续"
              )}
            </QuarkButton>
          )}
        </div>
      </div>
    </div>
  );
}
