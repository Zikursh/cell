# Plant Cell

A cutaway plant cell with twelve labeled parts and a key, built in Blender for 6th grade science.
The page is a 3D viewer that runs in any browser: turn the model around or take the tour.

```
index.html     the viewer page (generated, model embedded)
thumb.jpg      a render of the model
tools/         scripts that turn the .blend into the viewer page
```

## Hosting on GitHub Pages

Settings, then Pages. Under Build and deployment choose Deploy from a branch, branch `main`, folder `/ (root)`.
The site is then live at `https://<username>.github.io/cell/`.

## Rebuilding the page after the model changes

The key text on the page is read from the text object in the `.blend`, word for word, so fixing a
definition in Blender and rebuilding updates the page.

```
pip install bpy
mkdir -p /tmp/cell
python3 -I tools/export_model.py cell_model_progect.blend /tmp/cell
python3 tools/build_page.py /tmp/cell tools/plant-cell.stops.json index.html
```

`tools/plant-cell.stops.json` lists which Blender objects belong to each key entry. If objects are added
or renamed, update that file. The export skips anything hidden with the eye icon (the Boolean cutters),
turns metaballs and text into meshes, and thins very dense meshes so the page stays under 2 MB.
