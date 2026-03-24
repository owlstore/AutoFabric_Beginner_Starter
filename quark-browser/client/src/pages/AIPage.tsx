/*
 * Design: Quantum Blue Soft UI
 * AIPage: Chat interface with AI assistant, typing animation, suggestion chips
 */
import { useState, useRef, useEffect } from "react";
import { useApp } from "@/contexts/AppContext";
import { motion, AnimatePresence } from "framer-motion";
import {
  Send, Sparkles, User, Lightbulb, FileText, Languages, PenLine,
  RefreshCw, Copy, ThumbsUp, ThumbsDown, Mic
} from "lucide-react";
import { toast } from "sonner";

const AI_AVATAR = "https://private-us-east-1.manuscdn.com/sessionFile/LUR6DWgnUeDMYMT0r5ZnLE/sandbox/oYDV3iLEAEG6V50bGscZir_1770701361074_na1fn_YWktYXNzaXN0YW50LWF2YXRhcg.png?x-oss-process=image/resize,w_1920,h_1920/format,webp/quality,q_80&Expires=1798761600&Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvTFVSNkRXZ25VZURNWU1UMHI1Wm5MRS9zYW5kYm94L29ZRFYzaUxFQUVHNlY1MGJHc2NaaXItaW1nLTFfMTc3MDcwMTM1NzAwMF9uYTFmbl9hR1Z5YnkxaVp3LnBuZz94LW9zcy1wcm9jZXNzPWltYWdlL3Jlc2l6ZSx3XzE5MjAsaF8xOTIwL2Zvcm1hdCx3ZWJwL3F1YWxpdHkscV84MCIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc5ODc2MTYwMH19fV19&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=XUaekLDD6uIMwxjOV-Hvm1xlOjJiqD5uJxr-r526cC2LNFq7R9Z2ETvbCjGmZjlKvdwqyJ015xt5qZ47xeLh6JVumBWv2OtyzKh7IOrK6KyS7~C8kBRlfpdbots8GnLV5MJ9qSk2Lf~oCBPa-xg1Yvj~aYMdFJmYx3zhEttWlkZl~AwU0BW7OmcjhEw6btDFG3rTgTE0sCbNFfLIpdiFG~RJAgPMPc6PFIFWvO4L6mKwV2DX8BlTt1uZDIQW6IE3lPgrJy6ydV7aoPLcu2XsnM1LuX8d~137QeowRt95R1yWlVwBmlwU0Zw3p2ULcI2PfQoRZ2Kz9W5OTKfwKXxvAA__";

const suggestions = [
  { icon: Lightbulb, text: "帮我分析一下最新的AI技术趋势", color: "#F59E0B" },
  { icon: PenLine, text: "写一篇关于量子计算的科普文章", color: "#4F7BF7" },
  { icon: Languages, text: "将这段中文翻译成英文", color: "#7C3AED" },
  { icon: FileText, text: "帮我总结这篇文档的要点", color: "#10B981" },
];

const aiResponses: Record<string, string> = {
  default: `你好！我是 Quark AI 助手，很高兴为你服务。我可以帮助你：

**搜索与分析** — 智能搜索信息并生成深度分析报告
**写作与创作** — 文章撰写、文案创作、诗歌生成
**翻译与语言** — 多语言翻译、语法纠正、润色优化
**文档处理** — 文档摘要、要点提取、格式转换
**编程辅助** — 代码生成、Bug修复、技术方案设计

请告诉我你需要什么帮助？`,
};

