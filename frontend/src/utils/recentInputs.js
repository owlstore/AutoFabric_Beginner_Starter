export function mergeRecentInputs(prev, nextValue, limit = 6) {
  const trimmed = String(nextValue || "").trim();
  if (!trimmed) return prev;
  return [trimmed, ...prev.filter((item) => item !== trimmed)].slice(0, limit);
}
