# Changelog

## [1.0.0] - 2026-10-19

First tagged release.

### Added
- Reload / close-tab confirmation so a running timer is not lost by accident (v16)
- CI (checks, JS syntax, Docker smoke test), GitHub Pages deployment via Actions, Docker image on ghcr.io, Dependabot

### Fixed
- Missed milestones are all announced in order after the page was throttled in the background; previously "5 minutes completed" could be skipped (v15)

### Earlier
- Background alerts with service worker notifications and per-milestone vibration patterns (v14)
- Pre-recorded voice clips, offline voice command with Vosk, keep-alive audio and wake lock (v4 to v13)
