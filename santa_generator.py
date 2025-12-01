import bpy
import bmesh
from math import cos, sin, pi, radians, sqrt
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Animation parameters
ANIMATION_LENGTH = 300  # frames (10 seconds at 30fps)
ROTATIONS = 1.5  # Number of full rotations
FPS = 30


def create_material(name, base_color, roughness=0.8, metallic=0.0):
    """Create a principled BSDF material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (*base_color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic

    # Try to set subsurface (name changed in Blender 4.0+)
    try:
        bsdf.inputs['Subsurface Weight'].default_value = 0.05
    except KeyError:
        try:
            bsdf.inputs['Subsurface'].default_value = 0.05
        except KeyError:
            pass  # Skip if neither exists

    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat


# Create materials
red_velvet = create_material("Red_Velvet", (0.8, 0.05, 0.05), roughness=0.9)
white_fur = create_material("White_Fur", (0.95, 0.95, 0.95), roughness=0.95)
skin_tone = create_material("Skin", (0.9, 0.7, 0.6), roughness=0.6)
black_material = create_material("Black", (0.05, 0.05, 0.05), roughness=0.7)
gold_material = create_material("Gold", (0.9, 0.7, 0.2), roughness=0.3, metallic=0.9)
brown_material = create_material("Brown", (0.3, 0.15, 0.05), roughness=0.8)


# Create Santa's body parts
def create_body():
    """Create Santa's torso."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, location=(0, 0, 1.5))
    body = bpy.context.active_object
    body.name = "Body"
    body.scale = (1.0, 0.9, 1.3)
    body.data.materials.append(red_velvet)

    # Add subdivision for smoothness
    subsurf = body.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 3

    return body


def create_head():
    """Create Santa's head."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, location=(0, 0, 3.2))
    head = bpy.context.active_object
    head.name = "Head"
    head.scale = (1.0, 0.95, 1.1)
    head.data.materials.append(skin_tone)

    subsurf = head.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 3

    return head


def create_hat():
    """Create Santa's hat."""
    # Hat base (red cone)
    bpy.ops.mesh.primitive_cone_add(radius1=0.7, radius2=0.15, depth=1.5, location=(0, 0, 4.2))
    hat = bpy.context.active_object
    hat.name = "Hat"
    hat.rotation_euler = (radians(15), 0, 0)  # Slight tilt
    hat.data.materials.append(red_velvet)

    # Hat brim (white fur)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.65,
        minor_radius=0.12,
        location=(0, 0, 3.7)
    )
    brim = bpy.context.active_object
    brim.name = "Hat_Brim"
    brim.data.materials.append(white_fur)

    # Hat pom-pom
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, location=(0, 0.15, 4.8))
    pompom = bpy.context.active_object
    pompom.name = "Pompom"
    pompom.data.materials.append(white_fur)

    return [hat, brim, pompom]


def create_beard():
    """Create Santa's beard."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(0, 0.3, 3.0))
    beard = bpy.context.active_object
    beard.name = "Beard"
    beard.scale = (1.2, 0.7, 1.4)
    beard.data.materials.append(white_fur)

    subsurf = beard.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2

    return beard


def create_mustache():
    """Create Santa's mustache."""
    # Left side
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(-0.25, 0.45, 3.25))
    mustache_l = bpy.context.active_object
    mustache_l.name = "Mustache_L"
    mustache_l.scale = (1.3, 0.6, 0.5)
    mustache_l.data.materials.append(white_fur)

    # Right side
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(0.25, 0.45, 3.25))
    mustache_r = bpy.context.active_object
    mustache_r.name = "Mustache_R"
    mustache_r.scale = (1.3, 0.6, 0.5)
    mustache_r.data.materials.append(white_fur)

    return [mustache_l, mustache_r]


def create_nose():
    """Create Santa's nose."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(0, 0.55, 3.25))
    nose = bpy.context.active_object
    nose.name = "Nose"
    nose.scale = (0.8, 1.2, 0.9)

    # Rosy nose material
    nose_mat = create_material("Nose", (0.9, 0.3, 0.3), roughness=0.5)
    nose.data.materials.append(nose_mat)

    return nose


def create_eyes():
    """Create Santa's eyes."""
    # Left eye
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(-0.2, 0.5, 3.4))
    eye_l = bpy.context.active_object
    eye_l.name = "Eye_L"
    eye_l.data.materials.append(black_material)

    # Right eye
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(0.2, 0.5, 3.4))
    eye_r = bpy.context.active_object
    eye_r.name = "Eye_R"
    eye_r.data.materials.append(black_material)

    return [eye_l, eye_r]


