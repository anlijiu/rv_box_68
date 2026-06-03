# RV Exterior Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `RV_Exterior.FCStd`, a separate FreeCAD exterior model that reads as a 6.8 m single-rear-axle cab-over box truck RV with mj-style named exterior parts.

**Architecture:** Keep `RV.FCStd` as the logical/BOM skeleton and create `RV_Exterior.FCStd` independently. Implement a reproducible FreeCAD Python builder in `scripts/build_rv_exterior.py`, then run it through `freecad-mcp` or FreeCAD Python so the file can be regenerated. Validate the model by document guards, object counts, required object names, and FreeCAD view screenshots.

**Tech Stack:** FreeCAD Python API, `Part::Box`, `Part::Cylinder`, `App::Part`, freecad-mcp `execute_code`, shell `rg`, `git`.

---

## File Structure

- Create `scripts/build_rv_exterior.py`: deterministic FreeCAD builder for `RV_Exterior.FCStd`.
- Create `scripts/rv_exterior_config.py`: shared output path and dimension constants for builder and validator.
- Create `scripts/validate_rv_exterior.py`: FreeCAD validation script for required assemblies, dimensions, wheel structure, and object counts.
- Modify no source files outside `scripts/` unless a validation gap requires a spec update.
- Generate `RV_Exterior.FCStd` in the repository root.
- Leave existing `RV.FCStd` untouched.

## Task 1: Builder Skeleton And Document Guard

**Files:**
- Create: `scripts/rv_exterior_config.py`
- Create: `scripts/build_rv_exterior.py`

- [ ] **Step 1: Create shared config**

Create `scripts/rv_exterior_config.py` so the builder and validator use one source of truth for output paths and key dimensions:

```python
# 文件功能：提供 RV 外观生成与校验脚本共享的路径和尺寸参数。
import os


DOC_NAME = "RV_Exterior"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "RV_Exterior.FCStd")

P = {
    "overall_length": 6800,
    "overall_width": 2300,
    "overall_height": 3100,
    "cab_x_min": -1100,
    "cab_x_max": 600,
    "cab_width": 2200,
    "cab_height": 2050,
    "living_x_min": 900,
    "living_x_max": 5500,
    "living_width": 2300,
    "living_height": 2200,
    "living_floor_z": 850,
    "panel_thickness": 45,
    "wheelbase": 3800,
    "tire_diameter": 780,
    "tire_width": 240,
    "front_track": 1850,
    "rear_track": 1850,
    "frame_x_min": -700,
    "frame_x_max": 5400,
    "frame_rail_width": 80,
    "frame_rail_height": 160,
    "frame_y_center": 560,
    "frame_z_min": 560,
    "frame_z_max": 720,
    "crossmember_width": 80,
    "crossmember_length": 1200,
    "crossmember_height": 90,
    "crossmember_z_offset": 35,
}
```

- [ ] **Step 2: Create builder skeleton**

Create `scripts/build_rv_exterior.py` with this document guard:

```python
# 文件功能：生成独立的 RV 外观 FreeCAD 模型文件。
import os
import sys

import FreeCAD as App

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from rv_exterior_config import DOC_NAME, OUTPUT_FILE, P


COLORS = {
    "body": (0.82, 0.85, 0.86, 1.0),
    "trim": (0.18, 0.20, 0.22, 1.0),
    "chassis": (0.08, 0.09, 0.10, 1.0),
    "tire": (0.02, 0.02, 0.02, 1.0),
    "rim": (0.55, 0.58, 0.60, 1.0),
    "glass": (0.45, 0.75, 0.88, 0.35),
    "head_lamp": (1.0, 0.92, 0.55, 1.0),
    "turn_signal": (1.0, 0.55, 0.10, 1.0),
    "rear_lamp": (0.85, 0.05, 0.05, 1.0),
    "solar": (0.05, 0.10, 0.16, 1.0),
    "equipment": (0.88, 0.90, 0.90, 1.0),
    "awning": (0.22, 0.28, 0.32, 1.0),
}


def fresh_document():
    """Create a fresh RV_Exterior document without closing the RV document."""
    rv_doc = App.getDocument("RV")
    doc = App.getDocument(DOC_NAME)
    if doc is not None:
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    if rv_doc is not None and App.getDocument("RV") is None:
        raise RuntimeError("Unexpectedly closed RV document while creating RV_Exterior")
    return doc


def main():
    """Build and save the RV exterior document."""
    doc = fresh_document()
    root = doc.addObject("App::Part", "RV_Exterior_Asm")
    root.Label = "RV Exterior"
    doc.recompute()
    doc.saveAs(OUTPUT_FILE)
    print(f"OK: saved {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run builder through FreeCAD**

Run through freecad-mcp:

```python
import runpy

