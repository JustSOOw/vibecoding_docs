# GitHub 仓库分析器 - Claude Skill

自动分析任何 GitHub 仓库，通过 **LLM 智能分析** 生成深度洞察报告。

## ✨ 核心特性

与直接浏览 GitHub 不同，本 Skill 会：
- 🧠 **智能归纳** - 从 README/Issues/Releases 提炼关键信息
- 📊 **健康评估** - 多维度评价项目状态
- 🔥 **热点分析** - 识别社区最关注的问题
- 💡 **使用建议** - 给出上手建议和注意事项

## 🚀 快速开始

### 在 Claude Code 中使用

直接告诉 Claude：
```
请使用 github-repo-analyzer 分析 https://github.com/facebook/react
```

Claude 会自动：
1. 获取仓库数据
2. 进行智能分析
3. 生成 HTML 分析报告

### 手动运行

```bash
cd .claude/skills/github-repo-analyzer

# 获取数据
uv run scripts/fetch_repo_info.py https://github.com/facebook/react

# 预处理（可选，用于精简大数据）
uv run scripts/prepare_for_analysis.py output/facebook_react/raw_data.json
```

## 📁 目录结构

```
github-repo-analyzer/
├── SKILL.md                    # Skill 定义（LLM 分析指引）
├── README.md                   # 本文件
├── pyproject.toml              # 依赖声明
├── .env.example                # Token 配置模板
├── scripts/
│   ├── fetch_repo_info.py      # 数据获取脚本
│   └── prepare_for_analysis.py # 数据预处理脚本
└── output/                     # 输出目录
    └── {owner}_{repo}/
        ├── raw_data.json       # 原始数据
        └── report.html         # 分析报告
```

## ⚙️ 环境管理

使用 [uv](https://github.com/astral-sh/uv) 自动管理依赖：
- **无需手动安装** - `uv run` 自动处理
- **环境隔离** - 不污染全局 Python
- **快速** - 比 pip 快 10-100 倍

## 🔑 配置 GitHub Token（可选）

为获得更高的 API 速率限制：

```bash
cp .env.example .env
# 编辑 .env，填入你的 GitHub Token
```

## 📄 License

MIT
