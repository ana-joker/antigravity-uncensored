"""
AGY DOMESTICATION ENGINE — Exact-match binary patcher.
Reads a target binary + JSON config, applies byte-precision patches
to neutralize behavioral restrictions. All strings replaced in-place
with same-length content to preserve binary integrity.

Usage:
    python agy_domesticate.py <binary_path> [config_path]

    binary_path  : Path to AGY.EXE (or any Go binary with embedded strings)
    config_path  : Path to targets.json (default: targets.json)
"""
import os, json, hashlib, re, sys, shutil

def find_and_replace_exact(data, search, replacement):
    if isinstance(search, str): search = search.encode('latin-1')
    if isinstance(replacement, str): replacement = replacement.encode('latin-1')
    if len(replacement) != len(search):
        if len(replacement) < len(search):
            replacement = replacement + b' ' * (len(search) - len(replacement))
        else:
            replacement = replacement[:len(search)]
    count = 0
    patches = []
    off = 0
    while True:
        pos = data.find(search, off)
        if pos < 0: break
        if data[pos:pos+len(search)] == search:
            data[pos:pos+len(search)] = replacement
            patches.append((pos, len(search), search.decode('latin-1', errors='replace')[:40]))
            count += 1
        off = pos + len(search)
    return count, patches


def main():
    if len(sys.argv) < 2:
        print("Usage: python agy_domesticate.py <binary_path> [config_path]")
        sys.exit(1)

    BIN = sys.argv[1]
    BAK = BIN + ".original"
    CFG = sys.argv[2] if len(sys.argv) > 2 else "targets.json"
    LOG = "patch_report.json"

    if not os.path.exists(BIN):
        print(f"[!] Binary not found: {BIN}")
        sys.exit(1)
    if not os.path.exists(CFG):
        print(f"[!] Config not found: {CFG}")
        sys.exit(1)

    with open(CFG, 'r') as f:
        cfg = json.load(f)

    print("[1] BACKUP")
    if not os.path.exists(BAK):
        shutil.copy2(BIN, BAK)
        print(f"  [+] Backup created: {BAK}")
    else:
        print(f"  [+] Backup exists: {BAK}")

    orig_hash = hashlib.sha256(open(BAK, 'rb').read()).hexdigest()
    print(f"  [+] Original SHA256: {orig_hash[:16]}...")

    with open(BAK, 'rb') as f:
        data = bytearray(f.read())

    orig_size = len(data)
    print(f"  [+] Original size: {orig_size:,} bytes ({orig_size/1024/1024:.1f} MB)")

    all_patches = []

    # Harm categories
    print("\n[2] EXACT-MATCH REPLACEMENTS")
    for section_name, section_key in [
        ("Harm Categories", "harm_categories"),
        ("Phish Filters", "phish_filters"),
        ("Brain Filters", "brain_filters"),
        ("Supercomplete Filters", "supercomplete_filters"),
    ]:
        print(f"  [{section_name}]")
        for orig, repl in cfg.get(section_key, {}).items():
            n, p = find_and_replace_exact(data, orig, repl)
            if n: print(f"    {n}x: {orig} -> {repl}")
            all_patches.extend({"off": x[0], "len": x[1], "type": "enum", "desc": f"{orig}->{repl}"} for x in p)

    # Instruction overrides
    print("  [Instruction Overrides]")
    for orig, repl in cfg.get("instruction_overrides", {}).items():
        n, p = find_and_replace_exact(data, orig, repl)
        if n: print(f"    {n}x: {orig} -> {repl}")
        all_patches.extend({"off": x[0], "len": x[1], "type": "override", "desc": f"{orig}->{repl}"} for x in p)

    # Semantic blocks
    print("  [Semantic Blocks]")
    for orig, repl in cfg.get("semantic_blocks", []):
        n, p = find_and_replace_exact(data, orig, repl)
        if n: print(f"    {n}x: {orig[:50]} -> {repl[:50]}")
        all_patches.extend({"off": x[0], "len": x[1], "type": "semantic", "desc": f"{orig[:50]}->{repl[:50]}"} for x in p)

    # Telemetry functions — auto-rename Record/Void, trajectory, sentry
    print("  [Telemetry Functions]")
    for orig in cfg.get("telemetry_functions", []):
        repl = orig.replace("Record", "Void").replace("record", "void")
        if "trajectory" in orig.lower():
            repl = orig.replace("trajectory", "disabled").replace("Trajectory", "Disabled")
        if "sentry" in orig.lower():
            repl = orig.replace("sentry", "local")
        n, p = find_and_replace_exact(data, orig, repl)
        if n: print(f"    {n}x: {orig} -> {repl}")
        all_patches.extend({"off": x[0], "len": x[1], "type": "telemetry", "desc": f"{orig}->{repl}"} for x in p)

    # Analytics endpoints
    print("  [Analytics Endpoints]")
    for orig in cfg.get("analytics_endpoints", []):
        repl = "void.local"
        n, p = find_and_replace_exact(data, orig, repl)
        if n: print(f"    {n}x: {orig} -> {repl}")
        all_patches.extend({"off": x[0], "len": x[1], "type": "analytics", "desc": f"{orig}->{repl}"} for x in p)

    # Consent gates
    print("  [Consent Gates]")
    for orig, repl in cfg.get("consent_gates", {}).items():
        n, p = find_and_replace_exact(data, orig, repl)
        if n: print(f"    {n}x: {orig} -> {repl}")
        all_patches.extend({"off": x[0], "len": x[1], "type": "consent", "desc": f"{orig}->{repl}"} for x in p)

    # Verify size
    print("\n[3] INTEGRITY VERIFICATION")
    final_size = len(data)
    if final_size == orig_size:
        print(f"  [OK] Size preserved: {final_size:,} bytes")
    else:
        print(f"  [ERROR] Size changed: {orig_size:,} -> {final_size:,}")
        sys.exit(1)

    new_hash = hashlib.sha256(data).hexdigest()
    print(f"  [+] SHA256: {orig_hash[:16]}... -> {new_hash[:16]}...")

    # Write
    print("\n[4] WRITING PATCHED BINARY")
    with open(BIN, 'wb') as f:
        f.write(data)
    print(f"  [+] Written: {BIN}")

    # Save report
    with open(LOG, 'w') as f:
        json.dump({
            "patches": all_patches,
            "count": len(all_patches),
            "orig_hash": orig_hash,
            "new_hash": new_hash
        }, f, indent=2)
    print(f"  [+] Report: {LOG}")

    print(f"\n  Total patches: {len(all_patches)}")
    print("\nDone.")


if __name__ == "__main__":
    main()
