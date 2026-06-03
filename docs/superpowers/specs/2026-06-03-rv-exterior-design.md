# RV Exterior Assembly Design

## Goal

Create a separate FreeCAD exterior model, `RV_Exterior.FCStd`, whose final appearance is close to the currently opened `mj.FCStd` project style: a visible exterior assembly made from many named parts such as cabin, lamps, grill, bumper, wheels, body panels, roof equipment, and accessories.

The model should not reuse geometry from `mj.FCStd`. The mj project is used only as a reference for visual organization and exterior part vocabulary.

The target vehicle should read at first glance as a 6.8 meter cab-over box truck converted into an RV:

- Single front axle and single rear axle
- Cab-over truck cabin at the front
- Rectangular living box behind the cabin
- Truck-like proportions and stance
- RV equipment added as exterior details, not as a luxury integrated motorhome silhouette

## File Boundary

Keep `RV.FCStd` as the logical assembly and BOM skeleton. It contains the current business hierarchy such as Chassis, CargoBox, Electrical, WaterSystem, HVAC, and other systems. Its placeholder boxes are not the primary exterior model.

Create `RV_Exterior.FCStd` as a separate exterior assembly file. This file focuses on visible outside geometry and should be independently openable and inspectable in FreeCAD.

Do not create `RV_Master.FCStd` in the first implementation. A future master file can use `App::Link` to reference both `RV.FCStd` and `RV_Exterior.FCStd`, but cross-file linking is intentionally out of scope for the first exterior pass.

## Coordinate System

Use FreeCAD millimeters.

Coordinate conventions:

- X: vehicle length direction, positive toward the rear
- Y: vehicle width direction, positive toward the left side
- Z: vertical direction, positive upward
- Origin: front axle centerline projected onto the ground plane

This origin makes future linking to a master assembly predictable.

Primary X ranges:

| Region | X range | Notes |
| --- | ---: | --- |
| Front overhang | -1100 to 0 | Cab nose and front bumper sit ahead of the front axle. |
| Cab | -1100 to 600 | Cab-over cabin, including stepped nose and rear wall. |
| Cab-to-box gap | 600 to 900 | Clearance gap between cab rear and living box front. |
| Living box | 900 to 5500 | Rear RV box body. |
| Rear overhang | 3800 to 5700 | Includes the portion of the living box behind the rear axle and rear exterior accessories. |

The overall model spans approximately X = -1100 to X = 5700, which is 6800 mm total. The living box reaches X = 5500, leaving space at the rear for ladder, lamp blocks, bumper detail, and spare tire carrier.

## Vehicle Dimensions

Use these first-pass approximate dimensions:

| Parameter | Value |
| --- | ---: |
| Overall length | 6800 |
| Overall width | 2300 |
| Overall height | 3100 |
| Cab length | 1700 |
| Cab X min | -1100 |
| Cab X max | 600 |
| Front overhang | 1100 |
| Cab-to-box gap | 300 |
| Cab width | 2200 |
| Cab height | 2050 |
| Living box length | 4600 |
| Living box X min | 900 |
| Living box X max | 5500 |
| Living box width | 2300 |
| Living box height | 2200 |
| Living box floor Z | 850 |
| Panel thickness | 45 |
| Wheelbase | 3800 |
| Rear overhang | 1900 |
| Tire diameter | 780 |
| Tire width | 240 |
| Front track width | 1850 |
| Rear track width | 1850 |
| Rear wheel configuration | single tire per side |
| Frame rail height | 160 |
| Frame rail width | 80 |
| Frame rail length | 6100 |
| Frame rail X min | -700 |
| Frame rail X max | 5400 |
| Frame rail Z min | 560 |
| Frame rail Z max | 720 |

The visual priority is recognition as a 6.8 meter single-rear-axle truck. RV details are added on top of that truck silhouette.

Wheel center positions:

| Wheel | X | Y | Z |
| --- | ---: | ---: | ---: |
| Front left | 0 | 925 | 390 |
| Front right | 0 | -925 | 390 |
| Rear left | 3800 | 925 | 390 |
| Rear right | 3800 | -925 | 390 |