runpy.run_path("/home/an/workspace/freecad/rv_box_68/scripts/build_rv_exterior.py", run_name="__main__")
```

Expected output includes:

```text
OK: saved /home/an/workspace/freecad/rv_box_68/RV_Exterior.FCStd
```

- [ ] **Step 4: Verify RV was not modified**

Run in freecad-mcp:

```python
import FreeCAD as App
print("RV exists:", App.getDocument("RV") is not None)
print("RV_Exterior exists:", App.getDocument("RV_Exterior") is not None)
```

Expected output:

```text
RV exists: True
RV_Exterior exists: True
```

- [ ] **Step 5: Commit builder skeleton**

```bash
git add scripts/rv_exterior_config.py scripts/build_rv_exterior.py RV_Exterior.FCStd
git commit -m "Add RV exterior builder skeleton"
```

## Task 2: Geometry Helpers And Assembly Creation

**Files:**
- Modify: `scripts/build_rv_exterior.py`

- [ ] **Step 1: Add helpers**

Add helpers below `fresh_document()`:

```python
def set_visual(obj, color_key):
    """Apply the configured display color to a FreeCAD shape object."""
    color = COLORS[color_key]
    if hasattr(obj, "ViewObject") and obj.ViewObject:
        obj.ViewObject.ShapeColor = color[:3]
        if color[3] < 1.0 and hasattr(obj.ViewObject, "Transparency"):
            obj.ViewObject.Transparency = int((1.0 - color[3]) * 100)


def add_part(doc, parent, name, label=None):
    """Create an App::Part under the provided parent assembly."""
    obj = doc.addObject("App::Part", name)
    obj.Label = label or name
    parent.addObject(obj)
    return obj


def add_box(doc, parent, name, length, width, height, x, y, z, color_key):
    """Create a named box primitive under the provided parent assembly."""
    obj = doc.addObject("Part::Box", name)
    obj.Length = length
    obj.Width = width
    obj.Height = height
    obj.Placement.Base = App.Vector(x, y, z)
    parent.addObject(obj)
    set_visual(obj, color_key)
    return obj


def add_cylinder(doc, parent, name, radius, height, x, y, z, axis, color_key):
    """Create a named cylinder primitive oriented along the requested axis."""
    obj = doc.addObject("Part::Cylinder", name)
    obj.Radius = radius
    obj.Height = height
    if axis == "Y":
        obj.Placement.Rotation = App.Rotation(App.Vector(1, 0, 0), 90)
    elif axis == "X":
        obj.Placement.Rotation = App.Rotation(App.Vector(0, 1, 0), 90)
    elif axis == "Z":
        # Part::Cylinder is Z-aligned by default.
        pass
    else:
        raise RuntimeError(f"Unsupported cylinder axis: {axis}")
    obj.Placement.Base = App.Vector(x, y, z)
    parent.addObject(obj)
    set_visual(obj, color_key)
    return obj
