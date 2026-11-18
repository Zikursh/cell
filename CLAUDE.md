# Plant Cell: project notes for Claude Code

Static site for GitHub Pages. A student built a plant cell model in Blender for 6th grade science; this
repo holds its single-file three.js viewer page with a guided tour, and the tools that build it.

This repo is only the plant cell project.

## Layout
- `index.html`: the viewer page. Generated, do not edit by hand. Rebuild with the tools below.
- `thumb.jpg`: a render of the model, about 960 px wide.
- `tools/export_model.py`: .blend to GLB + JSON sidecar (needs `pip install bpy`, run with `python3 -I`).
- `tools/build_page.py` + `tools/viewer_template.html`: GLB + stops file to `index.html` (model embedded as base64).
- `tools/plant-cell.stops.json`: which Blender objects belong to each key entry.

## Rules
- The key text on the page is read from the text object in the .blend, word for word. It is the
  student's graded schoolwork. Never correct the spelling or definitions in the page; the student fixes
  them in Blender and the page is rebuilt.
- Objects hidden with the eye icon in the .blend are Boolean cutters and must stay out of exports.
- The meshes are flat shaded, so the export drops normals (three.js then flat shades and the file stays ~1.4 MB).
- Viewer look: AgX tone mapping to match Blender, three.js 0.160 from jsDelivr, no build step.
- Public repo about a child: no names (student or family), no school name, no photos. Do not name or
  link other projects from this repo.

## Open items (as of 2026-11-18)
1. The cell key is being revised (extra facts, spelling, a few definitions, cutters showing in renders).
   When a new .blend arrives, rerun the two commands in README.md.
