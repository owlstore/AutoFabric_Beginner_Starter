import SectionCard from "../common/SectionCard";
import Badge from "../common/Badge";
import JsonBlock from "../common/JsonBlock";

function TimelineList({ items }) {
  if (!items?.length) return <div className="text-sm text-slate-500">暂无流程事件</div>;
  return (
    <div className="space-y-3">
      {items.map((event) => (
        <div key={event.id} className="rounded-2xl border border-slate-200 p-4">
          <div className="mb-2 flex flex-wrap gap-2">
            <Badge tone="purple">{event.trigger_type}</Badge>
            <Badge tone="info">{event.to_status}</Badge>
          </div>
          <div className="text-sm text-slate-700">{event.note || "—"}</div>
          <div className="mt-2 text-xs text-slate-500">{event.created_at}</div>
        </div>
      ))}
    </div>
  );
}

function ExecutionList({ items }) {
  if (!items?.length) return <div className="text-sm text-slate-500">暂无执行记录</div>;
  return (
    <div className="space-y-4">
      {items.map((item) => (
        <div key={item.id} className="rounded-2xl border border-slate-200 p-4">
          <div className="mb-3 flex flex-wrap gap-2">
            <Badge tone="success">{item.status}</Badge>
            <Badge tone="info">{item.executor_name}</Badge>
            <Badge tone="default">{item.task_name}</Badge>
          </div>
          <div className="grid gap-4 xl:grid-cols-2">
            <div>
              <div className="mb-2 text-sm font-medium text-slate-700">输入</div>
              <JsonBlock data={item.input_payload} />
            </div>
            <div>
              <div className="mb-2 text-sm font-medium text-slate-700">输出</div>
              <JsonBlock data={item.output_payload} />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function ArtifactList({ items }) {
  if (!items?.length) return <div className="text-sm text-slate-500">暂无产物记录</div>;
  return (
    <div className="space-y-4">
      {items.map((item) => (
        <div key={item.id} className="rounded-2xl border border-slate-200 p-4">
          <div className="mb-3 flex flex-wrap gap-2">
            <Badge tone="success">{item.artifact_type}</Badge>
            <Badge tone="default">{item.artifact_ref}</Badge>
          </div>
          <JsonBlock data={item.metadata} />
        </div>
      ))}
    </div>
  );
}

function VerificationList({ items }) {
  if (!items?.length) return <div className="text-sm text-slate-500">暂无验证记录</div>;
  return (
    <div className="space-y-4">
      {items.map((item) => (
        <div key={item.id} className="rounded-2xl border border-slate-200 p-4">
          <div className="mb-3 flex flex-wrap gap-2">
            <Badge tone="success">{item.status}</Badge>
            <Badge tone="info">{item.verifier_name}</Badge>
          </div>
          <div className="grid gap-4 xl:grid-cols-2">
            <div>
              <div className="mb-2 text-sm font-medium text-slate-700">摘要</div>
              <JsonBlock data={item.summary} />
            </div>
            <div>
              <div className="mb-2 text-sm font-medium text-slate-700">检查项</div>
              <JsonBlock data={item.checks} />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default function RecordContentPanelV2({ activeTab, timelineItems, executionItems, artifactItems, verificationItems }) {
  if (activeTab === "timeline") {
    return (
      <SectionCard title="流程事件" extra={<Badge tone="info">{timelineItems.length}</Badge>}>
        <TimelineList items={timelineItems} />
      </SectionCard>
    );
  }

  if (activeTab === "executions") {
    return (
      <SectionCard title="执行记录" extra={<Badge tone="info">{executionItems.length}</Badge>}>
        <ExecutionList items={executionItems} />
      </SectionCard>
    );
  }

  if (activeTab === "artifacts") {
    return (
      <SectionCard title="产物记录" extra={<Badge tone="success">{artifactItems.length}</Badge>}>
        <ArtifactList items={artifactItems} />
      </SectionCard>
    );
  }

  return (
    <SectionCard title="验证记录" extra={<Badge tone="success">{verificationItems.length}</Badge>}>
      <VerificationList items={verificationItems} />
    </SectionCard>
  );
}
