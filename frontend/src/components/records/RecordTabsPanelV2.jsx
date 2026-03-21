import TabButton from "../common/TabButton";

export default function RecordTabsPanelV2({ activeTab, setActiveTab }) {
  return (
    <div className="flex flex-wrap gap-2">
      <TabButton active={activeTab === "timeline"} onClick={() => setActiveTab("timeline")}>流程事件</TabButton>
      <TabButton active={activeTab === "executions"} onClick={() => setActiveTab("executions")}>执行记录</TabButton>
      <TabButton active={activeTab === "artifacts"} onClick={() => setActiveTab("artifacts")}>产物记录</TabButton>
      <TabButton active={activeTab === "verifications"} onClick={() => setActiveTab("verifications")}>验证记录</TabButton>
    </div>
  );
}
