"""
loaders.py — CSV file loading utilities.
"""

import pandas as pd


def load_node_csv(path: str) -> pd.DataFrame:
    """Load the GaiaViz node CSV."""
    df = pd.read_csv(path)
    print(f"  Node CSV    : {path} ({len(df)} nodes)")
    return df


def load_asset_csv(path: str) -> pd.DataFrame:
    """Load the GaiaViz asset CSV."""
    df = pd.read_csv(path)
    print(f"  Asset CSV   : {path} ({len(df)} assets)")
    return df


def load_traffic_csv(path: str) -> pd.DataFrame:
    """Load the fused traffic/weather/events CSV."""
    df = pd.read_csv(path)
    print(f"  Traffic CSV : {path} ({len(df)} rows)")
    return df


def load_detection_csv(path: str) -> pd.DataFrame:
    """Load the YOLO detection results CSV."""
    df = pd.read_csv(path)
    print(f"  Detection CSV: {path} ({len(df)} rows, "
          f"{df['target_location'].nunique()} locations, "
          f"{df['timestamp'].nunique()} timestamps)")
    return df


def resolve_texture_id(asset_df: pd.DataFrame, image_name: str) -> int | None:
    """Look up item_id for an image filename in the asset CSV."""
    match = asset_df[asset_df["name"] == image_name]
    if match.empty:
        print(f"    WARNING: '{image_name}' not found in asset CSV")
        return None
    return int(match.iloc[0]["item_id"])
