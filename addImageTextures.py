import bpy
import os, sys, math
from PIL import Image

#print(os.getcwd())
#sys.path.insert(0, '/Users/wenxuan/Documents/Blender/')


def addTextureSingleImage(obj,type, path):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # Create two image textures and assign them to the sphere object
    tex1 = bpy.data.textures.new(name='Texture 1', type='IMAGE')

    tex1.image = bpy.data.images.load(path)

    mat = bpy.data.materials.new(name='Material')
    mat.use_nodes = True

    # Get the material's node tree
    nodes = mat.node_tree.nodes

    uv_map1 = nodes.new(type='ShaderNodeUVMap')
    uv_map1.name = 'UV Map 1'
    uv_map1.uv_map = 'UVMap'
    
    # Connect the UV maps to the image textures
    tex_node1 = nodes.new(type='ShaderNodeTexImage')
    tex_node1.image = tex1.image
    tex_node1.image.colorspace_settings.name = "Raw"
    
    mat.node_tree.links.new(uv_map1.outputs['UV'], tex_node1.inputs['Vector'])

    # Connect the output of the RGB mixer to the Material Output node
    mat.node_tree.links.new(nodes["Principled BSDF"].outputs['BSDF'], nodes["Material Output"].inputs['Surface'])


    mapping_node = nodes.new(type = 'ShaderNodeMapping')
    mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_node1.inputs['Vector'])
        
    tex_coord_node = mat.node_tree.nodes.new("ShaderNodeTexCoord")
    mat.node_tree.links.new(tex_coord_node.outputs['UV'], mapping_node.inputs['Vector'])

    # Connect the output of the RGB mixer to the base color input of the Principled BSDF node
    mat.node_tree.links.new(tex_node1.outputs['Color'], nodes["Principled BSDF"].inputs['Base Color'])
    mat.node_tree.links.new(tex_node1.outputs['Alpha'], nodes["Principled BSDF"].inputs['Alpha'])

    # Assign the material to the sphere object
    bpy.context.object.active_material = mat
    
    return


def addTextureImages(obj, type, path1, path2):

    
    # Create two image textures and assign them to the sphere object
    tex1 = bpy.data.textures.new(name='Texture 1', type='IMAGE')
    
    tex2 = bpy.data.textures.new(name='Texture 2', type='IMAGE')

    tex1.image = bpy.data.images.load(path1)
    tex2.image = bpy.data.images.load(path2)
    
    mat = bpy.data.materials.new(name='Material')
    mat.use_nodes = True

    # Get the material's node tree
    nodes = mat.node_tree.nodes
    
    uv_map1 = nodes.new(type='ShaderNodeUVMap')
    uv_map1.name = 'UV Map'
    uv_map1.uv_map = 'UVMap'
    
    uv_map2 = nodes.new(type='ShaderNodeUVMap')
    uv_map2.name = 'UV Map 1'
    uv_map2.uv_map = 'UVMap1'
    
    # Connect the UV maps to the image textures
    tex_node1 = nodes.new(type='ShaderNodeTexImage')
    tex_node1.image = tex1.image
    tex_node1.image.colorspace_settings.name = "Raw"
    
    mat.node_tree.links.new(uv_map1.outputs['UV'], tex_node1.inputs['Vector'])
     
    tex_node2 = nodes.new(type='ShaderNodeTexImage')
    tex_node2.image = tex2.image
    tex_node2.image.colorspace_settings.name = "Raw"
    mat.node_tree.links.new(uv_map2.outputs['UV'], tex_node2.inputs['Vector'])

    # Add a RGB mixer node
    rgb_mixer = nodes.new(type='ShaderNodeMixRGB')
    rgb_mixer.name = 'RGB Mixer'

    # Connect the output of the RGB mixer to the Material Output node
    mat.node_tree.links.new(nodes["Principled BSDF"].outputs['BSDF'], nodes["Material Output"].inputs['Surface'])

    mat.node_tree.links.new(tex_node1.outputs['Color'], rgb_mixer.inputs['Color1'])
    mat.node_tree.links.new(tex_node2.outputs['Color'], rgb_mixer.inputs['Color2'])
    mat.node_tree.links.new(tex_node2.outputs['Alpha'], rgb_mixer.inputs['Fac'])

    mapping_node = nodes.new(type = 'ShaderNodeMapping')
    
    if type == 'horizontal_oblong':
        mapping_node.inputs[1].default_value[0] = -0.5
        mapping_node.inputs[1].default_value[1] = 0.125
        mapping_node.inputs[3].default_value[0] = 2.0
        mapping_node.inputs[3].default_value[1] = 0.75
    elif type == 'vertical_oblong':
        mapping_node.inputs[1].default_value[0] = -0.25
        mapping_node.inputs[1].default_value[1] = -0.125
        mapping_node.inputs[3].default_value[0] = 1.5
        mapping_node.inputs[3].default_value[1] = 1.25
    elif type == 'cube':
        mapping_node.inputs[1].default_value[0] = 0.5
        mapping_node.inputs[1].default_value[1] = 0.25
        mapping_node.inputs[3].default_value[0] = 2
        mapping_node.inputs[3].default_value[1] = 2
        
    else:
        mapping_node.inputs[1].default_value[0] = -0.5
        mapping_node.inputs[3].default_value[0] = 2
   

    mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_node2.inputs['Vector'])

    tex_coord_node = mat.node_tree.nodes.new("ShaderNodeTexCoord")
    mat.node_tree.links.new(tex_coord_node.outputs['UV'], mapping_node.inputs['Vector'])

    # Connect the output of the RGB mixer to the base color input of the Principled BSDF node
    mat.node_tree.links.new(rgb_mixer.outputs['Color'], nodes["Principled BSDF"].inputs['Base Color'])

    # Assign the material to the sphere object
    bpy.context.object.active_material = mat
    
    return

