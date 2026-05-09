#!/usr/bin/env python3
"""
每日备考简报 — HTML 阅读器构建脚本
读取 daily/ 和 policy-review/ 中的 Markdown 文件，生成精美的单页阅读器。
支持浏览器直接打开，自带打印样式（打印即 PDF 导出）。
"""
import os
import re
import json
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DAILY_DIR = SCRIPT_DIR / "A-时效快报"
REVIEW_DIR = SCRIPT_DIR / "B-政策专题"
HUNAN_REVIEW_DIR = SCRIPT_DIR / "C-省情专题"
OUTPUT_FILE = SCRIPT_DIR / "备考日报.html"

def parse_md_sections(text):
    """将 Markdown 文本按 ## 标题拆分为段落，保留格式"""
    lines = text.split("\n")
    sections = []
    current_title = ""
    current_lines = []
    in_code_block = False

    for line in lines:
        if line.startswith("```"):
            in_code_block = not in_code_block
            current_lines.append(line)
            continue

        if not in_code_block and line.startswith("## "):
            if current_title or current_lines:
                sections.append((current_title, "\n".join(current_lines).strip()))
            current_title = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_title or current_lines:
        sections.append((current_title, "\n".join(current_lines).strip()))

    return sections

def process_inline(text):
    """处理行内 Markdown 语法：粗体、链接、代码、图片"""
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" style="max-width:100%;border-radius:6px;margin:8px 0;">', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text

def md_to_html(text):
    """简单的 Markdown→HTML 转换（覆盖简报中用到的语法）"""
    lines = text.split("\n")
    result = []
    in_table = False
    in_ul = False
    in_ol = False
    table_rows = []
    in_blockquote = False
    blockquote_lines = []

    def flush_table():
        nonlocal in_table, table_rows
        if not table_rows:
            return ""
        html = '<div class="table-wrapper"><table>\n'
        for i, row in enumerate(table_rows):
            tag = "th" if i == 0 else "td"
            cells = [process_inline(c.strip()) for c in row.split("|")[1:-1]]
            html += "<tr>\n" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "\n</tr>\n"
        html += "</table></div>\n"
        table_rows = []
        in_table = False
        return html

    def flush_ul():
        nonlocal in_ul
        in_ul = False
        return "</ul>\n"

    def flush_ol():
        nonlocal in_ol
        in_ol = False
        return "</ol>\n"

    def flush_blockquote():
        nonlocal in_blockquote, blockquote_lines
        content = "<br>".join(blockquote_lines)
        blockquote_lines = []
        in_blockquote = False
        return f'<blockquote>{content}</blockquote>\n'

    for line in lines:
        # 空行处理
        if not line.strip():
            if in_ul:
                result.append(flush_ul())
            if in_ol:
                result.append(flush_ol())
            if in_blockquote:
                result.append(flush_blockquote())
            if in_table and table_rows:
                result.append(flush_table())
            continue

        # 代码块
        if line.startswith("```"):
            continue

        # 表格行
        if line.strip().startswith("|") and line.strip().endswith("|"):
            if not in_table:
                in_table = True
            if not re.match(r"^\|[\s\-:|\s]+\|$", line.strip()):  # 跳过分隔行
                table_rows.append(line.strip())
            continue

        # 标题
        if line.startswith("### "):
            if in_table:
                result.append(flush_table())
            result.append(f'<h3>{line[4:].strip()}</h3>')
            continue
        if line.startswith("#### "):
            if in_table:
                result.append(flush_table())
            result.append(f'<h4>{line[5:].strip()}</h4>')
            continue

        # 引用块
        if line.startswith("> "):
            if not in_blockquote:
                in_blockquote = True
            content = process_inline(line[2:].strip())
            blockquote_lines.append(content)
            continue

        # 水平线
        if line.strip() == "---":
            if in_table:
                result.append(flush_table())
            result.append('<hr>')
            continue

        # 无序列表
        if re.match(r"^- ", line.strip()):
            if not in_ul:
                in_ul = True
                result.append('<ul>')
            content = process_inline(line.strip()[2:])
            result.append(f'<li>{content}</li>')
            continue

        # 有序列表
        if re.match(r"^\d+\. ", line.strip()):
            if not in_ol:
                in_ol = True
                result.append('<ol>')
            content = process_inline(re.sub(r'^\d+\. ', '', line.strip()))
            result.append(f'<li>{content}</li>')
            continue

        # 普通段落
        if in_table:
            result.append(flush_table())
        if in_blockquote:
            result.append(flush_blockquote())

        result.append(f'<p>{process_inline(line.strip())}</p>')

    # 收尾
    if in_table:
        result.append(flush_table())
    if in_ul:
        result.append(flush_ul())
    if in_ol:
        result.append(flush_ol())
    if in_blockquote:
        result.append(flush_blockquote())

    return "\n".join(result)

