# Blender Scripts Collection

A collection of procedural Blender scripts for generating animated 3D models.

## Scripts

### snowflake_generator.py
Generates procedurally created 3D snowflakes with realistic branching patterns.

Features:
- Hexagonal symmetry (6 arms)
- Recursive branching structure
- Configurable parameters (arm count, length, branch levels, thickness)
- Built-in rotation animation
- Customizable animation length and rotation speed

### santa_generator.py
Creates a complete 3D Santa Claus model with materials and animation.

Features:
- Full character model with body, head, hat, belt, and accessories
- Material system with red velvet, white fur, skin tones, and gold
- Rotation animation
- Subsurface scattering support for Blender 4.0+

## Usage

1. Open Blender
2. Switch to the Scripting workspace
3. Open the script you want to use (File > Open or paste into the text editor)
4. Run the script with the "Run Script" button or press Alt+P
5. The script will clear existing objects and generate the new model

## Configuration

Each script contains parameters at the top that can be modified:
- Geometry settings (dimensions, segment counts, proportions)
- Animation settings (length, rotation speed, FPS)
- Material properties (colors, roughness, metallic values)

## Requirements

- Blender 3.0 or higher
- Scripts are compatible with Blender 4.0+ (with version-specific handling for material nodes)

## Output

All scripts generate:
- Fully textured 3D models
- Keyframed rotation animations
- Camera and lighting setup (where applicable)

Models can be rendered or exported for use in other projects.