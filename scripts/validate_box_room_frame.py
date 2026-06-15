# 文件功能：校验车箱房钢结构骨架的门洞、窗洞、门框和有限元分析设置。
import os
import sys

import FreeCAD as App

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import box_room_frame


def beam_by_name(beams, name):
    """按名称查找一根梁柱记录。"""
    for beam in beams:
        if beam["name"] == name:
            return beam
    raise AssertionError(f"{name} missing")


def assert_point(point, expected):
    """校验三维点坐标完全符合参数化输出。"""
    actual = tuple(round(value, 6) for value in point)
    wanted = tuple(round(value, 6) for value in expected)
    assert actual == wanted, f"expected {wanted}, got {actual}"


def assert_connector(beams, name, x, y, lower_z, upper_z):
    """校验窗框竖向连接杆接入相邻侧墙骨架。"""
    connector = beam_by_name(beams, name)
    assert_point(connector["start"], (x, y, lower_z))
    assert_point(connector["end"], (x, y, upper_z))


params = dict(box_room_frame.PARAMS)
params["make_single_compound"] = False

beams = box_room_frame.build_frame(params)
length = params["length"]
width = params["width"]
door_width = params["entry_door_width"]
door_height = params["entry_door_height"]
coffee_window_height = params["right_front_coffee_window_height"]
door_center_x = length * params["entry_door_center_ratio"]
door_x0 = door_center_x - door_width / 2.0
door_x1 = door_center_x + door_width / 2.0
window_width = params["right_rear_window_width"]
window_height = params["right_rear_window_height"]
window_bottom_z = params["right_rear_window_bottom_z"]
window_center_x = length * params["right_rear_window_center_ratio"]
window_x0 = window_center_x - window_width / 2.0
window_x1 = window_center_x + window_width / 2.0
window_top_z = window_bottom_z + window_height
left_window_width = params["left_front_window_width"]
left_window_height = params["left_front_window_height"]
left_window_bottom_z = params["left_front_window_bottom_z"]
left_window_center_x = length * params["left_front_window_center_ratio"]
left_window_x0 = left_window_center_x - left_window_width / 2.0
left_window_x1 = left_window_center_x + left_window_width / 2.0
left_window_top_z = left_window_bottom_z + left_window_height
toilet_window_width = params["left_rear_toilet_window_width"]
toilet_window_height = params["left_rear_toilet_window_height"]
toilet_window_bottom_z = params["left_rear_toilet_window_bottom_z"]
toilet_window_center_x = length * params["left_rear_toilet_window_center_ratio"]
toilet_window_x0 = toilet_window_center_x - toilet_window_width / 2.0
toilet_window_x1 = toilet_window_center_x + toilet_window_width / 2.0
toilet_window_top_z = toilet_window_bottom_z + toilet_window_height
z_mid = params["height"] / 2.0
rear_reinforcement_x = length - params["tube"]
rear_mount_y0 = width * 0.25
rear_mount_y1 = width * 0.75
rear_lower_mount_z = params["height"] * 0.25
rear_upper_mount_z = params["height"] * 0.70
rear_carrier_force_n = (
    (
        params["rear_motorcycle_mass_kg"]
        + params["rear_rack_mass_kg"]
        + params["rear_ac_unit_mass_kg"]
    )
    * 9.81
    * params["rear_carrier_dynamic_factor"]
)

assert door_width == 800.0, f"entry door width must be 800 mm, got {door_width}"
assert coffee_window_height == 1500.0, f"right front coffee window height must be 1500 mm, got {coffee_window_height}"
assert window_width == 1200.0, f"right rear window width must be 1200 mm, got {window_width}"
assert left_window_width == 1200.0, f"left front window width must be 1200 mm, got {left_window_width}"
assert toilet_window_width == 800.0, f"left rear toilet window width must be 800 mm, got {toilet_window_width}"
assert params["rear_motorcycle_mass_kg"] == 250.0
assert params["rear_rack_mass_kg"] == 80.0
assert params["rear_ac_unit_mass_kg"] == 45.0
assert params["rear_carrier_dynamic_factor"] == 1.5

