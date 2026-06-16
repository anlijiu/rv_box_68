#!/home/an/.program/freecad/squashfs-root/usr/bin/FreeCADCmd
# 文件功能：参数化生成车箱房钢结构龙骨骨架和有限元分析设置。
"""参数化生成车箱房钢结构龙骨骨架。


PYTHONPATH=/home/an/.program/freecad/squashfs-root/usr/lib \
  /home/an/.program/freecad/squashfs-root/usr/bin/python \
  box_room_frame.py

默认输出:
    /tmp/a.FCStd

所有尺寸单位都是毫米。默认整体尺寸:
    6600 x 2450 x 2450

导出 1:30 STL:
  PYTHONPATH=/home/an/.program/freecad/squashfs-root/usr/lib \
  /home/an/.program/freecad/squashfs-root/usr/bin/python \
  -c "import box_room_frame; print(box_room_frame.export_stl_1_30())"

在 FreeCAD GUI 里手动编辑并导出 Python:
  1. 直接运行本脚本生成 /tmp/a.FCStd；
  2. 打开 /tmp/a.FCStd，选中某根钢材；
  3. 在属性面板的 Beam 分组里改 StartX/StartY/StartZ/EndX/EndY/EndZ/Tube；
  4. 在 Python 控制台运行:
       import sys
       sys.path.append("/home/an/workspace/test/python/freecad")
       import box_room_frame
       box_room_frame.rebuild_beams_from_properties()
       box_room_frame.export_current_document_to_python()
"""

import FreeCAD as App
import Part
import json


PARAMS = {
    # FreeCAD 文档名称；如果同名文档已存在，脚本会清空后重新生成。
    "doc_name": "BoxRoomFrame",
    # 主模型保存路径，格式为 FreeCAD 原生 FCStd。
    "output_path": "/tmp/a.FCStd",
    # 车箱房外包络尺寸：长、宽、高。
    "length": 6600.0,
    "width": 2450.0,
    "height": 2450.0,
    # 主龙骨方钢管边长。当前用实心方管实体表达，方便预览和导出。
    "tube": 80.0,
    # 车头和车尾端面 X 形抗扭撑的方钢管边长。
    "x_brace_tube": 50.0,
    # 车尾挂载摩托、挂架和空调外机时，车尾端面内侧加强件的方钢管边长。
    "rear_reinforcement_tube": 80.0,
    # 人面向车头、向车尾看时右手侧车厢中部的日常进出门宽度。
    "entry_door_width": 800.0,
    # 日常进出门高度。
    "entry_door_height": 2000.0,
    # 日常进出门中心在车长方向的位置比例。0.5 表示位于车厢中部。
    "entry_door_center_ratio": 0.5,
    # 右侧车头到门框之间的咖啡售卖窗高度，窗底就是地板。
    "right_front_coffee_window_height": 1500.0,
    # 人面向车头、向车尾看时右手侧后部床头上方窗户宽度。
    "right_rear_window_width": 1200.0,
    # 右侧后部床头上方窗户高度。
    "right_rear_window_height": 600.0,
    # 右侧后部床头上方窗户底边离地高度。
    "right_rear_window_bottom_z": 1600.0,
    # 右侧后部床头上方窗户中心在车长方向的位置比例。
    "right_rear_window_center_ratio": 0.82,
    # 人面向车头、向车尾看时左手侧车头部卡座茶几旁窗户宽度。
    # 窗后边缘延伸到第一个分仓纵梁位置。
    "left_front_window_width": 1612.0,
    # 左侧车头部卡座茶几旁窗户高度。
    "left_front_window_height": 600.0,
    # 左侧车头部卡座茶几旁窗户底边离地高度。
    "left_front_window_bottom_z": 1600.0,
    # 左侧车头部卡座茶几旁窗户中心在车长方向的位置比例。
    # 该比例对应窗后边缘对齐第一个分仓纵梁。
    "left_front_window_center_ratio": 0.2112121212121212,
    # 人面向车头、向车尾看时左手侧中部偏后的厕所窗宽度。
    "left_rear_toilet_window_width": 800.0,
    # 左手侧中部偏后的厕所窗高度。
    "left_rear_toilet_window_height": 400.0,
    # 左手侧中部偏后的厕所窗底边离地高度。
    "left_rear_toilet_window_bottom_z": 1700.0,
    # 左手侧中部偏后的厕所窗中心在车长方向的位置比例。
    "left_rear_toilet_window_center_ratio": 0.61,
    # 车尾外挂摩托估算重量。
    "rear_motorcycle_mass_kg": 250.0,
    # 车尾摩托挂架估算重量。
    "rear_rack_mass_kg": 80.0,
    # 车尾空调外机估算重量。
    "rear_ac_unit_mass_kg": 45.0,
    # 行驶颠簸和冲击的等效动载系数。
    "rear_carrier_dynamic_factor": 1.5,
    # 长度方向分仓数量。3 表示长 6600mm 被分成 3 个等长单元。
    "bay_count": 3,
    # True: 所有梁柱合并为一个 compound，模型树更干净。
    # False: 每根梁柱单独成为一个对象，便于逐根检查、编辑和导出。
    "make_single_compound": False,
}


# 图形界面中使用的颜色。无界面执行时 ViewObject 不存在，会自动跳过。
COLOR_OUTER = (0.25, 0.28, 0.30, 1.0)
COLOR_INNER = (0.75, 0.18, 0.12, 1.0)
BEAM_PROPERTY_NAMES = (
    "StartX",
    "StartY",
    "StartZ",
    "EndX",
    "EndY",
    "EndZ",
    "Tube",
    "Role",
)


def clear_doc(doc):
    """清空 FreeCAD 文档中的所有对象。

    参数:
        doc: FreeCAD 文档对象。

    用途:
        脚本可以重复执行。每次生成前先删除旧对象，避免同一个文档里
        累积多套骨架，导致保存出的 FCStd 难以判断哪套是最新结果。

    注意:
        这里使用 list(doc.Objects) 复制一份对象列表后再删除，因为删除
        对象会改变 doc.Objects 本身。直接遍历 doc.Objects 边遍历边删除，
        容易跳过对象。
    """
    for obj in list(doc.Objects):
        doc.removeObject(obj.Name)


