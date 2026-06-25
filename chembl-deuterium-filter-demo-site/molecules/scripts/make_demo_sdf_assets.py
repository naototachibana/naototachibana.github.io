#!/usr/bin/env python3
"""Fetch missing SDF files for demo CIDs from PubChem."""
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

def main():
    # __file__ is scripts/make_demo_sdf_assets.py
    # Repo root is 4 levels up: scripts/ -> molecules/ -> pubchem-deuterium-filter/ -> naototachibana.github.io/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
    os.chdir(repo_root)
    
    shard_path = "pubchem-deuterium-filter/molecules/assets/data/shard-00000.json"
    out_dir = Path("pubchem-deuterium-filter/molecules/assets/sdf")
    
    with open(shard_path) as f:
        shard = json.load(f)
    
    cids = [r["cid"] for r in shard]
    total = len(cids)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    existing = 0
    fetched_3d = 0
    fetched_2d = 0
    failed = []
    
    for i, cid in enumerate(cids):
        dest = out_dir / f"{cid}.sdf"
        
        if dest.exists():
            content = dest.read_text()
            if "M  END" in content:
                existing += 1
                print(f"[{i+1}/{total}] CID {cid}: exists")
                if not content.rstrip().endswith("$$$$"):
                    with open(dest, "a") as f:
                        f.write("\n$$$$\n")
                    print(f"  -> added $$$$")
                continue
        
        sdf_data = None
        for fmt, url in [
            ("3D", f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/record/SDF?record_type=3d"),
            ("2D", f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/record/SDF"),
        ]:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "HermesAgent/1.0"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = resp.read().decode("utf-8", errors="replace")
                    if "M  END" in data:
                        sdf_data = data
                        if fmt == "3D":
                            fetched_3d += 1
                        else:
                            fetched_2d += 1
                        print(f"[{i+1}/{total}] CID {cid}: {fmt}")
                        break
            except urllib.error.HTTPError as e:
                print(f"[{i+1}/{total}] CID {cid}: {fmt} HTTP {e.code}...", end=" ")
            except Exception as e:
                print(f"[{i+1}/{total}] CID {cid}: {fmt} {e}...", end=" ")
        else:
            failed.append(cid)
            print(f" FAILED")
            continue
        
        if sdf_data and not sdf_data.rstrip().endswith("$$$$"):
            sdf_data = sdf_data.rstrip() + "\n$$$$\n"
        
        dest.write_text(sdf_data)
        time.sleep(0.3)
    
    total_size = sum(f.stat().st_size for f in out_dir.glob("*.sdf"))
    print(f"\n=== Summary ===")
    print(f"Total:    {total}")
    print(f"Existing: {existing}")
    print(f"3D:       {fetched_3d}")
    print(f"2D:       {fetched_2d}")
    print(f"Failed:   {len(failed)}")
    if failed:
        print(f"Failed:   {failed}")
    print(f"Size:     {total_size/1024:.1f} KB")

if __name__ == "__main__":
    main()