```

- [ ] **Step 2: Add top-level assemblies**

In `main()`, create these under `RV_Exterior_Asm`:

```python
assemblies = {
    name: add_part(doc, root, name)
    for name in [
        "Cab_Asm",
        "Front_Fascia_Asm",
        "Chassis_Exterior_Asm",
        "Wheels_Asm",
        "Living_Box_Asm",
        "Openings_Asm",
        "Roof_Equipment_Asm",
        "Exterior_Accessories_Asm",
    ]
}
```

- [ ] **Step 3: Run and inspect assembly count**

Run builder through freecad-mcp and then:

```python
import FreeCAD as App
doc = App.getDocument("RV_Exterior")
root = doc.getObject("RV_Exterior_Asm")
print([obj.Name for obj in root.Group])
```

Expected output contains all 8 top-level assembly names.

## Task 3: Main Truck Proportions

**Files:**
- Modify: `scripts/build_rv_exterior.py`

- [ ] **Step 1: Add chassis geometry**

Add a `build_chassis(doc, assemblies)` function that creates frame rails, crossmembers, axles, mudguards, and side steps:

```python
def build_chassis(doc, assemblies):
    """Build visible chassis exterior parts below the cab and living box."""
    chassis = assemblies["Chassis_Exterior_Asm"]
    z = P["frame_z_min"]
    rail_len = P["frame_x_max"] - P["frame_x_min"]
    frame_y_left = P["frame_y_center"] - P["frame_rail_width"] / 2
    frame_y_right = -P["frame_y_center"] - P["frame_rail_width"] / 2
    crossmember_y = -P["crossmember_length"] / 2
    crossmember_z = z + P["crossmember_z_offset"]

    add_box(doc, chassis, "Frame_Rail_L", rail_len, P["frame_rail_width"], P["frame_rail_height"], P["frame_x_min"], frame_y_left, z, "chassis")
    add_box(doc, chassis, "Frame_Rail_R", rail_len, P["frame_rail_width"], P["frame_rail_height"], P["frame_x_min"], frame_y_right, z, "chassis")
    for name, x in [("Crossmember_Front", -500), ("Crossmember_Mid", 1900), ("Crossmember_Rear", 5200)]:
        add_box(doc, chassis, name, P["crossmember_width"], P["crossmember_length"], P["crossmember_height"], x, crossmember_y, crossmember_z, "chassis")

    add_cylinder(doc, chassis, "Front_Axle", 45, 2100, 0, -1050, 390, "Y", "chassis")
    add_cylinder(doc, chassis, "Rear_Axle", 55, 2100, P["wheelbase"], -1050, 390, "Y", "chassis")
    for name, x in [("Mudguard_Front_L", -160), ("Mudguard_Rear_L", P["wheelbase"] - 160)]:
        add_box(doc, chassis, name, 520, 80, 260, x, 965, 640, "trim")
    for name, x in [("Mudguard_Front_R", -160), ("Mudguard_Rear_R", P["wheelbase"] - 160)]:
        add_box(doc, chassis, name, 520, 80, 260, x, -1045, 640, "trim")
    add_box(doc, chassis, "Side_Step_L", 900, 160, 55, -350, 900, 720, "trim")
    add_box(doc, chassis, "Side_Step_R", 900, 160, 55, -350, -1060, 720, "trim")
```

- [ ] **Step 2: Add living box panels**

Add `build_living_box(doc, assemblies)` using `Panel thickness = 45`, with the structural panels plus spec-listed trim and skirt parts:

```python
def build_living_box(doc, assemblies):
    """Build the six structural living-box shell panels."""
    box = assemblies["Living_Box_Asm"]
    length = P["living_x_max"] - P["living_x_min"]
    width = P["living_width"]
    height = P["living_height"]
    t = P["panel_thickness"]
    floor_z = P["living_floor_z"]

    add_box(doc, box, "Floor_Panel", length, width, t, P["living_x_min"], -width / 2, floor_z, "body")
    add_box(doc, box, "Left_Wall", length, t, height, P["living_x_min"], width / 2 - t, floor_z, "body")
    add_box(doc, box, "Right_Wall", length, t, height, P["living_x_min"], -width / 2, floor_z, "body")
    add_box(doc, box, "Front_Wall", t, width, height, P["living_x_min"], -width / 2, floor_z, "body")
    add_box(doc, box, "Rear_Wall", t, width, height, P["living_x_max"] - t, -width / 2, floor_z, "body")
    add_box(doc, box, "Roof_Panel", length, width, t, P["living_x_min"], -width / 2, floor_z + height, "body")
    add_box(doc, box, "Corner_Trim_FL", 70, 70, height + t, P["living_x_min"] - 5, width / 2 - 70, floor_z, "trim")
    add_box(doc, box, "Corner_Trim_FR", 70, 70, height + t, P["living_x_min"] - 5, -width / 2, floor_z, "trim")
    add_box(doc, box, "Corner_Trim_RL", 70, 70, height + t, P["living_x_max"] - 65, width / 2 - 70, floor_z, "trim")
    add_box(doc, box, "Corner_Trim_RR", 70, 70, height + t, P["living_x_max"] - 65, -width / 2, floor_z, "trim")
    add_box(doc, box, "Side_Skirt_L", length, 80, 260, P["living_x_min"], width / 2 - 80, floor_z - 260, "trim")
    add_box(doc, box, "Side_Skirt_R", length, 80, 260, P["living_x_min"], -width / 2, floor_z - 260, "trim")
