"""import bpy

class TestPanel(bpy.types.Panel):
    bl_label = "Object Adder"
    bl_idname = "PT_TestPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'My 1st Addon'
   
    def draw(self, context):
        layout = self.layout
       
        row = layout.row()
        row.label(text= "Add an object", icon= 'OBJECT_ORIGIN')
        row = layout.row()
        row.operator("mesh.primitive_cube_add", icon= 'CUBE')
       
        row.operator("mesh.primitive_uv_sphere_add", icon= 'SPHERE')
        row = layout.row()
        row.operator("object.text_add", icon= 'FILE_FONT', text= "Font Button")
       
       
       
       
def register():
    bpy.utils.register_class(TestPanel)
   
def unregister():
    bpy.utils.unregister_class(TestPanel)
   
if __name__ == "__main__":
    register()"""
    
import bpy
import math
import mathutils
import os
import csv
import json
import numpy as np
 
def supprimer_tous_objets():
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Sélectionner et supprimer tous les objets dans la scène
    
    for obj in bpy.context.scene.objects:
        obj.select_set(True)
    bpy.ops.object.delete()
                
def supprimer_joueurs_table():
    liste_nom = ["plateau","base","filet"]#,"ALEXIS-LEBRUN_vs_FAN-ZHENDONG.jpg"]
    for obj in bpy.data.objects:
        if obj.name not in liste_nom and obj.type != 'CAMERA':
            # Récupérer l'objet
            obj = bpy.data.objects[obj.name]
            
            # Le sélectionner et le supprimer
            bpy.data.objects.remove(obj, do_unlink=True)
            
            
    

def creation_table(width,height,depth,position,nom):


    # Créer un cube à l'origine et le redimensionner pour créer le parallélépipède
    bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=position)

    # Récupérer l'objet cube nouvellement créé
    objet = bpy.context.object

    # Appliquer une échelle pour correspondre aux dimensions souhaitées
    objet.scale = (width, depth, height)

    # Nommer l'objet pour i
    objet.name = nom
    return objet

def create_sphere(location, radius=1):
    """
    Crée une sphère de rayon spécifié à la position donnée.
    
    :param location: Tuple des coordonnées (x, y, z) pour positionner la sphère.
    :param radius: Rayon de la sphère.
    :return: L'objet sphère créé.
    """
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=location)
    sphere = bpy.context.object
    sphere.name = "Sphere"
    return sphere

def create_cylinder_between(start, end, radius=0.5):
    """
    Crée un cylindre entre deux points donnés, avec un rayon spécifié.
    
    :param start: Tuple des coordonnées (x, y, z) du point de départ.
    :param end: Tuple des coordonnées (x, y, z) du point d'arrivée.
    :param radius: Rayon du cylindre.
    :return: L'objet cylindre créé.
    """
    # Calcul de la distance entre les deux points
    start_vec = mathutils.Vector(start)
    end_vec = mathutils.Vector(end)
    distance = (end_vec - start_vec).length

    # Créer un cylindre avec une hauteur de 1, puis le redimensionner
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=1, location=(0, 0, 0))
    cylinder = bpy.context.object
    cylinder.name = "Cylinder"

    # Positionner le cylindre au milieu des deux points
    cylinder.location = (start_vec + end_vec) / 2

    # Redimensionner le cylindre pour correspondre à la distance
    cylinder.scale[2] = distance

    # Calcul de la rotation pour aligner le cylindre entre les deux points
    direction = end_vec - start_vec
    rotation_quaternion = direction.to_track_quat('Z', 'Y')
    cylinder.rotation_euler = rotation_quaternion.to_euler()

    return cylinder



def move_object(obj, new_location):
    """
    Déplace l'objet spécifié aux nouvelles coordonnées.
    
    :param obj: L'objet à déplacer.
    :param new_location: Tuple des nouvelles coordonnées (x, y, z).
    """
    obj.location = new_location

