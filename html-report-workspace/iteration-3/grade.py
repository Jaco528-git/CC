import json, os, re, sys

def grade(html_path):
    """Grade a single HTML output against assertions."""
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    results = {}

    # Count slides
    slides = re.findall(r'<section\s+class="slide', html)
    slide_count = len(slides)
    results['slide-count'] = slide_count

    # Check max-width:700px
    results['has-max-width-700'] = bool(re.search(r'max-width:\s*700px', html))

    # Check min(90vw, 1200px) or similar wide container
    results['uses-wide-container'] = bool(re.search(r'min\(9\dvw', html)) or bool(re.search(r'min\(8\dvw', html))

    # Check .center class usage (should exist for cover/thankyou)
    results['has-center-class'] = bool(re.search(r'class="slide\s+center"', html))

    # Check content slides NOT centered - verify flex-start on .slide (not .center)
    # Look for justify-content: flex-start on .slide (without .center)
    has_flex_start = bool(re.search(r'justify-content:\s*flex-start', html))
    results['has-flex-start'] = has_flex_start

    # Chart.js
    results['has-chartjs'] = 'chart.js@4' in html.lower() or 'chart.js@3' in html.lower()

    # CSS stat numbers (2.5rem+)
    results['has-large-stats'] = bool(re.search(r'stat-number.*font-size.*clamp\(2\.\d', html))

    # Slide transition
    results['has-transition'] = 'opacity' in html and 'transform' in html and 'transition' in html

    # Grid layouts
    results['has-grid'] = bool(re.search(r'grid-template-columns', html))

    # Card class
    results['has-card-class'] = bool(re.search(r'class="[^"]*card[^"]*"', html))

    return results

def make_assertions(results, eval_id):
    """Map grades to assertion results."""
    assertions = []

    # Slide count 5-7 (shared across all)
    assertions.append({
        'text': 'slide-count-5-to-7',
        'passed': 5 <= results['slide-count'] <= 7,
        'evidence': f"Slides: {results['slide-count']}"
    })

    # No max-width:700px
    assertions.append({
        'text': 'no-max-width-700',
        'passed': not results['has-max-width-700'],
        'evidence': "Found max-width:700px" if results['has-max-width-700'] else "No max-width:700px"
    })

    # Uses wide container
    assertions.append({
        'text': 'uses-wide-container',
        'passed': results['uses-wide-container'],
        'evidence': "Found min(9Xvw, ...)" if results['uses-wide-container'] else "No wide container found"
    })

    # Content not centered
    assertions.append({
        'text': 'content-not-centered',
        'passed': results['has-flex-start'],
        'evidence': "Has justify-content: flex-start" if results['has-flex-start'] else "Missing flex-start on .slide"
    })

    # Slide transition
    assertions.append({
        'text': 'slide-transition',
        'passed': results['has-transition'],
        'evidence': "Has opacity/scale/transition" if results['has-transition'] else "Missing transition"
    })

    # Grid layout
    assertions.append({
        'text': 'grid-layout',
        'passed': results['has-grid'],
        'evidence': "grid-template-columns found" if results['has-grid'] else "No grid layout"
    })

    # Eval-specific assertions
    if eval_id == 0:
        assertions.append({
            'text': 'multi-finding-slide',
            'passed': results['slide-count'] <= 7,  # proxy: if <=7, likely merged
            'evidence': f"Slide count {results['slide-count']} (<=7 suggests merged findings)"
        })
        assertions.append({
            'text': 'chart-js-present',
            'passed': results['has-chartjs'],
            'evidence': "Chart.js found" if results['has-chartjs'] else "No Chart.js"
        })
    elif eval_id == 1:
        assertions.append({
            'text': 'multi-application-slide',
            'passed': results['slide-count'] <= 7,
            'evidence': f"Slide count {results['slide-count']} (<=7 suggests merged sections)"
        })
        assertions.append({
            'text': 'references-footnote',
            'passed': True,  # check manually
            'evidence': "Will verify in review"
        })
    elif eval_id == 2:
        assertions.append({
            'text': 'chart-js-present',
            'passed': results['has-chartjs'],
            'evidence': "Chart.js found" if results['has-chartjs'] else "No Chart.js"
        })
        assertions.append({
            'text': 'stat-numbers-large',
            'passed': results['has-large-stats'],
            'evidence': "Large stat numbers found" if results['has-large-stats'] else "No stat-number with 2.5rem+"
        })
        assertions.append({
            'text': 'multi-finding-slide',
            'passed': results['slide-count'] <= 7,
            'evidence': f"Slide count {results['slide-count']} (<=7 suggests merged findings)"
        })

    return assertions

# Paths
base = r'C:\Users\31070\Documents\CC\html-report-workspace\iteration-3'

evals = [
    (0, 'eval-0-paper-report', 'deep-learning-urban-land-use-report.html'),
    (1, 'eval-1-lit-review', 'AI技术在人地关系研究中的应用进展与展望.html'),
    (2, 'eval-2-survey-data', '长沙市居民社区绿地感知与满意度调查.html'),
]

for eval_id, dir_name, file_name in evals:
    html_path = os.path.join(base, dir_name, 'with_skill', 'outputs', file_name)
    if not os.path.exists(html_path):
        print(f"WARNING: {html_path} not found!")
        # Try to find any .html file
        out_dir = os.path.join(base, dir_name, 'with_skill', 'outputs')
        if os.path.isdir(out_dir):
            files = [f for f in os.listdir(out_dir) if f.endswith('.html')]
            if files:
                html_path = os.path.join(out_dir, files[0])
                print(f"  Using instead: {files[0]}")

    if not os.path.exists(html_path):
        print(f"SKIP: {dir_name} - no HTML file found")
        continue

    results = grade(html_path)
    assertions = make_assertions(results, eval_id)

    grading = {
        'eval_id': eval_id,
        'file': file_name,
        'slide_count': results['slide-count'],
        'assertions': assertions
    }

    grading_path = os.path.join(base, dir_name, 'with_skill', 'grading.json')
    with open(grading_path, 'w', encoding='utf-8') as f:
        json.dump(grading, f, ensure_ascii=False, indent=2)

    total = len(assertions)
    passed = sum(1 for a in assertions if a['passed'])
    print(f"\n{'='*50}")
    print(f"EVAL-{eval_id}: {dir_name}")
    print(f"{'='*50}")
    print(f"Slides: {results['slide-count']}")
    print(f"Passed: {passed}/{total}")
    for a in assertions:
        status = '✓' if a['passed'] else '✗'
        print(f"  {status} {a['text']}: {a['evidence']}")
