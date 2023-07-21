import bpy, os


def join_meshes():
    scene = bpy.context.scene
    
    obs = []
    for ob in scene.objects:
        # whatever objects you want to join...
        if ob.type == 'MESH':
            print(ob.name)
            obs.append(ob)
            ob.select_set(True)
    # to join mesh there needs to have one main active part
    bpy.context.view_layer.objects.active = obs[0]
    bpy.ops.object.join()
    
def export_fbx(name, export_path):
    # Select all meshes in the scene
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            obj.select_set(True)

    # Export selected objects as FBX
    fbx_name =  name + ".fbx"
    fbx_path = os.path.join(export_path, fbx_name)
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True)
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    

def bake_texture(obj, fbx_name, export_path):
    if not os.path.exists(export_path):
        os.makedirs(export_path)
    # set the baking engine to Cycles
    bpy.context.scene.render.engine = 'CYCLES'
    
    # Check if a compatible GPU is available, GPU will make rendering process much faster
    if bpy.context.preferences.system.legacy_compute_device_type == 'CUDA':
        bpy.context.preferences.addons['cycles'].preferences.devices[0].use = True
        bpy.context.scene.cycles.device = 'GPU'
    
    if obj == None or obj == 'whole':
        # If there are multiple objects on the scene, join them
        join_meshes()
        # Set obj to the newly created joined object
        obj = bpy.context.active_object
        print("After join:", obj.name)
    
    # Check if the object is a mesh
    if obj.type != 'MESH':
        print("Selected object is not a mesh")
        return
    texture_name = fbx_name + "_bakedtexture"
    # Create a new blank image and set its file format to PNG
    bakedImage = bpy.data.images.new(texture_name, width=720, height=720)
    bakedImage.file_format = 'PNG'

   # Add a texture node with the baked image to all materials on the object
    for slot in obj.material_slots:
        if slot.material is None:
            continue

        material = slot.material
        material.use_nodes = True
        nodes = material.node_tree.nodes
        # Create a new texture node, add the baked image, and mark it as active
        imageNode = nodes.new('ShaderNodeTexImage')
        imageNode.image = bakedImage
        imageNode.location = (100, 100)
        imageNode.image.colorspace_settings.name = "Raw"

        # Deselect all nodes
        for node in nodes:
            node.select = False

        imageNode.select = True
        nodes.active = imageNode

    # Create a new UV map and run a Smart UV Project on the object
    lm = obj.data.uv_layers.get("Bake")
    if not lm:
        lm = obj.data.uv_layers.new(name="Bake")

    lm.active = True
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT') # for all
    bpy.ops.uv.smart_project()
    bpy.ops.object.editmode_toggle()
    # Bake the texture to the newly created image node
    bpy.ops.object.select_all(action='DESELECT')
        
    # Select all mesh objects
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            obj.select_set(True)
    obj = bpy.context.active_object
    print(obj.name)
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'})
    # Save the baked image to the current folder/textures
    texture_name_export = fbx_name + "_bakedtexture.png"
    print(texture_name_export)
    print(export_path)
    texture_path = os.path.join(export_path, "textures", texture_name_export)
    bakedImage.save_render(filepath=texture_path)

    # Delete all previous material slots
    for slot in obj.material_slots:
        obj.active_material_index = 0
        bpy.ops.object.material_slot_remove()

    # Create a new material slot with the baked texture
    material = bpy.data.materials.new(name="BakedMaterial")
    bpy.context.object.data.materials.append(material)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    texture_node = nodes.new('ShaderNodeTexImage')
    texture_node.image = bpy.data.images.load(texture_path)
    texture_node.image.colorspace_settings.name = "sRGB"
    texture_node.location = (-300, 300)
    links = material.node_tree.links
    link = links.new(texture_node.outputs[0], bsdf.inputs[0])

    # Get all UV maps for the object
    uv_maps = obj.data.uv_layers
    # Get the UV map named "UVMap"
    uv_map = obj.data.uv_layers.get("UVMap")
    # If the UV map exists, remove it
    if uv_map is not None:
        obj.data.uv_layers.remove(uv_map)

    print("Texture baked texture and saved to", texture_path)
    
    return

def bake_material_to_new_uv_and_image(obj, fbx_name, export_path):
    if not os.path.exists(export_path):
        os.makedirs(export_path)
    image_name = fbx_name +"_"+ obj.name + "_bakedtexture"
    # Create a new image
    image = bpy.data.images.new(image_name, width=512, height=512)

    # Get the object's material
    material = obj.data.materials[0]
    nodes = material.node_tree.nodes

    # Create a new Image Texture node
    image_texture_node = nodes.new(type="ShaderNodeTexImage")
    image_texture_node.image = image
    image_texture_node.location = (-300, 500)
    image_texture_node.image.colorspace_settings.name = "Raw"

    # Connect the new Image Texture node to the Principled BSDF node
    principled_bsdf_node = next(node for node in nodes if node.type == 'BSDF_PRINCIPLED')

    # Set bake settings and bake
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.render.bake.use_selected_to_active = False
    
    for node in nodes:
        node.select = False
    image_texture_node.select = True
    nodes.active = image_texture_node
    
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


    bpy.ops.object.bake(type = "DIFFUSE")
    
    # Save the baked image to the current folder/textures
    texture_name_export = image_name + ".png"
    texture_path = os.path.join(export_path, "textures", texture_name_export)
    image.save_render(filepath=texture_path)
    
    material.node_tree.links.new(image_texture_node.outputs['Color'], principled_bsdf_node.inputs['Base Color'])
    material.node_tree.links.new(image_texture_node.outputs['Alpha'], principled_bsdf_node.inputs['Alpha'])
    image_texture_node.image = bpy.data.images.load(texture_path)
    image_texture_node.image.colorspace_settings.name = "sRGB"
    uv_map = nodes.new('ShaderNodeUVMap')
    uv_map.location = (-600, 500)
    material.node_tree.links.new(uv_map.outputs['UV'], image_texture_node.inputs['Vector'])
    
    bpy.ops.object.select_all(action='DESELECT')
    
    
    return
    
if __name__ == "__main__":
    background = '/Users/wenxuan/Documents/Blender/Assets/Patterns and Colours/Pattern(Solid)+Colour(7070014_7070014).png'
    fractal = '/Users/wenxuan/Documents/Blender/Assets/Fractals_old/Transparent/1200x1200/F (1).png'
    
    bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    cube = bpy.context.active_object
    # Create a sphere on top of the cube
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, enter_editmode=False, align='WORLD', location=(0, 0, 2))
    sphere = bpy.context.active_object
    
    
    
#    name = "final_test"
#    export_path = "/Users/wenxuan/Documents/Blender/TestingFolder"
#    bake_texture(name, export_path)