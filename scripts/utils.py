import numpy as np
import csv
import os
import json
import pandas as pd



def create_json_camera(name_output_csv,focale,centre_optique,distorsion_k1,distorsion_k2,distorsion_k3,position,rotation):
    """Function used to create json file with cam params

    Args:
        name_output_csv (str): Output path
        focale (float): Focal length
        centre_optique (float): Optical center
        distorsion_k1 (float): Distorsion K1
        distorsion_k2 (float): Distorsion K2
        distorsion_k3 (float): Distorsion K3
        position ((int,int,int)): Location
        rotation ((float,float,float)): Rotation
    """

    donnees = {}

    donnees["focale"] = focale
    donnees["centre_optique_x"] = centre_optique[0]
    donnees["centre_optique_y"] = centre_optique[1]
    donnees["distorsion_k1"] = distorsion_k1
    donnees["distorsion_k2"] = distorsion_k2
    donnees["distorsion_k3"] = distorsion_k3
    donnees["position_x"] = position[0]
    donnees["position_y"] = position[1]
    donnees["position_z"] = position[2]
    donnees["rotation_x"] = rotation[0]
    donnees["rotation_y"] = rotation[1]
    donnees["rotation_z"] = rotation[2]

    with open(name_output_csv, "w") as json_file:
        json.dump(donnees, json_file, indent=4)


def create_csv_position_using_feet(csv_position):
    """
        Function used to create csv file of players' positions, using the projection of the players' feet from 2d pose estimation to 3d scene
        
        Args:
                - Csv file of players' pose estimation
        Returns:
                - Create csv file (_position_joueur_grace_pieds.csv)
    """


    df_position = pd.read_csv(csv_position)

    nb_frame = df_position["frame"].max()+1
    nb_personnes = df_position[df_position["frame"] <= 3]["numero_pers"].max()+1

    liste = []
    for i in range(nb_frame):
        for j in range(nb_personnes):
            df_frame_pers = df_position[(df_position['frame'] == i) & (df_position['tracking'] == j)]
            if len(df_frame_pers[df_frame_pers["joint"] == 15]) > 0 and len(df_frame_pers[df_frame_pers["joint"] == 16]) > 0:
                x = (df_frame_pers[df_frame_pers["joint"] == 15].iloc[0]["x"] + df_frame_pers[df_frame_pers["joint"] == 16].iloc[0]["x"])/2
                y = (df_frame_pers[df_frame_pers["joint"] == 15].iloc[0]["y"] + df_frame_pers[df_frame_pers["joint"] == 16].iloc[0]["y"])/2
                liste.append([i,j,x,y,0])

    header = ["frame","numero_pers","distance_x","distance_y","distance_z"]
    with open(csv_position.replace('_pose_2d_mmpose_convertion_3d.csv','_position_joueur_grace_pieds.csv'),"w", newline='') as fichier_csv:
        fichier_csv_writer = csv.writer(fichier_csv, delimiter=',')
        fichier_csv_writer.writerow(header)
        for row in liste:
            fichier_csv_writer.writerow(row)


def match_players_feet(csv_position_pieds):
    """
        Function used to match players' number from csv file "_zone_joueur_avec_pos_balle.csv" already generated using feet position
        Args:
                - Csv "_position_joueur_grace_pieds.csv" path
        Returns :
                - Create csv players' position
    """
    csv_position = csv_position_pieds.replace("_position_joueur_grace_pieds.csv","_zone_joueur_avec_pos_balle.csv")

    df_position_pieds = pd.read_csv(csv_position_pieds)
    df_position = pd.read_csv(csv_position)
    
    nb_personnes = df_position_pieds[df_position_pieds["frame"] <= 1]["numero_pers"].max()+1

    liste_correspondances = []
    for i in range(2):
        liste_distances = []
        for j in range(nb_personnes):
            df_position_filtre = df_position[(df_position["frame"] == 0) & (df_position["numero_pers"] == i)]
            df_position_pieds_filtre = df_position_pieds[(df_position_pieds["frame"] == 0) & (df_position_pieds["numero_pers"] == j)]
            if len(df_position_filtre) > 0 and len(df_position_pieds_filtre) > 0:
                distance = np.sqrt((df_position_filtre.iloc[0]["distance_x"] - df_position_pieds_filtre.iloc[0]["distance_x"])**2 + (df_position_filtre.iloc[0]["distance_y"] - df_position_pieds_filtre.iloc[0]["distance_y"])**2)
                liste_distances.append(distance)
            else:
                liste_distances.append(1000)
        if len(liste_correspondances) == 1:
            liste_distances[liste_correspondances[0]] = 10000
        liste_correspondances.append(np.argmin(liste_distances))
    print(liste_correspondances)
    
    fichier_lecture = open(csv_position_pieds,"r")
    csv_reader = csv.reader(fichier_lecture, delimiter=',')
    header = next(csv_reader)
    liste = [header]
    for row in csv_reader:
        if int(row[1]) == liste_correspondances[0]:
            row[1] = 0
            liste.append(row)
        elif int(row[1]) == liste_correspondances[1]:
            row[1] = 1
            liste.append(row)

    with open(csv_position_pieds.replace('_position_joueur_grace_pieds.csv','_position_joueur_grace_pieds_ordonne.csv'),"w", newline='') as fichier_csv:
        fichier_csv_writer = csv.writer(fichier_csv, delimiter=',')
        for row in liste:
            fichier_csv_writer.writerow(row)

    


