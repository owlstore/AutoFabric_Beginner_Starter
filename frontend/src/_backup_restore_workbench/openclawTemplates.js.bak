export const OPENCLAW_TEMPLATES = [
  {
    id: "inspect_order_submission_ui",
    label: "Inspect Order Submission UI",
    task_name: "inspect_order_submission_ui",
    description: "Inspect a broken order submission flow in browser UI.",
    defaults: {
      url: "https://example.com/orders",
      issue: "submit button not working",
      account_hint: "demo_user",
    },
  },
  {
    id: "locate_payment_module",
    label: "Locate Payment Module",
    task_name: "locate_payment_module",
    description: "Locate payment-related module or page context through browser workflow.",
    defaults: {
      url: "https://example.com/payments",
      issue: "payment flow issue needs location and context",
      account_hint: "demo_user",
    },
  },
  {
    id: "collect_system_analysis_context",
    label: "Collect System Analysis Context",
    task_name: "collect_system_analysis_context",
    description: "Collect extra browser-side context for system understanding.",
    defaults: {
      url: "https://example.com/dashboard",
      issue: "need more context from browser workflow",
      account_hint: "demo_user",
    },
  },
];

export function getOpenclawTemplateById(id) {
  return OPENCLAW_TEMPLATES.find((item) => item.id === id) || OPENCLAW_TEMPLATES[0];
}
