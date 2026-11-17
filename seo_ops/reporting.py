"""Portable JSON and static dashboard output with optional webhook alerts."""
import html
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen


def save_report(report: dict, output: str, html_output: str | None = None):
    path = Path(output); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    if html_output:
        html_path = Path(html_output); html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(to_html(report), encoding='utf-8')


def to_html(report: dict) -> str:
    esc = lambda value: html.escape(str(value), quote=True)
    rows = ''.join(f'<tr><td><span class="{esc(f["severity"])}">{esc(f["severity"])}</span></td><td>{esc(f["code"])}</td><td>{esc(f["url"])}</td><td>{esc(f["detail"])}</td></tr>' for f in report['findings'])
    rows = rows or '<tr><td colspan="4">No findings. Review the scope and coverage before interpreting this as an all-clear.</td></tr>'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SEO Operations Audit</title><style>body{{margin:0;background:#f8f6f1;color:#171923;font:16px/1.5 system-ui,sans-serif}}main{{max-width:1100px;margin:4rem auto;padding:0 1.5rem}}h1{{color:#533e80;font-size:clamp(2rem,4vw,3.5rem);letter-spacing:-.04em}}.sub{{color:#56606e}}.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:1rem;margin:2rem 0}}.metric{{padding:1.4rem;border:1px solid #ddd9e5;border-radius:16px;background:white}}.metric strong{{display:block;font-size:2rem;color:#166d73}}table{{border-collapse:collapse;width:100%;background:white}}th,td{{padding:.9rem;text-align:left;border-bottom:1px solid #e8e5ed;vertical-align:top;overflow-wrap:anywhere}}th{{background:#eeeaf4}}.error{{color:#ad2433}}.warning{{color:#8f630e}}.info{{color:#166d73}}.scroll{{overflow:auto;border-radius:14px;border:1px solid #ddd9e5}}footer{{margin:2rem 0;color:#657080;font-size:.85rem}}</style></head>
<body><main><p class="sub">ENGINEERING PORTFOLIO / REPRODUCIBLE AUDIT</p><h1>SEO operations health</h1><p class="sub">{esc(report['target'])} · {esc(report['created_at'])} · {esc(report['mode'])} mode</p>
<section class="metrics"><div class="metric">Pages checked<strong>{report['pages_checked']}</strong></div><div class="metric">Errors<strong>{report['counts']['error']}</strong></div><div class="metric">Warnings<strong>{report['counts']['warning']}</strong></div><div class="metric">Status<strong>{esc(report['status'].upper())}</strong></div></section>
<div class="scroll"><table><thead><tr><th>Severity</th><th>Check</th><th>Page</th><th>Explanation</th></tr></thead><tbody>{rows}</tbody></table></div>
<footer>Checks identify markup and technical signals. They do not prove Google's indexing, ranking or rich-result eligibility. Demo data is fictional.</footer></main></body></html>'''


def notify(report, webhook=None):
    url = webhook or os.getenv('SEO_OPS_WEBHOOK_URL', '')
    if not url or report['counts']['error'] == 0:
        return False
    payload = {'text': f'SEO audit FAILED: {report["counts"]["error"]} error(s), {report["counts"]["warning"]} warning(s). Target: {report["target"]}. Check GitHub Actions artifact.'}
    request = Request(url, data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'}, method='POST')
    with urlopen(request, timeout=12):
        pass
    return True
