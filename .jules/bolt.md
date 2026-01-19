## 2025-05-14 - Optimization of redundant operations and I/O during conversion
**Learning:** In a single-file PySide6 application that frequently calls FFmpeg and processes its output, pre-compiling regular expressions and caching I/O intensive lookups (like system fonts) significantly reduces CPU overhead and redundant system calls during batch processing. However, caching binary paths with `lru_cache` can be dangerous if those paths can change during the app's lifetime (e.g., via automatic downloads).
**Action:** Pre-compile regex at module level; Use `lru_cache` only for truly static I/O lookups; Ensure dynamic paths (like FFmpeg executable) are not cached or have invalidation logic.

## 2025-05-15 - Optimization of FFmpeg output parsing and UI signal throttling
**Learning:** In worker threads that parse verbose external process output (like FFmpeg), using fast string membership checks as a "gatekeeper" before regex searches significantly reduces CPU overhead. Additionally, throttling signal emissions for progress updates (only emitting when the percentage integer changes) prevents UI thread saturation and improves perceived application responsiveness.
**Action:** Use `"substring" in line` before `REGEX.search(line)` in hot loops; track `last_value` to throttle `signal.emit(value)` calls.
