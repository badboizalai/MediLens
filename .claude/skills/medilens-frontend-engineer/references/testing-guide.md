# Frontend Testing Guide

| Layer | Tool | What |
| --- | --- | --- |
| Unit | Vitest | utils (severity mapping, FDI layout, unit conversions), hooks |
| Component | Testing Library | states, interactions, a11y roles/names |
| Stories | Storybook + test runner | every Design System and feature component state |
| E2E (mocked) | Playwright + MSW | flows: register → consent → upload → review → viewer → share |
| E2E (staging) | Playwright | smoke after deploy |
| Visual | Playwright `toHaveScreenshot` | each Unit plugin at camera presets; threshold 0.2% |
| A11y | @axe-core/playwright | 0 serious/critical on every route |
| Cross-browser | Playwright projects chromium/webkit/firefox + Pixel/iPhone viewports | main flows |

Tips: deterministic 3D screenshots → fixed DPR, disable animations, wait for `viewer:ready` event, `frameloop="demand"`.
Flaky test rule: quarantine within 24 h, fix root cause within the sprint.
