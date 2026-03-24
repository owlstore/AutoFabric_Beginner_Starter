/*
 * Design: Quantum Blue Soft UI
 * DrivePage: Cloud drive file manager with grid/list view, upload, folder navigation
 */
import { useState, useMemo } from "react";
import { useApp, type DriveFile } from "@/contexts/AppContext";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload, FolderPlus, Grid3X3, List, Search, MoreVertical,
  Folder, FileText, Image, Video, Music, File, Trash2,
  Download, Share2, Star, SortAsc, HardDrive, Cloud
} from "lucide-react";
import { toast } from "sonner";

const DRIVE_BG = "https://private-us-east-1.manuscdn.com/sessionFile/LUR6DWgnUeDMYMT0r5ZnLE/sandbox/oYDV3iLEAEG6V50bGscZir-img-3_1770701348000_na1fn_Y2xvdWQtZHJpdmUtYmc.png?x-oss-process=image/resize,w_1920,h_1920/format,webp/quality,q_80&Expires=1798761600&Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvTFVSNkRXZ25VZURNWU1UMHI1Wm5MRS9zYW5kYm94L29ZRFYzaUxFQUVHNlY1MGJHc2NaaXItaW1nLTNfMTc3MDcwMTM0ODAwMF9uYTFmbl9ZMnh2ZFdRdFpISnBkbVV0WW1jLnBuZz94LW9zcy1wcm9jZXNzPWltYWdlL3Jlc2l6ZSx3XzE5MjAsaF8xOTIwL2Zvcm1hdCx3ZWJwL3F1YWxpdHkscV84MCIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc5ODc2MTYwMH19fV19&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=vbyzXWQDJaKviu4PMrMtWpAoKZzCZJMk4UF93qp09ET5YYFT3aT8zZkveQsIWAQoea2QnbptA5kLqS7-Ou1aW~P8~4iVDdpGLIy9Kj-3EB~uSrpUAoNM0cpAdbyGbpd5eYB9AXiEFzHsvufTy~gydqesaxR8JYeho6fZBI6nD17VbpyHubvoIcIWo8L5M~OSiuphXR-HgSfxansr81vupTy9-F-pwu4uTalHuFMoor0QtrZClYNNY2l6kYf7Kt-49B7zIqSSE491s2~CWkpeVCGw8mtdPsx3vLVLfijNbzzxxjw5~MWkqtzRKI-A-ih2HzyBc2WGyKi4v0bg2alflw__";

function formatSize(bytes: number): string {
  if (bytes === 0) return "—";
  const units = ["B", "KB", "MB", "GB"];
  let i = 0;
  let size = bytes;
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++; }
  return `${size.toFixed(1)} ${units[i]}`;
}

