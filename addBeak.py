import bpy
import bmesh
import math

def addBeak(body_type):
    if body_type == 'sphere':
        loc = (2,0,7)
    elif body_type == 'vertical_oblong':
        loc = (2,0,9)
    elif body_type == 'horizontal_oblong':
        loc = (2,0,7)
    elif body_type == 'cube':
        loc = (2,0,6.5)
    else:
        loc = (2,0,7)
    
    # create cylinder object
    cube = bpy.ops.mesh.primitive_cube_add(location = loc)
    bpy.context.object.name = "Cube"
    obj = bpy.data.objects['Cube']
    mod = obj.modifiers.new('Subsurf', 'SUBSURF')
    mod.levels = 5 # Set the number of subdivisions
    mod.render_levels = 5 # Set the number of subdivisions to use for rendering

    bpy.ops.object.mode_set(mode='EDIT')
    
    bpy.ops.transform.resize(value=(0.5, 0.5, 1))
    me = bpy.context.active_object.data
    bm = bmesh.from_edit_mesh(me)
    for face in bm.faces:
        if abs(face.normal.z) < 0.99:
            face.select = False
    for face in bm.faces:
        if face.select:
            for edge in face.edges:
                edge.select == True
        else:
            for edge in face.edges:
                edge.select == False
                
    creaseLayer = bm.edges.layers.crease.verify()
    selectedEdges = [ e for e in bm.edges if e.select ]
    for e in selectedEdges: e[ creaseLayer ] = 1.0
    
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.data.update()
    
    obj.rotation_euler = (0, math.radians(90), 0)
    obj.update_tag()