function getAIResponse(input: string): string {
  const lower = input.toLowerCase();
  if (lower.includes("翻译")) {
    return `好的，我来帮你翻译。请提供需要翻译的内容。

我支持以下语言之间的互译：
- 中文 ↔ 英文
- 中文 ↔ 日文
- 中文 ↔ 韩文
- 以及更多语言...

只需将文本发送给我，我会自动检测语言并翻译。`;
  }
  if (lower.includes("ai") || lower.includes("人工智能") || lower.includes("技术趋势")) {
    return `## 2026年AI技术趋势分析

根据最新的行业研究报告，以下是2026年AI领域的关键趋势：

### 1. 多模态大模型
大语言模型正在向多模态方向演进，能够同时处理文本、图像、音频和视频。GPT-5、Gemini 2.0等模型展现了强大的跨模态理解能力。

### 2. AI Agent 生态
自主AI代理（AI Agent）成为热点，能够独立完成复杂任务链。从简单的对话助手进化为能够规划、执行、反思的智能体。

### 3. 端侧AI
AI模型的小型化使得在手机、PC等终端设备上运行成为可能，隐私保护和响应速度大幅提升。

### 4. AI + 科学研究
AI在药物发现、材料科学、气候模拟等领域取得突破性进展，加速科学发现的速度。

### 5. 监管与治理
各国加速AI立法，建立安全评估标准和伦理框架，推动负责任的AI发展。

需要我对某个方向做更深入的分析吗？`;
  }
  if (lower.includes("写") || lower.includes("文章") || lower.includes("量子")) {
    return `## 量子计算：开启计算新纪元

量子计算是利用量子力学原理进行信息处理的新型计算范式。与经典计算机使用比特（0或1）不同，量子计算机使用**量子比特（qubit）**，它可以同时处于0和1的叠加态。

### 核心概念

**量子叠加** — 一个量子比特可以同时表示0和1，这意味着n个量子比特可以同时表示2^n个状态。

**量子纠缠** — 两个纠缠的量子比特之间存在神秘的关联，对其中一个的测量会瞬间影响另一个。

**量子干涉** — 通过巧妙设计量子电路，可以让正确答案的概率增大，错误答案的概率减小。

### 应用前景

量子计算在密码学、药物设计、金融建模、人工智能等领域具有巨大潜力。

需要我继续展开某个部分吗？`;
  }
  return `感谢你的提问！关于"${input}"，我来为你详细解答：

这是一个很好的问题。让我从几个角度来分析：

**核心观点：** ${input}涉及到多个层面的考量，需要综合评估。

**详细分析：**
1. 从技术角度来看，这个领域正在快速发展
2. 从应用角度来看，已有多个成功的实践案例
3. 从趋势角度来看，未来前景广阔

如果你需要更具体的信息，请告诉我你最关心的方面，我会进一步深入分析。`;
}

