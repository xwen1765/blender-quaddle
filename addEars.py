import bpy
import os
import sys
import math
import bmesh

# ear traits
# earType: normal, flared, blunt
# earLength: long, normal, short
# position: left, right, both

# notes
# calculateDistance is incomplete
# height is currently set to 0 due to lack of measurements


# calculates how far apart the ears should be depending on the head type
def calculateDistance(earLength, head_type):
    if head_type == "head_sphere" or head_type == "head_vertical_oblong":
        return 2.3 + earLength/2
    elif head_type == "head_horizontal_oblong":
        return 3.5 + earLength/2
    else:
        return 2.3 + earLength/2
        
    


# determines the location and number of ears based on input
def addEars(earType, earLength, position, head_type, body_type):

    height = 7  # how far off the ears are from the ground
    if body_type == "vertical_oblong":
        height = 9
    size = 0.5  # center radius of ears
    length = 1.5  # length of ears

    # earLength can be normal, short, or long
    if earLength == "short":
        length = 1
    if earLength == "long":
        length = 3

    # how far apart the ears are from the center
    dist = calculateDistance(length, head_type)

    # ear types are straight, blunt, and flared
    if position == "left" or position == "both":
        loc = (0, -dist, height)
        makeEar(earType, size, length, loc, "left")
    if position == "right" or position == "both":
        loc = (0, dist, height)
        makeEar(earType, size, length, loc, "right")


# generates a single ear in the correct location
def makeEar(earType, size, length, loc, orientation):

    # determine end radiuses depending on type
    r1 = r2 = size
    if earType == "flared":
        r1 *= 2
        r2 *= 0.5
    if earType == "blunt":
        r1 *= 0.5
        r2 *= 2

    # rotate ear depending on side of the head
    rot = 0
    if orientation == "right":
        rot = math.radians(180)

    # generate ear
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=length, location=loc, rotation=(
        rot, math.radians(90), math.radians(90)))
    ear = bpy.context.active_object
    ear.name = "Ear"

# addEars("blunt", "short", "left", "head_sphere", "vertical_oblong")
