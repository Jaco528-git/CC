---
name: html-report
description: "用HTML生成演示级报告——当用户提到'报告'、'演示报告'、'html报告'、'展示报告'、'幻灯片报告'、'汇报'、'成果展示'，或需要将论文/数据/分析结果整理成全屏翻页式HTML演示文稿时使用。面向人文地理学/地理学学术圈（导师汇报、学术会议、开题答辩）。格式是类似PPT的全屏翻页展示，不是长网页滚动。优先于pptx/docx——用户明确偏好HTML的制作和修改效率。"
---

# HTML 演示报告技能

## 核心原则

- **是演示文稿，不是网页文章**：全屏翻页，每页一个核心观点，不是长滚动页面
- **提炼而非堆砌**：每页只放 3-5 个要点/数据/图表，核心观点用大号字突出
- **亮色系**：暖白底色、深色文字，干净学术风
- **视觉辅助**：每页必须有视觉元素——图表、大数字、关键词卡片、示意图
- **单文件自包含**：CSS/JS 内嵌，翻页交互原生支持
- **印刷友好**：支持逐页打印为 PDF
- **地图红线**：涉及中国地图必须标注来源和审图号，详见"地图使用规范"

## 布局规范

全屏翻页格式需要充分利用屏幕空间，避免内容挤在中央窄条。以下规则贯穿所有内容页。

1. **内容页顶对齐**：`.slide` 默认 `justify-content: flex-start; align-items: stretch;`，内容从顶部铺开。仅封面和致谢页使用 `.slide.center` 实现居中。

2. **宽度利用**：内容容器用 `min(90vw, 1200px)`，禁止 `max-width: 700px` 等窄幅限制。卡片网格、对比列、大数字区域均应横向铺满。

3. **字号体系**（全屏 `clamp()` 缩放）：
   - 核心数据：`clamp(2.5rem, 5vw, 4.5rem)`
   - 标题：`clamp(1.5rem, 3vw, 2.5rem)`
   - 正文要点：`clamp(1rem, 2vw, 1.4rem)`
   - 注释/来源：`clamp(0.8rem, 1.2vw, 1rem)`
   - 任何文字最小不低于 `0.75rem`

4. **网格列宽**：`grid-template-columns: repeat(auto-fit, minmax(280px, 1fr))`，卡片内容舒展不拥挤。

5. **布局多样性**：充分利用屏幕的横向和纵向空间——左描述+右图表、上中下分区、顶部色块+底部内容，避免所有内容叠在一个竖条里。

---

## ⚠️ 地图使用规范（地理学红线）

地理学演示中涉及地图时，必须遵守：

1. **来源清晰**：每张地图在 slide 底部或 figcaption 中标注来源
2. **审图号**：中国地图（含台湾、南海诸岛）必须标注审图号
3. **边界准确**：不可遗漏或变形中国领土要素
4. **用户把关**：生成后明确告知"地图部分请重点审核"

> ❌ 绝对禁止编造地图边界、使用来源不明的地图。
> ✅ 宁可不放地图，也不放不规范的。

---