export default function AIPage() {
  const { chatMessages, addChatMessage, clearChat } = useApp();
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);

  const handleSend = (text?: string) => {
    const msg = text || input.trim();
    if (!msg || isTyping) return;

    addChatMessage({ role: "user", content: msg });
    setInput("");
    setIsTyping(true);

    // Simulate AI response with typing delay
    const response = getAIResponse(msg);

    // Add the full response after a realistic delay
    setTimeout(() => {
      addChatMessage({ role: "assistant", content: response });
      setIsTyping(false);
    }, 1200 + Math.random() * 800);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-border/40"
        style={{ background: "oklch(0.975 0.005 260 / 0.95)" }}>
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl overflow-hidden ai-glow-pulse">
            <img src={AI_AVATAR} alt="AI" className="w-full h-full object-cover" />
          </div>
          <div>
            <h2 className="text-sm font-bold" style={{ color: "oklch(0.25 0.03 260)" }}>
              Quark AI 助手
            </h2>
            <p className="text-xs" style={{ color: "oklch(0.55 0.04 264)" }}>
              基于大语言模型 · 深度思考
            </p>
          </div>
        </div>
        <button
          onClick={() => { clearChat(); toast("对话已清空"); }}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
            hover:bg-[oklch(0.94_0.01_260)] transition-colors"
          style={{ color: "oklch(0.50 0.03 260)" }}
        >
          <RefreshCw size={14} />
          新对话
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-3xl mx-auto space-y-6">
          {chatMessages.length === 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center py-12"
            >
              <div className="w-16 h-16 rounded-2xl mx-auto mb-4 overflow-hidden ai-glow">
                <img src={AI_AVATAR} alt="AI" className="w-full h-full object-cover" />
              </div>
              <h3 className="text-xl font-bold mb-2" style={{ color: "oklch(0.25 0.03 260)" }}>
                你好，我是 Quark AI
              </h3>
              <p className="text-sm mb-8" style={{ color: "oklch(0.50 0.03 260)" }}>
                我可以帮你搜索、写作、翻译、分析，有什么可以帮你的？
              </p>

              {/* Suggestion chips */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg mx-auto">
                {suggestions.map((s, i) => {
                  const Icon = s.icon;
                  return (
                    <motion.button
                      key={i}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 + i * 0.05 }}
                      whileHover={{ y: -2 }}
                      onClick={() => handleSend(s.text)}
                      className="flex items-center gap-3 p-3 rounded-xl text-left neu-flat
                        hover:shadow-md transition-all duration-200"
                    >
                      <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
                        style={{ background: `${s.color}15` }}>
                        <Icon size={16} style={{ color: s.color }} />
                      </div>
                      <span className="text-xs font-medium leading-tight"
                        style={{ color: "oklch(0.35 0.03 260)" }}>
                        {s.text}
                      </span>
                    </motion.button>
                  );
                })}
              </div>
            </motion.div>
          )}

          {/* Chat messages */}
          <AnimatePresence>
            {chatMessages.map((msg, i) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}
              >
                {/* Avatar */}
                <div className={`shrink-0 w-8 h-8 rounded-xl overflow-hidden ${
                  msg.role === "assistant" ? "ai-glow" : ""
                }`}>
                  {msg.role === "assistant" ? (
                    <img src={AI_AVATAR} alt="AI" className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center"
                      style={{ background: "oklch(0.94 0.01 260)" }}>
                      <User size={16} style={{ color: "oklch(0.50 0.03 260)" }} />
                    </div>
                  )}
                </div>

                {/* Message bubble */}
                <div className={`max-w-[80%] ${msg.role === "user" ? "text-right" : ""}`}>
                  <div className={`inline-block rounded-2xl px-4 py-3 text-sm leading-relaxed
                    ${msg.role === "user"
                      ? "text-white"
                      : "neu-raised"
                    }`}
                    style={msg.role === "user"
                      ? { background: "linear-gradient(135deg, #4F7BF7, #6366F1)" }
                      : { color: "oklch(0.30 0.03 260)" }
                    }
                  >
                    <div className="whitespace-pre-wrap">{msg.content || (
                      <span className="flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
                        <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" style={{ animationDelay: "0.2s" }} />
                        <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" style={{ animationDelay: "0.4s" }} />
                      </span>
                    )}</div>
                  </div>

                  {/* Action buttons for AI messages */}
                  {msg.role === "assistant" && msg.content && (
                    <div className="flex items-center gap-1 mt-1.5 ml-1">
                      <button onClick={() => { navigator.clipboard.writeText(msg.content); toast("已复制到剪贴板"); }}
                        className="p-1 rounded hover:bg-[oklch(0.94_0.01_260)] transition-colors">
                        <Copy size={12} className="text-[oklch(0.60_0.03_260)]" />
                      </button>
                      <button onClick={() => toast("感谢反馈")}
                        className="p-1 rounded hover:bg-[oklch(0.94_0.01_260)] transition-colors">
                        <ThumbsUp size={12} className="text-[oklch(0.60_0.03_260)]" />
                      </button>
                      <button onClick={() => toast("感谢反馈")}
                        className="p-1 rounded hover:bg-[oklch(0.94_0.01_260)] transition-colors">
                        <ThumbsDown size={12} className="text-[oklch(0.60_0.03_260)]" />
                      </button>
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {isTyping && chatMessages.length > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center gap-2 ml-11"
            >
              <div className="flex gap-1">
                <span className="w-2 h-2 rounded-full animate-bounce" style={{ background: "oklch(0.58 0.22 264)", animationDelay: "0ms" }} />
                <span className="w-2 h-2 rounded-full animate-bounce" style={{ background: "oklch(0.58 0.22 264)", animationDelay: "150ms" }} />
                <span className="w-2 h-2 rounded-full animate-bounce" style={{ background: "oklch(0.58 0.22 264)", animationDelay: "300ms" }} />
              </div>
              <span className="text-xs" style={{ color: "oklch(0.55 0.04 264)" }}>AI 正在思考...</span>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-border/40 px-4 py-3"
        style={{ background: "oklch(0.975 0.005 260 / 0.95)" }}>
        <div className="max-w-3xl mx-auto">
          <div className="flex items-end gap-2 p-2 rounded-2xl neu-pressed">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="输入你的问题..."
              rows={1}
              className="flex-1 bg-transparent outline-none text-sm font-medium resize-none
                min-h-[36px] max-h-[120px] py-2 px-2"
              style={{ color: "oklch(0.25 0.03 260)" }}
            />
            <button
              onClick={() => toast("语音输入功能即将上线")}
              className="shrink-0 w-9 h-9 rounded-xl flex items-center justify-center
                hover:bg-[oklch(0.92_0.01_260)] transition-colors"
            >
              <Mic size={18} className="text-[oklch(0.50_0.03_260)]" />
            </button>
            <button
              onClick={() => handleSend()}
              disabled={!input.trim() || isTyping}
              className="shrink-0 w-9 h-9 rounded-xl flex items-center justify-center
                text-white transition-all disabled:opacity-40"
              style={{ background: "linear-gradient(135deg, #4F7BF7, #7C3AED)" }}
            >
              <Send size={16} />
            </button>
          </div>
          <p className="text-center text-xs mt-2" style={{ color: "oklch(0.65 0.02 260)" }}>
            Quark AI 可能会产生不准确的信息，请注意甄别
          </p>
        </div>
      </div>
    </div>
  );
}
