import argparse, os, yaml
import cadquery as cq
from mmcad.parts.basic import plate, shaft, link_rect

def _make_part(p):
    t = p["type"]
    if t == "plate": return plate(p["width"], p["height"], p["thickness"], p.get("holes"))
    if t == "shaft": return shaft(p["diameter"], p["length"])
    if t == "link":  return link_rect(p["length"], p["width"], p["thickness"], p.get("end_hole_d", 8))
    raise ValueError(f"Unknown part type: {t}")

def build(spec_path, outdir="build"):
    os.makedirs(outdir, exist_ok=True)
    spec = yaml.safe_load(open(spec_path, "r"))
    # parts
    for p in spec.get("parts", []):
        m = _make_part(p)
        cq.exporters.export(m, f"{outdir}/{p['name']}.step")
        cq.exporters.export(m, f"{outdir}/{p['name']}.stl")
    # assemblies (CSV for now; URDF later)
    with open(f"{outdir}/assembly.csv","w") as f:
        f.write("name,part,tx,ty,tz,rx,ry,rz\n")
        for a in spec.get("assemblies", []):
            for item in a["items"]:
                tx,ty,tz,rx,ry,rz = item["transform"]
                f.write(f"{a['name']},{item['part']},{tx},{ty},{tz},{rx},{ry},{rz}\n")
    print(f"Done. Files in {outdir}/")

def main():
    ap = argparse.ArgumentParser(description="MechaCoop CLI")
    ap.add_argument("spec", help="Path to YAML spec")
    ap.add_argument("--outdir", default="build")
    args = ap.parse_args()
    build(args.spec, args.outdir)
