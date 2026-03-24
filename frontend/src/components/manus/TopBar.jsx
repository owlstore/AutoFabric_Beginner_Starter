import StageProgressDots from "./StageProgressDots";

export default function TopBar({ project, currentStage, workspace }) {
  return (
    <header className="flex items-center justify-between h-[56px] px-5 border-b border-[#1e1e22] bg-[#131316]/80 backdrop-blur-md">
      <div className="flex items-center gap-3 min-w-0">
        {project ? (
          <div className="flex items-center gap-2 min-w-0">
            <div className="w-2 h-2 rounded-full bg-green-500 shrink-0 anim-pulse" />
            <span className="text-[13px] font-medium text-white truncate">
              {project.name || `Project #${project.id}`}
            </span>
            <span className="text-[11px] text-[#52525b] shrink-0">
              #{project.id}
            </span>
            {workspace?.control_mode && (
              <span className="hidden rounded-full border border-cyan-400/20 bg-cyan-400/10 px-2 py-0.5 text-[11px] text-cyan-100 lg:inline-flex">
                {workspace.control_mode}
              </span>
            )}
          </div>
        ) : (
          <span className="text-[13px] text-[#52525b]">选择或新建项目开始</span>
        )}
      </div>

      {currentStage && <StageProgressDots currentStage={currentStage} />}
    </header>
  );
}
