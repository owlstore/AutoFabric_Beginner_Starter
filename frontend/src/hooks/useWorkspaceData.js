import { useEffect, useMemo, useState } from "react";
import {
  buildCardsFromWorkspaces,
  buildDetailView,
  buildStageCounts,
  buildStatsFromWorkspaces,
} from "../adapters/workbenchAdapter";
import { fetchWorkspaceDetail, fetchWorkspaces, submitEntry } from "../api/workbenchApi";

export default function useWorkspaceData({ input, setInput, clearInputDraft, toast }) {
  const [submitting, setSubmitting] = useState(false);
  const [quickFilter, setQuickFilter] = useState("all");
  const [searchText, setSearchText] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [goalTypeFilter, setGoalTypeFilter] = useState("all");
  const [sortOrder, setSortOrder] = useState("updated_desc");
  const [activeCardId, setActiveCardId] = useState(null);
  const [goalCandidates, setGoalCandidates] = useState([]);
  const [expandedFields, setExpandedFields] = useState({
    goal: false,
    result: false,
    next: false,
  });

  const [cards, setCards] = useState([]);
  const [stats, setStats] = useState({ total: 0, completed: 0, running: 0, failed: 0 });
  const [stageCounts, setStageCounts] = useState({
    requirement: 0,
    clarification: 0,
    prototype: 0,
    orchestration: 0,
    execution: 0,
    testing: 0,
    delivery: 0,
    unknown: 0,
  });
  const [detailData, setDetailData] = useState(null);
  const [listLoading, setListLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [listError, setListError] = useState("");
  const [detailError, setDetailError] = useState("");

  async function loadList(forceSelectLatest = false) {
    try {
      setListLoading(true);
      setListError("");
      const payload = await fetchWorkspaces();
      const nextCards = buildCardsFromWorkspaces(payload);
      setCards(nextCards);
      setStats(buildStatsFromWorkspaces(payload));
      setStageCounts(buildStageCounts(payload));

      if (forceSelectLatest) {
        setActiveCardId(nextCards[0]?.goal_id ?? null);
      } else {
        setActiveCardId((prev) => prev ?? nextCards[0]?.goal_id ?? null);
      }

      return nextCards;
    } catch (err) {
      const message = String(err?.message || err);
      setListError(message);
      return [];
    } finally {
      setListLoading(false);
    }
  }

  async function loadDetail(goalId) {
    if (!goalId) return;
    try {
      setDetailLoading(true);
      setDetailError("");
      const payload = await fetchWorkspaceDetail(goalId);
      setDetailData(payload);
      return payload;
    } catch (err) {
      setDetailError(String(err?.message || err));
      return null;
    } finally {
      setDetailLoading(false);
    }
  }

  useEffect(() => {
    loadList();
  }, []);

  useEffect(() => {
    if (activeCardId) {
      loadDetail(activeCardId);
    }
  }, [activeCardId]);

  useEffect(() => {
    setGoalCandidates([]);
    setExpandedFields({ goal: false, result: false, next: false });
  }, [activeCardId]);

  const filteredCards = useMemo(() => {
    let next = [...cards];

    if (quickFilter !== "all") {
      next = next.filter((x) => x.stageKey === quickFilter);
    }

    if (statusFilter !== "all") {
      const labelMap = {
        completed: "已完成",
        running: "执行中",
        failed: "失败",
        draft: "草稿",
      };
      next = next.filter((x) => x.statusLabel === labelMap[statusFilter]);
    }

    if (goalTypeFilter !== "all") {
      const typeMap = {
        system_build: "系统构建",
        system_understanding: "系统理解",
        general_task: "通用任务",
      };
      next = next.filter((x) => x.goalTypeLabel === typeMap[goalTypeFilter]);
    }

    if (searchText.trim()) {
      const q = searchText.trim().toLowerCase();
      next = next.filter((x) =>
        [x.title, x.statusLabel, x.currentResult, x.nextAction, x.stageLabel, x.rawStage]
          .join(" ")
          .toLowerCase()
          .includes(q)
      );
    }

    if (sortOrder === "updated_desc") {
      next.sort((a, b) => Number(b.outcome_id || 0) - Number(a.outcome_id || 0));
    } else if (sortOrder === "updated_asc") {
      next.sort((a, b) => Number(a.outcome_id || 0) - Number(b.outcome_id || 0));
    } else if (sortOrder === "title_asc") {
      next.sort((a, b) => a.title.localeCompare(b.title));
    } else if (sortOrder === "title_desc") {
      next.sort((a, b) => b.title.localeCompare(a.title));
    }

    return next;
  }, [cards, quickFilter, statusFilter, goalTypeFilter, searchText, sortOrder]);

  const activeDetail = useMemo(() => {
    if (!detailData) return null;
    return buildDetailView(detailData);
  }, [detailData]);

  async function handleSubmit(e) {
    e.preventDefault();
    const trimmed = String(input || "").trim();
    if (!trimmed) return;

    try {
      setSubmitting(true);
      await submitEntry(trimmed);
      clearInputDraft();
      await loadList(true);
      toast.success("目标提交成功，已刷新结果清单。");
    } catch (err) {
      toast.error(`目标提交失败：${String(err?.message || err)}`);
    } finally {
      setSubmitting(false);
    }
  }

  function continueFromCurrentOutcome(detail) {
    if (!detail) return;
    const nextGoal = [
      `Continue from current outcome: ${detail.title}`,
      detail.currentResult ? `Current result: ${detail.currentResult}` : "",
      detail.nextAction ? `Next action to pursue: ${detail.nextAction}` : "",
    ]
      .filter(Boolean)
      .join("\n");
    setInput(nextGoal);
    window.scrollTo({ top: 0, behavior: "smooth" });
    toast.info("已把当前结果带入顶部输入框。");
  }

  function generateGoalCandidates(detail) {
    if (!detail) return;
    setGoalCandidates([
      `Continue implementation for: ${detail.title}\nFocus on: ${detail.nextAction || detail.currentResult}`,
      `Validate and refine current outcome: ${detail.title}\nBased on current result: ${detail.currentResult || detail.nextAction}`,
      `Create next executable task from outcome: ${detail.title}\nTarget next step: ${detail.nextAction || detail.currentResult}`,
    ]);
    toast.info("已生成后续目标候选。");
  }

  function applyGoalCandidate(candidate) {
    setInput(candidate);
    window.scrollTo({ top: 0, behavior: "smooth" });
    toast.success("已使用候选目标填充输入框。");
  }

  async function refreshWorkbench() {
    await loadList();
    if (activeCardId) {
      await loadDetail(activeCardId);
    }
    toast.success("工作台已刷新。");
  }

  async function refreshCurrentDetailOnly() {
    if (activeCardId) {
      await loadDetail(activeCardId);
    }
  }

  return {
    submitting,
    quickFilter,
    setQuickFilter,
    searchText,
    setSearchText,
    statusFilter,
    setStatusFilter,
    goalTypeFilter,
    setGoalTypeFilter,
    sortOrder,
    setSortOrder,
    activeCardId,
    setActiveCardId,
    goalCandidates,
    setGoalCandidates,
    expandedFields,
    setExpandedFields,
    cards,
    stats,
    stageCounts,
    detailData,
    listLoading,
    detailLoading,
    listError,
    detailError,
    filteredCards,
    activeDetail,
    loadList,
    loadDetail,
    handleSubmit,
    continueFromCurrentOutcome,
    generateGoalCandidates,
    applyGoalCandidate,
    refreshWorkbench,
    refreshCurrentDetailOnly,
  };
}
