# 3D/2D Asset Pipeline

1. **Source**: Z-Anatomy / BodyParts3D (CC BY-SA — attribution + share-alike), own Blender models. Record licence in `packages/anatomy-assets/ATTRIBUTION.md`.
2. **Normalise in Blender**: metres, Y-up, origin at pelvis centre, apply transforms; split meshes per `region_code`; name object = `region_code`; assign to collections = layers.
3. **Optimise**: decimate (full body ≤ 150k triangles, detailed Unit ≤ 80k), merge materials, bake simple colours (no heavy textures), KTX2 textures ≤ 1024 px if needed.
4. **Export**: glTF 2.0 binary (.glb), +Y up, apply modifiers, include custom properties if useful (`extras.region_code`).
5. **Compress**: `npx @gltf-transform/cli optimize in.glb out.glb --compress draco --texture-compress ktx2` (or meshopt); create LOD1 with `simplify`.
6. **Validate in CI**: `python scripts/check_glb_regions.py out.glb unit-config.json --max-mb 5` → fails on missing/extra names or size; Khronos glTF validator for spec errors.
7. **Publish**: upload to `s3://<env>-assets/anatomy/<unit>/<hash>.glb` behind CloudFront, `Cache-Control: public, max-age=31536000, immutable`; config references hashed URL.
8. **2D SVG**: design in Figma/Inkscape with layer ids = region codes; SVGO with `cleanupIds: false`; convert to React component (SVGR) keeping ids.
