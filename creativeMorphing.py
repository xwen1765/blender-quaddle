import bpy
import os
import sys
import importlib
import math

# --- 1. SETUP PATHS ---
dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

# --- 2. IMPORT MODULES ---
try:
    import createObject
    importlib.reload(createObject)
    import bakeImage
    importlib.reload(bakeImage)
    import addImageTextures
    importlib.reload(addImageTextures)
    import helperFunctions
    importlib.reload(helperFunctions)
    print("Modules loaded successfully.")
except ImportError as e:
    print(f"Error importing modules: {e}")

# --- 3. HELPER FUNCTIONS ---

def colorPatternPath(pattern_number, main_color_number, comp_color_number):
    """Reused from parser to find texture paths"""
    patterns = ["solid", "horizontal", "vertical", "diagonal", "grid"]
    colors = ['00','01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    
    smallerNumber = min(main_color_number, comp_color_number)
    largerNumber = max(main_color_number, comp_color_number)
    
    if pattern_number == 0 or largerNumber == smallerNumber:
        return dir + "/Assets/patterns/" + "solid" + "_" + colors[largerNumber]+ ".png"
    else:
        return dir + "/Assets/patterns/" + patterns[pattern_number] + "_" + colors[smallerNumber]  + "_" + colors[largerNumber]+ ".png"

def parseMorphTable(filepath):
    """
    Parses input file. 
    Expected format per line (12 items):
    [Src, Tgt, Pat, Col1, Col2, Frac, L_Dir, R_Dir, L_Start, L_End, R_Start, R_End]
    """
    f = open(filepath)
    morph_jobs = []
    line = f.readline()
    while line:
        if "[" in line:
            clean = line.split("[")[1].split("]")[0]
            items = clean.split(",")
            # Convert to ints, ignore whitespace
            morph_jobs.append([int(x) for x in items if x.strip()])
        line = f.readline()
    f.close()
    return morph_jobs

def get_bend_direction_name(index):
    """Maps integer input to direction string."""
    # 0 = No Arm / None, 1 = Up, 2 = Down
    mapping = ["none", "up", "down"]
    if 0 <= index < len(mapping):
        return mapping[index]
    return "none"

# --- 4. ARM CREATION FUNCTIONS ---

def addArms(body_type, left_right, bend_directions, morph_angle):
    if left_right == 'both':
        location, bend_angle = calculate_locations(body_type, 'left', bend_directions[0])
        addSingleArm(location, bend_angle, bend_directions[0], 'left', morph_angle)
        location, bend_angle = calculate_locations(body_type, 'right', bend_directions[1])
        addSingleArm(location, bend_angle, bend_directions[1], 'right', morph_angle)
    else:
        location, bend_angle = calculate_locations(body_type, left_right, bend_directions[0])
        addSingleArm(location, bend_angle, bend_directions[0], left_right, morph_angle)

def calculate_locations(body_type, left_right, bend_direction):
    # Normalized Radius lookup
    bt_lower = body_type.lower()
    if "horizontal" in bt_lower:
        radius = 6
    else:
        radius = 4

    if left_right == "right":
        if bend_direction == "up":
            location = (0, radius + 1, 0)
            bend_angle = (math.radians(90), 0, 0)
        elif bend_direction == "down":
            location = (0, radius + 1, 0)
            bend_angle = (math.radians(-90), 0, 0)
        else:
            location = (0, radius + 1, 0)
            bend_angle = (math.radians(90), 0, 0)
    elif left_right == "left":
        if bend_direction == "up":
            location = (0, -radius - 1,  0)
            bend_angle = (math.radians(90), 0, 0)
        elif bend_direction == "down":
            location = (0, -radius - 1,  0)
            bend_angle = (math.radians(-90), 0, 0)
        else:
            location = (0, -radius - 1,  0)
            bend_angle = (math.radians(90), 0, 0)
    else: 
        location = (radius + 1, 0, 0)
        bend_angle = (0, 0, 0)

    return location, bend_angle

def addSingleArm(location, bend_angle, bend_direction, left_right, morph_angle):
    """
    morph_angle input: 0.0 to 1.0
    """
    bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=1, depth=4, vertices=16, location=location)
    obj = bpy.context.active_object
    obj.name = "Arm_" + left_right
    
    mod = obj.modifiers.new('Subsurf', 'SUBSURF')
    mod.subdivision_type = 'SIMPLE'
    mod.levels = 4
    mod.render_levels = 3

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.transform.resize(value=(1, 1, 2))
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.data.update()

    if bend_direction != 'none':
        modifier = obj.modifiers.new(name='Simple Deform', type='SIMPLE_DEFORM')
        modifier.deform_method = 'BEND'
        # Logic: -90 + 180 * morph_angle = degrees
        modifier.angle = math.radians(-90 + 180.0 * morph_angle) 
        
        if (left_right == 'left' and bend_direction == 'up') or (left_right == 'right' and bend_direction == 'down'):
            modifier.limits[0] = 0.5
        else:
            modifier.limits[1] = 0.5
        modifier.deform_axis = 'X'

    obj.rotation_euler = bend_angle
    obj.update_tag()
    return obj