```

- [ ] **Step 3: Run and validate silhouette**

Update `main()` to call the Task 3 builders before recompute:

```python
def main():
    """Build and save the RV exterior document."""
    doc = fresh_document()
    root = doc.addObject("App::Part", "RV_Exterior_Asm")
    root.Label = "RV Exterior"
    assemblies = {
        name: add_part(doc, root, name)
        for name in [
            "Cab_Asm",
            "Front_Fascia_Asm",
            "Chassis_Exterior_Asm",
            "Wheels_Asm",
            "Living_Box_Asm",
            "Openings_Asm",
            "Roof_Equipment_Asm",
            "Exterior_Accessories_Asm",
        ]
    }
    build_chassis(doc, assemblies)
    build_living_box(doc, assemblies)
    doc.recompute()
    doc.saveAs(OUTPUT_FILE)
    print(f"OK: saved {OUTPUT_FILE}")
```

Run builder and capture `Isometric`, `Right`, and `Top` views. Expected: 6.8 m single-rear-axle truck proportions, not the old grid.

## Task 4: Cab, Front Fascia, And Wheels

**Files:**
- Modify: `scripts/build_rv_exterior.py`

- [ ] **Step 1: Add cab primitives**

Implement `build_cab(doc, assemblies)` with explicit per-part colors:

```python
def build_cab(doc, assemblies):
    """Build the cab-over cab exterior primitives."""
    cab = assemblies["Cab_Asm"]
    x_min = P["cab_x_min"]
    x_max = P["cab_x_max"]
    length = x_max - x_min
    width = P["cab_width"]
    y_min = -width / 2
    y_max = width / 2

    add_box(doc, cab, "Cab_Floor", length, width, 80, x_min, y_min, 760, "body")
    add_box(doc, cab, "Cab_Nose_Lower", 650, width, 520, x_min, y_min, 820, "body")
    add_box(doc, cab, "Cab_Front_Panel", 70, width, 1180, x_min, y_min, 1180, "body")
    add_box(doc, cab, "Cab_Side_Wall_L", length, 55, 1500, x_min, y_max - 55, 900, "body")
    add_box(doc, cab, "Cab_Side_Wall_R", length, 55, 1500, x_min, y_min, 900, "body")
    add_box(doc, cab, "Cab_Rear_Wall", 70, width, 1660, x_max - 70, y_min, 860, "body")
    add_box(doc, cab, "Cab_Roof", length - 120, width, 90, x_min + 60, y_min, 2400, "body")
    add_box(doc, cab, "Cab_Roof_Fairing", 860, width, 320, x_max - 860, y_min, 2490, "body")
    add_box(doc, cab, "Windshield", 45, 1380, 540, x_min - 10, -690, 1620, "glass")
    add_box(doc, cab, "Side_Window_L", 620, 35, 470, -760, y_max + 2, 1660, "glass")
    add_box(doc, cab, "Side_Window_R", 620, 35, 470, -760, y_min - 37, 1660, "glass")
    add_box(doc, cab, "Cab_Door_L", 760, 40, 980, -620, y_max + 5, 1050, "body")
    add_box(doc, cab, "Cab_Door_R", 760, 40, 980, -620, y_min - 45, 1050, "body")
    add_box(doc, cab, "Door_Handle_L", 120, 25, 35, -180, y_max + 45, 1460, "trim")
    add_box(doc, cab, "Door_Handle_R", 120, 25, 35, -180, y_min - 70, 1460, "trim")
    add_box(doc, cab, "Side_Mirror_L", 180, 35, 150, -980, y_max + 60, 1650, "chassis")
    add_box(doc, cab, "Side_Mirror_R", 180, 35, 150, -980, y_min - 95, 1650, "chassis")
