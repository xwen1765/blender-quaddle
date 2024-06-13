import bpy
import os, sys
sys.path.insert(0, '/Users/wenxuan/Documents/Blender/')
from mathutils import Matrix
import math, random
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


def addobject():
    # Create a new mesh object and link it to the scene
    mesh = bpy.data.meshes.new("diamond")
    obj = bpy.data.objects.new("diamond", mesh)

    scene = bpy.context.scene
    scene.collection.objects.link(obj)
    size = 5
    # Create a bmesh object to build the diamond geometry
    bm = bmesh.new()

    # Create the top and bottom vertices
    top_vertex = bm.verts.new((0, 0, size))
    bottom_vertex = bm.verts.new((0, 0, -size))

    # Create the four side vertices
    side_vertices = [
        bm.verts.new((size, 0, 0)),
        bm.verts.new((0, size, 0)),
        bm.verts.new((-size, 0, 0)),
        bm.verts.new((0, -size, 0)),
    ]

    # Create the faces
    for i in range(4):
        bm.faces.new((top_vertex, side_vertices[i], side_vertices[(i + 1) % 4]))
        bm.faces.new((bottom_vertex, side_vertices[i], side_vertices[(i + 1) % 4]))

    # Update the mesh with the new geometry and free the bmesh
    bm.to_mesh(mesh)
    bm.free()

    # Set shading mode to smooth
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()
    return obj

def bake_material_to_new_uv_and_image(obj, image_name, image_size, bake_type='DIFFUSE'):
    # Create a new UV map
    new_uv_map = obj.data.uv_layers.new(name="Bake_UV")
    new_uv_map.active_render = True


    # Create a new image
    image = bpy.data.images.new(image_name, width=image_size, height=image_size)

    # Get the object's material
    material = obj.data.materials[0]
    nodes = material.node_tree.nodes

    # Create a new Image Texture node
    image_texture_node = nodes.new(type="ShaderNodeTexImage")
    image_texture_node.image = image

    # Connect the new Image Texture node to the Principled BSDF node
    principled_bsdf_node = next(node for node in nodes if node.type == 'BSDF_PRINCIPLED')
   

    # Set the active UV map for baking
    obj.data.uv_layers.active = new_uv_map

    # Set bake settings and bake
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.bake_type = bake_type
    bpy.context.scene.render.bake.use_selected_to_active = False
    
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    for node in nodes:
        node.select = False
    image_texture_node.select = True
    nodes.active = image_texture_node

    bpy.ops.object.bake(type = bake_type)
    
    material.node_tree.links.new(image_texture_node.outputs['Color'], principled_bsdf_node.inputs['Base Color'])
        