def get_a_track_files():
    """获取 A 轨所有快报文件，按日期排序"""
    files = []
    if DAILY_DIR.exists():
        for f in DAILY_DIR.glob("*.md"):
            match = re.match(r"(\d{4}-\d{2}-\d{2})", f.stem)
            if match:
                files.append((match.group(1), str(f)))
    files.sort(key=lambda x: x[0], reverse=True)  # 按日期倒序（近→远）
    return files

def get_b_track_files():
    """获取 B 轨所有专题文件，按序号排序"""
    files = []
    if REVIEW_DIR.exists():
        for f in REVIEW_DIR.glob("*.md"):
            match = re.match(r"(\d+)-(.+)", f.stem)
            if match:
                files.append((int(match.group(1)), match.group(2), str(f)))
    files.sort(key=lambda x: x[0])
    return files

def get_c_track_files():
    """获取 C 轨所有省情专题文件，按序号排序"""
    files = []
    if HUNAN_REVIEW_DIR.exists():
        for f in HUNAN_REVIEW_DIR.glob("*.md"):
            match = re.match(r"(\d+)-(.+)", f.stem)
            if match:
                files.append((int(match.group(1)), match.group(2), str(f)))
    files.sort(key=lambda x: x[0])
    return files

def build_article_html(title, body_html, meta_info=""):
    """构建单篇文章的 HTML"""
    return f"""
    <article>
        <header class="article-header">
            <h1 class="article-title">{title}</h1>
            {f'<div class="article-meta">{meta_info}</div>' if meta_info else ''}
        </header>
        <div class="article-body">
            {body_html}
        </div>
    </article>
    """

def build_reader():
    """主构建函数"""
    a_files = get_a_track_files()
    b_files = get_b_track_files()
    c_files = get_c_track_files()

    # 构建导航列表
    nav_a_items = ""
    for date_str, path in a_files:
        nav_a_items += f'<li><a href="#a-{date_str}" class="nav-a" data-date="{date_str}">{date_str} 快报</a></li>\n'

    nav_b_items = ""
    for num, name, path in b_files:
        display_name = name.replace("-", " ")
        nav_b_items += f'<li><a href="#b-{num:02d}" class="nav-b" data-id="{num:02d}">{num:02d}. {display_name}</a></li>\n'

    nav_c_items = ""
    for num, name, path in c_files:
        display_name = name.replace("-", " ")
        nav_c_items += f'<li><a href="#c-{num:02d}" class="nav-c" data-id="{num:02d}">{num:02d}. {display_name}</a></li>\n'

    # 构建文章内容
    articles_html = ""

    # A 轨
    for date_str, path in a_files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            # 提取标题（第一行 #）
            first_line = text.split("\n")[0]
            title = first_line.lstrip("# ").strip() if first_line.startswith("#") else date_str

            # 提取标签行
            tags = ""
            tag_match = re.search(r'> 今日.*?#(.+)', text[:200])
            if tag_match:
                tags = " | " + tag_match.group(1).replace("#", "")

            body_html = md_to_html(text)
            articles_html += f'<section id="a-{date_str}" class="article-section">\n'
            articles_html += build_article_html(title, body_html, f"📅 {date_str}{tags}")
            articles_html += '</section>\n'
        except Exception as e:
            articles_html += f'<p>Error loading {path}: {e}</p>\n'

    # B 轨
    for num, name, path in b_files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            first_line = text.split("\n")[0]
            title = first_line.lstrip("# ").strip() if first_line.startswith("#") else name

            # 提取重要度
            importance = ""
            imp_match = re.search(r'考试重要度：(★+).*覆盖：(.*)', text[:300])
            if imp_match:
                importance = f"重要度 {imp_match.group(1)} | 覆盖 {imp_match.group(2)}"

            body_html = md_to_html(text)
            articles_html += f'<section id="b-{num:02d}" class="article-section">\n'
            articles_html += build_article_html(title, body_html, importance)
            articles_html += '</section>\n'
        except Exception as e:
            articles_html += f'<p>Error loading {path}: {e}</p>\n'

    # 构建完整 HTML
    # C 轨
    for num, name, path in c_files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            first_line = text.split("\n")[0]
            title = first_line.lstrip("# ").strip() if first_line.startswith("#") else name

            importance = ""
            imp_match = re.search(r'考试重要度：(★+).*覆盖：(.*)', text[:300])
            if imp_match:
                importance = f"重要度 {imp_match.group(1)} | 覆盖 {imp_match.group(2)}"

            body_html = md_to_html(text)
            articles_html += f'<section id="c-{num:02d}" class="article-section">\n'
            articles_html += build_article_html(title, body_html, importance)
            articles_html += '</section>\n'
        except Exception as e:
            articles_html += f'<p>Error loading {path}: {e}</p>\n'

    # 统计
    a_count = len(a_files)
    b_count = len(b_files)
    c_count = len(c_files)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>备考日报 · 阅读器</title>
