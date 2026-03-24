/*
 * Design: Quantum Blue Soft UI
 * ToolsPage: Bento grid of tools - calculator, translator, weather, scanner, etc.
 */
import { useState } from "react";
import { motion } from "framer-motion";
import {
  Calculator, Languages, CloudSun, ScanLine, FileText, Newspaper,
  QrCode, Palette, Timer, Ruler, Hash, BookOpen, Globe, Zap,
  Camera, PenLine, Sparkles
} from "lucide-react";
import { toast } from "sonner";

const TOOLS_IMG = "https://private-us-east-1.manuscdn.com/sessionFile/LUR6DWgnUeDMYMT0r5ZnLE/sandbox/oYDV3iLEAEG6V50bGscZir-img-4_1770701346000_na1fn_dG9vbHMtaWxsdXN0cmF0aW9u.png?x-oss-process=image/resize,w_1920,h_1920/format,webp/quality,q_80&Expires=1798761600&Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvTFVSNkRXZ25VZURNWU1UMHI1Wm5MRS9zYW5kYm94L29ZRFYzaUxFQUVHNlY1MGJHc2NaaXItaW1nLTRfMTc3MDcwMTM0NjAwMF9uYTFmbl9kRzl2YkhNdGFXeHNkWE4wY21GMGFXOXUucG5nP3gtb3NzLXByb2Nlc3M9aW1hZ2UvcmVzaXplLHdfMTkyMCxoXzE5MjAvZm9ybWF0LHdlYnAvcXVhbGl0eSxxXzgwIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNzk4NzYxNjAwfX19XX0_&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=qXBzAOHk2no2FeWXj5gsYGuyfOwwDF1NHolJ9-K5AaSNaGhz5E2B7tizwylXSlRRnevBy5Q-MZ29aZNnkmWR2FCpel~zlBZSQ39KH5-rv-XCV7yBpkPkFODZethBPUlyt993sdrw6cx~drseu7YhUFsjmg6R5gZBH8cdnt6NLE4-Mcj6~Xaoi0PPDobof0jTk7r7rdY0R0gCCXt~5bl-BYODwSdpXTL5jcSOW8Yr1h~8MG1~h2K1jmZqXyZrV3W6IiKC8E3lyy8I3i6ihS-oTz85qhxisg1sBcpewZ~p19L2dvNHM8tAHWPT~-LnpEwMCRrPQv9czKnsuHM5pKs1Mw__";

// Calculator component
function CalculatorTool() {
  const [display, setDisplay] = useState("0");
  const [prev, setPrev] = useState<number | null>(null);
  const [op, setOp] = useState<string | null>(null);
  const [reset, setReset] = useState(false);

  const handleNum = (n: string) => {
    if (reset) { setDisplay(n); setReset(false); return; }
    setDisplay(display === "0" ? n : display + n);
  };

  const handleOp = (o: string) => {
    if (prev !== null && op && !reset) {
      const result = calc(prev, parseFloat(display), op);
      setDisplay(String(result));
      setPrev(result);
    } else {
      setPrev(parseFloat(display));
    }
    setOp(o);
    setReset(true);
  };

  const calc = (a: number, b: number, o: string) => {
    switch (o) {
      case "+": return a + b;
      case "-": return a - b;
      case "×": return a * b;
      case "÷": return b !== 0 ? a / b : 0;
      default: return b;
    }
  };

  const handleEqual = () => {
    if (prev !== null && op) {
      const result = calc(prev, parseFloat(display), op);
      setDisplay(String(parseFloat(result.toFixed(10))));
      setPrev(null);
      setOp(null);
      setReset(true);
    }
  };

  const handleClear = () => { setDisplay("0"); setPrev(null); setOp(null); };

  const buttons = [
    ["C", "±", "%", "÷"],
    ["7", "8", "9", "×"],
    ["4", "5", "6", "-"],
    ["1", "2", "3", "+"],
    ["0", ".", "="],
  ];

  return (
    <div className="w-full max-w-xs mx-auto">
      <div className="neu-pressed rounded-xl p-4 mb-3 text-right">
        <div className="text-xs h-5" style={{ color: "oklch(0.60 0.03 260)" }}>
          {prev !== null ? `${prev} ${op}` : ""}
        </div>
        <div className="text-3xl font-bold font-mono truncate" style={{ color: "oklch(0.25 0.03 260)" }}>
          {display}
        </div>
      </div>
      <div className="grid grid-cols-4 gap-2">
        {buttons.flat().map((btn) => (
          <button
            key={btn}
            onClick={() => {
              if (btn === "C") handleClear();
              else if (btn === "=") handleEqual();
              else if (["+", "-", "×", "÷"].includes(btn)) handleOp(btn);
              else if (btn === "±") setDisplay(String(-parseFloat(display)));
              else if (btn === "%") setDisplay(String(parseFloat(display) / 100));
              else handleNum(btn);
            }}
            className={`
              ${btn === "0" ? "col-span-2" : ""}
              h-12 rounded-xl text-sm font-semibold transition-all duration-150
              ${["+", "-", "×", "÷", "="].includes(btn)
                ? "text-white"
                : btn === "C" || btn === "±" || btn === "%"
                  ? "text-[oklch(0.40_0.04_260)]"
                  : "text-[oklch(0.25_0.03_260)]"
              }
              ${["+", "-", "×", "÷", "="].includes(btn)
                ? ""
                : "neu-flat hover:shadow-md active:neu-pressed"
              }
            `}
            style={
              ["+", "-", "×", "÷", "="].includes(btn)
                ? { background: "linear-gradient(135deg, #4F7BF7, #7C3AED)" }
                : undefined
            }
          >
            {btn}
          </button>
        ))}
      </div>
    </div>
  );
}

