#!/usr/bin/env python3
"""
学术论文搜索工具 - 聚合 OpenAlex、Crossref、Semantic Scholar 的搜索结果。
用法:
  python search_papers.py "搜索词" [--author "作者名"] [--year 2023] [--oa-only] [--max 20] [--source openalex|all]
  python search_papers.py --doi "10.xxx/xxx"  # 精确查找单篇
"""
import json
import sys
import os

import urllib.request
import urllib.parse
import urllib.error
import time
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed

# Windows 控制台 UTF-8 编码兼容
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SSL_CONTEXT = ssl.create_default_context()
EMAIL = os.environ.get("PAPER_SEARCH_EMAIL", "cc-research@users.noreply.github.com")

def fetch_json(url, retries=2, delay=1.0):
    """获取 JSON，带重试和频率限制处理"""
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": f"PaperSearchBot/1.0 (mailto:{EMAIL})"})
            with urllib.request.urlopen(req, context=SSL_CONTEXT, timeout=15) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries:
                time.sleep(delay * (attempt + 1))
                continue
            return None
        except Exception:
            if attempt < retries:
                time.sleep(delay)
                continue
            return None

def search_openalex(query, max_results=20, year=None, oa_only=False, author_id=None):
    """搜索 OpenAlex"""
    params = {
        "search": query,
        "per_page": max_results,
        "filter": "type:article",
        "mailto": EMAIL
    }
    filters = []
    if year:
        filters.append(f"publication_year:{year}")
    if oa_only:
        filters.append("is_oa:true")
    if author_id:
        filters.append(f"authorships.author.id:{author_id}")
    if filters:
        params["filter"] = ",".join(filters)

    url = f"https://api.openalex.org/works?{urllib.parse.urlencode(params)}"
    data = fetch_json(url)
    if not data or "results" not in data:
        return []
    return data["results"]

def search_crossref(query, max_results=20):
    """搜索 Crossref"""
    url = f"https://api.crossref.org/works?query={urllib.parse.quote(query)}&rows={max_results}"
    data = fetch_json(url)
    if not data or "message" not in data or "items" not in data["message"]:
        return []
    return data["message"]["items"]

def search_semantic_scholar(query, max_results=10):
    """搜索 Semantic Scholar（限速严，数量少）"""
    fields = "title,authors,year,journal,citationCount,openAccessPdf,externalIds"
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={urllib.parse.quote(query)}&limit={max_results}&fields={fields}"
    data = fetch_json(url, retries=1)
    if not data or "data" not in data:
        return []
    return data["data"]

def resolve_author_id(name):
    """查找作者 OpenAlex ID"""
    url = f"https://api.openalex.org/authors?search={urllib.parse.quote(name)}&per_page=3&mailto={EMAIL}"
    data = fetch_json(url)
    if not data or "results" not in data or not data["results"]:
        return None
    return data["results"][0]["id"]

def check_unpaywall(doi):
    """检查单篇论文的 OA 状态和 PDF 链接"""
    url = f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email={EMAIL}"
    data = fetch_json(url)
    if not data:
        return {"is_oa": False, "pdf_url": None}
    pdf = None
    loc = data.get("best_oa_location") or {}
    if loc.get("url_for_pdf"):
        pdf = loc["url_for_pdf"]
    return {
        "is_oa": data.get("is_oa", False),
        "oa_status": data.get("oa_status", "closed"),
        "pdf_url": pdf,
        "journal_name": data.get("journal_name", ""),
    }

def extract_openalex_info(work):
    """从 OpenAlex 结果中提取统一格式"""
    title = work.get("title", work.get("display_name", "N/A"))
    authors = work.get("authorships", [])
    first_author = authors[0]["author"]["display_name"] if authors else "N/A"
    year = work.get("publication_year", "N/A")
    source = work.get("primary_location", {}) or {}
    journal = (source.get("source", {}) or {}).get("display_name", "N/A")
    cited = work.get("cited_by_count", 0)
    fwci = work.get("fwci", None)
    oa_info = work.get("open_access", {})
    is_oa = oa_info.get("is_oa", False)
    doi = work.get("doi", "")
    doi_clean = doi.replace("https://doi.org/", "") if doi else ""

    # 尝试从 Semantic Scholar 中找 OA PDF（若 OpenAlex 无）
    pdf_url = None
    if is_oa:
        primary = source
        if primary.get("pdf_url"):
            pdf_url = primary["pdf_url"]

    return {
        "title": title[:120],
        "first_author": first_author,
        "year": year,
        "journal": journal,
        "cited_by": cited,
        "fwci": round(fwci, 2) if fwci else None,
        "is_oa": is_oa,
        "oa_status": oa_info.get("oa_status", "closed"),
        "doi": doi_clean,
        "pdf_url": pdf_url,
        "source": "OpenAlex"
    }

