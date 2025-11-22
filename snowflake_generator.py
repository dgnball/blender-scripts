import bpy
import bmesh
from math import cos, sin, pi, radians
import mathutils

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Snowflake parameters
ARM_COUNT = 6  # Hexagonal symmetry
ARM_LENGTH = 5.0
ARM_SEGMENTS = 5
BRANCH_LEVELS = 2
BRANCH_ANGLE = 30  # degrees
BRANCH_LENGTH_RATIO = 0.6
THICKNESS = 0.08
BRANCH_THICKNESS_RATIO = 0.7

# Animation parameters
ANIMATION_LENGTH = 240  # frames (8 seconds at 30fps, 10 seconds at 24fps)
ROTATIONS = 2  # Number of full rotations during animation
FPS = 30


def create_cylinder_between_points(p1, p2, radius, name="Branch"):
    """Create a cylinder between two points."""
    # Calculate direction and length
    direction = p2 - p1
    length = direction.length

    if length < 0.001:  # Too short to create
        return None

    # Create cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=length,
        location=(p1 + p2) / 2
    )

    cylinder = bpy.context.active_object
    cylinder.name = name

    # Rotate to align with direction
    direction.normalize()
    z_axis = mathutils.Vector((0, 0, 1))

    # Calculate rotation
    if abs(direction.dot(z_axis)) < 0.9999:
        rotation_axis = z_axis.cross(direction)
        rotation_angle = z_axis.angle(direction)
        cylinder.rotation_mode = 'AXIS_ANGLE'
        cylinder.rotation_axis_angle = (rotation_angle, *rotation_axis)
    elif direction.dot(z_axis) < 0:
        cylinder.rotation_euler = (pi, 0, 0)

    return cylinder


def create_branch(start_point, direction, length, thickness, level=0, max_level=BRANCH_LEVELS):
    """Recursively create a branch with sub-branches."""
    objects = []

    # Calculate end point
    end_point = start_point + direction * length

    # Create main branch segment
    cylinder = create_cylinder_between_points(start_point, end_point, thickness)
    if cylinder:
        objects.append(cylinder)

    # Add sub-branches if not at max level
    if level < max_level:
        # Calculate positions along the branch for sub-branches
        num_sub_branches = 2 + level  # More sub-branches on earlier levels

        for i in range(1, num_sub_branches):
            # Position along main branch
            t = i / num_sub_branches
            sub_start = start_point + direction * length * t

            # Create two sub-branches (left and right)
            for side in [-1, 1]:
                # Rotate direction for sub-branch
                angle = radians(BRANCH_ANGLE * side)

                # Create rotation matrix around z-axis
                rot_z = mathutils.Matrix.Rotation(angle, 3, 'Z')
                sub_direction = rot_z @ direction

                sub_length = length * BRANCH_LENGTH_RATIO * (1 - t * 0.3)
                sub_thickness = thickness * BRANCH_THICKNESS_RATIO

                # Recursively create sub-branch
                sub_objects = create_branch(
                    sub_start,
                    sub_direction,
                    sub_length,
                    sub_thickness,
                    level + 1,
                    max_level
                )
                objects.extend(sub_objects)

    return objects


def create_snowflake():
    """Create the complete snowflake with hexagonal symmetry."""
    all_objects = []

    # Create 6 main arms with hexagonal symmetry
    for i in range(ARM_COUNT):
        angle = (2 * pi * i) / ARM_COUNT

        # Direction for this arm
        direction = mathutils.Vector((cos(angle), sin(angle), 0))
        start_point = mathutils.Vector((0, 0, 0))

        # Create the main arm and its branches
        arm_objects = create_branch(
            start_point,
            direction,
            ARM_LENGTH,
            THICKNESS
        )
        all_objects.extend(arm_objects)

    # Add center hexagon
    bpy.ops.mesh.primitive_cylinder_add(
        radius=THICKNESS * 2,
        depth=THICKNESS * 1.5,
        location=(0, 0, 0)
    )
    center = bpy.context.active_object
    center.name = "Center"
    all_objects.append(center)

    return all_objects


# Create the snowflake
print("Generating snowflake...")
snowflake_objects = create_snowflake()

# Join all objects into one
bpy.ops.object.select_all(action='DESELECT')
for obj in snowflake_objects:
    obj.select_set(True)

bpy.context.view_layer.objects.active = snowflake_objects[0]
bpy.ops.object.join()

snowflake = bpy.context.active_object
snowflake.name = "Snowflake"

# Add smooth shading
bpy.ops.object.shade_smooth()

# Add subdivision surface modifier for smoother appearance
subsurf = snowflake.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 2
subsurf.render_levels = 3

# Create enhanced ice material with more visual interest
mat = bpy.data.materials.new(name="Ice_Material")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
nodes.clear()