## 基础模板（全屏翻页）

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>报告标题</title>
<style>
  /* ── 设计系统 ── */
  :root {
    --bg: #f8f6f2; --card: #ffffff; --text: #2c2c2c; --muted: #8c8c8c;
    --border: #e0ddd8; --accent: #8b3a3a; --accent2: #3a6b8f; --accent3: #3d7a5a;
    --shadow: 0 1px 3px rgba(0,0,0,0.06);
    --font-sans: "PingFang SC","Noto Sans SC","Microsoft YaHei",sans-serif;
    --font-serif: "Noto Serif SC","STSong","SimSun",serif;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { height: 100%; overflow: hidden; font-family: var(--font-sans); background: var(--bg); color: var(--text); }
  .deck { width: 100vw; height: 100vh; position: relative; overflow: hidden; }
  
  /* ═══ 幻灯片基础 ═══ */
  .slide {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    padding: 5% 6%; opacity: 0; transform: scale(0.96);
    transition: opacity .4s ease, transform .4s ease;
    pointer-events: none; overflow-y: auto;
    /* 内容页默认顶对齐、横向铺开——不居中堆叠 */
    display: flex; flex-direction: column;
    justify-content: flex-start; align-items: stretch;
  }
  .slide.active { opacity: 1; transform: scale(1); pointer-events: auto; z-index: 10; }
  /* 封面和致谢页使用 .center 类居中 */
  .slide.center { justify-content: center; align-items: center; }
  
  .slide h1 { font-size: clamp(2rem, 4.5vw, 3.5rem); font-weight: 700; letter-spacing: 2px; margin-bottom: .3em; text-align: center; }
  .slide h2 { font-size: clamp(1.5rem, 3vw, 2.5rem); font-weight: 600; margin-bottom: .4em; text-align: center; }
  .slide .sub { font-size: clamp(1rem, 1.6vw, 1.3rem); color: var(--muted); text-align: center; max-width: min(80vw, 900px); margin: 0 auto; line-height: 1.7; }
  
  /* ── 内容容器：充分利用宽度 ── */
  .content { width: min(92vw, 1200px); margin: 0 auto; }
  
  /* ── 卡片网格 ── */
  .card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 12px; padding: 24px 20px; box-shadow: var(--shadow);
  }
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; width: 100%; }
  .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 18px; width: 100%; }
  .grid-auto { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 18px; width: 100%; }
  
  /* ── 大数字 ── */
  .stat-number { font-size: clamp(2.5rem, 5vw, 4.5rem); font-weight: 800; line-height: 1.1; }
  .stat-label { font-size: clamp(0.9rem, 1.4vw, 1.15rem); color: var(--muted); margin-top: 4px; }
  
  /* ── 页面指示器 ── */
  .pager { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); z-index: 100; display: flex; gap: 8px; align-items: center; }
  .dot { width: 7px; height: 7px; border-radius: 50%; background: rgba(0,0,0,0.12); cursor: pointer; transition: all .3s; }
  .dot.active { background: var(--accent); width: 24px; border-radius: 3px; }
  .page-num { font-size: 12px; color: rgba(0,0,0,0.25); letter-spacing: 1px; margin-left: 6px; }
</style>
</head>
<body>
<div class="deck" id="deck">
  <section class="slide center"><!-- 封面和致谢用 .center --></section>
  <section class="slide"><!-- 内容页不用 .center --></section>
</div>
<script>
(function(){
  var ss = document.querySelectorAll('.slide'), ci = 0;
  if (!ss.length) return;

  // 动态生成页面指示器
  var pager = document.createElement('div'); pager.className = 'pager';
  for (var i = 0; i < ss.length; i++) {
    var dot = document.createElement('span');
    dot.className = 'dot'; dot.dataset.goto = i;
    dot.addEventListener('click', function(){ go(parseInt(this.dataset.goto)); });
    pager.appendChild(dot);
  }
  var pn = document.createElement('span'); pn.className = 'page-num'; pn.id = 'pageNum';
  pager.appendChild(pn);
  document.body.appendChild(pager);
  var dots = pager.querySelectorAll('.dot');

  function go(n){
    ss[ci].classList.remove('active'); dots[ci].classList.remove('active');
    ci = (n + ss.length) % ss.length;
    ss[ci].classList.add('active'); dots[ci].classList.add('active');
    pn.textContent = String(ci+1).padStart(2,'0') + ' / ' + String(ss.length).padStart(2,'0');
  }
  var nxt = function(){ go(ci+1); }, prv = function(){ go(ci-1); };

  // 键盘
  document.addEventListener('keydown', function(e){
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') { e.preventDefault(); nxt(); }
    if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') { e.preventDefault(); prv(); }
  });

  // 点击（排除交互元素，左25%回退，右75%前进）
  document.addEventListener('click', function(e){
    if (e.target.closest('.pager, a, button, canvas, input, textarea, [contenteditable]')) return;
    if (e.clientX / window.innerWidth < 0.25) prv(); else nxt();
  });

  // 滚轮（500ms 节流）
  var wt = null;
  document.addEventListener('wheel', function(e){
    e.preventDefault(); if (wt) return;
    wt = setTimeout(function(){ wt = null; }, 500);
    if (e.deltaY > 0) nxt(); else prv();
  }, {passive: false});

  // 触摸滑动（水平滑动 > 50px 触发翻页）
  var tx = 0, ty = 0;
  document.addEventListener('touchstart', function(e){
    if (e.target.closest('a, button, canvas, input, textarea, [contenteditable]')) return;
    tx = e.touches[0].clientX; ty = e.touches[0].clientY;
  }, {passive: true});
  document.addEventListener('touchend', function(e){
    if (!tx && !ty) return;
    var dx = e.changedTouches[0].clientX - tx, dy = e.changedTouches[0].clientY - ty;
    if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 50) { dx < 0 ? nxt() : prv(); }
    tx = ty = 0;
  });

  go(0);
})();
</script>
</body>
</html>
```

---

## 设计系统

### 配色

| 用途 | 颜色 | 说明 |
|------|------|------|
| 背景 | `#f8f6f2` | 暖白 |
| 卡片 | `#ffffff` | 纯白 |
| 正文 | `#2c2c2c` | 深灰 |
| 辅助 | `#8c8c8c` | 注释 |
| 边框 | `#e0ddd8` | 浅灰 |
| 强调 | `#8b3a3a` | 深红棕（学术） |
| 辅助蓝 | `#3a6b8f` | 图表 |
| 辅助绿 | `#3d7a5a` | 正向指标 |

