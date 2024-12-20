import bpy
import os, sys
#generate path
dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)
    
from mathutils import Matrix
import math, random, mathutils
import numpy as np
import bmesh
import importlib

import addImageTextures
importlib.reload(addImageTextures)
import addArm
importlib.reload(addArm)
import addBeak
importlib.reload(addBeak)
import createObject
importlib.reload(createObject)
import addHead
importlib.reload(addHead)
import bakeImage
importlib.reload(bakeImage)
import helperFunctions
importlib.reload(helperFunctions)


def addArms(body_type, left_right, bend_directions, morph_angle):
    """
    Add arms to a body.

    Parameters:
    - body_type (str): The type of body to which the arms will be added.
    - left_right (str): A string indicating which arm or arms to add. Valid values are 'left', 'right', and 'both'.
    - bend_directions (list): A list of strings indicating the bend direction of each arm. Can be 'up', 'down' or 'none/straight'.
    """

    if left_right == 'both':
        location, bend_angle = calculate_locations(
            body_type, 'left', bend_directions[0])
        addSingleArm(location, bend_angle, bend_directions[0], 'left', morph_angle)
        location, bend_angle = calculate_locations(
            body_type, 'right', bend_directions[1])
        addSingleArm(location, bend_angle, bend_directions[1], 'right', morph_angle)
    else:
        location, bend_angle = calculate_locations(
            body_type, left_right, bend_directions[0])
        addSingleArm(location, bend_angle, bend_directions[0], left_right, morph_angle)
        


def calculate_locations(body_type, left_right, bend_direction):
    """
    Calculate the location and bend angle of an arm on a body.

    Parameters:
    - body_type (str): The type of body to which the arm is being added.
    - left_right (str): A string indicating which arm is being added. Valid values are 'left' and 'right'.
    - bend_direction (str): A string indicating the bend direction of the arm. Valid values are 'up', 'down' or 'none/straight'.

    Returns:
    - A tuple containing the location and bend angle of the arm as follows:
    - location (tuple): A tuple of 3 float values representing the x, y, and z coordinates of the arm's location on the body.
    - bend_angle (tuple): A tuple of 3 float values representing the up, down or  of the arm's bend angle.
    """

    if body_type == "sphere":
        radius = 4
    elif body_type == "horizontal_oblong":
        radius = 6
    elif body_type == "diamond":
        radius = 4
    elif body_type == "upfrustum" or body_type == "downfrustum" :
        radius = 4
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
    elif left_right == "front":
        if bend_direction == "up":
            location = (radius+1, 0 ,  0)
            bend_angle = (math.radians(-90), math.radians(180), math.radians(90))
        elif bend_direction == "down":
            location = (radius+1, 0,  0)
            bend_angle = (math.radians(-90), math.radians(360), math.radians(90))
        else:
            location = (radius+1, 0,  0)
            bend_angle = (0, math.radians(90), 0)
    elif left_right == "back":
        if bend_direction == "up":
            location = (-radius - 2, 0,  0)
            bend_angle = (math.radians(270), math.radians(180), math.radians(-90))
        elif bend_direction == "down":
            location = (-radius - 2,0,  0)
            bend_angle = (math.radians(270), math.radians(360), math.radians(-90))
        else:
            location = (-radius - 2, 0,  0)
            bend_angle = (0, math.radians(90), 0)

    return location, bend_angle


def addSingleArm(location, bend_angle, bend_direction, left_right, morph_angle):
    # create cone object
    bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=1, depth=4,vertices=16, location=location)
    bpy.context.object.name = "Arm"
    obj = bpy.data.objects['Arm']
    mod = obj.modifiers.new('Subsurf', 'SUBSURF')
    mod.subdivision_type = 'SIMPLE'
    mod.levels = 4  # Set the number of subdivisions
    mod.render_levels = 3  # Set the number of subdivisions to use for rendering

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.transform.resize(value=(1, 1, 2))
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.data.update()

    if bend_direction != 'none':
        modifier = obj.modifiers.new(
            name='Simple Deform', type='SIMPLE_DEFORM')
        modifier.deform_method = 'BEND'
        modifier.angle = math.radians(-90 + 180.0 * morph_angle)  # bend angle in degrees
        if (left_right == 'left' and bend_direction == 'up') or (left_right == 'right' and bend_direction == 'down'):
            modifier.limits[0] = 0.5
        else:
            modifier.limits[1] = 0.5
        # axis of the bend (can be 'X', 'Y', or 'Z')
        modifier.deform_axis = 'X'

    obj.rotation_euler = bend_angle  # Rotate 45 degrees around
    obj.update_tag()
    return

