# AutoFabric 下一阶段研发主线

## 目标一句话

把 AutoFabric 从“已跑通需求到交付闭环的自动化研发原型”，推进成“可复制、可推广、可扩展的自动化研发平台”。

---

## 一、我们已经确认的核心前提

这些内容不再摇摆，作为下一阶段主线的固定前提。

### 1. 平台主状态机

正式主链路固定为：

- `requirement`
- `clarification`
- `prototype`
- `orchestration`
- `execution`
- `testing`
- `delivery`

### 2. 角色分工

- `Codex`：负责需求分析、澄清、确认、原型方案、研发编排、评审与门禁
- `OpenClaw`：负责接收编排结果，统一调度 agent、skills、tools，并回传运行结果
- `Agent`：负责前端、后端、数据库、测试、部署等专业执行
- `Skill`：负责方法包、输入输出 schema、允许工具、质量约束
- `Tool`：负责具体执行，如 Figma、React、FastAPI、PostgreSQL、Pytest、Playwright、Docker、CI/CD

### 3. 前端产品原则

默认模式下，用户只做两件事：

- 提需求
- 看进度

因此默认前端采用：

- `Simple Mode`：会话框 + 运行监控 + 结果交付
- `Operator Mode`：隐藏的系统诊断与调优视图

### 4. OpenClaw 的正式定位

OpenClaw 是：

- 执行调度中枢
- 浏览器自动化执行器
- 多 Agent 运行时协调器

OpenClaw 不是：

- 项目主状态机
- 平台大脑
- 生命周期主治理层

### 5. 展示语言原则

面向用户的默认展示语言固定为中文：

- 前端 UI 文案默认中文
- 过程进度提示默认中文
- 风险提醒与确认提示默认中文
- 交付摘要与结果说明默认中文

以下内容允许保留英文或中英混合：

- 代码
- API path
- 文件名
- 第三方工具原始字段
- 需要保真的原始日志

---

## 二、下一阶段主线目标

下一阶段不是继续“补功能”，而是围绕以下主线推进：

### 主线目标

**建立一套稳定的控制平面 + 执行平面 + 工具平面，使 AutoFabric 从单次闭环演示升级为可持续运行的平台。**

这条主线拆成 5 个连续阶段。

---

## 三、阶段 1：冻结平台骨架

## 目标

先把所有最容易摇摆的核心定义固定下来。

### 本阶段必须确认的内容

#### 1. 控制平面

由 AutoFabric 自己掌握：

- `Project`
- `Stage`
- `Workspace`
- `stage_transition`
- `human_approval`
- `delivery_gate`

#### 2. 执行平面

由 OpenClaw Runtime 负责：

- 接收 `agent_jobs`
- 管理 `skills`
- 分派执行器
- 跟踪任务状态
- 收集日志与产物

#### 3. 工具平面

全部工具通过 adapter 接入：

- Figma
- React/Vite
- FastAPI
- PostgreSQL
- Alembic
- Pytest
- Playwright
- Docker Compose
- GitHub Actions

### 本阶段产物

- `agent_registry`
- `skill_registry`
- `tool_adapter_registry`
- `project_tool_policy`
- `delivery_profile`

### 确认点

完成标准：

- 角色边界不再反复变化
- 所有后续能力都能映射到 `Project / Agent / Skill / Tool`
- OpenClaw 不再承担主状态机职责

---

## 四、阶段 2：前端切换到 Codex 式任务驾驶舱

## 目标

把前端从“阶段后台”切成“用户只提需求、看进度”的产品形态。

### 本阶段重点

#### 1. 默认进入 Simple Mode

页面结构：

- 顶部：项目标题 + 当前总状态
- 中间：任务输入 + 流式过程
- 右侧：最新产物 / 测试 / 交付

默认展示要求：

- 中文优先
- 技术细节后置
- 不要求用户理解内部阶段术语

#### 2. Operator Mode 下沉

这些内容不在默认模式大面积展示：

- requirement spec
- prototype spec
- orchestration plan
- agent jobs
- runtime internals
- skill/tool 细节

#### 3. 重构读模型

后端面向 Simple Mode 输出：

- `conversation_summary`
- `current_action`
- `progress_events`
- `latest_outputs`
- `delivery_ready`
- `needs_confirmation`

### 本阶段产物

- 简化后的前端首页
- Simple Mode 读模型
- Operator Mode 诊断面板

### 确认点

完成标准：

- 普通用户无需理解阶段模型也能使用系统
- 一个新用户首次打开页面就知道如何开始
- 用户不再需要点击大量内部阶段按钮

---

## 五、阶段 3：建立 Codex -> OpenClaw -> Agent 的正式执行链

## 目标

让“Codex 编排，OpenClaw 调度，Agent 执行”的模型成为正式主链。

### 本阶段重点

#### 1. Agent Job 标准化

每个 job 至少包含：

- `agent_type`
- `required_skills`
- `allowed_tools`
- `risk_level`
- `review_mode`
- `depends_on`

