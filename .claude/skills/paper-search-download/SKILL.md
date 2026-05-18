---
name: paper-search-download
description: 学术论文搜索与下载。当用户需要搜索论文、查找文献、下载 PDF、查询某领域/关键词/作者的研究论文、期刊影响因子或引用量时使用。支持中英文检索，覆盖人文地理、社会科学及所有学术领域。触发词包括"找论文"、"搜文献"、"下载论文"、"查论文"、"search papers"、"影响因子"、"引用量"等。若用户要做完整文献综述、系统综述或研究综合，优先使用 academic-research-suite。
---

# 学术论文搜索下载

## 核心流程

**首选方式：使用内置 Python 脚本**（自动聚合多源、去重、格式化）

```bash
# 关键词搜索
python scripts/search_papers.py "搜索词" [--author 作者] [--year 年份] [--oa-only] [--max 20] [--format table|detail|json]

# DOI 精确定位
python scripts/search_papers.py --doi "10.xxx/xxx"

# 输出 JSON 供后续处理
python scripts/search_papers.py "搜索词" --json 2>/dev/null
```

脚本自动完成：多源并行搜索 → 去重合并 → OA 补充验证 → 按引用量排序（OA 优先）

**备用方式：手动调用 API**（见下方"数据源策略"）

## 数据源策略

### 主力 API（免费、无需认证、直接调用）

**OpenAlex** — 首选，覆盖面最广，元数据最丰富
- 搜索端点：`https://api.openalex.org/works?search=QUERY&per_page=25&filter=...`
- 有 `cited_by_count`（引用量）、`fwci`（领域权重引用影响，即影响因子等价物）
- 有 `open_access.is_oa`、`primary_location.source.display_name`（期刊名）
- 支持 filter：`publication_year`、`language`、`type`、`authorships.author.id`、`is_oa`
- 作者搜索需先查作者 ID：`https://api.openalex.org/authors?search=NAME`
- 邮件参数 `mailto=USER_EMAIL` 可提高限速（礼貌池 10rps → 100rps）

**Crossref** — 适合按 DOI 精确查找、补充期刊信息
- 搜索端点：`https://api.crossref.org/works?query=QUERY&rows=25`
- 返回 `title`、`author`、`container-title`（期刊名）、`published-print`、`DOI`、`is-referenced-by-count`

**Semantic Scholar** — 补充 OA PDF 链接（有 `openAccessPdf` 字段）
- 搜索端点：`https://api.semanticscholar.org/graph/v1/paper/search?query=QUERY&limit=25&fields=title,authors,year,journal,citationCount,openAccessPdf,externalIds`
- 限速较严，容易 429，作为辅助源

**Unpaywall** — 判断某篇论文是否可免费获取（按 DOI 查询）
- 端点：`https://api.unpaywall.org/v2/DOI?email=YOUR_EMAIL`
- 返回 `is_oa`、`best_oa_location.url_for_pdf`
- 仅用于单篇 DOI 查询，不做批量搜索

### 辅助搜索（通过 WebSearch / WebFetch）

当 API 结果不足或用户特别要求时使用：

- **Google Scholar**：用 `WebSearch` 搜索 `site:scholar.google.com KEYWORDS`，或用 `"paper title" scholar` 查找具体论文
- **知网 (CNKI)**：用 `WebSearch` 搜索 `site:cnki.net KEYWORDS`，可获取摘要页元数据，PDF 通常需机构权限
- **Science Direct / Wiley / SpringerLink**：通过 WebSearch 搜索 `"title" site:sciencedirect.com` 等，可获取页面元数据

### 各源能力对比

| 功能 | OpenAlex | Crossref | Semantic Scholar | Unpaywall | WebSearch |
|------|----------|----------|------------------|-----------|-----------|
| 关键词搜索 | [Y] 强 | [Y] | [Y] | [N] | [Y] |
| 引用量 | [Y] | [Y] | [Y] | [N] | [N] |
| 影响因子 | [Y] fwci | [N] | [N] | [N] | [N] |
| OA 判断 | [Y] | [N] | [Y] | [Y] 最准 | [N] |
| PDF 链接 | [N] | [N] | [Y] | [Y] | [Y] |
| 中文论文 | [?] 有限 | [?] 有限 | [N] | [N] | [Y] 知网 |

## 搜索命令模板

### 1. 关键词/领域搜索（最常用）

