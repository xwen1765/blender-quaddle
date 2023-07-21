import bpy
import os, sys
import importlib
import random, math

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
    
    
def camera_light_action(name = None, dir = dir, camera = True, light = True, action = False):
    # function for set camera, light and take png pics of quaddle
    if camera:
        bpy.ops.object.camera_add(location=(0, 0, 0))
        bpy.context.object.name = "Camera"
        bpy.context.scene.render.resolution_x = 720
        bpy.context.scene.render.resolution_y = 720
        bpy.context.object.delta_rotation_euler[0] = math.radians(90)
        bpy.data.objects["Camera"].location = (50, 0, 0)
        bpy.data.objects["Camera"].data.lens = 60.0
        bpy.data.objects["Camera"].rotation_euler = (math.radians(0), math.radians(90), math.radians(0))
        bpy.context.scene.camera = bpy.data.objects["Camera"]
    if light:
        light_data = bpy.data.lights.new(name="light_2.80", type='SUN')
        light_data.energy = 2
        light_object = bpy.data.objects.new(name="light_2.80", object_data=light_data)
        bpy.context.collection.objects.link(light_object)
        bpy.context.view_layer.objects.active = light_object
        light_object.location = (20, 0, 0)
        light_object.rotation_euler = (0, math.radians(90), 0)
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
   
    bpy.data.objects.remove(bpy.context.scene.camera, do_unlink=True)

    # Remove all SunLight objects
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT' and obj.data.type == 'SUN':
            bpy.data.objects.remove(obj, do_unlink=True)
    
    bpy.ops.object.select_all(action='DESELECT')
    return "done"

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
    
    randomImage1 = chooseRandomImage('/Users/wenxuan/Documents/Blender/Assets/Patterns and Colours/')
    randomImage3 = chooseRandomImage('/Users/wenxuan/Documents/Blender/Assets/Patterns and Colours/')
    randomImage2 = chooseRandomImage('/Users/wenxuan/Documents/Blender/Assets/Fractals_old/Transparent/1200x1200/')
    # Delete all objects in the scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Create a new sphere
    body, body_type = createObject.createSphere()
    path1 = '/Users/wenxuan/Documents/Blender/Assets/Patterns and Colours/' + randomImage1
    path2 = '/Users/wenxuan/Documents/Blender/Assets/Fractals_old/Transparent/1200x1200/' + randomImage2
    
    addImageTextures.addTextureImages(body, body_type, path1, path2)

    path3 = '/Users/wenxuan/Documents/Blender/Assets/Patterns and Colours/' + randomImage3
    head, headtype = addHead.createSphereHead(body_type)
    addImageTextures.addTextureSingleImage(head,headtype, path3)
    
#    addArm.addArms(body_type, "both", ['up', 'down'])
    
    obj = bpy.data.objects.get("Body")
    if obj:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
    
    
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
    
    bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(2, 2, 2))

#    camera_light_action(camera = True, light = True, action = True)