def set_camera_position(camera, location, look_at=None):
    """
    Déplace la caméra à une position donnée et, si spécifié, oriente la caméra vers un point.

    :param camera: L'objet caméra à manipuler.
    :param location: Tuple (x, y, z) représentant la nouvelle position de la caméra.
    :param look_at: (Optionnel) Tuple (x, y, z) représentant le point à regarder.
    """
    # Définir la position de la caméra
    camera.location = location

    # Si un point de visée est fourni, orienter la caméra vers ce point
    if look_at is not None:
        # Calculer la direction de visée
        direction = mathutils.Vector(look_at) - camera.location
        # Calculer la rotation pour regarder dans la direction
        rot_quaternion = direction.to_track_quat('Z', 'Y')
        # Appliquer la rotation à la caméra
        camera.rotation_euler = rot_quaternion.to_euler()

def set_camera_position(camera, location, look_at=None):
        """
        Déplace la caméra à une position donnée et, si spécifié, oriente la caméra vers un point.

        :param camera: L'objet caméra à manipuler.
        :param location: Tuple (x, y, z) représentant la nouvelle position de la caméra.
        :param look_at: (Optionnel) Tuple (x, y, z) représentant le point à regarder.
        """
        # Vérifie si l'objet caméra est valide
        if camera is None:
            print("Erreur : aucune caméra n'est définie dans la scène.")
            return
        
        # Définir la position de la caméra
        camera.location = location
        direction = mathutils.Vector(look_at)

        # Si un point de visée est fourni, orienter la caméra vers ce point
        if look_at is not None:
            #direction = (target_position - camera.location).normalized()
            #rot_quaternion = direction.to_track_quat('Z', 'Y')
            up = mathutils.Vector((0, 0, 1))

            # Calculer la matrice de rotation LookAt
            rot_matrix = mathutils.Matrix.LocRotScale(
                location,
                direction.to_track_quat('Z', 'Y'),
                mathutils.Vector((1, 1, 1))
            ).to_3x3()

            camera.rotation_euler = rot_matrix.to_euler()

def create_empty_sphere(position,nom_point,nom_collection):
    """
    Crée un objet Empty de type sphère à la position donnée 
    et l'ajoute dans une collection nom_collection.
    
    :param position: tuple (x, y, z) représentant la position de la sphère
    """
    # Vérifie si la collection 'point3d' existe, sinon la crée
    if nom_collection not in bpy.data.collections:
        point3d_collection = bpy.data.collections.new(nom_collection)
        bpy.context.scene.collection.children.link(point3d_collection)
    else:
        point3d_collection = bpy.data.collections[nom_collection]

    # Ajouter un objet Empty de type SPHERE à la position spécifiée
    bpy.ops.object.empty_add(type='SPHERE', location=position)
    empty = bpy.context.object  # Référence vers l'objet ajouté
    
    # Nommer l'objet Empty
    empty.name = nom_point
    point3d_collection.objects.link(empty)

    # Ajouter l'objet Empty à la collection 'point3d' et le retirer de la collection globale
    if empty.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(empty)

def tracer_balle(location, radius=1):
    """
    Crée une sphère blanche à une position donnée avec un rayon spécifique.
    
    :param location: tuple (x, y, z) représentant la position de la sphère
    :param radius: taille de la sphère (par défaut 1)
    """
    # Ajouter une sphère à la position spécifiée avec le rayon donné
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location)
    sphere = bpy.context.object  # Obtenir la référence de l'objet sphère créé
    sphere.name = "WhiteSphere"
    
    # Créer un matériau blanc
    mat = bpy.data.materials.get("WhiteMaterial")
    if mat is None:
        mat = bpy.data.materials.new(name="WhiteMaterial")
    
    mat.use_nodes = True  # Activer les nodes pour le matériau
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (1, 1, 1, 1)  # Blanc
        bsdf.inputs["Roughness"].default_value = 0.5  # Légèrement réfléchissant

    # Assigner le matériau à la sphère
    if sphere.data.materials:
        sphere.data.materials[0] = mat
    else:
        sphere.data.materials.append(mat)

