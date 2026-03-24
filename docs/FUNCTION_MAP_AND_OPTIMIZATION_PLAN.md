# AutoFabric 当前功能地图与优化计划

## 当前阶段判断

项目已经从“原型堆叠期”进入“可梳理、可优化期”。

原因有两个：

1. 前后端主入口已经稳定可用。
2. 新项目闭环已经验证通过：`requirement -> clarification -> prototype -> orchestration -> execution -> testing -> delivery`。

当前可以把工作重点从“救火修通”切换到“功能收口、产品优化、代码结构整理”。

## 一、当前真实可用的功能地图

### 1. 项目与阶段主对象

主对象已经明确是 `Project`，主阶段链路是：

- `requirement`
- `clarification`
- `prototype`
- `orchestration`
- `execution`
- `testing`
- `delivery`

核心入口：

- `POST /projects`
- `GET /projects`
- `GET /projects/{project_id}`
- `POST /projects/{project_id}/transition`

对应代码：

- `backend/app/routers/project_router.py`
- `backend/app/services/project_service.py`
- `backend/app/services/stage_transition_service.py`

当前结论：

- 这部分已经是系统正式主线。
- 阶段推进已可用，但历史兼容字段仍然存在。

### 2. 需求接入与需求结构化

当前支持从自然语言输入生成需求卡、需求块与任务结构。

核心接口：

- `POST /projects/{project_id}/ingest-requirement`
- `GET /projects/{project_id}/requirements/latest`

对应代码：

- `backend/app/routers/project_requirement_router.py`
- `backend/app/services/project_requirement_service.py`
- `backend/app/services/requirement_parser_service.py`

当前结论：

- 已可用。
- 已兼容 LLM 和 fallback 两条路径。
- 是工作台第一步的核心输入能力。

### 3. 澄清问题与澄清答案回写

当前支持根据需求自动生成澄清问题，并提交答案回写到项目上下文。

核心接口：

- `POST /projects/{project_id}/generate-clarifications`
- `GET /projects/{project_id}/clarifications/latest`
- `POST /projects/{project_id}/clarifications/submit-answers`

对应代码：

- `backend/app/routers/project_clarification_router.py`
- `backend/app/routers/project_clarification_answer_router.py`
- `backend/app/services/clarification_service.py`
- `backend/app/services/clarification_answer_service.py`

当前结论：

- 已可用。
- 是从需求走向编排的关键中间层。
- 但阶段推进逻辑还没有完全收口到统一 transition 语义。

### 4. 模板推断与 Requirement Spec

当前支持从需求文本推断模板，并生成项目级 `requirement_spec`。

核心接口：

- `GET /projects/{project_id}/template/infer`
- `POST /projects/{project_id}/build-requirement-spec`
- `GET /projects/{project_id}/requirement-spec/latest`

对应代码：

- `backend/app/routers/project_template_router.py`
- `backend/app/routers/project_requirement_spec_router.py`
- `backend/app/services/template_registry_service.py`
- `backend/app/services/requirement_spec_service.py`

当前结论：

- 已可用。
- 已经成为右侧 `Overview / Specs` 的核心数据来源之一。
- 模板命中质量还有优化空间，当前存在“订单后台被推成任务看板”的情况。

### 5. Prototype Spec

当前支持基于 requirement spec 生成页面树、组件图、字段图、流转图。

核心接口：

- `POST /projects/{project_id}/build-prototype-spec`
- `POST /projects/{project_id}/create-prototype-spec`
- `GET /projects/{project_id}/prototype-spec/latest`

对应代码：

- `backend/app/routers/project_prototype_spec_router.py`
- `backend/app/services/prototype_spec_service.py`

当前结论：

- 已可用。
- 已经进入工作台主视图。
- 也是后续 codebundle 生成的上游输入。

### 6. 编排、派发与 OpenClaw Runtime

当前支持从需求生成编排计划，再把最新编排派发到 OpenClaw 风格 runtime 进行模拟推进。

核心接口：

- `POST /projects/{project_id}/generate-orchestration-from-requirements`
- `POST /projects/{project_id}/dispatch-orchestration-latest`
- `GET /projects/{project_id}/openclaw/runtime/{dispatch_id}`
- `POST /projects/{project_id}/openclaw/runtime/{dispatch_id}/simulate`

