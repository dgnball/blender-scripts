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

# Create ice material
mat = bpy.data.materials.new(name="Ice_Material")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
nodes.clear()

# Create shader nodes
output = nodes.new(type='ShaderNodeOutputMaterial')
output.location = (400, 0)

glass = nodes.new(type='ShaderNodeBsdfGlass')
glass.location = (0, 0)
glass.inputs['IOR'].default_value = 1.31  # Ice IOR
glass.inputs['Roughness'].default_value = 0.05

# Add translucent shader for subsurface effect
translucent = nodes.new(type='ShaderNodeBsdfTranslucent')
translucent.location = (0, -200)
translucent.inputs['Color'].default_value = (0.9, 0.95, 1.0, 1.0)  # Slight blue tint

# Mix shaders
mix = nodes.new(type='ShaderNodeMixShader')
mix.location = (200, 0)
mix.inputs['Fac'].default_value = 0.8

# Connect nodes
links.new(glass.outputs['BSDF'], mix.inputs[1])
links.new(translucent.outputs['BSDF'], mix.inputs[2])
links.new(mix.outputs['Shader'], output.inputs['Surface'])

# Assign material to snowflake
snowflake.data.materials.append(mat)

# Setup camera
bpy.ops.object.camera_add(location=(12, -12, 8))
camera = bpy.context.active_object
camera.rotation_euler = (radians(60), 0, radians(45))

# Set as active camera
bpy.context.scene.camera = camera

# Setup lighting
# Key light
bpy.ops.object.light_add(type='AREA', location=(10, -10, 10))
key_light = bpy.context.active_object
key_light.data.energy = 200
key_light.data.size = 5

# Fill light
bpy.ops.object.light_add(type='AREA', location=(-8, -5, 8))
fill_light = bpy.context.active_object
fill_light.data.energy = 100
fill_light.data.size = 5
fill_light.data.color = (0.9, 0.95, 1.0)  # Slight blue tint

# Rim light from behind
bpy.ops.object.light_add(type='AREA', location=(0, 5, 5))
rim_light = bpy.context.active_object
rim_light.data.energy = 150
rim_light.data.size = 4

# Setup world (background)
world = bpy.data.worlds['World']
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.05, 0.05, 0.08, 1.0)  # Dark background
bg.inputs['Strength'].default_value = 0.5

# Setup render settings for better quality
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1920
bpy.context.scene.render.film_transparent = False

# Enable denoising
bpy.context.scene.cycles.use_denoising = True
bpy.context.view_layer.cycles.use_denoising = True

print("Snowflake generated successfully!")
print(f"- {len(snowflake_objects)} components merged")
print("- Ice material applied")
print("- Camera and lighting setup")
print("- Ready to render (F12)")
print("\nTip: Adjust parameters at the top of the script to customize your snowflake:")
print("  ARM_LENGTH, BRANCH_LEVELS, BRANCH_ANGLE, etc.")