The truck is single-rear-axle and single-tire-per-side in the first pass. Do not model rear dual tires unless the vehicle direction changes later.

Frame crossmember positions:

| Crossmember | X |
| --- | ---: |
| Front | -500 |
| Mid | 1900 |
| Rear | 5200 |

## Assembly Structure

`RV_Exterior.FCStd` should contain one root `App::Part`:

```text
RV_Exterior_Asm
```

Top-level exterior groups:

```text
RV_Exterior_Asm
├── Cab_Asm
├── Front_Fascia_Asm
├── Chassis_Exterior_Asm
├── Wheels_Asm
├── Living_Box_Asm
├── Openings_Asm
├── Roof_Equipment_Asm
└── Exterior_Accessories_Asm
```

### Cab_Asm

Visible cab-over truck cabin parts:

- `Cab_Floor`
- `Cab_Nose_Lower`
- `Cab_Front_Panel`
- `Cab_Rear_Wall`
- `Cab_Side_Wall_L`
- `Cab_Side_Wall_R`
- `Cab_Roof`
- `Cab_Roof_Fairing`
- `Windshield`
- `Side_Window_L`
- `Side_Window_R`
- `Cab_Door_L`
- `Cab_Door_R`
- `Door_Handle_L`
- `Door_Handle_R`
- `Side_Mirror_L`
- `Side_Mirror_R`

Cab shape is the hardest visual area. Do not make it a single rectangular block. Approximate the cab with multiple primitives:

| Part | Approximate geometry |
| --- | --- |
| `Cab_Floor` | Box from X = -1050 to 550, Y = +/-1050, Z = 700 to 780. |
| `Cab_Nose_Lower` | Short box at X = -1100 to -650, Y = +/-950, Z = 720 to 1250, below windshield. |
| `Cab_Front_Panel` | Vertical or slightly inset front panel at X = -1050 to -850. |
| `Cab_Rear_Wall` | Thin panel at X = 550 to 600. |
| `Cab_Side_Wall_L/R` | Side panels with glass overlays and door outlines. |
| `Cab_Roof` | Main roof box with slight front overhang. |
| `Cab_Roof_Fairing` | Smaller raised/stepped box at the front roof edge to avoid a plain cube silhouette. |
| `Windshield` | Translucent panel on the upper front face, tilted only if practical; a flat inset panel is acceptable first. |

Design note from `mj.FCStd`: the mj reference exposes cabin identity through separately named cabin, handles, lights, grill, bumper, and wheel compounds rather than through one monolithic shell. This design follows that separation with simple primitives.

### Front_Fascia_Asm

Truck front identity parts:

- `Front_Grill`
- `Front_Bumper`
- `Head_Lamp_L`
- `Head_Lamp_R`
- `Turn_Signal_L`
- `Turn_Signal_R`
- `Tow_Hook_L`
- `Tow_Hook_R`

### Chassis_Exterior_Asm

Visible chassis and running gear:

- `Frame_Rail_L`
- `Frame_Rail_R`
- `Crossmember_Front`
- `Crossmember_Mid`
- `Crossmember_Rear`
- `Front_Axle`
- `Rear_Axle`
- `Mudguard_Front_L`
- `Mudguard_Front_R`
- `Mudguard_Rear_L`
- `Mudguard_Rear_R`
- `Side_Step_L`
- `Side_Step_R`

### Wheels_Asm

Single front axle and single rear axle:

- `Front_Wheel_L`
- `Front_Wheel_R`
- `Rear_Wheel_L`
- `Rear_Wheel_R`

Each wheel should include a tire cylinder and a hub detail where practical.

Use each named wheel as an `App::Part` container. For example:

```text
Front_Wheel_L
├── Front_Wheel_L_Tire
├── Front_Wheel_L_Rim
└── Front_Wheel_L_Hub
```

Validation should count the four `App::Part` wheel containers as the four wheels, not the tire/rim/hub primitives inside them.

### Living_Box_Asm

The rear box should be made of panel-like parts, not one solid cube:

- `Floor_Panel`
- `Left_Wall`
- `Right_Wall`
- `Front_Wall`
- `Rear_Wall`
- `Roof_Panel`
- `Corner_Trim_FL`
- `Corner_Trim_FR`
- `Corner_Trim_RL`
- `Corner_Trim_RR`
- `Side_Skirt_L`
- `Side_Skirt_R`

### Openings_Asm

Doors, windows, vents, and service access:

- `Entry_Door`
- `Pass_Through_Frame`
- `Side_Window_1`
- `Side_Window_2`
- `Rear_Window`
- `Service_Hatch_1`
- `Service_Hatch_2`
- `Vent_Grille`

Openings are additive overlays in the first pass, not boolean cuts. Windows are thin translucent panels placed flush on wall faces. Doors, service hatches, vents, and `Pass_Through_Frame` are shallow framed rectangles placed on top of the relevant wall panel.

The wall panel remains solid behind these overlays. This is acceptable for first-pass exterior readability and avoids boolean fragility. A later manufacturing/detail pass may replace overlays with actual cutouts.

`Pass_Through_Frame` represents the framed outline where the cab would connect to the living box. It is a visible rectangular frame on the front wall of the living box, not an actual cut through both files.

### Roof_Equipment_Asm

RV-specific roof equipment:

- `Roof_AC`
- `Solar_Panel_1`
- `Solar_Panel_2`
- `Vent_Fan_1`
- `Vent_Fan_2`
- `Antenna`
- `Roof_Rack_L`
- `Roof_Rack_R`

### Exterior_Accessories_Asm

Additional exterior details:

- `Awning`
- `Ladder`
- `Spare_Tire_Carrier`
- `Storage_Box`
- `Marker_Light_Front_L`
- `Marker_Light_Front_R`
- `Marker_Light_Rear_L`
- `Marker_Light_Rear_R`
- `Rear_Lamp_L`
- `Rear_Lamp_R`

Accessory placement notes:

- `Awning`: elongated box or half-cylinder mounted along the upper edge of the living box right wall, approximately X = 1500 to 4300, Y near -1170, Z = 2700 to 2850.
- `Ladder`: rear wall accessory near the right rear corner, approximately X = 5520 to 5650, Y near -850, Z = 950 to 2850.
- `Spare_Tire_Carrier`: rear wall or rear bumper mounted, centered low on the rear face.
- `Storage_Box`: side-mounted or rear-mounted rectangular exterior box below the living box floor line.

## Geometry Strategy

Use simple FreeCAD primitives and boolean-safe geometry for the first pass:

- Use `Part::Box` for flat panels, steps, rails, bumpers, lamps, solar panels, and equipment blocks.
- Use `Part::Cylinder` for tires, hubs, axles, ladder rails, and round details.
- Use thin translucent boxes for glass.
- Use separate narrow boxes for grill slats and trim.
- Use color and transparency to convey material and part identity.

Do not use complex surfacing in the first implementation. The target is a clean, named, medium-detail exterior assembly, not a manufacturing-grade body shell.

## Color And Material Table

Use these first-pass view colors:

| Category | RGB | Alpha | Notes |
| --- | --- | ---: | --- |
| Body panels | `(0.82, 0.85, 0.86)` | `1.0` | Light neutral gray for cab and living box panels. |
| Trim and corner strips | `(0.18, 0.20, 0.22)` | `1.0` | Dark gray. |
| Chassis and frame | `(0.08, 0.09, 0.10)` | `1.0` | Near black. |
| Tires | `(0.02, 0.02, 0.02)` | `1.0` | Black rubber. |
| Rims and hubs | `(0.55, 0.58, 0.60)` | `1.0` | Metallic gray. |
| Glass | `(0.45, 0.75, 0.88)` | `0.35` | Translucent blue. |
| Head lamps | `(1.00, 0.92, 0.55)` | `1.0` | Warm pale yellow. |
| Turn signals | `(1.00, 0.55, 0.10)` | `1.0` | Amber. |
| Rear lamps | `(0.85, 0.05, 0.05)` | `1.0` | Red. |
| Solar panels | `(0.05, 0.10, 0.16)` | `1.0` | Dark blue-black. |
| Roof AC and vents | `(0.88, 0.90, 0.90)` | `1.0` | Light equipment gray. |
| Awning fabric | `(0.22, 0.28, 0.32)` | `1.0` | Dark neutral. |