def addSingleTextureImageWithUVProject(obj, type, path):
    # UV project modifier for the sphere
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # Connect projector to UV project modifier
    bpy.ops.object.modifier_add(type='UV_PROJECT')
    modifier = obj.modifiers[-1]
    modifier.name = "UVProject"
    
    # Add a new image texture to the obj
    obj_material = bpy.data.materials.new(name="Obj_Material")
    obj.data.materials.append(obj_material)
    obj_material.use_nodes = True
    obj_bsdf = obj_material.node_tree.nodes.get('Principled BSDF')

    obj_image_texture = obj_material.node_tree.nodes.new(type="ShaderNodeTexImage")
    obj_image_texture.location = (-600, 300)
    obj_image_texture.image = bpy.data.images.load(path)  # Replace with your image path
    obj_image_texture.image.colorspace_settings.name = "Raw"
    uv_node = obj_material.node_tree.nodes.new('ShaderNodeUVMap')
    uv_node.location = (-800, 300)
    uv_node.uv_map = "UVMap"

    # Set up projector
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    projector = bpy.context.active_object
    projector.delta_rotation_euler[1] = math.radians(90)
    projector.delta_scale = (6, 6, 1)

    modifier.projectors[0].object = projector
    modifier.uv_layer = "UVMap"

    # Connect the texture node to the UV mapping node
    obj_material.node_tree.links.new(obj_image_texture.outputs['Color'], obj_bsdf.inputs['Base Color'])
    obj_material.node_tree.links.new(uv_node.outputs['UV'], obj_image_texture.inputs['Vector'])
    bpy.ops.object.select_all(action='DESELECT')
    return
    
def addTextureImageWithUVProject(obj, type, path1, path2):
    # UV project modifier for the sphere
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # Connect projector to UV project modifier
    bpy.ops.object.modifier_add(type='UV_PROJECT')
    modifier1 = obj.modifiers[-1]
    modifier1.name = "UVProject1"
    bpy.ops.object.modifier_add(type='UV_PROJECT')
    modifier2 = obj.modifiers[-1]
    
    # Add a new image texture to the obj
    obj_material = bpy.data.materials.new(name="Obj_Material")
    obj.data.materials.append(obj_material)
    obj_material.use_nodes = True
    obj_bsdf = obj_material.node_tree.nodes.get('Principled BSDF')

    mixer_node = obj_material.node_tree.nodes.new(type='ShaderNodeMixRGB')
    mixer_node.location = (-250, 150)

    obj_image_texture = obj_material.node_tree.nodes.new(type="ShaderNodeTexImage")
    obj_image_texture.location = (-600, 300)
    
        
    obj_image_texture_2 = obj_material.node_tree.nodes.new(type="ShaderNodeTexImage")
    obj_image_texture_2.location = (-600, 0)
    obj.data.uv_layers.new(name="Frac_UVMap")

    obj_image_texture.image = bpy.data.images.load(path1)  # Replace with your image path
    obj_image_texture_2.image = bpy.data.images.load(path2)
    obj_image_texture.image.colorspace_settings.name = "Raw"
    obj_image_texture_2.image.colorspace_settings.name = "Raw"

    uv_node = obj_material.node_tree.nodes.new('ShaderNodeUVMap')
    uv_node.location = (-800, 300)
    uv_node.uv_map = "Frac_UVMap"

    uv_node_2 = obj_material.node_tree.nodes.new('ShaderNodeUVMap')
    uv_node_2.location = (-800, 0)
    uv_node_2.uv_map = "Frac_UVMap"

    # Set up projector
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    projector = bpy.context.active_object
    projector.delta_rotation_euler[1] = math.radians(90)
    projector.delta_scale = (6, 6, 1)

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    projector2 = bpy.context.active_object
    projector2.delta_location = (10,0,0)
    projector2.delta_rotation_euler[1] = math.radians(90)
    projector2.delta_scale = (7, 7, 1)


    modifier2.name = "UVProject2"
    modifier1.projectors[0].object  = projector
    modifier1.uv_layer = "UVMap"
    modifier2.projectors[0].object  = projector2
    modifier2.uv_layer = "Frac_UVMap"

    # Connect the texture node to the UV mapping node
    obj_material.node_tree.links.new(obj_image_texture.outputs['Color'], mixer_node.inputs['Color1'])
    obj_material.node_tree.links.new(obj_image_texture_2.outputs['Color'], mixer_node.inputs['Color2'])
    obj_material.node_tree.links.new(obj_image_texture_2.outputs['Alpha'], mixer_node.inputs['Fac'])
    obj_material.node_tree.links.new(mixer_node.outputs['Color'], obj_bsdf.inputs['Base Color'])
    obj_material.node_tree.links.new(uv_node.outputs['UV'], obj_image_texture.inputs['Vector'])
    obj_material.node_tree.links.new(uv_node_2.outputs['UV'], obj_image_texture_2.inputs['Vector'])
    bpy.ops.object.select_all(action='DESELECT')
    return 

if __name__ == '__main__':
    print("Testing here")
    bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    cube = bpy.context.active_object

    # Create a sphere on top of the cube
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, enter_editmode=False, align='WORLD', location=(0, 0, 2))
    sphere = bpy.context.active_object
    
    background = '/Users/wenxuan/Documents/Blender/Assets/Patterns and Colours/Pattern(Solid)+Colour(7070014_7070014).png'
    fractal = '/Users/wenxuan/Documents/Blender/Assets/Fractals_old/Transparent/1200x1200/F (1).png'
    
    addTextureImageWithUVProject(cube, "", background, fractal)