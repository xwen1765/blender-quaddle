import bpy, bmesh
import os, sys, importlib, math
sys.path.insert(0, '/Users/wenxuan/Documents/Blender/')
import helperFunctions
from mathutils import Matrix
importlib.reload(helperFunctions)

def createSphere():
    bpy.ops.mesh.primitive_uv_sphere_add(radius=5.0, location = (0,0,0))
    sphere = bpy.context.active_object
    type = 'sphere'
    sphere.name = "Body"
    mod = sphere.modifiers.new('Subsurf', 'SUBSURF')
    mod.levels = 2 # Set the number of subdivisions
    mod.render_levels = 1 # Set the number of subdivisions to use for rendering

    return sphere, type;

def createVerticalOblong():
    bpy.ops.mesh.primitive_uv_sphere_add(radius=5.0, location = (0,0,0))
    sphere = bpy.context.active_object
    bpy.ops.transform.resize(value=(1, 1, 1.5))
    type = 'vertical_oblong'
    sphere.name = "Body"
    mod = sphere.modifiers.new('Subsurf', 'SUBSURF')
    mod.levels = 2 # Set the number of subdivisions
    mod.render_levels = 1 # Set the number of subdivisions to use for rendering
    # Apply the Subdivision Surface modifier
#    bpy.ops.object.modifier_apply(modifier='Subsurf')
    return sphere, type;

def createHorizontalOblong():
    bpy.ops.mesh.primitive_uv_sphere_add(radius=5.0, location = (0,0,0))
    sphere = bpy.context.active_object
    bpy.ops.transform.resize(value=(1, 1.5, 1))
    type = 'horizontal_oblong'
    sphere.name = "Body"
    mod = sphere.modifiers.new('Subsurf', 'SUBSURF')
    mod.levels = 2 # Set the number of subdivisions
    mod.render_levels = 1 # Set the number of subdivisions to use for rendering
    # Apply the Subdivision Surface modifier
#    bpy.ops.object.modifier_apply(modifier='Subsurf')
    return sphere, type;

def createCube():
    location = (0,0,0)
    bpy.ops.mesh.primitive_round_cube_add(location = location, size = (9,9,9),  radius=2, arc_div=4, lin_div=0)
    cube = bpy.context.active_object
    cube.name = "Body"
    type = 'cube'
    cube.data.uv_layers.new(name="UVMap")
    mod = cube.modifiers.new('Subsurf', 'SUBSURF')
    mod.levels = 2 # Set the number of subdivisions
    mod.render_levels = 1 # Set the number of subdivisions to use for rendering
    return cube, type;

def createDiamond():
    location = (0,0,0)
    cube = bpy.ops.mesh.primitive_cube_add(location = location, size = 12)
    bpy.context.object.name = "Body"
    
    obj = bpy.data.objects['Body']

    # Add a bevel modifier to the object
    bpy.ops.object.modifier_add(type='BEVEL')

    # Get the bevel modifier
    bevel_modifier = bpy.context.object.modifiers["Bevel"]

    # Set the width of the bevel
    bevel_modifier.width = 10
    bevel_modifier.segments = 1

    mod = obj.modifiers.new('Subsurf', 'SUBSURF')
    mod.levels = 3 # Set the number of subdivisions
    mod.render_levels = 1 # Set the number of subdivisions to use for rendering
    type = 'diamond'
    
    
    bpy.ops.object.select_all(action='SELECT')
    saved_location = obj.location
    bpy.ops.transform.rotate(value=math.radians(45), orient_axis='Z')
    bpy.ops.transform.translate(value=-saved_location)
    bpy.ops.transform.resize(value=(1, 1.5, 1))
    bpy.ops.object.select_all(action='DESELECT')
    
    return obj, type

def createCylinder(radius=4, depth=9, waist_factor=math.radians(120), waist_height=0.5):

    # Add a primitive cylinder
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth)
    cylinder = bpy.context.active_object
    cylinder.name = 'Body'

    return cylinder, 'cylinder'

def createUpFrustum():
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=6, radius2=2, depth=9, location=(0, 0, 0))
    frustum = bpy.context.active_object
    frustum.name = 'Body'
    return frustum, 'upfrustum'

def createDownFrustum():
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=2, radius2=6, depth=9, location=(0, 0, 0))
    frustum = bpy.context.active_object
    frustum.name = 'Body'
    return frustum, 'downfrustum'

if __name__ == '__main__':
    # clear previous scene
    helperFunctions.reset_scene()
    createDownFrustum()
    
    