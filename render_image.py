import bpy
import math
import os
import csv
import json
import numpy as np
import cv2
from AddObjectScrip import creation_table,create_sphere,create_cylinder_between,tracer_balle




def enregistrement_image(frame,chemin_enregistrement,liste_farme_joueur1,liste_farme_joueur2,liste_pose_balle_3d,json_camera_data):
    """
        Fonction permettant d'enregistrer une image d'une scène blender
        Entrée:
                - Le numéro de la frame
                - Le chemin pour enregistrer l'image
                - La liste des joints du joueur 1
                - La liste des joints du joueur 2
                - La liste de la position de la balle
                - La liste des ligne du csv annotation enrichi
                - Le dictionnaire contenant les paramètres de la caméra
    """
    # Supprimer tous les objets existants dans la scène
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    plateau = creation_table(152,10,274,(0, 0, 76-5),"plateau")
    filet = creation_table(180,15,0.1,(0, 0, 76+7.5),"filet")
    base = creation_table(90,76-10,90,(0, 0, 76/2-5),"base")

    # Créer un matériau bleu
    blue_material = bpy.data.materials.new(name="BlueMaterial")
    blue_material.use_nodes = True
    bsdf = blue_material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.0, 0.0, 1.0, 1.0)  # Couleur RGBA pour bleu

    # Assigner le matériau au cube
    if plateau.data.materials:
        plateau.data.materials[0] = blue_material
    else:
        plateau.data.materials.append(blue_material)

    white_material = bpy.data.materials.new(name="WhiteMaterial")
    white_material.use_nodes = True
    bsdf_sphere = white_material.node_tree.nodes["Principled BSDF"]
    bsdf_sphere.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)  # Blanc
    # Assigner le matériau à la sphère
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
    bsdf_text.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)  # Noir



    text_obj1 = bpy.context.object
    text_obj1.data.body = str(abs(int(moyenne[1]))-137)+"cm"
    text_obj1.data.size = 20  # Taille du texte
    text_obj1.location = (moyenne[0], moyenne[1] if np.sign(moyenne[1]) == -1 else 137, 76)  # Position de l'objet texte
    text_obj1.rotation_euler[0] = math.radians(90)   # Rotation autour de X (en radians)
    text_obj1.rotation_euler[1] = math.radians(0)   # Rotation autour de Y
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
    text_obj2.location = (moyenne[0], moyenne[1] if np.sign(moyenne[1]) == -1 else 137, 76)  # Position de l'objet texte
    text_obj2.rotation_euler[0] = math.radians(90)   # Rotation autour de X (en radians)
    text_obj2.rotation_euler[1] = math.radians(0)   # Rotation autour de Y
    text_obj2.rotation_euler[2] = math.radians(0)
    text_obj2.data.materials.append(black_material)


    for row in liste_pose_balle_3d:
        if int(row[1]) == 4 and int(row[0]) == frame:
            if row[2] != "":
                tracer_balle((float(row[2]),-float(row[3]),float(row[4])+76),2)
            else:
                print(row)


    # Ajouter un plan en tant que sol
    bpy.ops.mesh.primitive_plane_add(size=4000, location=(-1000, -1000, 0))
    ground = bpy.context.object

    # Créer un matériau pour le sol avec la couleur RGB (22, 11, 55)
    ground_material = bpy.data.materials.new(name="GroundMaterial")
    ground_material.use_nodes = True
    bsdf_ground = ground_material.node_tree.nodes["Principled BSDF"]
    bsdf_ground.inputs["Base Color"].default_value = (232/255, 36/255, 95/255, 1.0)  # Conversion RGB en 0-1

    # Assigner le matériau au sol
    ground.data.materials.append(ground_material)


    
    # Ajouter une lumière avec une intensité élevée
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 500))
    light = bpy.context.object
    light.data.energy = 1000  # Augmenter l'énergie de la lumière

    # Ajouter une lumière secondaire pour améliorer l'éclairage
    bpy.ops.object.light_add(type='POINT', location=(-5, -5, 5))
    second_light = bpy.context.object
    second_light.data.energy = 500  # Ajuster l'énergie de la lumière secondaire

    # Ajouter une lumière du type 'SUN' pour un éclairage global
    #bpy.ops.object.light_add(type='SUN', location=(5, -5, 5))
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 500))
    sun_light = bpy.context.object
    sun_light.data.energy = 5  # Ajuster l'intensité de la lumière du soleil

    # Positionner et orienter la caméra
    bpy.ops.object.camera_add(location=(json_camera_data["position_x"], json_camera_data["position_y"], json_camera_data["position_z"]))
    camera = bpy.context.object
    print((math.radians(json_camera_data["rotation_x"]), math.radians(json_camera_data["rotation_y"]), math.radians(json_camera_data["rotation_z"])))
    #camera.rotation_euler = (1.1, 0, 0.8)  # Orienter la caméra
    camera.rotation_euler = (math.radians(json_camera_data["rotation_x"]), math.radians(json_camera_data["rotation_y"]), math.radians(json_camera_data["rotation_z"]))  # Orienter la caméra
    camera.data.lens = json_camera_data["focale"]
    camera.data.clip_start = 0.1  # Distance minimale visible
    camera.data.clip_end = 5000.0

    # Définir la caméra active pour le rendu
    bpy.context.scene.camera = camera

    # Activer un éclairage ambiant dans le monde
    bpy.context.scene.world.use_nodes = True
    world_node_tree = bpy.context.scene.world.node_tree
    bg_node = world_node_tree.nodes["Background"]
    bg_node.inputs["Strength"].default_value = 5  # Augmenter l'éclairement ambiant




    # Définir les paramètres du rendu (résolution et format)
    bpy.context.scene.render.resolution_x = 1280
    bpy.context.scene.render.resolution_y = 720
    bpy.context.scene.render.image_settings.file_format = 'PNG'

    # Spécifier le chemin de sortie de l'image
    bpy.context.scene.render.filepath = chemin_enregistrement #"C:/Users/ReViVD/Documents/GitHub/tt-mmpose/votre_image.png"

    # Rendre l'image
    bpy.ops.render.render(write_still=True)

    print("Image enregistrée avec succès !")
    