```bash
curl -s "https://api.openalex.org/works?search=URL_ENCODED_QUERY&per_page=25&filter=language:en,type:article&mailto=user@domain.com"
```

如果用户搜索中文，先翻译为英文搜 OpenAlex，同时用 WebSearch 搜知网。

### 2. 按作者搜索

先查作者 ID：
```bash
curl -s "https://api.openalex.org/authors?search=AUTHOR_NAME&mailto=user@domain.com"
```
再用 `filter=authorships.author.id:AUTHOR_ID` 搜作品。

### 3. 按 DOI 精确查找

```bash
curl -s "https://api.openalex.org/works/DOI_URL_ENCODED?mailto=user@domain.com"
curl -s "https://api.unpaywall.org/v2/DOI?email=user@domain.com"
```

### 4. 补充 Semantic Scholar

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=QUERY&limit=10&fields=title,authors,year,journal,citationCount,openAccessPdf,externalIds"
```

### 5. 知网/中文文献补充

用 WebSearch 工具搜索：`site:cnki.net 关键词`，然后用 WebFetch 获取搜索结果页的元数据。

## 输出格式

搜索结果必须以这个表格格式展示（每条结果一行）：

```
| # | 标题 | 第一作者 | 年份 | 期刊 | 引用 | OA | 影响因子 |
|---|---|---|---|---|---|---|---|
| 1 | Title | Author | 2024 | J. of Geography | 156 | [OA] | 2.3 |
| 2 | Title | Author | 2023 | Nature Geoscience | 89 | [X] | 8.5 |
```

每篇论文下方附 DOI 链接。OA 列用 [OA]（可获取）/ [X]（付费）/ [?]（不确定）。

搜索后，主动询问用户要下载哪几篇。

## PDF 下载流程

按优先级尝试获取 PDF：

1. **Unpaywall PDF**：若 `is_oa=true` 且 `best_oa_location.url_for_pdf` 非空，直接用 curl 下载
2. **Semantic Scholar openAccessPdf**：若该字段有 url，直接下载
3. **预印本**：检查 `oa_locations` 中有无 arXiv 等预印本链接
4. **机构仓储**：检查 Unpaywall `oa_locations` 中的 repository 链接

下载命令（按顺序尝试，直到成功）：

**1. 带 User-Agent 的 curl（绕过基础 bot 拦截）：**
```bash
curl -L -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
     -o "DOWNLOAD_DIR/FILENAME.pdf" "PDF_URL"
```

**2. 逐级尝试替代源：**
- 若 MDPI/Elsevier 等屏蔽直接 PDF：改用 Unpaywall 返回的仓储链接（arXiv、PubMed Central、机构仓储）
- 查看 Semantic Scholar `openAccessPdf.url`
- 如都失败，尝试通过 DOI 跳转：`curl -L -H "User-Agent: ..." -o "FILE.pdf" "https://doi.org/DOI"`

**3. 检查下载结果：**
- 有效 PDF 以 `%PDF` 开头（文件 > 10KB）
- 若文件 < 10KB 或以 `<HTML` 开头，说明被拦截，需换策略
```bash
head -c 4 "DOWNLOAD_DIR/FILENAME.pdf"  # 应显示 %PDF
```

### 文件命名规则

`作者姓氏_年份_标题前20字符.pdf`（去除特殊字符，空格替换为下划线）

### 下载目录

- 默认：当前工作目录下的 `downloads/papers/`
- 用户可指定其他目录

## 中文搜索特别说明

用户是人文地理专业研究生，搜索词可能为中文：
- 英文 API（OpenAlex/Crossref/Semantic Scholar）：将中文关键词翻译为英文搜索
- 知网：直接用中文关键词通过 WebSearch 搜索
- 结果优先展示 OA 可获取的论文，但也列出付费论文供参考
- 如果用户特别强调知网，专注于 WebSearch 知网搜索

## 注意事项

- 每次搜索 OpenAlex 时添加 `mailto=USER_EMAIL` 参数以提高限速，用 `cc-research@example.com` 作为默认邮箱
- Semantic Scholar 容易 429，不要连续调用，只在需要 PDF 时才查
- 始终先展示结果让用户选择，不要自动下载所有论文
- 如果所有 API 都失败，降级使用 WebSearch
- PDF 下载后向用户报告文件路径和大小
- 如果论文无法获取，列出可能的替代途径（预印本、ResearchGate、作者主页等）

