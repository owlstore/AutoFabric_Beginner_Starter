/*
 * Design: Quantum Blue Soft UI
 * SearchPage: Search results with AI summary at top, web results below
 */
import { useState, useEffect, useCallback } from "react";
import { useApp } from "@/contexts/AppContext";
import { motion } from "framer-motion";
import {
  Search, ArrowLeft, Sparkles, Globe, ExternalLink, Image, Video,
  Newspaper, Clock, Filter
} from "lucide-react";

const SEARCH_IMG = "https://private-us-east-1.manuscdn.com/sessionFile/LUR6DWgnUeDMYMT0r5ZnLE/sandbox/oYDV3iLEAEG6V50bGscZir-img-5_1770701350000_na1fn_c2VhcmNoLWlsbHVzdHJhdGlvbg.png?x-oss-process=image/resize,w_1920,h_1920/format,webp/quality,q_80&Expires=1798761600&Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvTFVSNkRXZ25VZURNWU1UMHI1Wm5MRS9zYW5kYm94L29ZRFYzaUxFQUVHNlY1MGJHc2NaaXItaW1nLTVfMTc3MDcwMTM1MDAwMF9uYTFmbl9jMlZoY21Ob0xXbHNiSFZ6ZEhKaGRHbHZiZy5wbmc~eC1vc3MtcHJvY2Vzcz1pbWFnZS9yZXNpemUsd18xOTIwLGhfMTkyMC9mb3JtYXQsd2VicC9xdWFsaXR5LHFfODAiLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3OTg3NjE2MDB9fX1dfQ__&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=CmDo2XcXRyL86~kg2b0ekEeVwgE1VfhigUJBfHmf5esbczdWgSI6lRAaI9O9ZpSRIFYAC7t4V1wb6Si0Is47eat6PtPCJ-c22GbA1WqT~bMM2wcF-0ohnRMsWYF4VKqjIgK~QWwpNdKY1JnJpXndnDW57nsi42J5upjLbD5E5WsEGLq1LDF1HO2OlaWFZG5fC8HCInxUKEbKeSyZ~wY7wb5zLJ-VN1ZfyOwz2sbl-prNx74YApGcMvlCljaP8~pV3yhC1dMfvBjFYu7BGe6q3hTReowK6eTeZ-tXB3zOL1-8drGnlFoe70xGQf9V6tamHG4eKQjqiki9SPtBvlYWyQ__";

interface SearchResult {
  title: string;
  url: string;
  snippet: string;
  source: string;
  time?: string;
}

const generateMockResults = (query: string): SearchResult[] => [
  {
    title: `${query} - 最新深度解析与技术趋势`,
    url: "https://tech.example.com/article/1",
    snippet: `关于"${query}"的最新研究表明，该领域正在经历前所未有的快速发展。多项技术突破为行业带来了新的可能性，专家预测未来三年将迎来爆发式增长...`,
    source: "科技前沿",
    time: "2小时前",
  },
  {
    title: `深入理解${query}：从入门到精通完全指南`,
    url: "https://learn.example.com/guide",
    snippet: `本文将从基础概念开始，逐步深入讲解${query}的核心原理、实践应用和最佳实践。无论你是初学者还是有经验的开发者，都能从中获得有价值的见解...`,
    source: "技术学堂",
    time: "5小时前",
  },
  {
    title: `${query}在2026年的发展前景与挑战`,
    url: "https://analysis.example.com/2026",
    snippet: `行业分析师对${query}在2026年的发展做出了详细预测。报告指出，市场规模预计将达到数千亿美元，但同时也面临着技术标准化、人才短缺等挑战...`,
    source: "行业观察",
    time: "1天前",
  },
  {
    title: `${query}实战案例：企业如何成功落地`,
    url: "https://case.example.com/enterprise",
    snippet: `多家头部企业分享了${query}的实际应用案例。从方案设计到部署实施，再到效果评估，完整展现了企业级应用的全流程经验...`,
    source: "企业实践",
    time: "2天前",
  },
  {
    title: `${query}相关开源项目推荐 Top 10`,
    url: "https://github.example.com/awesome",
    snippet: `精选了GitHub上与${query}相关的10个优质开源项目，涵盖工具库、框架、示例代码等多个方面，帮助开发者快速上手...`,
    source: "开源社区",
    time: "3天前",
  },
];

const tabs = [
  { icon: Globe, label: "全部" },
  { icon: Image, label: "图片" },
  { icon: Video, label: "视频" },
  { icon: Newspaper, label: "资讯" },
];

