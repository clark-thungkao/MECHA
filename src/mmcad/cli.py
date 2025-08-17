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
    # load YAML
    with open(spec_path, "r", encoding="utf-8") as fh:
        spec = yaml.safe_load(fh)

    # choose project name (YAML key, or file stem)
    project_name = spec.get("project") or os.path.splitext(os.path.basename(spec_path))[0]

    # create build/<project_name>
    proj_outdir = os.path.join(outdir, project_name)
    os.makedirs(proj_outdir, exist_ok=True)

    # parts
    for p in spec.get("parts", []):
        m = _make_part(p)
        cq.exporters.export(m, os.path.join(proj_outdir, f"{p['name']}.step"))
        cq.exporters.export(m, os.path.join(proj_outdir, f"{p['name']}.stl"))

    # assemblies
    asm_path = os.path.join(proj_outdir, "assembly.csv")
    with open(asm_path, "w", encoding="utf-8") as f:
        f.write("assembly,part,tx,ty,tz,rx,ry,rz\n")
        assemblies = spec.get("assemblies", [])
        if not assemblies:
            for p in spec.get("parts", []):
                f.write(f"default,{p['name']},0,0,0,0,0,0\n")
        else:
            for a in assemblies:
                for item in a["items"]:
                    tx, ty, tz, rx, ry, rz = item["transform"]
                    f.write(f"{a['name']},{item['part']},{tx},{ty},{tz},{rx},{ry},{rz}\n")

    print(f"Done. Files in {proj_outdir}/ (STEP, STL, and assembly.csv)")


def main():
    ap = argparse.ArgumentParser(description="MechaCoop CLI")
    ap.add_argument("spec", help="Path to YAML spec")
    ap.add_argument("--outdir", default="build")
    args = ap.parse_args()
    build(args.spec, args.outdir)
