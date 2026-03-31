# GaiaViz Scene Updater

A Python package that maps real-time traffic sensor data and YOLO object detection results onto a GaiaViz 3D scene. It reads CSV data files and updates the GaiaViz node CSV to change glyph colors, sizes, and textures — producing a static scene snapshot that visualizes corridor conditions.

## Overview

The Arlington Corridor Situational Awareness project uses GaiaViz to visualize traffic conditions across 5 locations on the I-66 and I-395 corridors. Each location is represented by a **hyperglyph** — a hierarchical 3D structure with a camera cube, detection leaf rings, weather cubes, and inter-location links.

This package automates the process of mapping data to those glyphs. Instead of manually editing the node CSV, you run one command and the scene updates.

## Quick start

```bash
# Run everything (links + leaves + textures):
python -m scene_updater \
  --node Subgrid-np_node.csv \
  --traffic fused_events_traffic_weather_dataset.csv \
  --detections image_level_results.csv \
  --asset Subgrid-np_asset.csv \
  --output final_np_node.csv
```

```bash
# Only update link colors from traffic data:
python -m scene_updater \
  --node Subgrid-np_node.csv \
  --traffic fused_events_traffic_weather_dataset.csv \
  --skip-leaves --skip-textures \
  --output updated_links.csv
```

```bash
# Only update leaf glyphs from YOLO detections:
python -m scene_updater \
  --node Subgrid-np_node.csv \
  --detections image_level_results.csv \
  --skip-links --skip-textures \
  --output updated_leaves.csv
```

```bash
# Only fix camera + weather textures:
python -m scene_updater \
  --node Subgrid-np_node.csv \
  --asset Subgrid-v111_v03_np_asset.csv \
  --skip-links --skip-leaves \
  --output fixed_textures.csv
```

## Overwriting the source file

By default, if `--output` is not specified, the script overwrites the input node CSV in place and creates a Timestamped backup automatically:
```bash
# Overwrites Subgrid-v111_v03_np_node.csv directly (backup created)
python -m scene_updater \
  --node Subgrid-np_node.csv \
  --traffic fused_events_traffic_weather_dataset.csv \
  --detections image_level_results.csv \
  --asset Subgrid-np_asset.csv
```

A backup file like `Subgrid-np_node.csv.backup_20260331_143022` is created before any changes are written. To skip the backup, add `--no-backup`.

To write to a separate file instead, use `--output`:
```bash
python -m scene_updater \
  --node Subgrid-np_node.csv \
  --traffic traffic.csv \
  --detections detections.csv \
  --asset asset.csv \
  --output final_np_node.csv
```


## Command line arguments

| Argument | Required | Description |
| `--node` | Yes | Path to the GaiaViz node CSV |
| `--traffic` | No | Path to the fused traffic/weather/events CSV |
| `--detections` | No | Path to the YOLO detection results CSV |
| `--asset` | No | Path to the GaiaViz asset CSV (for texture fixes) |
| `--output` | No | Output path (default: overwrites `--node`) |
| `--skip-links` | No | Skip link color update |
| `--skip-leaves` | No | Skip leaf color and scale update |
| `--skip-textures` | No | Skip camera and weather texture fixes |
| `--no-backup` | No | Skip creating a timestamped backup |

## Package structure

```
scene_updater/
├── __init__.py      # Package marker
├── __main__.py      # Entry point for python -m scene_updater
├── config.py        # All node IDs, color maps, thresholds
├── loaders.py       # CSV loading utilities
├── links.py         # Link color update logic
├── leaves.py        # Leaf color + scale update logic
├── textures.py      # Camera + weather texture fix logic
└── main.py          # Orchestrator: load → update → save
```

### Module descriptions

| Module | Purpose | Input CSV | Node fields modified |
| `config.py` | Central configuration. All node IDs, color palettes, scale thresholds, and location mappings. When node IDs change between scene versions, update this file only. | — | — |
| `loaders.py` | CSV loading utilities and asset texture ID resolution. | All CSVs | — |
| `links.py` | Changes link colors based on `vehicle_occupancy_level` from the traffic CSV. For each link, finds the dominant level at each endpoint, picks the worst case. | `fused_events_traffic_weather_dataset.csv` | `color_r`, `color_g`, `color_b` |
| `leaves.py` | Changes leaf glyph colors and scale based on YOLO detection counts. Aggregates across all cameras at each location per timestamp. 3 time snapshots (T0, T-1, T-2). | `image_level_results.csv` | `color_r`, `color_g`, `color_b`, `scale_x`, `scale_y`, `scale_z` |
| `textures.py` | Maps the correct camera JPEG and weather icon to each cube's `np_texture_id` using the asset CSV. | `np_asset.csv` | `np_texture_id` |
| `main.py` | Orchestrates loading, runs selected updaters in sequence, handles backup and save. | — | — |

