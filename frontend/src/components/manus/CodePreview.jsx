import { useState, useMemo } from "react";
import hljs from "highlight.js/lib/core";
import "highlight.js/styles/github-dark-dimmed.css";

const EXT_LANG = {
  js: "javascript", jsx: "javascript", ts: "typescript", tsx: "typescript",
  py: "python", json: "json", css: "css", html: "html", xml: "xml",
  yml: "yaml", yaml: "yaml", sql: "sql", sh: "bash", bash: "bash",
  dockerfile: "dockerfile", md: "markdown",
};

function getLanguage(path) {
  const ext = path.split(".").pop()?.toLowerCase() || "";
  return EXT_LANG[ext] || "";
}

function buildTree(files) {
  const tree = {};
  for (const f of files) {
    const parts = f.path.split("/");
    let node = tree;
    for (let i = 0; i < parts.length - 1; i++) {
      const dir = parts[i];
      if (!node[dir]) node[dir] = {};
      node = node[dir];
    }
    node[parts[parts.length - 1]] = f;
  }
  return tree;
}

function TreeNode({ name, node, depth = 0, activePath, onSelect }) {
  const isFile = node.path !== undefined;
  const [open, setOpen] = useState(depth < 2);

  if (isFile) {
    const isActive = node.path === activePath;
    return (
      <button
        onClick={() => onSelect(node.path)}
        className={`w-full text-left pl-${Math.min(depth * 3, 12)} pr-2 py-0.5 text-[12px] font-mono truncate hover:bg-[#1e1e28] transition-colors ${
          isActive ? "bg-[#1e1e28] text-blue-400" : "text-[#a1a1aa]"
        }`}
        style={{ paddingLeft: `${depth * 12 + 8}px` }}
      >
        <span className="text-[#52525b] mr-1.5">~</span>
        {name}
      </button>
    );
  }

  const entries = Object.entries(node).sort(([, a], [, b]) => {
    const aIsFile = a.path !== undefined;
    const bIsFile = b.path !== undefined;
    if (aIsFile === bIsFile) return 0;
    return aIsFile ? 1 : -1;
  });

  return (
    <div>
      <button
        onClick={() => setOpen(!open)}
        className="w-full text-left pr-2 py-0.5 text-[12px] font-mono text-[#71717a] hover:bg-[#1e1e28] hover:text-[#a1a1aa] transition-colors truncate"
        style={{ paddingLeft: `${depth * 12 + 8}px` }}
      >
        <span className="inline-block w-3 text-center text-[10px]">{open ? "v" : ">"}</span>
        {" "}{name}
      </button>
      {open && entries.map(([k, v]) => (
        <TreeNode key={k} name={k} node={v} depth={depth + 1} activePath={activePath} onSelect={onSelect} />
      ))}
    </div>
  );
}

export default function CodePreview({ files, className = "" }) {
  const [activePath, setActivePath] = useState(files[0]?.path || "");
  const tree = useMemo(() => buildTree(files), [files]);

  const activeFile = files.find((f) => f.path === activePath);
  const lang = activePath ? getLanguage(activePath) : "";
  const code = activeFile?.content || "";

  let highlighted;
  try {
    highlighted = lang && hljs.getLanguage(lang)
      ? hljs.highlight(code, { language: lang }).value
      : code.replace(/</g, "&lt;").replace(/>/g, "&gt;");
  } catch {
    highlighted = code.replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  const lines = highlighted.split("\n");

  return (
    <div className={`flex rounded-xl overflow-hidden border border-[#1e1e28] bg-[#0d0d12] ${className}`} style={{ height: "360px" }}>
      {/* File tree */}
      <div className="w-[180px] shrink-0 border-r border-[#1e1e28] overflow-y-auto py-1 bg-[#111114]">
        <div className="px-2 py-1 text-[10px] text-[#52525b] uppercase tracking-wider font-semibold">Files</div>
        {Object.entries(tree).map(([k, v]) => (
          <TreeNode key={k} name={k} node={v} activePath={activePath} onSelect={setActivePath} />
        ))}
      </div>

      {/* Code area */}
      <div className="flex-1 overflow-auto">
        {/* File header */}
        <div className="sticky top-0 flex items-center justify-between px-3 py-1.5 bg-[#131316] border-b border-[#1e1e28] z-10">
          <span className="text-[11px] font-mono text-[#71717a] truncate">{activePath}</span>
          <button
            onClick={() => navigator.clipboard.writeText(code)}
            className="text-[10px] text-[#52525b] hover:text-[#a1a1aa] transition-colors shrink-0 ml-2"
          >
            Copy
          </button>
        </div>
        {/* Code lines */}
        <pre className="p-0 text-[12px] leading-[1.6]">
          <table className="w-full border-collapse">
            <tbody>
              {lines.map((line, i) => (
                <tr key={i} className="hover:bg-[#1a1a1e]">
                  <td className="text-right pr-3 pl-2 text-[#3a3a42] select-none w-[1%] whitespace-nowrap font-mono text-[11px]">
                    {i + 1}
                  </td>
                  <td className="pl-2 pr-4 font-mono">
                    <code dangerouslySetInnerHTML={{ __html: line || " " }} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </pre>
      </div>
    </div>
  );
}
