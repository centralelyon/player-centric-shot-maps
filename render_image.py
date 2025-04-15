import bpy
import math
import os
import csv
import json
import numpy as np
import cv2
import glob
from BlenderScene import create_sphere,create_cylinder_between,delete_cube,draw_ball




def save_image_blender(frame,chemin_enregistrement,liste_farme_joueur1,liste_farme_joueur2,liste_pose_balle_3d,json_camera_data):
    """
        Function for saving an image from a blender scene
        Args:
                - Frame number
                - Save path
                - Player 1 Keypoint list
                - Player 2 Keypoint list
                - Ball position
                - List of lines from enhanced annotation csv
                - Cam params dictionary 
    """
    # Delete all existing objects in the scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    plateau = delete_cube(152,10,274,(0, 0, 76-5),"plateau")
    filet = delete_cube(180,15,0.1,(0, 0, 76+7.5),"filet")
    base = delete_cube(90,76-10,90,(0, 0, 76/2-5),"base")

    # Create a blue material
    blue_material = bpy.data.materials.new(name="BlueMaterial")
    blue_material.use_nodes = True
    bsdf = blue_material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.0, 0.0, 1.0, 1.0)  # RGBA color for blue

    # Assign the material to the cube
    if plateau.data.materials:
        plateau.data.materials[0] = blue_material
    else:
        plateau.data.materials.append(blue_material)

    white_material = bpy.data.materials.new(name="WhiteMaterial")
    white_material.use_nodes = True
    bsdf_sphere = white_material.node_tree.nodes["Principled BSDF"]
    bsdf_sphere.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)  # White
    # Assign the material to the sphere
    filet.data.materials.append(white_material)
    
    liste_centre_farme_joueur1 = []
    for row in liste_farme_joueur1:
        if int(row[0]) == frame:
            create_sphere((float(row[2]),-float(row[3]),float(row[4])), radius=5)
            liste_centre_farme_joueur1.append([float(row[2]),-float(row[3])])
    points_array = np.array(liste_centre_farme_joueur1)
    moyenne = points_array.mean(axis=0)
    print(moyenne)
    create_cylinder_between((moyenne[0],moyenne[1],0), (moyenne[0],moyenne[1],76), radius=1)
    create_cylinder_between((moyenne[0],moyenne[1],76), (moyenne[0],np.sign(moyenne[1])*137,76), radius=0.5)
    bpy.ops.object.text_add(location=(0, 0, 0))


    black_material = bpy.data.materials.new(name="BlackMaterial")
    black_material.use_nodes = True
    bsdf_text = black_material.node_tree.nodes["Principled BSDF"]
    bsdf_text.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)  # Black



    text_obj1 = bpy.context.object
    text_obj1.data.body = str(abs(int(moyenne[1]))-137)+"cm"
    text_obj1.data.size = 20  # Text size
    text_obj1.location = (moyenne[0], moyenne[1] if np.sign(moyenne[1]) == -1 else 137, 76)  # Text object position 
    text_obj1.rotation_euler[0] = math.radians(90) 
    text_obj1.rotation_euler[1] = math.radians(0)
    text_obj1.rotation_euler[2] = math.radians(0)
    text_obj1.data.materials.append(black_material)

    liste_centre_farme_joueur2 = []
    for row in liste_farme_joueur2:
        if int(row[0]) == frame:
            create_sphere((float(row[2]),-float(row[3]),float(row[4])), radius=5)
            liste_centre_farme_joueur2.append([float(row[2]),-float(row[3])])
    points_array = np.array(liste_centre_farme_joueur2)
    moyenne = points_array.mean(axis=0)
    create_cylinder_between((moyenne[0],moyenne[1],0), (moyenne[0],moyenne[1],76), radius=1)
    create_cylinder_between((moyenne[0],moyenne[1],76), (moyenne[0],np.sign(moyenne[1])*137,76), radius=0.5)
    bpy.ops.object.text_add(location=(0, 0, 0))
    text_obj2 = bpy.context.object
    text_obj2.data.body = str(abs(int(moyenne[1]))-137)+"cm"
    text_obj2.data.size = 20  # Taille du texte
    text_obj2.location = (moyenne[0], moyenne[1] if np.sign(moyenne[1]) == -1 else 137, 76)  # Text object position 
    text_obj2.rotation_euler[0] = math.radians(90) 
    text_obj2.rotation_euler[1] = math.radians(0)  
    text_obj2.rotation_euler[2] = math.radians(0)
    text_obj2.data.materials.append(black_material)


    for row in liste_pose_balle_3d:
        if int(row[1]) == 4 and int(row[0]) == frame:
            if row[2] != "":
                draw_ball((float(row[2]),-float(row[3]),float(row[4])+76),2)
            else:
                print(row)


    # Add a plane as the ground
    bpy.ops.mesh.primitive_plane_add(size=4000, location=(-1000, -1000, 0))
    ground = bpy.context.object

    # Create a material for the ground with RGB color (22, 11, 55)
    ground_material = bpy.data.materials.new(name="GroundMaterial")
    ground_material.use_nodes = True
    bsdf_ground = ground_material.node_tree.nodes["Principled BSDF"]
    bsdf_ground.inputs["Base Color"].default_value = (232/255, 36/255, 95/255, 1.0)  # Convert RGB to 0-1

    # Assign the material to the ground
    ground.data.materials.append(ground_material)


    
    # Add a high-intensity light
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 500))
    light = bpy.context.object
    light.data.energy = 1000 

    # Add a secondary light to improve lighting
    bpy.ops.object.light_add(type='POINT', location=(-5, -5, 5))
    second_light = bpy.context.object
    second_light.data.energy = 500 

    # Add a 'SUN' type light for global illumination
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 500))
    sun_light = bpy.context.object
    sun_light.data.energy = 5 

    # Position and orient the camera
    bpy.ops.object.camera_add(location=(json_camera_data["position_x"], json_camera_data["position_y"], json_camera_data["position_z"]))
    camera = bpy.context.object
    
    camera.rotation_euler = (math.radians(json_camera_data["rotation_x"]), math.radians(json_camera_data["rotation_y"]), math.radians(json_camera_data["rotation_z"]))  # Orienter la caméra
    camera.data.lens = json_camera_data["focale"]
    camera.data.clip_start = 0.1  # Minimum visible distance
    camera.data.clip_end = 5000.0

    # Set the active camera for rendering
    bpy.context.scene.camera = camera

    # Enable ambient lighting in the world
    bpy.context.scene.world.use_nodes = True
    world_node_tree = bpy.context.scene.world.node_tree
    bg_node = world_node_tree.nodes["Background"]
    bg_node.inputs["Strength"].default_value = 5 



    # Set rendering parameters (resolution and format)
    bpy.context.scene.render.resolution_x = 1280
    bpy.context.scene.render.resolution_y = 720
    bpy.context.scene.render.image_settings.file_format = 'PNG'

    # Specify output path for the image
    bpy.context.scene.render.filepath = chemin_enregistrement
    print(chemin_enregistrement)
    # Render the image
    bpy.ops.render.render(write_still=True)

    print("Image successfully recorded !")
    