## Dependencies

- Python 3.10+
- pandas

```bash
pip install pandas
```

---

## Scene structure

### Subgrid hierarchy

The scene is organized as a tree rooted at subgrid node 42 (the Arlington map). Five hyperglyph pins sit on this subgrid, each representing a traffic corridor location.

```
Subgrid (id=42, type=6, tex=projectfinal.png)
├── Dunn Loring pin  (id=43, geo=16, topo=5)
├── Ballston pin     (id=62, geo=16, topo=5)
├── Rosslyn pin      (id=80, geo=16, topo=5)
├── Shirlington pin  (id=99, geo=16, topo=5)
└── Pentagon pin     (id=117, geo=16, topo=5)
```

### Location mapping

| Location | Root node ID | GPS (lat, lon) | Subgrid position (x, y) | Route |
| I-66 West (Dunn Loring) | 43 | 38.8844, -77.1526 | -6.0, 5.8 | I-66 Corridor |
| I-66 Mid (Ballston/Glebe) | 62 | 38.8879, -77.1150 | 1.8, 11.2 | I-66 Corridor |
| I-66 East (Rosslyn) | 80 | 38.8953, -77.0999 | 10.7, 15.2 | I-66 Corridor |
| I-395 South (Shirlington) | 99 | 38.8326, -77.1050 | 2.3, -19.2 | I-395 Corridor |
| I-395 North (Pentagon) | 117 | 38.8690, -77.0590 | 12.3, -2.0 | I-395 Corridor |

### Hyperglyph internal structure

Each hyperglyph has an identical internal tree. Here is the structure for Dunn Loring (root 43) — other locations follow the same pattern with different node IDs:

```
Pin 43 (geo=16, bl=1)
├── Camera cube 44 (geo=1, bl=2, tex=West_Dunn_Loring.jpeg)
│   ├── Cluster A: Emergency (geo=19, bl=3, id=45)
│   │   ├── Leaf 46 (geo=7, bl=4) — T0
│   │   ├── Leaf 47 (geo=7, bl=4) — T-1
│   │   └── Leaf 48 (geo=7, bl=4) — T-2
│   ├── Cluster B: Trucks (geo=19, bl=3, id=49)
│   │   ├── Leaf 50 (geo=7, bl=4) — T0
│   │   ├── Leaf 51 (geo=7, bl=4) — T-1
│   │   └── Leaf 52 (geo=7, bl=4) — T-2
│   ├── Cluster C: Cars (geo=19, bl=3, id=53)
│   │   ├── Leaf 54 (geo=7, bl=4) — T0
│   │   ├── Leaf 55 (geo=7, bl=4) — T-1
│   │   └── Leaf 56 (geo=7, bl=4) — T-2
│   └── Link 57 (type=7, bl=3) → connects to Ballston cube 63
└── Weather rod 58 (geo=7, bl=2)
    ├── Storm cube 59 (geo=1, bl=3, tex=storm.png)
    ├── Snowflake cube 60 (geo=1, bl=3, tex=snowflake.png)
    └── Sun cube 61 (geo=1, bl=3, tex=sun.png)
```

### Camera cube node IDs

| Location | Cube node ID | Correct texture | Asset item_id |
| Dunn Loring | 44 | West_Dunn_Loring.jpeg | 19 |
| Ballston | 63 | Mid_Ballston_Glebe.jpeg | 9 |
| Rosslyn | 81 | example.jpg (placeholder) | 4 |
| Shirlington | 100 | South_Shirlington.jpeg | 16 |
| Pentagon | 118 | North_Pentagon.jpeg | 10 |

### Weather cube node IDs

| Location | Storm node | Snowflake node | Sun node |
| Dunn Loring | 59 (tex=17) | 60 (tex=15) | 61 (tex=18) |
| Ballston | 77 (tex=17) | 78 (tex=15) | 79 (tex=18) |
| Rosslyn | 96 (tex=17) | 97 (tex=15) | 98 (tex=18) |
| Shirlington | 114 (tex=17) | 115 (tex=15) | 116 (tex=18) |
| Pentagon | 133 (tex=17) | 134 (tex=15) | 135 (tex=18) |

### Leaf node IDs (detection glyphs)

Each location has 9 leaf nodes (3 clusters × 3 time snapshots).

**Cluster A — Emergency vehicles (bus_count)**

| Location | T0 (latest) | T-1 | T-2 | Active color |
| Dunn Loring | 46 | 47 | 48 | red (255,0,0) |
| Ballston | 65 | 66 | 67 | red (255,0,0) |
| Rosslyn | 83 | 84 | 85 | red (255,0,0) |
| Shirlington | 102 | 103 | 104 | red (255,0,0) |
| Pentagon | 120 | 121 | 122 | red (255,0,0) |