front_jamb = beam_by_name(beams, "right_entry_door_front_jamb")
rear_jamb = beam_by_name(beams, "right_entry_door_rear_jamb")
header = beam_by_name(beams, "right_entry_door_header")
door_front_upper = beam_by_name(beams, "right_entry_door_front_upper_connector")
door_rear_upper = beam_by_name(beams, "right_entry_door_rear_upper_connector")
coffee_window_header = beam_by_name(beams, "right_front_coffee_window_header")
right_bottom_rail = beam_by_name(beams, "outer_long_rail_y2450_z0")
window_front = beam_by_name(beams, "right_rear_window_front_jamb")
window_rear = beam_by_name(beams, "right_rear_window_rear_jamb")
window_sill = beam_by_name(beams, "right_rear_window_sill")
window_top = beam_by_name(beams, "right_rear_window_header")
left_window_front = beam_by_name(beams, "left_front_window_front_jamb")
left_window_rear = beam_by_name(beams, "left_front_window_rear_jamb")
left_window_sill = beam_by_name(beams, "left_front_window_sill")
left_window_top = beam_by_name(beams, "left_front_window_header")
toilet_window_front = beam_by_name(beams, "left_rear_toilet_window_front_jamb")
toilet_window_rear = beam_by_name(beams, "left_rear_toilet_window_rear_jamb")
toilet_window_sill = beam_by_name(beams, "left_rear_toilet_window_sill")
toilet_window_top = beam_by_name(beams, "left_rear_toilet_window_header")
rear_left_vertical = beam_by_name(beams, "rear_carrier_left_vertical_reinforcement")
rear_right_vertical = beam_by_name(beams, "rear_carrier_right_vertical_reinforcement")
rear_lower_crossmember = beam_by_name(beams, "rear_carrier_lower_mount_crossmember")
rear_upper_crossmember = beam_by_name(beams, "rear_carrier_upper_mount_crossmember")
rear_left_lower_diagonal = beam_by_name(beams, "rear_carrier_left_lower_diagonal")
rear_right_lower_diagonal = beam_by_name(beams, "rear_carrier_right_lower_diagonal")
rear_left_upper_diagonal = beam_by_name(beams, "rear_carrier_left_upper_diagonal")
rear_right_upper_diagonal = beam_by_name(beams, "rear_carrier_right_upper_diagonal")

assert_point(front_jamb["start"], (door_x0, width, 0.0))
assert_point(front_jamb["end"], (door_x0, width, door_height))
assert_point(rear_jamb["start"], (door_x1, width, 0.0))
assert_point(rear_jamb["end"], (door_x1, width, door_height))
assert_point(header["start"], (door_x0, width, door_height))
assert_point(header["end"], (door_x1, width, door_height))
assert_point(door_front_upper["start"], (door_x0, width, door_height))
assert_point(door_front_upper["end"], (door_x0, width, params["height"]))
assert_point(door_rear_upper["start"], (door_x1, width, door_height))
assert_point(door_rear_upper["end"], (door_x1, width, params["height"]))
assert_point(coffee_window_header["start"], (0.0, width, coffee_window_height))
assert_point(coffee_window_header["end"], (door_x0, width, coffee_window_height))
assert_point(right_bottom_rail["start"], (0.0, width, 0.0))
assert_point(right_bottom_rail["end"], (length, width, 0.0))
assert_point(window_front["start"], (window_x0, width, window_bottom_z))
assert_point(window_front["end"], (window_x0, width, window_top_z))
assert_point(window_rear["start"], (window_x1, width, window_bottom_z))
assert_point(window_rear["end"], (window_x1, width, window_top_z))
assert_point(window_sill["start"], (window_x0, width, window_bottom_z))
assert_point(window_sill["end"], (window_x1, width, window_bottom_z))
assert_point(window_top["start"], (window_x0, width, window_top_z))
assert_point(window_top["end"], (window_x1, width, window_top_z))
assert_point(left_window_front["start"], (left_window_x0, 0.0, left_window_bottom_z))
assert_point(left_window_front["end"], (left_window_x0, 0.0, left_window_top_z))
assert_point(left_window_rear["start"], (left_window_x1, 0.0, left_window_bottom_z))
assert_point(left_window_rear["end"], (left_window_x1, 0.0, left_window_top_z))
assert_point(left_window_sill["start"], (left_window_x0, 0.0, left_window_bottom_z))
assert_point(left_window_sill["end"], (left_window_x1, 0.0, left_window_bottom_z))
assert_point(left_window_top["start"], (left_window_x0, 0.0, left_window_top_z))
assert_point(left_window_top["end"], (left_window_x1, 0.0, left_window_top_z))
assert_point(toilet_window_front["start"], (toilet_window_x0, 0.0, toilet_window_bottom_z))
assert_point(toilet_window_front["end"], (toilet_window_x0, 0.0, toilet_window_top_z))
assert_point(toilet_window_rear["start"], (toilet_window_x1, 0.0, toilet_window_bottom_z))
assert_point(toilet_window_rear["end"], (toilet_window_x1, 0.0, toilet_window_top_z))
assert_point(toilet_window_sill["start"], (toilet_window_x0, 0.0, toilet_window_bottom_z))
assert_point(toilet_window_sill["end"], (toilet_window_x1, 0.0, toilet_window_bottom_z))
assert_point(toilet_window_top["start"], (toilet_window_x0, 0.0, toilet_window_top_z))
assert_point(toilet_window_top["end"], (toilet_window_x1, 0.0, toilet_window_top_z))
assert_point(rear_left_vertical["start"], (rear_reinforcement_x, rear_mount_y0, 0.0))
assert_point(rear_left_vertical["end"], (rear_reinforcement_x, rear_mount_y0, params["height"]))
assert_point(rear_right_vertical["start"], (rear_reinforcement_x, rear_mount_y1, 0.0))
assert_point(rear_right_vertical["end"], (rear_reinforcement_x, rear_mount_y1, params["height"]))
assert_point(rear_lower_crossmember["start"], (rear_reinforcement_x, rear_mount_y0, rear_lower_mount_z))
assert_point(rear_lower_crossmember["end"], (rear_reinforcement_x, rear_mount_y1, rear_lower_mount_z))
assert_point(rear_upper_crossmember["start"], (rear_reinforcement_x, rear_mount_y0, rear_upper_mount_z))
assert_point(rear_upper_crossmember["end"], (rear_reinforcement_x, rear_mount_y1, rear_upper_mount_z))
assert_point(rear_left_lower_diagonal["start"], (rear_reinforcement_x, rear_mount_y0, rear_lower_mount_z))
assert_point(rear_left_lower_diagonal["end"], (length, 0.0, 0.0))
assert_point(rear_right_lower_diagonal["start"], (rear_reinforcement_x, rear_mount_y1, rear_lower_mount_z))
assert_point(rear_right_lower_diagonal["end"], (length, width, 0.0))
assert_point(rear_left_upper_diagonal["start"], (rear_reinforcement_x, rear_mount_y0, rear_upper_mount_z))
assert_point(rear_left_upper_diagonal["end"], (length, 0.0, params["height"]))
assert_point(rear_right_upper_diagonal["start"], (rear_reinforcement_x, rear_mount_y1, rear_upper_mount_z))
assert_point(rear_right_upper_diagonal["end"], (length, width, params["height"]))

