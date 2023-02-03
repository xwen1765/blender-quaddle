import bpy
import os, sys
sys.path.insert(0, '/Users/wenxuan/Documents/Blender/')

def createSphere():
    bpy.ops.mesh.primitive_uv_sphere_add(radius=5.0, location = (0,0,0))
    sphere = bpy.context.active_object
    type = 'sphere'
    mod = sphere.modifiers.new('Subsurf', 'SUBSURF')
    mod.levels = 2 # Set the number of subdivisions
    mod.render_levels = 2 # Set the number of subdivisions to use for rendering

    return sphere, type;

def createVerticalOblong():
    bpy.ops.mesh.primitive_uv_sphere_add(radius=5.0, location = (0,0,0))
    sphere = bpy.context.active_object
    bpy.ops.transform.resize(value=(1, 1, 1.5))
    type = 'vertical_oblong'
    mod = sphere.modifiers.new('Subsurf', 'SUBSURF')
    mod.levels = 2 # Set the number of subdivisions
    mod.render_levels = 2 # Set the number of subdivisions to use for rendering

    return sphere, type;

def createHorizontalOblong():
    bpy.ops.mesh.primitive_uv_sphere_add(radius=5.0, location = (0,0,0))
    sphere = bpy.context.active_object
    bpy.ops.transform.resize(value=(1, 1.5, 1))
    type = 'horizontal_oblong'
    mod = sphere.modifiers.new('Subsurf', 'SUBSURF')
    mod.levels = 2 # Set the number of subdivisions
    mod.render_levels = 2 # Set the number of subdivisions to use for rendering

    return sphere, type;

def createCube():
    location = (0,0,0)
    cube = bpy.ops.mesh.primitive_cube_add(location = location, size = 9)
    bpy.context.object.name = "Cube"
    obj = bpy.data.objects['Cube']


    # Add a bevel modifier to the object
    bpy.ops.object.modifier_add(type='BEVEL')

    # Get the bevel modifier
    bevel_modifier = bpy.context.object.modifiers["Bevel"]

    # Set the width of the bevel
    bevel_modifier.width = 1
    bevel_modifier.segments = 10

    mod = obj.modifiers.new('Subsurf', 'SUBSURF')
    mod.levels = 2 # Set the number of subdivisions
    mod.render_levels = 1 # Set the number of subdivisions to use for rendering
    type = 'cube'
    return obj, type
