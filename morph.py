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

def morphing(obj_one = None, target_object = None, morph_level = 0):
    # Get the objects from the scene by name

     # Remove any existing Geometry Nodes modifiers on obj_one
    for modifier in obj_one.modifiers:
        if modifier.type == "NODES":
            bpy.ops.object.modifier_remove({"object": obj_one}, modifier="GeoNodes")

    # Create a new Geometry Nodes modifier for the first object
    modifier_name = "GeoNodes"
    geo_nodes = obj_one.modifiers.new(name=modifier_name, type="NODES")

    # Set up Geometry Nodes
    tree = bpy.data.node_groups.new(modifier_name, "GeometryNodeTree")
    geo_nodes.node_group = tree

    # Add necessary nodes
    input_node = tree.nodes.new("NodeGroupInput")
    output_node = tree.nodes.new("NodeGroupOutput")
    subdivide = tree.nodes.new("GeometryNodeSubdivideMesh")
    subdivide.inputs[1].default_value = 3
    set_position = tree.nodes.new("GeometryNodeSetPosition")
    sample_nearest = tree.nodes.new("GeometryNodeSampleNearest")
    sample_index = tree.nodes.new("GeometryNodeSampleIndex")
    sample_index.data_type = 'FLOAT_VECTOR'
    join_geometry_node = tree.nodes.new("GeometryNodeJoinGeometry")
    position = tree.nodes.new("GeometryNodeInputPosition")
    mixer = tree.nodes.new("ShaderNodeMixRGB")
    mixer.inputs[0].default_value = morph_level
    object_info = tree.nodes.new("GeometryNodeObjectInfo")
    object_info.inputs[0].default_value = target_object
    
    # Position the nodes
    input_node.location = (-300, 300)
    join_geometry_node.location = (-100, 300)
    subdivide.location = (100, 300)
    set_position.location = (300, 300)
    output_node.location = (500, 300)
    sample_index.location = (-100, 100)
    sample_nearest.location = (-300, 100)
    object_info.location = (-500, 100)
    position.location = (-300, 200)
    mixer.location = (100, 100)
    
    
    # Link the nodes
    tree.links.new(input_node.outputs[0], join_geometry_node.inputs[0])
    tree.links.new(join_geometry_node.outputs["Geometry"], subdivide.inputs[0])
    tree.links.new(subdivide.outputs[0], set_position.inputs[0])
    tree.links.new(set_position.outputs[0], output_node.inputs[0])
    
    tree.links.new(object_info.outputs['Geometry'], sample_index.inputs['Geometry'])
    tree.links.new(object_info.outputs['Geometry'], sample_nearest.inputs['Geometry'])
    
    tree.links.new(position.outputs['Position'], sample_index.inputs[3])
    tree.links.new(sample_nearest.outputs['Index'], sample_index.inputs[6])
    
    tree.links.new(position.outputs['Position'], mixer.inputs['Color1'])
    tree.links.new(sample_index.outputs[2], mixer.inputs['Color2'])
    
    tree.links.new(mixer.outputs['Color'], set_position.inputs['Position'])
    tree.links.new(input_node.outputs[1], mixer.inputs[0])

    return

helperFunctions.reset_scene()

background = '/Users/wenxuan/Documents/Blender/Assets/patterns/grid_09_11.png'
fractal = '/Users/wenxuan/Documents/Blender/Assets/fractals/F (32).png'
export = '/Users/wenxuan/Documents/Blender/TwoTesting'
bpy.ops.mesh.primitive_cube_add(size=5, enter_editmode=False, align='WORLD', location=(0, 0, 0))
cube = bpy.context.active_object
## Create a sphere on top of the cube
bpy.ops.mesh.primitive_uv_sphere_add(radius=2.5, enter_editmode=False, align='WORLD', location=(0, 0, 5))
#createObject.createVerticalOblong()
sphere = bpy.context.active_object
sphere.location = (0,0,12)


#addImageTextures.addTextureImageWithUVProject(cube, "", background, fractal)
addImageTextures.addTextureSingleImage(sphere, "sphere", background)
addImageTextures.addTextureSingleImage(cube, "sphere", background)

morphing(sphere, cube, 1)




#bakeImage.bake_material_to_new_uv_and_image(cube, "Testing", export)
#bakeImage.bake_material_to_new_uv_and_image(sphere, "Testing", export)

def printout(name):
    filter = []
    for t in dir(bpy.types):
        if t.startswith("GeometryNode"):
            if name in t:
                filter.append(t)
    print(filter)
printout('Object')