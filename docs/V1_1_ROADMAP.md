# AutoFabric V1.1 项目规划

## 目标
在 V1 已完成主链闭环的基础上，进入 V1.1 强化阶段，把系统从“能生成、能交付”推进到“更稳、更可运行、更可复用”。

## 当前基础
当前已具备：
- 需求输入
- 澄清问题生成
- Requirement Spec
- Prototype Spec
- Codegen V2
- Validation Report
- Delivery Package
- 新版产物优先读取
- 生成后端接口可挂载运行

## V1.1 核心方向

### 1. Prototype 强化
目标：
- 提高 prototype_spec 成功率
- 提高页面树 / 组件树 / 字段映射质量
- 适配更多需求类型

交付：
- prototype_spec 稳定输出
- 多模板页面推断策略
- flow_map / field_map 更完整

### 2. Runtime 强化
目标：
- 让 codebundle_v2 生成的 backend/router.py 真正可挂载
- 让生成接口可被直接调用
- 为后续前端预览打基础

交付：
- generated runtime mount 能力
- runtime status / mounted router 列表
- 业务接口 smoke test

### 3. Validation 强化
目标：
- 让 validation 不只是粗评分
- 增加需求覆盖、页面覆盖、接口覆盖、迁移覆盖、测试覆盖

交付：
- 更精细的 checks
- 更可信的 score
- 支持新版产物优先评分

### 4. 模板化准备
目标：
- 从单个 demo 扩展到多类项目模板
- 为 V1.2 做准备

优先模板：
- 工具型 Web App
- 任务看板
- 订单后台

## 推荐推进顺序
1. Prototype 强化
2. Runtime 强化
3. Validation 强化
4. 模板化准备

## 阶段完成标准
当以下条件满足时，V1.1 可视为通过：
- prototype_spec 不再频繁为空
- 生成后端接口可挂载并调用
- validation score 对新版产物更可信
- 至少 3 类需求可稳定走完整链路
