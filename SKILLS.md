# Skills 功能手册

> 实时更新 · 最后更新：2026-05-14
>
> 本文档描述当前所有可用 Skills 及 Agent 的功能。新增或删除技能后应同步更新此文档。
>
> - **项目 Skills** → `CC/.claude/skills/` — 26 个，全部集中在本项目管理
> - **系统内置** → Claude Code 自带，无需文件

---

## 一、项目 Skills（27个）

### 文档办公

| Skill | 功能 | 触发关键词 |
|-------|------|-----------|
| **docx** | Word 文档创建/读取/编辑，支持目录、页码、批注、修订、模板、查找替换、图片插换 | .docx, Word, 报告, 备忘录, 信件 |
| **pdf** | PDF 全套操作：读取提取、合并拆分、旋转、水印、表单填写、加密解密、OCR 扫描件 | .pdf, PDF表单, 合并PDF |
| **pptx** | PPT 创建/编辑/合并/拆分，支持模板、布局、演讲者备注、pptxgenjs | .pptx, 幻灯片, deck, presentation |
| **xlsx** | Excel 表格创建/编辑/修复，公式、图表、格式转换(.csv/.tsv)、数据清理 | .xlsx, 电子表格, 表格数据 |
| **doc-coauthoring** | 结构化文档协作工作流：上下文收集→内容优化→读者测试三阶段 | 写文档, 提案, 技术规范 |

### 设计与视觉

| Skill | 功能 | 触发关键词 |
|-------|------|-----------|
| **frontend-design** | 高质量前端界面，强调独特设计美学、排版、动效，避免AI通用风格 | 网页, 落地页, 仪表盘, React组件, UI |
| **algorithmic-art** | p5.js 生成算法艺术（流场、粒子系统、噪声场），输出哲学.md + 交互.html | 生成艺术, 算法艺术, 创意编程 |
| **canvas-design** | 静态视觉设计（海报/艺术品），自带20+字体库，输出 .png/.pdf | 海报, 艺术品, 静态设计 |
| **chart-generator** | matplotlib + antv 图表生成（柱状/折线/饼图/散点/雷达等） | 图表, 可视化, 柱状图, 散点图 |
| **theme-factory** | 10套预设配色+字体主题，可应用于幻灯片/文档/报告/网页 | 美化, 主题, 配色 |

### 代码质量

| Skill | 功能 | 触发关键词 |
|-------|------|-----------|
| **code-reviewer** | 代码四维审查（安全漏洞/性能问题/最佳实践/质量评分），输出结构化报告 | 代码审查, 安全审计, PR审查 |
| **systematic-debugging** | 系统化调试：根因追踪→条件等待→深度防御，先诊断后修复 | bug, 测试失败, 异常行为 |

### 开发自动化

| Skill | 功能 | 触发关键词 |
|-------|------|-----------|
| **playwright-cli** | 浏览器自动化：测试、截图、表单填写、请求模拟、会话管理 | 浏览器测试, 网页自动化, Playwright |

### Python 生态

| Skill | 功能 | 触发关键词 |
|-------|------|-----------|
| **python-performance-optimization** | cProfile + memory profiler 性能剖析与优化 | Python慢, 性能优化, 瓶颈 |
| **python-testing-patterns** | pytest 测试策略：fixtures, mocking, TDD | 写测试, pytest, 测试套件 |

### OpenCLI 工具链

| Skill | 功能 | 触发关键词 |
|-------|------|-----------|
| **opencli-usage** | OpenCLI 总览：命令发现、通用参数、输出格式 | opencli能做什么 |
| **opencli-adapter-author** | 为新站点编写 OpenCLI 适配器（从侦查到字段解码到验证） | 写adapter, 新站点适配 |
| **opencli-autofix** | 自动修复损坏的 OpenCLI 适配器（追踪→补丁→验证→提issue） | opencli命令失败 |
| **opencli-browser** | 通过 opencli 操控真实浏览器（检查页面/填表/点击/数据提取） | 浏览器操作, 页面提取 |

### 政策资讯

| Skill | 功能 | 触发关键词 |
|-------|------|-----------|
| **daily-policy-briefing** | 三轨制每日政策简报：(A)时效快报-当日政策要闻+面试模拟 (B)政策专题-近1-3年重大风向 (C)省情专题-湖南固有省情。均含申论范文。每日9:03自动执行 | 每日简报, 申论素材, 面试热点, 省情, 十五五 |

### 搜索与查找

| Skill | 功能 | 触发关键词 |
|-------|------|-----------|
| **smart-search** | 基于 OpenCLI 的智能搜索路由器，支持指定网站、社交媒体、新闻、购物等 | 搜索, 查询, 查找信息 |
| **find-skills** | 帮助发现和安装开源 Agent Skills 生态中的技能 | 找skill, 有没有XX的skill |

### 学术研究

| Skill | 功能 | 触发关键词 |
|-------|------|-----------|
| **paper-search-download** | 学术论文搜索与下载，覆盖人文地理/社科全领域，支持中英文、影响因子查询 | 找论文, 搜文献, 下载论文 |
| **research-paper-writer** | 社科/人文核心期刊学术论文写作（人文地理、人口、经济、GIS等），中文核心期刊格式 | 写论文, 学术论文 |
| **html-report** | HTML演示级报告生成，全屏翻页式，面向人文地理学学术圈（导师汇报、学术会议、开题答辩） | 报告, 演示报告, HTML报告, 汇报 |

### 元工具

| Skill | 功能 | 触发关键词 |
|-------|------|-----------|
| **skill-creator** | 创建/改进/评测 Skills，含 eval 框架、benchmark、description 优化器 | 创建skill, 优化skill, 测试skill |

---

## 二、项目 Agents（2个）

| Agent | 功能 | 触发关键词 |
|-------|------|-----------|
| **civil-service-exam-hunan-advisor** | 湖南公务员考试全流程顾问（国考/省考/选调） | 湖南省考, 国考, 湖南选调 |
| **jiaoxi-exam-advisor** | 教师资格考试全流程指导 | 教资考试, 教师资格证 |

---

## 三、系统内置 Skills（无需文件，始终可用）

| Skill | 功能 |
|-------|------|
| **init** | 为新项目初始化 CLAUDE.md 代码库文档 |
| **review** | GitHub PR 审查工作流 |
| **security-review** | 当前分支变更的安全审查 |
| **simplify** | 审查已修改代码的重用性、质量和效率 |
| **claude-api** | Claude API / Anthropic SDK 开发调试（含 prompt caching、模型迁移） |
| **loop** | 按间隔循环运行命令或提示词 |
| **update-config** | 管理 settings.json（权限、环境变量、hooks） |
| **keybindings-help** | 自定义键盘快捷键和按键绑定 |
| **fewer-permission-prompts** | 扫描日志，为常用只读命令添加优先允许列表，减少权限弹窗 |
