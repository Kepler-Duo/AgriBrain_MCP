# 🌱 智慧农业大脑框架

本项目旨在构建一个面向智慧农业的智能大脑系统，整合多种 AI 能力，通过工作流编排、服务化部署与工具封装，提升农业生产的自动化与智能化水平。

---

## 📁 项目结构与模块说明

### 1. `graphchat/` - LangGraph 工作流程图模块
该目录用于构建基于 [LangGraph](https://github.com/langchain-ai/langgraph) 的对话工作流框架，主要功能包括：

- 定义多节点对话流程（如感知 → 推理 → 决策）
- 管理节点状态和上下文传递
- 适用于农业生产中多轮交互任务场景（如病虫害诊断、田间问答）

### 2. `mcp_servers/` - MCP 服务启动模块
该模块封装了智慧农业任务调度核心的服务端逻辑，包括：

- 启动 MCP（Multi-Component Process）服务器
- 负责模型调用、任务调度与服务注册
- 提供统一的 API 接口供前端与业务调用

### 3. `tools/` - 工具节点模块
该目录下包含各种工具函数与原始 Function Call 形式工具，主要功能包括：

- 封装通用工具（如天气查询、作物数据分析、环境感知接口）
- 提供标准化的工具调用格式，支持 LangChain 工具集成
- 支持原始 OpenAI Function Calling 接口格式的工具定义

---

## ✅ TODO List

### ✅ 已完成项

- [x] 智慧农业大脑基础框架搭建
- [x] 环境监测助理模块
- [x] 病虫害管理助理模块

### 🚧 进行中 / 待完成项

- [ ] 作物生长监测子助理模块
- [ ] 农机调度决策子助理模块
- [ ] 水肥管理子助理模块
- [ ] `MCP_Servers` 模块功能完善
- [ ] 检索增强生成（RAG）能力集成

---
## 🚀 快速开始

```bash
# 安装依赖（建议使用 conda）
pip install -r requirements.txt

# 启动 MCP 服务
python MCP_Servers/environment_server.py

# 启动 LangGraph 流程测试
python graphchat/main.py