```

- [ ] **Step 2: Add front fascia**

Implement `build_front_fascia(doc, assemblies)`:

```python
def build_front_fascia(doc, assemblies):
    """Build the front identity parts: grill, bumper, lamps, and tow hooks."""
    fascia = assemblies["Front_Fascia_Asm"]
    front_x = P["cab_x_min"] - 55

    add_box(doc, fascia, "Front_Grill", 40, 820, 360, front_x, -410, 1230, "trim")
    for index, z in enumerate([1280, 1370, 1460]):
        add_box(doc, fascia, f"Grill_Slat_{index + 1}", 50, 920, 35, front_x - 10, -460, z, "rim")
    add_box(doc, fascia, "Front_Bumper", 180, 2050, 220, front_x - 50, -1025, 760, "chassis")
    add_box(doc, fascia, "Head_Lamp_L", 55, 260, 150, front_x - 15, 520, 1260, "head_lamp")
    add_box(doc, fascia, "Head_Lamp_R", 55, 260, 150, front_x - 15, -780, 1260, "head_lamp")
    add_box(doc, fascia, "Turn_Signal_L", 55, 210, 90, front_x - 20, 780, 1120, "turn_signal")
    add_box(doc, fascia, "Turn_Signal_R", 55, 210, 90, front_x - 20, -990, 1120, "turn_signal")
    add_box(doc, fascia, "Tow_Hook_L", 80, 120, 60, front_x - 70, 310, 700, "trim")
    add_box(doc, fascia, "Tow_Hook_R", 80, 120, 60, front_x - 70, -430, 700, "trim")
```

- [ ] **Step 3: Add wheel containers**

Implement `build_wheels(doc, assemblies)` so each wheel is an `App::Part` container:

```python
def build_one_wheel(doc, parent, name, x, y):
    """Build one wheel container with tire, rim, and hub cylinders."""
    wheel = add_part(doc, parent, name)
    add_cylinder(doc, wheel, f"{name}_Tire", P["tire_diameter"] / 2, P["tire_width"], x, y - P["tire_width"] / 2, 390, "Y", "tire")
    add_cylinder(doc, wheel, f"{name}_Rim", 230, P["tire_width"] + 8, x, y - P["tire_width"] / 2 - 4, 390, "Y", "rim")
    add_cylinder(doc, wheel, f"{name}_Hub", 120, P["tire_width"] + 16, x, y - P["tire_width"] / 2 - 8, 390, "Y", "rim")


def build_wheels(doc, assemblies):
    """Build four wheel containers at the spec wheel-center positions."""
    wheels = assemblies["Wheels_Asm"]
    front_half_track = P["front_track"] / 2
    rear_half_track = P["rear_track"] / 2

    build_one_wheel(doc, wheels, "Front_Wheel_L", 0, front_half_track)
    build_one_wheel(doc, wheels, "Front_Wheel_R", 0, -front_half_track)
    build_one_wheel(doc, wheels, "Rear_Wheel_L", P["wheelbase"], rear_half_track)
    build_one_wheel(doc, wheels, "Rear_Wheel_R", P["wheelbase"], -rear_half_track)
```

- [ ] **Step 4: Run and inspect wheels**

Update `main()` so the Task 4 builders run before recompute:

```python
    build_chassis(doc, assemblies)
    build_living_box(doc, assemblies)
    build_cab(doc, assemblies)
    build_front_fascia(doc, assemblies)
    build_wheels(doc, assemblies)
    doc.recompute()
```

Run in freecad-mcp:

```python
doc = App.getDocument("RV_Exterior")
wheels = doc.getObject("Wheels_Asm").Group
print([w.Name for w in wheels])
print([len(w.Group) for w in wheels])
```

Expected output:

```text
['Front_Wheel_L', 'Front_Wheel_R', 'Rear_Wheel_L', 'Rear_Wheel_R']
[3, 3, 3, 3]
```

## Task 5: Openings, Roof Equipment, And Accessories

**Files:**
- Modify: `scripts/build_rv_exterior.py`

- [ ] **Step 1: Add additive opening overlays**

Implement `build_openings(doc, assemblies)` with shallow boxes placed on wall surfaces:

```python
def build_openings(doc, assemblies):
    """Build exterior door, window, hatch, and grille overlays."""
    openings = assemblies["Openings_Asm"]
    right_y = -P["living_width"] / 2 - 18
    left_y = P["living_width"] / 2 + 3
    rear_x = P["living_x_max"] + 3

    add_box(doc, openings, "Entry_Door", 45, 720, 1580, 1320, right_y, 990, "body")
    add_box(doc, openings, "Pass_Through_Frame", 45, 640, 420, 2680, right_y, 1120, "trim")
    add_box(doc, openings, "Side_Window_1", 55, 820, 520, 2450, right_y - 6, 1810, "glass")
    add_box(doc, openings, "Side_Window_2", 55, 900, 520, 3900, right_y - 6, 1810, "glass")
    add_box(doc, openings, "Rear_Window", 55, 850, 470, rear_x, -425, 1840, "glass")
    add_box(doc, openings, "Service_Hatch_1", 45, 620, 380, 3300, left_y, 1080, "trim")
    add_box(doc, openings, "Service_Hatch_2", 45, 560, 340, 4550, left_y, 1080, "trim")
    add_box(doc, openings, "Vent_Grille", 45, 520, 260, 4700, left_y, 1280, "trim")
