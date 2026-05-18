import sys, json, os
sys.stdout.reconfigure(encoding='utf-8')

d = json.load(sys.stdin)
model = d.get('model', {}).get('display_name', '')
cw = d.get('context_window', {})
used_pct = cw.get('used_percentage')
input_tokens = cw.get('total_input_tokens')

folder = os.path.basename(d.get('cwd', ''))

window_size = cw.get('context_window_size')  # API 返回的实际窗口

parts = []

if folder:
    parts.append(folder)
if model:
    parts.append(model)

if input_tokens is not None and window_size:
    used_k = input_tokens / 1000
    win_k = window_size / 1000
    pct = input_tokens / window_size * 100
    parts.append(f'Usage: {pct:.0f}% ({used_k:.0f}k/{win_k:.0f}k)')
elif used_pct is not None:
    parts.append(f'Usage: {used_pct}%')

print(' | '.join(parts))
