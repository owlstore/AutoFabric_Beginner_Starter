import SectionCard from "../common/SectionCard";
import Badge from "../common/Badge";

export default function DeliverySummaryCard({
  artifacts,
  latestOutcome,
  onExportJson,
  onExportMarkdown,
  onCopySummary,
}) {
  const count = artifacts?.length || 0;
  const latestArtifact = artifacts?.[0] || null;
  const artifactType = latestArtifact?.artifact_type || latestOutcome?.current_result?.artifact?.type || "暂无产物";
  const deliveryReady = count > 0 || Boolean(latestOutcome?.current_result?.artifact);

  const hint = deliveryReady
    ? "当前已有产物沉淀，可继续整理交付说明与证据。"
    : "当前还没有明确产物，建议先执行并沉淀 artifact。";

  return (
    <SectionCard
      title="交付摘要"
      extra={<Badge tone={deliveryReady ? "success" : "default"}>{deliveryReady ? "可准备交付" : "待补产物"}</Badge>}
    >
      <div className="grid gap-3 md:grid-cols-3">
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-xs text-slate-500">产物数量</div>
          <div className="mt-2 text-2xl font-semibold text-slate-900">{count}</div>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-xs text-slate-500">最近产物类型</div>
          <div className="mt-2 text-sm font-medium text-slate-900">{artifactType}</div>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-xs text-slate-500">最近引用</div>
          <div className="mt-2 text-sm font-medium text-slate-900">{latestArtifact?.artifact_ref || "—"}</div>
        </div>
      </div>

      <div className="mt-4 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-slate-700">
        {hint}
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        <button
          onClick={onExportJson}
          className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          导出当前结果 JSON
        </button>
        <button
          onClick={onExportMarkdown}
          className="rounded-xl border border-blue-300 bg-blue-50 px-4 py-2 text-sm font-medium text-blue-700 hover:bg-blue-100"
        >
          导出交付摘要 Markdown
        </button>
        <button
          onClick={onCopySummary}
          className="rounded-xl border border-emerald-300 bg-emerald-50 px-4 py-2 text-sm font-medium text-emerald-700 hover:bg-emerald-100"
        >
          复制交付摘要
        </button>
      </div>
    </SectionCard>
  );
}