def create_csv_new_ref(csv_enrichi,csv_position):
    """
        Function used to create enhanced annotation csv file with new referentiel data 
        Args:
                - enhanced annotation csv file path
                - Csv position file
        Return:
                - Create csv (_enrichi_new_ref.csv)
    """

    fichier_lecture = open(csv_enrichi,"r")
    csv_reader = csv.reader(fichier_lecture, delimiter=',')
    header_csv_enrichi = next(csv_reader)
    liste_csv_enrichi = []
    for row in csv_reader:
        liste_csv_enrichi.append(row)
    


    df_position = pd.read_csv(csv_position)


    header_csv_enrichi.append("pos_joueur_0_pieds_x")
    header_csv_enrichi.append("pos_joueur_0_pieds_y")
    header_csv_enrichi.append("pos_joueur_1_pieds_x")
    header_csv_enrichi.append("pos_joueur_1_pieds_y")
    header_csv_enrichi.append("coor_balle_x_nex_ref_frappe")
    header_csv_enrichi.append("coor_balle_y_nex_ref_frappe")
    header_csv_enrichi.append("coor_balle_x_nex_ref_rebond")
    header_csv_enrichi.append("coor_balle_y_nex_ref_rebond")
    for i in range(len(liste_csv_enrichi)):
        liste_csv_enrichi[i].append(df_position[(df_position['frame'] == i) & (df_position['numero_pers'] == 0)].iloc[0]["distance_x"])
        liste_csv_enrichi[i].append(df_position[(df_position['frame'] == i) & (df_position['numero_pers'] == 0)].iloc[0]["distance_y"])
        liste_csv_enrichi[i].append(df_position[(df_position['frame'] == i) & (df_position['numero_pers'] == 1)].iloc[0]["distance_x"])
        liste_csv_enrichi[i].append(df_position[(df_position['frame'] == i) & (df_position['numero_pers'] == 1)].iloc[0]["distance_y"])
        if liste_csv_enrichi[i][14] != '':
            if np.sign(float(liste_csv_enrichi[i][14])) == np.sign(df_position[(df_position['frame'] == int(liste_csv_enrichi[i][21])) & (df_position['numero_pers'] == 0)].iloc[0]["distance_y"]):
                liste_csv_enrichi[i].append(float(liste_csv_enrichi[i][13]) - df_position[(df_position['frame'] == int(liste_csv_enrichi[i][21])) & (df_position['numero_pers'] == 0)].iloc[0]["distance_x"])
                liste_csv_enrichi[i].append(float(liste_csv_enrichi[i][14]) - df_position[(df_position['frame'] == int(liste_csv_enrichi[i][21])) & (df_position['numero_pers'] == 0)].iloc[0]["distance_y"])
                
                liste_csv_enrichi[i].append(float(liste_csv_enrichi[i][13]) - df_position[(df_position['frame'] == int(liste_csv_enrichi[i][2])) & (df_position['numero_pers'] == 0)].iloc[0]["distance_x"])
                liste_csv_enrichi[i].append(float(liste_csv_enrichi[i][14]) - df_position[(df_position['frame'] == int(liste_csv_enrichi[i][2])) & (df_position['numero_pers'] == 0)].iloc[0]["distance_y"])
            else:
                liste_csv_enrichi[i].append(float(liste_csv_enrichi[i][13]) - df_position[(df_position['frame'] == int(liste_csv_enrichi[i][21])) & (df_position['numero_pers'] == 1)].iloc[0]["distance_x"])
                liste_csv_enrichi[i].append(float(liste_csv_enrichi[i][14]) - df_position[(df_position['frame'] == int(liste_csv_enrichi[i][21])) & (df_position['numero_pers'] == 1)].iloc[0]["distance_y"])
                
                liste_csv_enrichi[i].append(float(liste_csv_enrichi[i][13]) - df_position[(df_position['frame'] == int(liste_csv_enrichi[i][2])) & (df_position['numero_pers'] == 1)].iloc[0]["distance_x"])
                liste_csv_enrichi[i].append(float(liste_csv_enrichi[i][14]) - df_position[(df_position['frame'] == int(liste_csv_enrichi[i][2])) & (df_position['numero_pers'] == 1)].iloc[0]["distance_y"])
        else:
            liste_csv_enrichi[i].append('')
            liste_csv_enrichi[i].append('')
            liste_csv_enrichi[i].append('')
            liste_csv_enrichi[i].append('')

    with open(csv_enrichi.replace('_enrichi.csv','_enrichi_new_ref.csv'),"w", newline='') as fichier_csv:
        fichier_csv_writer = csv.writer(fichier_csv, delimiter=',')
        fichier_csv_writer.writerow(header_csv_enrichi)
        for row in liste_csv_enrichi:
            fichier_csv_writer.writerow(row)



