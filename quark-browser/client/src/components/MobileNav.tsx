/*
 * Design: Quantum Blue Soft UI
 * MobileNav: Bottom tab bar for mobile devices
 */
import { useApp, type ActivePage } from "@/contexts/AppContext";
import { Home, Search, Bot, HardDrive, Wrench } from "lucide-react";
import { motion } from "framer-motion";

const navItems: { id: ActivePage; icon: typeof Home; label: string }[] = [
  { id: "home", icon: Home, label: "首页" },
  { id: "search", icon: Search, label: "搜索" },
  { id: "ai", icon: Bot, label: "AI" },
  { id: "drive", icon: HardDrive, label: "网盘" },
  { id: "tools", icon: Wrench, label: "工具" },
];

export default function MobileNav() {
  const { activePage, setActivePage } = useApp();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-border/40 px-2 py-1 safe-area-pb"
      style={{ background: "oklch(0.98 0.004 260 / 0.95)", backdropFilter: "blur(16px)" }}>
      <div className="flex items-center justify-around">
        {navItems.map((item) => {
          const isActive = activePage === item.id;
          const Icon = item.icon;
          return (
            <button
              key={item.id}
              onClick={() => setActivePage(item.id)}
              className="flex flex-col items-center gap-0.5 py-1.5 px-3 rounded-xl transition-all relative"
            >
              {isActive && (
                <motion.div
                  layoutId="mobile-nav-active"
                  className="absolute -top-1 w-5 h-0.5 rounded-full"
                  style={{ background: "linear-gradient(90deg, #4F7BF7, #7C3AED)" }}
                  transition={{ type: "spring", stiffness: 400, damping: 30 }}
                />
              )}
              <Icon
                size={20}
                className={`transition-colors ${
                  isActive ? "text-[oklch(0.58_0.22_264)]" : "text-[oklch(0.55_0.03_260)]"
                }`}
              />
              <span className={`text-[10px] font-medium transition-colors ${
                isActive ? "text-[oklch(0.50_0.20_264)]" : "text-[oklch(0.55_0.03_260)]"
              }`}>
                {item.label}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
