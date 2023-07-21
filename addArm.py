import bpy
import os
import sys
import math
import bmesh


def addArms(body_type, left_right, bend_directions):
    """
    Add arms to a body.

    Parameters:
    - body_type (str): The type of body to which the arms will be added.
    - left_right (str): A string indicating which arm or arms to add. Valid values are 'left', 'right', and 'both'.
    - bend_directions (list): A list of strings indicating the bend direction of each arm. Can be 'up', 'down' or 'none/straight'.
    """

    if left_right == 'both':
        location, bend_angle = calculate_locations(
            body_type, 'left', bend_directions[0])
        addSingleArm(location, bend_angle, bend_directions[0], 'left')
        location, bend_angle = calculate_locations(
            body_type, 'right', bend_directions[1])
        addSingleArm(location, bend_angle, bend_directions[1], 'right')
    else:
        location, bend_angle = calculate_locations(
            body_type, left_right, bend_directions[0])
        addSingleArm(location, bend_angle, bend_directions[0], left_right)


def calculate_locations(body_type, left_right, bend_direction):
    """
    Calculate the location and bend angle of an arm on a body.

    Parameters:
    - body_type (str): The type of body to which the arm is being added.
    - left_right (str): A string indicating which arm is being added. Valid values are 'left' and 'right'.
    - bend_direction (str): A string indicating the bend direction of the arm. Valid values are 'up', 'down' or 'none/straight'.

    Returns:
    - A tuple containing the location and bend angle of the arm as follows:
    - location (tuple): A tuple of 3 float values representing the x, y, and z coordinates of the arm's location on the body.
    - bend_angle (tuple): A tuple of 3 float values representing the up, down or  of the arm's bend angle.
    """

    if body_type == "sphere":
        radius = 4
    elif body_type == "horizontal_oblong":
        radius = 6
    elif body_type == "diamond":
        radius = 4
    elif body_type == "upfrustum" or body_type == "downfrustum" :
        radius = 4
    else:
        radius = 4

    if left_right == "right":
        if bend_direction == "up":
            location = (0, radius + 1, 0)
            bend_angle = (math.radians(90), 0, 0)
        elif bend_direction == "down":
            location = (0, radius + 1, 0)
            bend_angle = (math.radians(-90), 0, 0)
        else:
            location = (0, radius + 1, 0)
            bend_angle = (math.radians(90), 0, 0)
    elif left_right == "left":
        if bend_direction == "up":
            location = (0, -radius - 1,  0)
            bend_angle = (math.radians(90), 0, 0)
        elif bend_direction == "down":
            location = (0, -radius - 1,  0)
            bend_angle = (math.radians(-90), 0, 0)
        else:
            location = (0, -radius - 1,  0)
            bend_angle = (math.radians(90), 0, 0)

    return location, bend_angle


def addSingleArm(location, bend_angle, bend_direction, left_right):
    # create cone object
    bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=1, depth=4,vertices=16, location=location)
    bpy.context.object.name = "Arm"
    obj = bpy.data.objects['Arm']
    mod = obj.modifiers.new('Subsurf', 'SUBSURF')
    mod.subdivision_type = 'SIMPLE'
    mod.levels = 4  # Set the number of subdivisions
    mod.render_levels = 3  # Set the number of subdivisions to use for rendering

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.transform.resize(value=(1, 1, 2))
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.data.update()

    if bend_direction != 'none':
        modifier = obj.modifiers.new(
            name='Simple Deform', type='SIMPLE_DEFORM')
        modifier.deform_method = 'BEND'
        modifier.angle = math.radians(90.0)  # bend angle in degrees
        if (left_right == 'left' and bend_direction == 'up') or (left_right == 'right' and bend_direction == 'down'):
            modifier.limits[0] = 0.5
        else:
            modifier.limits[1] = 0.5
        # axis of the bend (can be 'X', 'Y', or 'Z')
        modifier.deform_axis = 'X'

    obj.rotation_euler = bend_angle  # Rotate 45 degrees around
    obj.update_tag()
    return
'''
def addSingleArm(location, bend_angle):
    # create cylinder object
    cube = bpy.ops.mesh.primitive_cube_add(location=location)
    bpy.context.object.name = "Arm"
    obj = bpy.data.objects['Arm']
    mod = obj.modifiers.new('Subsurf', 'SUBSURF')
    mod.levels = 3  # Set the number of subdivisions
    mod.render_levels = 3  # Set the number of subdivisions to use for rendering

    bpy.ops.object.mode_set(mode='EDIT')

    bpy.ops.transform.resize(value=(1, 1, 2))
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
    selectedEdges = [e for e in bm.edges if e.select]
    for e in selectedEdges:
        e[creaseLayer] = 1.0

    bpy.ops.object.mode_set(mode='OBJECT')
    obj.data.update()

    if bend_angle != (math.radians(90), 0, 0):
        modifier = obj.modifiers.new(
            name='Simple Deform', type='SIMPLE_DEFORM')
        modifier.deform_method = 'BEND'
        modifier.angle = math.radians(90.0)  # bend angle in degrees
        # axis of the bend (can be 'X', 'Y', or 'Z')
        modifier.deform_axis = 'X'

    obj.rotation_euler = bend_angle  # Rotate 45 degrees around
    obj.update_tag()
    return
'''