def create_enhanced_csv_with_feet(csv_annotation_enrichi):
    """
        Function used to add 6 columns to "_csv_annotation_enrichi.csv" file
        Columns added:
            - pos_pied_jA_x
            - pos_pied_jA_y
            - pos_pied_jA_z
            - pos_pied_jB_x
            - pos_pied_jB_y
            - pos_pied_jB_z
        Args:
                - enhanced annotation csv file path
        Returns:
                - Create csv file "_annotation_enrichi_pos_pieds.csv"
    """

    fichier_lecture = open(csv_annotation_enrichi,"r")
    csv_reader = csv.reader(fichier_lecture, delimiter=',')
    header = next(csv_reader)
    header.append("pos_pied_jA_x")
    header.append("pos_pied_jA_y")
    header.append("pos_pied_jA_z")
    header.append("pos_pied_jB_x")
    header.append("pos_pied_jB_y")
    header.append("pos_pied_jB_z")

    liste = []
    for row in csv_reader:
        liste.append(row)

    dossier = os.path.spli(csv_annotation_enrichi)[0]
    chemin_clips = os.path.join(dossier,'clips')
    liste_clip = os.listdir(chemin_clips)

    for clip in liste_clip:
        chemin_clip = os.path.join(dossier,"clips",clip,clip+"_annotation.csv")
        fichier_lecture = open(chemin_clip,"r")
        csv_reader = csv.reader(fichier_lecture, delimiter=',')
        header = next(csv_reader)
        liste_cvs_clip = []


        for row in csv_reader:
            liste_cvs_clip.append(row)

        
        liste_positions_j1 = []
        liste_positions_j2 = []

        chemin_clip = os.path.join(dossier,"clips",clip,"csv_json_openpose",clip+"_position_joueur_grace_pieds_ordonne.csv")
        fichier_lecture = open(chemin_clip,"r")
        csv_reader = csv.reader(fichier_lecture, delimiter=',')
        header = next(csv_reader)

        for row in csv_reader:
            if int(row[1]) == 0:
                liste_positions_j1.append(row)
            elif int(row[1]) == 1:
                liste_positions_j2.append(row)
        
        new_l = []
        for row in liste_cvs_clip:
            row2 = []
            row2.append(liste_positions_j1[int(row[21])][2])
            row2.append(liste_positions_j1[int(row[21])][3])
            row2.append(liste_positions_j1[int(row[21])][4])
            row2.append(liste_positions_j2[int(row[21])][2])
            row2.append(liste_positions_j2[int(row[21])][3])
            row2.append(liste_positions_j2[int(row[21])][4])
            new_l.append(row[2])
        