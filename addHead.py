import bpy
import os, sys
print(os.getcwd())
sys.path.insert(0, '/Users/wenxuan/Documents/Blender/')

def createSphereHead(body_type):
    if body_type == 'sphere':
        loc = (0,0,7)
    elif body_type == 'vertical_oblong':
        loc = (0,0,9)
    elif body_type == 'horizontal_oblong':
        loc = (0,0,7)
    elif body_type == 'cube':
        loc = (0,0,6.5)
    else:
        loc = (0,0,7)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=2.0, location =  loc)
    head = bpy.context.active_object
    type = 'head_sphere'
    mod = head.modifiers.new('Subsurf', 'SUBSURF')
    mod.levels = 2 # Set the number of subdivisions
    mod.render_levels = 2 # Set the number of subdivisions to use for rendering
    return head, type;