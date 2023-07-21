import bpy
import os
import sys
#generate path
dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)


def createSphereHead(body_type):
    if body_type == 'sphere' or body_type == 'cube':
        loc = (0, 0, 7)
    elif body_type == 'vertical_oblong':
        loc = (0, 0, 9.5)
    elif body_type == 'horizontal_oblong':
        loc = (0, 0, 7)
    else:
        loc = (0, 0, 7)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=2.5, location=loc)
    head = bpy.context.active_object
    type = 'head_sphere'
    head.name = "Head"
    mod = head.modifiers.new('Subsurf', 'SUBSURF')
    mod.levels = 2  # Set the number of subdivisions
    mod.render_levels = 2  # Set the number of subdivisions to use for rendering
    return head, type

def createHorizontalOblongHead(body_type):
    if body_type == 'sphere' or body_type == 'cube':
        loc = (0, 0, 7)
    elif body_type == 'vertical_oblong':
        loc = (0, 0, 9.5)
    elif body_type == 'horizontal_oblong':
        loc = (0, 0, 7)
    else:
        loc = (0, 0, 7)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=2.5, location=loc)
    head = bpy.context.active_object
    bpy.ops.transform.resize(value=(1, 1.5, 1))
    type = 'head_horizontal_oblong'
    head.name = "Head"
    mod = head.modifiers.new('Subsurf', 'SUBSURF')
    mod.levels = 2  # Set the number of subdivisions
    mod.render_levels = 2  # Set the number of subdivisions to use for rendering
    return head, type

def createVerticalOblongHead(body_type):
    if body_type == 'sphere' or body_type =='cube':
        loc = (0, 0, 7.5)
    elif body_type == 'vertical_oblong':
        loc = (0, 0, 10)
    elif body_type == 'horizontal_oblong':
        loc = (0, 0, 7.5)
    else:
        loc = (0, 0, 7.5)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=2.5, location=loc)
    head = bpy.context.active_object
    bpy.ops.transform.resize(value=(1, 1, 1.3))
    type = 'head_vertical_oblong'
    head.name = "Head"
    mod = head.modifiers.new('Subsurf', 'SUBSURF')
    mod.levels = 2  # Set the number of subdivisions
    mod.render_levels = 2  # Set the number of subdivisions to use for rendering
    return head, type

def createCubeHead(body_type):
    if body_type == 'sphere' or body_type =='cube':
        loc = (0, 0, 7)
    elif body_type == 'vertical_oblong':
        loc = (0, 0, 9.5)
    elif body_type == 'horizontal_oblong':
        loc = (0, 0, 7)
    else:
        loc = (0, 0, 7)
        
    cube = bpy.ops.mesh.primitive_cube_add(location = loc, size = 4.75)
    bpy.context.object.name = "Head"
    
    obj = bpy.data.objects['Head']

    # Add a bevel modifier to the object
    bpy.ops.object.modifier_add(type='BEVEL')

    # Get the bevel modifier
    bevel_modifier = bpy.context.object.modifiers["Bevel"]

    # Set the width of the bevel
    bevel_modifier.width = 1
    bevel_modifier.segments = 3

    mod = obj.modifiers.new('Subsurf', 'SUBSURF')
    mod.levels = 2 # Set the number of subdivisions
    mod.render_levels = 1 # Set the number of subdivisions to use for rendering
    type = 'cube'
    return obj, type