# Create shader nodes for a more complex ice material
output = nodes.new(type='ShaderNodeOutputMaterial')
output.location = (800, 0)

# Main glass shader
glass = nodes.new(type='ShaderNodeBsdfGlass')
glass.location = (400, 100)
glass.inputs['IOR'].default_value = 1.31  # Ice IOR
glass.inputs['Roughness'].default_value = 0.02  # Very smooth ice

# Glossy shader for highlights
glossy = nodes.new(type='ShaderNodeBsdfGlossy')
glossy.location = (400, -100)
glossy.inputs['Roughness'].default_value = 0.1
glossy.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)

# Translucent shader for subsurface effect
translucent = nodes.new(type='ShaderNodeBsdfTranslucent')
translucent.location = (400, -300)
translucent.inputs['Color'].default_value = (0.85, 0.92, 1.0, 1.0)  # Blue tint

# Fresnel for edge detection
fresnel = nodes.new(type='ShaderNodeFresnel')
fresnel.location = (0, 0)
fresnel.inputs['IOR'].default_value = 1.31

# Mix glass and glossy based on fresnel
mix1 = nodes.new(type='ShaderNodeMixShader')
mix1.location = (600, 0)

# Mix in translucent
mix2 = nodes.new(type='ShaderNodeMixShader')
mix2.location = (600, -200)
mix2.inputs['Fac'].default_value = 0.3

# Final mix
mix3 = nodes.new(type='ShaderNodeMixShader')
mix3.location = (600, 100)

# Connect nodes for layered ice effect
links.new(fresnel.outputs['Fac'], mix1.inputs['Fac'])
links.new(glass.outputs['BSDF'], mix1.inputs[1])
links.new(glossy.outputs['BSDF'], mix1.inputs[2])
links.new(translucent.outputs['BSDF'], mix2.inputs[1])
links.new(mix1.outputs['Shader'], mix2.inputs[2])
links.new(mix2.outputs['Shader'], output.inputs['Surface'])

# Assign material to snowflake
snowflake.data.materials.append(mat)

# Setup camera with slight tilt for dynamic view
bpy.ops.object.camera_add(location=(15, -10, 6))
camera = bpy.context.active_object
camera.rotation_euler = (radians(70), 0, radians(50))
camera.data.lens = 85  # Slightly telephoto for nice compression

# Set as active camera
bpy.context.scene.camera = camera

# Enable depth of field for cinematic look (optional - comment out if you want everything sharp)
camera.data.dof.use_dof = True
camera.data.dof.focus_distance = 18.0
camera.data.dof.aperture_fstop = 2.8

# Setup cinematic lighting
# Key light - main bright light from above-right
bpy.ops.object.light_add(type='AREA', location=(12, -8, 12))
key_light = bpy.context.active_object
key_light.data.energy = 300
key_light.data.size = 6
key_light.data.color = (1.0, 0.98, 0.95)  # Warm white
key_light.rotation_euler = (radians(45), 0, radians(35))

# Fill light - softer, cooler light from the left
bpy.ops.object.light_add(type='AREA', location=(-10, -6, 8))
fill_light = bpy.context.active_object
fill_light.data.energy = 120
fill_light.data.size = 8
fill_light.data.color = (0.85, 0.90, 1.0)  # Cool blue
fill_light.rotation_euler = (radians(50), 0, radians(-30))

# Rim/back light - creates edge highlights
bpy.ops.object.light_add(type='AREA', location=(2, 10, 5))
rim_light = bpy.context.active_object
rim_light.data.energy = 250
rim_light.data.size = 5
rim_light.data.color = (0.9, 0.95, 1.0)  # Cool rim light
rim_light.rotation_euler = (radians(60), 0, radians(180))

# Accent light - adds sparkle from below
bpy.ops.object.light_add(type='POINT', location=(0, 0, -5))
accent_light = bpy.context.active_object
accent_light.data.energy = 100
accent_light.data.color = (1.0, 1.0, 1.0)
accent_light.data.shadow_soft_size = 0.5

# Setup world with gradient background
world = bpy.data.worlds['World']
world.use_nodes = True
world_nodes = world.node_tree.nodes
world_links = world.node_tree.links

# Clear existing nodes
world_nodes.clear()

# Create gradient background
world_output = world_nodes.new(type='ShaderNodeOutputWorld')
world_output.location = (400, 0)

background = world_nodes.new(type='ShaderNodeBackground')
background.location = (200, 0)
background.inputs['Strength'].default_value = 0.3

# Color ramp for gradient
color_ramp = world_nodes.new(type='ShaderNodeValToRGB')
color_ramp.location = (0, 0)
color_ramp.color_ramp.elements[0].color = (0.02, 0.03, 0.08, 1.0)  # Dark blue
color_ramp.color_ramp.elements[1].color = (0.08, 0.10, 0.15, 1.0)  # Lighter blue