for prefix, x0, x1, y, bottom_z, top_z in (
    ("right_rear_window", window_x0, window_x1, width, window_bottom_z, window_top_z),
    ("left_front_window", left_window_x0, left_window_x1, 0.0, left_window_bottom_z, left_window_top_z),
    (
        "left_rear_toilet_window",
        toilet_window_x0,
        toilet_window_x1,
        0.0,
        toilet_window_bottom_z,
        toilet_window_top_z,
    ),
):
    assert_connector(beams, f"{prefix}_front_lower_connector", x0, y, z_mid, bottom_z)
    assert_connector(beams, f"{prefix}_front_upper_connector", x0, y, top_z, params["height"])
    assert_connector(beams, f"{prefix}_rear_lower_connector", x1, y, z_mid, bottom_z)
    assert_connector(beams, f"{prefix}_rear_upper_connector", x1, y, top_z, params["height"])

middle_rail_names = {beam["name"] for beam in beams}
assert "outer_post_x2200_y2450" not in middle_rail_names
assert "side_middle_rail_y2450" not in middle_rail_names
assert "side_middle_rail_y2450_front_of_door" not in middle_rail_names

right_rail_rear = beam_by_name(beams, "side_middle_rail_y2450_rear_of_door")
assert_point(right_rail_rear["start"], (door_x1, width, z_mid))
assert_point(right_rail_rear["end"], (length, width, z_mid))

doc, created_beams = box_room_frame.create_document(params)
analysis = box_room_frame.create_fem_analysis(doc)

assert len(created_beams) == len(beams)
assert doc.getObject("fem_frame_compound") is not None
assert analysis.Name == "frame_static_analysis"
assert round(doc.getObject("rear_roof_downforce").Force.Value, 3) == round(
    rear_carrier_force_n * 1000.0,
    3,
)
for name in [
    "frame_steel_material",
    "front_bottom_fixed_constraint",
    "rear_roof_downforce",
    "frame_gmsh_mesh",
    "frame_calculix_solver",
]:
    assert doc.getObject(name) is not None, f"{name} missing"

print("OK: BoxRoomFrame validation passed")
