"""
leaves.py — Update leaf glyph colors and scale based on YOLO detections.

Reads YOLO detection CSV, aggregates counts per location per timestamp,
then maps detection counts to leaf node color and scale.
"""

import pandas as pd
from .config import (
    LOCATIONS, LEAF_NODES, LEAF_COLORS, DETECTION_COLUMNS,
    MIN_SCALE, MAX_SCALE, ZERO_SCALE,
)


def _get_yolo_name(location_name: str) -> str:
    """Convert short location name to the YOLO CSV's target_location."""
    return LOCATIONS[location_name]["yolo_name"]


def _get_latest_timestamps(detection_df: pd.DataFrame, n: int = 3) -> list:
    """Get the n most recent timestamps."""
    return sorted(detection_df["timestamp"].unique(), reverse=True)[:n]


def _get_count(detection_df: pd.DataFrame, location: str,
               timestamp: str, column: str) -> int:
    """Sum detections across all cameras at a location for one timestamp."""
    mask = (
        (detection_df["target_location"] == location) &
        (detection_df["timestamp"] == timestamp)
    )
    return int(detection_df.loc[mask, column].sum())


def _compute_max_counts(detection_df: pd.DataFrame) -> dict:
    """Max detection count per vehicle type (for scale normalization)."""
    agg = detection_df.groupby(
        ["target_location", "timestamp"]
    ).agg({
        "car_count": "sum",
        "truck_count": "sum",
        "bus_count": "sum",
    }).reset_index()

    return {
        "car":       max(agg["car_count"].max(), 1),
        "truck":     max(agg["truck_count"].max(), 1),
        "emergency": max(agg["bus_count"].max(), 1),
    }


def _count_to_scale(count: int, max_count: int) -> float:
    """Map detection count → scale value. 0 = near invisible."""
    if count == 0:
        return ZERO_SCALE
    ratio = count / max_count
    return MIN_SCALE + ratio * (MAX_SCALE - MIN_SCALE)


def update_leaves(node_df: pd.DataFrame, detection_df: pd.DataFrame):
    """
    Update leaf node colors and scale based on YOLO detections.
    Returns (updated_node_df, list_of_changes).
    """
    changes = []
    timestamps = _get_latest_timestamps(detection_df, n=3)
    max_counts = _compute_max_counts(detection_df)

    print("\n" + "=" * 60)
    print("  LEAF COLOR + SCALE UPDATE")
    print("=" * 60)
    print(f"\n    Timestamps: T0={timestamps[0]}, T-1={timestamps[1]}, T-2={timestamps[2]}")
    print(f"    Max counts: car={max_counts['car']}, "
          f"truck={max_counts['truck']}, emergency={max_counts['emergency']}")

    for loc_name, leaf_map in LEAF_NODES.items():
        yolo_name = _get_yolo_name(loc_name)
        print(f"\n    {loc_name} (root {LOCATIONS[loc_name]['root_id']})")

        for det_type, leaf_ids in leaf_map.items():
            column = DETECTION_COLUMNS[det_type]
            active_color = LEAF_COLORS[det_type]
            grey_color = LEAF_COLORS["grey"]
            max_count = max_counts[det_type]

            for i, (leaf_id, ts) in enumerate(zip(leaf_ids, timestamps)):
                count = _get_count(detection_df, yolo_name, ts, column)
                color = active_color if count > 0 else grey_color
                scale = _count_to_scale(count, max_count)

                mask = node_df["np_node_id"] == leaf_id
                if not mask.any():
                    print(f"      WARNING: Node {leaf_id} not found")
                    continue

                new_rgb = (f"rgb({color['color_r']},"
                           f"{color['color_g']},{color['color_b']})")

                node_df.loc[mask, "color_r"] = color["color_r"]
                node_df.loc[mask, "color_g"] = color["color_g"]
                node_df.loc[mask, "color_b"] = color["color_b"]
                node_df.loc[mask, "scale_x"] = scale
                node_df.loc[mask, "scale_y"] = scale
                node_df.loc[mask, "scale_z"] = scale

                time_label = ["T0", "T-1", "T-2"][i]
                status = f"{count}" if count > 0 else "0"
                print(f"      {det_type:>10} {time_label}: count={status:>3}  "
                      f"{new_rgb}  scale={scale:.3f}")

                changes.append({
                    "leaf_id": leaf_id, "type": det_type,
                    "time": time_label, "count": count, "scale": scale,
                })

    return node_df, changes