def create_arms():
    """Create Santa's arms."""
    arms = []

    for side in [-1, 1]:
        # Upper arm
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.25,
            depth=1.0,
            location=(side * 1.2, 0, 1.8)
        )
        arm = bpy.context.active_object
        arm.name = f"Arm_{'L' if side == -1 else 'R'}"
        arm.rotation_euler = (radians(20), 0, radians(side * 30))
        arm.data.materials.append(red_velvet)

        # Hand/mitten
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.22,
            location=(side * 1.5, -0.2, 1.2)
        )
        hand = bpy.context.active_object
        hand.name = f"Hand_{'L' if side == -1 else 'R'}"
        hand.scale = (1.0, 1.2, 0.8)
        hand.data.materials.append(red_velvet)

        arms.extend([arm, hand])

    return arms


def create_legs():
    """Create Santa's legs."""
    legs = []

    for side in [-1, 1]:
        # Leg
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.28,
            depth=1.2,
            location=(side * 0.4, 0, 0.3)
        )
        leg = bpy.context.active_object
        leg.name = f"Leg_{'L' if side == -1 else 'R'}"
        leg.data.materials.append(red_velvet)

        # Boot
        bpy.ops.mesh.primitive_cube_add(
            size=0.5,
            location=(side * 0.4, 0.15, -0.4)
        )
        boot = bpy.context.active_object
        boot.name = f"Boot_{'L' if side == -1 else 'R'}"
        boot.scale = (1.0, 1.5, 0.8)
        boot.data.materials.append(black_material)

        # Boot cuff
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.3,
            minor_radius=0.08,
            location=(side * 0.4, 0, -0.15)
        )
        cuff = bpy.context.active_object
        cuff.name = f"Boot_Cuff_{'L' if side == -1 else 'R'}"
        cuff.data.materials.append(white_fur)

        legs.extend([leg, boot, cuff])

    return legs


def create_belt():
    """Create Santa's belt."""
    # Belt main
    bpy.ops.mesh.primitive_torus_add(
        major_radius=1.05,
        minor_radius=0.12,
        location=(0, 0, 1.2)
    )
    belt = bpy.context.active_object
    belt.name = "Belt"
    belt.scale = (1.0, 0.9, 0.3)
    belt.data.materials.append(black_material)

    # Belt buckle
    bpy.ops.mesh.primitive_cube_add(
        size=0.35,
        location=(0, 0.95, 1.2)
    )
    buckle = bpy.context.active_object
    buckle.name = "Buckle"
    buckle.scale = (1.2, 0.3, 0.8)
    buckle.data.materials.append(gold_material)

    # Buckle center (hole)
    bpy.ops.mesh.primitive_cube_add(
        size=0.2,
        location=(0, 0.95, 1.2)
    )
    buckle_hole = bpy.context.active_object
    buckle_hole.name = "Buckle_Hole"
    buckle_hole.scale = (0.8, 1.0, 0.6)
    buckle_hole.data.materials.append(black_material)

    return [belt, buckle, buckle_hole]


def create_coat_trim():
    """Create white fur trim on coat."""
    trims = []

    # Bottom trim
    bpy.ops.mesh.primitive_torus_add(
        major_radius=1.15,
        minor_radius=0.15,
        location=(0, 0, 0.9)
    )
    trim_bottom = bpy.context.active_object
    trim_bottom.name = "Trim_Bottom"
    trim_bottom.scale = (1.0, 0.9, 0.4)
    trim_bottom.data.materials.append(white_fur)
    trims.append(trim_bottom)

    # Front trim (left side)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.12,
        depth=2.0,
        location=(0.45, 0.85, 1.8)
    )
    trim_front_l = bpy.context.active_object
    trim_front_l.name = "Trim_Front_L"
    trim_front_l.rotation_euler = (radians(10), 0, 0)
    trim_front_l.data.materials.append(white_fur)
    trims.append(trim_front_l)

    # Front trim (right side)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.12,
        depth=2.0,
        location=(-0.45, 0.85, 1.8)
    )
    trim_front_r = bpy.context.active_object
    trim_front_r.name = "Trim_Front_R"
    trim_front_r.rotation_euler = (radians(10), 0, 0)
    trim_front_r.data.materials.append(white_fur)
    trims.append(trim_front_r)

    # Collar
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.65,
        minor_radius=0.12,
        location=(0, 0, 2.8)
    )
    collar = bpy.context.active_object
    collar.name = "Collar"
    collar.scale = (1.0, 0.95, 0.5)
    collar.data.materials.append(white_fur)
    trims.append(collar)

    return trims


