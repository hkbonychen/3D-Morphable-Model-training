#!/bin/bash

#remove files or directory
if [ -f "./visualizations/final_weights.pdf" ]
then
	rm ./visualizations/final_weights.pdf
fi
if [ -f "./visualizations/pruning.pdf" ]
then
	rm ./visualizations/pruning.pdf
fi
rm -rf ./ply
rm -rf ./problematic
rm -rf ./pca_result
rm -rf ./shape_nicp
rm -rf ./recovered_ply
if [ -f "shape_model.mat" ]
then
	rm shape_model.mat
fi
if [ -f "settings.json" ]
then
	rm settings.json
fi
if [ -f "initial_shape_model.pkl" ]
then
	rm initial_shape_model.pkl
fi

#create directory back
mkdir ./ply
#mkdir ./ply/landmarks
#mkdir ./ply/models
mkdir shape_nicp
mkdir problematic
mkdir pca_result
mkdir recovered_ply