<style>
:root {{
    --bg: #fdfaf6;
    --card-bg: #ffffff;
    --text: #2d2d2d;
    --text-secondary: #6b6b6b;
    --accent: #b5343a;
    --accent-light: #f8e5e6;
    --blue: #1a5276;
    --blue-light: #e8f0f6;
    --green: #1e7e5c;
    --green-light: #e6f4ef;
    --gold: #b8860b;
    --gold-light: #fef9e7;
    --border: #e8e3dc;
    --shadow: 0 2px 12px rgba(0,0,0,0.06);
    --radius: 10px;
    --font-cn: "PingFang SC", "Microsoft YaHei", "Noto Sans SC", "Hiragino Sans GB", -apple-system, sans-serif;
    --font-mono: "SF Mono", "Fira Code", "Cascadia Code", monospace;
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
    font-family: var(--font-cn);
    background: var(--bg);
    color: var(--text);
    line-height: 1.85;
    display: flex;
    min-height: 100vh;
}}

/* ======== 侧边栏 ======== */
.sidebar {{
    position: fixed;
    top: 0; left: 0;
    width: 260px;
    height: 100vh;
    background: #fff;
    border-right: 1px solid var(--border);
    padding: 28px 20px;
    overflow-y: auto;
    z-index: 100;
    box-shadow: 2px 0 16px rgba(0,0,0,0.04);
}}

.sidebar-header {{
    margin-bottom: 28px;
    padding-bottom: 20px;
    border-bottom: 1px solid var(--border);
}}

.sidebar-header h2 {{
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: 0.03em;
}}

.sidebar-header .stats {{
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-top: 6px;
}}

.sidebar-section {{
    margin-bottom: 24px;
}}

.sidebar-section h3 {{
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-secondary);
    margin-bottom: 10px;
    padding-left: 4px;
}}

.sidebar-section ul {{
    list-style: none;
}}

.sidebar-section li {{
    margin-bottom: 2px;
}}

.sidebar-section a {{
    display: block;
    padding: 7px 12px;
    border-radius: 6px;
    font-size: 0.86rem;
    color: var(--text);
    text-decoration: none;
    transition: all 0.15s;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

.sidebar-section a:hover {{
    background: #f5f2ed;
    color: var(--accent);
}}

.sidebar-section a.active {{
    background: var(--accent-light);
    color: var(--accent);
    font-weight: 600;
}}

/* ======== 主内容区 ======== */
.main {{
    margin-left: 260px;
    flex: 1;
    padding: 32px 40px 80px;
    max-width: 900px;
}}

/* ======== 顶部工具栏 ======== */
.toolbar {{
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-bottom: 28px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border);
}}

.btn {{
    padding: 8px 18px;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: #fff;
    font-size: 0.85rem;
    font-family: var(--font-cn);
    cursor: pointer;
    transition: all 0.15s;
    color: var(--text);
    text-decoration: none;
}}

.btn:hover {{
    background: #f5f2ed;
    border-color: #ccc;
}}

.btn-print {{
    background: var(--accent);
    color: #fff;
    border-color: var(--accent);
}}

.btn-print:hover {{
    background: #a02e34;
}}

/* ======== 文章区 ======== */
.article-section {{
    margin-bottom: 48px;
}}

.article-header {{
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 2px solid var(--accent);
}}

.article-title {{
    font-size: 1.7rem;
    font-weight: 800;
    line-height: 1.3;
    color: #1a1a1a;
    letter-spacing: 0.02em;
}}

.article-meta {{
    margin-top: 8px;
    font-size: 0.85rem;
    color: var(--text-secondary);
}}

/* ======== 正文排版 ======== */
.article-body h3 {{
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--accent);
    margin: 28px 0 12px;
    padding-left: 14px;
    border-left: 4px solid var(--accent);
}}

