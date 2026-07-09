# AI 短剧脚本生成器 · 剧工厂 🎬

30 秒生成爆款竖屏短剧脚本，由 DeepSeek V4 驱动。

## 快速开始

```bash
# 1. 安装依赖（Python 3.11+）
#    使用 QClaw 内置 Python（位于 D:\Program Files\QClaw\…）
#    或系统已安装的 python3

# 2. 设置 DeepSeek API Key
set DEEPSEEK_KEY=你的key

# 3. 启动服务
python3 server.py
# 浏览器打开 http://localhost:3722
```

## 功能特性

- ✅ **五大热门题材**：都市逆袭、甜宠言情、悬疑惊悚、穿越重生、先婚后爱
- ✅ **三种节奏风格**：爆款爽文、极简快节奏、深度剧情
- ✅ **完整输出结构**：分镜表 + 完整剧本 + 下集钩子
- ✅ **竖屏原生**：每镜头为手机竖屏设计
- ✅ **极低成本**：DeepSeek V4，单次量级 ¥0.005–0.02

## 技术栈

- **后端**：Python 3.11 (http.server) + DeepSeek Chat API
- **前端**：原生 HTML/CSS/JS，暗色主题
- **无外部依赖**（纯 Python 标准库 + 系统已装 Git）
- 代理支持：自动识别系统代理设置

## 项目结构

```
ai-script-hub/
├── server.py          # Python 后端（Express-like 路由）
├── public/index.html  # 前端页面
├── prompts.js         # 提示词模板（预留）
├── server.js          # Node.js 版（预留）
├── run_server.bat     # 一键启动（Windows）
├── .gitignore
└── package.json
```
