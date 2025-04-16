import bpy
import math
import mathutils
import os
import csv
import json
import numpy as np
 
def delete_all_objects():
    """Function to delete all objects
    """
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Select and delete all object in the scene
    
    for obj in bpy.context.scene.objects:
        obj.select_set(True)
    bpy.ops.object.delete()
                
def delete_players():
    """Delete players (delete all object excepted the table)
    """
    liste_nom = ["plateau","base","filet"]
    for obj in bpy.data.objects:
        if obj.name not in liste_nom and obj.type != 'CAMERA':
            obj = bpy.data.objects[obj.name]
            bpy.data.objects.remove(obj, do_unlink=True)
            
            
    

def delete_cube(width,height,depth,position,nom):
    """Create object cube (used to create table)

    Args:
        width (int): width
        height (int): height
        depth (int): depth
        location ((float,float,float)): cube location
        nom (str): name

    Returns:
        object: table object
    """
    bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=position)
    objet = bpy.context.object
    objet.scale = (width, depth, height)
    objet.name = nom
    return objet

def create_sphere(location, radius=1):
    """Create sphere

    Args:
        location ((float,float,float)): sphere location
        radius (int): sphere radius. Defaults to 1.

    Returns:
        object: sphere object
    """
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=location)
    sphere = bpy.context.object
    sphere.name = "Sphere"
    return sphere

def create_cylinder_between(start, end, radius=0.5):
    """Create a clinder

    Args:
        start ((float,float,float)): Start location
        end ((float,float,float)): end location
        radius (float): Cylinder radius. Defaults to 0.5.

    Returns:
        object: cylinder
    """
    # Calculating the distance between the two points
    start_vec = mathutils.Vector(start)
    end_vec = mathutils.Vector(end)
    distance = (end_vec - start_vec).length

    # Create a cylinder with a height of 1, then resize it
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=1, location=(0, 0, 0))
    cylinder = bpy.context.object
    cylinder.name = "Cylinder"

    # Position the cylinder in the middle of the two points
    cylinder.location = (start_vec + end_vec) / 2

    cylinder.scale[2] = distance

    # Calculating the rotation to align the cylinder between the two points
    direction = end_vec - start_vec
    rotation_quaternion = direction.to_track_quat('Z', 'Y')
    cylinder.rotation_euler = rotation_quaternion.to_euler()

    return cylinder



def move_object(obj, new_location):
    """Move object

    Args:
        obj (object): Object to move
        new_location ((float,float,float)): New location
    """
    obj.location = new_location

def set_camera_position(camera, location, look_at=None):
    """Moves the camera to a given position and, if specified, orients the camera to a point.

    Args:
        camera (object): Camera object
        location ((float,float,float)): new location
        look_at ((float,float,float)): Orientation. Defaults to None.
    """
    if camera is None:
        print("Error : no camera is defined in the scene.")
        return
    
    camera.location = location
    direction = mathutils.Vector(look_at)

    if look_at is not None:
        up = mathutils.Vector((0, 0, 1))

        rot_matrix = mathutils.Matrix.LocRotScale(
            location,
            direction.to_track_quat('Z', 'Y'),
            mathutils.Vector((1, 1, 1))
        ).to_3x3()

        camera.rotation_euler = rot_matrix.to_euler()

def create_empty_sphere(position,nom_point,nom_collection):
    """Creates an Empty sphere object of type sphere at the given position and adds it to a collection nom_collection.

    Args:
        position ((float,float,float)): location
        nom_point (str): name
        nom_collection (str): collection name
    """
    if nom_collection not in bpy.data.collections:
        point3d_collection = bpy.data.collections.new(nom_collection)
        bpy.context.scene.collection.children.link(point3d_collection)
    else:
        point3d_collection = bpy.data.collections[nom_collection]

    bpy.ops.object.empty_add(type='SPHERE', location=position)
    empty = bpy.context.object 
    
    empty.name = nom_point
    point3d_collection.objects.link(empty)

    if empty.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(empty)

