/*
 * Design: Quantum Blue Soft UI
 * Home: Central search box (upper 1/3), quick shortcuts grid, info cards (Bento Grid)
 * Hero background uses generated quantum particle network image
 */
import { useState, useRef, useEffect } from "react";
import { useApp } from "@/contexts/AppContext";
import { motion } from "framer-motion";
import {
  Search, Mic, Camera, Sparkles, Cloud, CloudSun, TrendingUp,
  FileText, Calculator, Languages, ScanLine, Newspaper,
  Globe, ShoppingCart, MessageCircle, Github, Mail, Music,
  Tv, PenLine
} from "lucide-react";
import { toast } from "sonner";

const HERO_BG = "https://private-us-east-1.manuscdn.com/sessionFile/LUR6DWgnUeDMYMT0r5ZnLE/sandbox/oYDV3iLEAEG6V50bGscZir-img-1_1770701357000_na1fn_aGVyby1iZw.png?x-oss-process=image/resize,w_1920,h_1920/format,webp/quality,q_80&Expires=1798761600&Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvTFVSNkRXZ25VZURNWU1UMHI1Wm5MRS9zYW5kYm94L29ZRFYzaUxFQUVHNlY1MGJHc2NaaXItaW1nLTFfMTc3MDcwMTM1NzAwMF9uYTFmbl9hR1Z5YnkxaVp3LnBuZz94LW9zcy1wcm9jZXNzPWltYWdlL3Jlc2l6ZSx3XzE5MjAsaF8xOTIwL2Zvcm1hdCx3ZWJwL3F1YWxpdHkscV84MCIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc5ODc2MTYwMH19fV19&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=igzK0CwzOKcRjPLFb6qt9M~Lpc3FIDRmbIxzsXb~PgWPQ~aESgDemvaZH2WhxsXXfiNCedpqwrcQl2M1RXv4VboO8pd5PqAwfO023nWOnb5By6Xc-HK5y241FzxfDDpMkVn~z-jHzQrMDs5Hmkkc-j34xrbweNyRuR43yc-7ofxyE6y8QbaqDRFFVK0zDB4T2xqHwWGYH3OvcK4QaKFz7WPIVbvtKU2HYBv6hvWpXHvSswI64ntQVphFNPyCdPKnWp554HBRyI92z0~3RdeLaL-99M8XWc0HYyK1UpeEmobWGuSTsrhsVeBTKqJl2lIFfsTezNXvN24NnBoP2g-7Yg__";

const quickLinks = [
  { icon: Search, label: "百度", url: "https://www.baidu.com", color: "#4F7BF7" },
  { icon: Tv, label: "哔哩哔哩", url: "https://www.bilibili.com", color: "#00A1D6" },
  { icon: MessageCircle, label: "知乎", url: "https://www.zhihu.com", color: "#0084FF" },
  { icon: PenLine, label: "微博", url: "https://weibo.com", color: "#E6162D" },
  { icon: Github, label: "GitHub", url: "https://github.com", color: "#333333" },
  { icon: ShoppingCart, label: "淘宝", url: "https://www.taobao.com", color: "#FF5000" },
  { icon: Mail, label: "QQ邮箱", url: "https://mail.qq.com", color: "#4F7BF7" },
  { icon: Music, label: "网易云", url: "https://music.163.com", color: "#C20C0C" },
];

const hotSearches = [
  "AI大模型最新进展",
  "2026春节档电影",
  "量子计算突破",
  "新能源汽车排行",
  "ChatGPT替代品",
];

const toolShortcuts = [
  { icon: Calculator, label: "计算器", color: "#4F7BF7" },
  { icon: Languages, label: "翻译", color: "#7C3AED" },
  { icon: ScanLine, label: "扫描", color: "#10B981" },
  { icon: CloudSun, label: "天气", color: "#F59E0B" },
  { icon: FileText, label: "文档", color: "#EC4899" },
  { icon: Newspaper, label: "资讯", color: "#06B6D4" },
];

