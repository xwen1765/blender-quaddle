import bpy
import os
import sys
import importlib
import math

#generate path
dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)
    

# --- Import and Reload Custom Modules ---
try:
    import createObject
    importlib.reload(createObject)
    import bakeImage
    importlib.reload(bakeImage)
    import addImageTextures
    importlib.reload(addImageTextures)
    print("Successfully imported 'createObject.py' and 'bakeImage.py'")
except ImportError as e:
    print(f"Error: Could not import a required module: {e}")
    print(f"Please ensure the files are located at: {scripts_path}")
    # Use dummy classes to prevent errors if an import fails
    class createObject: pass
    class bakeImage: pass

def createCone():
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=6, radius2=0.1, depth=9, location=(0, 0, 0))
    Cone = bpy.context.active_object
    Cone.name = 'Body'
    return Cone, 'Cone'
def createUpsideDownCone():
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=6, radius2=0.1, depth=9, location=(0, 0, 0))
    Cone = bpy.context.active_object
    Cone.name = 'Body'
    return Cone, 'UpsideDownCone'
def createCube():
    bpy.ops.mesh.primitive_cube_add(size= 8, location=(0, 0, 0))
    cube = bpy.context.active_object
    cube.name = 'Body'
    return cube, 'Cube'

# --- Function to map string names to creation functions ---
object_creation_map = {
    "Sphere": createObject.createSphere,
    "VerticalOblong": createObject.createVerticalOblong,
    "HorizontalOblong": createObject.createHorizontalOblong,
    "Cube": createCube,
#    "Diamond": createObject.createDiamond, 
    "Cylinder": createObject.createCylinder,
    "UpFrustum": createObject.createUpFrustum,
    "DownFrustum": createObject.createDownFrustum,
    "Cone": createCone,
    "UpsideDownCone": createUpsideDownCone,
}

# --- Core Morphing and Rendering Functions ---

def create_morphed_object(source_name, target_name, morph_value):
    """
    Creates two objects by name, morphs the source to the target,
    deletes the target, and returns the final morphed object.
    """
    if source_name not in object_creation_map:
        raise ValueError(f"Unknown source object name: {source_name}")
    source_obj, _ = object_creation_map[source_name]()
    source_obj.name = "MorphObject_Source"

    if target_name not in object_creation_map:
        raise ValueError(f"Unknown target object name: {target_name}")
    target_obj, _ = object_creation_map[target_name]()
    target_obj.name = "MorphObject_Target"

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

    return source_obj, "MorphObject"


def render_frame(obj_to_render, filepath):
    """
    Sets up a temporary camera and light, renders the given object
    to the specified file path, and cleans up the camera and light.
    """
    bpy.ops.object.camera_add(location=(30, -5, 15))
    camera_obj = bpy.context.active_object
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    empty_target = bpy.context.active_object
    constraint = camera_obj.constraints.new(type='TRACK_TO')
    constraint.target = empty_target
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'
    # Add a Sun light. Its location doesn't matter for lighting direction, only rotation does.
    bpy.ops.object.light_add(type='SUN', align='WORLD', location=(10, 0, 0))
    light_obj = bpy.context.active_object
    light_obj.rotation_euler = ( 0, math.radians(90),  0)
    light_obj.data.energy = 3


    scene = bpy.context.scene
    scene.camera = camera_obj
    scene.render.filepath = filepath
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = True
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512

    bpy.ops.render.render(write_still=True)
    
    bpy.ops.object.select_all(action='DESELECT')
    camera_obj.select_set(True)
    light_obj.select_set(True)
    empty_target.select_set(True)
    bpy.ops.object.delete()


# --- Main Execution ---
if __name__ == "__main__":
    
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
        
    # --- Define your morphing job here ---
    SOURCE_SHAPE_NAME = "Sphere"
    TARGET_SHAPE_NAME = "Cube"
    NUM_FRAMES = 20
    
    body_pattern = 'grid_05_08.png'
    fractal = 'F (5).png'
    

    # --- Prepare output directories ---
    folder_name = f"{SOURCE_SHAPE_NAME}_to_{TARGET_SHAPE_NAME}_Render"
    output_folder = bpy.path.abspath(f"//{folder_name}/")
    baked_textures_folder = os.path.join(output_folder, "baked_textures")
    if not os.path.exists(output_folder): os.makedirs(output_folder)
    if not os.path.exists(baked_textures_folder): os.makedirs(baked_textures_folder)
    print(f"Render output will be saved to: {output_folder}")
    print(f"Baked textures will be saved to: {baked_textures_folder}")
    
    # --- Set up paths for bakeImage module ---
    # Assuming 'dir' from your snippet refers to the main scripts path
    base_path = dir
    pattern_path = os.path.join(base_path, 'Assets/patterns')
    fractal_path = os.path.join(base_path, 'Assets/fractals')
    path1 = os.path.join(pattern_path, body_pattern)
    path2 = os.path.join(fractal_path, fractal)

    # --- Render Loop ---
    for i in range(NUM_FRAMES):
        print(f"--- Processing Frame {i+1}/{NUM_FRAMES} ---")
        
        morph_progress = i / (NUM_FRAMES - 1) -0.01
        
        # 1. Create the morphed object for this frame
        morphed_obj, obj_type = create_morphed_object(
            SOURCE_SHAPE_NAME, TARGET_SHAPE_NAME, morph_progress
        )
        print(f"Created '{obj_type}' with morph value {morph_progress:.2f}")
        
        # 2. Apply and Bake material using your custom module
        # This assumes the morphed_obj is the 'body'
        try:
            texture_name = f"baked_texture_frame_{i:03d}"
            addImageTextures.addTextureImageWithUVProject(morphed_obj, "Sphere", path1, path2)
            bakeImage.bake_material_to_new_uv_and_image(morphed_obj, texture_name, baked_textures_folder)
            print(f"Applied and baked material to '{morphed_obj.name}'")
            
        except Exception as e:
            print(f"Could not bake material for frame {i}: {e}")
       
        # 3. Render the textured object
        frame_filepath = os.path.join(output_folder, f"frame_{i:03d}.png")
        render_frame(morphed_obj, frame_filepath)
        print(f"Rendered frame to {frame_filepath}")
#        stop
        # 4. Delete the morphed object to prepare for the next loop
        bpy.ops.object.select_all(action='DESELECT')
        morphed_obj.select_set(True)
        bpy.ops.object.delete()

    print(f"\nSUCCESS: Rendered {NUM_FRAMES} frames.")
