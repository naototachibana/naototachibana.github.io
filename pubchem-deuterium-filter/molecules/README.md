# PubChem Deuterium Filter — Molecule Viewer

This directory contains an interactive 3D molecular viewer for explicitly
deuterium-labelled PubChem compounds extracted by the
[pubchem-deuterium-filter](https://github.com/naototachibana/pubchem-deuterium-filter) pipeline.

## Contents

- `index.html` — Main page with 3Dmol.js viewers
- `assets/sdf/*.sdf` — Local SDF files for 6 sample CIDs, fetched from
  PubChem PUG-REST (`/rest/pug/compound/cid/{CID}/record/SDF`) on
  2026-06-24. These are small, static SDF files for visualisation only.

## CIDs Included

| CID | Compound | D Atoms |
|-----|----------|---------|
| 24523 | Deuterium gas (D₂) | 2 |
| 24602 | Heavy water (D₂O) | 2 |
| 12669 | Methane-d1 | 1 |
| 13517 | Perdeuterated tert-butyl chloride | 9 |
| 27870 | Perdeuterated tetracosane (C₂₄D₅₀) | 50 |
| 40913 | β-Estradiol-d2 | 2 |

## Live Page

https://naototachibana.github.io/pubchem-deuterium-filter/molecules/