# --- 5. SHAPE DEFINITIONS ---

def createCone():
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=6, radius2=0.1, depth=9, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = 'Body'
    return obj, 'Cone'

def createUpsideDownCone():
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=6, radius2=0.1, depth=9, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.rotation_euler[0] = math.radians(180)
    obj.name = 'Body'
    return obj, 'UpsideDownCone'

def createCube():
    bpy.ops.mesh.primitive_cube_add(size=8, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = 'Body'
    return obj, 'Cube'

shape_map = {
    0: createObject.createSphere,
    1: createObject.createHorizontalOblong,
    2: createObject.createVerticalOblong,
    3: createCube, 
    4: createObject.createDiamond,
    5: createObject.createCylinder,
    6: createObject.createUpFrustum,
    7: createObject.createDownFrustum,
    8: createCone,            
    9: createUpsideDownCone   
}

shape_name_lookup = {
    0: "Sphere", 1: "HorizontalOblong", 2: "VerticalOblong", 3: "Cube",
    4: "Diamond", 5: "Cylinder", 6: "UpFrustum", 7: "DownFrustum",
    8: "Cone", 9: "UpsideDownCone"
}

# --- 6. CORE LOGIC ---

def create_morphed_object(source_idx, target_idx, morph_value):
    # Source
    if source_idx in shape_map: source_obj, _ = shape_map[source_idx]()
    else: source_obj, _ = createObject.createSphere()
    source_obj.name = "MorphObject_Source"

    # Target
    if target_idx in shape_map: target_obj, _ = shape_map[target_idx]()
    else: target_obj, _ = createCone()
    target_obj.name = "MorphObject_Target"

    # Morph
    bpy.context.view_layer.objects.active = source_obj
    source_obj.select_set(True)
    bpy.ops.object.shade_smooth()

    source_obj.shape_key_add(name='Basis')
    sw_modifier = source_obj.modifiers.new(name='Shrinkwrap', type='SHRINKWRAP')
    sw_modifier.target = target_obj
    sw_modifier.wrap_method = 'NEAREST_VERTEX'
    bpy.ops.object.modifier_apply_as_shapekey(modifier=sw_modifier.name)
    
    morph_key = source_obj.data.shape_keys.key_blocks[-1]
    morph_key.value = morph_value

    bpy.ops.object.select_all(action='DESELECT')
    target_obj.select_set(True)
    bpy.ops.object.delete()
    
    # Rename to Body for the export script to find it easily
    source_obj.name = "Body"

    return source_obj

def apply_texture_to_arm(arm_obj, pattern_path):
    if not arm_obj: return
    try:
        addImageTextures.addTextureSingleImage(arm_obj, "Arm", pattern_path)
    except Exception as e:
        print(f"Failed to texture arm: {e}")

# --- 7. EXPORT AND RENDER LOGIC (INTEGRATED) ---

def process_render_and_export(name, output_folder, models_folder, export_png, export_fbx, export_gltf):
    """
    Handles Camera setup, Rendering, Resize/Rotation transformation, and 3D Export.
    Integrated from the provided parser snippet.
    """
    
    # --- 1. RENDER PNG ---
    if export_png:
        body = bpy.data.objects.get("Body")
        # Head usually doesn't exist in morphs, but we keep the logic just in case
        head = bpy.data.objects.get("Head")
        
        # Default center calculation
        total_center = (0,0,0)
        
        if body:
            body_center = helperFunctions.calculate_center(body)
            if head:
                head_center = helperFunctions.calculate_center(head)
                total_center = (body_center + head_center) / 2
            else:
                total_center = body_center
        else:
            print("Either 'Body' or 'Head' object is not found in the scene")
            
        # Use the helper function to set camera/light and render
        # Note: helperFunctions.camera_light_action typically renders the image to export_path
        helperFunctions.camera_light_action(name, output_folder, True, True, True, total_center)

    # --- 2. TRANSFORMATION (Scale, Center, Rotate) ---
    # Prepare for 3D export by modifying the geometry in place
    
    obj = bpy.data.objects.get("Body")
    if obj:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
    
        # Select All (Arms + Body) to transform together
        bpy.ops.object.select_all(action='SELECT')
        
        saved_location = obj.location
        
        # Scale all selected objects down by a factor of 20 (0.1 in float)
        bpy.ops.transform.resize(value=(0.1, 0.1, 0.1))
        
        # Translate to center based on body location
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.ops.transform.translate(value=-saved_location)
        bpy.ops.object.select_all(action='DESELECT')
        
        # Rotate 90 degrees Z
        bpy.ops.object.select_all(action='SELECT')
        # saved_location is used again here in the original snippet
        bpy.ops.transform.rotate(value=math.radians(90), orient_axis='Z')
        bpy.ops.transform.translate(value=-saved_location)
        bpy.ops.object.select_all(action='DESELECT')
    
    # --- 3. EXPORT FBX ---
    if export_fbx:
        # Use the specific export path for models
        # Note: calling bakeImage.export_fbx which usually expects 'name' and 'path'
        bakeImage.export_fbx(name, models_folder)
        
    # --- 4. EXPORT GLTF ---
    if export_gltf:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                obj.select_set(True)
        
        # Export selected objects as gltf
        gltf_name =  name + ".gltf"
        gltf_path = os.path.join(models_folder, gltf_name)
        bpy.ops.export_scene.gltf(filepath=gltf_path, export_format='GLTF_EMBEDDED', export_apply=True)
        
        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')


def generateMorphSequence(traits, output_root, export_fbx=False, export_gltf=False, num_frames=20):
    # Unpack Traits
    src_idx = traits[0]
    tgt_idx = traits[1]
    pattern_idx = traits[2]
    col1 = traits[3]
    col2 = traits[4]
    fractal_idx = traits[5]
    l_bend_idx = traits[6] 
    r_bend_idx = traits[7]
    l_start_ang = traits[8]
    l_end_ang = traits[9]
    r_start_ang = traits[10]
    r_end_ang = traits[11]

    l_dir = get_bend_direction_name(l_bend_idx)
    r_dir = get_bend_direction_name(r_bend_idx)

    # Setup Folders
    seq_name = f"Morph_{src_idx}_to_{tgt_idx}_P{pattern_idx}"
    output_folder = os.path.join(output_root, seq_name)
    baked_folder = os.path.join(output_folder, "baked_textures")
    models_folder = os.path.join(output_folder, "3D_Models")
    
    if not os.path.exists(output_folder): os.makedirs(output_folder)
    if not os.path.exists(baked_folder): os.makedirs(baked_folder)
    if (export_fbx or export_gltf) and not os.path.exists(models_folder): 
        os.makedirs(models_folder)

    # Resolve Texture Paths
    tex_path = colorPatternPath(pattern_idx, col1, col2)
    fractal_path = ""
    if fractal_idx != 0:
        fractal_path = dir + "/Assets/fractals/F (" + str(fractal_idx) + ").png"

    print(f"Starting Morph: {seq_name}")
    source_shape_name = shape_name_lookup.get(src_idx, "Sphere")

    # --- FRAME LOOP ---
    for i in range(num_frames):
        # Progress 0.0 to 1.0
        progress = i / (num_frames - 1)
        
        # 1. Clear Scene
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        helperFunctions.reset_scene() # Ensure clean slate using helper

        # 2. Create Morphed Body
        morphed_obj = create_morphed_object(src_idx, tgt_idx, progress)
        
        # 3. Apply Texture & Bake Body
        try:
            bake_name = f"tex_frame_{i:03d}"
            if fractal_path:
                addImageTextures.addTextureImageWithUVProject(morphed_obj, "", tex_path, fractal_path)
            else:
                addImageTextures.addSingleTextureImageWithUVProject(morphed_obj, "Sphere", tex_path)
            bakeImage.bake_material_to_new_uv_and_image(morphed_obj, bake_name, baked_folder)
        except Exception as e:
            print(f"Bake warning frame {i}: {e}")

        # 4. CALCULATE ARM ANGLES (Linear Interpolation)
        current_l_angle = l_start_ang + (l_end_ang - l_start_ang) * progress
        current_r_angle = r_start_ang + (r_end_ang - r_start_ang) * progress
        
        # Convert degrees to 0.0-1.0 range
        morph_val_left = (current_l_angle + 90) / 180.0
        morph_val_right = (current_r_angle + 90) / 180.0

        # 5. ADD ARMS
        if l_dir != "none":
            addArms(source_shape_name, 'left', [l_dir], morph_val_left)
            left_arm = bpy.data.objects.get("Arm_left")
            apply_texture_to_arm(left_arm, tex_path)

        if r_dir != "none":
            addArms(source_shape_name, 'right', [r_dir], morph_val_right)
            right_arm = bpy.data.objects.get("Arm_right")
            apply_texture_to_arm(right_arm, tex_path)

        # 6. RENDER AND EXPORT (Using integrated Logic)
        frame_name = f"frame_{i:03d}"
        
        # This function renders the PNG using helperFunctions
        # Then applies the Scale/Rotate logic
        # Then exports the 3D files
        process_render_and_export(
            name=frame_name,
            output_folder=output_folder,
            models_folder=models_folder,
            export_png=True, 
            export_fbx=export_fbx,
            export_gltf=export_gltf
        )
        
        print(f"Processed Frame {i}")

    print(f"Finished Sequence: {seq_name}")


# --- 8. MAIN EXECUTION ---
if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    input_path = None
    output_path = dir
    export_fbx = False
    export_gltf = False
    
    # Argument Parsing
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
        
        if "--input_path" in argv:
            idx = argv.index("--input_path")
            if idx < len(argv) - 1: input_path = argv[idx + 1]
            
        if "--output_path" in argv:
            idx = argv.index("--output_path")
            if idx < len(argv) - 1: output_path = argv[idx + 1]
            
        if "--export_fbx" in argv:
            export_fbx = True
            
        if "--export_gltf" in argv:
            export_gltf = True

    if input_path is not None and os.path.exists(input_path):
        job_list = parseMorphTable(input_path)
        for traits in job_list:
            if len(traits) < 12:
                print(f"Skipping invalid line (needs 12 args): {traits}")
                continue
            generateMorphSequence(traits, output_path, export_fbx, export_gltf, num_frames=20)
    else:
        # --- ELSE PART: Direct Example ---
        print("No input file provided. Running default example object.")
        
        # Example Traits Array (12 items):
        # [0] Src: Sphere (0)
        # [1] Tgt: Cone (8)
        # [2] Pattern: Grid (3)
        # [3] Col1: 1
        # [4] Col2: 2
        # [5] Fractal: 8
        # [6] Left Dir: Up (1)
        # [7] Right Dir: Down (2)
        # [8-11] Left/Right Start/End Angles
        
        test_traits = [0, 0, 3, 4, 8, 8, 1, 2, 0, 90, 90, 0]
        
        generateMorphSequence(test_traits, output_path, export_fbx, export_gltf, num_frames=10)