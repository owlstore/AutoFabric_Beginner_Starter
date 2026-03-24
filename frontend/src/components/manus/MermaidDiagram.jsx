import { useEffect, useRef, useState } from "react";
import mermaid from "mermaid";

let mermaidInitialized = false;

function initMermaid() {
  if (mermaidInitialized) return;
  mermaid.initialize({
    startOnLoad: false,
    theme: "dark",
    themeVariables: {
      darkMode: true,
      background: "#0d0d12",
      primaryColor: "#1e3a5f",
      primaryTextColor: "#c9c9d0",
      primaryBorderColor: "#2a4a6f",
      lineColor: "#3b82f6",
      secondaryColor: "#1e1e28",
      tertiaryColor: "#131316",
      fontFamily: "ui-monospace, SFMono-Regular, monospace",
      fontSize: "13px",
    },
    flowchart: { htmlLabels: true, curve: "basis" },
    securityLevel: "loose",
  });
  mermaidInitialized = true;
}

let counter = 0;

export default function MermaidDiagram({ code, className = "" }) {
  const containerRef = useRef(null);
  const [error, setError] = useState(null);
  const [svg, setSvg] = useState("");

  useEffect(() => {
    if (!code?.trim()) return;
    initMermaid();

    const id = `mermaid-${++counter}`;
    let cancelled = false;

    (async () => {
      try {
        const { svg: rendered } = await mermaid.render(id, code.trim());
        if (!cancelled) {
          setSvg(rendered);
          setError(null);
        }
      } catch (e) {
        if (!cancelled) {
          setError(e.message || "Mermaid render failed");
          setSvg("");
        }
        // Clean up dangling element mermaid might have inserted
        const el = document.getElementById("d" + id);
        if (el) el.remove();
      }
    })();

    return () => { cancelled = true; };
  }, [code]);

  if (!code?.trim()) return null;

  if (error) {
    return (
      <details className={`rounded-lg border border-[#2a2a30] bg-[#0d0d12] p-3 ${className}`}>
        <summary className="text-[11px] text-[#52525b] cursor-pointer">Mermaid 渲染失败 — 查看源码</summary>
        <pre className="mt-2 text-[11px] font-mono text-[#71717a] whitespace-pre-wrap overflow-x-auto">{code}</pre>
      </details>
    );
  }

  return (
    <div
      ref={containerRef}
      className={`rounded-lg border border-[#1e1e28] bg-[#0d0d12] p-3 overflow-x-auto ${className}`}
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
}