def create_render_all_rebounds(chemin_enregistrement,liste_rebonds,liste_positions,json_camera_data,afficher_table=True):
    """
        Function for saving an image from a blender scene with all rebound of the ball
        Args:
                - Save path
                - Rebounds list
                - List of player positions
                - Cam params dictionary 
    """
    # Delete all existing objects in the scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    if afficher_table:
        plateau = delete_cube(152,10,274,(0, 0, 76-5),"plateau")
        filet = delete_cube(180,15,0.1,(0, 0, 76+7.5),"filet")
        base = delete_cube(90,76-10,90,(0, 0, 76/2-5),"base")

        # Create a blue material
        blue_material = bpy.data.materials.new(name="BlueMaterial")
        blue_material.use_nodes = True
        bsdf = blue_material.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (0.0, 0.0, 1.0, 1.0)

        # Assign the material to the cube
        if plateau.data.materials:
            plateau.data.materials[0] = blue_material
        else:
            plateau.data.materials.append(blue_material)

        white_material = bpy.data.materials.new(name="WhiteMaterial")
        white_material.use_nodes = True
        bsdf_sphere = white_material.node_tree.nodes["Principled BSDF"]
        bsdf_sphere.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)  # White
        # Assign the material to the sphere
        filet.data.materials.append(white_material)
    
    for row in liste_rebonds:
        create_sphere((float(row[2]),-float(row[3]),76), radius=2)
    

    for row in liste_positions:
        create_sphere((float(row[2]),-float(row[3]),76), radius=5)
        create_cylinder_between((float(row[2]),-float(row[3]),0),(float(row[2]),-float(row[3]),76), radius=0.5)


    # Add a plane as the ground
    bpy.ops.mesh.primitive_plane_add(size=4000, location=(-1000, -1000, 0))
    ground = bpy.context.object

    # Create a material for the ground with RGB color (22, 11, 55)
    ground_material = bpy.data.materials.new(name="GroundMaterial")
    ground_material.use_nodes = True
    bsdf_ground = ground_material.node_tree.nodes["Principled BSDF"]
    bsdf_ground.inputs["Base Color"].default_value = (232/255, 36/255, 95/255, 1.0)  # Convert RGB to 0-1

    # Assign the material to the ground
    ground.data.materials.append(ground_material)


    
    # Add a high-intensity light
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 500))
    light = bpy.context.object
    light.data.energy = 1000 

    # Add a secondary light to improve lighting
    bpy.ops.object.light_add(type='POINT', location=(-5, -5, 5))
    second_light = bpy.context.object
    second_light.data.energy = 500 

    # Add a 'SUN' type light for global illumination
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 500))
    sun_light = bpy.context.object
    sun_light.data.energy = 5

    # Position and orient the camera
    bpy.ops.object.camera_add(location=(json_camera_data["position_x"], json_camera_data["position_y"], json_camera_data["position_z"]))
    camera = bpy.context.object
    
    camera.rotation_euler = (math.radians(json_camera_data["rotation_x"]), math.radians(json_camera_data["rotation_y"]), math.radians(json_camera_data["rotation_z"]))
    camera.data.lens = json_camera_data["focale"]
    camera.data.clip_start = 0.1 
    camera.data.clip_end = 5000.0

    # Set the active camera for rendering
    bpy.context.scene.camera = camera

    # Enable ambient lighting in the world
    bpy.context.scene.world.use_nodes = True
    world_node_tree = bpy.context.scene.world.node_tree
    bg_node = world_node_tree.nodes["Background"]
    bg_node.inputs["Strength"].default_value = 5 



    bpy.context.scene.render.resolution_x = 1280
    bpy.context.scene.render.resolution_y = 720
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = chemin_enregistrement 
    bpy.ops.render.render(write_still=True)

    print("Image successfully recorded !")