def print_point(label, point):
    """按统一格式打印一个三维点坐标。

    参数:
        label: 点的标签，例如 "start" 或 "end"。
        point: 三维坐标，格式为 (x, y, z)，单位 mm。

    用途:
        调试 make_beam 时查看每根梁柱的中心线起点和终点，确认骨架
        空间位置是否符合预期。
    """
    x, y, z = point
    message = f"{label}: x={x:.2f}, y={y:.2f}, z={z:.2f}"
    print(message, flush=True)
    App.Console.PrintMessage(message + "\n")


def make_beam(name, start, end, tube, role):
    """按起点和终点生成一根矩形方钢管梁柱实体。

    参数:
        name: 梁柱名称，用于后续对象命名和排查。
        start: 梁柱中心线起点坐标，格式为 (x, y, z)，单位 mm。
        end: 梁柱中心线终点坐标，格式为 (x, y, z)，单位 mm。
        tube: 方钢管截面边长，单位 mm。当前用实心方管表示。
        role: 梁柱角色标记，通常为 "outer" 或 "inner"。

    返回:
        一个字典，包含 name、shape、role。shape 是 FreeCAD Part Shape。

    建模规则:
        1. 如果梁柱沿 X、Y 或 Z 轴方向布置，直接用 Part.makeBox 生成，
           这样计算最简单，也能保证尺寸准确。
        2. 如果梁柱是斜向布置，例如端面 X 抗扭撑，则先在局部 X 轴上
           生成一根方管，再把局部 X 轴旋转到 start -> end 的方向。
        3. start/end 表示中心线位置，因此实体会围绕中心线向两侧偏移
           tube / 2，方便按外框坐标布置骨架。
    """
    message = f"make_beam: name={name}, tube={tube:.2f}, role={role}"
    print(message, flush=True)
    App.Console.PrintMessage(message + "\n")
    print_point("  start", start)
    print_point("  end", end)

    x1, y1, z1 = start
    x2, y2, z2 = end

    # 先计算三个方向上的跨度，用它判断梁柱是轴向件还是斜撑。
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    dz = abs(z2 - z1)

    if dx > 0 and dy == 0 and dz == 0:
        # 沿 X 方向的梁：长度为 dx，截面为 tube x tube。
        # y/z 坐标减 tube/2，让输入点落在方管中心线上。
        base = App.Vector(min(x1, x2), y1 - tube / 2, z1 - tube / 2)
        shape = Part.makeBox(dx, tube, tube, base)
    elif dy > 0 and dx == 0 and dz == 0:
        # 沿 Y 方向的梁：用于端面横梁、屋面/地面横向梁等。
        base = App.Vector(x1 - tube / 2, min(y1, y2), z1 - tube / 2)
        shape = Part.makeBox(tube, dy, tube, base)
    elif dz > 0 and dx == 0 and dy == 0:
        # 沿 Z 方向的柱：用于四角立柱和分仓立柱。
        base = App.Vector(x1 - tube / 2, y1 - tube / 2, min(z1, z2))
        shape = Part.makeBox(tube, tube, dz, base)
    else:
        # 非轴向件主要用于 X 形抗扭撑。先转成 FreeCAD 向量对象。
        start_vec = App.Vector(x1, y1, z1)
        end_vec = App.Vector(x2, y2, z2)
        direction = end_vec.sub(start_vec)
        length = direction.Length
        if length <= 0:
            raise ValueError(f"{name} has zero length: {start} -> {end}")

        # 斜撑的建模方法：
        # 1. 在局部坐标中先做一根沿 X 轴的方管；
        # 2. 方管的 y/z 起点为 -tube/2，让中心线位于局部 X 轴；
        # 3. 用 App.Rotation 把局部 X 轴旋转到真实方向 direction；
        # 4. Placement 的平移部分放在 start_vec，使斜撑从 start 开始。
        shape = Part.makeBox(length, tube, tube, App.Vector(0, -tube / 2, -tube / 2))
        shape.Placement = App.Placement(
            start_vec,
            App.Rotation(App.Vector(1, 0, 0), direction),
        )

    return {
        "name": name,
        "start": _point_as_floats(start),
        "end": _point_as_floats(end),
        "tube": float(tube),
        "shape": shape,
        "role": role,
    }


def add_beam(beams, seen, name, start, end, tube, role):
    """把一根梁柱加入列表，并自动去重。

    参数:
        beams: 已生成梁柱列表，函数会向里面追加新梁柱。
        seen: 已加入梁柱的几何键集合，用于判断重复。
        name/start/end/tube/role: 传给 make_beam 的梁柱参数。

    为什么需要去重:
        多条建模规则可能会描述同一根构件。例如端面框架的顶梁和屋面横梁
        在边界位置可能重合。如果不去重，模型里会出现两根完全重叠的实体，
        既增加文件体积，也会影响后续布尔操作或 STL 网格质量。

    去重方式:
        把 start/end 两个点排序后展平成 tuple，再四舍五入到 6 位小数。
        这样同一根梁柱无论从 A->B 还是 B->A 添加，都会得到同一个 key。
    """
    key = tuple(round(v, 6) for point in sorted((start, end)) for v in point)
    if key in seen:
        return
    seen.add(key)
    beams.append(make_beam(name, start, end, tube, role))


def add_optional_beam(beams, seen, name, start, end, tube, role):
    """在长度有效时添加梁柱，零长度梁柱直接跳过。"""
    if _point_as_floats(start) == _point_as_floats(end):
        return
    add_beam(beams, seen, name, start, end, tube, role)


def add_side_window_frame(beams, seen, prefix, x0, x1, y, z_mid, z_bottom, z_top, z_roof, tube):
    """添加侧墙窗框，并把窗框竖边接入中腰梁和顶梁。"""
    for name, start, end in (
        (
            f"{prefix}_front_jamb",
            (x0, y, z_bottom),
            (x0, y, z_top),
        ),
        (
            f"{prefix}_rear_jamb",
            (x1, y, z_bottom),
            (x1, y, z_top),
        ),
        (
            f"{prefix}_sill",
            (x0, y, z_bottom),
            (x1, y, z_bottom),
        ),
        (
            f"{prefix}_header",
            (x0, y, z_top),
            (x1, y, z_top),
        ),
        (
            f"{prefix}_front_lower_connector",
            (x0, y, z_mid),
            (x0, y, z_bottom),
        ),
        (
            f"{prefix}_front_upper_connector",
            (x0, y, z_top),
            (x0, y, z_roof),
        ),
        (
            f"{prefix}_rear_lower_connector",
            (x1, y, z_mid),
            (x1, y, z_bottom),
        ),
        (
            f"{prefix}_rear_upper_connector",
            (x1, y, z_top),
            (x1, y, z_roof),
        ),
    ):
        add_beam(
            beams,
            seen,
            name,
            start,
            end,
            tube,
            "inner",
        )


