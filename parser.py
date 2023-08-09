import bpy
import importlib
import os, sys, time, math, shutil

#generate path
dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

import addImageTextures
importlib.reload(addImageTextures)
import createObject
importlib.reload(createObject)
import addHead
importlib.reload(addHead)
import addEars
importlib.reload(addEars)
import addArm
importlib.reload(addArm)
import addBeak
importlib.reload(addBeak)
import bakeImage
importlib.reload(bakeImage)
import helperFunctions
importlib.reload(helperFunctions)

#parse the object table
def tableParser(filepath):
    f = open(filepath)
    pow_set = [[]]

    line = f.readline()
    for i in range(17):
        clean = line.split("[")[1]
        clean = clean[:-2]
        
        trait_items = clean.split(",")
        
        for j in range(len(pow_set)):    
            for k in trait_items:
                pow_set.append(pow_set[j]+[k])
        
        index = len(pow_set) - 1
        while (index>=0):
            if(len(pow_set[index]) == i):
                pow_set.remove(pow_set[index])
            index-=1

        line = f.readline()
    f.close()
    return pow_set


#other potential methods:
#check valid object

def colorPatternPath(pattern_number, main_color_number, comp_color_number):
    patterns = ["solid", "horizontal", "vertical", "diagonal", "grid"]