def create_video_from_images(image_folder, output_path, fps=25):
    """Function to create video from image

    Args:
        image_folder (str): Path of folder containing all images
        output_path (str): Output path of the video
        fps (int): Number of frame per second. Defaults to 25.
    """
    # Get list of images in the folder, sorted by name
    images = sorted(glob.glob(os.path.join(image_folder, "*.png")))  # or "*.jpg"
    if not images:
        print("No images found in folder.")
        return

    # Read the first image to get dimensions
    frame = cv2.imread(images[0])
    height, width, layers = frame.shape

    # Initialize the video with image dimensions
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use MPEG-4 codex for .mp4
    video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    images
    images.sort()
    images.sort(key=len)
    for image_path in images:
        frame = cv2.imread(image_path)
        video.write(frame) 

    video.release()
    print(f"Video saved at : {output_path}")


def create_video_3d(chemin_pose_3d,chemin_pose_balle_3d,chemin_json_camera,dossier_enregistrement,chemin_csv_enrichi,chemin_enregistrement):
    """Function to create 3d reconstruction of player's position

    Args:
        chemin_pose_3d (str): 3d Pose Estimation csv path
        chemin_pose_balle_3d (str): 3d Ball trajectory csv path
        chemin_json_camera (str): camera json path
        dossier_enregistrement (str): Folder save path (for individual images)
        chemin_csv_enrichi (str): enhanced annotation csv path
        chemin_enregistrement (str): save path (for the video)
    """
    json_camera = open(chemin_json_camera,"r")
    json_camera_data = json.load(json_camera)

    fichier_lecture = open(chemin_csv_enrichi,"r")
    csv_reader = csv.reader(fichier_lecture, delimiter=',')
    next(csv_reader)
    liste_rebonds = []
    liste_positions = []
    liste_positions.append([0,0,0,0])
    for row in csv_reader:
        if row[13] != "":
            liste_rebonds.append([row[0],row[1],row[13],row[14]])
            liste_positions.append([row[0],row[1],row[34],row[35]])
            liste_positions.append([row[0],row[1],row[37],row[38]])

    fichier_lecture = open(chemin_pose_3d,"r")
    csv_reader = csv.reader(fichier_lecture, delimiter=',')
    next(csv_reader)
    liste_pose_3d = []
    for row in csv_reader:
        liste_pose_3d.append(row)
    
    fichier_lecture = open(chemin_pose_balle_3d,"r")
    csv_reader = csv.reader(fichier_lecture, delimiter=',')
    next(csv_reader)
    liste_pose_balle_3d = []
    for row in csv_reader:
        liste_pose_balle_3d.append(row)

    
    liste_farme_joueur1 = []
    for row in liste_pose_3d:
        if float(row[1]) == 0:
            liste_farme_joueur1.append(row)
    liste_farme_joueur2 = []
    for row in liste_pose_3d:
        if float(row[1]) == 2:
            liste_farme_joueur2.append(row)

    

    nb_frames = max(int(liste_farme_joueur1[-1][0]),int(liste_farme_joueur2[-1][0]),int(liste_pose_balle_3d[-1][0]))
    if not os.path.isdir(dossier_enregistrement):
        os.mkdir(dossier_enregistrement)
    for i in range(nb_frames):    
        save_image_blender(i,os.path.join(dossier_enregistrement,str(i)+".jpg"),liste_farme_joueur1,liste_farme_joueur2,liste_pose_balle_3d,json_camera_data)

    create_video_from_images(dossier_enregistrement, chemin_enregistrement, fps=25)



   
if __name__ == "__main__":
    create_video_3d(os.path.join("example/set_1_point_8_position_joueur_grace_pieds.csv"),
                    os.path.join("example/set_1_point_8_zone_joueur_avec_pos_balle_3D.csv"),
                    os.path.join("example/PRITHIKA-PAVADE_vs_SIBEL-ALTINKAYA_camera.json"),
                    os.path.join(os.getcwd(),"example","images"),
                    os.path.join("example/set_1_point_8_annotation_enrichi.csv"),
                    "3d_video.mp4")