function formatDate(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  if (diff < 86400000) return "今天";
  if (diff < 172800000) return "昨天";
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`;
  return date.toLocaleDateString("zh-CN");
}

function getFileIcon(type: DriveFile["type"]) {
  const map = {
    folder: { icon: Folder, color: "#F59E0B" },
    file: { icon: File, color: "#6B7280" },
    image: { icon: Image, color: "#EC4899" },
    video: { icon: Video, color: "#EF4444" },
    document: { icon: FileText, color: "#4F7BF7" },
    audio: { icon: Music, color: "#8B5CF6" },
  };
  return map[type] || map.file;
}

export default function DrivePage() {
  const { driveFiles, addDriveFile, removeDriveFile } = useApp();
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());
  const [sortBy, setSortBy] = useState<"name" | "date" | "size">("date");

  const filteredFiles = useMemo(() => {
    let files = driveFiles.filter(f =>
      f.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
    files.sort((a, b) => {
      if (a.type === "folder" && b.type !== "folder") return -1;
      if (a.type !== "folder" && b.type === "folder") return 1;
      if (sortBy === "name") return a.name.localeCompare(b.name);
      if (sortBy === "size") return b.size - a.size;
      return b.modifiedAt.getTime() - a.modifiedAt.getTime();
    });
    return files;
  }, [driveFiles, searchTerm, sortBy]);

  const totalSize = driveFiles.reduce((sum, f) => sum + f.size, 0);

  const handleUpload = () => {
    addDriveFile({
      name: `新文件_${Date.now().toString(36)}.txt`,
      type: "document",
      size: Math.floor(Math.random() * 5000000),
      modifiedAt: new Date(),
      path: "/",
    });
    toast("文件上传成功");
  };

  const handleDelete = (id: string) => {
    removeDriveFile(id);
    selectedFiles.delete(id);
    setSelectedFiles(new Set(selectedFiles));
    toast("文件已删除");
  };

  return (
    <div className="flex-1 overflow-y-auto">
      {/* Header Banner */}
      <div className="relative h-40 overflow-hidden">
        <img src={DRIVE_BG} alt="" className="w-full h-full object-cover" />
        <div className="absolute inset-0" style={{
          background: "linear-gradient(135deg, oklch(0.58 0.22 264 / 0.85), oklch(0.50 0.18 280 / 0.85))"
        }} />
        <div className="absolute inset-0 flex items-center px-8">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl flex items-center justify-center"
              style={{ background: "oklch(1 0 0 / 0.2)", backdropFilter: "blur(8px)" }}>
              <Cloud size={28} className="text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">夸克网盘</h2>
              <p className="text-sm text-white/80">已用 {formatSize(totalSize)} / 6 TB</p>
            </div>
          </div>
          <div className="ml-auto flex items-center gap-3">
            <div className="w-48 h-2 rounded-full overflow-hidden" style={{ background: "oklch(1 0 0 / 0.2)" }}>
              <div className="h-full rounded-full" style={{
                width: `${Math.min((totalSize / (6 * 1024 * 1024 * 1024 * 1024)) * 100, 100)}%`,
                background: "linear-gradient(90deg, #10B981, #06B6D4)"
              }} />
            </div>
          </div>
        </div>
      </div>

      {/* Toolbar */}
      <div className="sticky top-0 z-10 px-6 py-3 border-b border-border/40 flex items-center gap-3"
        style={{ background: "oklch(0.975 0.005 260 / 0.95)", backdropFilter: "blur(12px)" }}>
        <button
          onClick={handleUpload}
          className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold text-white"
          style={{ background: "linear-gradient(135deg, #4F7BF7, #7C3AED)" }}
        >
          <Upload size={16} />
          上传
        </button>
        <button
          onClick={() => {
            addDriveFile({ name: "新建文件夹", type: "folder", size: 0, modifiedAt: new Date(), path: "/" });
            toast("文件夹已创建");
          }}
          className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium neu-flat
            hover:shadow-md transition-all"
          style={{ color: "oklch(0.40 0.04 260)" }}
        >
          <FolderPlus size={16} />
          新建文件夹
        </button>

        <div className="flex-1" />

        {/* Search */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl w-64 neu-pressed">
          <Search size={14} style={{ color: "oklch(0.55 0.04 260)" }} />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="搜索文件..."
            className="flex-1 bg-transparent outline-none text-sm"
            style={{ color: "oklch(0.25 0.03 260)" }}
          />
        </div>

        {/* Sort */}
        <button
          onClick={() => setSortBy(sortBy === "date" ? "name" : sortBy === "name" ? "size" : "date")}
          className="flex items-center gap-1 px-2 py-1.5 rounded-lg text-xs font-medium
            hover:bg-[oklch(0.94_0.01_260)] transition-colors"
          style={{ color: "oklch(0.50 0.03 260)" }}
        >
          <SortAsc size={14} />
          {sortBy === "date" ? "时间" : sortBy === "name" ? "名称" : "大小"}
        </button>

        {/* View toggle */}
        <div className="flex items-center rounded-lg p-0.5" style={{ background: "oklch(0.94 0.008 260)" }}>
          <button
            onClick={() => setViewMode("grid")}
            className={`p-1.5 rounded-md transition-all ${
              viewMode === "grid" ? "bg-white shadow-sm" : ""
            }`}
          >
            <Grid3X3 size={14} style={{ color: viewMode === "grid" ? "oklch(0.58 0.22 264)" : "oklch(0.55 0.03 260)" }} />
          </button>
          <button
            onClick={() => setViewMode("list")}
            className={`p-1.5 rounded-md transition-all ${
              viewMode === "list" ? "bg-white shadow-sm" : ""
            }`}
          >
            <List size={14} style={{ color: viewMode === "list" ? "oklch(0.58 0.22 264)" : "oklch(0.55 0.03 260)" }} />
          </button>
        </div>
      </div>

      {/* File Grid / List */}
      <div className="px-6 py-4">
        {viewMode === "grid" ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            <AnimatePresence>
              {filteredFiles.map((file, i) => {
                const { icon: Icon, color } = getFileIcon(file.type);
                return (
                  <motion.div
                    key={file.id}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    transition={{ delay: i * 0.02 }}
                    className="group neu-raised rounded-xl p-4 cursor-pointer hover:shadow-lg
                      hover:-translate-y-0.5 transition-all duration-200"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="w-10 h-10 rounded-xl flex items-center justify-center"
                        style={{ background: `${color}15` }}>
                        <Icon size={22} style={{ color }} />
                      </div>
                      <button
                        onClick={(e) => { e.stopPropagation(); handleDelete(file.id); }}
                        className="opacity-0 group-hover:opacity-100 p-1 rounded-lg
                          hover:bg-[oklch(0.94_0.01_260)] transition-all"
                      >
                        <MoreVertical size={14} className="text-[oklch(0.55_0.03_260)]" />
                      </button>
                    </div>
                    <p className="text-sm font-medium truncate mb-1"
                      style={{ color: "oklch(0.30 0.03 260)" }}>
                      {file.name}
                    </p>
                    <p className="text-xs" style={{ color: "oklch(0.55 0.03 260)" }}>
                      {file.type === "folder" ? "文件夹" : formatSize(file.size)} · {formatDate(file.modifiedAt)}
                    </p>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        ) : (
          <div className="space-y-1">
            {/* List header */}
            <div className="flex items-center gap-4 px-4 py-2 text-xs font-semibold"
              style={{ color: "oklch(0.55 0.03 260)" }}>
              <span className="flex-1">文件名</span>
              <span className="w-24 text-right">大小</span>
              <span className="w-24 text-right">修改时间</span>
              <span className="w-20" />
            </div>
            <AnimatePresence>
              {filteredFiles.map((file, i) => {
                const { icon: Icon, color } = getFileIcon(file.type);
                return (
                  <motion.div
                    key={file.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -10 }}
                    transition={{ delay: i * 0.02 }}
                    className="flex items-center gap-4 px-4 py-2.5 rounded-xl cursor-pointer group
                      hover:bg-[oklch(0.97_0.005_260)] transition-colors"
                  >
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
                        style={{ background: `${color}15` }}>
                        <Icon size={16} style={{ color }} />
                      </div>
                      <span className="text-sm font-medium truncate"
                        style={{ color: "oklch(0.30 0.03 260)" }}>
                        {file.name}
                      </span>
                    </div>
                    <span className="w-24 text-right text-xs" style={{ color: "oklch(0.55 0.03 260)" }}>
                      {file.type === "folder" ? "—" : formatSize(file.size)}
                    </span>
                    <span className="w-24 text-right text-xs" style={{ color: "oklch(0.55 0.03 260)" }}>
                      {formatDate(file.modifiedAt)}
                    </span>
                    <div className="w-20 flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button onClick={() => toast("下载功能即将上线")}
                        className="p-1 rounded hover:bg-[oklch(0.94_0.01_260)]">
                        <Download size={14} className="text-[oklch(0.55_0.03_260)]" />
                      </button>
                      <button onClick={() => toast("分享功能即将上线")}
                        className="p-1 rounded hover:bg-[oklch(0.94_0.01_260)]">
                        <Share2 size={14} className="text-[oklch(0.55_0.03_260)]" />
                      </button>
                      <button onClick={() => handleDelete(file.id)}
                        className="p-1 rounded hover:bg-[oklch(0.94_0.01_260)]">
                        <Trash2 size={14} className="text-red-400" />
                      </button>
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        )}

        {filteredFiles.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20">
            <HardDrive size={48} className="mb-4" style={{ color: "oklch(0.80 0.04 260)" }} />
            <p className="text-sm" style={{ color: "oklch(0.55 0.03 260)" }}>
              {searchTerm ? "未找到匹配的文件" : "暂无文件"}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
