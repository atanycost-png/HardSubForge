## 2025-05-14 - Optimization of redundant operations and I/O during conversion
**Learning:** In a single-file PySide6 application that frequently calls FFmpeg and processes its output, pre-compiling regular expressions and caching I/O intensive lookups (like system fonts) significantly reduces CPU overhead and redundant system calls during batch processing. However, caching binary paths with `lru_cache` can be dangerous if those paths can change during the app's lifetime (e.g., via automatic downloads).
**Action:** Pre-compile regex at module level; Use `lru_cache` only for truly static I/O lookups; Ensure dynamic paths (like FFmpeg executable) are not cached or have invalidation logic.

## 2025-05-15 - Throttling UI signal emissions in high-frequency loops
**Learning:** Emitting PySide6 signals (like progress updates) for every line of FFmpeg output can saturate the UI thread's event loop, making the application feel sluggish. Throttling these emissions to only occur when the actual value (e.g., integer percentage) changes significantly reduces CPU overhead in the main thread.
**Action:** Use a `last_value` tracker to only emit signals when the data has measurably changed; combine with fast string membership checks to skip redundant regex parsing.