# Build Santa!
print("Creating Santa Claus...")

all_parts = []

body = create_body()
all_parts.append(body)

head = create_head()
all_parts.append(head)

hat_parts = create_hat()
all_parts.extend(hat_parts)

beard = create_beard()
all_parts.append(beard)

mustache = create_mustache()
all_parts.extend(mustache)

nose = create_nose()
all_parts.append(nose)

eyes = create_eyes()
all_parts.extend(eyes)

arms = create_arms()
all_parts.extend(arms)

legs = create_legs()
all_parts.extend(legs)

belt_parts = create_belt()
all_parts.extend(belt_parts)

trim_parts = create_coat_trim()
all_parts.extend(trim_parts)

# Create an empty to act as parent for all parts
bpy.ops.object.empty_add(location=(0, 0, 1.5))
santa_root = bpy.context.active_object
santa_root.name = "Santa"

# Parent all parts to the root
for part in all_parts:
    part.parent = santa_root

# Apply smooth shading to all parts
for part in all_parts:
    part.select_set(True)
bpy.ops.object.shade_smooth()
bpy.ops.object.select_all(action='DESELECT')

# ===== CAMERA SETUP =====
bpy.ops.object.camera_add(location=(8, -6, 2.5))
camera = bpy.context.active_object
camera.rotation_euler = (radians(85), 0, radians(50))
camera.data.lens = 50
bpy.context.scene.camera = camera

# Add slight depth of field for cinematic look
camera.data.dof.use_dof = True
camera.data.dof.focus_distance = 10.0
camera.data.dof.aperture_fstop = 4.0

# ===== LIGHTING SETUP =====

# Key light - warm from top-right
bpy.ops.object.light_add(type='AREA', location=(6, -4, 8))
key_light = bpy.context.active_object
key_light.data.energy = 400
key_light.data.size = 8
key_light.data.color = (1.0, 0.95, 0.85)  # Warm white
key_light.rotation_euler = (radians(45), 0, radians(30))

# Fill light - cooler from left
bpy.ops.object.light_add(type='AREA', location=(-5, -3, 5))
fill_light = bpy.context.active_object
fill_light.data.energy = 200
fill_light.data.size = 6
fill_light.data.color = (0.9, 0.95, 1.0)  # Cool blue
fill_light.rotation_euler = (radians(50), 0, radians(-30))

# Rim light - from behind for edge definition
bpy.ops.object.light_add(type='AREA', location=(0, 5, 4))
rim_light = bpy.context.active_object
rim_light.data.energy = 300
rim_light.data.size = 5
rim_light.data.color = (1.0, 0.98, 0.95)
rim_light.rotation_euler = (radians(60), 0, radians(180))

# Festive colored accent lights
# Red accent
bpy.ops.object.light_add(type='POINT', location=(3, 2, 3))
red_accent = bpy.context.active_object
red_accent.data.energy = 100
red_accent.data.color = (1.0, 0.2, 0.2)
red_accent.data.shadow_soft_size = 1.0

# Green accent
bpy.ops.object.light_add(type='POINT', location=(-3, 2, 3))
green_accent = bpy.context.active_object
green_accent.data.energy = 80
green_accent.data.color = (0.2, 1.0, 0.2)
green_accent.data.shadow_soft_size = 1.0

# ===== WORLD SETUP =====
world = bpy.data.worlds['World']
world.use_nodes = True
world_nodes = world.node_tree.nodes
world_nodes.clear()

world_output = world_nodes.new(type='ShaderNodeOutputWorld')
world_output.location = (300, 0)

background = world_nodes.new(type='ShaderNodeBackground')
background.location = (0, 0)
background.inputs['Color'].default_value = (0.02, 0.05, 0.15, 1.0)  # Dark festive blue
background.inputs['Strength'].default_value = 0.2

world.node_tree.links.new(background.outputs['Background'], world_output.inputs['Surface'])

