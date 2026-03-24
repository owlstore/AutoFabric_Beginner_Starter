/*
 * Design: Quantum Blue Soft UI
 * SettingsPage: App settings with sections
 */
import { useState } from "react";
import { motion } from "framer-motion";
import {
  Settings, Shield, Eye, Globe, Palette, Bell, Database,
  HardDrive, Info, ChevronRight, Moon, Sun, Smartphone, Monitor
} from "lucide-react";
import { toast } from "sonner";

interface SettingItem {
  icon: typeof Settings;
  label: string;
  description: string;
  color: string;
  type: "toggle" | "select" | "action";
  value?: boolean;
}

const settingSections: { title: string; items: SettingItem[] }[] = [
  {
    title: "通用",
    items: [
      { icon: Globe, label: "默认搜索引擎", description: "百度", color: "#4F7BF7", type: "select" },
      { icon: Palette, label: "主题外观", description: "跟随系统", color: "#7C3AED", type: "select" },
      { icon: Globe, label: "语言", description: "简体中文", color: "#06B6D4", type: "select" },
      { icon: Monitor, label: "字体大小", description: "标准", color: "#F59E0B", type: "select" },
    ],
  },
  {
    title: "隐私与安全",
    items: [
      { icon: Shield, label: "广告拦截", description: "已开启", color: "#10B981", type: "toggle", value: true },
      { icon: Eye, label: "无痕模式", description: "已关闭", color: "#8B5CF6", type: "toggle", value: false },
      { icon: Shield, label: "安全DNS", description: "已开启", color: "#4F7BF7", type: "toggle", value: true },
      { icon: Database, label: "清除浏览数据", description: "缓存、Cookie、历史", color: "#EF4444", type: "action" },
    ],
  },
  {
    title: "通知与下载",
    items: [
      { icon: Bell, label: "推送通知", description: "已开启", color: "#F59E0B", type: "toggle", value: true },
      { icon: HardDrive, label: "下载路径", description: "默认路径", color: "#06B6D4", type: "select" },
      { icon: Smartphone, label: "同步设置", description: "已登录", color: "#7C3AED", type: "action" },
    ],
  },
  {
    title: "关于",
    items: [
      { icon: Info, label: "版本信息", description: "Quark Browser v2.0.0", color: "#6B7280", type: "action" },
    ],
  },
];

export default function SettingsPage() {
  const [toggles, setToggles] = useState<Record<string, boolean>>({
    "广告拦截": true,
    "无痕模式": false,
    "安全DNS": true,
    "推送通知": true,
  });

  const handleToggle = (label: string) => {
    setToggles(prev => ({ ...prev, [label]: !prev[label] }));
    toast(`${label}已${toggles[label] ? "关闭" : "开启"}`);
  };

  return (
    <div className="flex-1 overflow-y-auto px-6 py-6">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center"
            style={{ background: "oklch(0.58 0.22 264 / 0.1)" }}>
            <Settings size={20} style={{ color: "oklch(0.58 0.22 264)" }} />
          </div>
          <h2 className="text-lg font-bold" style={{ color: "oklch(0.25 0.03 260)" }}>设置</h2>
        </div>

        {/* Theme quick toggle */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 p-5 rounded-2xl"
          style={{
            background: "linear-gradient(135deg, oklch(0.58 0.22 264 / 0.08), oklch(0.55 0.20 300 / 0.08))",
            border: "1px solid oklch(0.58 0.22 264 / 0.15)",
          }}
        >
          <p className="text-sm font-semibold mb-3" style={{ color: "oklch(0.35 0.04 260)" }}>
            主题模式
          </p>
          <div className="flex gap-3">
            {[
              { icon: Sun, label: "浅色", active: true },
              { icon: Moon, label: "深色", active: false },
              { icon: Monitor, label: "系统", active: false },
            ].map((theme) => {
              const Icon = theme.icon;
              return (
                <button
                  key={theme.label}
                  onClick={() => toast(`已切换到${theme.label}模式`)}
                  className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-medium
                    transition-all duration-200 ${
                      theme.active
                        ? "bg-white shadow-sm"
                        : "hover:bg-white/50"
                    }`}
                  style={{ color: theme.active ? "oklch(0.58 0.22 264)" : "oklch(0.50 0.03 260)" }}
                >
                  <Icon size={16} />
                  {theme.label}
                </button>
              );
            })}
          </div>
        </motion.div>

        {/* Settings sections */}
        {settingSections.map((section, si) => (
          <motion.div
            key={section.title}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: si * 0.05 }}
            className="mb-6"
          >
            <h3 className="text-xs font-bold mb-3 px-1 uppercase tracking-wider"
              style={{ color: "oklch(0.55 0.04 264)" }}>
              {section.title}
            </h3>
            <div className="neu-raised rounded-2xl overflow-hidden divide-y divide-border/30">
              {section.items.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.label}
                    onClick={() => {
                      if (item.type === "toggle") handleToggle(item.label);
                      else toast(`${item.label}设置即将上线`);
                    }}
                    className="w-full flex items-center gap-4 px-4 py-3.5 text-left
                      hover:bg-[oklch(0.97_0.005_260)] transition-colors"
                  >
                    <div className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0"
                      style={{ background: `${item.color}12` }}>
                      <Icon size={18} style={{ color: item.color }} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium" style={{ color: "oklch(0.30 0.03 260)" }}>
                        {item.label}
                      </p>
                      <p className="text-xs" style={{ color: "oklch(0.55 0.03 260)" }}>
                        {item.type === "toggle"
                          ? (toggles[item.label] ? "已开启" : "已关闭")
                          : item.description
                        }
                      </p>
                    </div>
                    {item.type === "toggle" ? (
                      <div className={`w-11 h-6 rounded-full p-0.5 transition-colors duration-200 ${
                        toggles[item.label] ? "" : ""
                      }`}
                        style={{
                          background: toggles[item.label]
                            ? "linear-gradient(135deg, #4F7BF7, #7C3AED)"
                            : "oklch(0.85 0.01 260)"
                        }}
                      >
                        <div className={`w-5 h-5 rounded-full bg-white shadow-sm transition-transform duration-200 ${
                          toggles[item.label] ? "translate-x-5" : "translate-x-0"
                        }`} />
                      </div>
                    ) : (
                      <ChevronRight size={16} className="text-[oklch(0.65_0.03_260)]" />
                    )}
                  </button>
                );
              })}
            </div>
          </motion.div>
        ))}

        {/* Footer */}
        <div className="text-center py-8">
          <div className="w-10 h-10 rounded-xl mx-auto mb-2 flex items-center justify-center"
            style={{
              background: "linear-gradient(135deg, #4F7BF7, #7C3AED)",
              boxShadow: "0 4px 12px oklch(0.58 0.22 264 / 0.3)"
            }}>
            <span className="text-white font-bold text-sm">Q</span>
          </div>
          <p className="text-xs font-medium" style={{ color: "oklch(0.50 0.03 260)" }}>
            Quark Browser v2.0.0
          </p>
          <p className="text-xs mt-1" style={{ color: "oklch(0.65 0.02 260)" }}>
            极速、智能、安全的浏览体验
          </p>
        </div>
      </div>
    </div>
  );
}