export default function HomePage() {
  const { setActivePage, setSearchQuery, addHistory } = useApp();
  const [query, setQuery] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSearch = () => {
    if (!query.trim()) return;
    setSearchQuery(query.trim());
    addHistory({ title: query.trim(), url: `quark://search?q=${encodeURIComponent(query.trim())}` });
    setActivePage("search");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleSearch();
  };

  // Current time for greeting
  const [time, setTime] = useState(new Date());
  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 60000);
    return () => clearInterval(timer);
  }, []);

  const greeting = time.getHours() < 12 ? "上午好" : time.getHours() < 18 ? "下午好" : "晚上好";

  return (
    <div className="flex-1 overflow-y-auto">
      {/* Hero Section with Search */}
      <div className="relative min-h-[380px] md:min-h-[420px] flex flex-col items-center justify-center px-4"
        style={{
          backgroundImage: `url(${HERO_BG})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
        }}
      >
        {/* Overlay */}
        <div className="absolute inset-0" style={{ background: "oklch(0.965 0.006 260 / 0.55)" }} />

        <div className="relative z-10 w-full max-w-2xl mx-auto text-center">
          {/* Brand */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="text-4xl md:text-5xl font-display font-extrabold mb-2 tracking-tight"
              style={{ color: "oklch(0.25 0.03 260)" }}>
              Quark
            </h1>
            <p className="text-sm font-medium mb-6 md:mb-8" style={{ color: "oklch(0.45 0.04 260)" }}>
              {greeting}，更好的搜索从这里开始
            </p>
          </motion.div>

          {/* Search Box */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className={`
              relative rounded-2xl transition-all duration-300
              ${isFocused ? "ai-glow" : "neu-raised"}
            `}
          >
            <div className="flex items-center gap-2 md:gap-3 px-4 md:px-5 py-3 md:py-3.5 rounded-2xl bg-white/90 backdrop-blur-sm">
              <Search size={20} className="shrink-0" style={{ color: "oklch(0.58 0.22 264)" }} />
              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
                onKeyDown={handleKeyDown}
                placeholder="搜索或输入网址..."
                className="flex-1 bg-transparent outline-none text-sm md:text-base font-medium
                  placeholder:text-[oklch(0.65_0.02_260)]"
                style={{ color: "oklch(0.25 0.03 260)" }}
              />
              <button
                onClick={() => toast("语音搜索功能即将上线")}
                className="shrink-0 w-8 h-8 rounded-lg flex items-center justify-center
                  hover:bg-[oklch(0.94_0.01_260)] transition-colors hidden sm:flex"
              >
                <Mic size={18} className="text-[oklch(0.50_0.03_260)]" />
              </button>
              <button
                onClick={() => toast("拍照搜索功能即将上线")}
                className="shrink-0 w-8 h-8 rounded-lg flex items-center justify-center
                  hover:bg-[oklch(0.94_0.01_260)] transition-colors hidden sm:flex"
              >
                <Camera size={18} className="text-[oklch(0.50_0.03_260)]" />
              </button>
              <button
                onClick={() => { setActivePage("ai"); }}
                className="shrink-0 px-3 py-1.5 rounded-xl text-xs font-semibold text-white
                  flex items-center gap-1 ai-glow-pulse transition-all"
                style={{ background: "linear-gradient(135deg, #4F7BF7, #7C3AED)" }}
              >
                <Sparkles size={14} />
                AI
              </button>
            </div>
          </motion.div>

          {/* Hot searches */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="flex flex-wrap items-center justify-center gap-2 mt-4"
          >
            <TrendingUp size={14} style={{ color: "oklch(0.55 0.06 260)" }} />
            {hotSearches.map((term, i) => (
              <button
                key={i}
                onClick={() => { setQuery(term); setSearchQuery(term); setActivePage("search"); }}
                className="text-xs px-2.5 py-1 rounded-full transition-colors
                  hover:bg-white/60 backdrop-blur-sm"
                style={{
                  color: "oklch(0.40 0.04 260)",
                  background: "oklch(0.97 0.005 260 / 0.6)",
                }}
              >
                {term}
              </button>
            ))}
          </motion.div>
        </div>
      </div>

      {/* Quick Links */}
      <div className="max-w-4xl mx-auto px-4 -mt-6 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glass-card rounded-2xl p-4 md:p-5"
        >
          <div className="grid grid-cols-4 sm:grid-cols-8 gap-3 md:gap-4">
            {quickLinks.map((link, i) => {
              const Icon = link.icon;
              return (
                <motion.button
                  key={i}
                  whileHover={{ y: -2 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => {
                    addHistory({ title: link.label, url: link.url });
                    toast(`正在打开 ${link.label}`);
                  }}
                  className="flex flex-col items-center gap-1.5 group"
                >
                  <div className="w-11 h-11 md:w-12 md:h-12 rounded-xl neu-flat flex items-center justify-center
                    group-hover:shadow-lg transition-all duration-200">
                    <Icon size={20} style={{ color: link.color }} />
                  </div>
                  <span className="text-[11px] md:text-xs font-medium" style={{ color: "oklch(0.45 0.03 260)" }}>
                    {link.label}
                  </span>
                </motion.button>
              );
            })}
          </div>
        </motion.div>
      </div>

      {/* Bento Grid */}
      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {/* Weather Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="neu-raised rounded-2xl p-5 col-span-1"
          >
            <div className="flex items-center gap-2 mb-3">
              <CloudSun size={18} style={{ color: "#F59E0B" }} />
              <span className="text-xs font-semibold" style={{ color: "oklch(0.50 0.03 260)" }}>天气</span>
            </div>
            <div className="flex items-end gap-2">
              <span className="text-3xl font-bold" style={{ color: "oklch(0.25 0.03 260)" }}>18°</span>
              <span className="text-sm mb-1" style={{ color: "oklch(0.50 0.03 260)" }}>晴</span>
            </div>
            <p className="text-xs mt-2" style={{ color: "oklch(0.55 0.03 260)" }}>
              北京 · 空气质量良好
            </p>
          </motion.div>

          {/* AI Assistant Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35 }}
            onClick={() => setActivePage("ai")}
            className="rounded-2xl p-5 col-span-1 cursor-pointer group transition-all duration-300
              hover:shadow-lg"
            style={{
              background: "linear-gradient(135deg, oklch(0.58 0.22 264 / 0.1), oklch(0.55 0.20 300 / 0.1))",
              border: "1px solid oklch(0.58 0.22 264 / 0.2)",
            }}
          >
            <div className="flex items-center gap-2 mb-3">
              <div className="w-7 h-7 rounded-lg flex items-center justify-center ai-glow-pulse"
                style={{ background: "linear-gradient(135deg, #4F7BF7, #7C3AED)" }}>
                <Sparkles size={14} className="text-white" />
              </div>
              <span className="text-xs font-semibold" style={{ color: "oklch(0.40 0.06 264)" }}>AI 助手</span>
            </div>
            <p className="text-sm font-medium" style={{ color: "oklch(0.30 0.04 260)" }}>
              智能搜索、写作、翻译
            </p>
            <p className="text-xs mt-1" style={{ color: "oklch(0.50 0.04 264)" }}>
              点击开始对话 →
            </p>
          </motion.div>

          {/* Cloud Drive Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            onClick={() => setActivePage("drive")}
            className="neu-raised rounded-2xl p-5 col-span-1 cursor-pointer group
              hover:shadow-lg transition-all duration-300"
          >
            <div className="flex items-center gap-2 mb-3">
              <Cloud size={18} style={{ color: "#06B6D4" }} />
              <span className="text-xs font-semibold" style={{ color: "oklch(0.50 0.03 260)" }}>网盘</span>
            </div>
            <p className="text-sm font-medium" style={{ color: "oklch(0.30 0.03 260)" }}>
              6TB 超大空间
            </p>
            <div className="mt-2 h-1.5 rounded-full overflow-hidden" style={{ background: "oklch(0.92 0.008 260)" }}>
              <div className="h-full rounded-full" style={{
                width: "23%",
                background: "linear-gradient(90deg, #4F7BF7, #06B6D4)"
              }} />
            </div>
            <p className="text-xs mt-1.5" style={{ color: "oklch(0.55 0.03 260)" }}>
              已用 1.38TB / 6TB
            </p>
          </motion.div>

          {/* Tools Grid */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.45 }}
            className="neu-raised rounded-2xl p-5 col-span-1 sm:col-span-2"
          >
            <div className="flex items-center gap-2 mb-4">
              <Sparkles size={18} style={{ color: "oklch(0.58 0.22 264)" }} />
              <span className="text-xs font-semibold" style={{ color: "oklch(0.50 0.03 260)" }}>常用工具</span>
            </div>
            <div className="grid grid-cols-3 sm:grid-cols-6 gap-3">
              {toolShortcuts.map((tool, i) => {
                const Icon = tool.icon;
                return (
                  <motion.button
                    key={i}
                    whileHover={{ y: -2 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setActivePage("tools")}
                    className="flex flex-col items-center gap-2 group"
                  >
                    <div className="w-10 h-10 md:w-11 md:h-11 rounded-xl flex items-center justify-center transition-all
                      group-hover:shadow-md"
                      style={{ background: `${tool.color}15` }}
                    >
                      <Icon size={18} style={{ color: tool.color }} />
                    </div>
                    <span className="text-[11px] md:text-xs font-medium" style={{ color: "oklch(0.45 0.03 260)" }}>
                      {tool.label}
                    </span>
                  </motion.button>
                );
              })}
            </div>
          </motion.div>

          {/* Hot News Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="neu-raised rounded-2xl p-5 col-span-1"
          >
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp size={18} style={{ color: "#EC4899" }} />
              <span className="text-xs font-semibold" style={{ color: "oklch(0.50 0.03 260)" }}>热搜榜</span>
            </div>
            <div className="space-y-2.5">
              {["AI Agent革命", "量子芯片突破", "火星探测进展", "新能源政策"].map((item, i) => (
                <button
                  key={i}
                  onClick={() => { setSearchQuery(item); setActivePage("search"); }}
                  className="flex items-center gap-2 w-full text-left group"
                >
                  <span className="w-5 h-5 rounded-md flex items-center justify-center text-[10px] font-bold"
                    style={{
                      background: i < 3 ? "linear-gradient(135deg, #4F7BF7, #7C3AED)" : "oklch(0.92 0.008 260)",
                      color: i < 3 ? "white" : "oklch(0.50 0.03 260)",
                    }}
                  >
                    {i + 1}
                  </span>
                  <span className="text-sm truncate group-hover:text-[oklch(0.58_0.22_264)] transition-colors"
                    style={{ color: "oklch(0.35 0.03 260)" }}>
                    {item}
                  </span>
                </button>
              ))}
            </div>
          </motion.div>
        </div>
      </div>

      {/* Footer */}
      <div className="text-center py-4 px-4">
        <p className="text-xs" style={{ color: "oklch(0.70 0.02 260)" }}>
          Quark Browser · 极速智能浏览体验
        </p>
      </div>
    </div>
  );
}
