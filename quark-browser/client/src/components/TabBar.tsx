/*
 * Design: Quantum Blue Soft UI
 * TabBar: Browser-style tab bar at the top
 */
import { useApp } from "@/contexts/AppContext";
import { X, Plus, Globe } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function TabBar() {
  const { tabs, addTab, removeTab, setActiveTab } = useApp();

  return (
    <div className="flex items-center gap-1 px-3 py-1.5 border-b border-border/40"
      style={{ background: "oklch(0.975 0.005 260)" }}>
      <div className="flex items-center gap-1 flex-1 overflow-x-auto scrollbar-hide">
        <AnimatePresence mode="popLayout">
          {tabs.map((tab) => (
            <motion.div
              key={tab.id}
              layout
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.2 }}
              onClick={() => setActiveTab(tab.id)}
              className={`
                flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm cursor-pointer
                max-w-[180px] min-w-[100px] group transition-all duration-200
                ${tab.isActive
                  ? "bg-white shadow-sm border border-border/30"
                  : "hover:bg-[oklch(0.96_0.008_260)]"
                }
              `}
            >
              <Globe size={14} className="shrink-0 text-[oklch(0.55_0.06_260)]" />
              <span className="truncate text-[oklch(0.35_0.03_260)] font-medium text-xs">
                {tab.title}
              </span>
              <button
                onClick={(e) => { e.stopPropagation(); removeTab(tab.id); }}
                className="ml-auto shrink-0 opacity-0 group-hover:opacity-100 transition-opacity
                  hover:bg-[oklch(0.90_0.01_260)] rounded p-0.5"
              >
                <X size={12} className="text-[oklch(0.50_0.03_260)]" />
              </button>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
      <button
        onClick={() => addTab({ title: "新标签页", url: "quark://newtab" })}
        className="shrink-0 w-7 h-7 rounded-lg flex items-center justify-center
          hover:bg-[oklch(0.94_0.01_260)] transition-colors"
      >
        <Plus size={16} className="text-[oklch(0.50_0.03_260)]" />
      </button>
    </div>
  );
}
