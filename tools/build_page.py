"""Build a single-file 3D viewer page from an exported model.
Usage: python3 build_page.py <dir with cell.glb + cell.json> <stops.json> <out index.html>
The stop names and descriptions come from the key text typed in Blender, word for word.
The stops file only says which Blender objects belong to each entry."""
import sys, json, base64, re, pathlib
src, stops_path, out = map(pathlib.Path, sys.argv[1:4])
here = pathlib.Path(__file__).parent
cfg = json.loads(stops_path.read_text())
side = json.loads((src / "cell.json").read_text())
entries = []
for block in re.split(r"\n\s*\n", side["key_text"].strip()):
    name, _, text = block.partition(":")
    entries.append((name.strip(), " ".join(text.split())))
stops = []
for st in cfg["stops"]:
    hit = [e for e in entries if st["match"].lower() in e[0].lower()]
    if not hit: sys.exit(f"no key entry matches {st['match']!r}; entries are {[e[0] for e in entries]}")
    name, text = hit[0]
    col = next((side["objects"][n]["col"] for n in st["cell"] if n in side["objects"] and side["objects"][n]["col"]), [0.5, 0.5, 0.5])
    missing = [n for n in st["cell"] + st["key"] if n not in side["objects"]]
    if missing: sys.exit(f"{name}: objects not in the model: {missing}")
    stops.append(dict(name=name, text=text, col=col, cell=st["cell"], key=st["key"], frame=st.get("frame"), center=st.get("center"), radius=st.get("radius")))
data = dict(title=cfg["title"], subtitle=cfg["subtitle"], keySplitZ=cfg["key_split_z"], stops=stops)
html = (here / "viewer_template.html").read_text()
html = html.replace("__TITLE__", cfg["title"]).replace("__DATA__", json.dumps(data)).replace("__GLB__", base64.b64encode((src / "cell.glb").read_bytes()).decode())
out.write_text(html)
print(f"wrote {out} ({len(html)/1e6:.2f} MB), {len(stops)} stops")
