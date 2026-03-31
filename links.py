"""
links.py — Update link node colors based on vehicle occupancy levels.

Reads the fused traffic CSV, determines the dominant occupancy level
per road segment endpoint, picks the worst case, and sets link color.
"""

import pandas as pd
from .config import LINKS, LINK_COLORS, LOCATIONS


SEVERITY = {"high": 3, "moderate": 2, "low": 1}


def _get_traffic_name(location_name: str) -> str:
    """Convert short location name to the traffic CSV's anchor_location_name."""
    return LOCATIONS[location_name]["traffic_name"]


def _endpoint_level(traffic_df: pd.DataFrame, loc_name: str,
                    link_prefixes: list) -> str:
    """Dominant occupancy level at one endpoint."""
    traffic_name = _get_traffic_name(loc_name)
    loc_data = traffic_df[traffic_df["anchor_location_name"] == traffic_name]

    if len(loc_data) > 0 and link_prefixes:
        prefix_mask = loc_data["link_name"].apply(
            lambda x: any(str(x).startswith(p) for p in link_prefixes)
            if pd.notna(x) else False
        )
        filtered = loc_data[prefix_mask]
        if len(filtered) > 0:
            loc_data = filtered

    if len(loc_data) == 0:
        print(f"      {loc_name}: no data → default low")
        return "low"

    level = loc_data["vehicle_occupancy_level"].mode().iloc[0]
    print(f"      {loc_name}: {level} ({len(loc_data)} sensors)")
    return level


def update_links(node_df: pd.DataFrame, traffic_df: pd.DataFrame):
    """
    Update link node colors based on traffic occupancy.
    Returns (updated_node_df, list_of_changes).
    """
    changes = []

    print("\n" + "=" * 60)
    print("  LINK COLOR UPDATE")
    print("=" * 60)

    for link_id, info in LINKS.items():
        print(f"\n    Link {link_id}: {info['segment_name']}")

        endpoint_levels = [
            _endpoint_level(traffic_df, loc, info["link_prefixes"])
            for loc in info["locations"]
        ]

        # Worst-case between endpoints
        level = max(endpoint_levels, key=lambda x: SEVERITY.get(x, 0))
        color = LINK_COLORS[level]

        mask = node_df["np_node_id"] == link_id
        if not mask.any():
            print(f"      WARNING: Node {link_id} not found")
            continue

        row = node_df.loc[mask].iloc[0]
        old_rgb = f"rgb({int(row.color_r)},{int(row.color_g)},{int(row.color_b)})"
        new_rgb = f"rgb({color['color_r']},{color['color_g']},{color['color_b']})"

        node_df.loc[mask, "color_r"] = color["color_r"]
        node_df.loc[mask, "color_g"] = color["color_g"]
        node_df.loc[mask, "color_b"] = color["color_b"]

        print(f"      → {level.upper()}  {old_rgb} → {new_rgb}")
        changes.append({"link_id": link_id, "level": level, "new_color": new_rgb})

    return node_df, changes
