// src/api/client.js
export function loadOutcomeTimeline(outcomeId) {
  // 示例：返回与 outcomeId 相关的数据
  return fetch(`/api/outcome/${outcomeId}/timeline`)
    .then(response => response.json())
    .catch(err => console.error(err));
}