.article-body h4 {{
    font-size: 1.02rem;
    font-weight: 700;
    color: var(--blue);
    margin: 20px 0 8px;
}}

.article-body p {{
    margin: 8px 0;
    font-size: 0.95rem;
    text-align: justify;
}}

.article-body strong {{
    color: #1a1a1a;
    font-weight: 700;
}}

.article-body a {{
    color: var(--blue);
    text-decoration: none;
    border-bottom: 1px dotted var(--blue);
}}

.article-body a:hover {{
    border-bottom-style: solid;
}}

.article-body blockquote {{
    margin: 14px 0;
    padding: 12px 18px;
    background: var(--blue-light);
    border-left: 4px solid var(--blue);
    border-radius: 0 6px 6px 0;
    font-size: 0.92rem;
    color: #2c3e50;
}}

.article-body ul, .article-body ol {{
    margin: 10px 0;
    padding-left: 24px;
}}

.article-body li {{
    margin: 4px 0;
    font-size: 0.92rem;
}}

.article-body hr {{
    border: none;
    border-top: 1px dashed var(--border);
    margin: 24px 0;
}}

/* ======== 表格 ======== */
.table-wrapper {{
    overflow-x: auto;
    margin: 14px 0;
    -webkit-overflow-scrolling: touch;
}}

.article-body table {{
    width: 100%;
    min-width: 360px;
    border-collapse: collapse;
    font-size: 0.88rem;
    box-shadow: var(--shadow);
    border-radius: 8px;
    overflow: hidden;
}}

.article-body th {{
    background: #f7f3ed;
    padding: 10px 14px;
    text-align: left;
    font-weight: 700;
    font-size: 0.84rem;
    color: #4a4a4a;
    border-bottom: 2px solid var(--border);
    white-space: nowrap;
}}

.article-body td {{
    padding: 9px 14px;
    border-bottom: 1px solid #f0ece6;
    vertical-align: top;
    overflow-wrap: break-word;
    word-break: break-word;
}}

.article-body tr:last-child td {{
    border-bottom: none;
}}

.article-body tr:hover td {{
    background: #fdfaf6;
}}

.article-body td a {{
    color: var(--blue);
    text-decoration: none;
    border-bottom: 1px dotted var(--blue);
}}

.article-body td a:hover {{
    border-bottom-style: solid;
}}

.article-body td strong {{
    color: #1a1a1a;
    font-weight: 700;
}}

/* ======== 代码 ======== */
.article-body code {{
    background: #f4f1ec;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: var(--font-mono);
    font-size: 0.85em;
    color: var(--accent);
}}

/* ======== 回到顶部 ======== */
.back-to-top {{
    position: fixed;
    bottom: 30px;
    right: 30px;
    width: 44px;
    height: 44px;
    background: var(--accent);
    color: #fff;
    border: none;
    border-radius: 50%;
    font-size: 1.2rem;
    cursor: pointer;
    box-shadow: 0 3px 12px rgba(181,52,58,0.3);
    display: none;
    z-index: 200;
    transition: all 0.2s;
}}

.back-to-top:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(181,52,58,0.4);
}}

/* ======== 空状态 ======== */
.empty-state {{
    text-align: center;
    padding: 80px 20px;
    color: var(--text-secondary);
}}

.empty-state h2 {{
    font-size: 1.5rem;
    margin-bottom: 12px;
}}

