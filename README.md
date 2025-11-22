# Rendering Your Animated Snowflake Video

## Step 1: Install Blender

### Option A: Download from Website (Recommended)
1. Go to https://www.blender.org/download/
2. Click "Download Blender" for macOS
3. Open the downloaded `.dmg` file
4. Drag Blender to your Applications folder
5. Open Blender from Applications (you may need to right-click → Open the first time due to macOS security)

### Option B: Install via Homebrew
```bash
brew install --cask blender
```

## Step 2: Run the Script in Blender

1. **Open Blender**
2. **Open the Scripting workspace** (click "Scripting" at the top)
3. **Open the script**: Click "Open" and navigate to `snowflake_generator.py`
4. **Run the script**: Click the "Play" button (▶) or press `Alt+P`
5. **Preview the animation**: Press `Spacebar` in the viewport
6. **Render the video**: Press `Cmd+F12` (or go to Render → Render Animation)
7. **Wait** while it renders (time depends on settings)
8. **Find your video** at `/tmp/snowflake_animation.mp4`

## What You'll Get

The animation script creates:
- **8 seconds** of smooth rotation (240 frames at 30fps)
- **2 full rotations** of the snowflake
- **Cinematic lighting** with 4 lights creating dramatic effects:
  - Warm key light from top-right
  - Cool blue fill light from left
  - Rim light creating edge highlights
  - Accent light from below for sparkle
- **Depth of field** (optional blur) for cinematic look
- **Motion blur** for smooth movement
- **1920x1080 HD** resolution
- **Gradient background** (dark to light blue)

## Rendering Tips

### For Fastest Rendering (Preview Quality)
Edit these lines in the script:
```python
bpy.context.scene.cycles.samples = 64  # Less samples = faster
bpy.context.scene.render.resolution_percentage = 50  # Half resolution
```

### For Best Quality (Final Output)
```python
bpy.context.scene.cycles.samples = 256  # Or even 512 for pristine quality
bpy.context.scene.render.resolution_percentage = 100
```

### Render Time Estimates (on M1/M2 Mac)
- **Preview (64 samples, 50%)**: ~5-10 minutes
- **Good (128 samples, 100%)**: ~15-30 minutes
- **Excellent (256 samples, 100%)**: ~30-60 minutes

## Customization Options

### Animation Speed
```python
ANIMATION_LENGTH = 240  # frames
# 120 frames = 4 seconds (faster)
# 360 frames = 12 seconds (slower, more graceful)

ROTATIONS = 2  # number of spins
# 1 = single slow rotation
# 3 = faster spinning
```

### Video Settings
```python
FPS = 30  # Standard for web
# 24 = cinematic film look
# 60 = ultra-smooth (renders slower)
```

### Camera Effects

**Remove depth of field** (make everything sharp):
Find these lines and comment them out:
```python
# camera.data.dof.use_dof = True
# camera.data.dof.focus_distance = 18.0
# camera.data.dof.aperture_fstop = 2.8
```

**Adjust blur amount** (if keeping DOF):
```python
camera.data.dof.aperture_fstop = 2.8  # Lower = more blur (1.4 = very blurry)
                                       # Higher = less blur (8.0 = subtle)
```

### Lighting Intensity

Make it brighter or darker by adjusting energy values:
```python
key_light.data.energy = 300   # Increase for brighter (try 500)
fill_light.data.energy = 120  # Soften shadows (try 200)
rim_light.data.energy = 250   # Edge highlights (try 400 for more pop)
```

### Add Vertical Movement

Uncomment these lines in the script for floating motion:
```python
snowflake.location = (0, 0, 0)
snowflake.keyframe_insert(data_path="location", frame=1)
snowflake.location = (0, 0, 0.3)
snowflake.keyframe_insert(data_path="location", frame=ANIMATION_LENGTH // 2)
snowflake.location = (0, 0, 0)
snowflake.keyframe_insert(data_path="location", frame=ANIMATION_LENGTH)
```

## Advanced: Viewport Preview

Before committing to a full render:

1. **Switch viewport shading**: Press `Z` → `Rendered`
2. **Play animation**: Press `Spacebar`
3. **Adjust view**: Use mouse to orbit around

This lets you see how it will look without waiting for full render!

## Output Locations

The script saves to `/tmp/snowflake_animation.mp4`

To change the output location, edit this line:
```python
bpy.context.scene.render.filepath = '/Users/yourusername/Movies/snowflake.mp4'
```

## Creating Different Versions

Try these combinations:

**Delicate Crystal**
```python
THICKNESS = 0.05
BRANCH_LEVELS = 3
ANIMATION_LENGTH = 360  # Slow, graceful
ROTATIONS = 1
```

**Bold Geometric**
```python
THICKNESS = 0.12
BRANCH_ANGLE = 45
ANIMATION_LENGTH = 180  # Faster
ROTATIONS = 3
```

**Sparkly Ice**
```python
glass.inputs['Roughness'].default_value = 0.15  # More scattering
accent_light.data.energy = 300  # Brighter sparkle
```

## Troubleshooting

**Snowflake appears still (not animating):**
- Make sure you pressed `Spacebar` to play the animation in the viewport
- Check the timeline at the bottom - it should show frames 1-240
- Ensure you're not viewing just a single frame
- Try scrubbing through the timeline to see if the snowflake rotates

**Render is stuck at 0%:**
- Be patient! The first frame always takes the longest (compiling shaders)
- Check the Blender console for errors

**Video file is huge:**
- This is normal for high quality
- You can compress later with QuickTime or HandBrake

**Animation looks choppy:**
- Make sure motion blur is enabled
- Increase samples for smoother lighting

**Can't find the output file:**
- Check the console output for the exact path
- Try an absolute path like `/Users/yourusername/Desktop/snowflake.mp4`

**Rendering is too slow:**
- Lower samples to 64
- Reduce resolution_percentage to 50
- Turn off depth of field
- Make the animation shorter

## Fun Ideas

1. **Loop it perfectly**: Set ROTATIONS to exactly match your FPS for seamless loops
2. **Color variations**: Change light colors for sunset (orange), night (deep blue), etc.
3. **Multiple snowflakes**: Run script multiple times, position differently, render together
4. **Add music**: Import your video into iMovie/Final Cut and add atmospheric music
5. **Instagram**: Render at 1080x1080 square format for social media

Enjoy your beautiful rotating snowflake!