```

- [ ] **Step 2: Add roof equipment**

Implement `build_roof_equipment(doc, assemblies)`:

```python
def build_roof_equipment(doc, assemblies):
    """Build roof-mounted equipment and rack rails."""
    roof = assemblies["Roof_Equipment_Asm"]
    roof_z = P["living_floor_z"] + P["living_height"] + P["panel_thickness"]

    roof_ac = add_part(doc, roof, "Roof_AC")
    add_box(doc, roof_ac, "Roof_AC_Base", 760, 620, 210, 1900, -310, roof_z, "equipment")
    add_box(doc, roof_ac, "Roof_AC_Cover", 620, 500, 170, 1970, -250, roof_z + 210, "equipment")
    add_box(doc, roof, "Solar_Panel_1", 1120, 620, 35, 3000, 210, roof_z + 35, "solar")
    add_box(doc, roof, "Solar_Panel_2", 1120, 620, 35, 4200, 210, roof_z + 35, "solar")
    add_box(doc, roof, "Vent_Fan_1", 430, 430, 95, 2850, -760, roof_z + 45, "equipment")
    add_box(doc, roof, "Vent_Fan_2", 430, 430, 95, 4550, -760, roof_z + 45, "equipment")
    add_cylinder(doc, roof, "Antenna", 18, 520, 5050, 720, roof_z + 70, "Z", "trim")
    add_box(doc, roof, "Roof_Rack_L", 3650, 45, 80, 1600, 910, roof_z + 80, "trim")
    add_box(doc, roof, "Roof_Rack_R", 3650, 45, 80, 1600, -955, roof_z + 80, "trim")
```

- [ ] **Step 3: Add exterior accessories**

Implement `build_accessories(doc, assemblies)` with awning X = 1500 to 4300, Y near -1170, Z = 2700 to 2850:

```python
def build_accessories(doc, assemblies):
    """Build exterior accessories, rear lamps, and small marker lights."""
    accessories = assemblies["Exterior_Accessories_Asm"]
    right_y = -P["living_width"] / 2
    left_marker_y = P["living_width"] / 2 - 80
    rear_x = P["living_x_max"]

    awning = add_part(doc, accessories, "Awning")
    add_box(doc, awning, "Awning_Case", 2800, 100, 130, 1500, right_y - 120, 2720, "awning")
    add_box(doc, awning, "Awning_Lead_Rail", 2800, 65, 70, 1500, right_y - 185, 2550, "awning")
    ladder = add_part(doc, accessories, "Ladder")
    add_box(doc, ladder, "Ladder_Left_Rail", 55, 45, 1420, rear_x + 35, 620, 1080, "trim")
    add_box(doc, ladder, "Ladder_Right_Rail", 55, 45, 1420, rear_x + 35, 900, 1080, "trim")
    for index, z in enumerate([1260, 1640, 2020]):
        add_box(doc, ladder, f"Ladder_Rung_{index + 1}", 50, 330, 35, rear_x + 50, 615, z, "trim")
    spare_tire_carrier = add_part(doc, accessories, "Spare_Tire_Carrier")
    add_cylinder(doc, spare_tire_carrier, "Spare_Tire", 320, 180, rear_x + 70, -90, 1280, "X", "tire")
    add_box(doc, accessories, "Storage_Box", 850, 420, 360, 2050, right_y - 90, 840, "trim")
    add_box(doc, accessories, "Marker_Light_Front_L", 45, 110, 55, 1150, left_marker_y, 2810, "turn_signal")
    add_box(doc, accessories, "Marker_Light_Front_R", 45, 110, 55, 1150, right_y - 30, 2810, "turn_signal")
    add_box(doc, accessories, "Marker_Light_Rear_L", 45, 110, 55, 5200, left_marker_y, 2810, "turn_signal")
    add_box(doc, accessories, "Marker_Light_Rear_R", 45, 110, 55, 5200, right_y - 30, 2810, "turn_signal")
    add_box(doc, accessories, "Rear_Lamp_L", 55, 150, 240, rear_x + 8, 760, 980, "rear_lamp")
    add_box(doc, accessories, "Rear_Lamp_R", 55, 150, 240, rear_x + 8, -910, 980, "rear_lamp")