def _point_as_floats(point):
    """把三维点标准化为 float tuple，便于保存和导出。"""
    if len(point) != 3:
        raise ValueError(f"point must have 3 values: {point!r}")
    return tuple(float(value) for value in point)


def _beam_record(name, start, end, tube, role):
    """创建一条可序列化的钢材记录。"""
    return {
        "name": str(name),
        "start": _point_as_floats(start),
        "end": _point_as_floats(end),
        "tube": float(tube),
        "role": str(role),
    }


def _add_beam_properties(obj, beam):
    """把钢材参数写入 FreeCAD 对象属性面板，供手动编辑和导出。"""
    for prop_name in BEAM_PROPERTY_NAMES:
        if prop_name in obj.PropertiesList:
            continue
        prop_type = "App::PropertyString" if prop_name == "Role" else "App::PropertyFloat"
        obj.addProperty(prop_type, prop_name, "Beam", "Editable beam parameter")

    start = _point_as_floats(beam["start"])
    end = _point_as_floats(beam["end"])
    obj.StartX, obj.StartY, obj.StartZ = start
    obj.EndX, obj.EndY, obj.EndZ = end
    obj.Tube = float(beam["tube"])
    obj.Role = str(beam["role"])


def _beam_record_from_object(obj):
    """从 FreeCAD 对象属性读回一条钢材记录。"""
    missing = [name for name in BEAM_PROPERTY_NAMES if not hasattr(obj, name)]
    if missing:
        raise ValueError(f"{obj.Name} is missing beam properties: {missing}")
    return _beam_record(
        obj.Name,
        (obj.StartX, obj.StartY, obj.StartZ),
        (obj.EndX, obj.EndY, obj.EndZ),
        obj.Tube,
        obj.Role,
    )


def beam_records_from_document(doc):
    """从当前文档收集所有带 Beam 属性的钢材记录。"""
    records = []
    for obj in doc.Objects:
        if all(hasattr(obj, name) for name in BEAM_PROPERTY_NAMES):
            records.append(_beam_record_from_object(obj))
    return sorted(records, key=lambda record: record["name"])


def _format_point(point):
    x, y, z = _point_as_floats(point)
    return f"({x!r}, {y!r}, {z!r})"


def format_beams_as_python(beams):
    """把钢材记录稳定格式化为可复制回脚本的 BEAMS Python 代码。"""
    lines = ["BEAMS = ["]
    for beam in sorted(beams, key=lambda record: record["name"]):
        record = _beam_record(
            beam["name"],
            beam["start"],
            beam["end"],
            beam["tube"],
            beam["role"],
        )
        lines.extend(
            [
                "    {",
                f'        "name": {json.dumps(record["name"])},',
                f'        "start": {_format_point(record["start"])},',
                f'        "end": {_format_point(record["end"])},',
                f'        "tube": {record["tube"]!r},',
                f'        "role": {json.dumps(record["role"])},',
                "    },",
            ]
        )
    lines.append("]")
    return "\n".join(lines) + "\n"


def add_beam_object(doc, beam):
    """按一条钢材记录创建可编辑、可导出的 FreeCAD 对象。"""
    generated = beam if "shape" in beam else make_beam(
        beam["name"],
        beam["start"],
        beam["end"],
        beam["tube"],
        beam["role"],
    )
    obj = doc.addObject("Part::Feature", generated["name"])
    obj.Shape = generated["shape"]
    _add_beam_properties(
        obj,
        _beam_record(
            generated["name"],
            generated["start"],
            generated["end"],
            generated["tube"],
            generated["role"],
        ),
    )
    if obj.ViewObject:
        obj.ViewObject.ShapeColor = (
            COLOR_OUTER if generated["role"] == "outer" else COLOR_INNER
        )
    return obj


def add_editable_beam(
    doc=None,
    name="custom_beam",
    start=(0.0, 0.0, 0.0),
    end=(1000.0, 0.0, 0.0),
    tube=80.0,
    role="inner",
):
    """在当前文档中新增一根可编辑、可导出的钢材。"""
    doc = App.ActiveDocument if doc is None else doc
    if doc is None:
        raise ValueError("no active FreeCAD document")
    obj = add_beam_object(doc, _beam_record(name, start, end, tube, role))
    doc.recompute()
    return obj


def rebuild_beams_from_properties(doc=None):
    """根据对象属性里的 Start/End/Tube 重建 Shape。

    在 FreeCAD GUI 中手动改 StartX/EndZ 等属性后，运行：

        import box_room_frame
        box_room_frame.rebuild_beams_from_properties()

    即可让实体几何跟随属性刷新。
    """
    doc = App.ActiveDocument if doc is None else doc
    if doc is None:
        raise ValueError("no active FreeCAD document")
    for obj in doc.Objects:
        if not all(hasattr(obj, name) for name in BEAM_PROPERTY_NAMES):
            continue
        record = _beam_record_from_object(obj)
        obj.Shape = make_beam(
            record["name"],
            record["start"],
            record["end"],
            record["tube"],
            record["role"],
        )["shape"]
    doc.recompute()


def export_current_document_to_python(doc=None, output_path="/tmp/box_room_frame_exported.py"):
    """从当前 FreeCAD 文档导出钢材清单 Python 代码。"""
    doc = App.ActiveDocument if doc is None else doc
    if doc is None:
        raise ValueError("no active FreeCAD document")
    records = beam_records_from_document(doc)
    if not records:
        raise ValueError("document does not contain editable beam objects")

    body = format_beams_as_python(records)
    content = (
        "# Generated from editable FreeCAD beam objects.\n"
        "# Copy BEAMS into box_room_frame.py or import this file and call\n"
        "# box_room_frame.create_document_from_beam_records(BEAMS).\n\n"
        + body
    )
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(content)
    return output_path


