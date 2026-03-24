import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import * as api from "../api/phase2Api";
import ProjectCard from "../components/dashboard/ProjectCard";

export default function DashboardPage() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    api.listProjects()
      .then((data) => {
        const list = Array.isArray(data) ? data : data.items || [];
        setProjects(list);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const filtered = projects.filter((p) => {
    if (filter === "active" && p.status !== "active") return false;
    if (filter === "delivered" && p.current_stage_key !== "delivery") return false;
    if (search && !p.name?.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const stats = {
    total: projects.length,
    active: projects.filter((p) => p.status === "active").length,
    delivered: projects.filter((p) => p.current_stage_key === "delivery").length,
  };

  function handleSelect(id) {
    navigate(`/?project=${id}`);
  }

  return (
    <div className="min-h-screen bg-[#091017]">
      <header className="border-b border-white/5 px-6 py-4">
        <div className="mx-auto max-w-5xl flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold text-white">AutoFabric Dashboard</h1>
            <p className="text-[12px] text-slate-500">项目概览与管理</p>
          </div>
          <button
            onClick={() => navigate("/")}
            className="px-4 py-2 text-[13px] rounded-xl bg-cyan-600/20 text-cyan-300 border border-cyan-500/20 hover:bg-cyan-600/30 transition"
          >
            新建项目
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-6 py-8">
        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <StatCard label="总项目" value={stats.total} />
          <StatCard label="进行中" value={stats.active} color="cyan" />
          <StatCard label="已交付" value={stats.delivered} color="emerald" />
        </div>

        {/* Filters */}
        <div className="flex items-center gap-3 mb-6">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="搜索项目..."
            className="flex-1 max-w-xs px-3 py-2 text-[13px] rounded-xl bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:border-cyan-500/30 focus:outline-none"
          />
          <div className="flex gap-1">
            {[
              { key: "all", label: "全部" },
              { key: "active", label: "进行中" },
              { key: "delivered", label: "已交付" },
            ].map((f) => (
              <button
                key={f.key}
                onClick={() => setFilter(f.key)}
                className={`px-3 py-1.5 text-[12px] rounded-lg transition ${
                  filter === f.key
                    ? "bg-cyan-600/20 text-cyan-300 border border-cyan-500/20"
                    : "text-slate-400 hover:text-white hover:bg-white/5"
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>

        {/* Project grid */}
        {loading ? (
          <div className="text-center py-20 text-slate-500">加载中...</div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-20 text-slate-500">
            {search ? "没有匹配的项目" : "还没有项目，去创建一个吧"}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((p) => (
              <ProjectCard key={p.id} project={p} onSelect={handleSelect} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

function StatCard({ label, value, color = "white" }) {
  const colorMap = {
    white: "text-white",
    cyan: "text-cyan-300",
    emerald: "text-emerald-300",
  };
  return (
    <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
      <p className="text-[11px] uppercase tracking-[0.18em] text-slate-500">{label}</p>
      <p className={`mt-2 text-2xl font-semibold ${colorMap[color]}`}>{value}</p>
    </div>
  );
}
