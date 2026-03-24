/*
 * Design: Quantum Blue Soft UI
 * Sidebar: Narrow icon rail (56px) expandable to 200px
 * Neumorphic raised buttons with active state pressed effect
 */
import { useApp, type ActivePage } from "@/contexts/AppContext";
import { motion, AnimatePresence } from "framer-motion";
import {
  Home, Search, Bot, HardDrive, Wrench, Bookmark, Clock, Settings,
  ChevronLeft, ChevronRight
} from "lucide-react";

const navItems: { id: ActivePage; icon: typeof Home; label: string }[] = [
  { id: "home", icon: Home, label: "首页" },
  { id: "search", icon: Search, label: "搜索" },
  { id: "ai", icon: Bot, label: "AI 助手" },
  { id: "drive", icon: HardDrive, label: "网盘" },
  { id: "tools", icon: Wrench, label: "工具箱" },
  { id: "bookmarks", icon: Bookmark, label: "书签" },
  { id: "history", icon: Clock, label: "历史" },
  { id: "settings", icon: Settings, label: "设置" },
];

export default function Sidebar() {
  const { activePage, setActivePage, sidebarCollapsed, setSidebarCollapsed } = useApp();

  return (
    <motion.aside
      initial={false}
      animate={{ width: sidebarCollapsed ? 56 : 200 }}
      transition={{ duration: 0.25, ease: [0.4, 0, 0.2, 1] }}
      className="h-screen flex flex-col py-4 px-2 border-r border-border/50 relative z-20"
      style={{ background: "oklch(0.975 0.005 260)" }}
    >
      {/* Logo */}
      <div className="flex items-center justify-center mb-6 px-1">
        <div className="w-8 h-8 rounded-xl flex items-center justify-center"
          style={{
            background: "linear-gradient(135deg, #4F7BF7, #7C3AED)",
            boxShadow: "0 4px 12px oklch(0.58 0.22 264 / 0.3)"
          }}
        >
          <span className="text-white font-bold text-sm">Q</span>
        </div>
        <AnimatePresence>
          {!sidebarCollapsed && (
            <motion.span
              initial={{ opacity: 0, width: 0 }}
              animate={{ opacity: 1, width: "auto" }}
              exit={{ opacity: 0, width: 0 }}
              className="ml-2 font-display font-bold text-lg overflow-hidden whitespace-nowrap"
              style={{ color: "oklch(0.30 0.04 260)" }}
            >
              Quark
            </motion.span>
          )}
        </AnimatePresence>
      </div>

      {/* Nav Items */}
      <nav className="flex-1 flex flex-col gap-1.5">
        {navItems.map((item) => {
          const isActive = activePage === item.id;
          const Icon = item.icon;
          return (
            <button
              key={item.id}
              onClick={() => setActivePage(item.id)}
              className={`
                flex items-center gap-3 rounded-xl transition-all duration-200 group relative
                ${sidebarCollapsed ? "justify-center px-0 py-2.5 mx-auto w-10 h-10" : "px-3 py-2.5"}
                ${isActive
                  ? "neu-pressed"
                  : "hover:bg-[oklch(0.96_0.008_260)] active:neu-pressed"
                }
              `}
            >
              <Icon
                size={20}
                className={`shrink-0 transition-colors duration-200 ${
                  isActive
                    ? "text-[oklch(0.58_0.22_264)]"
                    : "text-[oklch(0.50_0.03_260)] group-hover:text-[oklch(0.40_0.06_260)]"
                }`}
              />
              <AnimatePresence>
                {!sidebarCollapsed && (
                  <motion.span
                    initial={{ opacity: 0, width: 0 }}
                    animate={{ opacity: 1, width: "auto" }}
                    exit={{ opacity: 0, width: 0 }}
                    className={`text-sm font-medium overflow-hidden whitespace-nowrap ${
                      isActive
                        ? "text-[oklch(0.58_0.22_264)]"
                        : "text-[oklch(0.45_0.03_260)] group-hover:text-[oklch(0.30_0.04_260)]"
                    }`}
                  >
                    {item.label}
                  </motion.span>
                )}
              </AnimatePresence>
              {/* Active indicator */}
              {isActive && (
                <motion.div
                  layoutId="sidebar-active"
                  className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 rounded-r-full"
                  style={{ background: "linear-gradient(180deg, #4F7BF7, #7C3AED)" }}
                  transition={{ type: "spring", stiffness: 400, damping: 30 }}
                />
              )}
              {/* Tooltip for collapsed */}
              {sidebarCollapsed && (
                <div className="absolute left-full ml-2 px-2 py-1 rounded-lg text-xs font-medium whitespace-nowrap
                  opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50
                  bg-[oklch(0.20_0.02_260)] text-white shadow-lg">
                  {item.label}
                </div>
              )}
            </button>
          );
        })}
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
        className="flex items-center justify-center w-8 h-8 rounded-lg mx-auto mt-2
          hover:bg-[oklch(0.94_0.01_260)] transition-colors"
      >
        {sidebarCollapsed ? (
          <ChevronRight size={16} className="text-[oklch(0.50_0.03_260)]" />
        ) : (
          <ChevronLeft size={16} className="text-[oklch(0.50_0.03_260)]" />
        )}
      </button>
    </motion.aside>
  );
}
