# Performance Budgets

| Metric | Budget | Measured by | Enforced |
| --- | --- | --- | --- |
| Initial JS (app route) | ≤ 200 KB gzip | size-limit | CI fail |
| Viewer chunk | ≤ 350 KB gzip | size-limit | CI fail |
| LCP (p75 real users) | ≤ 2.5 s | web-vitals → CloudWatch RUM | alert |
| INP (p75) | ≤ 200 ms | RUM | alert |
| CLS (p75) | ≤ 0.1 | RUM | alert |
| Lighthouse (public pages) | ≥ 90 perf, ≥ 95 a11y | Lighthouse CI | CI fail |
| GLB size | ≤ 5 MB compressed | check_glb_regions.py | CI fail |
| Model load on 4G | ≤ 3 s | Playwright with throttling | report |
| FPS | ≥ 50 desktop, ≥ 30 mid-range mobile | manual + perf overlay | release check |
| Draw calls | ≤ 100 | renderer.info | dev check |
