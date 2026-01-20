## 2025-05-14 - Optimization of redundant operations and I/O during conversion
**Learning:** In a single-file PySide6 application that frequently calls FFmpeg and processes its output, pre-compiling regular expressions and caching I/O intensive lookups (like system fonts) significantly reduces CPU overhead and redundant system calls during batch processing. However, caching binary paths with `lru_cache` can be dangerous if those paths can change during the app's lifetime (e.g., via automatic downloads).
**Action:** Pre-compile regex at module level; Use `lru_cache` only for truly static I/O lookups; Ensure dynamic paths (like FFmpeg executable) are not cached or have invalidation logic.

## 2025-05-15 - Throttling and Gatekeepers for FFmpeg output processing
**Learning:** Verbose output from FFmpeg can saturate the GUI main thread if every line triggers a regex search and a signal emission. Throttling progress signals to only emit on integer changes and using string membership as a "gatekeeper" before regex searches measurably reduces CPU usage and improves UI responsiveness during long conversions.
**Action:** Use 'time=' and 'Duration' gatekeepers for FFmpeg output parsing; implement 'last_percent' tracking to throttle GUI signals in worker threads.
