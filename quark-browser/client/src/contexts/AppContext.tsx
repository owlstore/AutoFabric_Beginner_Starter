import React, { createContext, useContext, useState, useCallback } from "react";

// Types
export interface Tab {
  id: string;
  title: string;
  url: string;
  favicon?: string;
  isActive: boolean;
}

export interface Bookmark {
  id: string;
  title: string;
  url: string;
  favicon?: string;
  folder?: string;
  createdAt: Date;
}

export interface HistoryItem {
  id: string;
  title: string;
  url: string;
  favicon?: string;
  visitedAt: Date;
}

export interface DriveFile {
  id: string;
  name: string;
  type: "file" | "folder" | "image" | "video" | "document" | "audio";
  size: number;
  modifiedAt: Date;
  path: string;
  parentId?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export type ActivePage = "home" | "search" | "ai" | "drive" | "tools" | "bookmarks" | "history" | "settings";

interface AppState {
  activePage: ActivePage;
  setActivePage: (page: ActivePage) => void;
  tabs: Tab[];
  addTab: (tab: Omit<Tab, "id" | "isActive">) => void;
  removeTab: (id: string) => void;
  setActiveTab: (id: string) => void;
  bookmarks: Bookmark[];
  addBookmark: (bookmark: Omit<Bookmark, "id" | "createdAt">) => void;
  removeBookmark: (id: string) => void;
  history: HistoryItem[];
  addHistory: (item: Omit<HistoryItem, "id" | "visitedAt">) => void;
  clearHistory: () => void;
  driveFiles: DriveFile[];
  addDriveFile: (file: Omit<DriveFile, "id">) => void;
  removeDriveFile: (id: string) => void;
  chatMessages: ChatMessage[];
  addChatMessage: (msg: Omit<ChatMessage, "id" | "timestamp">) => void;
  clearChat: () => void;
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (collapsed: boolean) => void;
}

const AppContext = createContext<AppState | null>(null);

let idCounter = 0;
const genId = () => `id_${++idCounter}_${Date.now()}`;

// Default data
const defaultBookmarks: Bookmark[] = [
  { id: "b1", title: "百度", url: "https://www.baidu.com", favicon: "🔍", createdAt: new Date() },
  { id: "b2", title: "知乎", url: "https://www.zhihu.com", favicon: "💬", createdAt: new Date() },
  { id: "b3", title: "GitHub", url: "https://github.com", favicon: "🐙", createdAt: new Date() },
  { id: "b4", title: "哔哩哔哩", url: "https://www.bilibili.com", favicon: "📺", createdAt: new Date() },
  { id: "b5", title: "微博", url: "https://weibo.com", favicon: "📰", createdAt: new Date() },
  { id: "b6", title: "淘宝", url: "https://www.taobao.com", favicon: "🛒", createdAt: new Date() },
];

const defaultHistory: HistoryItem[] = [
  { id: "h1", title: "如何使用React 19新特性", url: "https://react.dev", favicon: "⚛️", visitedAt: new Date(Date.now() - 3600000) },
  { id: "h2", title: "Tailwind CSS 4.0 发布说明", url: "https://tailwindcss.com", favicon: "🎨", visitedAt: new Date(Date.now() - 7200000) },
  { id: "h3", title: "TypeScript 5.6 新功能", url: "https://typescriptlang.org", favicon: "📘", visitedAt: new Date(Date.now() - 10800000) },
  { id: "h4", title: "2026年AI技术趋势分析", url: "https://ai-trends.com", favicon: "🤖", visitedAt: new Date(Date.now() - 86400000) },
  { id: "h5", title: "Node.js 22 性能优化指南", url: "https://nodejs.org", favicon: "💚", visitedAt: new Date(Date.now() - 172800000) },
];

const defaultDriveFiles: DriveFile[] = [
  { id: "f1", name: "工作文档", type: "folder", size: 0, modifiedAt: new Date(), path: "/" },
  { id: "f2", name: "照片", type: "folder", size: 0, modifiedAt: new Date(), path: "/" },
  { id: "f3", name: "项目计划书.docx", type: "document", size: 2456000, modifiedAt: new Date(Date.now() - 86400000), path: "/" },
  { id: "f4", name: "会议记录.pdf", type: "document", size: 1234000, modifiedAt: new Date(Date.now() - 172800000), path: "/" },
  { id: "f5", name: "产品设计稿.png", type: "image", size: 5678000, modifiedAt: new Date(Date.now() - 259200000), path: "/" },
  { id: "f6", name: "演示视频.mp4", type: "video", size: 156780000, modifiedAt: new Date(Date.now() - 345600000), path: "/" },
  { id: "f7", name: "数据分析.xlsx", type: "document", size: 890000, modifiedAt: new Date(Date.now() - 432000000), path: "/" },
  { id: "f8", name: "背景音乐.mp3", type: "audio", size: 4560000, modifiedAt: new Date(Date.now() - 518400000), path: "/" },
];

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [activePage, setActivePage] = useState<ActivePage>("home");
  const [tabs, setTabs] = useState<Tab[]>([
    { id: "tab1", title: "新标签页", url: "quark://newtab", isActive: true },
  ]);
  const [bookmarks, setBookmarks] = useState<Bookmark[]>(defaultBookmarks);
  const [history, setHistory] = useState<HistoryItem[]>(defaultHistory);
  const [driveFiles, setDriveFiles] = useState<DriveFile[]>(defaultDriveFiles);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const addTab = useCallback((tab: Omit<Tab, "id" | "isActive">) => {
    const id = genId();
    setTabs(prev => [
      ...prev.map(t => ({ ...t, isActive: false })),
      { ...tab, id, isActive: true },
    ]);
  }, []);