对应代码：

- `backend/app/routers/project_orchestration_from_requirement_router.py`
- `backend/app/routers/project_dispatch_from_orchestration_router.py`
- `backend/app/routers/project_openclaw_runtime_router.py`

当前结论：

- 已能支撑当前工作台中的“流式执行演示”。
- 但属于“可演示、待收敛”的能力，协议与正式执行链还有分层空间。

### 7. 执行产物、代码骨架、验证报告、交付包

当前已经打通了完整产物链。

核心接口：

- `POST /projects/{project_id}/generate-execution-artifacts`
- `POST /projects/{project_id}/generate-codebundle`
- `POST /projects/{project_id}/build-validation-report`
- `POST /projects/{project_id}/build-delivery-package`
- `GET /projects/{project_id}/artifacts/files`
- `GET /projects/artifacts/{artifact_id}/content`

对应代码：

- `backend/app/routers/project_execution_artifact_router.py`
- `backend/app/routers/project_codegen_router.py`
- `backend/app/routers/project_validation_report_router.py`
- `backend/app/routers/project_delivery_engine_router.py`
- `backend/app/routers/project_artifact_explorer_router.py`
- `backend/app/services/project_artifact_registry_service.py`

当前结论：

- 这是目前最有价值的闭环能力。
- 已经通过 fresh smoke 验证。
- 已能在工作台里看到真实交付文件。

### 8. Workspace Summary 聚合视图

当前前端主工作台依赖的是聚合接口，而不是分散逐块取数。

核心接口：

- `GET /projects/{project_id}/workspace-summary`

对应代码：

- `backend/app/routers/project_workspace_summary_router.py`
- `backend/app/services/project_workspace_summary_service.py`

当前结论：

- 这是当前产品层最重要的“读模型”。
- 已经能聚合 project、stage、requirement、prototype、validation、artifacts。
- 但仍带少量副作用与兼容逻辑。

### 9. 当前前端主界面

前端入口已经切到 Manus 风格项目工作台。

对应代码：

- `frontend/src/App.jsx`
- `frontend/src/pages/ProjectWorkbenchManusPage.jsx`
- `frontend/src/pages/ProjectWorkbenchManusPage.css`

当前结论：

- 三栏工作台已经成立。
- 左侧是项目与阶段，中间是流式过程，右侧是 `Overview / Specs / Files`。
- 这已经可以作为正式产品界面的基础版。

## 二、当前最需要优化的地方

### P0：统一正式主线，减少“能跑但混乱”

#### 1. 路由太多，正式能力和实验能力混在一起

`backend/app/main.py` 当前注册了大量 router，其中包含：

- 正式项目链路
- OpenClaw 运行时
- runtime sync
- generated runtime
- calculation demo
- 旧实验接口

问题：

- 对外接口面过大。
- 新人不容易判断哪些是正式主线。
- 后续维护容易继续叠重复能力。

优化建议：

- 定义一条“正式产品 API 面”。
- 把 demo / runtime / bridge / legacy 标记为实验层。
- 先不删能力，但要先做分层。

#### 2. GET 聚合接口有副作用

`project_workspace_summary_service.py` 在缺 prototype 时会自动触发生成。

问题：

- 读接口不纯。
- 调试和缓存会变复杂。
- 前端很难准确判断“是查看”还是“触发生成”。

优化建议：

- `workspace-summary` 只做聚合读取。
- 自动补建逻辑迁到显式 action。
- 工作台里明确区分“查看”和“生成”。

#### 3. 阶段推进入口需要绝对收口

现在已经有统一 `transition`，但部分 service 仍会直接改 `projects.current_stage`。

典型风险点：

- `clarification_service.py`
- 一些生成型 service

优化建议：

- 规定只有 `stage_transition_service.py` 可以改阶段。
- 其他 service 只能返回“建议推进到哪个阶段”。
- 这样阶段审计和 smoke 才会长期稳定。

### P1：前端结构需要从“大页面脚本”走向“产品模块”

#### 4. `ProjectWorkbenchManusPage.jsx` 过大

当前页面承载了：

- 项目创建
- 需求接入
- 澄清生成
- 编排派发
- runtime 轮询
- artifact 打开
- dock 切换
- 错误处理

