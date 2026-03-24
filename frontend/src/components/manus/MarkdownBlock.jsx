import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import hljs from "highlight.js/lib/core";
import javascript from "highlight.js/lib/languages/javascript";
import python from "highlight.js/lib/languages/python";
import json from "highlight.js/lib/languages/json";
import bash from "highlight.js/lib/languages/bash";
import css from "highlight.js/lib/languages/css";
import xml from "highlight.js/lib/languages/xml";
import yaml from "highlight.js/lib/languages/yaml";
import sql from "highlight.js/lib/languages/sql";
import dockerfile from "highlight.js/lib/languages/dockerfile";
import typescript from "highlight.js/lib/languages/typescript";
import "highlight.js/styles/github-dark-dimmed.css";

hljs.registerLanguage("javascript", javascript);
hljs.registerLanguage("js", javascript);
hljs.registerLanguage("jsx", javascript);
hljs.registerLanguage("python", python);
hljs.registerLanguage("py", python);
hljs.registerLanguage("json", json);
hljs.registerLanguage("bash", bash);
hljs.registerLanguage("sh", bash);
hljs.registerLanguage("css", css);
hljs.registerLanguage("html", xml);
hljs.registerLanguage("xml", xml);
hljs.registerLanguage("yaml", yaml);
hljs.registerLanguage("yml", yaml);
hljs.registerLanguage("sql", sql);
hljs.registerLanguage("dockerfile", dockerfile);
hljs.registerLanguage("typescript", typescript);
hljs.registerLanguage("ts", typescript);
hljs.registerLanguage("tsx", typescript);

function CodeBlock({ className, children }) {
  const lang = className?.replace("language-", "") || "";
  const code = String(children).replace(/\n$/, "");
  let highlighted;
  try {
    highlighted = lang && hljs.getLanguage(lang)
      ? hljs.highlight(code, { language: lang }).value
      : hljs.highlightAuto(code).value;
  } catch {
    highlighted = code;
  }

  return (
    <div className="relative group my-2">
      {lang && (
        <span className="absolute top-1.5 right-10 text-[10px] text-[#52525b] font-mono">{lang}</span>
      )}
      <button
        onClick={() => navigator.clipboard.writeText(code)}
        className="absolute top-1.5 right-2 text-[10px] text-[#52525b] hover:text-[#a1a1aa] opacity-0 group-hover:opacity-100 transition-opacity"
      >
        Copy
      </button>
      <pre className="p-3 rounded-lg bg-[#0d0d12] border border-[#1e1e28] overflow-x-auto text-[12px] leading-relaxed">
        <code dangerouslySetInnerHTML={{ __html: highlighted }} />
      </pre>
    </div>
  );
}

export default function MarkdownBlock({ content, className = "" }) {
  if (!content) return null;

  return (
    <div className={`markdown-body text-[13px] text-[#c9c9d0] leading-relaxed ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ className: cn, children, ...props }) {
            const isInline = !cn;
            if (isInline) {
              return (
                <code className="px-1 py-0.5 rounded bg-[#1e1e28] text-[12px] text-blue-300 font-mono" {...props}>
                  {children}
                </code>
              );
            }
            return <CodeBlock className={cn}>{children}</CodeBlock>;
          },
          h1: ({ children }) => <h1 className="text-lg font-bold text-white mt-4 mb-2">{children}</h1>,
          h2: ({ children }) => <h2 className="text-base font-semibold text-white mt-3 mb-1.5">{children}</h2>,
          h3: ({ children }) => <h3 className="text-sm font-semibold text-[#e4e4e7] mt-2 mb-1">{children}</h3>,
          p: ({ children }) => <p className="mb-2">{children}</p>,
          ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-0.5">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-0.5">{children}</ol>,
          li: ({ children }) => <li className="text-[13px]">{children}</li>,
          a: ({ href, children }) => (
            <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">
              {children}
            </a>
          ),
          table: ({ children }) => (
            <div className="overflow-x-auto my-2">
              <table className="w-full text-[12px] border-collapse">{children}</table>
            </div>
          ),
          th: ({ children }) => (
            <th className="text-left px-2 py-1.5 border-b border-[#2a2a30] text-[#a1a1aa] font-medium bg-[#0d0d12]">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="px-2 py-1 border-b border-[#1e1e28] text-[#c9c9d0]">{children}</td>
          ),
          blockquote: ({ children }) => (
            <blockquote className="border-l-2 border-blue-500/40 pl-3 my-2 text-[#71717a] italic">
              {children}
            </blockquote>
          ),
          hr: () => <hr className="border-[#1e1e28] my-3" />,
        }}
      />
    </div>
  );
}
