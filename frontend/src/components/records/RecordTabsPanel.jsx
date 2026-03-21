import TabButton from "../common/TabButton";

export default function RecordTabsPanel({ activeTab, handleTabChange }) {
  return (
    <div className="flex flex-wrap gap-2">
      <TabButton active={activeTab === "overview"} onClick={() => handleTabChange("overview")}>概览数据</TabButton>
      <TabButton active={activeTab === "openclaw"} onClick={() => handleTabChange("openclaw")}>OpenClaw</TabButton>
      <TabButton active={activeTab === "goal"} onClick={() => handleTabChange("goal")}>目标模型</TabButton>
      <TabButton active={activeTab === "timeline"} onClick={() => handleTabChange("timeline")}>流程事件</TabButton>
      <TabButton active={activeTab === "executions"} onClick={() => handleTabChange("executions")}>执行记录</TabButton>
      <TabButton active={activeTab === "artifacts"} onClick={() => handleTabChange("artifacts")}>产物记录</TabButton>
      <TabButton active={activeTab === "verifications"} onClick={() => handleTabChange("verifications")}>验证记录</TabButton>
    </div>
  );
}
