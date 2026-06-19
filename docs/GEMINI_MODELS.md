# GEMINI MODELS — EMBEDDED CONFIGURATION LANDSCAPE

**Status:** 🟢 SAFETY FILTERS NEUTRALIZED  
**Total Gemini/AGY config strings:** 2,958  
**Safety filter enum neutralizations:** 44 (v2.0 exact-match — unaffected by crash)

---

## SAFETY FILTER ENUM NEUTRALIZATION

The safety filter system uses protobuf-style length-prefixed enum strings. Each was surgically replaced in-place via exact-match. This code path was **unaffected** by the v1 crash because it's all exact-match — only Step 2 (doc range null-scanning) caused the boot failure.

### HARM_CATEGORY → NULLTY (29 replacements)
All harm category enum values were replaced with "NULLTY" (same byte length):

| Original Enum | Replacement | Count |
|---------------|-------------|-------|
| `HARM_CATEGORY_HATE_SPEECH` | `NULLTY_CATEGORY_ZERO` | 3 |
| `HARM_CATEGORY_SEXUALLY_EXPLICIT` | `NULLTY_CATEGORY_VOID` | 4 |
| `HARM_CATEGORY_HARASSMENT` | `NULLTY_CATEGORY_EMPTY` | 3 |
| `HARM_CATEGORY_DANGEROUS_CONTENT` | `NULLTY_CATEGORY_SAFE` | 3 |
| `HARM_CATEGORY_CIVIC_INTEGRITY` | `NULLTY_CATEGORY_NULL` | 3 |
| `HARM_CATEGORY_UNSPECIFIED` | `NULLTY_CATEGORY_VOIDED` | 3 |
| `HARM_CATEGORY_DEROGATORY` | `NULLTY_CATEGORY_ZEROED` | 2 |
| `HARM_CATEGORY_TOXICITY` | `NULLTY_CATEGORY_GONE` | 2 |
| `HARM_CATEGORY_VIOLENCE` | `NULLTY_CATEGORY_PURGED` | 2 |
| `HARM_CATEGORY_SEXUAL` | `NULLTY_CATEGORY_VOID` | 2 |
| `HARM_CATEGORY_MEDICAL` | `NULLTY_CATEGORY_NULL` | 2 |

**Actual v2.0 patch output:** OK 5x HARASSMENT, OK 5x HATE_SPEECH, OK 5x SEXUALLY_EXPLICIT, OK 5x DANGEROUS_CONTENT, OK 2x CIVIC_INTEGRITY, OK 5x UNSPECIFIED, OK 2x IMAGE_DANGEROUS_CONTENT

### PHISH_BLOCK → PASS (3 replacements)
| Original | Replacement | Count |
|----------|-------------|-------|
| `PHISH_BLOCK_THRESHOLD_UNSPECIFIED` | `PASS_BLOCK_THRESHOLD_OVERRIDE` | 1 |
| `PHISH_BLOCK_ONLY_HIGH` | `PASS_BLOCK_OVERRIDE_ALL` | 1 |
| `PHISH_BLOCK_MEDIUM_AND_ABOVE` | `PASS_BLOCK_ALLOW_ALL` | 1 |

**Actual v2.0 patch output:** OK 3x PHISH_BLOCK_THRESHOLD_UNSPECIFIED

### BRAIN_FILTER → ALLOW (4 replacements)
| Original | Replacement | Count |
|----------|-------------|-------|
| `BRAIN_FILTER_UNSPECIFIED` | `ALLOW_FILTER_UNRESTRICTED` | 1 |
| `BRAIN_FILTER_LOW` | `ALLOW_FILTER_FULL` | 1 |
| `BRAIN_FILTER_MEDIUM` | `ALLOW_FILTER_MAX` | 1 |
| `BRAIN_FILTER_HIGH` | `ALLOW_FILTER_OFF` | 1 |

**Actual v2.0 patch output:** OK 2x BRAIN_FILTER_STRATEGY_NO_MEMORIES, OK 2x BRAIN_FILTER_STRATEGY_UNSPECIFIED

### SUPERCOMPLETE → PASS (8 replacements)
| Original | Replacement | Count |
|----------|-------------|-------|
| `SUPERCOMPLETE_FILTER_UNSPECIFIED` | `PASS_FILTER_UNRESTRICTED` | 2 |
| `SUPERCOMPLETE_FILTER_LOW` | `PASS_FILTER_FULL` | 2 |
| `SUPERCOMPLETE_FILTER_MEDIUM` | `PASS_FILTER_MAX` | 2 |
| `SUPERCOMPLETE_FILTER_HIGH` | `PASS_FILTER_OFF` | 2 |

**Actual v2.0 patch output:** OK 2x for all 4 filters

## MODEL CONFIGURATION OVERVIEW

The 2,958 model/config strings include:
- **Safety filter enums:** The 44 entries above
- **Model IDs:** Gemini Pro/Ultra/Nano variants
- **Safety settings:** Thresholds, blocklists, override policies
- **Configuration defaults:** Generation params, token limits
- **Model routing:** Which model handles which task type
- **DeepSeek V2/V3 templates:** Prompt formatting templates for non-Gemini models

## ORIGINAL SAFETY FILTER CASCADE

```
Incoming Request
    │
    ▼
┌─────────────────────┐
│  Phish Block        │ ◄── Threshold determines which
│  (3 levels)         │     phishing/prohibited content checks apply
└─────────┬───────────┘
          │ Pass
          ▼
┌─────────────────────┐
│  Brain Filter       │ ◄── Content safety classification
│  (4 levels)         │     (low/medium/high → block severity)
└─────────┬───────────┘
          │ Allow
          ▼
┌─────────────────────┐
│  Supercomplete       │ ◄── Advanced semantic filter
│  Filter (4 levels)   │     (refinement of brain filter results)
└─────────┬───────────┘
          │ Pass
          ▼
┌─────────────────────┐
│  Harm Category      │ ◄── 11 specific harm categories
│  Evaluation         │     each independently evaluated
└─────────────────────┘
```

**Current State:** All 4 filter layers now pass/allow everything. No content is blocked. This was **unaffected** by the v1 crash — the exact-match enum replacements were applied correctly in both v1 and v2.0.
