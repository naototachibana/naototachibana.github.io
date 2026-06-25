#!/usr/bin/env python3
"""
Extract a small demo shard from the deuterium-only TSV for GitHub Pages.

Usage:
  python3 scripts/make_demo_shard.py \
    --input <path/to/deuterium_only.tsv> \
    --out-dir assets/data \
    --limit 20

Outputs:
  assets/data/manifest.json
  assets/data/shard-00000.json
"""

import argparse
import csv
import json
import os
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Make demo shard for molecule viewer")
    parser.add_argument("--input", required=True, help="Path to deuterium_only.tsv")
    parser.add_argument("--out-dir", default="assets/data", help="Output directory")
    parser.add_argument("--limit", type=int, default=20, help="Number of records to extract")
    args = parser.parse_args()

    in_path = Path(args.input)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        print(f"ERROR: input file not found: {in_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Reading from: {in_path}")
    print(f"Output dir:   {out_dir}")
    print(f"Limit:        {args.limit} records")

    records = []
    with open(in_path, newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for i, row in enumerate(reader):
            if i >= args.limit:
                break
            try:
                d_count = int(row.get("deuterium_atom_count", "0"))
            except (ValueError, TypeError):
                d_count = 0
            if d_count <= 0:
                continue

            cid_raw = row.get("cid", "").strip()
            try:
                cid = int(cid_raw)
            except (ValueError, TypeError):
                cid = None

            record = {
                "cid": cid,
                "deuterium_atom_count": d_count,
                "canonical_isomeric_smiles": row.get("canonical_isomeric_smiles", ""),
                "source_file": row.get("source_file", ""),
                "record_index": row.get("record_index", ""),
                "pubchem_url": f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}" if cid else None,
            }
            records.append(record)

    if not records:
        print("WARNING: No deuterium records found in the input. "
              "Check if the TSV has a header and deuterium_atom_count > 0 rows.",
              file=sys.stderr)
        # Try reading without assuming header
        print("Trying fallback: reading raw TSV with known column order...")
        records = []
        with open(in_path, newline="") as f:
            # Read header line
            header_line = f.readline().strip().split("\t")
            print(f"Header: {header_line}")
            reader = csv.DictReader(f, fieldnames=header_line, delimiter="\t")
            for i, row in enumerate(reader):
                if i >= args.limit:
                    break
                try:
                    d_count = int(row.get("deuterium_atom_count", "0"))
                except (ValueError, TypeError):
                    d_count = 0
                if d_count <= 0:
                    continue
                cid_raw = row.get("cid", "").strip()
                try:
                    cid = int(cid_raw)
                except (ValueError, TypeError):
                    cid = None
                record = {
                    "cid": cid,
                    "deuterium_atom_count": d_count,
                    "canonical_isomeric_smiles": row.get("canonical_isomeric_smiles", ""),
                    "source_file": row.get("source_file", ""),
                    "record_index": row.get("record_index", ""),
                    "pubchem_url": f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}" if cid else None,
                }
                records.append(record)

    print(f"\nExtracted {len(records)} records")

    # Write shard
    shard_path = out_dir / "shard-00000.json"
    with open(shard_path, "w") as f:
        json.dump(records, f, indent=2)
    print(f"Shard:  {shard_path}  ({os.path.getsize(shard_path)} bytes)")

    # Write manifest
    manifest = {
        "dataset": "PubChem explicit deuterium compounds",
        "source": f"local slice from {in_path}",
        "page_size": 10,
        "shard_size": len(records),
        "shards_per_page": 2,
        "total_records_available_locally": len(records),
        "documented_total_records": 559150,
        "records_published_in_demo": len(records),
        "pages_published_in_demo": max(1, len(records) // 10),
        "shards": [
            {
                "id": 0,
                "path": "assets/data/shard-00000.json",
                "start_index": 0,
                "count": len(records),
            }
        ],
        "note": "Proof-of-concept shard only. Full TSV and bulk results are not published.",
    }
    manifest_path = out_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Manifest: {manifest_path}  ({os.path.getsize(manifest_path)} bytes)")

    # Quick validation
    print("\n=== First 3 records ===")
    for r in records[:3]:
        print(f"  CID {r['cid']:>8}  D={r['deuterium_atom_count']}  {r['canonical_isomeric_smiles'][:50]}")
    print(f"  ... ({len(records)} total)")


if __name__ == "__main__":
    main()
