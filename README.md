# Setting Up Blender for Python Snowflake Generation on Mac

## Step 1: Install Blender

### Option A: Download from Website (Recommended)
1. Go to https://www.blender.org/download/
2. Click "Download Blender" for macOS
3. Open the downloaded `.dmg` file
4. Drag Blender to your Applications folder
5. Open Blender from Applications (you may need to right-click → Open the first time due to Mac security)

### Option B: Install via Homebrew
```bash
brew install --cask blender
```

## Step 2: Running the Snowflake Script

### Method 1: Using Blender's Text Editor (Best for beginners)

1. **Open Blender**
   - Launch Blender from Applications
   - Close the splash screen

2. **Switch to Scripting Workspace**
   - At the top of the window, click "Scripting" tab
   - This gives you a nice layout with text editor and 3D viewport

3. **Load the Script**
   - In the text editor panel, click "Open" (folder icon at top)
   - Navigate to and select `snowflake_generator.py`
   - Or click "New" and paste the script content

4. **Run the Script**
   - Click the "Play" button (▶) at the top of the text editor
   - Or press `Option + P` (Alt + P)
   - Watch your snowflake appear in the 3D viewport!

5. **View Your Snowflake**
   - Use middle mouse button (or two-finger drag) to rotate view
   - Scroll to zoom
   - Press `Numpad 0` to see through camera view
   - Press `Z` for viewport shading options (try "Rendered" to see materials)

6. **Render the Final Image**
   - Press `F12` to render
   - Or go to Render → Render Image
   - The render will open in a new window
   - Save with Image → Save As

### Method 2: Command Line (For advanced users)

```bash
# Run Blender with the script
/Applications/Blender.app/Contents/MacOS/Blender --background --python snowflake_generator.py

# Or run and render immediately
/Applications/Blender.app/Contents/MacOS/Blender --background --python snowflake_generator.py --render-output //snowflake.png --render-frame 1

# Run with GUI to see the result
/Applications/Blender.app/Contents/MacOS/Blender --python snowflake_generator.py
```

## Step 3: Customize Your Snowflake

Edit these parameters at the top of the script:

```python
ARM_LENGTH = 5.0              # How long each arm extends
ARM_SEGMENTS = 5              # Complexity of each arm
BRANCH_LEVELS = 2             # How many levels of branches (2-3 recommended)
BRANCH_ANGLE = 30             # Angle of branches (degrees)
BRANCH_LENGTH_RATIO = 0.6     # How long branches are vs main arm
THICKNESS = 0.08              # Thickness of the ice crystals
BRANCH_THICKNESS_RATIO = 0.7  # How thick branches are vs main arm
```

**Try these variations:**
- **Delicate snowflake**: `BRANCH_LEVELS = 3`, `THICKNESS = 0.05`, `BRANCH_ANGLE = 25`
- **Chunky snowflake**: `THICKNESS = 0.12`, `BRANCH_LENGTH_RATIO = 0.8`
- **Sparse snowflake**: `BRANCH_LEVELS = 1`, `ARM_LENGTH = 6.0`

## Step 4: Tips for Best Results

### Better Rendering Quality
In the script, these settings control quality:
```python
bpy.context.scene.cycles.samples = 128  # Increase to 256 or 512 for better quality
bpy.context.scene.render.resolution_x = 1920  # Increase for higher resolution
```

### Viewport Navigation (Mac trackpad)
- **Rotate**: Two-finger drag
- **Pan**: Shift + Two-finger drag  
- **Zoom**: Pinch gesture or scroll

### Viewport Navigation (Mac mouse)
- **Rotate**: Middle mouse button + drag (or Shift + Option + drag)
- **Pan**: Shift + Middle mouse button + drag
- **Zoom**: Scroll wheel

### Keyboard Shortcuts
- `Numpad 0`: Camera view
- `Numpad 7`: Top view
- `F12`: Render image
- `Z`: Shading menu (try Solid, Material Preview, or Rendered)
- `G`: Move selected object
- `R`: Rotate selected object
- `S`: Scale selected object

## Step 5: Export Your Snowflake

### As an Image
1. Press `F12` to render
2. In the render window: Image → Save As
3. Choose format (PNG for transparency, JPEG for smaller files)

### As a 3D Model
1. Select the snowflake object
2. File → Export → Choose format:
   - `.obj` - Universal format
   - `.stl` - For 3D printing
   - `.gltf` - For web/AR applications

## Troubleshooting

**Script doesn't run:**
- Make sure you're in Blender 3.0 or newer
- Check the console for error messages (Window → Toggle System Console)

**Can't see the snowflake:**
- Press `Home` key to frame all objects
- Press `Numpad 0` for camera view
- Try pressing `Z` and selecting "Material Preview" or "Rendered"

**Render takes forever:**
- Reduce `samples` from 128 to 64
- Reduce resolution
- Your first render will take longer as Blender compiles shaders

**Snowflake looks faceted:**
- The subdivision modifier smooths it during rendering
- Press `F12` to see the smooth version

## Next Steps

**Animate your snowflake:**
- Add rotation animation
- Make it slowly spin as it falls
- Render as video

**Multiple snowflakes:**
- Run the script multiple times with different parameters
- Position them in a scene
- Create a snowfall

**Advanced materials:**
- Experiment with the ice material node setup
- Add sparkle/glitter effects
- Try different colors for artistic effects

Have fun creating beautiful snowflakes! 🎿❄️
