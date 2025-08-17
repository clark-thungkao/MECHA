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
    with open(spec_path, "r", encoding="utf-8") as fh:
        spec = yaml.safe_load(fh)

    # parts
    for p in spec.get("parts", []):
        m = _make_part(p)
        cq.exporters.export(m, f"{outdir}/{p['name']}.step")
        cq.exporters.export(m, f"{outdir}/{p['name']}.stl")

    # assemblies (always write a CSV)
    asm_path = os.path.join(outdir, "assembly.csv")
    with open(asm_path, "w", encoding="utf-8") as f:
        f.write("assembly,part,tx,ty,tz,rx,ry,rz\n")

        assemblies = spec.get("assemblies", [])
        if not assemblies:
            # fallback: identity transforms for each part
            for p in spec.get("parts", []):
                f.write(f"default,{p['name']},0,0,0,0,0,0\n")
        else:
            for a in assemblies:
                for item in a["items"]:
                    tx, ty, tz, rx, ry, rz = item["transform"]
                    f.write(f"{a['name']},{item['part']},{tx},{ty},{tz},{rx},{ry},{rz}\n")

    print(f"Done. Files in {outdir}/ (STEP, STL, and assembly.csv)")

def main():
    ap = argparse.ArgumentParser(description="MechaCoop CLI")
    ap.add_argument("spec", help="Path to YAML spec")
    ap.add_argument("--outdir", default="build")
    args = ap.parse_args()
    build(args.spec, args.outdir)