#### 2. Skill 装配机制

由 OpenClaw Runtime 负责：

- 加载 skill 版本
- 绑定允许工具
- 应用 guardrails
- 执行失败重试

#### 3. Tool Policy 执行

项目级策略要生效，例如：

- 是否允许浏览器执行
- 是否允许真实数据库写入
- 是否允许部署
- 是否允许外网访问

### 本阶段产物

- `agent_jobs` 标准 schema
- `skill_bindings`
- `tool_policy enforcement`
- OpenClaw runtime 回写机制

### 确认点

完成标准：

- 任何执行任务都能明确回答：
  - 谁做
  - 用什么 skill 做
  - 用什么工具做
  - 风险怎么控制

---

## 六、阶段 4：把工具链接成整体解决方案

## 目标

不再只是“能生成代码”，而是形成端到端工程方案。

### 工具链集成顺序

#### T1：必须接通

- 原型设计：Figma
- 前端：React + Vite
- 后端：FastAPI
- 数据库：PostgreSQL + SQLAlchemy + Alembic
- 测试：Pytest + Playwright
- 浏览器自动化兜底：OpenClaw
- 部署：Docker Compose

#### T2：增强接入

- GitHub / GitLab
- GitHub Actions / CI
- 对象存储
- Preview 环境

### 默认交付形式

默认交付不采用虚拟机优先，而采用：

1. `源码包`
2. `Docker Compose 交付包`
3. `预览环境 / 可挂载运行时`

虚拟机镜像只作为：

- 政企场景
- 内网场景
- 特殊部署规范场景

### 本阶段产物

- `delivery_profiles`
  - `source_package`
  - `compose_package`
  - `preview_runtime`
  - `enterprise_vm_package`（可选）

### 确认点

完成标准：

- 一个项目可以稳定交付“可运行的整体方案”，而不只是代码碎片

---

## 七、阶段 5：从产品闭环升级到平台闭环

## 目标

让系统具备“可复制、可推广、可持续优化”的平台能力。

### 本阶段重点

#### 1. Operate Layer

补齐：

- runtime mount
- deploy record
- runtime status
- log aggregation
- observability summary

#### 2. Feedback Layer

补齐：

- 用户反馈
- 缺陷回流
- next iteration suggestion
- 交付后问题归因

#### 3. Learning Layer

补齐：

- case snapshots
- template evaluation
- skill effectiveness
- common failure patterns
- 历史相似项目召回

### 本阶段产物

- `deployment_records`
- `runtime_observations`
- `feedback_backlog`
- `case_library`
- `next_iteration_plan`

### 确认点

完成标准：

- 一个项目交付后，系统还能继续运营、观察、回流和学习
- 平台能从每次项目执行中提升下一次执行质量

---

## 八、什么时候算“形成可推广的平台”

不是功能够多就算平台，而是以下 6 条都满足时，才算进入可推广阶段。

### 1. 主链路稳定

- 新项目从需求到交付可重复跑通
- 多次运行结果一致性可接受

### 2. 前端易用

- 普通用户只需提需求、看进度
- 高级模式不干扰默认使用
- 默认交互与展示语言为中文

### 3. Agent / Skill / Tool 体系清晰

- 角色、技能、工具可解释
- 可扩展但不混乱

### 4. 交付形式标准化

- 至少有标准源码包
- 至少有标准 Compose 包
- 至少有预览或运行入口

### 5. 可运维

- 部署、运行、日志、失败回流有记录

### 6. 可学习

- 能沉淀案例
- 能优化模板
- 能改进下一轮执行

---

## 九、接下来每一步怎么确认

建议按“阶段结束即评审”的方式推进。

### Step 1 评审

确认：

- 架构角色边界是否冻结
- OpenClaw、Codex、Agent、Skill、Tool 是否不再混淆

### Step 2 评审

确认：

- 默认前端是否已经变成 Codex 式会话入口
- 用户是否只需提需求与看进度

### Step 3 评审

确认：

- OpenClaw 是否真正能统一调度多 agent
- skills 是否真正由 runtime 装配和管理

### Step 4 评审

确认：

- 工具链是否形成完整工程交付方案
- 交付形式是否标准化

### Step 5 评审

确认：

- 是否形成 deploy / observe / feedback / learning 闭环

---

## 十、下一阶段的正式研发主线

如果压缩成一句研发主线，就是：

**先冻结控制平面与执行平面的边界，再把前端简化成 Codex 式驾驶舱，然后完成 Agent/Skill/Tool 注册体系与标准交付方案，最后补齐运行、反馈、学习能力，形成可推广的平台。**

这条主线的顺序不能乱：

1. 冻结角色边界
2. 简化前端产品形态
3. 建立 Agent/Skill/Tool 执行体系
4. 打通工具链与标准交付
5. 补 Operate / Feedback / Learning

## 最终一句话

下一阶段的核心不是“再做更多功能”，而是：

**把现在这条能跑通的自动化研发链路，收敛成一个真正可推广的平台骨架。**