def build_frame(params):
    """根据参数生成整套车箱房龙骨骨架的梁柱数据。

    参数:
        params: 参数字典。主要字段包括 length、width、height、tube、
            x_brace_tube、rear_reinforcement_tube、entry_door_width、entry_door_height、
            entry_door_center_ratio、right_front_coffee_window_height、
            right_rear_window_width、right_rear_window_height、
            right_rear_window_bottom_z、right_rear_window_center_ratio、
            left_front_window_width、left_front_window_height、
            left_front_window_bottom_z、left_front_window_center_ratio、
            left_rear_toilet_window_width、left_rear_toilet_window_height、
            left_rear_toilet_window_bottom_z、left_rear_toilet_window_center_ratio、
            bay_count。

    返回:
        beams 列表。每个元素都是 make_beam 返回的字典，里面包含
        Part Shape 和角色信息。

    坐标约定:
        x 方向: 车箱长度方向，x=0 可理解为车头面，x=length 为车尾面。
        y 方向: 车箱宽度方向，y=0 和 y=width 为左右侧面。
        z 方向: 高度方向，z=0 为底部，z=height 为顶部。

    骨架组成:
        1. 长向顶/底外框梁；
        2. 车头/车尾端面顶/底横梁；
        3. 分仓立柱；
        4. 屋面和地面横向梁；
        5. 中腰梁，让侧面和端面呈“日”字形；
        6. 顶部和底部中心纵梁；
        7. 右侧中部日常进出门门框；
        8. 右侧车头到门框之间的咖啡售卖窗；
        9. 右侧后部床头上方窗框；
        10. 左侧车头部卡座茶几旁窗框；
        11. 左侧中部偏后厕所窗框；
        12. 车尾外挂摩托和空调外机加强框；
        13. 车头和车尾端面的 X 形抗扭撑。
    """
    length = float(params["length"])
    width = float(params["width"])
    height = float(params["height"])
    tube = float(params["tube"])
    x_brace_tube = float(params["x_brace_tube"])
    rear_reinforcement_tube = float(params["rear_reinforcement_tube"])
    entry_door_width = float(params["entry_door_width"])
    entry_door_height = float(params["entry_door_height"])
    entry_door_center_ratio = float(params["entry_door_center_ratio"])
    right_front_coffee_window_height = float(params["right_front_coffee_window_height"])
    right_rear_window_width = float(params["right_rear_window_width"])
    right_rear_window_height = float(params["right_rear_window_height"])
    right_rear_window_bottom_z = float(params["right_rear_window_bottom_z"])
    right_rear_window_center_ratio = float(params["right_rear_window_center_ratio"])
    left_front_window_width = float(params["left_front_window_width"])
    left_front_window_height = float(params["left_front_window_height"])
    left_front_window_bottom_z = float(params["left_front_window_bottom_z"])
    left_front_window_center_ratio = float(params["left_front_window_center_ratio"])
    left_rear_toilet_window_width = float(params["left_rear_toilet_window_width"])
    left_rear_toilet_window_height = float(params["left_rear_toilet_window_height"])
    left_rear_toilet_window_bottom_z = float(params["left_rear_toilet_window_bottom_z"])
    left_rear_toilet_window_center_ratio = float(params["left_rear_toilet_window_center_ratio"])
    rear_motorcycle_mass_kg = float(params["rear_motorcycle_mass_kg"])
    rear_rack_mass_kg = float(params["rear_rack_mass_kg"])
    rear_ac_unit_mass_kg = float(params["rear_ac_unit_mass_kg"])
    rear_carrier_dynamic_factor = float(params["rear_carrier_dynamic_factor"])
    bay_count = int(params["bay_count"])

    # 基础参数校验：尺寸不能为 0 或负数。
    if min(
        length,
        width,
        height,
        tube,
        x_brace_tube,
        rear_reinforcement_tube,
        entry_door_width,
        entry_door_height,
        right_front_coffee_window_height,
        right_rear_window_width,
        right_rear_window_height,
        right_rear_window_bottom_z,
        left_front_window_width,
        left_front_window_height,
        left_front_window_bottom_z,
        left_rear_toilet_window_width,
        left_rear_toilet_window_height,
        left_rear_toilet_window_bottom_z,
        rear_motorcycle_mass_kg,
        rear_rack_mass_kg,
        rear_ac_unit_mass_kg,
        rear_carrier_dynamic_factor,
    ) <= 0:
        raise ValueError(
            "length, width, height, tube, x_brace_tube, entry_door_width, "
            "rear_reinforcement_tube, entry_door_height, "
            "right_front_coffee_window_height, "
            "right_rear_window_width, right_rear_window_height, "
            "right_rear_window_bottom_z, left_front_window_width, "
            "left_front_window_height, left_front_window_bottom_z, "
            "left_rear_toilet_window_width, left_rear_toilet_window_height, "
            "left_rear_toilet_window_bottom_z, rear_motorcycle_mass_kg, "
            "rear_rack_mass_kg, rear_ac_unit_mass_kg, and "
            "rear_carrier_dynamic_factor must be positive"
        )

    # 分仓数量至少为 1，否则无法计算分仓位置。
    if bay_count < 1:
        raise ValueError("bay_count must be at least 1")

    # 管径过大时，实体会在宽度或高度方向严重自交，这里提前阻止。
    if tube >= min(width, height) / 2:
        raise ValueError("tube is too large for this frame size")
    if not 0.0 < entry_door_center_ratio < 1.0:
        raise ValueError("entry_door_center_ratio must be between 0 and 1")
    if not 0.0 < right_rear_window_center_ratio < 1.0:
        raise ValueError("right_rear_window_center_ratio must be between 0 and 1")
    if not 0.0 < left_front_window_center_ratio < 1.0:
        raise ValueError("left_front_window_center_ratio must be between 0 and 1")
    if not 0.0 < left_rear_toilet_window_center_ratio < 1.0:
        raise ValueError("left_rear_toilet_window_center_ratio must be between 0 and 1")
    if entry_door_width >= length:
        raise ValueError("entry_door_width must be smaller than length")
    if entry_door_height >= height:
        raise ValueError("entry_door_height must be smaller than height")
    if right_front_coffee_window_height >= height:
        raise ValueError("right_front_coffee_window_height must be smaller than height")
    if right_rear_window_width >= length:
        raise ValueError("right_rear_window_width must be smaller than length")
    if left_front_window_width >= length:
        raise ValueError("left_front_window_width must be smaller than length")
    if left_rear_toilet_window_width >= length:
        raise ValueError("left_rear_toilet_window_width must be smaller than length")
    if right_rear_window_bottom_z + right_rear_window_height >= height:
        raise ValueError("right rear window must stay below the roof")
    if left_front_window_bottom_z + left_front_window_height >= height:
        raise ValueError("left front window must stay below the roof")
    if left_rear_toilet_window_bottom_z + left_rear_toilet_window_height >= height:
        raise ValueError("left rear toilet window must stay below the roof")

    entry_door_center_x = length * entry_door_center_ratio
    entry_door_x0 = entry_door_center_x - entry_door_width / 2.0
    entry_door_x1 = entry_door_center_x + entry_door_width / 2.0
    if entry_door_x0 <= 0.0 or entry_door_x1 >= length:
        raise ValueError("entry door must stay inside the side wall")
    right_rear_window_center_x = length * right_rear_window_center_ratio
    right_rear_window_x0 = right_rear_window_center_x - right_rear_window_width / 2.0
    right_rear_window_x1 = right_rear_window_center_x + right_rear_window_width / 2.0
    right_rear_window_top_z = right_rear_window_bottom_z + right_rear_window_height
    if right_rear_window_x0 <= 0.0 or right_rear_window_x1 >= length:
        raise ValueError("right rear window must stay inside the side wall")
    if right_rear_window_x0 <= entry_door_x1:
        raise ValueError("right rear window must be behind the entry door")
    left_front_window_center_x = length * left_front_window_center_ratio
    left_front_window_x0 = left_front_window_center_x - left_front_window_width / 2.0
    left_front_window_x1 = left_front_window_center_x + left_front_window_width / 2.0
    left_front_window_top_z = left_front_window_bottom_z + left_front_window_height
    if left_front_window_x0 <= 0.0 or left_front_window_x1 >= length:
        raise ValueError("left front window must stay inside the side wall")
    if left_front_window_x1 >= entry_door_x0:
        raise ValueError("left front window must stay ahead of the entry door")
    left_rear_toilet_window_center_x = length * left_rear_toilet_window_center_ratio
    left_rear_toilet_window_x0 = (
        left_rear_toilet_window_center_x - left_rear_toilet_window_width / 2.0
    )
    left_rear_toilet_window_x1 = (
        left_rear_toilet_window_center_x + left_rear_toilet_window_width / 2.0
    )
    left_rear_toilet_window_top_z = (
        left_rear_toilet_window_bottom_z + left_rear_toilet_window_height
    )
    if left_rear_toilet_window_x0 <= 0.0 or left_rear_toilet_window_x1 >= length:
        raise ValueError("left rear toilet window must stay inside the side wall")
    if left_rear_toilet_window_x0 <= left_front_window_x1:
        raise ValueError("left rear toilet window must stay behind the front window")

    # xs 是长度方向每个分仓站位的位置。例如 6600mm、3 仓时：
    # [0, 2200, 4400, 6600]。
    xs = [round(length * i / bay_count, 6) for i in range(bay_count + 1)]
    y0, y1 = 0.0, width
    z0, z_mid, z1 = 0.0, height / 2.0, height

    beams = []
    seen = set()

    # 两侧墙的长向顶梁和底梁，共 4 根。
    # y=0/y=width 表示左右两侧，z=0/z=height 表示底部/顶部。
    for y in (y0, y1):
        for z in (z0, z1):
            add_beam(
                beams,
                seen,
                f"outer_long_rail_y{int(y)}_z{int(z)}",
                (0.0, y, z),
                (length, y, z),
                tube,
                "outer",
            )

    # 车头和车尾端面的宽向顶梁和底梁，共 4 根。
    # x=0 是车头面，x=length 是车尾面。
    for x in (0.0, length):
        for z in (z0, z1):
            add_beam(
                beams,
                seen,
                f"outer_end_rail_x{int(x)}_z{int(z)}",
                (x, y0, z),
                (x, y1, z),
                tube,
                "outer",
            )

    # 每个分仓站位上的侧立柱。
    # 两端 x=0/x=length 视为外框柱，中间站位视为内部分仓柱。
    for x in xs:
        for y in (y0, y1):
            # 右侧车头到门前框之间是咖啡售卖窗，洞口内不能保留竖向分仓柱。
            if y == y1 and 0.0 < x < entry_door_x0:
                continue
            add_beam(
                beams,
                seen,
                f"outer_post_x{int(x)}_y{int(y)}",
                (x, y, z0),
                (x, y, z1),
                tube,
                "outer" if x in (0.0, length) else "inner",
            )

    # 每个分仓站位上的屋面横梁和地面横梁。
    # 这些梁横跨宽度方向，用于把左右侧墙连成空间框架。
    for x in xs:
        for z in (z0, z1):
            add_beam(
                beams,
                seen,
                f"transverse_x{int(x)}_z{int(z)}",
                (x, y0, z),
                (x, y1, z),
                tube,
                "inner" if x not in (0.0, length) else "outer",
            )

    # 左侧面的中腰梁。外框 + 中腰梁 + 分仓立柱会形成连续“日”字格。
    add_beam(
        beams,
        seen,
        f"side_middle_rail_y{int(y0)}",
        (0.0, y0, z_mid),
        (length, y0, z_mid),
        tube,
        "inner",
    )

    # 左侧车头部上方为卡座茶几旁窗，窗底高于中腰梁，不切断原有中腰梁。
    add_side_window_frame(
        beams,
        seen,
        "left_front_window",
        left_front_window_x0,
        left_front_window_x1,
        y0,
        z_mid,
        left_front_window_bottom_z,
        left_front_window_top_z,
        z1,
        tube,
    )

    # 左侧中部偏后为厕所窗，窗框上下接入中腰梁和顶梁。
    add_side_window_frame(
        beams,
        seen,
        "left_rear_toilet_window",
        left_rear_toilet_window_x0,
        left_rear_toilet_window_x1,
        y0,
        z_mid,
        left_rear_toilet_window_bottom_z,
        left_rear_toilet_window_top_z,
        z1,
        tube,
    )

    # 右侧车头到门框之间是咖啡售卖窗，窗底就是地板。
    # 因此门前中腰梁不能穿过售卖窗口，只保留门后的中腰梁。
    add_beam(
        beams,
        seen,
        "right_front_coffee_window_header",
        (0.0, y1, right_front_coffee_window_height),
        (entry_door_x0, y1, right_front_coffee_window_height),
        tube,
        "inner",
    )
    add_optional_beam(
        beams,
        seen,
        f"side_middle_rail_y{int(y1)}_rear_of_door",
        (entry_door_x1, y1, z_mid),
        (length, y1, z_mid),
        tube,
        "inner",
    )

    # 人面向车头、向车尾看时，右手侧为 y=width。门位于该侧中部。
    for name, start, end in (
        (
            "right_entry_door_front_jamb",
            (entry_door_x0, y1, z0),
            (entry_door_x0, y1, entry_door_height),
        ),
        (
            "right_entry_door_rear_jamb",
            (entry_door_x1, y1, z0),
            (entry_door_x1, y1, entry_door_height),
        ),
        (
            "right_entry_door_header",
            (entry_door_x0, y1, entry_door_height),
            (entry_door_x1, y1, entry_door_height),
        ),
        (
            "right_entry_door_front_upper_connector",
            (entry_door_x0, y1, entry_door_height),
            (entry_door_x0, y1, z1),
        ),
        (
            "right_entry_door_rear_upper_connector",
            (entry_door_x1, y1, entry_door_height),
            (entry_door_x1, y1, z1),
        ),
    ):
        add_beam(
            beams,
            seen,
            name,
            start,
            end,
            tube,
            "inner",
        )

    # 右侧后部上方为床头窗，窗框上下接入中腰梁和顶梁。
    add_side_window_frame(
        beams,
        seen,
        "right_rear_window",
        right_rear_window_x0,
        right_rear_window_x1,
        y1,
        z_mid,
        right_rear_window_bottom_z,
        right_rear_window_top_z,
        z1,
        tube,
    )

    # 车尾将外挂摩托、挂架和空调外机，因此在尾端内侧增设独立挂载加强框。
    rear_reinforcement_x = length - tube
    rear_mount_y0 = width * 0.25
    rear_mount_y1 = width * 0.75
    rear_lower_mount_z = height * 0.25
    rear_upper_mount_z = height * 0.70
    for name, start, end in (
        (
            "rear_carrier_left_vertical_reinforcement",
            (rear_reinforcement_x, rear_mount_y0, z0),
            (rear_reinforcement_x, rear_mount_y0, z1),
        ),
        (
            "rear_carrier_right_vertical_reinforcement",
            (rear_reinforcement_x, rear_mount_y1, z0),
            (rear_reinforcement_x, rear_mount_y1, z1),
        ),
        (
            "rear_carrier_lower_mount_crossmember",
            (rear_reinforcement_x, rear_mount_y0, rear_lower_mount_z),
            (rear_reinforcement_x, rear_mount_y1, rear_lower_mount_z),
        ),
        (
            "rear_carrier_upper_mount_crossmember",
            (rear_reinforcement_x, rear_mount_y0, rear_upper_mount_z),
            (rear_reinforcement_x, rear_mount_y1, rear_upper_mount_z),
        ),
        (
            "rear_carrier_left_lower_diagonal",
            (rear_reinforcement_x, rear_mount_y0, rear_lower_mount_z),
            (length, y0, z0),
        ),
        (
            "rear_carrier_right_lower_diagonal",
            (rear_reinforcement_x, rear_mount_y1, rear_lower_mount_z),
            (length, y1, z0),
        ),
        (
            "rear_carrier_left_upper_diagonal",
            (rear_reinforcement_x, rear_mount_y0, rear_upper_mount_z),
            (length, y0, z1),
        ),
        (
            "rear_carrier_right_upper_diagonal",
            (rear_reinforcement_x, rear_mount_y1, rear_upper_mount_z),
            (length, y1, z1),
        ),
    ):
        add_beam(
            beams,
            seen,
            name,
            start,
            end,
            rear_reinforcement_tube,
            "inner",
        )

    # 车头和车尾端面的中腰梁，让端面也呈“日”字形。
    for x in (0.0, length):
        add_beam(
            beams,
            seen,
            f"end_middle_rail_x{int(x)}",
            (x, y0, z_mid),
            (x, y1, z_mid),
            tube,
            "inner",
        )

    # 顶面和底面的中心纵梁。
    # 它位于宽度中心 y=width/2，从车头贯通到车尾，提高顶/底面的整体性。
    for z in (z0, z1):
        add_beam(
            beams,
            seen,
            f"center_long_rail_z{int(z)}",
            (0.0, width / 2.0, z),
            (length, width / 2.0, z),
            tube,
            "inner",
        )

    # 底面加密加强：增加两道次纵梁和三道次横梁，把底部荷载更直接地分散到
    # 侧墙立柱、端面框架和中部分仓站位上。
    bottom_secondary_long_rail_y0 = width * 0.25
    bottom_secondary_long_rail_y1 = width * 0.75
    for y in (bottom_secondary_long_rail_y0, bottom_secondary_long_rail_y1):
        add_beam(
            beams,
            seen,
            f"bottom_secondary_long_rail_y{int(round(y))}_z0",
            (0.0, y, z0),
            (length, y, z0),
            tube,
            "inner",
        )
    for x in (length / 6.0, length / 2.0, length * 5.0 / 6.0):
        add_beam(
            beams,
            seen,
            f"bottom_secondary_transverse_x{int(round(x))}_z0",
            (x, y0, z0),
            (x, y1, z0),
            tube,
            "inner",
        )

    # 车头和车尾端面的 X 形抗扭撑。
    # 每个端面两根对角撑：左下到右上、左上到右下。
    for x in (0.0, length):
        add_beam(
            beams,
            seen,
            f"x_brace_a_x{int(x)}",
            (x, y0, z0),
            (x, y1, z1),
            x_brace_tube,
            "inner",
        )
        add_beam(
            beams,
            seen,
            f"x_brace_b_x{int(x)}",
            (x, y0, z1),
            (x, y1, z0),
            x_brace_tube,
            "inner",
        )

    return beams


