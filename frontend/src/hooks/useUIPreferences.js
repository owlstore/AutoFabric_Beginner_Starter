import { useEffect } from "react";
import { STORAGE_KEYS } from "../constants/storageKeys";

function read(key, fallback) {
  try {
    const value = localStorage.getItem(key);
    return value === null ? fallback : value;
  } catch {
    return fallback;
  }
}

export default function useUIPreferences({
  activeCardId,
  setActiveCardId,
  activeTab,
  setActiveTab,
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
}) {
  useEffect(() => {
    const savedGoalId = read(STORAGE_KEYS.ACTIVE_GOAL_ID, "");
    const savedTab = read(STORAGE_KEYS.ACTIVE_RECORD_TAB, "timeline");
    const savedQuickFilter = read(STORAGE_KEYS.QUICK_FILTER, "all");
    const savedSearchText = read(STORAGE_KEYS.SEARCH_TEXT, "");
    const savedStatusFilter = read(STORAGE_KEYS.STATUS_FILTER, "all");
    const savedGoalTypeFilter = read(STORAGE_KEYS.GOAL_TYPE_FILTER, "all");
    const savedSortOrder = read(STORAGE_KEYS.SORT_ORDER, "updated_desc");

    if (savedGoalId) setActiveCardId(Number(savedGoalId));
    if (savedTab) setActiveTab(savedTab);
    if (savedQuickFilter) setQuickFilter(savedQuickFilter);
    if (savedSearchText !== undefined) setSearchText(savedSearchText);
    if (savedStatusFilter) setStatusFilter(savedStatusFilter);
    if (savedGoalTypeFilter) setGoalTypeFilter(savedGoalTypeFilter);
    if (savedSortOrder) setSortOrder(savedSortOrder);
  }, []);

  useEffect(() => {
    try {
      if (activeCardId !== null && activeCardId !== undefined) {
        localStorage.setItem(STORAGE_KEYS.ACTIVE_GOAL_ID, String(activeCardId));
      }
    } catch {}
  }, [activeCardId]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.ACTIVE_RECORD_TAB, activeTab);
    } catch {}
  }, [activeTab]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.QUICK_FILTER, quickFilter);
    } catch {}
  }, [quickFilter]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.SEARCH_TEXT, searchText);
    } catch {}
  }, [searchText]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.STATUS_FILTER, statusFilter);
    } catch {}
  }, [statusFilter]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.GOAL_TYPE_FILTER, goalTypeFilter);
    } catch {}
  }, [goalTypeFilter]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.SORT_ORDER, sortOrder);
    } catch {}
  }, [sortOrder]);
}
