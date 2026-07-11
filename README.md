# 🎬 剧工厂 · AI 短剧脚本生成器

> **一句话梗概 → 30秒 → 完整短剧剧本（分镜表 + 人物设定 + 对白 + 下集钩子）**

🌐 **在线体验：** [www.jugongchang.icu](https://www.jugongchang.icu)
📦 **GitHub：** [github.com/ugo2000/ai-script-hub](https://github.com/ugo2000/ai-script-hub)

---

## ✨ 它能做什么

输入一句核心梗概，比如：

> *"一个被公司辞退的中年程序员，在出租屋意外发现一个能预测未来3分钟的APP"*

30 秒后，你得到：

| 模块 | 内容 |
|------|------|
| 🎭 **人物设定** | 主角性格/背景/关系表 |
| 🎬 **分镜表** | 每镜头时长、场景、运镜、景别 |
| 💬 **完整对白** | 竖屏短剧格式，情节推进 |
| 🪝 **下集钩子** | 结尾反转/悬念，引导追更 |

## 🎯 支持题材

| 题材 | 说明 |
|------|------|
| 🔥 都市逆袭 | 打工人翻身、商场博弈 |
| 💕 甜宠言情 | 先婚后爱、契约情侣 |
| 👻 悬疑惊悚 | 反转不断、细思极恐 |
| 🌌 穿越重生 | 古穿今、今穿古、重生虐渣 |
| 📱 系统文 | 签到、抽奖、面板、神豪 |

## 🚀 快速上手

```bash
# 克隆
git clone https://github.com/ugo2000/ai-script-hub.git
cd ai-script-hub

# 安装依赖
pip install -r requirements.txt

# 设置 API Key
export DEEPSEEK_KEY=sk-your-key-here

# 启动（端口 3722）
python3 server.py
```

浏览器打开 `http://localhost:3722` 即可使用。

## 🧱 技术栈

```
前端   原生 HTML/CSS/JS（暗色主题 | 响应式 | 单页应用）
后端   Python http.server + DeepSeek Chat API
支付   支付宝当面付（个人开发者友好）
鉴权   HMAC-SHA256 token + SQLite
部署   Docker + 腾讯云 + Cloudflare Tunnel（零入站端口）
```

## 💰 定价

| 版本 | 价格 | 特点 |
|------|------|------|
| 🆓 免费版 | ¥0 | 每日 2 次，全部题材，限 hot 风格 |
| 🚀 专业版 | ¥39/月 | 无限次生成，全部风格 + 自定义人物 |
| 🏢 工作室版 | ¥199/月 | 批量产出，Word/PDF 导出（开发计划中） |

## 📸 截图

![首页截图](https://www.jugongchang.icu/og-image.png)

## 🤝 贡献

欢迎提 Issue / PR。任何想法都可以来 [Discussions](https://github.com/ugo2000/ai-script-hub/discussions) 聊。

## 📄 许可

MIT License

---

**剧工厂** — 让每个人都能成为短剧编剧 🎬