/* ======== 打印样式 ======== */
@media print {{
    .sidebar, .toolbar, .back-to-top {{
        display: none !important;
    }}

    .main {{
        margin-left: 0;
        padding: 20px 0;
        max-width: 100%;
    }}

    body {{
        background: #fff;
        font-size: 11pt;
    }}

    .article-title {{
        font-size: 18pt;
        page-break-before: always;
    }}

    .article-section:first-of-type .article-title {{
        page-break-before: avoid;
    }}

    .article-body a {{
        color: inherit;
        border-bottom: none;
    }}

    .article-body a::after {{
        content: " (" attr(href) ")";
        font-size: 0.8em;
        color: #999;
    }}

    .table-wrapper {{
        overflow-x: visible;
    }}

    .article-body table {{
        box-shadow: none;
        font-size: 10pt;
    }}

    .article-body th {{
        background: #f0f0f0;
        color: #000;
    }}

    .article-body td a::after {{
        content: " (" attr(href) ")";
        font-size: 0.75em;
    }}
}}

/* ======== 移动端响应 ======== */
@media (max-width: 768px) {{
    .sidebar {{
        display: none;
    }}

    .main {{
        margin-left: 0;
        padding: 16px;
    }}

    .article-title {{
        font-size: 1.3rem;
    }}

    .article-body table {{
        font-size: 0.8rem;
        min-width: 300px;
    }}

    .article-body th,
    .article-body td {{
        padding: 7px 10px;
    }}
}}
</style>
</head>
<body>

<!-- 侧边栏 -->
<nav class="sidebar">
    <div class="sidebar-header">
        <h2>备考日报</h2>
        <div class="stats">A 轨 {a_count} 篇 · B 轨 {b_count} 篇 · C 轨 {c_count} 篇</div>
    </div>

    <div class="sidebar-section">
        <h3>时效快报</h3>
        <ul>
            {nav_a_items if nav_a_items else '<li style="color:#999;font-size:0.82rem;padding:6px 12px;">暂无</li>'}
        </ul>
    </div>

    <div class="sidebar-section">
        <h3>政策专题</h3>
        <ul>
            {nav_b_items if nav_b_items else '<li style="color:#999;font-size:0.82rem;padding:6px 12px;">暂无</li>'}
        </ul>
    </div>

    <div class="sidebar-section">
        <h3>湖南省情</h3>
        <ul>
            {nav_c_items if nav_c_items else '<li style="color:#999;font-size:0.82rem;padding:6px 12px;">暂无</li>'}
        </ul>
    </div>
</nav>

<!-- 主内容 -->
<main class="main">
    <div class="toolbar">
        <button class="btn" onclick="window.print()" title="打印当前页面或保存为 PDF">打印 / 导出 PDF</button>
    </div>

    <div id="content">
        {articles_html if articles_html else '<div class="empty-state"><h2>暂无简报</h2><p>等待每日自动生成中...</p></div>'}
    </div>
</main>

<button class="back-to-top" id="backToTop" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">↑</button>

<script>
// 回到顶部按钮
const btn = document.getElementById('backToTop');
window.addEventListener('scroll', () => {{
    btn.style.display = window.scrollY > 400 ? 'block' : 'none';
}});

// 侧边栏激活状态（滚动监听）
const sections = document.querySelectorAll('.article-section');
const navLinks = document.querySelectorAll('.sidebar-section a');

function updateActiveLink() {{
    let current = '';
    sections.forEach(section => {{
        const top = section.getBoundingClientRect().top;
        if (top < 120) {{
            current = section.id;
        }}
    }});
    navLinks.forEach(link => {{
        link.classList.remove('active');
        const target = link.getAttribute('href')?.replace('#', '');
        if (target === current) {{
            link.classList.add('active');
        }}
    }});
}}

window.addEventListener('scroll', updateActiveLink);

// 打印当前文章
function printArticle(id) {{
    const section = document.getElementById(id);
    if (!section) return;
    const win = window.open('', '_blank', 'width=800,height=600');
    win.document.write('<html><head><title>打印</title>');
    win.document.write('<link rel="stylesheet" href="' + window.location.href + '">');
    win.document.write('</head><body>');
    win.document.write(section.outerHTML);
    win.document.write('</body></html>');
    win.document.close();
    setTimeout(() => win.print(), 300);
}}
</script>

</body>
</html>"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[OK] Generated {OUTPUT_FILE}")
    print(f"     A-track: {a_count} articles")
    print(f"     B-track: {b_count} articles")
    print(f"     C-track: {c_count} articles")

if __name__ == "__main__":
    build_reader()