export default function SearchPage() {
  const { searchQuery, setSearchQuery, setActivePage, addHistory } = useApp();
  const [query, setQuery] = useState(searchQuery);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [activeTab, setActiveTab] = useState(0);
  const [aiSummary, setAiSummary] = useState("");
  const [isAiLoading, setIsAiLoading] = useState(false);

  const doSearch = useCallback((q: string) => {
    if (!q.trim()) return;
    setResults(generateMockResults(q));
    // Simulate AI summary generation
    setIsAiLoading(true);
    setAiSummary("");
    const summary = `根据对"${q}"的智能分析，以下是核心要点摘要：\n\n1. 该领域目前处于快速发展阶段，技术迭代速度加快\n2. 主要应用场景包括企业级解决方案和消费级产品\n3. 市场规模预计在未来3年内实现翻倍增长\n4. 建议关注技术标准化进程和生态建设`;
    let idx = 0;
    const timer = setInterval(() => {
      idx += 2;
      setAiSummary(summary.slice(0, idx));
      if (idx >= summary.length) {
        clearInterval(timer);
        setIsAiLoading(false);
      }
    }, 30);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (searchQuery) doSearch(searchQuery);
  }, [searchQuery, doSearch]);

  const handleSearch = () => {
    if (!query.trim()) return;
    setSearchQuery(query.trim());
    addHistory({ title: query.trim(), url: `quark://search?q=${encodeURIComponent(query.trim())}` });
    doSearch(query.trim());
  };

  return (
    <div className="flex-1 overflow-y-auto">
      {/* Search Header */}
      <div className="sticky top-0 z-10 border-b border-border/40 px-4 py-3"
        style={{ background: "oklch(0.975 0.005 260 / 0.95)", backdropFilter: "blur(12px)" }}>
        <div className="max-w-3xl mx-auto flex items-center gap-3">
          <button
            onClick={() => setActivePage("home")}
            className="shrink-0 w-8 h-8 rounded-lg flex items-center justify-center
              hover:bg-[oklch(0.94_0.01_260)] transition-colors"
          >
            <ArrowLeft size={18} className="text-[oklch(0.45_0.03_260)]" />
          </button>
          <div className="flex-1 flex items-center gap-2 px-4 py-2 rounded-xl neu-pressed">
            <Search size={16} style={{ color: "oklch(0.58 0.22 264)" }} />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              className="flex-1 bg-transparent outline-none text-sm font-medium"
              style={{ color: "oklch(0.25 0.03 260)" }}
            />
          </div>
          <button
            onClick={handleSearch}
            className="shrink-0 px-4 py-2 rounded-xl text-sm font-semibold text-white"
            style={{ background: "linear-gradient(135deg, #4F7BF7, #7C3AED)" }}
          >
            搜索
          </button>
        </div>

        {/* Tabs */}
        <div className="max-w-3xl mx-auto flex items-center gap-1 mt-3">
          {tabs.map((tab, i) => {
            const Icon = tab.icon;
            return (
              <button
                key={i}
                onClick={() => setActiveTab(i)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all
                  ${activeTab === i
                    ? "bg-[oklch(0.58_0.22_264/0.1)] text-[oklch(0.50_0.20_264)]"
                    : "text-[oklch(0.50_0.03_260)] hover:bg-[oklch(0.94_0.01_260)]"
                  }`}
              >
                <Icon size={14} />
                {tab.label}
              </button>
            );
          })}
          <button className="ml-auto flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium
            text-[oklch(0.50_0.03_260)] hover:bg-[oklch(0.94_0.01_260)] transition-colors">
            <Filter size={14} />
            筛选
          </button>
        </div>
      </div>

      {/* Results */}
      <div className="max-w-3xl mx-auto px-4 py-6">
        {/* AI Summary */}
        {(aiSummary || isAiLoading) && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 rounded-2xl p-5 relative overflow-hidden"
            style={{
              background: "linear-gradient(135deg, oklch(0.58 0.22 264 / 0.06), oklch(0.55 0.20 300 / 0.06))",
              border: "1px solid oklch(0.58 0.22 264 / 0.15)",
            }}
          >
            <div className="flex items-center gap-2 mb-3">
              <div className="w-6 h-6 rounded-md flex items-center justify-center"
                style={{ background: "linear-gradient(135deg, #4F7BF7, #7C3AED)" }}>
                <Sparkles size={12} className="text-white" />
              </div>
              <span className="text-sm font-semibold" style={{ color: "oklch(0.40 0.06 264)" }}>
                AI 智能摘要
              </span>
              {isAiLoading && (
                <div className="w-2 h-2 rounded-full bg-[oklch(0.58_0.22_264)] animate-pulse" />
              )}
            </div>
            <p className="text-sm leading-relaxed whitespace-pre-line"
              style={{ color: "oklch(0.30 0.03 260)" }}>
              {aiSummary}
              {isAiLoading && <span className="inline-block w-0.5 h-4 bg-[oklch(0.58_0.22_264)] animate-pulse ml-0.5 align-middle" />}
            </p>
          </motion.div>
        )}

        {/* Search Results */}
        <div className="space-y-4">
          {results.map((result, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="group"
            >
              <a
                href={result.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block neu-raised rounded-xl p-4 hover:shadow-lg transition-all duration-200
                  group-hover:-translate-y-0.5"
              >
                <div className="flex items-center gap-2 mb-1.5">
                  <Globe size={14} className="text-[oklch(0.55_0.06_260)]" />
                  <span className="text-xs" style={{ color: "oklch(0.55 0.04 260)" }}>
                    {result.source}
                  </span>
                  {result.time && (
                    <>
                      <span className="text-xs" style={{ color: "oklch(0.70 0.02 260)" }}>·</span>
                      <span className="text-xs flex items-center gap-1" style={{ color: "oklch(0.60 0.03 260)" }}>
                        <Clock size={10} />
                        {result.time}
                      </span>
                    </>
                  )}
                  <ExternalLink size={12} className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity
                    text-[oklch(0.55_0.06_260)]" />
                </div>
                <h3 className="text-base font-semibold mb-1.5 group-hover:text-[oklch(0.50_0.20_264)] transition-colors"
                  style={{ color: "oklch(0.25 0.03 260)" }}>
                  {result.title}
                </h3>
                <p className="text-sm leading-relaxed line-clamp-2"
                  style={{ color: "oklch(0.50 0.03 260)" }}>
                  {result.snippet}
                </p>
              </a>
            </motion.div>
          ))}
        </div>

        {results.length === 0 && !isAiLoading && (
          <div className="flex flex-col items-center justify-center py-20">
            <img src={SEARCH_IMG} alt="search" className="w-48 h-auto opacity-60 mb-6" />
            <p className="text-sm" style={{ color: "oklch(0.55 0.03 260)" }}>
              输入关键词开始搜索
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
