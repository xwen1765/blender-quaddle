import bpy
import os, sys
from PIL import Image

print(os.getcwd())
sys.path.insert(0, '/Users/wenxuan/Documents/Blender/')

def addTextureTwoImages(obj,type, fractal, background):
    result_img = combine_images(fractal, background)
    addTextureSingleImage(obj, type, result_img)
    

def combine_images(fractal, background):
    script_path = sys.path[0]
    # Open the first image
    img1 = Image.open(fractal).convert("RGBA")
    # Open the second image
    img2 = Image.open(background).convert("RGBA")
    # Resize both images to 1200x1200
    img1 = img1.resize((1200,1200))
    img2 = img2.resize((1200,1200))
    
    # Create a new image with the same size as the first image
    result_img = Image.new("RGBA", img1.size, (0, 0, 0, 0))
    result_img.paste(img2, (0, 0), img2)
    result_img.paste(img1, (0, 0), img1)
    result_img.save(script_path + "/temp.png")
    return script_path + "/temp.png"

def addTextureSingleImage(obj,type, path):
    # Create two image textures and assign them to the sphere object
    tex1 = bpy.data.textures.new(name='Texture 1', type='IMAGE')

    tex1.image = bpy.data.images.load(path)

    mat = bpy.data.materials.new(name='Material')
    mat.use_nodes = True

    # Get the material's node tree
    nodes = mat.node_tree.nodes

    # Create two UV maps
    uv_texture1 = bpy.ops.mesh.uv_texture_add()

    uv_map1 = nodes.new(type='ShaderNodeUVMap')
    uv_map1.name = 'UV Map 1'
    uv_map1.uv_map = 'UVMap'
    
    # Connect the UV maps to the image textures
    tex_node1 = nodes.new(type='ShaderNodeTexImage')
    tex_node1.image = tex1.image

    mat.node_tree.links.new(uv_map1.outputs['UV'], tex_node1.inputs['Vector'])

    # Connect the output of the RGB mixer to the Material Output node
    mat.node_tree.links.new(nodes["Principled BSDF"].outputs['BSDF'], nodes["Material Output"].inputs['Surface'])


    mapping_node = nodes.new(type = 'ShaderNodeMapping')
    mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_node1.inputs['Vector'])

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
    else:
        mapping_node.inputs[1].default_value[0] = -0.5
        mapping_node.inputs[3].default_value[0] = 2
        
    tex_coord_node = mat.node_tree.nodes.new("ShaderNodeTexCoord")
    mat.node_tree.links.new(tex_coord_node.outputs['UV'], mapping_node.inputs['Vector'])

    # Connect the output of the RGB mixer to the base color input of the Principled BSDF node
    mat.node_tree.links.new(tex_node1.outputs['Color'], nodes["Principled BSDF"].inputs['Base Color'])
    mat.node_tree.links.new(tex_node1.outputs['Alpha'], nodes["Principled BSDF"].inputs['Alpha'])

    # Assign the material to the sphere object
    bpy.context.object.active_material = mat


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

    # Create two UV maps
    uv_texture1 = bpy.ops.mesh.uv_texture_add()
    uv_texture2 = bpy.ops.mesh.uv_texture_add()

    uv_map1 = nodes.new(type='ShaderNodeUVMap')
    uv_map1.name = 'UV Map 1'
    uv_map1.uv_map = 'UVMap.001'
    uv_map2 = nodes.new(type='ShaderNodeUVMap')
    uv_map2.name = 'UV Map 2'
    uv_map2.uv_map = 'UVMap'

    # Connect the UV maps to the image textures
    tex_node1 = nodes.new(type='ShaderNodeTexImage')
    tex_node1.image = tex1.image
    tex_node2 = nodes.new(type='ShaderNodeTexImage')
    tex_node2.image = tex2.image

    mat.node_tree.links.new(uv_map1.outputs['UV'], tex_node1.inputs['Vector'])
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
    
if __name__ == '__main__':
    print("Testing here")
    background = '/Users/wenxuan/Documents/Blender/Assets/Patterns and Colours/Pattern(Solid)+Colour(7070014_7070014).png'
    fractal = '/Users/wenxuan/Documents/Blender/Assets/Fractals/Transparent/1200x1200/F (1).png'
    result_img = combine_images(fractal, background)