def addBeak(body_type, beak_size):
    if body_type == 'sphere':
        loc = (3,0,7)
    elif body_type == 'vertical_oblong':
        loc = (3,0,9)
    elif body_type == 'horizontal_oblong':
        loc = (3,0,7)
    elif body_type == 'cube':
        loc = (3,0,6.5)
    else:
        loc = (3,0,7)
    
    # create cylinder object
    bpy.ops.mesh.primitive_cone_add(radius1=0 + beak_size, radius2=2 - beak_size, depth=3,vertices=16, location=loc)
    bpy.context.object.name = "Beak"
    obj = bpy.data.objects['Beak']
    mod = obj.modifiers.new('Subsurf', 'SUBSURF')
    mod.subdivision_type = 'SIMPLE'
    mod.levels = 3  # Set the number of subdivisions
    mod.render_levels = 3  # Set the number of subdivisions to use for rendering



    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.transform.resize(value=(0.75, 0.75, 1))
    
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.data.update()
    
    obj.rotation_euler = (0, math.radians(90), 0)
    obj.update_tag()

def createUpFrustumMorph(rate = 1):
    
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=4-2*rate, radius2=4+2*rate, depth=9, location=(0, 0, 0))
    cone1 = bpy.context.object

    frustum = bpy.context.active_object
    bpy.context.view_layer.objects.active = frustum
    frustum.name = 'Body'
    return frustum, 'upfrustum'


def camera_light_action(name = None, dir = dir, camera = True, light = True, action = False,  center = [0,0,0]):
    # function for set camera, light and take png pics of quaddle
    if camera or light or action:
        # Compute Bounding Box
        bbox_corners = helperFunctions.calculate_collection_bbox("Collection")
        if bbox_corners is None:
            return "Collection not found"
        
        # Calculate center and size of the bounding box
        bbox_center = sum(bbox_corners, mathutils.Vector()) / len(bbox_corners)
        bbox_size = (
            max(c.x for c in bbox_corners) - min(c.x for c in bbox_corners),
            max(c.y for c in bbox_corners) - min(c.y for c in bbox_corners),
            max(c.z for c in bbox_corners) - min(c.z for c in bbox_corners)
        )
                     
    if camera:
        bpy.ops.object.camera_add(location=(0, 0, 0))
        bpy.context.object.name = "Camera"
        bpy.context.scene.render.resolution_x = 1440
        bpy.context.scene.render.resolution_y = 1440
        bpy.context.scene.render.resolution_percentage = 100
        bpy.context.object.delta_rotation_euler[0] = math.radians(90)
        cam_distance = max(bbox_size) * 2  # Example factor, might need adjustment
        bpy.data.objects["Camera"].location = ((bbox_center.x + cam_distance ) * 1.5, 0 , bbox_center.z )
#        cam_distance = 35
#        bpy.data.objects["Camera"].location = (bbox_center.x + cam_distance, 0, bbox_center.z)
        bpy.data.objects["Camera"].data.lens = 50
        bpy.data.objects["Camera"].rotation_euler = (math.radians(0), math.radians(90), math.radians(0))
        bpy.context.scene.camera = bpy.data.objects["Camera"]
    if light:
        light_data = bpy.data.lights.new(name="light_2.80", type='SUN')
        light_data.energy = 2
#        light_data.size = 10
        light_object = bpy.data.objects.new(name="light_2.80", object_data=light_data)
        bpy.context.collection.objects.link(light_object)
        bpy.context.view_layer.objects.active = light_object
        light_object.location = (100, 0, 0)
        
        light_object.rotation_euler = ( 0, math.radians(90),  0)
    if action:
        directory = dir + '/RenderPics/'
        if not os.path.exists(directory):
            os.makedirs(directory)
        if name == None:
            prefix = 'example'
        else:
            prefix = name
        extension = '.png'
        # count the number of existing example images in the directory
        count = sum(1 for filename in os.listdir(directory) if filename.startswith(prefix) and filename.endswith(extension))
        # set the filepath for the next example image
        filepath = f"{directory}{prefix}{count + 1:03d}{extension}"
        bpy.context.scene.render.filepath = filepath
        
#        bpy.context.scene.render.image_settings.compression = 15
        # Set render samples
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.samples = 16
        
        # render the image
        bpy.ops.render.render(write_still=True)
   
    bpy.data.objects.remove(bpy.context.scene.camera, do_unlink=True)

    # Remove all SunLight objects
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT' and obj.data.type == 'SUN':
            bpy.data.objects.remove(obj, do_unlink=True)
    
    bpy.ops.object.select_all(action='DESELECT')
    return "done"

