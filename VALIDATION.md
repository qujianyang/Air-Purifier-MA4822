# Rev D CAD generation and verification

Verified on Windows on 18 November 2026 using Python 3.12.14, CadQuery 2.6.1, cadquery-ocp 7.8.1.1.post1 and VTK 9.3.1. An existing local CAD environment was used; this run used the real OpenCascade geometry kernel.

## What was corrected

1. The received bell-mouth profile used a diagonal offset that crossed the flare. OpenCascade reported a valid shape, but its inside/outside test treated distant points as material and produced false intersections. The corrected profile offsets the inner segments by 1.8 mm along their normals, with a 228 mm outside lip. A regression check verifies finite material, the throat wall and an empty throat.
2. The original manifold was a solid ring. It now contains a closed annular gallery, four communicating 1.6 mm bores and a bored outlet nipple. The tap fittings extend into the gallery connection and the throat tube meets the outlet.
3. The overview renders now use numbered pins and a separate legend, avoiding long crossing leaders. The flow detail looks down onto the bell-mouth with the fan deck omitted so the taps and manifold can be seen.

## Results

| Check | Household | Bench |
| --- | --- | --- |
| Assembly components | 150 | 184 |
| All component shapes valid | Pass | Pass |
| Components within 400 × 300 × 650 mm envelope | Pass | Pass |
| STEP re-import valid | Pass | Pass |
| Unexpected intersections in the new-part collision check | 0 | 0 |
| Required household sensors present | Pass | Pass |
| Outlet SPS30 and FS3000 excluded from household | Pass | Not applicable |
| Outlet SPS30 and FS3000 present on bench | Not applicable | Pass |
| Four tap bores open; annular gallery hollow | Pass | Pass |
| Tap fittings meet manifold | Pass | Pass |
| P− branch and throat tube meet intended ports | Pass | Pass |
| Minimum clearance between P04/P05 tubes and wiring | 3.9 mm | 3.9 mm |

The fan-deck opening and the bell-mouth throat are both 160 mm in diameter. Their junction is at Z = 395 mm. The deck and bell-mouth have no volumetric interference. Full component, collision and sensor-retention records are in `validation/household/` and `validation/bench/`. Additional checks are in `geometry_acceptance.json` and can be repeated with `python verify_geometry.py` after generating both configurations.

The collision check covers the new parts against bounding-box-nearby assembly parts; it is not a complete manufacturing interference or tolerance analysis. Tube and harness solids are routing envelopes, not full fluid-domain or cable models. These are CAD checks, not measured airflow, filtration, sealing or hardware-performance results.

## Files to use in the report

Use the household files:

- `images/cad_sensor_cutaway.png` — household sensor placement.
- `images/cad_rear.png` — rear electronics and pressure routing.
- `images/cad_flow_detail.png` — bell-mouth, four taps, ring manifold and outlet.

All three images were rendered directly from the same corrected parametric source that exports the supplied STEP files. The household contains no outlet PM sensor or FS3000. The cutaway legend numbers are defined by the new image; check caption numbering when replacing an earlier render.

The report DOCX and app were not edited in this CAD update. Replace the intended report figures with these household PNGs and link the household STEP. Use the bench files only when discussing the development rig. The original files in Downloads remain unchanged.
