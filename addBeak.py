import bpy
import bmesh
import math

def addBeak(body_type):
    if body_type == 'sphere':
        loc = (3,0,7)
    elif body_type == 'vertical_oblong':
        loc = (3,0,9)
    elif body_type == 'horizontal_oblong':
        loc = (3,0,7)
    elif body_type == 'cube':
        loc = (3,0,6.5)
    else:
        loc = (3,0,7)
    
    # create cylinder object
    bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=1, depth=1,vertices=16, location=loc)
    bpy.context.object.name = "Beak"
    obj = bpy.data.objects['Beak']
    mod = obj.modifiers.new('Subsurf', 'SUBSURF')
    mod.subdivision_type = 'SIMPLE'
    mod.levels = 3  # Set the number of subdivisions
    mod.render_levels = 3  # Set the number of subdivisions to use for rendering



    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.transform.resize(value=(0.75, 0.75, 1))
    
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.data.update()
    
    obj.rotation_euler = (0, math.radians(90), 0)
    obj.update_tag()