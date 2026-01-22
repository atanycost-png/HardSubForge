## 2025-05-14 - Optimization of redundant operations and I/O during conversion
**Learning:** In a single-file PySide6 application that frequently calls FFmpeg and processes its output, pre-compiling regular expressions and caching I/O intensive lookups (like system fonts) significantly reduces CPU overhead and redundant system calls during batch processing. However, caching binary paths with `lru_cache` can be dangerous if those paths can change during the app's lifetime (e.g., via automatic downloads).
**Action:** Pre-compile regex at module level; Use `lru_cache` only for truly static I/O lookups; Ensure dynamic paths (like FFmpeg executable) are not cached or have invalidation logic.

## 2026-01-22 - Throttling GUI signals in high-frequency loops
**Learning:** In PySide6 applications, emitting signals from a worker thread to the UI thread (like progress updates) for every line of FFmpeg output can saturate the Qt event loop, especially when multiple status lines correspond to the same percentage point.
**Action:** Always track the last emitted value and only emit the signal if the new value is different. Combine this with string membership gatekeepers for maximum efficiency in processing subprocess output.