# ===== ANIMATION SETUP =====

# Set frame range
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = ANIMATION_LENGTH
bpy.context.scene.render.fps = FPS

# Animate Santa rotation
santa_root.rotation_mode = 'XYZ'
santa_root.rotation_euler = (0, 0, 0)
santa_root.keyframe_insert(data_path="rotation_euler", frame=1)

final_rotation = 2 * pi * ROTATIONS
santa_root.rotation_euler = (0, 0, final_rotation)
santa_root.keyframe_insert(data_path="rotation_euler", frame=ANIMATION_LENGTH)

# Linear interpolation for smooth rotation
fcurves = santa_root.animation_data.action.fcurves
for fcurve in fcurves:
    for keyframe in fcurve.keyframe_points:
        keyframe.interpolation = 'LINEAR'

# Add slight wave animation to arms
for arm in [obj for obj in all_parts if 'Arm' in obj.name]:
    arm.rotation_euler.z = arm.rotation_euler.z
    arm.keyframe_insert(data_path="rotation_euler", frame=1)

    # Wave up
    original_z = arm.rotation_euler.z
    arm.rotation_euler.z = original_z + radians(15)
    arm.keyframe_insert(data_path="rotation_euler", frame=ANIMATION_LENGTH // 3)

    # Wave down
    arm.rotation_euler.z = original_z - radians(10)
    arm.keyframe_insert(data_path="rotation_euler", frame=2 * ANIMATION_LENGTH // 3)

    # Return
    arm.rotation_euler.z = original_z
    arm.keyframe_insert(data_path="rotation_euler", frame=ANIMATION_LENGTH)

# Pulsing lights for festive effect
for light, phase in [(red_accent, 0), (green_accent, ANIMATION_LENGTH // 4)]:
    light.data.energy = 100
    light.data.keyframe_insert(data_path="energy", frame=1 + phase)
    light.data.energy = 200
    light.data.keyframe_insert(data_path="energy", frame=ANIMATION_LENGTH // 2 + phase)
    light.data.energy = 100
    light.data.keyframe_insert(data_path="energy", frame=ANIMATION_LENGTH + phase)

# ===== RENDER SETTINGS =====

bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.resolution_percentage = 100

# Video output
bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
bpy.context.scene.render.ffmpeg.format = 'MPEG4'
bpy.context.scene.render.ffmpeg.codec = 'H264'
bpy.context.scene.render.ffmpeg.constant_rate_factor = 'HIGH'
bpy.context.scene.render.ffmpeg.ffmpeg_preset = 'BEST'
bpy.context.scene.render.filepath = '/tmp/santa_animation.mp4'

# Motion blur
bpy.context.scene.render.use_motion_blur = True
bpy.context.scene.render.motion_blur_shutter = 0.5

# Denoising
bpy.context.scene.cycles.use_denoising = True
bpy.context.view_layer.cycles.use_denoising = True

# GPU rendering on Mac
bpy.context.scene.cycles.device = 'GPU'
preferences = bpy.context.preferences.addons['cycles'].preferences
preferences.compute_device_type = 'METAL'
preferences.get_devices()
for device in preferences.devices:
    device.use = True

print("\n" + "=" * 60)
print("🎅 SANTA CLAUS GENERATED SUCCESSFULLY! 🎅")
print("=" * 60)
print(f"Animation length: {ANIMATION_LENGTH} frames ({ANIMATION_LENGTH / FPS:.1f} seconds)")
print(f"Rotations: {ROTATIONS}")
print(f"Total parts: {len(all_parts)}")
print(f"Resolution: {bpy.context.scene.render.resolution_x}x{bpy.context.scene.render.resolution_y}")
print(f"FPS: {FPS}")
print("\nFEATURES:")
print("  ✓ Full 3D Santa with hat, beard, coat, belt, boots")
print("  ✓ Waving arms animation")
print("  ✓ Festive red & green pulsing accent lights")
print("  ✓ Cinematic lighting with warm key & cool fill")
print("  ✓ Depth of field for professional look")
print("\nTO RENDER:")
print("  Press Cmd+F12 (or Render → Render Animation)")
print(f"\nOutput: {bpy.context.scene.render.filepath}")
print("\nTO PREVIEW:")
print("  Press Spacebar to play animation")
print("  Press Z → Rendered to see materials")
print("=" * 60)
print("Ho Ho Ho! 🎄")