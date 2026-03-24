import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import { AppProvider, useApp } from "./contexts/AppContext";
import Sidebar from "./components/Sidebar";
import TabBar from "./components/TabBar";
import MobileNav from "./components/MobileNav";
import { useIsMobile } from "./hooks/useMediaQuery";
import { motion, AnimatePresence } from "framer-motion";
import { useEffect } from "react";
import HomePage from "./pages/Home";
import SearchPage from "./pages/SearchPage";
import AIPage from "./pages/AIPage";
import DrivePage from "./pages/DrivePage";
import ToolsPage from "./pages/ToolsPage";
import BookmarksPage from "./pages/BookmarksPage";
import HistoryPage from "./pages/HistoryPage";
import SettingsPage from "./pages/SettingsPage";

function AppLayout() {
  const { activePage, setSidebarCollapsed } = useApp();
  const isMobile = useIsMobile();

  // Auto-collapse sidebar on mobile
  useEffect(() => {
    if (isMobile) setSidebarCollapsed(true);
  }, [isMobile, setSidebarCollapsed]);

  const renderPage = () => {
    switch (activePage) {
      case "home": return <HomePage />;
      case "search": return <SearchPage />;
      case "ai": return <AIPage />;
      case "drive": return <DrivePage />;
      case "tools": return <ToolsPage />;
      case "bookmarks": return <BookmarksPage />;
      case "history": return <HistoryPage />;
      case "settings": return <SettingsPage />;
      default: return <HomePage />;
    }
  };

  return (
    <div className="h-screen flex overflow-hidden" style={{ background: "oklch(0.965 0.006 260)" }}>
      <div
        style={{
          position: "fixed",
          right: 12,
          bottom: 12,
          zIndex: 9999,
          background: "#111827",
          color: "#ffffff",
          padding: "6px 10px",
          borderRadius: 999,
          fontSize: 11,
          letterSpacing: "0.04em",
          boxShadow: "0 8px 24px rgba(0,0,0,0.22)",
        }}
      >
        Quark Browser 已更新 · 2026-03-23 11:35
      </div>
      {/* Desktop sidebar */}
      {!isMobile && <Sidebar />}

      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Desktop tab bar */}
        {!isMobile && <TabBar />}

        <main className={`flex-1 flex flex-col overflow-hidden ${isMobile ? "pb-16" : ""}`}>
          <AnimatePresence mode="wait">
            <motion.div
              key={activePage}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2, ease: "easeOut" }}
              className="flex-1 flex flex-col overflow-hidden"
            >
              {renderPage()}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>

      {/* Mobile bottom nav */}
      {isMobile && <MobileNav />}
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider defaultTheme="light">
        <TooltipProvider>
          <AppProvider>
            <Toaster />
            <AppLayout />
          </AppProvider>
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
