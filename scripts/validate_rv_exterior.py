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

# Count user-created (non-system) objects: exclude Origin, Axes, Planes, Points
system_names = {"Origin", "X_Axis", "Y_Axis", "Z_Axis", "XY_Plane", "XZ_Plane", "YZ_Plane", "X", "Y", "Z"}
user_objects = [obj for obj in doc.Objects if not (obj.Name in system_names or any(obj.Name.startswith(p) for p in ["Origin", "X_Axis", "Y_Axis", "Z_Axis", "XY_Plane", "XZ_Plane", "YZ_Plane"]))]
assert 40 <= len(user_objects) <= 120, f"unexpected user object count: {len(user_objects)}"

print("OK: RV_Exterior validation passed")
