import SectionCard from "../common/SectionCard";
import Badge from "../common/Badge";
import JsonBlock from "../common/JsonBlock";

function renderSectionData(section) {
  if (!section) return null;

  if (section.type === "list") {
    const items = Array.isArray(section.data) ? section.data : [];
    if (!items.length) {
      return <div className="text-sm text-slate-500">暂无内容</div>;
    }
    return (
      <div className="space-y-3">
        {items.map((item, index) => (
          <div key={item?.id ?? index} className="rounded-2xl border border-slate-200 p-4">
            <JsonBlock data={item} />
          </div>
        ))}
      </div>
    );
  }

  return <JsonBlock data={section.data ?? {}} />;
}

export default function DetailSectionsPanel({ sections = [] }) {
  if (!sections.length) {
    return (
      <SectionCard title="阶段详情">
        <div className="text-sm text-slate-500">暂无阶段详情。</div>
      </SectionCard>
    );
  }

  return (
    <SectionCard
      title="阶段详情"
      extra={<Badge tone="info">{sections.length} 个分区</Badge>}
    >
      <div className="space-y-5">
        {sections.filter((x) => x?.visible !== false).map((section) => (
          <div key={section.key} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <div className="mb-3 flex items-center justify-between gap-3">
              <div className="text-sm font-semibold text-slate-900">{section.label}</div>
              <div className="flex items-center gap-2">
                <Badge tone="default">{section.type}</Badge>
                {typeof section.count === "number" ? <Badge tone="info">{section.count}</Badge> : null}
              </div>
            </div>
            {renderSectionData(section)}
          </div>
        ))}
      </div>
    </SectionCard>
  );
}