if __name__ == '__main__':
    # clear previous scene
    bpy.ops.object.mode_set(mode='OBJECT')
    helperFunctions.reset_scene()
    randomImage1 = helperFunctions.chooseRandomImage('/Users/wenxuan/Documents/Blender/Assets/Patterns and Colours/')
    randomImage2 = helperFunctions.chooseRandomImage('/Users/wenxuan/Documents/Blender/Assets/Patterns and Colours/')
    dir = '/Users/wenxuan/Documents/Blender/Assets/Patterns and Colours/'
    randomImage3 = helperFunctions.chooseRandomImage('/Users/wenxuan/Documents/Blender/Assets/Fractals_old/Transparent/1200x1200/')
    frac_dic = "/Users/wenxuan/Documents/Blender/Assets/Fractals_old/Transparent/1200x1200/" +randomImage3
    # Create a cube
    bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    cube = bpy.context.active_object

    # Create a sphere on top of the cube
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, enter_editmode=False, align='WORLD', location=(0, 0, 2))
    sphere = bpy.context.active_object

    # Add image texture to the cube
    cube_material = bpy.data.materials.new(name="Cube_Material")
    cube.data.materials.append(cube_material)
    cube_material.use_nodes = True
    cube_bsdf = cube_material.node_tree.nodes.get('Principled BSDF')
    image_texture = cube_material.node_tree.nodes.new(type="ShaderNodeTexImage")
    image_texture.location = (-300, 300)
    image_texture.image = bpy.data.images.load(dir+randomImage1)  # Replace with your image path
    cube_material.node_tree.links.new(image_texture.outputs['Color'], cube_bsdf.inputs['Base Color'])

    # UV project modifier for the sphere
    bpy.ops.object.select_all(action='DESELECT')
    sphere.select_set(True)
    bpy.context.view_layer.objects.active = sphere
    # Connect projector to UV project modifier
    bpy.ops.object.modifier_add(type='UV_PROJECT')
    modifier1 = sphere.modifiers[-1]
    modifier1.name = "UVProject1"
    bpy.ops.object.modifier_add(type='UV_PROJECT')
    modifier2 = sphere.modifiers[-1]
    
    # Add a new image texture to the sphere
    sphere_material = bpy.data.materials.new(name="Sphere_Material")
    sphere.data.materials.append(sphere_material)
    sphere_material.use_nodes = True
    sphere_bsdf = sphere_material.node_tree.nodes.get('Principled BSDF')
    
    mixer_node = sphere_material.node_tree.nodes.new(type='ShaderNodeMixRGB')
    mixer_node.location = (-250, 150)
    
    sphere_image_texture = sphere_material.node_tree.nodes.new(type="ShaderNodeTexImage")
    sphere_image_texture.location = (-600, 300)
    sphere_image_texture_2 = sphere_material.node_tree.nodes.new(type="ShaderNodeTexImage")
    sphere_image_texture_2.location = (-600, 0)
    sphere.data.uv_layers.new(name="Frac_UVMap")
    
    sphere_image_texture.image = bpy.data.images.load(dir+randomImage2)  # Replace with your image path
    sphere_image_texture_2.image = bpy.data.images.load(frac_dic)
    
    
    uv_node = sphere_material.node_tree.nodes.new('ShaderNodeUVMap')
    uv_node.location = (-800, 300)
    uv_node.uv_map = "UVMap"
    
    uv_node_2 = sphere_material.node_tree.nodes.new('ShaderNodeUVMap')
    uv_node_2.location = (-800, 0)
    uv_node_2.uv_map = "Frac_UVMap"
    
    # Set up projector
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    projector = bpy.context.active_object
    projector.delta_rotation_euler[1] = math.radians(90)
    projector.delta_scale = (2, 2, 1)
    
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    projector2 = bpy.context.active_object
    projector2.delta_location = (4,0,2)
    projector2.delta_rotation_euler[1] = math.radians(90)
    projector2.delta_scale = (2, 2, 1)
        
    
    modifier2.name = "UVProject2"
    modifier1.projectors[0].object  = projector
    modifier1.uv_layer = "UVMap"
    modifier2.projectors[0].object  = projector2
    modifier2.uv_layer = "Frac_UVMap"
    
    # Connect the texture node to the UV mapping node
    sphere_material.node_tree.links.new(sphere_image_texture.outputs['Color'], mixer_node.inputs['Color1'])
    sphere_material.node_tree.links.new(sphere_image_texture_2.outputs['Color'], mixer_node.inputs['Color2'])
    sphere_material.node_tree.links.new(sphere_image_texture_2.outputs['Alpha'], mixer_node.inputs['Fac'])
    sphere_material.node_tree.links.new(mixer_node.outputs['Color'], sphere_bsdf.inputs['Base Color'])
    sphere_material.node_tree.links.new(uv_node.outputs['UV'], sphere_image_texture.inputs['Vector'])
    sphere_material.node_tree.links.new(uv_node_2.outputs['UV'], sphere_image_texture_2.inputs['Vector'])
    
    bake_material_to_new_uv_and_image(sphere, "Baked_Texture", 512)

        
      
#    randomImage1 = helperFunctions.chooseRandomImage('/Users/wenxuan/Documents/Blender/Assets/Patterns and Colours/')
#    randomImage3 = helperFunctions.chooseRandomImage('/Users/wenxuan/Documents/Blender/Assets/Patterns and Colours/')
#    randomImage2 = helperFunctions.chooseRandomImage('/Users/wenxuan/Documents/Blender/Assets/Fractals_old/Transparent/1200x1200/')
#    # Delete all objects in the scene
#    bpy.ops.object.select_all(action='SELECT')
#    bpy.ops.object.delete()

#    # Create a new sphere
#    body, body_type = createObject.createSphere()
#    path1 = '/Users/wenxuan/Documents/Blender/Assets/Patterns and Colours/' + randomImage1
#    path2 = '/Users/wenxuan/Documents/Blender/Assets/Fractals_old/Transparent/1200x1200/' + randomImage2
#    
##    path_white = "/Users/wenxuan/Documents/Blender/Assets/Patterns and Colours/Pattern(Solid)+Colour(9900000_9900000).png"
#    addImageTextures.addTextureImages(body, body_type, path1, path2)

#    
#    path3 = '/Users/wenxuan/Documents/Blender/Assets/Patterns and Colours/' + randomImage3
#    head, headtype = addHead.createSphereHead(body_type)
#    addImageTextures.addTextureSingleImage(head,headtype, path3)
#    
#    helperFunctions.camera_light_action(camera = True, light = False, action = True)
#    
#    
##    fbx_name = "fbx3"
##    export_path = "/Users/wenxuan/Documents/Blender/"
##    bakeImage.bake_texture(fbx_name, export_path)
#    
#    addBeak.addBeak(body_type)
#    
#    # define the possible values for left_right and bend_directions
#    left_right_options = ['left', 'right', 'both']
#    bend_direction_options = ['up', 'down', 'none']
#    # generate a random value for left_right and bend_directions
#    left_right = random.choice(left_right_options)
#    bend_directions = [random.choice(bend_direction_options) for _ in range(2)]

#    addArm.addArms(body_type, left_right, bend_directions)
##    
#    # place light, camera and see if render is needed
#    camera_light_action()
#    
#    # export everything to fbx
#    bakeImage.export_fbx(fbx_name, export_path)
    
    
    
    
    
