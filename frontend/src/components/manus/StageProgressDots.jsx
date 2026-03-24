import { STAGES, STAGE_LABELS } from "../../constants/stages";

export default function StageProgressDots({ currentStage }) {
  const currentIdx = STAGES.indexOf(currentStage);

  return (
    <div className="flex items-center gap-0.5">
      {STAGES.map((stage, i) => {
        const done = i < currentIdx;
        const active = i === currentIdx;
        const label = STAGE_LABELS[stage] || stage;

        return (
          <div key={stage} className="flex items-center">
            {i > 0 && (
              <div className={`w-6 h-[1.5px] transition-colors duration-500 ${
                done ? "bg-[#3b82f6]" : "bg-[#27272a]"
              }`} />
            )}
            <div className="relative group" title={label}>
              <div
                className={`w-2 h-2 rounded-full transition-all duration-500 stage-dot-${stage} ${
                  done || active ? "" : "!bg-[#27272a] !shadow-none"
                } ${active ? "scale-150" : ""}`}
              />
              {active && (
                <div className={`absolute -inset-1 rounded-full stage-dot-${stage} opacity-20 animate-ping`} />
              )}
              {/* Tooltip */}
              <div className="absolute -bottom-7 left-1/2 -translate-x-1/2 px-2 py-0.5 rounded bg-[#27272a] text-[10px] text-[#a1a1aa] whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                {label}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
