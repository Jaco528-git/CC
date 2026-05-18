import json, os, re, sys

def grade(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    results = {}

    slides = re.findall(r'<section\s+class="slide', html)
    results['slide_count'] = len(slides)

    results['has_max_width_700'] = bool(re.search(r'max-width:\s*700px', html))
    results['uses_wide_container'] = bool(re.search(r'min\(9\dvw', html)) or bool(re.search(r'min\(8\dvw', html))
    results['has_center_class'] = bool(re.search(r'class="slide\s+center"', html))
    results['has_flex_start'] = bool(re.search(r'justify-content:\s*flex-start', html))
    results['has_chartjs'] = 'chart.js@4' in html.lower() or 'chart.js@3' in html.lower()
    results['has_large_stats'] = bool(re.search(r'font-size.*clamp\(2\.[5-9]', html))
    results['has_transition'] = 'opacity' in html and 'transform' in html and 'transition' in html
    results['has_grid'] = bool(re.search(r'grid-template-columns', html))

    # Font size proportionality: check for smaller fonts in grid contexts
    results['has_dense_grid_font'] = bool(re.search(r'font-size.*clamp\(0\.8[5-9]|font-size.*clamp\(0\.9[0-4]', html))

    return results

def make_assertions(results, eval_id):
    assertions = []

    assertions.append({
        'text': 'no-max-width-700',
        'passed': not results['has_max_width_700'],
        'evidence': "No max-width:700px" if not results['has_max_width_700'] else "Found max-width:700px"
    })
    assertions.append({
        'text': 'uses-wide-container',
        'passed': results['uses_wide_container'],
        'evidence': "Wide container found" if results['uses_wide_container'] else "No wide container"
    })
    assertions.append({
        'text': 'content-not-centered',
        'passed': results['has_flex_start'],
        'evidence': "Has flex-start" if results['has_flex_start'] else "Missing flex-start"
    })
    assertions.append({
        'text': 'slide-transition',
        'passed': results['has_transition'],
        'evidence': "Has transition" if results['has_transition'] else "Missing"
    })
    assertions.append({
        'text': 'grid-layout',
        'passed': results['has_grid'],
        'evidence': "Grid found" if results['has_grid'] else "No grid"
    })

    # Font proportion check
    assertions.append({
        'text': 'font-container-proportion',
        'passed': results['has_dense_grid_font'],
        'evidence': "Has smaller fonts for dense grids" if results['has_dense_grid_font'] else "No context-aware font sizing"
    })

    if eval_id == 0:
        assertions.append({
            'text': 'chart-js-present',
            'passed': results['has_chartjs'],
            'evidence': "Chart.js found" if results['has_chartjs'] else "No Chart.js"
        })
    elif eval_id == 2:
        assertions.append({
            'text': 'chart-js-present',
            'passed': results['has_chartjs'],
            'evidence': "Chart.js found" if results['has_chartjs'] else "No Chart.js"
        })
        assertions.append({
            'text': 'stat-numbers-large',
            'passed': results['has_large_stats'],
            'evidence': "Large stats found" if results['has_large_stats'] else "No large stats"
        })

    return assertions

base = r'C:\Users\31070\Documents\CC\html-report-workspace\iteration-4'

evals = [
    (0, 'eval-0-paper-report'),
    (1, 'eval-1-lit-review'),
    (2, 'eval-2-survey-data'),
]

for eval_id, dir_name in evals:
    out_dir = os.path.join(base, dir_name, 'with_skill', 'outputs')
    if not os.path.isdir(out_dir):
        print(f"SKIP: {out_dir} not found")
        continue

    html_files = [f for f in os.listdir(out_dir) if f.endswith('.html')]
    if not html_files:
        print(f"SKIP: {dir_name} - no HTML files")
        continue

    html_path = os.path.join(out_dir, html_files[0])
    results = grade(html_path)
    assertions = make_assertions(results, eval_id)

    grading = {
        'eval_id': eval_id,
        'file': html_files[0],
        'slide_count': results['slide_count'],
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
    print(f"File: {html_files[0]}")
    print(f"Slides: {results['slide_count']}")
    print(f"Passed: {passed}/{total}")
    for a in assertions:
        status = '✓' if a['passed'] else '✗'
        print(f"  {status} {a['text']}: {a['evidence']}")
