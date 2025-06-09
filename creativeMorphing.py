import bpy
import bmesh
import math

def create_base_cube(height, size):
    """
    Creates a rectangular prism (cube) centered at the origin.

    Args:
        height (float): The total height of the prism along the Z-axis.
        size (float): The width and depth of the square base along X and Y.
    """
    # Ensure we are in object mode to create a new mesh
    if bpy.context.object and bpy.context.object.mode == 'EDIT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Create a new cube
    bpy.ops.mesh.primitive_cube_add(size=size, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    
    # Get the newly created object
    obj = bpy.context.active_object
    obj.name = "MorphingPrism"
    
    # Adjust the dimensions
    obj.dimensions = (size, size, height)
    
    # Apply the scale to make the dimension changes real
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    return obj

def morph_to_cylinder(obj, morph_percentage):
    """
    Morphs the top and bottom faces of a given mesh object from a square to a circle.

    Args:
        obj (bpy.types.Object): The mesh object to morph.
        morph_percentage (float): The percentage of the morph (0-100). 
                                  0 is a full cube, 100 is a full cylinder.
    """
    if not obj or obj.type != 'MESH':
        print("Error: Please provide a valid mesh object.")
        return

    # Ensure we are in object mode before accessing mesh data
    if obj.mode == 'EDIT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # --- Calculations ---
    # The morph factor will be from 0.0 to 1.0
    morph_factor = morph_percentage / 100.0
    
    # Get the dimensions of the object to calculate the radius
    # We assume the base is on the XY plane
    square_width = obj.dimensions.x
    
    # To preserve the area, Area_square = Area_circle
    # size^2 = pi * r^2  =>  r = sqrt(size^2 / pi)
    radius = math.sqrt(square_width**2 / math.pi)

    # --- Mesh Modification ---
    # Create a BMesh from the object's mesh data
    bm = bmesh.new()
    bm.from_mesh(obj.data)

    # Identify top and bottom vertices
    # Get the height from the object's bounding box to handle any origin point
    z_coords = [v.co.z for v in bm.verts]
    min_z, max_z = min(z_coords), max(z_coords)
    
    # A small epsilon for floating point comparisons
    epsilon = 0.0001
    
    top_verts = [v for v in bm.verts if abs(v.co.z - max_z) < epsilon]
    bottom_verts = [v for v in bm.verts if abs(v.co.z - min_z) < epsilon]

    # --- Morphing Logic ---
    for v in top_verts + bottom_verts:
        # Original position of the vertex
        original_pos = v.co.copy()
        
        # Calculate the vector from the center (0,0) to the vertex on the XY plane
        vec_xy = original_pos.xy
        
        # If the vector has a length (i.e., not the center vertex if one exists)
        if vec_xy.length > 0:
            # The target position is on a circle. We find this by normalizing
            # the vector from the center to the vertex and scaling it by the new radius.
            target_pos_xy = vec_xy.normalized() * radius
            
            # Interpolate between the original and target position using the morph factor
            # new_pos = original * (1 - factor) + target * factor
            final_pos_xy = original_pos.xy.lerp(target_pos_xy, morph_factor)
            
            # Update the vertex's X and Y coordinates
            v.co.x = final_pos_xy.x
            v.co.y = final_pos_xy.y
            # Z coordinate remains unchanged

    # --- Finalization ---
    # Write the BMesh data back to the object's mesh
    bm.to_mesh(obj.data)
    # Free the BMesh
    bm.free()
    
    # Update the viewport to show the changes
    obj.data.update()


# --- Blender Operator Class ---
# This class creates a tool that can be run from the Blender UI

class MORPH_OT_creator(bpy.types.Operator):
    """Creates a prism and morphs it into a cylinder"""
    bl_idname = "mesh.morph_creator"
    bl_label = "Create and Morph Prism"
    bl_options = {'REGISTER', 'UNDO'}

    # Add a property for the user to control the morph percentage
    morph_percent: bpy.props.FloatProperty(
        name="Morph %",
        description="The percentage of morph from square to circle (0 to 100)",
        default=50.0,
        min=0.0,
        max=100.0
    )

    def execute(self, context):
        # --- Main Execution ---
        # 1. Clear existing mesh objects for a clean scene (optional)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_by_type(type='MESH')
        bpy.ops.object.delete()

        # 2. Create the base cube
        height = 6.0
        size = 3.0
        base_object = create_base_cube(height, size)
        
        # Make sure the new object is active and selected
        context.view_layer.objects.active = base_object
        base_object.select_set(True)

        # 3. Morph the object using the property value
        morph_to_cylinder(base_object, self.morph_percent)
        
        self.report({'INFO'}, f"Morphed prism created with {self.morph_percent}% morph.")

        return {'FINISHED'}


# --- Registration ---
# This is required to make the operator available in Blender

def menu_func(self, context):
    self.layout.operator(MORPH_OT_creator.bl_idname, icon='MOD_SUBSURF')

def register():
    bpy.utils.register_class(MORPH_OT_creator)
    bpy.types.VIEW3D_MT_add.append(menu_func)

def unregister():
    bpy.utils.unregister_class(MORPH_OT_creator)
    bpy.types.VIEW3D_MT_add.remove(menu_func)


# This allows you to run the script directly from Blender's Text Editor
if __name__ == "__main__":
    register()

    # You can also run the operator directly for testing
    bpy.ops.mesh.morph_creator(morph_percent=50)

