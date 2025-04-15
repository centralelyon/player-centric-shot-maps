# Player Centric Referentiel
This repo explain how to generate 3D scene of table tennis points.
To create this scene, we used the API of Blender bpy. We provided a script to create scene with the table, players and ball position for each frame and the camera. We also provided a script to create a video of the point generated in the 3D scene.  

## How to cite

> Aymeric Erades & Romain Vuillemot (2025). « Player-Centric Shot Maps in Table Tennis ». Computer graphics Forum (Proc. Eurovis), p. 10.

```
@article{erades:hal-04997867,
  TITLE = {{Player-Centric Shot Maps in Table Tennis}},
  AUTHOR = {Erades, Aymeric and Vuillemot, Romain},
  URL = {https://hal.science/hal-04997867},
  JOURNAL = {{Computer graphics Forum (Proc. Eurovis)}},
  PAGES = {10},
  YEAR = {2025},
  MONTH = Jun,
  HAL_ID = {hal-04997867},
  HAL_VERSION = {v1},
}
```

## Steps
### 1. Install
- Python 3.11 requiered for bpy
- Download MMPose https://github.com/open-mmlab/mmpose
- ```bash
   pip install -r requirements.txt
   ```
- Download Blender https://www.blender.org/download/ (recommanded)


### 2. Pose estimation
To estimate player positions we use position of players' feet by using pose estimation with mmpose  
To generate pose estimation on a table tennis point video:  
- Use `create_mmpose_files()` from [mmpose_inference.py](https://github.com/centralelyon/tt-player-centric/blob/main/mmpose_inference.py)
  - Params:
    - video_path  
(We need a video of a single camera with only one point)

This function create a csv file with all players positions and with a tracking provided  
the file looks like this:  
<img src="images/csv_pose.png" alt="csv file" width="1100">

Genrate position file:
- Use `create_csv_position_using_feet()` from [utils.py](https://github.com/centralelyon/tt-player-centric/blob/main/utils.py)

This function create a csv file with all players positions and with a tracking provided  
the file looks like this:  
<img src="images/csv_position.png" alt="csv file" width="1100">

### 3. Calibrate camera
If you we don't know intrisec camera parameters, we can estimate them with OpenCv functions such as `slovepnp()` or `calibrateCamera()` ([doc](https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html). These functions can be used directly inside blender with https://rtstudios.gumroad.com/l/camera_pnpoint 
To estimate these parameters, we can use 6 known points from the table whose correspondences in the 3d scene are known
<img src="images/table_6_points.png" alt="Calibration with 6 points" width="1100">
We need to create a json with these parameters (exemple: https://github.com/centralelyon/tt-player-centric/blob/main/exemple/PRITHIKA-PAVADE_vs_SIBEL-ALTINKAYA_camera.json)  
To create this json file we provide the function `create_json_camera()` from [utils.py](https://github.com/centralelyon/tt-player-centric/blob/main/utils.py)
This function needs as parameters some informations from `calibrateCamera()` function:
- Focal length
- Optical center
- Distorsion (K1,K2,K3)
- Location
- Rotation


## 4. Create video of player's position
To create the video of players' position we need to annotate more informations such as rebounce positions, hit positions and compute 3D ball trajectories.  
We provided an exemple with all necessary files to create the video. All of this are in folder exemple.  
To generate video `python render_image.py`  
<img src="images/video3D.jpg" alt="3D video" width="1100">  
This function use:
- Players' position
- Ball position
- Camera parameters
- Annotations

## 5. Create csv with new referentiel
To create the csv with coordonates in the new referentiel we need to use `create_csv_new_ref()` from [utils.py](https://github.com/centralelyon/tt-player-centric/blob/main/utils.py)
Exemple:  
`create_csv_new_ref("exemple/set_1_point_8_annotation_enrichi.csv","exemple/set_1_point_8_position_ordonne.csv")`

Exemple of new referentiel points ploted:
<img src="images/new_ref.png" alt="New referentiel points" width="1100">


## 6. Miscellaneous
[BlenderScene.py](https://github.com/centralelyon/tt-player-centric/blob/main/BlenderScene.py) is to create 3D scene in Blender.  
Load the file in blender  
You need to change paths:
- chemin_pose_3d
- chemin_pose_balle_3d
Execute the code
<img src="images/blender_scene.png" alt="Blender scene" width="1100">