def recuperation_points_table(json_path):
    """
    Fonction permettant de ressortir les points enregistrés pour l'homographie (généralement les coins de la table)
    Entrée: Le chemin du json contenant les points pour l'homographie
    Sortie: un éléments contenant les points
    """

    with open(json_path) as json_file:
        json_course = json.load(json_file)

    # we convert to a flat array [[20,10],[80,10],[95,90],[5,90]]
    scr_pct1 = json_course['calibration']['srcPct1']
    src_pts1 = np.float32(list(map(lambda x: list(x.values()), scr_pct1)))

    src_pts1 = np.float32(json_course['homography']['srcPts'])

    return(src_pts1)

def animation(scene):
    """
    Crée une sphère de rayon spécifié à la position donnée.
    
    :param location: Tuple des coordonnées (x, y, z) pour positionner la sphère.
    :param radius: Rayon de la sphère.
    :return: L'objet sphère créé.
    """
    supprimer_joueurs_table()
    create_sphere(((445.9006744421334, -1043.8479120954487, 76)), radius=5)
    create_sphere(((351.29387231437613, -987.0047081181731, 76)), radius=5)
    create_sphere(((251.3677907393966, -2692.7569235527067, 76)), radius=5)
    create_sphere(((463.65536843358586, -2416.0113300113962, 76)), radius=5)

    liste_centre_farme_joueur1 = []
    for row in liste_farme_joueur1:
        if int(row[0]) == scene.frame_current:
            create_sphere((float(row[3]),float(row[4]),float(row[5])), radius=5)
            liste_centre_farme_joueur1.append([float(row[3]),float(row[4])])
    points_array = np.array(liste_centre_farme_joueur1)
    moyenne = points_array.mean(axis=0)
    create_cylinder_between((moyenne[0],moyenne[1],0), (moyenne[0],moyenne[1],76), radius=1)
    create_cylinder_between((moyenne[0],moyenne[1],76), (moyenne[0],np.sign(moyenne[1])*137,76), radius=0.5)
    bpy.ops.object.text_add(location=(0, 0, 0))
    text_obj1 = bpy.context.object
    text_obj1.data.body = str(abs(int(moyenne[1]))-137)+"cm"
    text_obj1.data.size = 20  # Taille du texte
    text_obj1.location = (moyenne[0], moyenne[1] if np.sign(moyenne[1]) == -1 else 137, 76)  # Position de l'objet texte
    text_obj1.rotation_euler[0] = math.radians(90)   # Rotation autour de X (en radians)
    text_obj1.rotation_euler[1] = math.radians(0)   # Rotation autour de Y
    text_obj1.rotation_euler[2] = math.radians(90)

    liste_centre_farme_joueur2 = []
    for row in liste_farme_joueur2:
        if int(row[0]) == scene.frame_current:
            create_sphere((float(row[3]),float(row[4]),float(row[5])), radius=5)
            liste_centre_farme_joueur2.append([float(row[3]),float(row[4])])
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
    text_obj2.rotation_euler[2] = math.radians(90)


    for row in liste_pose_balle_3d:
        if int(row[1]) == 4 and int(row[0]) == scene.frame_current:
            tracer_balle((float(row[2]),float(row[3]),float(row[4])+76),2)

    #bpy.ops.mesh.primitive_uv_sphere_add(radius=10, enter_editmode=False, align='WORLD', location=(0,scene.frame_current*20,90))
    sphere = bpy.context.object
    sphere.name = "Sphere"
    return sphere
    