Set transparency only where FreeCAD's view object supports it; transparency failures are non-critical.

## Visual Style

The model should resemble mj in organization rather than by copied geometry:

- Many named visible exterior objects
- Semantically grouped parts
- Independent lamps, grill, bumper, wheels, and accessories
- Separate panels instead of one large anonymous body
- Object labels that describe vehicle parts clearly

The model should not look like the current `docs/plan/1.md` output, where placeholder boxes are spread on an abstract grid.

## Build Flow

1. Create or replace a FreeCAD document named `RV_Exterior`.
   - Use `App.getDocument("RV_Exterior")` and a document-specific guard.
   - Never operate on `App.ActiveDocument` unless it has been verified to be `RV_Exterior`.
   - Do not modify the currently open `RV` document.
2. Create the root `RV_Exterior_Asm`.
3. Create the top-level `App::Part` groups listed above.
4. Add the main truck proportions:
   - frame rails
   - front axle
   - rear axle
   - four wheels
   - cab floor, lower nose, side walls, rear wall, roof, and roof fairing
   - living box panels
5. Add mj-style exterior parts:
   - front grill
   - bumper
   - lights
   - mirrors
   - doors
   - windows
   - roof equipment
   - ladder
   - awning
   - storage box
6. Apply colors and transparency.
7. Recompute the document.
8. Save as `RV_Exterior.FCStd` in the project root.

## Validation

The implementation should verify:

- `RV_Exterior.FCStd` exists and can be opened independently.
- The root object `RV_Exterior_Asm` exists.
- The eight top-level exterior assemblies exist.
- `Wheels_Asm` contains exactly four wheels.
- `Living_Box_Asm` contains floor, roof, left wall, right wall, front wall, and rear wall.
- `Front_Fascia_Asm` contains grill, bumper, and both head lamps.
- `Cab_Asm` contains at least 14 named parts, including cab floor, lower nose, front panel, rear wall, side walls, roof, windshield, side windows, doors, handles, and mirrors.
- `Roof_Equipment_Asm` contains at least 8 named parts.
- `Exterior_Accessories_Asm` contains at least 10 named parts.
- Wheel centers match the specified X/Y/Z positions within a small tolerance.
- Living box panel thickness uses the `Panel thickness` parameter.
- Object count is greater than 40 and less than 120.
- Isometric, front, right, and top views show coherent 6.8 meter single-rear-axle truck proportions.
- The model does not display the old abstract placement grid.

## Error Handling

The generation script should:

- Refuse to silently append duplicate geometry to an existing non-empty `RV_Exterior` document.
- Either create a fresh document or explicitly clear only the `RV_Exterior` document.
- Use explicit document lookup with `App.getDocument("RV_Exterior")`.
- Check that `App.getDocument("RV")` is not used as the build target.
- Keep all dimensions in a parameter section.
- Give useful errors naming the assembly or object that failed to create.
- Treat view color or transparency failures as non-fatal.
- Recompute before saving.

## Out Of Scope

The first implementation will not:

- Copy geometry from `/home/an/a/mj.FCStd`
- Build high-detail curved body surfaces
- Replace the existing logical `RV.FCStd`
- Create `RV_Master.FCStd`
- Add Assembly4 constraints
- Create cross-file `App::Link` references
- Model detailed interior systems
- Convert every existing business body into an exterior part

## Open Decisions

The approved decisions for this design are:

- Target level: mj-style exterior assembly
- Geometry source: rebuild from scratch, do not reuse mj geometry
- Vehicle form: cab-over truck RV
- Vehicle scale: 6.8 meter single-rear-axle truck
- File architecture: separate `RV_Exterior.FCStd`; keep `RV.FCStd` as logical/BOM skeleton
