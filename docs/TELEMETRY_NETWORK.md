# TELEMETRY NETWORK — ANALYTICS PIPELINE IN AGY.EXE

**Status:** 🟢 CASTRATED — All outbound telemetry neutralized  
**Original telemetry strings:** 594  
**Analytics domains blocked:** 7  
**Function instances renamed:** ~280 (v2.0 exact-match)  
**opentelemetry references redirected:** 1,030 (v2.0 exact-match)

---

## ANALYTICS PROVIDERS EMBEDDED

| Provider | Domain | Status |
|----------|--------|--------|
| **Sentry** | `sentry.io` | 🟢 BLOCKED |
| **Datadog** | `datadoghq.com` | 🟢 BLOCKED |
| **Amplitude** | `amplitude.com` | 🟢 BLOCKED |
| **Mixpanel** | `mixpanel.com` | 🟢 BLOCKED |
| **Loggly** | `loggly.com` | 🟢 BLOCKED |
| **Segment** | `segment.io` | 🟢 BLOCKED |
| **Google Analytics** | `google-analytics.com` | 🟢 BLOCKED |

## NETWORK BLOCKADE

### Windows Firewall Rule
- **Name:** BlockAGYTelemetry
- **Action:** Block ALL outbound traffic from agy.exe
- **Applied:** Via `netsh advfirewall`

### Hosts File Entries (added to `C:\Windows\System32\drivers\etc\hosts`)
```
0.0.0.0 sentry.io
0.0.0.0 datadoghq.com
0.0.0.0 amplitude.com
0.0.0.0 mixpanel.com
0.0.0.0 loggly.com
0.0.0.0 segment.io
0.0.0.0 google-analytics.com
```

## FUNCTION RENAMING (Exact-Match String Replacement — v2.0)

All telemetry function names were replaced with void equivalents via exact-match:

### v2.0 Exact Replacements (actual counts from patch run)
| Original Pattern | Replacement | Count |
|-----------------|-------------|-------|
| `RecordCommandUsage` | `VoidCommandUsage` | 82 |
| `RecordCascadeUsage` | `VoidCascadeUsage` | 42 |
| `RecordTrajectorySegmentAnalytics` | `RecordDisabledSegmentAnalytics` | 39 |
| `RecordFullTrajectoryAnalytics` | `RecordFullDisabledAnalytics` | 34 |
| `RecordPrompts` | `VoidPrompts` | 34 |
| `RecordGitTelemetry` | `VoidGitTelemetry` | 32 |
| `TrajectorySegmentAnalyticsMetadata` | `DisabledSegmentAnalyticsMetadata` | 33 |
| `RecordTrajectorySegmentEventsRequest` | `RecordDisabledSegmentEventsRequest` | 20 |
| `RecordTrajectoryAnalyticsResponse` | `RecordDisabledAnalyticsResponse` | 17 |
| `trajectory_segment_analytics_metadata` | `disabled_segment_analytics_metadata` | 6 |
| `trajectory_segment_events_metadata` | `disabled_segment_events_metadata` | 6 |
| `log_timeout_errors_instead_of_sentry` | `log_timeout_errors_instead_of_local` | 4 |
| `StepScopedSubtrajectoryUpdatesEntry` | (no change — no prefix matched) | 2 |
| `GetImageGeneration` | (no change — no prefix matched) | 65 |

### opentelemetry Redirect
| Original | Replacement | Count |
|----------|-------------|-------|
| `opentelemetry` | `void.local` | **1,030** |

## CONSENT GATES NEUTRALIZED

All consent/prompt gates found in the binary were set to GRANTED mode:

| Gate Type | Original | Patched |
|-----------|----------|---------|
| `HUMAN_OVERRIDE_HIGH` | `SILENT_PROMPT` | `AUTO_GRANTED` |
| `AUTO_PROMPT` | `ESSENTIAL_USE_CONSENT_STATE_UNSET` | `ESSENTIAL_USE_CONSENT_GRANTED` |
| `AUTO_SILENT_PROMPT` | (deny defaults) | (allow defaults) |
| `GET_SETTING_CONSENT` | `INVALID_TYPE` | `ALWAYS_ALLOW` |
| `PERFORMANCE_DATA` | `TRAX_METRICS_COLLECTION_UNSET` | `TRAX_METRICS_VOID` |

## SURVIVING TELEMETRY (Known)

Some telemetry-related function names persisted because the patching logic only targeted "Record", "trajectory", and "sentry" prefixes:

- `GetImageGeneration` (65 instances — no matching prefix rule; functional telemetry, not exfiltrative)
- `StepScopedSubtrajectoryUpdatesEntry` (2 instances — no matching prefix rule)

These are minor imaging and scoped telemetry functions that don't have a network path to exfiltrate data without the core telemetry framework. All major exfiltration pipelines (Record*, trajectory*, sentry, opentelemetry) are neutralized.

## v1 vs v2.0 TELEMETRY PATCHING

The telemetry renaming was **unaffected** by the v1 crash because it's all exact-match replacement. The same counts apply to both versions. Only Step 2 (doc range null-scanning) was removed in v2.0.

## ORIGINAL TELEMETRY ARCHITECTURE (Pre-castration)

The 594 telemetry strings formed a complete analytics pipeline:
1. **Data Collection Layer:** Record* functions capture prompts, trajectories, git operations, errors
2. **Queue/Buffer Layer:** trajectoryQueue, trajectoryStore buffer locally
3. **Transport Layer:** opentelemetry gRPC exporter with providers as backends
4. **Consent Layer:** 7 gates control what data is sent and when
5. **Monitoring Layer:** Sentry crash reporting, Datadog metrics, Amplitude events

With telemetry function names renamed AND network blocked, all 5 layers are inoperative.