### 字号（全屏下）

| 元素 | 字号 | 说明 |
|------|------|------|
| 首页大标题 | `clamp(2.5rem, 5vw, 4rem)` | 封面使用 |
| 幻灯片标题 | `clamp(1.5rem, 3vw, 2.5rem)` | 内容页标题 |
| 核心数据 | `clamp(2.5rem, 5vw, 4.5rem)` | 大数字展示 |
| 宽栏正文 | `clamp(1.1rem, 1.8vw, 1.4rem)` | 单列/全宽区域 |
| 网格密集正文 | `clamp(0.9rem, 1.3vw, 1.1rem)` | grid-3/grid-4 内的卡片 |
| 表格内文字 | `clamp(0.8rem, 1.1vw, 0.95rem)` | 表格/密集数据 |
| 注释/来源 | `clamp(0.75rem, 1vw, 0.9rem)` | 图注/脚注 |

**关键规则：字体大小必须与容器宽度成比例。**  
- 网格越密集（列数越多），卡片内的字号越小  
- full-width 宽栏可以用大字，grid-4 窄卡片用小字  
- 不要让大字体在小卡片里换行 3-4 行，视觉效果差

---

## 演示文稿结构：灵活合并稀疏页面

核心原则：**页数由内容和报告时间决定，没有硬性上限。** 但要注意避免"信息密度太低"——每个核心发现独占一页会频繁翻页，扰乱听众注意力。

**密度指导只适用于内容页**（核心发现、深入分析、结论）。封面、汇报纲要、致谢页天然是框架性或引导性的，不需要追求密度。

**合并的指导原则：**

- **相邻的同类型内容页**可以合并：例如 3 个核心发现合并成一张对比网格页，背景和目标合并成一页，参考文献作为结论页的脚注
- **可用的合并模式**：
  - 研究背景 + 研究目标 + 方法概述 → 1 页（用 `grid-2` 或 `grid-3` 概括）
  - 多个并列发现/案例 → 1 页（用网格或对比布局并排展示）
  - 参考文献 → 结论页底部的小字脚注（不单独成页）
- **密度检查**：列完所有 slide 后，检查是否有相邻的内容页属于"信息罗列"类型，就合并它们
- **特殊情况**：某个数据或图表非常重要，可以独占一页（如关键地图、复杂图表）

典型的序列参考：

```
第1页：封面　　　　— 标题 + 作者/单位（.center 居中）
第2页：概述　　　　— 目录网格 + 核心数据速览
第3页：核心发现　　— 2~4 个关键结果用网格/大数字并列展示
第4页：深入分析　　— 图表 + 解读（如需要，可以拆多页）
第5页：结论　　　　— 3~5 条要点 + 参考文献脚注
第6页：致谢/问答　 — 感谢页（.center 居中）
```

---

## 幻灯片布局模板

### 封面页

```html
<section class="slide center" style="background:radial-gradient(ellipse at 50% 30%,rgba(139,58,58,0.05) 0%,transparent 60%),var(--bg);">
  <h1 style="font-size:clamp(2rem,4.5vw,3.5rem);font-weight:700;letter-spacing:3px;text-align:center;line-height:1.3;padding:0 4%;">论文标题</h1>
  <div style="width:50px;height:3px;background:var(--accent);margin:20px auto;border-radius:2px;"></div>
  <p style="font-size:1rem;color:var(--muted);text-align:center;line-height:1.6;">作者¹　通讯作者¹*</p>
  <p style="font-size:0.85rem;color:var(--muted);margin-top:4px;">1. 单位名称</p>
  <p style="font-size:0.8rem;color:rgba(0,0,0,0.3);margin-top:28px;">点击 / 方向键翻页</p>
</section>
```

### 目录/概述页（合并目录 + 数据速览）

