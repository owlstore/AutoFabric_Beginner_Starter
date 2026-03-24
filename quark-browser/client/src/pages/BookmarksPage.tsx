/*
 * Design: Quantum Blue Soft UI
 * BookmarksPage: Bookmark manager with grid cards
 */
import { useApp } from "@/contexts/AppContext";
import { motion, AnimatePresence } from "framer-motion";
import { Bookmark, Plus, Trash2, ExternalLink, Search, Star } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

export default function BookmarksPage() {
  const { bookmarks, addBookmark, removeBookmark } = useApp();
  const [searchTerm, setSearchTerm] = useState("");
  const [showAdd, setShowAdd] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newUrl, setNewUrl] = useState("");

  const filtered = bookmarks.filter(b =>
    b.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    b.url.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleAdd = () => {
    if (!newTitle.trim() || !newUrl.trim()) return;
    addBookmark({ title: newTitle, url: newUrl, favicon: "⭐" });
    setNewTitle("");
    setNewUrl("");
    setShowAdd(false);
    toast("书签已添加");
  };

  return (
    <div className="flex-1 overflow-y-auto px-6 py-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ background: "oklch(0.58 0.22 264 / 0.1)" }}>
              <Bookmark size={20} style={{ color: "oklch(0.58 0.22 264)" }} />
            </div>
            <div>
              <h2 className="text-lg font-bold" style={{ color: "oklch(0.25 0.03 260)" }}>书签管理</h2>
              <p className="text-xs" style={{ color: "oklch(0.55 0.03 260)" }}>
                共 {bookmarks.length} 个书签
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl w-56 neu-pressed">
              <Search size={14} style={{ color: "oklch(0.55 0.04 260)" }} />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="搜索书签..."
                className="flex-1 bg-transparent outline-none text-sm"
                style={{ color: "oklch(0.25 0.03 260)" }}
              />
            </div>
            <button
              onClick={() => setShowAdd(!showAdd)}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold text-white"
              style={{ background: "linear-gradient(135deg, #4F7BF7, #7C3AED)" }}
            >
              <Plus size={16} />
              添加
            </button>
          </div>
        </div>

        {/* Add form */}
        <AnimatePresence>
          {showAdd && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-6 overflow-hidden"
            >
              <div className="neu-raised rounded-2xl p-5">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
                  <input
                    type="text"
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    placeholder="书签名称"
                    className="px-4 py-2 rounded-xl text-sm neu-pressed outline-none"
                    style={{ color: "oklch(0.25 0.03 260)" }}
                  />
                  <input
                    type="text"
                    value={newUrl}
                    onChange={(e) => setNewUrl(e.target.value)}
                    placeholder="网址 (https://...)"
                    className="px-4 py-2 rounded-xl text-sm neu-pressed outline-none"
                    style={{ color: "oklch(0.25 0.03 260)" }}
                  />
                </div>
                <div className="flex justify-end gap-2">
                  <button onClick={() => setShowAdd(false)}
                    className="px-4 py-1.5 rounded-lg text-sm font-medium
                      hover:bg-[oklch(0.94_0.01_260)] transition-colors"
                    style={{ color: "oklch(0.50 0.03 260)" }}>
                    取消
                  </button>
                  <button onClick={handleAdd}
                    className="px-4 py-1.5 rounded-lg text-sm font-semibold text-white"
                    style={{ background: "linear-gradient(135deg, #4F7BF7, #7C3AED)" }}>
                    保存
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Bookmarks grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <AnimatePresence>
            {filtered.map((bm, i) => (
              <motion.div
                key={bm.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ delay: i * 0.03 }}
                className="group neu-raised rounded-xl p-4 hover:shadow-lg hover:-translate-y-0.5
                  transition-all duration-200 cursor-pointer"
              >
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center text-lg shrink-0"
                    style={{ background: "oklch(0.94 0.01 260)" }}>
                    {bm.favicon || "🌐"}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-semibold truncate mb-0.5"
                      style={{ color: "oklch(0.25 0.03 260)" }}>
                      {bm.title}
                    </h3>
                    <p className="text-xs truncate" style={{ color: "oklch(0.55 0.04 260)" }}>
                      {bm.url}
                    </p>
                  </div>
                </div>
                <div className="flex items-center justify-end gap-1 mt-3 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button onClick={() => window.open(bm.url, "_blank")}
                    className="p-1.5 rounded-lg hover:bg-[oklch(0.94_0.01_260)] transition-colors">
                    <ExternalLink size={14} className="text-[oklch(0.55_0.04_260)]" />
                  </button>
                  <button onClick={() => { removeBookmark(bm.id); toast("书签已删除"); }}
                    className="p-1.5 rounded-lg hover:bg-[oklch(0.94_0.01_260)] transition-colors">
                    <Trash2 size={14} className="text-red-400" />
                  </button>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {filtered.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20">
            <Star size={48} className="mb-4" style={{ color: "oklch(0.80 0.04 260)" }} />
            <p className="text-sm" style={{ color: "oklch(0.55 0.03 260)" }}>
              {searchTerm ? "未找到匹配的书签" : "暂无书签，点击上方添加"}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
