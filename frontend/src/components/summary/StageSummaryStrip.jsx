import MetricCard from "../common/MetricCard";

const STAGE_ITEMS = [
  { key: "requirement", label: "需求", tone: "default" },
  { key: "clarification", label: "澄清", tone: "info" },
  { key: "prototype", label: "原型", tone: "warning" },
  { key: "orchestration", label: "编排", tone: "default" },
  { key: "execution", label: "执行", tone: "info" },
  { key: "testing", label: "测试", tone: "success" },
  { key: "delivery", label: "交付", tone: "success" },
];

export default function StageSummaryStrip({ stageCounts, quickFilter, setQuickFilter }) {
  return (
    <div className="mb-6 grid gap-4 md:grid-cols-2 xl:grid-cols-7">
      <MetricCard
        label="全部"
        value={Object.values(stageCounts || {}).reduce((sum, n) => sum + Number(n || 0), 0)}
        active={quickFilter === "all"}
        onClick={() => setQuickFilter("all")}
      />
      {STAGE_ITEMS.map((item) => (
        <MetricCard
          key={item.key}
          label={item.label}
          value={stageCounts?.[item.key] ?? 0}
          tone={item.tone}
          active={quickFilter === item.key}
          onClick={() => setQuickFilter(item.key)}
        />
      ))}
    </div>
  );
}