**Cluster B — Trucks (truck_count)**

| Location | T0 (latest) | T-1 | T-2 | Active color |
| Dunn Loring | 50 | 51 | 52 | yellow (255,255,0) |
| Ballston | 69 | 70 | 71 | yellow (255,255,0) |
| Rosslyn | 87 | 88 | 89 | yellow (255,255,0) |
| Shirlington | 106 | 107 | 108 | yellow (255,255,0) |
| Pentagon | 124 | 125 | 126 | yellow (255,255,0) |

**Cluster C — Cars (car_count)**

| Location | T0 (latest) | T-1 | T-2 | Active color |
| Dunn Loring | 54 | 55 | 56 | blue (0,0,255) |
| Ballston | 73 | 74 | 75 | blue (0,0,255) |
| Rosslyn | 91 | 92 | 93 | blue (0,0,255) |
| Shirlington | 110 | 111 | 112 | blue (0,0,255) |
| Pentagon | 128 | 129 | 130 | blue (0,0,255) |

**Leaf color logic:** If detection count > 0 at that timestamp, the leaf shows its assigned color. If count = 0, the leaf turns grey (128,128,128).

**Leaf scale logic:** Scale is normalized within each vehicle type. `scale = 0.15 + (count / max_count) × 1.05`. Zero detections shrink to 0.05 (near invisible).

### Link node IDs

| Link node ID | A-end (parent) | B-end (child) | Road segment | Default color |
| 57 | Dunn Loring cube (44) | Ballston cube (63) | I-66 | green (0,255,0) |
| 94 | Rosslyn cube (81) | Ballston cube (63) | I-66 | green (0,255,0) |
| 131 | Pentagon cube (118) | Shirlington cube (100) | I-395 | green (0,255,0) |

**Link color logic:** Based on `vehicle_occupancy_level` from the traffic CSV. The script finds the dominant level at each endpoint, picks the worst case.

| Occupancy level | Color |
| low | green (0,255,0) |
| moderate | yellow (255,255,0) |
| high | red (255,0,0) |

### Asset texture IDs

| item_id | Filename | Used by |
| 4 | example.jpg | Rosslyn camera (placeholder) |
| 9 | Mid_Ballston_Glebe.jpeg | Ballston camera cube |
| 10 | North_Pentagon.jpeg | Pentagon camera cube |
| 13 | projectfinal.png | Subgrid map texture |
| 15 | snowflake.png | Weather cubes |
| 16 | South_Shirlington.jpeg | Shirlington camera cube |
| 17 | storm.png | Weather cubes |
| 18 | sun.png | Weather cubes |
| 19 | West_Dunn_Loring.jpeg | Dunn Loring camera cube |

### GaiaViz geometry reference

| geo ID | Shape | Used for |
| 1 | Cube | Camera cubes, weather cubes |
| 6 | Link geometry | Links between hyperglyphs |
| 7 | Ring / Rod | Leaf detection rings, weather rod |
| 16 | Pin | Location root pin |
| 19 | Pin (variant) | Cluster parent nodes |
| 21 | Grid mesh | Subgrid map |

### GaiaViz type codes

| Type | Meaning |
| 0 | Grid |
| 1 | Camera |
| 5 | Hyperglyph |
| 6 | Subgrid |
| 7 | Link |

---

## Input CSV formats

### Traffic CSV (`fused_events_traffic_weather_dataset.csv`)

Key columns used by the link updater:

| Column | Description | Example |
| `anchor_location_name` | Location name | I-395 North (near Pentagon) |
| `vehicle_occupancy_level` | low / moderate / high | low |
| `link_name` | Road segment identifier | I-395N |

### Detection CSV (`image_level_results.csv`)

Key columns used by the leaf updater:

| Column | Description | Example |
| `target_location` | Location (underscore format) | I395_North_Pentagon |
| `timestamp` | Capture timestamp | 20260329T191639Z |
| `car_count` | Cars detected in this image | 12 |
| `truck_count` | Trucks detected | 2 |
| `bus_count` | Buses detected (used as emergency proxy) | 0 |

### Asset CSV (`*_np_asset.csv`)

| Column | Description | Example |
| `item_id` | Texture ID referenced by `np_texture_id` in node CSV | 19 |
| `name` | Image filename | West_Dunn_Loring.jpeg |
| `path` | File path | .\User\_Global_\images\ |

---

## Updating for a new scene version

When node IDs change (e.g. moving from v111 to v03), only `config.py` needs to be updated:

1. Open the new node CSV and identify the 5 location pins on the subgrid
2. Trace each pin's children to find camera cubes, leaf nodes, weather cubes, and links
3. Update the IDs in `config.py`

The rest of the codebase references `config.py` and does not hardcode any node IDs.