if __name__ == "__main__":
    competition = "2021_ChEuropeF_ClujNapoca"
    match = "PRITHIKA-PAVADE_vs_SIBEL-ALTINKAYA"
    point = "set_1_point_0"
    dossier = os.path.join("C:/Users/ReViVD/Desktop/dataroom/pipeline-tt",competition,match)
    chemin_pose_3d = os.path.join("C:/Users/ReViVD/Desktop/dataroom/pipeline-tt/2024_ChMondeEquipe_Busan/FAN-ZHENDONG_vs_ALEXIS-LEBRUN/clips/set_1_point_0/csv_json_openpose/set_1_point_0_pose_3d_mmpose.csv")
    chemin_pose_3d = os.path.join("C:/Users/ReViVD/Desktop/dataroom/pipeline-tt/2024_ChMondeEquipe_Busan/FAN-ZHENDONG_vs_ALEXIS-LEBRUN/clips/set_1_point_0/csv_json_openpose/set_1_point_0_pose_2d_mmpose_convertion_3d.csv")
    chemin_pose_3d = os.path.join(dossier,"clips",point,"csv_json_openpose/",point+"_pose_2d_mmpose_convertion_3d.csv")
    #chemin_pose_3d = os.path.join("C:/Users/ReViVD/Desktop/dataroom/pipeline-tt/2024_ChMondeEquipe_Busan/FAN-ZHENDONG_vs_ALEXIS-LEBRUN/clips/set_1_point_0/csv_json_openpose/set_1_point_0_pose_3d_final.csv")
    chemin_pose_balle_3d = os.path.join(dossier,"clips",point,"csv_json_openpose/",point+"_zone_joueur_avec_pos_balle_3D.csv")
    #points_table = recuperation_points_table(os.path.join("C:/Users/ReViVD/Desktop/dataroom/pipeline-tt/2024_ChMondeEquipe_Busan/FAN-ZHENDONG_vs_ALEXIS-LEBRUN/FAN-ZHENDONG_vs_ALEXIS-LEBRUN_perspective.json"))
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


    frame = bpy.context.scene.frame_current
    liste_farme_joueur1 = []
    for row in liste_pose_3d:
        if float(row[6]) == 0:
            liste_farme_joueur1.append(row)
    liste_farme_joueur2 = []
    for row in liste_pose_3d:
        if float(row[6]) == 1:
            liste_farme_joueur2.append(row)
    
    liste_farme_arbitre = []
    for row in liste_pose_3d:
        if float(row[6]) == 2:
            liste_farme_arbitre.append(row)

    supprimer_tous_objets()
    # Supprimer tous les handlers du changement de frame
    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_post.clear()

    # Supprimer tous les handlers du rendu
    bpy.app.handlers.render_pre.clear()
    bpy.app.handlers.render_post.clear()

    # Supprimer tous les handlers du chargement de scène
    bpy.app.handlers.load_pre.clear()
    bpy.app.handlers.load_post.clear()


    #bpy.app.handlers.frame_change_pre.append(supprimer_joueurs_table)
    bpy.app.handlers.frame_change_pre.append(animation)
    plateau = creation_table(152,10,274,(0, 0, 76-5),"plateau")
    filet = creation_table(180,15,0.1,(0, 0, 76+7.5),"filet")
    base = creation_table(90,76-10,90,(0, 0, 76/2-5),"base")

    """keypoint_Nose_j1 = create_sphere((0,-200,165), radius=5)
    keypoint_Left_Eye_j1 = create_sphere((-5,-200,167), radius=5)
    keypoint_Right_Eye_j1 = create_sphere((5,-200,167), radius=5)
    keypoint_Left_Ear_j1 = create_sphere((-7,-200,165), radius=5)
    keypoint_Right_Ear_j1 = create_sphere((7,-200,165), radius=5)
    keypoint_Left_Shoulder_j1 = create_sphere((-10,-200,150), radius=5)
    keypoint_Right_Shoulder_j1 = create_sphere((10,-200,150), radius=5)
    keypoint_Left_Elbow_j1 = create_sphere((-50,-200,150), radius=5)
    keypoint_Right_Elbow_j1 = create_sphere((50,-200,150), radius=5)
    keypoint_Left_Wrist_j1 = create_sphere((-100,-200,150), radius=5)
    keypoint_Right_Wrist_j1 = create_sphere((100,-200,150), radius=5)
    keypoint_Left_Hip_j1 = create_sphere((-10,-200,90), radius=5)
    keypoint_Right_Hip_j1 = create_sphere((10,-200,90), radius=5)
    keypoint_Left_Knee_j1 = create_sphere((-10,-200,40), radius=5)
    keypoint_Right_Knee_j1 = create_sphere((10,-200,40), radius=5)
    keypoint_Left_Ankle_j1 = create_sphere((-10,-200,0), radius=5)
    keypoint_Right_Ankle_j1 = create_sphere((10,-200,0), radius=5)
    
    cylindre_Right_Ankle_Right_Knee_j1 = create_cylinder_between((10,-200,0), (10,-200,40), radius=0.5)
    cylindre_Left_Ankle_Left_Knee_j1 = create_cylinder_between((-10,-200,0), (-10,-200,40), radius=0.5)
    cylindre_Right_Knee_Right_Hip_j1 = create_cylinder_between((10,-200,40), (10,-200,90), radius=0.5)
    cylindre_Left_Knee_Left_Hip_j1 = create_cylinder_between((-10,-200,40), (-10,-200,90), radius=0.5)
    cylindre_Right_Hip_Right_Shoulder_j1 = create_cylinder_between((10,-200,90), (10,-200,150), radius=0.5)
    cylindre_Left_Hip_Left_Shoulder_j1 = create_cylinder_between((-10,-200,90), (-10,-200,150), radius=0.5)
    cylindre_Right_Shoulder_Right_Elbow_j1 = create_cylinder_between((10,-200,150), (50,-200,150), radius=0.5)
    cylindre_Left_Shoulder_Left_Elbow_j1 = create_cylinder_between((-10,-200,150), (-50,-200,150), radius=0.5)
    cylindre_Right_Elbow_Right_Wrist_j1 = create_cylinder_between((50,-200,150), (100,-200,150), radius=0.5)
    cylindre_Left_Elbow_Left_Wrist_j1 = create_cylinder_between((-50,-200,150), (-100,-200,150), radius=0.5)
    
    cylindre_Right_Shoulder_Right_Ear_j1 = create_cylinder_between((10,-200,150), (7,-200,165), radius=0.5)
    cylindre_Left_Shoulder_Left_Ear_j1 = create_cylinder_between((-10,-200,150), (-7,-200,165), radius=0.5)
    cylindre_Right_Ear_Right_Eye_j1 = create_cylinder_between((7,-200,165), (5,-200,167), radius=0.5)
    cylindre_Left_Ear_Left_Eye_j1 = create_cylinder_between((-7,-200,165), (-5,-200,167), radius=0.5)
    cylindre_Right_Eye_Nose_j1 = create_cylinder_between((5,-200,167), (0,-200,165), radius=0.5)
    cylindre_Left_Eye_Nose_j1 = create_cylinder_between((-5,-200,167), (0,-200,165), radius=0.5)




    
    keypoint_Nose_j2 = create_sphere((0,200,165), radius=5)
    keypoint_Left_Eye_j2 = create_sphere((-5,200,167), radius=5)
    keypoint_Right_Eye_j2 = create_sphere((5,200,167), radius=5)
    keypoint_Left_Ear_j2 = create_sphere((-7,200,165), radius=5)
    keypoint_Right_Ear_j2 = create_sphere((7,200,165), radius=5)
    keypoint_Left_Shoulder_j2 = create_sphere((-10,200,150), radius=5)
    keypoint_Right_Shoulder_j2 = create_sphere((10,200,150), radius=5)
    keypoint_Left_Elbow_j2 = create_sphere((-50,200,150), radius=5)
    keypoint_Right_Elbow_j2 = create_sphere((50,200,150), radius=5)
    keypoint_Left_Wrist_j2 = create_sphere((-100,200,150), radius=5)
    keypoint_Right_Wrist_j2 = create_sphere((100,200,150), radius=5)
    keypoint_Left_Hip_j2 = create_sphere((-10,200,90), radius=5)
    keypoint_Right_Hip_j2 = create_sphere((10,200,90), radius=5)
    keypoint_Left_Knee_j2 = create_sphere((-10,200,40), radius=5)
    keypoint_Right_Knee_j2 = create_sphere((10,200,40), radius=5)
    keypoint_Left_Ankle_j2 = create_sphere((-10,200,0), radius=5)
    keypoint_Right_Ankle_j2 = create_sphere((10,200,0), radius=5)
    
    
    cylindre_Right_Ankle_Right_Knee_j1 = create_cylinder_between((10,200,0), (10,200,40), radius=0.5)
    cylindre_Left_Ankle_Left_Knee_j2 = create_cylinder_between((-10,200,0), (-10,200,40), radius=0.5)
    cylindre_Right_Knee_Right_Hip_j2 = create_cylinder_between((10,200,40), (10,200,90), radius=0.5)
    cylindre_Left_Knee_Left_Hip_j2 = create_cylinder_between((-10,200,40), (-10,200,90), radius=0.5)
    cylindre_Right_Hip_Right_Shoulder_j2 = create_cylinder_between((10,200,90), (10,200,150), radius=0.5)
    cylindre_Left_Hip_Left_Shoulder_j2 = create_cylinder_between((-10,200,90), (-10,200,150), radius=0.5)
    cylindre_Right_Shoulder_Right_Elbow_j2 = create_cylinder_between((10,200,150), (50,200,150), radius=0.5)
    cylindre_Left_Shoulder_Left_Elbow_j2 = create_cylinder_between((-10,200,150), (-50,200,150), radius=0.5)
    cylindre_Right_Elbow_Right_Wrist_j2 = create_cylinder_between((50,200,150), (100,200,150), radius=0.5)
    cylindre_Left_Elbow_Left_Wrist_j2 = create_cylinder_between((-50,200,150), (-100,200,150), radius=0.5)
    
    cylindre_Right_Shoulder_Right_Ear_j2 = create_cylinder_between((10,200,150), (7,200,165), radius=0.5)
    cylindre_Left_Shoulder_Left_Ear_j2 = create_cylinder_between((-10,200,150), (-7,200,165), radius=0.5)
    cylindre_Right_Ear_Right_Eye_j2 = create_cylinder_between((7,200,165), (5,200,167), radius=0.5)
    cylindre_Left_Ear_Left_Eye_j2 = create_cylinder_between((-7,200,165), (-5,200,167), radius=0.5)
    cylindre_Right_Eye_Nose_j2 = create_cylinder_between((5,200,167), (0,200,165), radius=0.5)
    cylindre_Left_Eye_Nose_j2 = create_cylinder_between((-5,200,167), (0,200,165), radius=0.5)"""
    
    create_sphere(((762.9176027138635, -545.9278031802423, 76)), radius=5)
    create_sphere(((713.3769726927287, -516.161992750974, 76)), radius=5)
    create_sphere(((661.0509144661461, -1409.3751392904687, 76)), radius=5)
    create_sphere(((772.2148065764487, -1264.4579583768252, 76)), radius=5)

    

    liste_centre_farme_joueur1 = []
    for row in liste_farme_joueur1:
        if int(row[0]) == frame:
            create_sphere((float(row[3]),float(row[4]),float(row[5])), radius=5)
            liste_centre_farme_joueur1.append([float(row[3]),float(row[4])])
    points_array = np.array(liste_centre_farme_joueur1)
    moyenne = points_array.mean(axis=0)
    create_cylinder_between((moyenne[0],moyenne[1],0), (moyenne[0],moyenne[1],76), radius=1)
    create_cylinder_between((moyenne[0],moyenne[1],76), (moyenne[0],np.sign(moyenne[1])*137,76), radius=0.5)
    bpy.ops.object.text_add(location=(0, 0, 0))

    text_obj1 = bpy.context.object
    text_obj1.data.body = str(abs(int(moyenne[1]))-137)+"cm"
    text_obj1.data.size = 20  # Taille du texte
    text_obj1.location = (moyenne[0], moyenne[1] if np.sign(moyenne[1]) == -1 else 137, 76)  # Position de l'objet texte
    text_obj1.rotation_euler[0] = math.radians(90)   # Rotation autour de X (en radians)
    text_obj1.rotation_euler[1] = math.radians(0)   # Rotation autour de Y
    text_obj1.rotation_euler[2] = math.radians(90)

    liste_centre_farme_joueur2 = []
    for row in liste_farme_joueur2:
        if int(row[0]) == frame:
            create_sphere((float(row[3]),float(row[4]),float(row[5])), radius=5)
            liste_centre_farme_joueur2.append([float(row[3]),float(row[4])])
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
    text_obj2.rotation_euler[2] = math.radians(90)



    for row in liste_farme_arbitre:
        if int(row[0]) == frame:
            create_sphere((float(row[3]),float(row[4]),float(row[5])), radius=5)


    for row in liste_pose_balle_3d:
        if int(row[1]) == 4 and int(row[0]) == frame:
            tracer_balle((float(row[2]),float(row[3]),float(row[4])+76),2)


    """camera = bpy.context.scene.camera
    
    # Exemple d'utilisation
    if camera is None:
        # Créer une nouvelle caméra si aucune n'existe
        bpy.ops.object.camera_add(location=(0, 0, 10))
        camera = bpy.context.object
        bpy.context.scene.camera = camera  # Définir la nouvelle caméra comme caméra active


    # Nouvelle position pour la caméra
    #new_position = (1260.3195480939117, -51.22700635113004, 2398.5393302470033)
    new_position = (200, 0, 200)

    # Point à regarder
    look_at_point = (0, 0, 0)

    set_camera_position(camera, new_position, look_at=look_at_point)"""

    
    sphere1 = create_empty_sphere((-152/2,274/2,76),"sphere1","points3d")
    sphere2 = create_empty_sphere((152/2,274/2,76),"sphere2","points3d")
    sphere3 = create_empty_sphere((152/2,-274/2,76),"sphere3","points3d")
    sphere4 = create_empty_sphere((-152/2,-274/2,76),"sphere4","points3d")
    sphere5 = create_empty_sphere((152/2,0,76),"sphere5","points3d")
    sphere6 = create_empty_sphere((-152/2,0,76),"sphere6","points3d")


    """bpy.ops.object.camera_add(location=(770.38, 3.7689, 437.04))
    camera = bpy.context.object
    camera.rotation_euler = (math.radians(65.87), math.radians(-0.3039), math.radians(90.478))
    # Ajouter un cube à la scène
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))

    
    # Ajouter une lumière avec une intensité élevée
    bpy.ops.object.light_add(type='POINT', location=(5, -5, 5))
    light = bpy.context.object
    light.data.energy = 1000  # Augmenter l'énergie de la lumière

    # Ajouter une lumière secondaire pour améliorer l'éclairage
    bpy.ops.object.light_add(type='POINT', location=(-5, -5, 5))
    second_light = bpy.context.object
    second_light.data.energy = 500  # Ajuster l'énergie de la lumière secondaire



    #bpy.ops.object.light_add(type='SUN', location=(0, 0, 80))
    # Ajouter une lumière du type 'SUN' pour un éclairage global
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 80))
    sun_light = bpy.context.object
    sun_light.data.energy = 100  # Ajuster l'intensité de la lumière du soleil


    # Définir la caméra ajoutée comme caméra active
    bpy.context.scene.camera = camera

    
    # Activer un éclairage ambiant dans le monde
    bpy.context.scene.world.use_nodes = True
    world_node_tree = bpy.context.scene.world.node_tree
    bg_node = world_node_tree.nodes["Background"]
    bg_node.inputs["Strength"].default_value = 5  # Augmenter l'éclairement ambiant

    
    # Définir les paramètres du rendu (résolution et format)
    bpy.context.scene.render.resolution_x = 640
    bpy.context.scene.render.resolution_y = 480
    bpy.context.scene.render.image_settings.file_format = 'PNG'


    bpy.context.scene.render.filepath = "C:/Users/ReViVD/Desktop/dataroom/pipeline-tt/2024_ChMondeEquipe_Busan/FAN-ZHENDONG_vs_ALEXIS-LEBRUN/clips/set_1_point_0/set_1_point_0_animation_3d.png"  # Chemin de sauvegarde de la vidéo
    

    # Rendre et enregistrer l'image
    bpy.ops.render.render(write_still=True)"""




    