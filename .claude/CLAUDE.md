# CC 项目 — Claude Code 自定义配置管理

本项目集中管理所有 Claude Code 的非内置扩展：Skills、Agents、插件、脚本等。

## 项目结构

```
CC/
├── .claude/
│   ├── skills/          ← 所有 Skills（26个）
│   ├── agents/          ← 自定义 Agents（公务员考试、教资考试顾问）
│   ├── settings.local.json  ← 项目级权限与 hooks
│   ├── scheduled_tasks.json ← 定时任务（每日简报等）
│   └── CLAUDE.md
├── plugins/             ← 第三方 marketplace 插件
├── statusline.py        ← 自定义终端状态栏
├── SKILLS.md            ← Skills 功能手册（实时更新）
├── html-report-workspace/ ← HTML 报告工作区
├── 备考日报/            ← 公务员考试备考日报输出
├── downloads/           ← 论文下载缓存（paper-search-download）
└── Claude-Code-指令参考.md ← Claude Code 指令速查
```

## 工作流

1. **每日简报**：定时自动触发 `daily-policy-briefing`
2. **备考资料**：输出到 `备考日报/` 目录
3. **学术写作**：`paper-search-download` + `research-paper-writer` 覆盖论文全流程
4. **可视化报告**：`html-report` 生成翻页式演示报告
