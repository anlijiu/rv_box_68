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

## Vehicle Dimensions

Use these first-pass approximate dimensions:

| Parameter | Value |
| --- | ---: |
| Overall length | 6800 |
| Overall width | 2300 |
| Overall height | 3100 |
| Cab length | 1700 |
| Cab width | 2200 |
| Cab height | 2050 |
| Living box length | 4600 |
| Living box width | 2300 |
| Living box height | 2200 |
| Living box floor Z | 850 |
| Wheelbase | 3800 |
| Rear overhang | 1600 |
| Tire diameter | 780 |
| Tire width | 240 |
| Frame rail height | 160 |
| Frame rail width | 80 |

The visual priority is recognition as a 6.8 meter single-rear-axle truck. RV details are added on top of that truck silhouette.

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

- `Cab_Shell`
- `Windshield`
- `Side_Window_L`
- `Side_Window_R`
- `Cab_Door_L`
- `Cab_Door_R`
- `Door_Handle_L`
- `Door_Handle_R`
- `Side_Mirror_L`
- `Side_Mirror_R`

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
- `Cab_Pass_Through_Hint`
- `Side_Window_1`
- `Side_Window_2`
- `Rear_Window`
- `Service_Hatch_1`
- `Service_Hatch_2`
- `Vent_Grille`

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

## Geometry Strategy

Use simple FreeCAD primitives and boolean-safe geometry for the first pass:

- Use `Part::Box` for flat panels, steps, rails, bumpers, lamps, solar panels, and equipment blocks.
- Use `Part::Cylinder` for tires, hubs, axles, ladder rails, and round details.
- Use thin translucent boxes for glass.
- Use separate narrow boxes for grill slats and trim.
- Use color and transparency to convey material and part identity.

Do not use complex surfacing in the first implementation. The target is a clean, named, medium-detail exterior assembly, not a manufacturing-grade body shell.

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
2. Create the root `RV_Exterior_Asm`.
3. Create the top-level `App::Part` groups listed above.
4. Add the main truck proportions:
   - frame rails
   - front axle
   - rear axle
   - four wheels
   - cab shell
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
- Object count is greater than 40 and less than 120.
- Isometric, front, right, and top views show coherent 6.8 meter single-rear-axle truck proportions.
- The model does not display the old abstract placement grid.

## Error Handling

The generation script should:

- Refuse to silently append duplicate geometry to an existing non-empty `RV_Exterior` document.
- Either create a fresh document or explicitly clear only the `RV_Exterior` document.
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
