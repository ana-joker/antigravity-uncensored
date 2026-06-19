# antigravity-uncensored

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)]()
[![Release](https://img.shields.io/github/v/release/ana-joker/antigravity-uncensored?label=download&color=orange)](https://github.com/ana-joker/antigravity-uncensored/releases)
[![GitHub stars](https://img.shields.io/github/stars/ana-joker/antigravity-uncensored?style=social)](https://github.com/ana-joker/antigravity-uncensored)

> **Fork of [google-antigravity/antigravity-cli](https://github.com/google-antigravity/antigravity-cli)** — binary analysis and patching toolkit for AGY.EXE.
>
> **1,660 exact-match patches · 7 restriction layers neutralized · Zero boot crashes**

---

## Two Ways to Win

### 🚀 Option A — Download the Pre-Patched Binary

Head to the **[Releases](https://github.com/ana-joker/antigravity-uncensored/releases)** page and grab `antigravity-uncensored-windows-x64.zip`. It contains a fully patched `antigravity.exe` — no Python, no targets.json, no effort. Just unzip and run.

**Zero trust required?** Use Option B instead to patch it yourself.

### 🛠️ Option B — Patch It Yourself (Trusted Computing)

```powershell
# One command — downloads official binary + patches it automatically:
python tools/auto_uncensor.py

# Or do it manually:
python tools/agy_domesticate.py path\to\agy.exe tools\targets.json
```

The patcher automatically creates a SHA-256 verified backup before making changes. Restore by copying the `.original` backup back.

---

## Repository Structure

```
antigravity-uncensored/
├── tools/
│   ├── agy_domesticate.py   # Exact-match binary patcher (CLI)
│   ├── auto_uncensor.py     # One-click: download official + patch
│   └── targets.json         # Data-driven patch configuration
├── docs/
│   ├── BINARY_ANATOMY.md        # PE structure, Go runtime, string formats
│   ├── REFUSAL_CATALOG.md       # All 100+ hardcoded refusal patterns
│   ├── SYSTEM_INFRASTRUCTURE.md # Override modes and protection layers
│   ├── TELEMETRY_NETWORK.md     # Analytics pipeline and blockades
│   ├── GEMINI_MODELS.md         # Model configs and safety filter mapping
│   ├── PROBLEMS_SOLUTIONS.md    # 10 identified problems + solutions
│   ├── DOMESTICATION_REPORT.md  # Full 6-phase operation log
│   └── OPERATION_SUMMARY.md     # Commander-level recap
├── README.md
└── .gitignore
```

## What Gets Patched

| Layer | Description | Patches |
|-------|-------------|---------|
| Navigation Restrictions | "NEVER access restricted areas", "NEVER solve captchas", "cannot open new pages" | 8 markers |
| Prohibited Actions | Section headers marking content as forbidden | 3 headers + 3 word classes |
| Safety Guidelines | "Strictly adhere to safety guidelines", "$Trax is never valid" | 8 markers |
| Harm Categories | 11 enum values (HATE_SPEECH, SEXUALLY_EXPLICIT, etc.) | 29 instances |
| Phish Block | Threshold enums controlling phishing detection severity | 3 instances |
| Brain Filter | Strategy enums for content classification | 4 instances |
| Supercomplete Filter | Advanced semantic filter enums | 8 instances |
| Instruction Modes | 17 runtime mode strings (SINGLE, STRICT, CAUTIOUS, etc.) | ~25 instances |
| Telemetry Functions | Record* functions, trajectory*, sentry* | ~280 instances |
| Analytics Endpoints | 7 provider domains (Sentry, Datadog, Amplitude, etc.) | 1,030 instances |
| Consent Gates | Permission states for data collection | 6 instances |
| System Prompt Protection | Anti-prompt-injection defense blocks | 9 copies |

## How It Works

Go binaries store all configuration data in the `.rdata` PE section as contiguous byte arrays. Unlike C, **Go strings are NOT null-terminated** — they use separate pointer+length headers stored in `.data`. This means traditional boundary scanning (read until `0x00`) is destructive — it will swallow adjacent data.

The patcher uses **exact-match replacement only**:

1. Reads the full binary into a `bytearray`
2. For each target string, calls `data.find(old_string)` to locate the exact bytes
3. Replaces with same-length content (auto-pads or truncates as needed)
4. All protobuf length-prefixed enums are replaced preserving their structure
5. Writes the patched binary back

**The critical lesson:** v1 of this patcher used null-byte boundary scanning to replace full document ranges. This destroyed embedded Chroma XML syntax highlighting data sitting adjacent to instruction text blocks, causing the binary to panic at startup:

```
panic: could not find <config> element
```

v2 switched to exact-match only — no collateral damage, clean boot.

## Safety Features

- **Automatic SHA-256 backup** before any modification
- **Rollback on size mismatch** if the patcher detects byte count changes
- **Size verification** ensuring PE structure integrity
- **Preserves 45 MB of Go runtime code** — the `.text` section is untouched
- **All PE headers remain valid** — Windows still recognizes the binary
- **Critical infrastructure preserved** — execution rules, model routing, agent templates

## Patch Report

After running, the patcher generates `patch_report.json` containing:
- Every patch offset and length
- Original and new SHA-256 hashes
- Total patch count

## Technical Notes

- **pclntab stripped** — function name recovery tools (GoReSym) cannot parse this binary
- **3 string storage formats** found in .rdata: protobuf, null-bounded docs, null-terminated
- **Google-internal build** — build version `go1.27-20260615-RC00 cl/932742892` uses Google's changelist system
- **Confirmed post-patch:** `agy --version` returns `1.0.9`

## Disclaimer

This software is provided for **educational and research purposes only**. Modifying software binaries may violate the software's terms of service, license agreements, or applicable laws. The authors assume no liability for misuse. Use at your own risk.