```html
<section class="slide">
  <h2 style="margin-bottom:20px;">汇报纲要</h2>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;width:min(92vw,1100px);margin:0 auto;">
    <div class="card" style="text-align:center;padding:18px 16px;">
      <div style="font-size:1.6rem;font-weight:700;color:var(--accent);">01</div>
      <div style="font-size:1rem;margin-top:6px;font-weight:500;">研究背景</div>
      <div style="font-size:0.85rem;color:var(--muted);margin-top:2px;">问题提出与意义</div>
    </div>
    <div class="card" style="text-align:center;padding:18px 16px;">
      <div style="font-size:1.6rem;font-weight:700;color:var(--accent2);">02</div>
      <div style="font-size:1rem;margin-top:6px;font-weight:500;">数据与方法</div>
      <div style="font-size:0.85rem;color:var(--muted);margin-top:2px;">来源与框架</div>
    </div>
    <!-- 更多... -->
  </div>
</section>
```

也可以将目录卡片与关键统计数据合并，在网格下方用全宽条形区域展示数据速览。

### 核心数据页（大数字，铺满宽度）

```html
<section class="slide">
  <h2 style="margin-bottom:14px;">关键发现</h2>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px;width:min(92vw,1100px);margin:0 auto;">
    <div class="card" style="text-align:center;padding:28px 20px;">
      <div class="stat-number" style="color:var(--accent);">91.3%</div>
      <div class="stat-label">预测精度</div>
    </div>
    <div class="card" style="text-align:center;padding:28px 20px;">
      <div class="stat-number" style="color:var(--accent2);">R²=0.87</div>
      <div class="stat-label">模型拟合度</div>
    </div>
    <div class="card" style="text-align:center;padding:28px 20px;">
      <div class="stat-number" style="color:var(--accent3);">+15%</div>
      <div class="stat-label">相较传统模型提升</div>
    </div>
  </div>
  <p class="sub" style="font-size:0.85rem;margin-top:16px;">补充说明文字放在底部</p>
</section>
```

3~4 个大数字卡片 = 至少 2 个核心发现并列展示。不要让单个数据点独占一页。

### 要点列表页（全宽）

```html
<section class="slide">
  <h2 style="margin-bottom:14px;">研究结论</h2>
  <div style="width:min(88vw,1100px);margin:0 auto;">
    <div style="display:flex;gap:16px;margin-bottom:16px;align-items:flex-start;">
      <div style="width:32px;height:32px;border-radius:50%;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;font-size:0.95rem;font-weight:600;flex-shrink:0;">1</div>
      <div><strong style="font-size:1.15rem;">结论一</strong><p style="font-size:1rem;color:var(--muted);margin-top:3px;line-height:1.6;">详细说明</p></div>
    </div>
    <!-- 重复：4条结论并列 -->
  </div>
</section>
```

### 图表页（宽幅图表）

```html
<section class="slide">
  <h2 style="margin-bottom:10px;">模型性能对比</h2>
  <div class="card" style="width:min(88vw,1100px);margin:0 auto;padding:20px;">
    <canvas id="chart" style="max-height:350px;"></canvas>
  </div>
  <p style="font-size:0.85rem;color:var(--muted);margin-top:8px;text-align:center;">图1 不同模型精度对比</p>
</section>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<script>/* Chart.js 代码 */</script>
```

图表容器使用 `min(88vw, 1100px)` 宽度，充分利用横向空间。

### 分栏对比页（横向铺开）

```html
<section class="slide">
  <h2 style="margin-bottom:14px;">方法对比</h2>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;width:min(90vw,1100px);margin:0 auto;">
    <div class="card" style="padding:24px;">
      <h3 style="font-size:1.2rem;font-weight:600;color:var(--accent);margin-bottom:10px;">传统方法</h3>
      <ul style="list-style:none;font-size:1rem;color:var(--muted);line-height:1.8;">
        <li style="margin-bottom:8px;">✗ 依赖人工特征</li>
        <li style="margin-bottom:8px;">✗ 精度有限</li>
        <li>✓ 可解释性强</li>
      </ul>
    </div>
    <div class="card" style="padding:24px;">
      <h3 style="font-size:1.2rem;font-weight:600;color:var(--accent2);margin-bottom:10px;">深度学习方法</h3>
      <ul style="list-style:none;font-size:1rem;color:var(--muted);line-height:1.8;">
        <li style="margin-bottom:8px;">✓ 自动特征学习</li>
        <li style="margin-bottom:8px;">✓ 精度提升15%+</li>
        <li>✗ 需大量标注数据</li>
      </ul>
    </div>
  </div>
</section>
```

