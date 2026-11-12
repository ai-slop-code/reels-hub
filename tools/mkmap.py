"""Generate 1080x1920 SVG map cards for the Giro intro teaser.
usage: python3 -I mkmap.py <ne_geojson> <outdir>
"""
import json, math, sys, os

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
fc = json.load(open(src))

W, H = 1080, 1920
SEA = "#0F1C2B"; LAND = "#24323F"; LAND_LINE = "#3A4A5A"
ITA = "#EFE6DA"; ITA_LINE = "#FFFFFF"; PINK = "#F27BAA"; INK = "#0F1C2B"
FONT = "'Avenir Next', 'Helvetica Neue', Helvetica, sans-serif"

TRIESTE = (13.7768, 45.6495)
ROMA = (12.4964, 41.9028)


def feats(names):
    return [f for f in fc["features"] if f["properties"].get("ADMIN") in names
            or f["properties"].get("NAME") in names]


def rings(f):
    g = f["geometry"]
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    for p in polys:
        for r in p:
            yield r


class Proj:
    def __init__(self, lon0, lon1, lat0, lat1, box):
        self.lon0, self.lat1 = lon0, lat1
        self.k = math.cos(math.radians((lat0 + lat1) / 2))
        bx, by, bw, bh = box
        self.s = min(bw / ((lon1 - lon0) * self.k), bh / (lat1 - lat0))
        self.ox = bx + (bw - (lon1 - lon0) * self.k * self.s) / 2
        self.oy = by + (bh - (lat1 - lat0) * self.s) / 2

    def __call__(self, lon, lat):
        return (self.ox + (lon - self.lon0) * self.k * self.s,
                self.oy + (self.lat1 - lat) * self.s)


def path(f, P, tol=0.8):
    d = []
    for r in rings(f):
        pts, last = [], None
        for lon, lat in r:
            x, y = P(lon, lat)
            if x < -2000 or x > W + 2000 or y < -2000 or y > H + 2000:
                pass
            if last is None or abs(x - last[0]) + abs(y - last[1]) > tol:
                pts.append((x, y)); last = (x, y)
        if len(pts) > 2:
            d.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z")
    return "".join(d)


NEIGH = ["France", "Switzerland", "Austria", "Slovenia", "Croatia", "Bosnia and Herzegovina",
         "Montenegro", "Albania", "Greece", "San Marino", "Vatican", "Germany", "Liechtenstein",
         "Hungary", "Serbia", "Monaco", "Tunisia", "Algeria", "Malta", "Kosovo", "North Macedonia", "Republic of Serbia"]


def base(P, italy_fill=ITA, slo=None):
    s = [f'<rect width="{W}" height="{H}" fill="{SEA}"/>']
    for f in feats(NEIGH):
        fill = slo if (slo and f["properties"].get("ADMIN") == "Slovenia") else LAND
        s.append(f'<path d="{path(f, P)}" fill="{fill}" stroke="{LAND_LINE}" stroke-width="2" stroke-linejoin="round"/>')
    for f in feats(["Italy"]):
        s.append(f'<path d="{path(f, P)}" fill="{italy_fill}" stroke="{ITA_LINE}" stroke-width="2" stroke-linejoin="round"/>')
    return s


def dot(P, ll, r=16, glow=True):
    x, y = P(*ll)
    g = []
    if glow:
        g.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r*3.2}" fill="{PINK}" opacity="0.22"/>')
        g.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r*2}" fill="{PINK}" opacity="0.35"/>')
    g.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{PINK}" stroke="#FFFFFF" stroke-width="5"/>')
    return g, (x, y)


def label(x, y, text, size=52, anchor="start", fill="#FFFFFF", weight=700, halo=SEA, spacing=0):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}" fill="{fill}" stroke="{halo}" stroke-width="10" paint-order="stroke" '
            f'letter-spacing="{spacing}">{text}</text>')


def svg(parts):
    # square canvas (qlmanage renders square thumbnails); content centred, crop to 1080x1920 afterwards
    pad = (H - W) / 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{H}" height="{H}" viewBox="{-pad} 0 {H} {H}">'
            f'<rect x="{-pad}" width="{H}" height="{H}" fill="{SEA}"/>' + "".join(parts) + "</svg>")


# --- overview (Italy) ---  map band y 230..1330, captions live below 1380
P = Proj(6.2, 19.2, 36.3, 47.4, (40, 230, W - 80, 1100))
for name, with_rome in (("map_trieste", False), ("map_trieste_roma", True)):
    parts = base(P)
    g, (tx, ty) = dot(P, TRIESTE); parts += g
    parts.append(label(tx + 34, ty - 18, "Terst", 54))
    if with_rome:
        g, (rx, ry) = dot(P, ROMA); parts += g
        parts.append(label(rx + 36, ry + 18, "Rím", 54))
    open(f"{out}/{name}.svg", "w").write(svg(parts))

# --- close-up Trieste + Slovenian border ---
P2 = Proj(12.95, 14.75, 45.05, 46.25, (0, 250, W, 1080))
parts = base(P2, slo="#33475A")
# emphasise the Italy-Slovenia border by re-stroking Slovenia in pink dashes
for f in feats(["Slovenia"]):
    parts.append(f'<path d="{path(f, P2, 0.5)}" fill="none" stroke="{PINK}" stroke-width="7" stroke-dasharray="18 12" stroke-linejoin="round"/>')
g, (tx, ty) = dot(P2, TRIESTE, r=22); parts += g
parts.append(label(tx - 40, ty + 14, "Terst", 64, anchor="end", fill=INK, halo=ITA))
sx, sy = P2(14.35, 45.86)
parts.append(label(sx, sy, "SLOVINSKO", 58, anchor="middle", spacing=6))
ix, iy = P2(13.55, 46.12)
parts.append(label(ix, iy, "TALIANSKO", 58, anchor="middle", fill=INK, halo=ITA, spacing=6))
mx, my = P2(13.35, 45.55)
parts.append(label(mx, my, "Jadranské more", 44, anchor="middle", fill="#8FA3B8", weight=500))
open(f"{out}/map_trieste_border.svg", "w").write(svg(parts))
print("ok")