def calculate_center(obj):
    # Get the bounding box of the object
    bbox_corners = [mathutils.Vector(corner) for corner in obj.bound_box]
    
    # Calculate the center of the bounding box in object's local coordinates
    local_center = sum(bbox_corners, mathutils.Vector()) / 8.0
    
    # Convert the center to world coordinates
    global_center = obj.matrix_world @ local_center
    
    return global_center




if __name__ == '__main__':
    
    # You can test morphing objects by modifying arm angle, body ratio, beak size, body pattern here:
    # === Morphing Configuration Parameters ===
    # Arm Angles
    arm_bend_angle = 0      # Range: 0 to 1 (right arm)
    arm_bend_angle2 = 0.25  # Range: 0 to 1 (left arm)
    arm_bend_angle3 = 1   # Range: 0 to 1 (back arm)

    # Beak Sizes and Ratios
    beak_size = 2          # Range: 0 to 2
    body_ratio = 1         # Range: 0 to 1
    body_pattern_angle = 15 # Range: 0, 15, 30, 45, 60, 75, 90
    
    # Input Patterns
    body_pattern = 'stripes_rotation_'+str(body_pattern_angle)+'.png'
    head_pattern = 'grid_05_08.png'
    fractal = 'F (5).png'

    # Base Paths
    base_path = dir
    pattern_path = os.path.join(base_path, 'Assets/morphing_patterns')
    head_pattern_path = os.path.join(base_path, 'Assets/patterns')
    fractal_path = os.path.join(base_path, 'Assets/fractals')
    
    
    # === File Paths ===
    
    # Input File Paths
    path1 = os.path.join(pattern_path, body_pattern)
    path2 = os.path.join(fractal_path, fractal)
    path3 = os.path.join(head_pattern_path, head_pattern)

    # Output Paths
    name = "MorphTesting"
    output_path = os.path.join(base_path, "Testing")
    export_path = os.path.join(output_path, "Stimuli")

    # === Scene Cleanup ===
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # === Object Creation ===
    # Create main body
    body, body_type = createUpFrustumMorph(body_ratio)
    addImageTextures.addTextureImageWithUVProject(body, "", path1, path2)

    # Create head
    head, head_type = addHead.createSphereHead(body_type)
    addImageTextures.addTextureSingleImage(head, head_type, path3)

    # === Texture Baking ===
    bakeImage.bake_material_to_new_uv_and_image(head, name, export_path)
    bakeImage.bake_material_to_new_uv_and_image(body, name, export_path)

    # === Add Features ===
    # Add beak
    addBeak(body_type, beak_size)

    # Add arms in different directions
    # Right arm
    addArms(body_type, 'right', ['up'], arm_bend_angle)
    # Front arm
    addArms(body_type, 'left', ['down'], arm_bend_angle2)
    # Back arm
    addArms(body_type, 'back', ['up'], arm_bend_angle3)

    # === Camera and Lighting Setup ===
    # Get object references
    body = bpy.data.objects.get("Body")
    head = bpy.data.objects.get("Head")

    # Calculate centers for camera positioning
    body_center = helperFunctions.calculate_center(body)
    head_center = helperFunctions.calculate_center(head)
    total_center = (body_center + head_center) / 2

    # Setup camera and lighting
    name = 'example_morphing_quaddle'
    export_path = os.path.join(base_path, 'morphImage')
    camera_light_action(name, export_path, True, True, True, total_center)

    # === Final Transformations ===
    scale_factor = 0.1     # For final object scaling
    rotation_angle = 90    # Degrees for Z-axis rotation
    # Scale down
    bpy.ops.object.select_all(action='SELECT')
    saved_location = body.location
    bpy.ops.transform.resize(value=(scale_factor,) * 3)
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
    bpy.ops.transform.translate(value=-saved_location)
    bpy.ops.object.select_all(action='DESELECT')

    # Rotate
    bpy.ops.object.select_all(action='SELECT')
    saved_location = body.location
    bpy.ops.transform.rotate(value=math.radians(rotation_angle), orient_axis='Z')
    bpy.ops.transform.translate(value=-saved_location)
    bpy.ops.object.select_all(action='DESELECT')

    # === Export ===
    # Select all mesh objects
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            obj.select_set(True)

    # Export as GLTF
    gltf_name = f"{name}.gltf"
    gltf_path = os.path.join(export_path, gltf_name)
    bpy.ops.export_scene.gltf(
        filepath=gltf_path, 
        export_format='GLTF_EMBEDDED',
        export_apply=True
    )

    # Cleanup selection
    bpy.ops.object.select_all(action='DESELECT')

    
    
    
    
    
