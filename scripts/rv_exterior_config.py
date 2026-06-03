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