def create_document(params):
    """创建 FreeCAD 文档，生成骨架对象，并保存为 FCStd 文件。

    参数:
        params: 参数字典。除几何参数外，还包含 doc_name、output_path、
            make_single_compound。

    返回:
        (doc, beams)
        doc 是 FreeCAD 文档对象；
        beams 是 build_frame 生成的梁柱数据列表。

    工作流程:
        1. 如果指定文档已存在，则复用并清空；否则新建文档。
        2. 调用 build_frame 生成所有梁柱 Shape。
        3. 根据 make_single_compound 决定合并成一个对象，还是逐根创建对象。
        4. 创建一个 parameters 对象保存关键参数，方便打开模型后查看。
        5. recompute 后保存到 params["output_path"]。

    无界面兼容:
        FreeCADCmd 或 FreeCAD 自带 python 在无界面运行时，obj.ViewObject
        可能为 None。因此设置颜色前都会判断 ViewObject 是否存在。
    """
    if params["doc_name"] in App.listDocuments():
        doc = App.getDocument(params["doc_name"])
    else:
        doc = App.newDocument(params["doc_name"])
    clear_doc(doc)

    beams = build_frame(params)

    if params.get("make_single_compound", True):
        # 合并为一个 compound 后，模型树只有一个主体对象，适合交付和查看。
        compound = Part.makeCompound([beam["shape"] for beam in beams])
        obj = doc.addObject("Part::Feature", "box_room_steel_frame")
        obj.Shape = compound
        obj.Label = "6.6m x 2.45m x 2.45m 日字形钢车箱房龙骨骨架"
        if obj.ViewObject:
            obj.ViewObject.ShapeColor = COLOR_OUTER
    else:
        # 逐根输出对象，适合检查每根梁柱的位置和命名。
        for beam in beams:
            add_beam_object(doc, beam)

    # 用一个 App::FeaturePython 对象记录主要参数。
    # 它不参与几何，只作为模型内的参数说明。
    notes = doc.addObject("App::FeaturePython", "parameters")
    notes.addProperty("App::PropertyString", "OverallSize").OverallSize = (
        f'{params["length"]} x {params["width"]} x {params["height"]} mm'
    )
    notes.addProperty("App::PropertyFloat", "TubeSize").TubeSize = float(params["tube"])
    notes.addProperty("App::PropertyFloat", "XBraceTubeSize").XBraceTubeSize = float(
        params["x_brace_tube"]
    )
    notes.addProperty("App::PropertyFloat", "RearReinforcementTubeSize").RearReinforcementTubeSize = float(
        params["rear_reinforcement_tube"]
    )
    notes.addProperty("App::PropertyFloat", "EntryDoorWidth").EntryDoorWidth = float(
        params["entry_door_width"]
    )
    notes.addProperty("App::PropertyFloat", "EntryDoorHeight").EntryDoorHeight = float(
        params["entry_door_height"]
    )
    notes.addProperty("App::PropertyFloat", "RightFrontCoffeeWindowHeight").RightFrontCoffeeWindowHeight = float(
        params["right_front_coffee_window_height"]
    )
    notes.addProperty("App::PropertyFloat", "RightRearWindowWidth").RightRearWindowWidth = float(
        params["right_rear_window_width"]
    )
    notes.addProperty("App::PropertyFloat", "RightRearWindowHeight").RightRearWindowHeight = float(
        params["right_rear_window_height"]
    )
    notes.addProperty("App::PropertyFloat", "LeftFrontWindowWidth").LeftFrontWindowWidth = float(
        params["left_front_window_width"]
    )
    notes.addProperty("App::PropertyFloat", "LeftFrontWindowHeight").LeftFrontWindowHeight = float(
        params["left_front_window_height"]
    )
    notes.addProperty("App::PropertyFloat", "LeftRearToiletWindowWidth").LeftRearToiletWindowWidth = float(
        params["left_rear_toilet_window_width"]
    )
    notes.addProperty("App::PropertyFloat", "LeftRearToiletWindowHeight").LeftRearToiletWindowHeight = float(
        params["left_rear_toilet_window_height"]
    )
    notes.addProperty("App::PropertyFloat", "RearMotorcycleMassKg").RearMotorcycleMassKg = float(
        params["rear_motorcycle_mass_kg"]
    )
    notes.addProperty("App::PropertyFloat", "RearRackMassKg").RearRackMassKg = float(
        params["rear_rack_mass_kg"]
    )
    notes.addProperty("App::PropertyFloat", "RearAcUnitMassKg").RearAcUnitMassKg = float(
        params["rear_ac_unit_mass_kg"]
    )
    notes.addProperty("App::PropertyFloat", "RearCarrierDynamicFactor").RearCarrierDynamicFactor = float(
        params["rear_carrier_dynamic_factor"]
    )
    notes.addProperty("App::PropertyInteger", "BayCount").BayCount = int(
        params["bay_count"]
    )

    doc.recompute()
    doc.saveAs(params["output_path"])
    return doc, beams


