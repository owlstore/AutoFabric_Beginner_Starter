/*
 * Design: Quantum Blue Soft UI
 * HistoryPage: Browsing history with timeline grouping
 */
import { useApp } from "@/contexts/AppContext";
import { motion, AnimatePresence } from "framer-motion";
import { Clock, Trash2, Search, ExternalLink, Globe } from "lucide-react";
import { useState, useMemo } from "react";
import { toast } from "sonner";

function formatTime(date: Date): string {
  return date.toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" });
}

function getDateGroup(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  if (diff < 86400000) return "今天";
  if (diff < 172800000) return "昨天";
  if (diff < 604800000) return "本周";
  return "更早";
}

export default function HistoryPage() {
  const { history, clearHistory } = useApp();
  const [searchTerm, setSearchTerm] = useState("");

  const filtered = useMemo(() =>
    history.filter(h =>
      h.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      h.url.toLowerCase().includes(searchTerm.toLowerCase())
    ), [history, searchTerm]);

  const grouped = useMemo(() => {
    const groups: Record<string, typeof history> = {};
    filtered.forEach(item => {
      const group = getDateGroup(item.visitedAt);
      if (!groups[group]) groups[group] = [];
      groups[group].push(item);
    });
    return groups;
  }, [filtered]);

  return (
    <div className="flex-1 overflow-y-auto px-6 py-6">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ background: "oklch(0.58 0.22 264 / 0.1)" }}>
              <Clock size={20} style={{ color: "oklch(0.58 0.22 264)" }} />
            </div>
            <div>
              <h2 className="text-lg font-bold" style={{ color: "oklch(0.25 0.03 260)" }}>浏览历史</h2>
              <p className="text-xs" style={{ color: "oklch(0.55 0.03 260)" }}>
                共 {history.length} 条记录
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl w-56 neu-pressed">
              <Search size={14} style={{ color: "oklch(0.55 0.04 260)" }} />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="搜索历史..."
                className="flex-1 bg-transparent outline-none text-sm"
                style={{ color: "oklch(0.25 0.03 260)" }}
              />
            </div>
            <button
              onClick={() => { clearHistory(); toast("历史记录已清空"); }}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm font-medium
                hover:bg-red-50 transition-colors text-red-400"
            >
              <Trash2 size={14} />
              清空
            </button>
          </div>
        </div>

        {/* Timeline */}
        <div className="space-y-6">
          {Object.entries(grouped).map(([group, items]) => (
            <div key={group}>
              <h3 className="text-xs font-bold mb-3 px-1 uppercase tracking-wider"
                style={{ color: "oklch(0.55 0.04 264)" }}>
                {group}
              </h3>
              <div className="space-y-1">
                <AnimatePresence>
                  {items.map((item, i) => (
                    <motion.div
                      key={item.id}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -10 }}
                      transition={{ delay: i * 0.02 }}
                      className="flex items-center gap-4 px-4 py-3 rounded-xl group
                        hover:bg-white/80 hover:shadow-sm transition-all cursor-pointer"
                    >
                      <span className="text-xs font-mono w-12 shrink-0"
                        style={{ color: "oklch(0.60 0.03 260)" }}>
                        {formatTime(item.visitedAt)}
                      </span>
                      <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 text-sm"
                        style={{ background: "oklch(0.94 0.01 260)" }}>
                        {item.favicon || <Globe size={14} className="text-[oklch(0.55_0.04_260)]" />}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate"
                          style={{ color: "oklch(0.30 0.03 260)" }}>
                          {item.title}
                        </p>
                        <p className="text-xs truncate" style={{ color: "oklch(0.60 0.03 260)" }}>
                          {item.url}
                        </p>
                      </div>
                      <button
                        onClick={() => window.open(item.url, "_blank")}
                        className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg
                          hover:bg-[oklch(0.94_0.01_260)] transition-all"
                      >
                        <ExternalLink size={14} className="text-[oklch(0.55_0.04_260)]" />
                      </button>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            </div>
          ))}
        </div>

        {filtered.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20">
            <Clock size={48} className="mb-4" style={{ color: "oklch(0.80 0.04 260)" }} />
            <p className="text-sm" style={{ color: "oklch(0.55 0.03 260)" }}>
              {searchTerm ? "未找到匹配的记录" : "暂无浏览历史"}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
