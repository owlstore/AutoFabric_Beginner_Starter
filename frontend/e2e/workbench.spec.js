import { expect, test } from "@playwright/test";

test("@smoke operator view renders stable workbench structure", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByTestId("workbench-shell")).toBeVisible();
  await expect(page.getByTestId("workbench-brand")).toContainText("项目任务驾驶舱");
  await expect(page.getByTestId("project-sidebar")).toBeVisible();
  await expect(page.getByTestId("project-list")).toBeVisible();
  await expect(page.getByTestId("project-composer-input")).toBeVisible();
  await expect(page.getByTestId("project-start-button")).toBeEnabled();
  await expect(page.getByTestId("dock-tab-overview")).toBeVisible();
  await expect(page.getByTestId("dock-tab-files")).toBeVisible();
  await expect(page.getByTestId("refresh-workbench-button")).toBeVisible();
  await expect(page.getByTestId("error-panel")).toHaveCount(0);
});

test("@smoke simple view keeps composer usable", async ({ page }) => {
  await page.goto("/");

  await page.getByTestId("view-toggle-button").click();
  await expect(page.getByTestId("project-sidebar")).toHaveCount(0);
  await expect(page.getByTestId("view-toggle-button")).toContainText("进入操作视图");

  const composer = page.getByTestId("project-composer-input");
  await composer.fill("Playwright 页面级冒烟验证");
  await expect(composer).toHaveValue("Playwright 页面级冒烟验证");
  await expect(page.getByTestId("project-start-button")).toBeEnabled();

  await page.getByTestId("dock-tab-files").click();
  await expect(page.getByText("更多结果")).toBeVisible();

  await page.getByTestId("view-toggle-button").click();
  await expect(page.getByTestId("project-sidebar")).toBeVisible();
});

test("@fullflow simple view can turn one prompt into a delivered task template", async ({ page }) => {
  test.setTimeout(240_000);

  const requirement = `任务看板自动化回归 ${Date.now()}，支持任务新增、状态切换、负责人分配、优先级管理和筛选统计，并生成代码、测试报告和交付包。`;

  await page.goto("/");
  await page.getByTestId("view-toggle-button").click();
  await expect(page.getByTestId("project-sidebar")).toHaveCount(0);
  await expect(page.getByTestId("simple-status-strip")).toBeVisible();

  const composer = page.getByTestId("project-composer-input");
  await composer.fill(requirement);
  await page.getByTestId("project-start-button").click();

  await expect(page.getByText("项目已交付")).toBeVisible({ timeout: 180_000 });

  await page.getByTestId("dock-tab-overview").click();
  await expect(page.getByTestId("template-outcome-panel")).toBeVisible({ timeout: 30_000 });
  await expect(page.getByTestId("template-outcome-title")).toContainText("任务看板");
  await expect(page.getByTestId("template-outcome-card-primary_flow")).toContainText(/任务新增|状态切换/);
  await expect(page.getByTestId("result-summary-panel")).toBeVisible();
  await expect(page.getByTestId("result-highlight-delivery")).toContainText("交付包");
  await expect(page.getByTestId("result-highlight-quality")).toContainText("/ 100");

  await page.getByTestId("dock-tab-files").click();
  await expect(page.getByTestId("artifact-browser-list")).toBeVisible({ timeout: 15_000 });
  await expect(page.getByTestId("artifact-preview")).toBeVisible({ timeout: 15_000 });
  await expect(page.getByTestId("artifact-browser-list").getByText("ACCEPTANCE_CHECKLIST.md").first()).toBeVisible();
  await expect(page.getByTestId("artifact-browser-list").getByText("template_delivery_profile.json").first()).toBeVisible();
  await expect(page.getByTestId("artifact-browser-list").getByText("preview_index.html").first()).toBeVisible();
  await expect(page.getByTestId("artifact-browser-list").getByText("acceptance_smoke.sh").first()).toBeVisible();
});
