# Coze AI Agent - Vercel 部署

> 3分钟部署你的 AI 智能助手到 Vercel，完全免费！

## 🚀 快速开始

### 1. 上传到 GitHub

将此文件夹上传到你的 GitHub 仓库：

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/你的用户名/仓库名.git
git push -u origin main
```

或直接在 GitHub 网页上传文件。

### 2. 部署到 Vercel

1. 访问 https://vercel.com
2. 用 GitHub 账号登录
3. 点击 "New Project"
4. 选择你的仓库
5. 添加环境变量：
   - `COZE_API_TOKEN` = `你的Token`
   - `BOT_ID` = `你的BotID`
6. 点击 "Deploy"

### 3. 完成！

访问你的网站：`https://your-project.vercel.app`

## 📁 项目结构

```
.
├── api/
│   └── chat.py          # Python 后端 API
├── public/
│   └── index.html       # 前端聊天界面
├── requirements.txt     # Python 依赖
├── vercel.json         # Vercel 配置
└── README.md           # 本文档
```

## 🔧 配置

### 环境变量

在 Vercel 项目设置中配置：

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `COZE_API_TOKEN` | Coze API Token | `pat_xxx...` |
| `BOT_ID` | Coze Bot ID | `7529840362341515291` |

### 获取这些值

- **COZE_API_TOKEN**: 在 Coze 平台的 Personal Access Tokens 页面获取
- **BOT_ID**: 在智能体编辑页面的 URL 中找到

## 📚 详细文档

查看完整部署指南：`VERCEL_DEPLOYMENT_GUIDE.md`

## 🎯 功能特点

✅ 完全免费（Vercel 免费套餐）
✅ 全球 CDN 加速
✅ 自动 HTTPS
✅ 零运维
✅ 自动部署（推送代码即部署）

## 🔄 更新

修改代码后推送到 GitHub，Vercel 会自动重新部署。

## 🆘 需要帮助？

- 查看 `VERCEL_DEPLOYMENT_GUIDE.md` 获取详细步骤
- 访问 Vercel 文档：https://vercel.com/docs
- 查看 Coze 文档：https://www.coze.cn/docs

## 📄 许可证

MIT License
