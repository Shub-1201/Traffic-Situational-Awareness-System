"""
config.py — Central configuration for the GaiaViz scene updater.

All node IDs, color mappings, texture mappings, and thresholds live here.
When node IDs change between scene versions, update THIS file only.
"""

# ══════════════════════════════════════════════════════════════════
#  SUBGRID
# ══════════════════════════════════════════════════════════════════
SUBGRID_ID = 42

# ══════════════════════════════════════════════════════════════════
#  LOCATION DEFINITIONS
# ══════════════════════════════════════════════════════════════════
# Each location has a hyperglyph root pin on the subgrid.
# The YOLO CSV uses underscored names; the traffic CSV uses descriptive names.

LOCATIONS = {
    "Dunn Loring": {
        "root_id": 43,
        "yolo_name": "I66_West_Dunn_Loring",
        "traffic_name": "I-66 West (near Dunn Loring)",
        "lat": 38.8844,
        "lon": -77.1526,
        "subgrid_pos": (-6.0, 5.8),
    },
    "Ballston": {
        "root_id": 62,
        "yolo_name": "I66_Mid_Ballston_Glebe",
        "traffic_name": "I-66 Mid (near Ballston/Glebe)",
        "lat": 38.8879,
        "lon": -77.1150,
        "subgrid_pos": (1.8, 11.2),
    },
    "Rosslyn": {
        "root_id": 80,
        "yolo_name": "I66_East_Rosslyn",
        "traffic_name": "I-66 East (near Rosslyn)",
        "lat": 38.8953,
        "lon": -77.0999,
        "subgrid_pos": (10.7, 15.2),
    },
    "Shirlington": {
        "root_id": 99,
        "yolo_name": "I395_South_Shirlington",
        "traffic_name": "I-395 South (near Shirlington)",
        "lat": 38.8326,
        "lon": -77.1050,
        "subgrid_pos": (2.3, -19.2),
    },
    "Pentagon": {
        "root_id": 117,
        "yolo_name": "I395_North_Pentagon",
        "traffic_name": "I-395 North (near Pentagon)",
        "lat": 38.8690,
        "lon": -77.0590,
        "subgrid_pos": (12.3, -2.0),
    },
}

# ══════════════════════════════════════════════════════════════════
#  CAMERA CUBE NODES
# ══════════════════════════════════════════════════════════════════
# bl=2, geo=1 (cube with camera JPEG texture), direct child of root pin

CAMERA_CUBES = {
    "Dunn Loring":  44,
    "Ballston":     63,
    "Rosslyn":      81,
    "Shirlington":  100,
    "Pentagon":     118,
}

# Location → camera image filename in the asset CSV
CAMERA_IMAGES = {
    "Dunn Loring":  "West_Dunn_Loring.jpeg",
    "Ballston":     "Mid_Ballston_Glebe.jpeg",
    "Rosslyn":      "example.jpg",               # placeholder
    "Shirlington":  "South_Shirlington.jpeg",
    "Pentagon":     "North_Pentagon.jpeg",
}

# ══════════════════════════════════════════════════════════════════
#  WEATHER CUBE NODES
# ══════════════════════════════════════════════════════════════════
# bl=3, geo=1 (cubes on the weather rod), each gets a weather icon texture
# Order per location: [storm, snowflake, sun]

WEATHER_CUBES = {
    "Dunn Loring":  [59, 60, 61],
    "Ballston":     [77, 78, 79],
    "Rosslyn":      [96, 97, 98],
    "Shirlington":  [114, 115, 116],
    "Pentagon":     [133, 134, 135],
}

# Weather icon order (matches the 3 cube positions)
WEATHER_IMAGES = ["storm.png", "snowflake.png", "sun.png"]

# ══════════════════════════════════════════════════════════════════
#  LEAF NODE IDS (detection glyphs)
# ══════════════════════════════════════════════════════════════════
# bl=4, geo=7 (ring glyphs), 3 clusters × 3 leaves per hyperglyph
# Cluster A = emergency, Cluster B = trucks, Cluster C = cars
# Within each cluster: [T0 (latest), T-1, T-2]

LEAF_NODES = {
    "Dunn Loring": {
        "emergency": [46, 47, 48],
        "truck":     [50, 51, 52],
        "car":       [54, 55, 56],
    },
    "Ballston": {
        "emergency": [65, 66, 67],
        "truck":     [69, 70, 71],
        "car":       [73, 74, 75],
    },
    "Rosslyn": {
        "emergency": [83, 84, 85],
        "truck":     [87, 88, 89],
        "car":       [91, 92, 93],
    },
    "Shirlington": {
        "emergency": [102, 103, 104],
        "truck":     [106, 107, 108],
        "car":       [110, 111, 112],
    },
    "Pentagon": {
        "emergency": [120, 121, 122],
        "truck":     [124, 125, 126],
        "car":       [128, 129, 130],
    },
}

# Detection type → CSV column in the YOLO detection file
DETECTION_COLUMNS = {
    "emergency": "bus_count",
    "truck":     "truck_count",
    "car":       "car_count",
}

# ══════════════════════════════════════════════════════════════════
#  LINK NODE IDS
# ══════════════════════════════════════════════════════════════════
# type=7 nodes connecting hyperglyphs, representing road segments

LINKS = {
    57: {
        "segment_name": "I-66 (Dunn Loring → Ballston)",
        "link_prefixes": ["I-66"],
        "locations": ["Dunn Loring", "Ballston"],
    },
    94: {
        "segment_name": "I-66 (Rosslyn → Ballston)",
        "link_prefixes": ["I-66"],
        "locations": ["Rosslyn", "Ballston"],
    },
    131: {
        "segment_name": "I-395 (Pentagon → Shirlington)",
        "link_prefixes": ["I-395"],
        "locations": ["Pentagon", "Shirlington"],
    },
}

# ══════════════════════════════════════════════════════════════════
#  COLOR PALETTES
# ══════════════════════════════════════════════════════════════════

# Link colors based on occupancy level
LINK_COLORS = {
    "low":      {"color_r": 0,   "color_g": 255, "color_b": 0},    # green
    "moderate": {"color_r": 255, "color_g": 255, "color_b": 0},    # yellow
    "high":     {"color_r": 255, "color_g": 0,   "color_b": 0},    # red
}

# Leaf colors based on detection type
LEAF_COLORS = {
    "emergency": {"color_r": 255, "color_g": 0,   "color_b": 0},   # red
    "truck":     {"color_r": 255, "color_g": 255, "color_b": 0},   # yellow
    "car":       {"color_r": 0,   "color_g": 0,   "color_b": 255}, # blue
    "grey":      {"color_r": 128, "color_g": 128, "color_b": 128}, # no detection
}

# ══════════════════════════════════════════════════════════════════
#  SCALE CONFIGURATION
# ══════════════════════════════════════════════════════════════════
MIN_SCALE = 0.15        # visible minimum when count > 0
MAX_SCALE = 1.2         # max size for highest count
ZERO_SCALE = 0.05       # near-invisible when count = 0
