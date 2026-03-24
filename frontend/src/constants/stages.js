export const STAGES = [
  "requirement",
  "clarification",
  "prototype",
  "orchestration",
  "execution",
  "testing",
  "delivery",
];

export const STAGE_LABELS = {
  requirement: "需求",
  clarification: "澄清",
  prototype: "原型",
  orchestration: "编排",
  execution: "执行",
  testing: "测试",
  delivery: "交付",
};

export function getNextStage(currentStage) {
  const idx = STAGES.indexOf(currentStage);
  if (idx === -1 || idx === STAGES.length - 1) return null;
  return STAGES[idx + 1];
}
