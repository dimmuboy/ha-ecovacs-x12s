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
DEFAULTS = COLORS | FLAGS
TRACE = 'svg > path[transform="scale(0.2-0.2)"]'
HEX = re.compile(r"#[0-9a-fA-F]{6}")


def valid_color(key, value):
    return isinstance(value, str) and (
        (key == "map_background" and value == "") or HEX.fullmatch(value) is not None
    )


def settings_key(options):
    return tuple(
        (key, value if valid_color(key, value) else default)
        if key in COLORS else (key, value if isinstance(value, bool) else default)
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
    for i in range(6):
        color = opt[f"map_room_{i+1}"] if opt["map_colored_rooms"] else opt["map_floor"]
        rules.append(f".r{i}{{fill:{color}}}")
    for key, selector in (
        ("map_show_path", TRACE),
        ("map_show_robot", "use[href='#d']"),
        ("map_show_dock", "use[href='#c']"),
        ("map_show_zones", ".w"),
    ):
        if not opt[key]:
            rules.append(f"{selector}{{display:none}}")
    if color := opt["map_background"]:
        # SVG root percentages cover the viewport even for a negative viewBox origin.
        match = re.search(r'\bviewBox="(-?[\d.]+)[ ,]+(-?[\d.]+)[ ,]+([\d.]+)[ ,]+([\d.]+)"', svg)
        if match:
            x, y, w, h = match.groups()
            start = svg.find(">") + 1
            if svg.startswith("<svg") and start:
                svg = svg[:start] + f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}"/>' + svg[start:]
    return (svg[:-6] + "<style>" + "".join(rules) + "</style></svg>").encode()
