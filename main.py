"""
main.py — Orchestrator for the GaiaViz scene updater.

Loads all CSV inputs, runs selected update modules, saves the result.
"""

import argparse
import shutil
from datetime import datetime

from .loaders import (
    load_node_csv, load_asset_csv,
    load_traffic_csv, load_detection_csv,
)
from .links import update_links
from .leaves import update_leaves
from .textures import update_camera_textures, update_weather_textures


def main():
    parser = argparse.ArgumentParser(
        description="GaiaViz Scene Updater — update node CSV from traffic + detection data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run everything:
  python -m scene_updater --traffic traffic.csv --detections detections.csv --asset asset.csv --node node.csv --output final.csv

  # Only update link colors:
  python -m scene_updater --traffic traffic.csv --node node.csv --skip-leaves --skip-textures

  # Only fix textures:
  python -m scene_updater --asset asset.csv --node node.csv --skip-links --skip-leaves
        """,
    )

    # Input files
    parser.add_argument("--node", required=True,
                        help="GaiaViz node CSV (required)")
    parser.add_argument("--traffic", default=None,
                        help="Fused traffic/weather/events CSV")
    parser.add_argument("--detections", default=None,
                        help="YOLO detection results CSV")
    parser.add_argument("--asset", default=None,
                        help="GaiaViz asset CSV (for texture fixes)")

    # Output
    parser.add_argument("--output", default=None,
                        help="Output path (default: overwrites --node)")

    # Skip flags
    parser.add_argument("--skip-links", action="store_true",
                        help="Skip link color update")
    parser.add_argument("--skip-leaves", action="store_true",
                        help="Skip leaf color/scale update")
    parser.add_argument("--skip-textures", action="store_true",
                        help="Skip texture ID fixes")
    parser.add_argument("--no-backup", action="store_true",
                        help="Skip creating a backup")

    args = parser.parse_args()
    if args.output is None:
        args.output = args.node

    # ── Load node CSV (always required) ──
    print("\nLoading files...")
    node_df = load_node_csv(args.node)

    # ── Track what we did ──
    summary = []

    # ── PART 1: Link colors ──
    if not args.skip_links:
        if args.traffic is None:
            print("\n  Skipping links: --traffic not provided")
        else:
            traffic_df = load_traffic_csv(args.traffic)
            node_df, link_changes = update_links(node_df, traffic_df)
            summary.append(f"  Links updated: {len(link_changes)}")
            for c in link_changes:
                summary.append(f"    Link {c['link_id']}: {c['level'].upper()} → {c['new_color']}")

    # ── PART 2: Leaf colors + scale ──
    if not args.skip_leaves:
        if args.detections is None:
            print("\n  Skipping leaves: --detections not provided")
        else:
            detection_df = load_detection_csv(args.detections)
            node_df, leaf_changes = update_leaves(node_df, detection_df)
            grey = sum(1 for c in leaf_changes if c["count"] == 0)
            active = sum(1 for c in leaf_changes if c["count"] > 0)
            summary.append(f"  Leaves colored: {active}, greyed: {grey}")

    # ── PART 3: Texture fixes ──
    if not args.skip_textures:
        if args.asset is None:
            print("\n  Skipping textures: --asset not provided")
        else:
            asset_df = load_asset_csv(args.asset)
            node_df, cam_changes = update_camera_textures(node_df, asset_df)
            node_df, wx_changes = update_weather_textures(node_df, asset_df)
            cam_fixed = sum(1 for c in cam_changes if c["status"] == "FIXED")
            wx_fixed = sum(1 for c in wx_changes if c["status"] == "FIXED")
            summary.append(f"  Camera textures fixed: {cam_fixed}/{len(cam_changes)}")
            summary.append(f"  Weather textures fixed: {wx_fixed}/{len(wx_changes)}")

    # ── Backup ──
    if not args.no_backup and args.output == args.node:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{args.node}.backup_{ts}"
        shutil.copy2(args.node, backup_path)
        print(f"\n  Backup: {backup_path}")

    # ── Save ──
    node_df.to_csv(args.output, index=False)

    # ── Summary ──
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    for line in summary:
        print(line)
    print(f"\n  Saved: {args.output}\n")


if __name__ == "__main__":
    main()
