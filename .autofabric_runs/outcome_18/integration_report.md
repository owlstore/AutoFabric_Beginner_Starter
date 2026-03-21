# Frontend Backend Integration Report

## 1. 总体情况
- 扫描前端文件数：17
- 含 HTTP 调用的文件数：1
- 匹配到的后端路由数：0

## 2. 前端调用情况
### `frontend/src/api/client.js`
- 调用：`{'method': 'POST', 'path': '/entry/submit', 'source': 'fetch'}`
- 调用：`{'method': 'GET', 'path': '/goals/list-view', 'source': 'fetch'}`
- 调用：`{'method': 'GET', 'path': '/health', 'source': 'fetch'}`
- 调用：`{'method': 'GET', 'path': '/outcomes/list-view', 'source': 'fetch'}`
- 调用：`{'method': 'GET', 'path': '/workspace/{goalId}', 'source': 'fetch'}`
- 调用：`{'method': 'POST', 'path': '/workspace/{goalId}/actions/execute', 'source': 'fetch'}`
- 调用：`{'method': 'GET', 'path': '/workspaces', 'source': 'fetch'}`

## 3. 已匹配到的接口

## 4. 结论
- 当前前端调用与后端路由尚未形成自动可识别的稳定映射。
- 可能存在 base URL 拼接、封装调用或未统一抽象。

## 5. 下一步建议
- 统一前端 API 路径常量。
- 为 adapter 层建立更明确的函数命名与接口映射。
- 开始将 `app/main.py` 路由拆分到 router 模块。