# Texture coordinate for gradient
tex_coord = world_nodes.new(type='ShaderNodeTexCoord')
tex_coord.location = (-400, 0)

# Mapping node
mapping = world_nodes.new(type='ShaderNodeMapping')
mapping.location = (-200, 0)

# Connect world nodes
world_links.new(tex_coord.outputs['Window'], mapping.inputs['Vector'])
world_links.new(mapping.outputs['Vector'], color_ramp.inputs['Fac'])
world_links.new(color_ramp.outputs['Color'], background.inputs['Color'])
world_links.new(background.outputs['Background'], world_output.inputs['Surface'])

# ===== ANIMATION SETUP =====

# Set animation frame range
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = ANIMATION_LENGTH
bpy.context.scene.render.fps = FPS

# Animate snowflake rotation
snowflake.rotation_mode = 'XYZ'
snowflake.rotation_euler = (0, 0, 0)

# Set initial keyframe
snowflake.keyframe_insert(data_path="rotation_euler", frame=1)

# Set final keyframe (multiple rotations)
final_rotation = 2 * pi * ROTATIONS
snowflake.rotation_euler = (0, 0, final_rotation)
snowflake.keyframe_insert(data_path="rotation_euler", frame=ANIMATION_LENGTH)

# Set interpolation to linear for constant rotation speed
fcurves = snowflake.animation_data.action.fcurves
for fcurve in fcurves:
    for keyframe in fcurve.keyframe_points:
        keyframe.interpolation = 'LINEAR'

# Optional: Add subtle wobble for more organic movement
# Uncomment these lines if you want a slight floating motion
# snowflake.location = (0, 0, 0)
# snowflake.keyframe_insert(data_path="location", frame=1)
# snowflake.location = (0, 0, 0.3)
# snowflake.keyframe_insert(data_path="location", frame=ANIMATION_LENGTH // 2)
# snowflake.location = (0, 0, 0)
# snowflake.keyframe_insert(data_path="location", frame=ANIMATION_LENGTH)

# Optional: Animate a light for dynamic lighting effects
key_light.data.energy = 300
key_light.data.keyframe_insert(data_path="energy", frame=1)
key_light.data.energy = 400
key_light.data.keyframe_insert(data_path="energy", frame=ANIMATION_LENGTH // 2)
key_light.data.energy = 300
key_light.data.keyframe_insert(data_path="energy", frame=ANIMATION_LENGTH)

# Setup render settings for high-quality video
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128  # Good balance of quality and speed
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080  # 16:9 for video
bpy.context.scene.render.resolution_percentage = 100

# Video output settings
bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
bpy.context.scene.render.ffmpeg.format = 'MPEG4'
bpy.context.scene.render.ffmpeg.codec = 'H264'
bpy.context.scene.render.ffmpeg.constant_rate_factor = 'HIGH'  # High quality
bpy.context.scene.render.ffmpeg.ffmpeg_preset = 'BEST'
bpy.context.scene.render.filepath = '/tmp/snowflake_animation.mp4'

# Enable motion blur for smoother animation
bpy.context.scene.render.use_motion_blur = True
bpy.context.scene.render.motion_blur_shutter = 0.5

# Enable denoising for cleaner renders
bpy.context.scene.cycles.use_denoising = True
bpy.context.view_layer.cycles.use_denoising = True

# Use GPU if available (much faster!)
bpy.context.scene.cycles.device = 'GPU'
preferences = bpy.context.preferences.addons['cycles'].preferences
preferences.compute_device_type = 'METAL'  # For Mac
preferences.get_devices()
for device in preferences.devices:
    device.use = True

print("\n" + "=" * 60)
print("SNOWFLAKE ANIMATION GENERATED SUCCESSFULLY!")
print("=" * 60)
print(f"Animation length: {ANIMATION_LENGTH} frames ({ANIMATION_LENGTH / FPS:.1f} seconds)")
print(f"Rotations: {ROTATIONS}")
print(f"Resolution: {bpy.context.scene.render.resolution_x}x{bpy.context.scene.render.resolution_y}")
print(f"FPS: {FPS}")
print("\nTO RENDER YOUR VIDEO:")
print("  Option 1: Press Ctrl+F12 (or Cmd+F12 on Mac)")
print("  Option 2: Go to Render → Render Animation")
print(f"\nVideo will be saved to: {bpy.context.scene.render.filepath}")
print("\nTO PREVIEW:")
print("  Press Spacebar in the viewport to play animation")
print("  Use viewport shading 'Rendered' (press Z → Rendered) to see materials")
print("\nTO CUSTOMIZE:")
print("  - Adjust ANIMATION_LENGTH for longer/shorter video")
print("  - Adjust ROTATIONS for more/fewer spins")
print("  - Adjust cycles.samples (128 = good, 256 = great, 512 = excellent)")
print("  - Comment out depth_of_field lines for sharper focus")
print("=" * 60)