# 剧工厂推广行动指南
**日期：2026-07-11** | 网站：https://www.jugongchang.icu

---

## 一、V2EX 发帖文案（站长/程序员视角）

**建议标题：** 免费送独立站用户：我写了个 AI 短剧脚本生成器，30秒出专业剧本

**正文：**

```markdown
先上地址：https://www.jugongchang.icu

## 背景

我是独立开发者，做了两个月短剧工具。起因是发现抖音快手上一天几千部短剧在上，但大多数编剧还在手写剧本。既然大模型这么强，为什么不搞个一键生成？

## 干了什么

输入一句话梗概 → 选择类型（都市/古装/悬疑/甜宠/系统文5种）→ 30秒出产：

- 完整分镜表（场景、镜头时长、运镜方法）
- 人物设定表
- 完整对白剧本
- 下集钩子

## 技术栈

- 前端：纯原生 HTML/CSS/JS（无框架，单页）
- 后端：Python HTTP Server + DeepSeek V4 API
- 支付：支付宝当面付（个人可接，免资质）
- 部署：腾讯云 + Cloudflare Tunnel（全站无入站端口，安全）
- 用户：HMAC-SHA256 token 鉴权 + SQLite

## 良心之处

- 免费用户每天 2 次额度（随便用，完全够尝鲜）
- 专业版 39/月（无限次，送优先队列）
- 工作室版 199/月（不限量，可以团队用）
- 源码在 GitHub：https://github.com/ugo2000/ai-script-hub（欢迎 star）

## 求反馈

- 输出的剧本质量能不能打？有没有需要加的类型？
- 你觉得短剧这个赛道还有哪些工具是刚需？
- 直接评论区骂，我受得住。

🎬 点击白嫖：https://www.jugongchang.icu
```

---

## 二、产品目录站提交清单

### 1. 即刻「产品博物馆」
- **链接：** https://web.okjike.com/category/product
- **方式：** 在即刻发布动态带 #产品博物馆 标签，文案见下面「即刻短动态版」

### 2. Product Hunt
- **链接：** https://www.producthunt.com/
- **方式：** 需注册 maker 账号，提交产品。建议准备英文版介绍
- **英文标题：** JugongChang - AI Short Drama Script Generator in 30 Seconds
- **英文一句话：** Turn one sentence plot into a professional short drama script with storyboard, character sheets and dialogue - 100% Chinese content optimized.

### 3. 少数派
- **链接：** https://sspai.com/
- **方式：** 在「Matrix」板块发布文章，偏工具推荐风格
- **建议角度：**「AI 时代的内容生产方式：用大模型写短剧脚本是什么体验」

### 4. 掘金（juejin.cn）
- **链接：** https://juejin.cn/
- **方式：** 发技术文章，可侧重「从零到一：独立开发者的 AI 短剧工具技术实践」

### 5. 公众号投稿渠道（如果有）
- 推荐：知晓程序、AI 科技大本营、机器之心、极客公园

### 6. 知乎
- **链接：** https://www.zhihu.com/
- **方式：** 回答「有哪些好用的 AI 写剧本工具？」或创建类似问题

### 7. 独立开发者社区
- **V2EX**（上文已准备）
- **Hacker News**（Show HN，需英文）
- **ProductHunt**（同上）

---

## 三、百度搜索资源平台提交

### Step 1: 注册百度搜索资源平台
- **链接：** https://ziyuan.baidu.com/
- **账号：** 百度账号即可（如果已有百度账号直接登录）
- **操作：** 添加站点 `www.jugongchang.icu`

### Step 2: 验证网站所有权
三种验证方式（任选其一）：
- **方式 A - CNAME 验证（推荐）：** 添加 CNAME 记录验证（不需要改动现有 Cloudflare 配置）
- **方式 B - HTML 文件验证：** 下载百度提供的验证文件，上传到服务器
- **方式 C - HTML 标签验证：** 在 `<head>` 中添加 meta 标签

### Step 3: 提交 sitemap
- 当前 sitemap 地址：`https://www.jugongchang.icu/sitemap.xml`
- 在百度搜索资源平台 → 站点管理 → 链接提交 → Sitemap 提交

### Step 4: 自动推送（建议）
在页面中添加百度自动推送代码（如果还没加，下次迭代可以加上）：

```html
<script>
(function(){
  var bp = document.createElement('script');
  bp.src = 'https://zz.bdstatic.com/linksubmit/push.js';
  var s = document.getElementsByTagName('script')[0];
  s.parentNode.insertBefore(bp, s);
})();
</script>
```

---

## 四、即刻短动态版（小红书/即刻通用）

### 小红书·种草版
```
🎬 惊呆了！输入一句话，AI 30秒生成完整短剧剧本！

最近发现了个宝藏工具「剧工厂」
作为一个短视频创作者，真的被惊艳到了

✨ 用起来有多爽？
- 输入一句梗概，比如「女主被绿后意外获得读心术」
- 选个类型：都市逆袭、悬疑、甜宠、古装、系统文
- 30秒后，一份完整的短剧剧本就出来了

📋 输出包含：
✔ 分镜表（每个镜头的时长、运镜、场景）
✔ 人物设定（性格、背景、关系）
✔ 完整对白剧本
✔ 下集钩子

💰 每天免费2次，够用了！
专业版39/月，工作室199/月

🔗 传送门：www.jugongchang.icu

#AI工具 #短剧 #短视频创作 #编剧神器 #独立开发者
```

### 即刻版
```
做了个 AI 短剧脚本生成器，30秒出成品。

输入一句话梗概 → 选择都市/古装/悬疑/甜宠 → 生成
输出：分镜表、人物表、完整剧本、下集钩子

免费版每天2次，专业版39/月。
网址 jugongchang.icu

欢迎体验，有任何意见直接甩过来。
```

---

## 五、待办清单（按优先级）

- [ ] **[你在做了] 去 V2EX 发帖**
- [ ] **提交百度搜索资源平台**（需要百度账号，几分钟能搞定）
- [ ] **提交 Product Hunt**（需要英文，我可以帮你翻译）
- [ ] **去即刻发一条带 #产品博物馆 的贴**
- [ ] **整理 GitHub README**（完善项目介绍，方便别人 star）
- [ ] **提交 sitemap 到 Google Search Console**（不需要账号注册，有 Google 账号就行）
- [ ] **去知乎回答相关提问** / 创建「有哪些好用的 AI 剧本工具」问题