对比页是最适合铺满宽度的场景——左右两栏各占一半屏幕，文字用大号字。

### 致谢页

```html
<section class="slide center" style="background:radial-gradient(ellipse at 50% 40%,rgba(139,58,58,0.04) 0%,transparent 60%),var(--bg);">
  <h1 style="font-size:clamp(2.5rem,5vw,4rem);">感谢聆听</h1>
  <div style="width:50px;height:3px;background:var(--accent);margin:20px auto;border-radius:2px;"></div>
  <p class="sub">欢迎批评指正</p>
  <p style="font-size:0.85rem;color:rgba(0,0,0,0.3);margin-top:32px;">联系方式 · 邮箱</p>
</section>
```

---

## ⚠️ 视觉节奏：避免呆板统一

**当前问题：** 每页都是"标题 + 白色卡片网格"——再好看的模式重复 6-7 次也会显得呆板。

**修正方法：相邻两页不要用相同布局。** 至少准备以下 4-5 种布局类型轮换使用：

### 布局类型库

**A. 全色背景页（section divider）— 适合章节过渡**
```html
<section class="slide center" style="background:linear-gradient(135deg, var(--accent) 0%, #6d2e2e 100%);">
  <div style="text-align:center;color:#fff;">
    <div style="font-size:clamp(3rem,6vw,5rem);font-weight:800;opacity:0.15;">02</div>
    <h2 style="color:#fff;font-size:clamp(2rem,4vw,3rem);">数据与方法</h2>
    <div style="width:40px;height:2px;background:rgba(255,255,255,0.4);margin:16px auto;"></div>
    <p style="color:rgba(255,255,255,0.7);font-size:1rem;">研究设计 · 数据来源 · 分析框架</p>
  </div>
</section>
```

**B. 左文右图不对称页 — 打破网格对称**
```html
<section class="slide" style="flex-direction:row;align-items:center;">
  <div style="flex:1;padding-right:4%;">
    <h2 style="text-align:left;margin-bottom:16px;">核心发现</h2>
    <p style="font-size:clamp(1rem,1.6vw,1.3rem);line-height:1.8;color:#444;">描述文字...</p>
  </div>
  <div style="flex:1;background:var(--accent2);border-radius:16px;min-height:300px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:3rem;opacity:0.8;">🗺️</div>
</section>
```

**C. 纯引语/结论页 — 一页只放一句话**
```html
<section class="slide center" style="background:var(--bg);">
  <div style="max-width:min(80vw,900px);text-align:center;">
    <div style="font-size:clamp(2rem,4vw,3.5rem);font-weight:700;line-height:1.4;color:var(--accent);">
      "步行距离是影响<br>绿地使用频率的最显著因素"
    </div>
    <p style="font-size:1rem;color:var(--muted);margin-top:24px;">r = &minus;0.42, p &lt; 0.001</p>
  </div>
</section>
```

**D. 顶部色块 + 底部内容**
```html
<section class="slide" style="padding:0;">
  <div style="width:100%;height:45%;background:linear-gradient(135deg,var(--accent2),var(--accent));display:flex;align-items:center;justify-content:center;">
    <h2 style="color:#fff;font-size:clamp(2rem,4vw,3rem);">长沙市社区绿地调查</h2>
  </div>
  <div style="flex:1;padding:4% 6%;display:flex;flex-direction:column;justify-content:center;">
    <div class="content"><!-- 卡片内容 --></div>
  </div>
</section>
```

### 节奏控制规则

1. **相邻两页不同布局**：如果第 3 页用了"卡片网格"，第 4 页就不要再用网格，换成"左文右图"或"纯引语"
2. **每 3-4 页插入一个节奏变化**：连续内容页之间插入一个全色过渡页或引语页，给听众"换气"的空间
3. **封面和致谢页都居中**，但背景处理不同——封面用渐变色，致谢用简练纯色
4. **卡片样式也可以变化**：大部分用白色卡片，偶尔用"无边卡片"或"色块卡片"来打破视觉一致

---

## 图表