def creer_rendu_tous_rebonds(chemin_enregistrement,liste_rebonds,liste_positions,json_camera_data,afficher_table=True):
    """
        Fonction permettant d'enregistrer une image d'une scène blender
        Entrée:
                - Le chemin pour enregistrer l'image
                - La liste rebonds
                - La liste de la position des joueurs
                - Le dictionnaire contenant les paramètres de la caméra
    """
    # Supprimer tous les objets existants dans la scène
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    if afficher_table:
        plateau = creation_table(152,10,274,(0, 0, 76-5),"plateau")
        filet = creation_table(180,15,0.1,(0, 0, 76+7.5),"filet")
        base = creation_table(90,76-10,90,(0, 0, 76/2-5),"base")

        # Créer un matériau bleu
        blue_material = bpy.data.materials.new(name="BlueMaterial")
        blue_material.use_nodes = True
        bsdf = blue_material.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (0.0, 0.0, 1.0, 1.0)  # Couleur RGBA pour bleu

        # Assigner le matériau au cube
        if plateau.data.materials:
            plateau.data.materials[0] = blue_material
        else:
            plateau.data.materials.append(blue_material)

        white_material = bpy.data.materials.new(name="WhiteMaterial")
        white_material.use_nodes = True
        bsdf_sphere = white_material.node_tree.nodes["Principled BSDF"]
        bsdf_sphere.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)  # Blanc
        # Assigner le matériau à la sphère
        filet.data.materials.append(white_material)
    
    for row in liste_rebonds:
        create_sphere((float(row[2]),-float(row[3]),76), radius=2)
    

    for row in liste_positions:
        create_sphere((float(row[2]),-float(row[3]),76), radius=5)
        create_cylinder_between((float(row[2]),-float(row[3]),0),(float(row[2]),-float(row[3]),76), radius=0.5)


    # Ajouter un plan en tant que sol
    bpy.ops.mesh.primitive_plane_add(size=4000, location=(-1000, -1000, 0))
    ground = bpy.context.object

    # Créer un matériau pour le sol avec la couleur RGB (22, 11, 55)
    ground_material = bpy.data.materials.new(name="GroundMaterial")
    ground_material.use_nodes = True
    bsdf_ground = ground_material.node_tree.nodes["Principled BSDF"]
    bsdf_ground.inputs["Base Color"].default_value = (232/255, 36/255, 95/255, 1.0)  # Conversion RGB en 0-1

    # Assigner le matériau au sol
    ground.data.materials.append(ground_material)


    
    # Ajouter une lumière avec une intensité élevée
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 500))
    light = bpy.context.object
    light.data.energy = 1000  # Augmenter l'énergie de la lumière

    # Ajouter une lumière secondaire pour améliorer l'éclairage
    bpy.ops.object.light_add(type='POINT', location=(-5, -5, 5))
    second_light = bpy.context.object
    second_light.data.energy = 500  # Ajuster l'énergie de la lumière secondaire

    # Ajouter une lumière du type 'SUN' pour un éclairage global
    #bpy.ops.object.light_add(type='SUN', location=(5, -5, 5))
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 500))
    sun_light = bpy.context.object
    sun_light.data.energy = 5  # Ajuster l'intensité de la lumière du soleil

    # Positionner et orienter la caméra
    bpy.ops.object.camera_add(location=(json_camera_data["position_x"], json_camera_data["position_y"], json_camera_data["position_z"]))
    camera = bpy.context.object
    print((math.radians(json_camera_data["rotation_x"]), math.radians(json_camera_data["rotation_y"]), math.radians(json_camera_data["rotation_z"])))
    #camera.rotation_euler = (1.1, 0, 0.8)  # Orienter la caméra
    camera.rotation_euler = (math.radians(json_camera_data["rotation_x"]), math.radians(json_camera_data["rotation_y"]), math.radians(json_camera_data["rotation_z"]))  # Orienter la caméra
    camera.data.lens = json_camera_data["focale"]
    camera.data.clip_start = 0.1  # Distance minimale visible
    camera.data.clip_end = 5000.0

    # Définir la caméra active pour le rendu
    bpy.context.scene.camera = camera

    # Activer un éclairage ambiant dans le monde
    bpy.context.scene.world.use_nodes = True
    world_node_tree = bpy.context.scene.world.node_tree
    bg_node = world_node_tree.nodes["Background"]
    bg_node.inputs["Strength"].default_value = 5  # Augmenter l'éclairement ambiant




    # Définir les paramètres du rendu (résolution et format)
    bpy.context.scene.render.resolution_x = 1280
    bpy.context.scene.render.resolution_y = 720
    bpy.context.scene.render.image_settings.file_format = 'PNG'

    # Spécifier le chemin de sortie de l'image
    bpy.context.scene.render.filepath = chemin_enregistrement #"C:/Users/ReViVD/Documents/GitHub/tt-mmpose/votre_image.png"

    # Rendre l'image
    bpy.ops.render.render(write_still=True)

    print("Image enregistrée avec succès !")