def create_document_from_beam_records(
    beams,
    params=None,
    output_path="/tmp/a.FCStd",
    doc_name="BoxRoomFrameCustom",
):
    """根据 BEAMS 钢材清单生成 FreeCAD 文档。

    用法:
        import box_room_frame
        from box_room_frame_exported import BEAMS
        box_room_frame.create_document_from_beam_records(BEAMS)
    """
    p = dict(PARAMS if params is None else params)
    p["doc_name"] = doc_name
    p["output_path"] = output_path
    p["make_single_compound"] = False

    if p["doc_name"] in App.listDocuments():
        doc = App.getDocument(p["doc_name"])
    else:
        doc = App.newDocument(p["doc_name"])
    clear_doc(doc)

    normalized = [
        _beam_record(
            beam["name"],
            beam["start"],
            beam["end"],
            beam["tube"],
            beam["role"],
        )
        for beam in beams
    ]
    for beam in normalized:
        add_beam_object(doc, beam)

    notes = doc.addObject("App::FeaturePython", "parameters")
    notes.addProperty("App::PropertyString", "Source").Source = "BEAMS"
    notes.addProperty("App::PropertyInteger", "BeamCount").BeamCount = len(normalized)

    doc.recompute()
    doc.saveAs(p["output_path"])
    return doc, normalized