// Translator component
function TranslatorTool() {
  const [source, setSource] = useState("");
  const [translated, setTranslated] = useState("");
  const [sourceLang, setSourceLang] = useState("中文");
  const [targetLang, setTargetLang] = useState("英文");

  const handleTranslate = () => {
    if (!source.trim()) return;
    // Mock translation
    const mockTranslations: Record<string, string> = {
      "你好": "Hello",
      "谢谢": "Thank you",
      "世界": "World",
    };
    setTranslated(mockTranslations[source] || `[Translation of "${source}"]`);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3 justify-center">
        <span className="text-sm font-medium px-3 py-1 rounded-lg"
          style={{ background: "oklch(0.58 0.22 264 / 0.1)", color: "oklch(0.50 0.20 264)" }}>
          {sourceLang}
        </span>
        <button
          onClick={() => { setSourceLang(targetLang); setTargetLang(sourceLang); setSource(translated); setTranslated(source); }}
          className="w-8 h-8 rounded-lg flex items-center justify-center neu-flat hover:shadow-md transition-all"
        >
          <span className="text-xs">⇄</span>
        </button>
        <span className="text-sm font-medium px-3 py-1 rounded-lg"
          style={{ background: "oklch(0.55 0.20 300 / 0.1)", color: "oklch(0.50 0.18 300)" }}>
          {targetLang}
        </span>
      </div>
      <textarea
        value={source}
        onChange={(e) => setSource(e.target.value)}
        placeholder="输入要翻译的文本..."
        className="w-full h-24 p-3 rounded-xl text-sm neu-pressed outline-none resize-none"
        style={{ color: "oklch(0.25 0.03 260)" }}
      />
      <button
        onClick={handleTranslate}
        className="w-full py-2 rounded-xl text-sm font-semibold text-white"
        style={{ background: "linear-gradient(135deg, #4F7BF7, #7C3AED)" }}
      >
        翻译
      </button>
      {translated && (
        <div className="p-3 rounded-xl text-sm" style={{
          background: "oklch(0.58 0.22 264 / 0.05)",
          border: "1px solid oklch(0.58 0.22 264 / 0.1)",
          color: "oklch(0.30 0.03 260)"
        }}>
          {translated}
        </div>
      )}
    </div>
  );
}