def create_video_from_images(image_folder, output_path, fps=25):
    # Obtenir la liste des images dans le dossier, triée par nom
    images = sorted(glob.glob(os.path.join(image_folder, "*.png")))  # ou "*.jpg" selon le format d'image
    if not images:
        print("Aucune image trouvée dans le dossier.")
        return

    # Lire la première image pour obtenir les dimensions
    frame = cv2.imread(images[0])
    height, width, layers = frame.shape

    # Initialiser la vidéo avec les dimensions de l'image
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Utilise le codec MPEG-4 pour .mp4
    video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    images
    images.sort()
    images.sort(key=len)
    for image_path in images:
        frame = cv2.imread(image_path)
        video.write(frame)  # Ajouter chaque image en tant que frame de la vidéo

    video.release()
    print(f"Vidéo enregistrée à : {output_path}")


def create_video_3d(chemin_pose_3d,chemin_pose_balle_3d,chemin_json_camera,dossier_enregistrement,chemin_csv_enrichi,chemin_enregistrement):
    """
        Function to create 3d reconstruction of player's position
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
        if float(row[1]) == 1:
            liste_farme_joueur2.append(row)

    

    nb_frames = max(int(liste_farme_joueur1[-1][0]),int(liste_farme_joueur2[-1][0]),int(liste_pose_balle_3d[-1][0]))
    if not os.path.isdir(dossier_enregistrement):
        os.mkdir(dossier_enregistrement)
    for i in range(nb_frames):    
        enregistrement_image(i,os.path.join(dossier_enregistrement,str(i)+".jpg"),liste_farme_joueur1,liste_farme_joueur2,liste_pose_balle_3d,json_camera_data)

    create_video_from_images(dossier_enregistrement, chemin_enregistrement, fps=25)




   
if __name__ == "__main__":
    create_video_3d("exemple/set_1_point_8_position_joueur_grace_pieds.csv",
                    "exemple/set_1_point_8_zone_joueur_avec_pos_balle_3D.csv",
                    "exemple/PRITHIKA-PAVADE_vs_SIBEL-ALTINKAYA_camera.json",
                    "exemple/images",
                    "exemple/set_1_point_8_annotation_enrichi.csv",
                    "3d_video.mp4")