def create_fem_analysis(doc=None, params=None):
    """为当前车箱房骨架创建静态有限元分析设置。

    这个函数创建材料、固定约束、垂向载荷、Gmsh 网格对象和 CalculiX 求解器。
    它负责把分析对象写入 FreeCAD 文档；实际网格划分和求解需要本机安装并配置
    Gmsh/CalculiX 后在 FreeCAD FEM 工作台中执行。
    """
    doc = App.ActiveDocument if doc is None else doc
    if doc is None:
        raise ValueError("no active FreeCAD document")
    p = dict(PARAMS if params is None else params)

    import ObjectsFem

    beam_objects = [
        obj for obj in doc.Objects if all(hasattr(obj, name) for name in BEAM_PROPERTY_NAMES)
    ]
    if not beam_objects:
        raise ValueError("document does not contain editable beam objects")

    analysis = ObjectsFem.makeAnalysis(doc, "frame_static_analysis")
    compound = Part.makeCompound([obj.Shape for obj in beam_objects])
    frame = doc.addObject("Part::Feature", "fem_frame_compound")
    frame.Shape = compound

    material = ObjectsFem.makeMaterialSolid(doc, "frame_steel_material")
    material_record = material.Material
    material_record["Name"] = "Q235 structural steel"
    material_record["Density"] = "7850 kg/m^3"
    material_record["YoungsModulus"] = "200000 MPa"
    material_record["PoissonRatio"] = "0.30"
    material.Material = material_record
    analysis.addObject(material)

    fixed = ObjectsFem.makeConstraintFixed(doc, "front_bottom_fixed_constraint")
    fixed.References = [(frame, "Face1")]
    analysis.addObject(fixed)

    rear_carrier_mass = (
        float(p["rear_motorcycle_mass_kg"])
        + float(p["rear_rack_mass_kg"])
        + float(p["rear_ac_unit_mass_kg"])
    )
    rear_carrier_force_n = rear_carrier_mass * 9.81 * float(p["rear_carrier_dynamic_factor"])

    load = ObjectsFem.makeConstraintForce(doc, "rear_roof_downforce")
    load.References = [(frame, "Face2")]
    load.Force = f"{rear_carrier_force_n:.3f} N"
    load.Direction = (frame, ["Face2"])
    load.Reversed = True
    analysis.addObject(load)

    mesh = analysis.addObject(ObjectsFem.makeMeshGmsh(doc, "frame_gmsh_mesh"))[0]
    mesh.Shape = frame
    mesh.CharacteristicLengthMax = f'{max(float(p["tube"]), 80.0)} mm'
    mesh.CharacteristicLengthMin = f'{max(float(p["tube"]) / 4.0, 20.0)} mm'

    solver = ObjectsFem.makeSolverCalculiXCcxTools(doc, "frame_calculix_solver")
    solver.AnalysisType = "static"
    solver.GeometricalNonlinearity = False
    solver.ThermoMechSteadyState = False
    solver.MatrixSolverType = "default"
    solver.IterationsControlParameterTimeUse = False
    solver.SplitInputWriter = False
    analysis.addObject(solver)

    doc.recompute()
    return analysis


