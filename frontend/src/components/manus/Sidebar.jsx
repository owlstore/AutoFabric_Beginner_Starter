import { useState } from "react";
import QuarkButton from "../quark/QuarkButton";

export default function Sidebar({ projects, activeId, onSelect, onCreate }) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={`flex flex-col border-r border-[#1e1e22] bg-[#131316] transition-all duration-300 ${
        collapsed ? "w-[52px]" : "w-[260px]"
      }`}
    >
      {/* Logo area */}
      <div className="flex items-center gap-2.5 px-4 h-[56px] border-b border-[#1e1e22]">
        {!collapsed && (
          <div className="flex items-center gap-2 min-w-0">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold shrink-0">
              AF
            </div>
            <span className="text-[13px] font-semibold text-white tracking-tight truncate">
              AutoFabric
            </span>
          </div>
        )}
        <QuarkButton
          onClick={() => setCollapsed((c) => !c)}
          variant="raw"
          className="ml-auto p-1.5 rounded-md hover:bg-[#1e1e22] text-[#71717a] transition-colors"
          title={collapsed ? "展开" : "收起"}
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            {collapsed ? (
              <path d="M5 3l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            ) : (
              <path d="M9 3L5 7l4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            )}
          </svg>
        </QuarkButton>
      </div>

      {/* New project */}
      <div className="px-2.5 pt-3 pb-1">
        <QuarkButton
          onClick={onCreate}
          variant="raw"
          className={`w-full flex items-center gap-2 rounded-lg px-3 py-2 text-[13px] text-[#a1a1aa] border border-dashed border-[#2a2a2e] hover:border-[#3b82f6] hover:text-[#60a5fa] hover:bg-[#1a1a2e] transition-all duration-200 ${
            collapsed ? "justify-center px-0" : ""
          }`}
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" className="shrink-0">
            <path d="M7 2v10M2 7h10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
          {!collapsed && <span>新建项目</span>}
        </QuarkButton>
      </div>

      {/* Project list */}
      <nav className="flex-1 overflow-y-auto px-2 py-1.5">
        {projects.map((p, i) => {
          const isActive = p.id === activeId;
          return (
            <QuarkButton
              key={p.id}
              onClick={() => onSelect(p.id)}
              variant="raw"
              className={`group w-full text-left rounded-lg px-3 py-2 mb-0.5 transition-all duration-150 ${
                isActive
                  ? "bg-[#1e1e28] text-white"
                  : "text-[#a1a1aa] hover:bg-[#1a1a1e] hover:text-[#d4d4d8]"
              } ${collapsed ? "flex justify-center px-0" : ""}`}
              title={p.name}
              style={{ animationDelay: `${i * 30}ms` }}
            >
              {collapsed ? (
                <div className={`w-7 h-7 rounded-md flex items-center justify-center text-[11px] font-semibold ${
                  isActive ? "bg-blue-600/20 text-blue-400" : "bg-[#1e1e22] text-[#71717a]"
                }`}>
                  {p.name?.charAt(0)?.toUpperCase() || "#"}
                </div>
              ) : (
                <div className="flex items-center gap-2.5 min-w-0">
                  <div className={`w-1.5 h-1.5 rounded-full shrink-0 transition-colors ${
                    isActive ? "bg-blue-400" : "bg-transparent group-hover:bg-[#3a3a3e]"
                  }`} />
                  <span className="text-[13px] truncate">{p.name || `Project #${p.id}`}</span>
                </div>
              )}
            </QuarkButton>
          );
        })}

        {projects.length === 0 && !collapsed && (
          <div className="px-3 py-10 text-center">
            <div className="text-[#3a3a3e] text-2xl mb-2">○</div>
            <p className="text-[11px] text-[#52525b]">暂无项目</p>
          </div>
        )}
      </nav>
    </aside>
  );
}