```

- [ ] **Step 4: Capture views**

Update `main()` so every exterior builder runs before recompute:

```python
    build_chassis(doc, assemblies)
    build_living_box(doc, assemblies)
    build_cab(doc, assemblies)
    build_front_fascia(doc, assemblies)
    build_wheels(doc, assemblies)
    build_openings(doc, assemblies)
    build_roof_equipment(doc, assemblies)
    build_accessories(doc, assemblies)
    doc.recompute()
```

Capture:

```text
Isometric
Front
Right
Top
```

Expected visual result: from right side, the model reads as a 6.8 m single-rear-axle box truck RV.

## Task 6: Validation Script

**Files:**
- Create: `scripts/validate_rv_exterior.py`

- [ ] **Step 1: Create validation script**

Create a FreeCAD validation script that checks all code-level spec checks:

```python
# 文件功能：校验 RV 外观 FreeCAD 模型的装配结构、关键尺寸和对象数量。
import os
import sys

import FreeCAD as App

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from rv_exterior_config import OUTPUT_FILE, P

assert os.path.exists(OUTPUT_FILE), f"{OUTPUT_FILE} missing"
doc = App.getDocument("RV_Exterior")
assert doc is not None, "RV_Exterior document not open"
root = doc.getObject("RV_Exterior_Asm")
assert root is not None, "RV_Exterior_Asm missing"

required = [
    "Cab_Asm",
    "Front_Fascia_Asm",
    "Chassis_Exterior_Asm",
    "Wheels_Asm",
    "Living_Box_Asm",
    "Openings_Asm",
    "Roof_Equipment_Asm",
    "Exterior_Accessories_Asm",
]
for name in required:
    assert doc.getObject(name) is not None, f"{name} missing"

root_names = {obj.Name for obj in root.Group}
assert root_names == set(required), f"expected 8 top-level assemblies, got {sorted(root_names)}"

wheels = doc.getObject("Wheels_Asm").Group
assert len(wheels) == 4, f"expected 4 wheel containers, got {len(wheels)}"
expected_wheels = {
    "Front_Wheel_L": (0, P["front_track"] / 2),
    "Front_Wheel_R": (0, -P["front_track"] / 2),
    "Rear_Wheel_L": (P["wheelbase"], P["rear_track"] / 2),
    "Rear_Wheel_R": (P["wheelbase"], -P["rear_track"] / 2),
}
for wheel in wheels:
    names = {child.Name for child in wheel.Group}
    assert any(name.endswith("_Tire") for name in names), f"{wheel.Name} tire missing"
    assert any(name.endswith("_Hub") for name in names), f"{wheel.Name} hub missing"
    tire = next(child for child in wheel.Group if child.Name.endswith("_Tire"))
    expected_x, expected_y = expected_wheels[wheel.Name]
    assert tire.Placement.Base.x == expected_x, f"{wheel.Name} X center mismatch"
    assert tire.Placement.Base.y == expected_y - P["tire_width"] / 2, f"{wheel.Name} Y placement mismatch"

for name in ["Cab_Nose_Lower", "Cab_Front_Panel", "Cab_Roof_Fairing", "Windshield"]:
    assert doc.getObject(name) is not None, f"{name} missing"
for name in ["Floor_Panel", "Left_Wall", "Right_Wall", "Front_Wall", "Rear_Wall", "Roof_Panel"]:
    panel = doc.getObject(name)
    assert panel is not None, f"{name} missing"
    dimensions = [panel.Length.Value, panel.Width.Value, panel.Height.Value]
    assert 45 in dimensions, f"{name} does not use 45 mm panel thickness"