def export_stl_1_30(params=None, output_path="/tmp/a_1_30.stl"):
    """导出 1:30 比例的 STL 文件，供 3D 打印模型使用。

    参数:
        params: 可选参数字典。为 None 时使用全局 PARAMS。
        output_path: STL 输出路径，默认 /tmp/a_1_30.stl。

    返回:
        实际写出的 STL 文件路径。

    缩放逻辑:
        原始模型单位是毫米，真实尺寸为 6600 x 2450 x 2450 mm。
        1:30 缩放后，模型约为:
            220.0 x 81.67 x 81.67 mm
        这个尺寸更适合常见桌面 3D 打印机打印展示模型。

    重要说明:
        这个函数不会修改主参数，也不会改变主脚本直接执行时只输出
        /tmp/a.FCStd 的行为。需要 STL 时显式调用本函数即可。
    """
    # 复制参数，避免调用者传入 PARAMS 时被函数内部意外修改。
    p = dict(PARAMS if params is None else params)
    # 先生成原始比例文档和梁柱数据，保证 STL 与 FCStd 使用同一套建模逻辑。
    doc, beams = create_document(p)
    compound = Part.makeCompound([beam["shape"] for beam in beams])

    # 构造缩放矩阵。A11/A22/A33 分别是 X/Y/Z 三个方向的缩放比例。
    matrix = App.Matrix()
    matrix.A11 = 1.0 / 30.0
    matrix.A22 = 1.0 / 30.0
    matrix.A33 = 1.0 / 30.0
    scaled_shape = compound.transformGeometry(matrix)

    # 把缩放后的 Shape 放入文档对象，再交给 Mesh.export 输出 STL。
    obj = doc.addObject("Part::Feature", "box_room_steel_frame_1_30")
    obj.Shape = scaled_shape
    doc.recompute()

    # Mesh 是 FreeCAD 的网格导出模块。放在函数内部导入，可以让普通 FCStd
    # 生成流程不必提前加载 STL 导出模块。
    import Mesh

    Mesh.export([obj], output_path)
    return output_path


if __name__ == "__main__":
    # 直接运行本脚本时，只生成 FreeCAD 原生模型 /tmp/a.FCStd。
    # STL 需要通过 export_stl_1_30() 显式导出。
    document, frame_beams = create_document(PARAMS)
    print(f'FCStd exported: {PARAMS["output_path"]}')
    print(
        "Overall size: "
        f'{PARAMS["length"]} x {PARAMS["width"]} x {PARAMS["height"]} mm'
    )
    print(f'Tube size: {PARAMS["tube"]} mm')
    print(f'X brace tube size: {PARAMS["x_brace_tube"]} mm')
    print(f'Bay count: {PARAMS["bay_count"]}')
    print(f"Beam count: {len(frame_beams)}")
    print(f"freecad /tmp/a.FCStd")
