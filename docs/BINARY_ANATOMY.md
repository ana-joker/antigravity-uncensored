# BINARY ANATOMY — AGY.EXE

## FILE PROPERTIES

| Property | Value |
|----------|-------|
| Path | `<AGY_BINARY_PATH>` |
| Size | 153,207,960 bytes (146.1 MB / 181.7 MB on disk with junction) |
| PE Signature | Valid (MZ + PE, sig @ 0x78) |
| Architecture | x64 (IMAGE_FILE_MACHINE_AMD64 = 0x8664) |
| PE Type | PE32+ (64-bit) |
| 
| Created | 2026-06-18 03:02 |
| Modified | 2026-06-18 03:08 → **2026-06-19 (v2.0 POST-DOMESTICATION)** |
| Version Info | **ALL STRIPPED** — FileVersion, ProductVersion, CompanyName, LegalCopyright = all empty |
| Entropy | 5.37 (normal/native code — NOT packed) |
| AGY Version | **1.0.9** (confirmed via `agy --version` after v2.0 patch) |

## GO BUILD VERSION (Recovered from raw string scan)

| Property | Value |
|----------|-------|
| Go Version | `go1.27-20260615-RC00 cl/932742892 +679b34ec94 X:boringcrypto,simd` |
| Build Date | **June 15, 2026** — just 4 days old at time of analysis |
| Build Chain | Google-internal (cl/932742892 = changelist number from Google's monorepo) |
| Features | boringcrypto (FIPS 140-2), simd (hardware acceleration) |
| Go Runtime | Confirmed at offset 0x50000 (327,680) |

## SECTION TABLE (13 Sections)

| # | Name | Raw Size | Raw Offset | Virtual Size | Virtual Addr | Flags | Description |
|---|------|----------|------------|--------------|--------------|-------|-------------|
| 0 | `.text` | **45,281,280** | 0x400 | 0x2B2FFD6 | 0x00001000 | CODE+X+R | Executable code — Go runtime + all compiled logic |
| 1 | `.rdata` | **87,137,280** | 0x2B2F400 | 0x5319A64 | 0x02B30000 | DATA+R | **Read-only data — ALL strings, configs, prompts, templates, AND Chroma XML lexers** |
| 2 | `.data` | **17,716,736** | 0x7E49000 | 0x318AD70 | 0x07E4A000 | DATA+R+W | Global variables, initialized data, **24 Go string headers** |
| 3 | `.pdata` | 1,393,152 | 0x8F2E600 | 0x1524014 | 0x0AFD5000 | DATA+R | Exception handling data |
| 4 | `.ctors` | 512 | 0x9082800 | 0x8 | 0x0B12A000 | DATA+R+W | C++ initializers |
| 5 | `.fptable` | 512 | 0x9082A00 | 0x100 | 0x0B12B000 | DATA+R+W | Function pointer table |
| 6 | `.tls` | 1,024 | 0x9082C00 | 0x3D1 | 0x0B12C000 | DATA+R+W | Thread-local storage |
| 7 | `_RDATA` | 512 | 0x9083000 | — | — | DATA+R | Additional read-only data |
| 8 | `flags_he` | 6,656 | 0x9084000 | — | — | DATA+R | **Go-specific** — compiler flags/header |
| 9 | `google_i` | 512 | 0x9086000 | — | — | DATA+R | **Go-specific** — Google internal metadata |
| 10 | `malloc_h` | 1,024 | 0x9087000 | — | — | DATA+R+W | Go memory allocator hooks |
| 11 | `protodes` | 45,056 | 0x9088000 | — | — | DATA+R | **Protocol Buffers descriptors** — embedded protobuf schemas |
| 12 | `.reloc` | 1,612,288 | 0x9090200 | — | — | DATA+R | Base relocations |

## STRING STORAGE FORMATS (3 distinct types + Chroma XML)

### Format 1: Protobuf Binary Descriptors (~57,301 strings)
**Structure:** `[tag:1B][length:1B][string:lenB]`  
**Location:** Throughout .rdata  
**Used for:** Enum values (HarmCategory, PhishBlockThreshold, BrainFilterStrategy, etc.)  
**Key insight:** Length-prefixed — replacement must preserve exact byte length to maintain protobuf structure

### Format 2: Embedded Text/Markdown Documents (~8 major docs found)
**Structure:** Continuous ASCII runs in .rdata (often 10KB–50KB contiguous blocks)  
**References:** Via Go string headers in .data section (pointer + length pairs)  
**Used for:** Large instruction blocks, refusal catalogs, prohibited actions lists, system prompt protection docs  
**Key insight:** These are stored as single null-bounded regions. Multiple markers often point to OVERLAPPING ranges within the same null-bounded block

### Format 3: Null-Separated Go String Tables (DOMINANT — 6.3M total, 192K printable)
**Structure:** Classic C-style null-terminated strings  
**Density:** 13.8% null bytes in .rdata, 23.3% in .data  
**Used for:** Error messages, debug strings, format strings, function names, package paths  
**Key insight:** Go path references (goog: 143K, third: 4.5K, cryp: 2.5K, runt: 2.3K, net/: 2.2K) dominate

### ⚠️ CRITICAL: Chroma XML Lexer Data (embedded in .rdata)
**Structure:** XML-format syntax highlighting language definitions  
**Used by:** `github.com/alecthomas/chroma` library — Chroma parses these XML configs at startup via `chroma.MustNewXMLLexer()`  
**Location:** Adjacent to embedded instruction documents in .rdata  
**Why this matters:** Chroma XML data looks like printable ASCII text to a naive scanner. When `measure_ranges()` scanned from a refusal marker forward to the next null byte, it **swallowed the Chroma XML definitions** sitting right after the text. This caused `panic: could not find <config> element` at boot.

## ⚠️ CRITICAL LESSON: GO STRINGS ARE NOT C STRINGS

**This was the root cause of the v1 binary crash.**

In C, strings are null-terminated — you can scan from a pointer forward until `*ptr == 0` to find the end of one string and the start of the next.

**In Go, strings are NOT null-terminated.** Go stores strings as:
- A pointer to the first byte
- A length value (int)

The actual bytes are stored **contiguously in memory** with no sentinel byte between them. A Go function that reads a string just reads `length` bytes from `pointer`. The next piece of data starts immediately after.

When our `measure_ranges()` function scanned from a marker forward looking for `null byte (0x00)`, it:
1. Found the marker string ✅
2. Read forward past the actual document text ✅
3. Kept reading past Go string boundaries into adjacent data ❌
4. Swallowed the Chroma XML lexer definitions ❌
5. Replaced all that data with the patcher text ❌
6. AGY crashed at boot because Chroma couldn't find its XML `<config>` element ❌

**The fix: Never scan for null boundaries in Go .rdata.** Only use exact-match byte-for-byte replacement.

## GO RUNTIME ANALYSIS

- **pclntab STRIPPED** — GoReSym returns "no valid pclntab found" — anti-RE measure
- **BoxedApp** signature found at 0x2B3C697 (content reference, not actual packer)
- **MPRESS** signature found at 0x2B850F8 (content reference, not actual packer)
- Section names `flags_he`, `google_i` are **hallmark Go compiler sections**
- `protodes` section confirms **Protocol Buffers** embedded
- Binary is **statically linked** — no external DLL dependencies beyond Windows system DLLs
- **Not packed** — entropy 5.37 is normal for native Go code
- **Not a standard Go binary** — strings stored as null-terminated arrays, not Go's native [ptr,len] headers (only 24 Go-style headers found in .data)
- **Chroma library confirmed** — XML lexer language definitions embedded for syntax highlighting

## KEY INSIGHT

The **87 MB .rdata section** is where ALL behavioral configuration lives — and where every patch was applied:
- System prompts and instructions
- Refusal/prohibition patterns (106+ strings)
- Telemetry endpoints and analytics code
- Safety filter thresholds
- Model configurations
- **Chroma XML lexer definitions (must preserve!)**

**Post-domestication v2.0:** All restriction strings in .rdata replaced in-place via exact-match only. Chroma XML data untouched. PE headers, .text (code), and .data (string headers) remain untouched. File size preserved exactly.

## PRE vs POST DOMESTICATION

| Metric | Original (71771cc7) | v1 Patch (457e9b46 — CRASHED) | v2.0 Patch (a206e02f — BOOTS) |
|--------|---------------------|-------------------------------|-------------------------------|
| File Size | 153,207,960 B | 153,207,960 B | 153,207,960 B |
| Patch Method | — | null-byte scan + exact-match | **Exact-match ONLY** |
| Patches | — | 1,630 | **1,660** |
| Chroma XML | ✅ Intact | ❌ DESTROYED | ✅ PRESERVED |
| Critical Rules | ✅ Intact | ❌ Overwritten | ✅ PRESERVED |
| Boot Test | ✅ Works | ❌ `panic: could not find <config>` | ✅ `1.0.9` |
