<<<<<<< HEAD
##To use the virtual python environment in "one-shot-envs", do the following:
conda create --prefix <path of virtual environment> -c menpo python=3.5.4 -y
cp -rf ./lsfm-envs <path of virtual environment>
conda activate <path of virtual environment>
conda install -c menpo suitesparse scikit-sparse cyrasterize
conda install -c anaconda tensorflow-gpu tensorflow-estimator flask
pip install menpo menpofit menpodetect menpo3d dlib lsfm eos-py python-pcl

...
go to the folder of virtual environment/lib/python3.5/site-packages/menpo3d
edit extractimage.py --> 
--original--
from menpo3d.rasterize import GLRasterizer, model_to_clip_transform
--new--
from menpo3d.rasterize.opengl import GLRasterizer
from menpo3d.rasterize import model_to_clip_transform

## Constructing a new model from a private dataset
## Step-by-step Instructions 
## Put the input models and landmark files into a folder, e.g. /home/u/workspace/data/Unre_3DMM_Obj/Landmark_68
## There are two python scripts in the directory:
## preprocessor.py: process the obj files and landmark and copy into lsfm working directory
## clean.py: clear all pre-processored result
cp -rf [folder containing model and landmark files] /home/u/workspace/data/Unre_3DMM_Obj/Landmark_68
cd /home/u/workspace/data/Unre_3DMM_Obj/Landmark_68
(optional)python3 clean.py
python3 preprocessor.py /home/u/workspace/lsfm/input_dir/
## activate lsfm virtual environment
## go to lsfm directory and start the training
conda activate lsfm
cd /home/u/workspace/lsfm
(optional)cd ./output_dir; ./clean.sh; cd ..
cd ./bin
python3 lsfm -i ../input_dir/ -o ../output_dir/ -j 11
## the result being used for fitting is stored in /home/u/workspace/lsfm/output_dir/pca_result

##if tempalte needs to be initialized, use the following command
python3 lsfm init /home/u/miniconda2/envs/lsfm/lib/python3.5/site-packages/lsfm/data/template0.ply
python3 lsfm init /home/u/workspace/practice/3DMM/PublicMM1/01_MorphableModel.mat

=======
# 3D-Morphable-Model-training
This program is to train the face 3D morphable model (3DMM)
>>>>>>> f3b89ce0429047300bf0967a43d7b995b8ca6e2a