问题：

- 页面过重。
- 状态耦合高。
- 后续优化 UI 和产品逻辑会相互干扰。

优化建议：

- 拆成：
  - `useProjectList`
  - `useWorkspaceSummary`
  - `useProjectFlowRunner`
  - `useArtifactPreview`
- 页面只保留布局和组合逻辑。

#### 5. API 层没有真正收口

`frontend/src/api/projectWorkbenchApi.js` 目前几乎还是空壳，而主页面自己写了大量 `requestJson(...)`。

问题：

- 请求逻辑散落在页面里。
- 错误处理、超时策略、返回适配难统一。

优化建议：

- 把项目工作台所有请求统一收进 `projectWorkbenchApi.js`。
- 再补一层 adapter，把后端字段适配成稳定前端模型。

### P1：数据契约还有历史兼容痕迹

#### 6. 新旧字段仍然并存

当前已经兼容了这些双字段：

- `current_stage` / `current_stage_key`
- `stage_name` / `stage_key`
- `from_stage` / `from_stage_key`
- `to_stage` / `to_stage_key`
- `reason` / `transition_reason`

问题：

- 现在能跑，但长期继续双写会提高维护成本。

优化建议：

- 先保留兼容层。
- 然后定义“标准字段”。
- 最终通过迁移逐步淘汰旧字段写入。

#### 7. 模板推断质量还不稳定

现状：

- 需求已经能推模板。
- 但业务语义和模板命中仍有误差。

优化建议：

- 先做规则和关键词修正。
- 再做基于 requirement blocks 的二次判定。
- 不要直接把错误模板带到 codegen 下游。

### P2：仓库噪音较多，影响继续演进

#### 8. 前端大量备份目录仍在主树内

例如：

- `frontend/src/_backup_*`

问题：

- 搜索结果噪音大。
- 很容易误读为仍在使用的实现。

优化建议：

- 统一迁到归档目录，或者从 `src` 挪出。
- 保留历史，但不继续干扰主线开发。

#### 9. 后端仍保留一些重复或未注册实现

例如：

- `prototype_spec_router.py` 仍在仓库中，但正式主线已切到 `project_prototype_spec_router.py`

优化建议：

- 标记为 legacy，或迁出正式目录。
- 避免后续再次把重复接口挂回主应用。

## 三、建议的优化顺序

### 第一阶段：产品主线收口

目标：

- 明确正式 API 面
- 明确正式工作台数据模型
- 明确阶段推进唯一入口

建议动作：

- 清点 `backend/app/main.py` 中正式与实验 router
- 取消 `workspace-summary` 的自动生成副作用
- 统一阶段修改只能走 `transition`

### 第二阶段：前端工作台模块化

目标：

- 把当前 Manus 页面从“大组件”拆成稳定模块

建议动作：

- 收口 `projectWorkbenchApi.js`
- 拆 hooks
- 拆 action runner
- 拆 artifact preview 状态

### 第三阶段：数据契约治理

目标：

- 保留兼容能力，但减少继续扩散旧字段

建议动作：

- 定义标准字段
- 标出兼容字段
- 逐步从 service 层去掉直接依赖旧字段

### 第四阶段：体验优化

目标：

- 让工作台更像真正产品，而不是“能跑的控制台”

建议动作：

- 区分“生成动作”和“阶段推进动作”
- 增强 `Overview / Specs / Files`
- 做更明确的状态反馈、空状态、失败状态

## 四、我建议立刻开始做的 3 件事

### 1. 收口前端 API 层

优先级最高。

因为它收益最大，而且不会破坏当前主链路。

### 2. 把 `workspace-summary` 改成纯读接口

这是当前最重要的后端收敛动作。

### 3. 做一轮“正式 / 实验 / 遗留”目录标注

让整个仓库的演进方向清晰下来，避免之后继续堆叠。

## 五、当前阶段结论

结论可以简化成一句话：

项目现在已经不是“先修通再说”，而是“可以正式进入功能梳理和优化阶段”。

下一步最值得做的，不是继续补新能力，而是：

- 收口接口
- 收口页面状态
- 收口数据契约

这样后面无论是继续做产品体验，还是接更强的执行器，都会更稳。
