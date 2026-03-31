"""
textures.py — Fix texture IDs on camera cubes and weather cubes.

Maps the correct location-specific JPEG to each camera cube,
and ensures weather cubes show storm/snowflake/sun icons.
"""

import pandas as pd
from .config import CAMERA_CUBES, CAMERA_IMAGES, WEATHER_CUBES, WEATHER_IMAGES
from .loaders import resolve_texture_id


def update_camera_textures(node_df: pd.DataFrame, asset_df: pd.DataFrame):
    """
    Fix camera cube textures to show the correct location image.
    Returns (updated_node_df, list_of_changes).
    """
    changes = []

    print("\n" + "=" * 60)
    print("  CAMERA TEXTURE UPDATE")
    print("=" * 60)

    for location, cube_id in CAMERA_CUBES.items():
        image_name = CAMERA_IMAGES[location]
        tex_id = resolve_texture_id(asset_df, image_name)
        if tex_id is None:
            continue

        mask = node_df["np_node_id"] == cube_id
        if not mask.any():
            print(f"    WARNING: Node {cube_id} not found")
            continue

        old_tex = int(node_df.loc[mask, "np_texture_id"].values[0])
        old_match = asset_df[asset_df["item_id"] == old_tex]
        old_name = old_match.iloc[0]["name"] if not old_match.empty else "?"

        node_df.loc[mask, "np_texture_id"] = tex_id

        status = "OK" if old_tex == tex_id else "FIXED"
        print(f"    {location:>15} (cube {cube_id}): "
              f"tex {old_tex}({old_name}) → {tex_id}({image_name}) [{status}]")

        changes.append({
            "location": location, "cube_id": cube_id,
            "old_tex": old_tex, "new_tex": tex_id, "status": status,
        })

    return node_df, changes


def update_weather_textures(node_df: pd.DataFrame, asset_df: pd.DataFrame):
    """
    Fix weather cube textures to show storm/snowflake/sun.
    Returns (updated_node_df, list_of_changes).
    """
    changes = []

    print("\n" + "=" * 60)
    print("  WEATHER TEXTURE UPDATE")
    print("=" * 60)

    for location, cube_ids in WEATHER_CUBES.items():
        for cube_id, image_name in zip(cube_ids, WEATHER_IMAGES):
            tex_id = resolve_texture_id(asset_df, image_name)
            if tex_id is None:
                continue

            mask = node_df["np_node_id"] == cube_id
            if not mask.any():
                print(f"    WARNING: Node {cube_id} not found")
                continue

            old_tex = int(node_df.loc[mask, "np_texture_id"].values[0])
            old_match = asset_df[asset_df["item_id"] == old_tex]
            old_name = old_match.iloc[0]["name"] if not old_match.empty else "?"

            node_df.loc[mask, "np_texture_id"] = tex_id

            status = "OK" if old_tex == tex_id else "FIXED"
            print(f"    {location:>15} node {cube_id}: "
                  f"tex {old_tex}({old_name}) → {tex_id}({image_name}) [{status}]")

            changes.append({
                "location": location, "node_id": cube_id,
                "old_tex": old_tex, "new_tex": tex_id, "status": status,
            })

    return node_df, changes
