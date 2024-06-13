import bpy
import os, sys
import importlib
import random, math, mathutils

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)
    
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
import parser
importlib.reload(parser)
import helperFunctions
importlib.reload(helperFunctions)

#generate path
dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

def reset_scene():
    # delete everything in the editor
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    for material in bpy.data.materials:
        bpy.data.materials.remove(material)
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)
    for image in bpy.data.images:
        bpy.data.images.remove(image)
    for light in bpy.data.lights:
        bpy.data.lights.remove(light)
    bpy.ops.object.select_all(action='DESELECT')

def calculate_collection_bbox(collection_name):
    min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
    max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')
    
    collection = bpy.data.collections.get(collection_name)
    if not collection:
        return None  # Collection not found
    print(collection)
    # Iterate over all objects in the collection
    for obj in collection.objects:
        if obj.type == 'MESH':
            # Get all vertices of the object in world space
            world_vertices = [obj.matrix_world @ v.co for v in obj.data.vertices]
            
            # Update the min and max coordinates
            for v in world_vertices:
                min_x = min(min_x, v.x)
                min_y = min(min_y, v.y)
                min_z = min(min_z, v.z)
                max_x = max(max_x, v.x)
                max_y = max(max_y, v.y)
                max_z = max(max_z, v.z)
    
    # Create bounding box corners
    bbox_corners = [
        mathutils.Vector((min_x, min_y, min_z)),
        mathutils.Vector((max_x, min_y, min_z)),
        mathutils.Vector((max_x, max_y, min_z)),
        mathutils.Vector((min_x, max_y, min_z)),
        mathutils.Vector((min_x, min_y, max_z)),
        mathutils.Vector((max_x, min_y, max_z)),
        mathutils.Vector((max_x, max_y, max_z)),
        mathutils.Vector((min_x, max_y, max_z)),
    ]
    
    return bbox_corners

    
def camera_light_action(name = None, dir = dir, camera = True, light = True, action = False,  center = [0,0,0]):
    # function for set camera, light and take png pics of quaddle
    if camera or light or action:
        # Compute Bounding Box
        bbox_corners = calculate_collection_bbox("Collection")
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
        bpy.context.object.delta_rotation_euler[0] = math.radians(90)
        cam_distance = max(bbox_size) * 2  # Example factor, might need adjustment
        bpy.data.objects["Camera"].location = (bbox_center.x + cam_distance, 0, bbox_center.z)
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
        
        bpy.context.scene.render.resolution_percentage = 50
        bpy.context.scene.render.image_settings.compression = 15
        # Set render samples
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.samples = 16
        
        # render the image
        
        bpy.ops.render.render(write_still=True)
   
#    bpy.data.objects.remove(bpy.context.scene.camera, do_unlink=True)

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

def chooseRandomImage(directory):
    imgExtension = ["png", "jpeg", "jpg"]
    allImages = list()
    for img in os.listdir(directory): #Lists all files
        ext = img.split(".")[len(img.split(".")) - 1]
        if (ext in imgExtension):
            allImages.append(img)
    choice = random.randint(0, len(allImages) - 1)
    chosenImage = allImages[choice] #Do Whatever you want with the image file
    return chosenImage


if __name__ == '__main__':
    # clear previous scene
    reset_scene()
    
    randomImage1 = chooseRandomImage('/Users/wenxuan/Documents/Blender/Assets/patterns')
    randomImage3 = chooseRandomImage('/Users/wenxuan/Documents/Blender/Assets/patterns')
    randomImage2 = chooseRandomImage('/Users/wenxuan/Documents/Blender/Assets/fractals')
    # Delete all objects in the scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Create a new sphere
    body, body_type = createObject.createCube()
    path1 = '/Users/wenxuan/Documents/Blender/Assets/patterns/' + randomImage1
    path2 = '/Users/wenxuan/Documents/Blender/Assets/fractals/' + randomImage2
    
    addImageTextures.addTextureImageWithUVProject(body, body_type, path1, path2)

    path3 = '/Users/wenxuan/Documents/Blender/Assets/patterns/' + randomImage3
    head, headtype = addHead.createSphereHead(body_type)
    addImageTextures.addTextureSingleImage(head,headtype, path3)
    
    addArm.addArms(body_type, "right", ['down', 'down'])
    
    obj = bpy.data.objects.get("Body")
    if obj:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
    # Fetch the objects from the current scene
    body = bpy.data.objects.get("Body")
    head = bpy.data.objects.get("Head")
    total_center = calculate_center(body);
    if body and head:
        body_center = calculate_center(body)
        head_center = calculate_center(head)
        total_center = (body_center + head_center) / 2
        print(total_center)
    else:
        print("Either 'Body' or 'Head' object is not found in the scene")
    
    helperFunctions.reset_scene()
    # set default
    input_path = None
    output_path = dir
    test_set = [['3', '4', '9', '4', '4', '0', '0', '0', '0', '3', '2', '2', '1', '3', '1', '2', '0']]
    test_set = [[int(x) for x in test_set[0]]]
    test_name = generateName(test_set)
    for index in range(len(test_set)):
        name = "test" + "_" + test_name[index]
        generateQuaddle(test_set[index], name, dir, 'False', 'False')
    camera_light_action(camera = True, light = True, action = True, center = total_center)
    
    # Scale all selected objects down by a factor of 20
    bpy.ops.object.select_all(action='SELECT')
    saved_location = obj.location
    print(saved_location)
    bpy.ops.transform.resize(value=(0.05, 0.05, 0.05))
    bpy.context.scene.cursor.location = (0.0,0.0,0.0)
    bpy.ops.transform.translate(value=-saved_location)
    bpy.ops.object.select_all(action='DESELECT')
    
    bpy.ops.object.select_all(action='SELECT')
    saved_location = obj.location
    bpy.ops.transform.rotate(value=math.radians(90), orient_axis='Z')
    bpy.ops.transform.translate(value=-saved_location)
    bpy.ops.object.select_all(action='DESELECT')
    
#    bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(2, 2, 2))

    