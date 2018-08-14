#!/usr/bin/python
#! -*- encoding: utf-8 -*-

# This file is modified from OpenMVG (Open Multiple View Geometry) C++ library.

# Python implementation of the bash script written by Romuald Perrot
# Created by @vins31
# Modified by Pierre Moulon
# Further modified by Wudao Ling
#
# usage : python openmvg.py image_dir
#
# image_dir is the input directory where images are located
# output will be saved at python file location

# Indicate the openMVG/openMVS binary directory
OPENMVG_SFM_BIN = "/home/wudao/openMVG_Build/Linux-x86_64-RELEASE"
OPENMVS_SFM_BIN = "/home/wudao/openMVS_build/bin"
CAMERA_SENSOR_WIDTH_DATABASE = "/home/wudao/openMVG/src/openMVG/exif/sensor_width_database/sensor_width_camera_database.txt"

# endoscope camera intrinsics Kmatrix: “f;0;ppx;0;f;ppy;0;0;1”
CAMERA_INTRINSICS = "474.8972; 0; 322.1932; 0; 474.5878; 242.7300; 0; 0; 1"

import os
import subprocess
import sys

if len(sys.argv) != 2 or sys.argv[1][0] == '.':
    print ("Usage %s absolute_image_directory" % sys.argv[0])
    sys.exit(1)

input_dir = sys.argv[1]
output_dir = os.path.dirname(os.path.abspath(__file__)) + "/results"
matches_dir = os.path.join(output_dir, "matches")
reconstruction_dir = os.path.join(output_dir, "reconstruction_sequential")

print ("Using input dir  : ", input_dir)
print ("      output dir : ", output_dir)

# Create folders if not present
if not os.path.exists(output_dir):
  os.mkdir(output_dir)
if not os.path.exists(matches_dir):
  os.mkdir(matches_dir)
if not os.path.exists(reconstruction_dir):
  os.mkdir(reconstruction_dir)

# change directory for openMVS logs and undistorted images
os.chdir(reconstruction_dir)

print ("1. Intrinsics analysis")
pIntrisics = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_SfMInit_ImageListing"),  "-i", input_dir, "-o", matches_dir, "-d", CAMERA_SENSOR_WIDTH_DATABASE, "-k", CAMERA_INTRINSICS])
pIntrisics.wait()

print ("2. Compute features")
pFeatures = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeFeatures"),  "-i", matches_dir+"/sfm_data.json", "-o", matches_dir, "-m", "SIFT"] )
pFeatures.wait()

print ("3. Compute matches")
pMatches = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeMatches"),  "-i", matches_dir+"/sfm_data.json", "-o", matches_dir, "-g", "f"] )
pMatches.wait()

print ("4. Do Sequential/Incremental reconstruction")
pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_IncrementalSfM"),  "-i", matches_dir+"/sfm_data.json", "-m", matches_dir, "-o", reconstruction_dir] )
pRecons.wait()

print ("5. Colorize Structure")
pColor = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeSfM_DataColor"),  "-i", reconstruction_dir+"/sfm_data.bin", "-o", os.path.join(reconstruction_dir,"colorized.ply")] )
pColor.wait()

# export openMVG to openMVS
print ("6. Export openMVG to openMVS")
pExport = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_openMVG2openMVS"), "-i", reconstruction_dir+"/sfm_data.bin", "-o", reconstruction_dir+"/scene.mvs"])
pExport.wait()

# densify point cloud (optional)
print ("7. Densify point clouds")
pDensify = subprocess.Popen( [os.path.join(OPENMVS_SFM_BIN, "DensifyPointCloud"), reconstruction_dir+"/scene.mvs"])
pDensify.wait()

# mesh reconstruction
print ("8. Rough mesh reconstruction")
pMesh = subprocess.Popen( [os.path.join(OPENMVS_SFM_BIN, "ReconstructMesh"), reconstruction_dir+"/scene_dense.mvs"])
pMesh.wait()

# # mesh refining (optional)
# print ("9. Refine mesh")
# pRefine = subprocess.Popen( [os.path.join(OPENMVS_SFM_BIN, "RefineMesh"), reconstruction_dir+"/scene_mesh.mvs"])
# pRefine.wait()

# mesh texturing
print ("10. Texture mesh")
pTexture = subprocess.Popen( [os.path.join(OPENMVS_SFM_BIN, "TextureMesh"), reconstruction_dir+"/scene_dense_mesh.mvs"])
pTexture.wait()

# visualizatin
print ("11. Visualize reconstruction")
pVisual = subprocess.Popen( [os.path.join(OPENMVS_SFM_BIN, "Viewer"), reconstruction_dir+"/scene_dense_mesh_texture.mvs"])
pVisual.wait()