def extract_crossref_info(item):
    """从 Crossref 结果提取信息"""
    title = item.get("title", ["N/A"])[0] if item.get("title") else "N/A"
    author_list = item.get("author", [])
    first_author = f"{author_list[0].get('given', '')} {author_list[0].get('family', '')}".strip() if author_list else "N/A"
    pub = item.get("published-print", {}) or item.get("created", {})
    year = pub.get("date-parts", [[None]])[0][0] if pub.get("date-parts") else "N/A"
    journal = item.get("container-title", ["N/A"])[0] if item.get("container-title") else "N/A"
    cited = item.get("is-referenced-by-count", 0)
    doi = item.get("DOI", "")

    return {
        "title": title[:120],
        "first_author": first_author,
        "year": year,
        "journal": journal,
        "cited_by": cited,
        "fwci": None,
        "is_oa": None,
        "oa_status": "unknown",
        "doi": doi,
        "pdf_url": None,
        "source": "Crossref"
    }

def extract_s2_info(paper):
    """从 Semantic Scholar 结果提取信息"""
    authors = paper.get("authors", [])
    first_author = authors[0].get("name", "N/A") if authors else "N/A"
    journal_info = paper.get("journal") or {}
    journal = journal_info.get("name", "N/A") if journal_info else "N/A"
    oa = paper.get("openAccessPdf") or {}
    external = paper.get("externalIds") or {}
    doi = external.get("DOI", "")

    return {
        "title": (paper.get("title") or "N/A")[:120],
        "first_author": first_author,
        "year": paper.get("year", "N/A"),
        "journal": journal,
        "cited_by": paper.get("citationCount", 0),
        "fwci": None,
        "is_oa": bool(oa.get("url")),
        "oa_status": "oa" if oa.get("url") else "unknown",
        "doi": doi,
        "pdf_url": oa.get("url"),
        "source": "SemanticScholar"
    }

def merge_results(results_list, max_total=25):
    """合并去重（按 DOI 或 标题+第一作者），保持来源多样性"""
    seen = set()
    merged = []
    for paper in results_list:
        doi = paper.get("doi", "")
        if doi:
            key = doi
        else:
            # 无 DOI 时用标题+第一作者去重，比纯标题更精确
            title = paper.get("title", "")[:80]
            authors = paper.get("authors", [])
            first_author = authors[0] if authors else ""
            key = f"{title}|{first_author}"
        if key in seen:
            continue
        seen.add(key)
        merged.append(paper)
        if len(merged) >= max_total:
            break
    return merged

def enrich_oa_status(results, max_check=5):
    """为没有 OA 信息的论文通过 Unpaywall 补充"""
    to_check = [p for p in results if p.get("is_oa") in (None, False) and p.get("doi")]
    for paper in to_check[:max_check]:
        info = check_unpaywall(paper["doi"])
        if info["is_oa"]:
            paper["is_oa"] = True
            paper["oa_status"] = info["oa_status"]
            if info["pdf_url"]:
                paper["pdf_url"] = info["pdf_url"]
        elif paper.get("is_oa") is None:
            paper["is_oa"] = False
    return results

