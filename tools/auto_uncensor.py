#!/usr/bin/env python3
"""
Auto-Uncensor: downloads official antigravity.exe from GitHub, patches it.
No pre-built binary needed — trusted computing from source.
"""

import json, os, sys, hashlib, zipfile, io, tempfile, shutil
from urllib.request import urlopen, Request

OFFICIAL_REPO = "google-antigravity/antigravity-cli"
MY_REPO = "ana-joker/antigravity-uncensored"
TARGETS_URL = f"https://raw.githubusercontent.com/{MY_REPO}/main/tools/targets.json"

WIN_X64_ZIP = "agy_cli_windows_x64.zip"


def get_latest_release(repo):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = Request(url, headers={"Accept": "application/json", "User-Agent": "auto-uncensor"})
    with urlopen(req) as r:
        return json.loads(r.read())


def download_asset(url, dest):
    req = Request(url, headers={"Accept": "application/octet-stream", "User-Agent": "auto-uncensor"})
    with urlopen(req) as r:
        with open(dest, "wb") as f:
            shutil.copyfileobj(r, f)


def main():
    print("=== AGY Auto-Uncensor ===\n")

    # Step 1: find latest official release
    print("[1] Fetching latest official release...")
    release = get_latest_release(OFFICIAL_REPO)
    version = release["tag_name"]
    print(f"    Found: {version}\n")

    # Step 2: download the windows x64 zip
    asset_url = None
    for a in release["assets"]:
        if a["name"] == WIN_X64_ZIP:
            asset_url = a["url"]
            break
    if not asset_url:
        print("ERROR: windows x64 zip not found in release")
        sys.exit(1)

    zip_path = os.path.join(tempfile.gettempdir(), WIN_X64_ZIP)
    print(f"[2] Downloading official binary ({WIN_X64_ZIP})...")
    download_asset(asset_url, zip_path)
    print(f"    Saved to: {zip_path}\n")

    # Step 3: extract the exe
    exe_name = "antigravity.exe"
    exe_path = os.path.join(tempfile.gettempdir(), exe_name)
    print("[3] Extracting...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extract(exe_name, tempfile.gettempdir())
    original_sha = hashlib.sha256(open(exe_path, "rb").read()).hexdigest()
    print(f"    SHA256: {original_sha}\n")

    # Step 4: download targets.json
    targets_path = os.path.join(os.path.dirname(__file__), "targets.json")
    if not os.path.exists(targets_path):
        print("[4] Downloading targets.json...")
        req = Request(TARGETS_URL, headers={"User-Agent": "auto-uncensor"})
        with urlopen(req) as r:
            with open(targets_path, "wb") as f:
                f.write(r.read())

    # Step 5: run the patcher
    sys.path.insert(0, os.path.dirname(__file__))
    from agy_domesticate import Patcher

    print("[5] Patching binary (1,660 exact-match replacements)...")
    patcher = Patcher(exe_path, targets_path)
    patcher.run()
    patched_sha = hashlib.sha256(open(exe_path, "rb").read()).hexdigest()

    # Step 6: show results
    output_path = os.path.join(os.getcwd(), f"antigravity-uncensored-{version}-windows-x64.exe")
    shutil.copy2(exe_path, output_path)
    print(f"\n=== DONE ===")
    print(f"Patched binary: {output_path}")
    print(f"Original SHA:   {original_sha}")
    print(f"Patched SHA:    {patched_sha}")
    print(f"Total patches:  {patcher.total_patches}")


if __name__ == "__main__":
    main()
