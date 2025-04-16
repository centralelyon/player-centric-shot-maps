from mmpose.apis import MMPoseInferencer
import os
import csv
import numpy as np


def create_mmpose_files(video_path):
    """
        Use mmpose3d and 2d to create 2 csv files (one with 2d pose and one with 3d pose)
        Args:
                - Video path
        Returns:
                - Create csv file  (video_path.replace(".mp4","_pose_3d_mmpose.csv"))
                    (format: ["frame","numero_pers","joint","x","y","z","tracking"])
                - Create csv file  (video_path.replace(".mp4","_pose_2d_mmpose.csv"))
                    (format: ["frame","numero_pers","joint","x","y","z","tracking"])
    """

    inferencer = MMPoseInferencer('human')

    result_generator = inferencer(video_path, show=False)#, pred_out_dir='pred_out_dir')
    #result = next(result_generator)
    results = [result for result in result_generator]
    liste_tracking_json = openpose_json2list_tracking(results)

    
    en_tete = ["frame","numero_pers","joint","x","y","tracking"]
    liste_pose = []

    for i,r in enumerate(results):
        for j in range(len(r["predictions"][0])):
            for k in range(len(r["predictions"][0][j]["keypoints"])):
                sous_liste = []
                sous_liste.append(i)
                sous_liste.append(j)
                sous_liste.append(k)
                sous_liste.append(r["predictions"][0][j]["keypoints"][k][0])
                sous_liste.append(r["predictions"][0][j]["keypoints"][k][1])
                sous_liste.append(liste_tracking_json[i][j])
                liste_pose.append(sous_liste)

    nom_csv = os.path.join(os.path.split(video_path)[0],os.path.split(video_path)[1].replace(".mp4","_pose_2d_mmpose.csv"))
    
    with open(nom_csv,"w", newline='') as fichier_csv:
        fichier_csv_writer = csv.writer(fichier_csv, delimiter=',')
        fichier_csv_writer.writerow(en_tete)
        for row in liste_pose:
            fichier_csv_writer.writerow(row)


    ########################
    ########## 3D ##########
    ########################
    
    inferencer = MMPoseInferencer(pose3d='human3d')
    result_generator = inferencer(video_path, show=False, pred_out_dir='pred_out_dir',draw_gt=True,save_vis=True,out_dir='output')
    #result = next(result_generator)
    results = [result for result in result_generator]
    en_tete = ["frame","numero_pers","joint","x","y","z","tracking"]

    liste_pose = []

    for i,r in enumerate(results):
        for j in range(len(r["predictions"][0])):
            for k in range(len(r["predictions"][0][j]["keypoints"])):
                sous_liste = []
                sous_liste.append(i)
                sous_liste.append(j)
                sous_liste.append(k)
                sous_liste.append(r["predictions"][0][j]["keypoints"][k][0])
                sous_liste.append(r["predictions"][0][j]["keypoints"][k][1])
                sous_liste.append(r["predictions"][0][j]["keypoints"][k][2])
                sous_liste.append(liste_tracking_json[i][j])
                liste_pose.append(sous_liste)

    nom_csv = os.path.join(os.path.split(video_path)[0],os.path.split(video_path)[1].replace(".mp4","_pose_3d_mmpose.csv"))
    
    with open(nom_csv,"w", newline='') as fichier_csv:
        fichier_csv_writer = csv.writer(fichier_csv, delimiter=',')
        fichier_csv_writer.writerow(en_tete)
        for row in liste_pose:
            fichier_csv_writer.writerow(row)
    
    
def openpose_json2list_tracking(results): 
    '''
        Functino use to add tracking to mmpose files created with create_mmpose_files()
        The tracking use player keypoints to compute minimum distance between to consecutive frames
    ''' 
    liste_sortie = []
    val_precedente = []
    val_actuelle = [[]]
    nb_personnes_tot = -1
    val_precedente = {}
    for r in results:
        if len(r["predictions"][0])>0:
            if nb_personnes_tot == -1:
                nb_personnes_tot = len(r["predictions"][0])
            nb_personnes = len(r["predictions"][0])
            val_actuelle = []
            liste_joueurs_avec_vals_moyennes_deplacements = []
            for i in range(nb_personnes):
                data_keypoints = r["predictions"][0][i]["keypoints"]
                val_actuelle.append(data_keypoints)
                liste_un_joueur_avec_vals_moyennes_deplacements = []
                for k in range(len(val_precedente)):
                    x = 0
                    y = 0
                    nb_points = 1
                    for j in range(0,len(data_keypoints)):
                        if ((data_keypoints[j][0] != 0) and (val_precedente[k][j][0] != 0)):  
                            x += abs(data_keypoints[j][0] - val_precedente[k][j][0])
                            y += abs(data_keypoints[j][1] - val_precedente[k][j][1])
                            nb_points += 1
                    if x+y == 0:
                        x = y = 5000
                    liste_un_joueur_avec_vals_moyennes_deplacements.append((x+y)/nb_points) #we could use sqrt((x²+y²)/nb_points) 
                liste_joueurs_avec_vals_moyennes_deplacements.append(liste_un_joueur_avec_vals_moyennes_deplacements)
            if liste_joueurs_avec_vals_moyennes_deplacements[0] != []:
                position_des_joueurs = []
                for j in range(len(liste_joueurs_avec_vals_moyennes_deplacements)):
                    if min(liste_joueurs_avec_vals_moyennes_deplacements[j]) < 70:
                        position_des_joueurs.append(np.argmin(liste_joueurs_avec_vals_moyennes_deplacements[j]))
                    else:
                        position_des_joueurs.append(nb_personnes_tot)
                        nb_personnes_tot += 1
                #position_des_joueurs = [np.argmin(liste_joueurs_avec_vals_moyennes_deplacements[i]) for i in range(len(liste_joueurs_avec_vals_moyennes_deplacements))]
                
            else:
                position_des_joueurs = [i for i in range(len(liste_joueurs_avec_vals_moyennes_deplacements))]
                nb_personnes = len(position_des_joueurs)
            liste_sortie.append(position_des_joueurs[:])



            
            for i in position_des_joueurs:
                val_precedente[i] = val_actuelle[position_des_joueurs.index(i)]
        else:
            liste_sortie.append([])
    
    return(liste_sortie)


if __name__ == "__main__":
    create_mmpose_files(os.path.join("example/set_1_point_8/set_1_point_8.mp4"))