// Weather component
function WeatherTool() {
  const forecast = [
    { day: "今天", icon: "☀️", high: 18, low: 6 },
    { day: "明天", icon: "⛅", high: 15, low: 4 },
    { day: "周三", icon: "🌧️", high: 12, low: 3 },
    { day: "周四", icon: "☁️", high: 14, low: 5 },
    { day: "周五", icon: "☀️", high: 19, low: 7 },
  ];

  return (
    <div>
      <div className="text-center mb-4">
        <p className="text-xs mb-1" style={{ color: "oklch(0.55 0.03 260)" }}>北京 · 晴</p>
        <div className="text-5xl mb-1">☀️</div>
        <p className="text-4xl font-bold" style={{ color: "oklch(0.25 0.03 260)" }}>18°C</p>
        <p className="text-sm" style={{ color: "oklch(0.50 0.03 260)" }}>体感温度 16° · 湿度 45%</p>
      </div>
      <div className="flex justify-between gap-2">
        {forecast.map((d, i) => (
          <div key={i} className="flex-1 text-center p-2 rounded-xl neu-flat">
            <p className="text-xs font-medium mb-1" style={{ color: "oklch(0.50 0.03 260)" }}>{d.day}</p>
            <p className="text-lg mb-1">{d.icon}</p>
            <p className="text-xs" style={{ color: "oklch(0.35 0.03 260)" }}>
              {d.high}° / {d.low}°
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

const allTools = [
  { icon: Calculator, label: "计算器", color: "#4F7BF7", category: "常用", component: "calculator" },
  { icon: Languages, label: "翻译", color: "#7C3AED", category: "常用", component: "translator" },
  { icon: CloudSun, label: "天气", color: "#F59E0B", category: "常用", component: "weather" },
  { icon: ScanLine, label: "扫描王", color: "#10B981", category: "AI工具" },
  { icon: Camera, label: "AI相机", color: "#EC4899", category: "AI工具" },
  { icon: PenLine, label: "AI写作", color: "#6366F1", category: "AI工具" },
  { icon: Sparkles, label: "AI摘要", color: "#8B5CF6", category: "AI工具" },
  { icon: QrCode, label: "二维码", color: "#06B6D4", category: "实用" },
  { icon: Timer, label: "计时器", color: "#EF4444", category: "实用" },
  { icon: Ruler, label: "尺子", color: "#14B8A6", category: "实用" },
  { icon: Hash, label: "进制转换", color: "#F97316", category: "实用" },
  { icon: Palette, label: "取色器", color: "#A855F7", category: "实用" },
  { icon: BookOpen, label: "小说", color: "#D946EF", category: "内容" },
  { icon: Newspaper, label: "资讯", color: "#0EA5E9", category: "内容" },
  { icon: Globe, label: "网页翻译", color: "#22C55E", category: "内容" },
  { icon: Zap, label: "快传", color: "#EAB308", category: "内容" },
];

export default function ToolsPage() {
  const [activeTool, setActiveTool] = useState<string | null>(null);
  const categories = Array.from(new Set(allTools.map(t => t.category)));

  return (
    <div className="flex-1 overflow-y-auto">
      {/* Header */}
      <div className="relative h-32 overflow-hidden">
        <img src={TOOLS_IMG} alt="" className="w-full h-full object-cover" />
        <div className="absolute inset-0" style={{ background: "oklch(0.965 0.006 260 / 0.7)" }} />
        <div className="absolute inset-0 flex items-center px-8">
          <div>
            <h2 className="text-xl font-bold" style={{ color: "oklch(0.25 0.03 260)" }}>工具箱</h2>
            <p className="text-sm" style={{ color: "oklch(0.50 0.03 260)" }}>
              {allTools.length} 个实用工具，提升你的效率
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-6">
        {/* Active tool panel */}
        {activeTool && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 neu-raised rounded-2xl p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-bold" style={{ color: "oklch(0.25 0.03 260)" }}>
                {allTools.find(t => t.component === activeTool)?.label}
              </h3>
              <button
                onClick={() => setActiveTool(null)}
                className="text-xs px-3 py-1 rounded-lg hover:bg-[oklch(0.94_0.01_260)] transition-colors"
                style={{ color: "oklch(0.50 0.03 260)" }}
              >
                收起
              </button>
            </div>
            {activeTool === "calculator" && <CalculatorTool />}
            {activeTool === "translator" && <TranslatorTool />}
            {activeTool === "weather" && <WeatherTool />}
          </motion.div>
        )}

        {/* Tool categories */}
        {categories.map((cat) => (
          <div key={cat} className="mb-6">
            <h3 className="text-sm font-bold mb-3 px-1" style={{ color: "oklch(0.40 0.04 260)" }}>
              {cat}
            </h3>
            <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-3">
              {allTools.filter(t => t.category === cat).map((tool, i) => {
                const Icon = tool.icon;
                return (
                  <motion.button
                    key={i}
                    whileHover={{ y: -3 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => {
                      if (tool.component) setActiveTool(tool.component);
                      else toast(`${tool.label}功能即将上线`);
                    }}
                    className="flex flex-col items-center gap-2 p-3 rounded-xl group
                      neu-flat hover:shadow-lg transition-all duration-200"
                  >
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center transition-all
                      group-hover:scale-110"
                      style={{ background: `${tool.color}12` }}
                    >
                      <Icon size={20} style={{ color: tool.color }} />
                    </div>
                    <span className="text-xs font-medium" style={{ color: "oklch(0.40 0.03 260)" }}>
                      {tool.label}
                    </span>
                  </motion.button>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
