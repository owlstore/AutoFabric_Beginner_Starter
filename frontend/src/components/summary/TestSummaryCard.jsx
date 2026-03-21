import SectionCard from "../common/SectionCard";
import Badge from "../common/Badge";

export default function TestSummaryCard({ verifications }) {
  const count = verifications?.length || 0;
  const latest = verifications?.[0] || null;
  const passed = verifications?.some((item) => item.status === "passed");

  const statusTone = latest?.status === "passed" ? "success" : latest?.status ? "warning" : "default";
  const statusText = latest?.status ? latest.status : "暂无验证";

  const nextHint = passed
    ? "验证结果已通过，可继续推进交付整理。"
    : count > 0
    ? "已有验证记录，建议继续补充验证覆盖。"
    : "当前尚无验证记录，建议执行后补齐验证。";

  return (
    <SectionCard
      title="测试摘要"
      extra={<Badge tone={statusTone}>{statusText}</Badge>}
    >
      <div className="grid gap-3 md:grid-cols-3">
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-xs text-slate-500">验证记录数</div>
          <div className="mt-2 text-2xl font-semibold text-slate-900">{count}</div>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-xs text-slate-500">最近验证器</div>
          <div className="mt-2 text-sm font-medium text-slate-900">{latest?.verifier_name || "—"}</div>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-xs text-slate-500">最近状态</div>
          <div className="mt-2 text-sm font-medium text-slate-900">{statusText}</div>
        </div>
      </div>

      <div className="mt-4 rounded-2xl border border-blue-200 bg-blue-50 p-4 text-sm text-slate-700">
        {nextHint}
      </div>
    </SectionCard>
  );
}