for name in ["Corner_Trim_FL", "Corner_Trim_FR", "Corner_Trim_RL", "Corner_Trim_RR", "Side_Skirt_L", "Side_Skirt_R"]:
    assert doc.getObject(name) is not None, f"{name} missing"
for name in ["Front_Grill", "Front_Bumper", "Head_Lamp_L", "Head_Lamp_R"]:
    assert doc.getObject(name) is not None, f"{name} missing"
for name in ["Entry_Door", "Pass_Through_Frame", "Side_Window_1", "Side_Window_2", "Rear_Window", "Service_Hatch_1", "Service_Hatch_2", "Vent_Grille"]:
    assert doc.getObject(name) is not None, f"{name} missing"
for name in ["Roof_AC", "Roof_Rack_L", "Roof_Rack_R", "Antenna"]:
    assert doc.getObject(name) is not None, f"{name} missing"
for name in ["Roof_AC_Base", "Roof_AC_Cover"]:
    assert doc.getObject(name) is not None, f"{name} missing"
for name in ["Awning", "Ladder", "Spare_Tire_Carrier", "Storage_Box", "Rear_Lamp_L", "Rear_Lamp_R"]:
    assert doc.getObject(name) is not None, f"{name} missing"
for name in ["Awning_Case", "Awning_Lead_Rail", "Ladder_Left_Rail", "Ladder_Right_Rail", "Ladder_Rung_1", "Spare_Tire"]:
    assert doc.getObject(name) is not None, f"{name} missing"
for name in ["Marker_Light_Front_L", "Marker_Light_Front_R", "Marker_Light_Rear_L", "Marker_Light_Rear_R"]:
    assert doc.getObject(name) is not None, f"{name} missing"

assert len(doc.getObject("Cab_Asm").Group) >= 14, "Cab_Asm must contain at least 14 parts"
assert len(doc.getObject("Living_Box_Asm").Group) >= 12, "Living_Box_Asm must contain at least 12 parts"
assert len(doc.getObject("Roof_Equipment_Asm").Group) >= 8, "Roof_Equipment_Asm must contain at least 8 parts"
assert len(doc.getObject("Exterior_Accessories_Asm").Group) >= 10, "Exterior_Accessories_Asm must contain at least 10 parts"
assert 40 <= len(doc.Objects) <= 120, f"unexpected object count: {len(doc.Objects)}"

print("OK: RV_Exterior validation passed")
```

- [ ] **Step 2: Run validation**

Run:

```python
import runpy

runpy.run_path("/home/an/workspace/freecad/rv_box_68/scripts/validate_rv_exterior.py")
```

Expected output:

```text
OK: RV_Exterior validation passed
```

## Task 7: Final Save And Commit

**Files:**
- Modify: `scripts/build_rv_exterior.py`
- Create: `scripts/validate_rv_exterior.py`
- Create: `RV_Exterior.FCStd`

- [ ] **Step 1: Rebuild from clean document**

Run the builder once from a clean `RV_Exterior` document.

- [ ] **Step 2: Run validation**

Run `scripts/validate_rv_exterior.py` in FreeCAD and confirm success.

- [ ] **Step 3: Capture screenshots**

Use freecad-mcp `get_view` for Isometric, Front, Right, and Top.

- [ ] **Step 4: Manual visual validation**

Confirm from screenshots:

```text
Right view reads as a 6.8 m cab-over single-rear-axle box truck RV.
Front view shows grill, bumper, head lamps, turn signals, and cab-over proportions.
Top view shows roof AC, two solar panels, vent fans, antenna, and roof rack rails.
The model is made of named exterior objects, not an abstract grid or placeholder skeleton.
```

- [ ] **Step 5: Check git status**

```bash
git status --short
```

Expected changed/new files:

```text
?? RV_Exterior.FCStd
?? scripts/build_rv_exterior.py
?? scripts/rv_exterior_config.py
?? scripts/validate_rv_exterior.py
```

`RV.FCStd` may remain untracked from earlier work and should not be included unless explicitly requested.

- [ ] **Step 6: Commit implementation**

```bash
git add scripts/rv_exterior_config.py scripts/build_rv_exterior.py scripts/validate_rv_exterior.py RV_Exterior.FCStd
git commit -m "Build RV exterior FreeCAD model"
```
