import bpy
import os, sys
sys.path.insert(0, '/Users/wenxuan/Documents/Blender/')
from mathutils import Matrix
import math
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

import random
imgExtension = ["png", "jpeg", "jpg"] #Image Extensions to be chosen from
allImages = list()
def chooseRandomImage(directory):
    allImages = list()
    for img in os.listdir(directory): #Lists all files
        ext = img.split(".")[len(img.split(".")) - 1]
        if (ext in imgExtension):
            allImages.append(img)
    choice = random.randint(0, len(allImages) - 1)
    chosenImage = allImages[choice] #Do Whatever you want with the image file
    return chosenImage


if __name__ == '__main__':
    
    randomImage1 = chooseRandomImage('/Users/wenxuan/Documents/Blender/Assets/Patterns and Colours/')
    randomImage3 = chooseRandomImage('/Users/wenxuan/Documents/Blender/Assets/Patterns and Colours/')
    randomImage2 = chooseRandomImage('/Users/wenxuan/Documents/Blender/Assets/Fractals/Transparent/1200x1200/')
    # Delete all objects in the scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Create a new sphere
#    body, body_type = createObject.createSphere()
    body, body_type = createObject.createSphere()
    print(body_type)
    print(body_type)
    path1 = '/Users/wenxuan/Documents/Blender/Assets/Patterns and Colours/' + randomImage1
    path2 = '/Users/wenxuan/Documents/Blender/Assets/Fractals/Transparent/1200x1200/' + randomImage2
    addImageTextures.addTextureTwoImages(body, body_type, path2, path1)
    
    left_right = 'both'
    bend_directions = ['down', 'up']
    addArm.addArms(body_type, left_right, bend_directions)
    
    path3 = '/Users/wenxuan/Documents/Blender/Assets/Patterns and Colours/' + randomImage3
    head, headtype = addHead.createSphereHead(body_type)
    addImageTextures.addTextureSingleImage(head,headtype, path3)
    
    addBeak.addBeak(body_type)
    
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    bpy.context.object.name = "Camera"
    bpy.data.objects["Camera"].location = (50, 0, 0)
    bpy.data.objects["Camera"].rotation_euler = (0, math.radians(90), 0)
    bpy.context.scene.camera = bpy.data.objects["Camera"]
    
    light_data = bpy.data.lights.new(name="light_2.80", type='SUN')
    light_data.energy = 1
    light_object = bpy.data.objects.new(name="light_2.80", object_data=light_data)
    bpy.context.collection.objects.link(light_object)
    bpy.context.view_layer.objects.active = light_object
    light_object.location = (20, 0, 0)
    light_object.rotation_euler = (0, math.radians(90), 0)
    

    bpy.context.scene.render.filepath = '/Users/wenxuan/Documents/Blender/example9.png'
    bpy.ops.render.render(write_still=True)
    