### Chart.js（推荐）

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<canvas id="myChart" style="max-height:280px;"></canvas>
<script>
new Chart(document.getElementById('myChart'), {
  type: 'bar', // 'bar','line','pie','doughnut','radar'
  data: {
    labels: ['A','B','C'],
    datasets: [{ label: '指标', data: [12,19,3],
      backgroundColor: ['#8b3a3a','#3a6b8f','#3d7a5a'] }]
  },
  options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
});
</script>
```

### 纯CSS图表（无外部依赖）

适合简单的水平条形图或指标进度：

```html
<div style="margin:8px 0;max-width:500px;">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
    <span style="width:70px;font-size:0.85rem;">指标A</span>
    <div style="flex:1;height:16px;background:#e8e5e0;border-radius:3px;overflow:hidden;">
      <div style="width:85%;height:100%;background:var(--accent2);border-radius:3px;"></div>
    </div>
    <span style="font-size:0.8rem;color:var(--muted);">85%</span>
  </div>
</div>
```

---

## 设计指南

### 页面核心清晰

- 每页有一个标题说清这页讲什么（如"深度学习提升分类精度15%+"），而非"结果分析"
- 核心数据用大号字（2.5rem+），加粗，强调色
- 辅助说明用中号字（1.1rem左右），灰色
- 来源/注释用小字（0.85rem），浅灰

### 密度控制

参见上文"演示文稿结构"的合并原则——相邻同类型内容页应合并，每页 3-5 个数据点或 1 个对比网格是合适的密度。仅关键地图或复杂图表可独占一页。

### 对比与并列

- 用分栏布局做对比（左vs右、前vs后），充分利用横向空间
- 用颜色区分不同类别（红棕=传统方法，蓝=深度学习方法）
- 对比列至少用 `min(80vw, 1100px)` 宽度

### 图片与视觉元素

演示文稿不是论文，**图片的作用是辅助理解和控制视觉节奏**，不一定是学术图表。

- **封面使用装饰性背景**：渐变、纹理、或占位图框，让第一页有视觉冲击力
- **章节过渡页用大号数字或图标**：全色背景 + 超大章节号 + 简短短语
- **内容页可加入示意图片框**：即使没有真实图片，用彩色占位块 + 说明文字（如"此处插入研究区位置图"）也比纯文字好
- **使用 emoji/icon 作为低成本视觉元素**：🌳 绿地、📊 数据、🔬 方法、📍 区位——但不要过度使用
- **地理学演示的优势**：卫星影像、土地利用图、DEM 高程图、城市航拍等本身就是最好的视觉素材。优先使用这些（标注来源）
- **CSS 渐变和几何装饰**：直线、圆圈、色块等低成本元素可以用来分割区域、引导视线

### 字体与容器比例协调

参见上文"设计系统"中的字号表——字号应与容器宽度成比例。补充规则：

- **卡片宽度决定字号**：grid-2 宽卡用 `clamp(1rem, 1.6vw, 1.2rem)`，grid-4 窄卡用 `clamp(0.85rem, 1.2vw, 1rem)`
- **表格行高适度**：表格内字体 0.85-0.95rem，行高 1.4-1.5
- **大数字不配长文**：大数字卡片（2.5rem+）下方只跟简短标签（2-5 字）
- **内联覆写**：密集网格中用 `style="font-size:0.9rem;"` 微调，无需为每种网格定义 CSS 类
- **验证方法**：浏览器逐页检查——文字换行超 3 行则缩小字号，卡片空旷则放大

---

## 印刷

```css
@media print {
  @page { margin: 1cm; }
  body { background: white; }
  .slide { position: relative; opacity: 1 !important; transform: none !important; pointer-events: none; page-break-after: always; display: flex; }
  .slide.active { z-index: auto; }
  .pager, .dot, .page-num { display: none; }
}
```

---

## 质量检查

1. **编码**：`<meta charset="UTF-8">` 存在
2. **翻页交互**：键盘方向键、点击、滚轮、触摸滑动四种翻页均正常
3. **首页指示**：有"点击/方向键翻页"提示
4. **页面指示器**：底部圆点页码正确
5. **响应式**：窗口缩至375px内容不溢出
6. **打印**：逐页分页正常
7. **地图审核**：如有地图，来源和审图号已标注
8. **布局检查**：内容是否铺满屏幕宽度？内容页是否使用了 `.slide`（顶对齐）而不是 `.center`？
9. **视觉节奏检查**：相邻两页是否用了不同布局？是否有连续 3 页以上看起来结构雷同？
10. **图片/视觉元素检查**：是否有至少一处非图表视觉元素（装饰性背景、图标、色块、图片框）？
11. **字体比例检查**：密集网格（grid-3/grid-4）中的卡片字体是否偏小？表格字体是否过于拥挤？full-width 区域字体是否偏小？
12. **密度检查**：相邻内容页是否可以合并？是否有单一发现/数据点独占内容页的情况？