  const removeTab = useCallback((id: string) => {
    setTabs(prev => {
      const filtered = prev.filter(t => t.id !== id);
      if (filtered.length === 0) {
        return [{ id: genId(), title: "新标签页", url: "quark://newtab", isActive: true }];
      }
      if (!filtered.some(t => t.isActive)) {
        filtered[filtered.length - 1].isActive = true;
      }
      return filtered;
    });
  }, []);

  const setActiveTab = useCallback((id: string) => {
    setTabs(prev => prev.map(t => ({ ...t, isActive: t.id === id })));
  }, []);

  const addBookmark = useCallback((bookmark: Omit<Bookmark, "id" | "createdAt">) => {
    setBookmarks(prev => [...prev, { ...bookmark, id: genId(), createdAt: new Date() }]);
  }, []);

  const removeBookmark = useCallback((id: string) => {
    setBookmarks(prev => prev.filter(b => b.id !== id));
  }, []);

  const addHistory = useCallback((item: Omit<HistoryItem, "id" | "visitedAt">) => {
    setHistory(prev => [{ ...item, id: genId(), visitedAt: new Date() }, ...prev]);
  }, []);

  const clearHistory = useCallback(() => setHistory([]), []);

  const addDriveFile = useCallback((file: Omit<DriveFile, "id">) => {
    setDriveFiles(prev => [...prev, { ...file, id: genId() }]);
  }, []);

  const removeDriveFile = useCallback((id: string) => {
    setDriveFiles(prev => prev.filter(f => f.id !== id));
  }, []);

  const addChatMessage = useCallback((msg: Omit<ChatMessage, "id" | "timestamp">) => {
    setChatMessages(prev => [...prev, { ...msg, id: genId(), timestamp: new Date() }]);
  }, []);

  const clearChat = useCallback(() => setChatMessages([]), []);

  return (
    <AppContext.Provider
      value={{
        activePage, setActivePage,
        tabs, addTab, removeTab, setActiveTab,
        bookmarks, addBookmark, removeBookmark,
        history, addHistory, clearHistory,
        driveFiles, addDriveFile, removeDriveFile,
        chatMessages, addChatMessage, clearChat,
        searchQuery, setSearchQuery,
        sidebarCollapsed, setSidebarCollapsed,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp must be used within AppProvider");
  return ctx;
}