#    colors = ["gray", "black", "white", "brown", "red", "orange", "yellow", "green", "blue", "purple", "pink", "light_red", "light_orange", "light_yellow", "light_green", "light_blue", "light_purple", "light_pink"]
    colors = ['00','01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    smallerNumber = min(main_color_number, comp_color_number)
    largerNumber = max(main_color_number, comp_color_number)
    if pattern_number == 0 or largerNumber == smallerNumber:
        # if it is 
        return dir + "/Assets/patterns/" + "solid" + "_" + colors[largerNumber]+ ".png"
    else:
        return dir + "/Assets/patterns/" + patterns[pattern_number] + "_" + colors[smallerNumber]  + "_" + colors[largerNumber]+ ".png"

def getBodyCenter():
    obj = bpy.data.objects.get("Body")
    if obj:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
    saved_location = obj.location
    bpy.ops.object.select_all(action='DESELECT')
    return saved_location
    
#in progress

#Body 0 -
#BMain_Colour 1 -
#BComp_Colour 2 
#BPattern 3
#Fractal 4 -
#Head 5 -
#HMain_Colour 6 -
#HComp_Colour 7
#HPattern 8
#Ear_Left_Type 9 -
#Ear_Right_Type 10 - 
#Ear_Left_Length 11 - 
#Ear_Right_Length 12 - 
#Arm_Position 13
#Arm_Angle_Left 14
#Arm_Angle_Right 15
#Beak 16
def generateQuaddle(traits, name, output_path, export_png, export_fbx, export_gltf):
    # Delete all objects in the scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    helperFunctions.reset_scene()
    
    path1 = colorPatternPath(traits[3],traits[1], traits[2])
    
    #body shape
    body = bpy.data.objects.new("empty", None)
    body_type = ""
    if traits[0] == 0:
        body, body_type = createObject.createSphere()
    elif traits[0] == 1:
        body, body_type = createObject.createHorizontalOblong()
    elif traits[0] == 2:
        body, body_type = createObject.createVerticalOblong()
    elif traits[0] == 3:
        body, body_type = createObject.createCube()
    elif traits[0] == 4:
        body, body_type = createObject.createDiamond()
    elif traits[0] == 5:
        body, body_type = createObject.createCylinder()
    elif traits[0] == 6:
        body, body_type = createObject.createUpFrustum()
    elif traits[0] == 7:
        body, body_type = createObject.createDownFrustum()
    
    #fractal 
    #issue, the latest fractal replaces the older fractals
    
    if traits[4] != 0:
        path2 = dir + "/Assets/fractals/F (" + str(traits[4]) + ").png"
        addImageTextures.addTextureImageWithUVProject(body, "", path1, path2)
    else:    
        addImageTextures.addSingleTextureImageWithUVProject(body, body_type, path1)
    
    
    #add head
    if traits[5] == 0:
        head, head_type = addHead.createSphereHead(body_type)
    elif traits[5] == 1:
        head, head_type = addHead.createHorizontalOblongHead(body_type)
    elif traits[5] == 2:
        head, head_type = addHead.createVerticalOblongHead(body_type)
    elif traits[5] == 3:
        head, head_type = addHead.createCubeHead(body_type)
    
    path3 = colorPatternPath(traits[8],traits[6], traits[7])
    addImageTextures.addTextureSingleImage(head, head_type, path3)
    
    # create path and clean the directory
    export_path = os.path.join(output_path, "Stimuli")
    
    #bake image
#    bakeImage.bake_texture(obj = None, fbx_name = name, export_path = export_path)
    bakeImage.bake_material_to_new_uv_and_image(head, name, export_path)
    bakeImage.bake_material_to_new_uv_and_image(body, name, export_path)
    #add accessaries
    #add ear
    
    ear_left_types = ["none","normal", "blunt", "flared"]
    ear_right_types = ["none","normal", "blunt", "flared"]
    ear_left_lengths = ["normal", "short","long"] 
    ear_right_lengths = ["normal", "short","long"] 
        
    ear_left_type = ear_left_types[traits[9]]
    ear_right_type = ear_right_types[traits[10]]
    ear_left_length = ear_left_lengths[traits[11]]
    ear_right_length = ear_right_lengths[traits[12]]
        
    if ear_left_type != "none":
        addEars.addEars(ear_left_type, ear_left_length, "left", head_type, body_type)
    if ear_right_type != "none":
        addEars.addEars(ear_right_type, ear_right_length, "right", head_type, body_type)
    
    #add arm
    if traits[13]!= 0:
        arm_positions = ["none","left", "right", "both"]
        arm_angles = ["none","up","down"]

        arm_position = arm_positions[traits[13]]
        arm_angle_left = arm_angles[traits[14]]
        arm_angle_right = arm_angles[traits[15]]
        
        
        bend_directions = []
        bend_directions.append(arm_angle_left)
        bend_directions.append(arm_angle_right)
        if arm_position == "right":
            # avoid problem
            bend_directions = []
            bend_directions.append(arm_angle_right)
    
        addArm.addArms(body_type, arm_position, bend_directions)
        
    #add beak
    if traits[16] != 0:
        addBeak.addBeak(body_type)

    if export_png == 'True' or export_png == True:
        helperFunctions.camera_light_action(name, export_path, True, True, True)
        
    #Save location of body
    obj = bpy.data.objects.get("Body")
    if obj:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

    
    # Scale all selected objects down by a factor of 20
    bpy.ops.object.select_all(action='SELECT')
    saved_location = obj.location
    bpy.ops.transform.resize(value=(0.05, 0.05, 0.05))
    bpy.context.scene.cursor.location = (0.0,0.0,0.0)
    bpy.ops.transform.translate(value=-saved_location)
    bpy.ops.object.select_all(action='DESELECT')
    
    bpy.ops.object.select_all(action='SELECT')
    saved_location = obj.location
    bpy.ops.transform.rotate(value=math.radians(90), orient_axis='Z')
    bpy.ops.transform.translate(value=-saved_location)
    bpy.ops.object.select_all(action='DESELECT')
    
    #export fbx
    if export_fbx == 'True' or export_fbx == True:
        bakeImage.export_fbx(name, export_path)
        
    if export_gltf == 'True' or export_gltf == True:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                obj.select_set(True)
        # Export selected objects as FBX
        gltf_name =  name + ".gltf"
        gltf_path = os.path.join(export_path, gltf_name)
        bpy.ops.export_scene.gltf(filepath=gltf_path, export_format='GLTF_EMBEDDED')
        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')
    return "Finished!"


#Body 0 -
#BMain_Colour 1 -
#BComp_Colour 2 
#BPattern 3
#Fractal 4 -
#Head 5 -
#HMain_Colour 6 -
#HComp_Colour 7
#HPattern 8
#Ear_Left_Type 9 -
#Ear_Right_Type 10 - 
#Ear_Left_Length 11 - 
#Ear_Right_Length 12 - 
#Arm_Position 13
#Arm_Angle_Left 14
#Arm_Angle_Right 15
#Beak 16

def generateName(set):
    naming = ["BOD", "BMC", "BCC", "BPT", "FRC", "HEA", "HMC", "HCC", "HPT", "ELT", "ERT", "ELL", "ERL", "AP", "AAL", "AAR", "BEK"]
    output_names = []
    for elem in set:
        one_name = ""
        for index in range(len(elem)):
            one_name = one_name + str(naming[index]) + str(elem[index]) + "_"
        output_names.append(one_name[:-1])
    return output_names

if __name__ == "__main__":
    helperFunctions.reset_scene()
    # set default
    input_path = None
    output_path = dir
    
    # Parse command line input
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
        
        if "--input_path" in argv:
            input_path_index = argv.index("--input_path")
            if input_path_index < len(argv) - 1:
                input_path = argv[input_path_index + 1]
            else:
                print("Error: no input path specified after --input_path")
                # add further error handling here as needed

        if "--output_path" in argv:
            output_path_index = argv.index("--output_path")
            if output_path_index < len(argv) - 1:
                output_path = argv[output_path_index + 1]
            else:
                print("Error: no output path specified after --output_path")
                # add further error handling here as needed
                
        if "--export_png" in argv:
            export_png_index = argv.index("--export_png")
            if export_png_index < len(argv) - 1:
                export_png = argv[export_png_index + 1]
            else:
                export_png = True
                print("Export PNG sets to True")
                # add further error handling here as needed
        
        if "--export_fbx" in argv:
            export_fbx_index = argv.index("--export_fbx")
            if export_fbx_index < len(argv) - 1:
                export_fbx = argv[export_fbx_index + 1]
            else:
                export_fbx = False
                print("Export FBX sets to False")
                # add further error handling here as needed
        
        if "--export_gltf" in argv:
            export_gltf_index = argv.index("--export_gltf")
            if export_gltf_index < len(argv) - 1:
                export_gltf = argv[export_gltf_index + 1]
            else:
                export_gltf = False
                print("Export GLTF sets to False")
                # add further error handling here as needed

    if input_path is not None:
        for file_name in os.listdir(input_path):
            if "Object Table" in file_name:
                # This is test code for some Quaddles
                # Generating Quaddles from the ObjectTable is quite similar, loop through pow_set and call generateQuaddle each time (create naming system)
                traits = tableParser(input_path + "/" + file_name)
                print(traits)
                traits_names = generateName(traits)
                print(traits_names)

                for index in range(len(traits)):
                    name = traits_names[index]
                    current_trait = traits[index]

                    start_time = time.time()

                    generateQuaddle([int(x) for x in current_trait], name, output_path, export_png, export_fbx, export_gltf)

                    end_time = time.time()
                    running_time = end_time - start_time
                    print(f"Running time: {running_time} seconds for generating quaddle: {name}")
    else:
        test_set = [['3', '4', '9', '4', '4', '0', '0', '0', '0', '3', '2', '2', '1', '3', '1', '2', '0']]
        test_set = [[int(x) for x in test_set[0]]]
        test_name = generateName(test_set)
        for index in range(len(test_set)):
            name = "test" + "_" + test_name[index]
            generateQuaddle(test_set[index], name, dir, 'False', 'False')
            
            