"""Lightweight styling of the native Ecovacs SVG; no new renderer."""
import re
from functools import lru_cache

COLORS = {
    "map_background": "",
    "map_floor": "#edf3fb",
    "map_walls": "#666666",
    "map_path": "#ffffff",
    "map_robot": "#0000ff",
    "map_dock": "#ffe605",
    "map_room_1": "#a2bce7",
    "map_room_2": "#ecd099",
    "map_room_3": "#9bd4da",
    "map_room_4": "#ecc6c9",
    "map_room_5": "#d7bce3",
    "map_room_6": "#c3e2b6",
}
FLAGS = {
    "map_colored_rooms": True,
    "map_show_path": True,
    "map_show_robot": True,
    "map_show_dock": True,
    "map_show_zones": True,
}
NUMBERS = {
    "map_room_opacity": 100,
    "map_path_opacity": 100,
    "map_wall_opacity": 100,
    "map_padding": 0,
    "map_rotation": 0,
}
DEFAULTS = COLORS | FLAGS | NUMBERS

def rgb_to_hex(value):
    if isinstance(value, (list, tuple)) and len(value) == 3 and all(
        type(v) is int and 0 <= v <= 255 for v in value
    ):
        return "#" + "".join(f"{v:02x}" for v in value)
    return value

def hex_to_rgb(value):
    if isinstance(value, str) and HEX.fullmatch(value):
        return [int(value[i:i+2], 16) for i in (1, 3, 5)]
    return [0, 0, 0]

def valid_number(key, value):
    return type(value) in (int, float) and (
        value in (0, 90, 180, 270) if key == "map_rotation"
        else 0 <= value <= (50 if key == "map_padding" else 100)
    )
TRACE = 'svg > path[transform="scale(0.2-0.2)"]'
HEX = re.compile(r"#[0-9a-fA-F]{6}")


def valid_color(key, value):
    return isinstance(value, str) and (
        (key == "map_background" and value == "") or HEX.fullmatch(value) is not None
    )


def settings_key(options):
    return tuple(
        (key, value if valid_color(key, value) else default)
        if key in COLORS else (key, value if valid_number(key, value) else default)
        if key in NUMBERS else (key, value if isinstance(value, bool) else default)
        for key, default in DEFAULTS.items()
        for value in [options.get(key, default)]
    )


@lru_cache(maxsize=2)
def style_svg(svg, settings):
    """Apply CSS after upstream styles; preserve original SVG geometry."""
    opt = dict(settings)
    if opt == DEFAULTS or not svg.endswith("</svg>"):
        return svg.encode()
    rules = [
        f".u{{fill:{opt['map_floor']}}}",
        f".o path{{stroke:{opt['map_walls']}}}",
        f"{TRACE}{{stroke:{opt['map_path']}}}",
        f"#d circle[fill='blue']{{fill:{opt['map_robot']}}}",
        f"#dbg stop{{stop-color:{opt['map_robot']}}}",
        "#dbg stop[offset='97%']{stop-opacity:0}",
        f"#c path{{fill:{opt['map_dock']}}}",
    ]
    rules.extend([
        f".o path{{stroke-opacity:{opt['map_wall_opacity']/100}}}",
        f"{TRACE}{{stroke-opacity:{opt['map_path_opacity']/100}}}",
    ])
    for i in range(6):
        color = opt[f"map_room_{i+1}"] if opt["map_colored_rooms"] else opt["map_floor"]
        rules.append(f".r{i}{{fill:{color};fill-opacity:{opt['map_room_opacity']/100}}}")
    for key, selector in (
        ("map_show_path", TRACE),
        ("map_show_robot", "use[href='#d']"),
        ("map_show_dock", "use[href='#c']"),
        ("map_show_zones", ".w"),
    ):
        if not opt[key]:
            rules.append(f"{selector}{{display:none}}")
    match = re.search(r'\bviewBox="(-?[\d.]+)[ ,]+(-?[\d.]+)[ ,]+([\d.]+)[ ,]+([\d.]+)"', svg)
    if match and svg.startswith("<svg"):
        x, y, w, h = map(float, match.groups())
        angle = opt["map_rotation"]
        pad = opt["map_padding"]
        cx, cy = x + w/2, y + h/2
        nw, nh = (h, w) if angle in (90, 270) else (w, h)
        nx, ny = cx - nw/2 - pad, cy - nh/2 - pad
        nw, nh = nw + 2*pad, nh + 2*pad
        svg = svg[:match.start()] + f'viewBox="{nx:g} {ny:g} {nw:g} {nh:g}"' + svg[match.end():]
        start = svg.find(">") + 1
        body = svg[start:-6]
        if angle:
            # Preserve direct-child CSS selectors: rotate a nested SVG instead of a group.
            # Inner SVG retains its own coordinate system and original stylesheet.
            body += "<style>" + "".join(rules) + "</style>"
            rules = []
            body = (
                f'<svg x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" '
                f'viewBox="{x:g} {y:g} {w:g} {h:g}" overflow="visible" '
                f'transform="rotate({angle:g} {cx:g} {cy:g})">{body}</svg>'
            )
        if color := opt["map_background"]:
            body = f'<rect x="{nx:g}" y="{ny:g}" width="{nw:g}" height="{nh:g}" fill="{color}"/>' + body
        svg = svg[:start] + body + "</svg>"
    return (svg[:-6] + "<style>" + "".join(rules) + "</style></svg>").encode()
