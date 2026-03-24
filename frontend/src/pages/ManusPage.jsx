import Sidebar from "../components/manus/Sidebar";
import TopBar from "../components/manus/TopBar";
import ChatFlow from "../components/manus/ChatFlow";
import ChatInput from "../components/manus/ChatInput";
import WorkspacePanel from "../components/manus/WorkspacePanel";
import useProjectFlow from "../hooks/useProjectFlow";

export default function ManusPage() {
  const flow = useProjectFlow();

  return (
    <div className="flex h-screen bg-[#091017]">
      {/* Sidebar */}
      <Sidebar
        projects={flow.projects}
        activeId={flow.activeProjectId}
        onSelect={flow.selectProject}
        onCreate={flow.createNewProject}
      />

      {/* Main area */}
      <div className="flex min-w-0 flex-1">
        <div className="flex min-w-0 flex-1 flex-col">
          <TopBar
            project={flow.activeProject}
            currentStage={flow.activeProject?.current_stage_key}
            workspace={flow.workspaceSnapshot?.workspace}
          />

          <ChatFlow
            messages={flow.messages}
            loading={flow.loading}
            stageName={flow.currentAction}
          />

          <ChatInput
            onSend={flow.handleSend}
            disabled={flow.loading}
            placeholder={
              flow.activeProjectId
                ? "补充约束、技术偏好或交付要求，Autopilot 会继续推进..."
                : "描述你的项目目标，系统会自动创建并推进整个任务链路..."
            }
          />
        </div>

        <WorkspacePanel snapshot={flow.workspaceSnapshot} loading={flow.loading} />
      </div>
    </div>
  );
}