def draw_ball(location, radius=1):
    """Creates a white sphere at a given position with a specific radius.

    Args:
        location ((float,float,float)): location
        radius (int): Ball radius. Defaults to 1.
    """
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location)
    sphere = bpy.context.object 
    sphere.name = "WhiteSphere"
    
    mat = bpy.data.materials.get("WhiteMaterial")
    if mat is None:
        mat = bpy.data.materials.new(name="WhiteMaterial")
    
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (1, 1, 1, 1)
        bsdf.inputs["Roughness"].default_value = 0.5

    if sphere.data.materials:
        sphere.data.materials[0] = mat
    else:
        sphere.data.materials.append(mat)

def recuperation_points_table(json_path):
    """Function to retrieve table corners

    Args:
        json_path (str): perspective json path
    Returns:
        List: List containing the position of the 4 table corners 
    """

    with open(json_path) as json_file:
        json_course = json.load(json_file)

    scr_pct1 = json_course['calibration']['srcPct1']
    src_pts1 = np.float32(list(map(lambda x: list(x.values()), scr_pct1)))

    src_pts1 = np.float32(json_course['homography']['srcPts'])

    return(src_pts1)

def animation(scene):
    """Function to animate ball position in blender scene

    Args:
        scene (object): scene object

    Returns:
        object: sphere object of the ball
    """
    delete_players()
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
    text_obj1.data.size = 20
    text_obj1.location = (moyenne[0], moyenne[1] if np.sign(moyenne[1]) == -1 else 137, 76)
    text_obj1.rotation_euler[0] = math.radians(90)
    text_obj1.rotation_euler[1] = math.radians(0)
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
    text_obj2.data.size = 20
    text_obj2.location = (moyenne[0], moyenne[1] if np.sign(moyenne[1]) == -1 else 137, 76) 
    text_obj2.rotation_euler[0] = math.radians(90) 
    text_obj2.rotation_euler[1] = math.radians(0)  
    text_obj2.rotation_euler[2] = math.radians(90)


    for row in liste_pose_balle_3d:
        if int(row[1]) == 4 and int(row[0]) == scene.frame_current:
            draw_ball((float(row[2]),float(row[3]),float(row[4])+76),2)

    sphere = bpy.context.object
    sphere.name = "Sphere"
    return sphere
    
if __name__ == "__main__":
    #chemin_pose_3d = os.path.join("example","/set_1_point_0/position_files/set_1_point_0_pose_3d_mmpose.csv")
    chemin_pose_3d = os.path.join("example","set_1_point_0","position_files","set_1_point_0_pose_2d_mmpose_convertion_3d.csv")
    chemin_pose_balle_3d = os.path.join("example","set_1_point_0","position_files","set_1_point_0_zone_joueur_avec_pos_balle_3D.csv")
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

    delete_all_objects()
    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_post.clear()

    bpy.app.handlers.render_pre.clear()
    bpy.app.handlers.render_post.clear()

    bpy.app.handlers.load_pre.clear()
    bpy.app.handlers.load_post.clear()


    bpy.app.handlers.frame_change_pre.append(animation)
    plateau = delete_cube(152,10,274,(0, 0, 76-5),"plateau")
    filet = delete_cube(180,15,0.1,(0, 0, 76+7.5),"filet")
    base = delete_cube(90,76-10,90,(0, 0, 76/2-5),"base")
    
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
            draw_ball((float(row[2]),float(row[3]),float(row[4])+76),2)


    
    sphere1 = create_empty_sphere((-152/2,274/2,76),"sphere1","points3d")
    sphere2 = create_empty_sphere((152/2,274/2,76),"sphere2","points3d")
    sphere3 = create_empty_sphere((152/2,-274/2,76),"sphere3","points3d")
    sphere4 = create_empty_sphere((-152/2,-274/2,76),"sphere4","points3d")
    sphere5 = create_empty_sphere((152/2,0,76),"sphere5","points3d")
    sphere6 = create_empty_sphere((-152/2,0,76),"sphere6","points3d")




    