def format_results_table(results):
    """格式化输出为 Markdown 表格"""
    lines = []
    lines.append("| # | 标题 | 第一作者 | 年份 | 期刊 | 引用 | OA | FWCI/IF |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for i, p in enumerate(results, 1):
        oa_icon = "[OA]" if p.get("is_oa") else ("[X]" if p.get("is_oa") is False else "[?]")
        title = p["title"][:60].replace("|", "/")
        author = p["first_author"][:20].replace("|", "/")
        journal = (p.get("journal") or "N/A")[:25].replace("|", "/")
        fwci = f"{p['fwci']:.1f}" if p.get("fwci") else "-"
        lines.append(
            f"| {i} | {title} | {author} | {p['year']} | {journal} | {p['cited_by']} | {oa_icon} | {fwci} |"
        )
        doi_str = p.get("doi", "")
        src = p.get("source", "")
        if doi_str:
            lines.append(f"  > DOI: [{doi_str}](https://doi.org/{doi_str}) | 来源: {src}")
        else:
            lines.append(f"  > 来源: {src}")
    return "\n".join(lines)

def format_detailed(results):
    """详细格式输出，包含摘要等信息"""
    lines = []
    for i, p in enumerate(results, 1):
        oa_icon = "[OA] 可获取" if p.get("is_oa") else ("[X] 付费" if p.get("is_oa") is False else "[?] 不确定")
        lines.append(f"### {i}. {p['title']}")
        lines.append(f"- **作者**: {p['first_author']}")
        lines.append(f"- **年份**: {p['year']}")
        lines.append(f"- **期刊**: {p.get('journal', 'N/A')}")
        lines.append(f"- **引用量**: {p['cited_by']}")
        if p.get("fwci"):
            lines.append(f"- **FWCI (影响因子)**: {p['fwci']:.2f}")
        lines.append(f"- **OA 状态**: {oa_icon}")
        if p.get("doi"):
            lines.append(f"- **DOI**: [{p['doi']}](https://doi.org/{p['doi']})")
        if p.get("pdf_url"):
            lines.append(f"- **PDF**: {p['pdf_url']}")
        lines.append(f"- **来源**: {p.get('source', 'N/A')}")
        lines.append("")
    return "\n".join(lines)

def search_all(query, max_results=20, year=None, oa_only=False, author_name=None):
    """全源搜索并返回合并结果"""
    author_id = None
    if author_name:
        author_id = resolve_author_id(author_name)
        if author_id:
            print(f"[OK] Found author ID: {author_id} ({author_name})", file=sys.stderr)
        else:
            print(f"[WARN] Author '{author_name}' not found, searching as keyword", file=sys.stderr)

    results = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {}
        if author_id:
            futures[executor.submit(search_openalex, query, max_results, year, oa_only, author_id)] = "OpenAlex"
        else:
            futures[executor.submit(search_openalex, query, max_results, year, oa_only)] = "OpenAlex"
        futures[executor.submit(search_crossref, query, max_results)] = "Crossref"
        futures[executor.submit(search_semantic_scholar, query, min(max_results, 10))] = "SemanticScholar"

        for future in as_completed(futures):
            source = futures[future]
            try:
                data = future.result()
                print(f"  [{source}] 返回 {len(data)} 条结果", file=sys.stderr)
                if source == "OpenAlex":
                    results.extend([extract_openalex_info(w) for w in data])
                elif source == "Crossref":
                    results.extend([extract_crossref_info(w) for w in data])
                else:
                    results.extend([extract_s2_info(w) for w in data])
            except Exception as e:
                print(f"  [{source}] 错误: {e}", file=sys.stderr)

    merged = merge_results(results, max_results)
    merged = enrich_oa_status(merged)
    # OA 结果优先，然后按引用量降序
    merged.sort(key=lambda x: (not x.get("is_oa"), -(x.get("cited_by") or 0)))
    return merged

def main():
    import argparse
    parser = argparse.ArgumentParser(description="学术论文搜索工具")
    parser.add_argument("query", nargs="?", default="", help="搜索词")
    parser.add_argument("--doi", default="", help="按 DOI 精确查找")
    parser.add_argument("--author", default="", help="作者名")
    parser.add_argument("--year", type=int, default=0, help="发表年份")
    parser.add_argument("--oa-only", action="store_true", help="仅显示 OA 论文")
    parser.add_argument("--max", type=int, default=20, help="最大结果数")
    parser.add_argument("--format", choices=["table", "detail"], default="table", help="输出格式")
    parser.add_argument("--json", action="store_true", help="输出原始 JSON")

    args = parser.parse_args()
    query = args.query.strip()

    if not query and not args.doi:
        print("用法: python search_papers.py '搜索词' [--author 作者] [--year 年份] [--oa-only] [--max 20]", file=sys.stderr)
        print("      python search_papers.py --doi '10.xxx/xxx'", file=sys.stderr)
        sys.exit(1)

    if args.doi:
        doi = args.doi.replace("https://doi.org/", "")
        if not doi.startswith("10."):
            print("[WARN] DOI format incorrect, should start with 10.", file=sys.stderr)
            sys.exit(1)
        # 先从 OpenAlex 查
        print(f"[Search] Looking up DOI: {doi}", file=sys.stderr)
        url = f"https://api.openalex.org/works/https://doi.org/{urllib.parse.quote(doi)}?mailto={EMAIL}"
        data = fetch_json(url)
        if data and data.get("id"):
            r = extract_openalex_info(data)
            unpaywall = check_unpaywall(doi)
            if unpaywall["is_oa"]:
                r["is_oa"] = True
                r["oa_status"] = unpaywall["oa_status"]
                if unpaywall["pdf_url"]:
                    r["pdf_url"] = unpaywall["pdf_url"]
            results = [r]
        else:
            print("[ERROR] DOI not found", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"[Search] Query: {query}", file=sys.stderr)
        if args.author:
            print(f"   作者: {args.author}", file=sys.stderr)
        if args.year:
            print(f"   年份: {args.year}", file=sys.stderr)

        results = search_all(
            query,
            max_results=args.max,
            year=args.year or None,
            oa_only=args.oa_only,
            author_name=args.author or None
        )

    print(f"\n[Results] Found {len(results)} papers:\n", file=sys.stderr)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif args.format == "detail":
        print(format_detailed(results))
    else:
        print(format_results_table(results))

    # 输出 OA PDF 可下载提示
    oa_count = sum(1 for r in results if r.get("is_oa") and r.get("pdf_url"))
    if oa_count:
        print(f"\n[Download] {oa_count} OA papers available. Use --json to see PDF URLs.", file=sys.stderr)


if __name__ == "__main__":
    main()
