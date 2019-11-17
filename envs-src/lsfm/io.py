from collections import OrderedDict
from functools import partial
import json
from pathlib import Path
from shutil import copy
import csv

from scipy.io import savemat

import numpy as np
from menpo.base import LazyList
import menpo.io as mio
from menpo.io.output.base import _validate_filepath
import menpo3d.io as m3io
from menpo.image.base import normalize_pixels_range
from menpo.shape import PointCloud

export_pickle = partial(mio.export_pickle, protocol=4)
import_pickle = partial(mio.import_pickle, encoding='latin1')


def ensure_exists(p):
    if not p.is_dir():
        p.mkdir(parents=True)


def initialize_root(root):
    ensure_exists(root)

    ensure_exists(root / 'shape_nicp')
    ensure_exists(root / 'problematic')

    ensure_exists(root / 'visualizations' / 'landmarks')
    ensure_exists(root / 'visualizations' / 'shape_nicp')
    ensure_exists(root / 'visualizations' / 'pruning')


def import_mesh(path, hasTexture=False, landmark_type='ibug68'):
    if path.suffix == '.pkl' or path.suffix == '.gz':
        mesh = import_pickle(path)
    else:
        mesh = m3io.import_mesh(path)
    if hasTexture:
        if mesh.texture.pixels.dtype != np.float64:
            mesh.texture.pixels = normalize_pixels_range(mesh.texture.pixels)
    else:
        landmark = []               
        count = 0
        with open(str(path) + '.landmark') as pp_file:
            pp_file = csv.reader(pp_file, delimiter=' ')
            for row in pp_file:
                count = count + 1
                if landmark_type == 'ibug100':
                    if count >= 1 and count <= 100:
                        landmark.append([float(row[0]), float(row[1]), float(row[2])])
                if landmark_type == 'ibug68':
                    if count < 69:
                        landmark.append([float(row[0]), float(row[1]), float(row[2])])
                if landmark_type == 'ibugEar':
                    if count >= 78 and count <= 88:
                        landmark.append([float(row[0]), float(row[1]), float(row[2])])
                    if count >= 90 and count <= 100:
                        landmark.append([float(row[0]), float(row[1]), float(row[2])])
        mesh.landmarks[landmark_type] = PointCloud(np.array(landmark))        
    return mesh


def path_settings(r):
    return r / 'settings.json'


def _save_settings_to_path(settings, path, overwrite=False):
    path = _validate_filepath(path, overwrite)
    settings_json = settings.copy()
    settings_json['ids_to_paths'] = {id_: str(path) for id_, path in
                                     settings['ids_to_paths'].items()}
    with open(str(path), 'wt') as f:
        json.dump(settings_json, f, sort_keys=True, indent='    ')


def _load_settings_for_path(path):
    with open(str(path), 'rt') as f:
        settings = json.load(f)
    settings['ids_to_paths'] = OrderedDict(sorted(
        [(id_, Path(path)) for id_, path in settings['ids_to_paths'].items()],
        key=lambda x: x[0]))
    return settings


def import_settings(r):
    return _load_settings_for_path(path_settings(r))


def export_settings(r, settings, overwrite=False):
    _save_settings_to_path(settings, path_settings(r), overwrite=overwrite)


def path_shape_nicp(r, id_):
    return r / 'shape_nicp' / '{}.pkl'.format(id_)


def _load_shape_nicp_for_path(path):
    from .data import load_template  # circular import
    mesh = load_template().from_vector(import_pickle(path))
    mesh.path = path
    return mesh


def import_shape_nicp(r, id_):
    return _load_shape_nicp_for_path(path_shape_nicp(r, id_))


def export_shape_nicp(r, id_, mesh):
    export_pickle(mesh.as_vector(), path_shape_nicp(r, id_), overwrite=True)


def paths_shape_nicp(r):
    return sorted(list(mio.pickle_paths(str(path_shape_nicp(r, '*')))))


def shape_nicp_ids(r):
    return [p.stem for p in paths_shape_nicp(r)]


def shape_nicps(r):
    return LazyList.init_from_iterable(paths_shape_nicp(r),
                                       f=_load_shape_nicp_for_path)


def path_initial_shape_model(r):
    return r / 'initial_shape_model.pkl'


def import_initial_shape_model(r):
    return import_pickle(path_initial_shape_model(r))


def export_initial_shape_model(r, model):
    export_pickle(model, path_initial_shape_model(r))


def path_shape_model(r):
    return r / 'shape_model.mat'


def path_shape_model_cropped(r):
    return r / 'shape_model_cropped.mat'


def export_lsfm_model(pca, n_training_samples, path, extra_dict=None):
    if extra_dict is None:
        extra_dict = {}
    mdict = {
        'components': pca.components.T,
        'eigenvalues': pca.eigenvalues,
        'cumulative_explained_variance': pca.eigenvalues_cumulative_ratio(),
        'mean': pca.mean_vector,
        'n_training_samples': n_training_samples,
        'trilist': pca.mean().trilist
    }
    if extra_dict is not None:
        for k, v in extra_dict.items():
            mdict[k] = v

    savemat(str(path), mdict)

    # if name.endswith('_tri'):
    #     masking_info = mio.import_pickle(
    #         model_path.parent.parent / 'radial_mask_tri.pkl')
    #     mdict['map_crop_to_full'] = masking_info['map_cropped_to_full']
    #     mdict['map_full_to_cropped'] = masking_info['map_full_to_cropped']
    #     name = name.split('_tri')[0]


def path_problematic(r, id_):
    return r / 'problematic' / '{}.txt'.format(id_)


def export_problematic(r, id_, msg):
    with open(str(path_problematic(r, id_)), 'wt') as f:
        f.write(msg)


# ---------------------------- VISUALIZATION IO ------------------------------ #
def path_landmark_visualization(r, id_):
    return r / 'visualizations' / 'landmarks' / '{}.png'.format(id_)


def export_landmark_visualization(r, id_, img):
    mio.export_image(img, path_landmark_visualization(r, id_), overwrite=True)


def path_shape_nicp_visualization(r, id_):
    return r / 'visualizations' / 'shape_nicp' / '{}.png'.format(id_)


def export_shape_nicp_visualization(r, id_, img):
    mio.export_image(img, path_shape_nicp_visualization(r, id_), overwrite=True)


def path_pruning_visualization(r, id_, rank, w_norm, width):
    return (r / 'visualizations' / 'pruning' /
            '{rank:0{width}} - {w_norm:.5f} ({id_}).png'.format(
                rank=rank, width=width, w_norm=w_norm, id_=id_))


def export_pruning_visualization(r, id_, rank, w_norm, n_meshes=10000):
    width = len(str(n_meshes))
    nicp_vis_path = path_shape_nicp_visualization(r, id_)
    prune_result_path = path_pruning_visualization(r, id_, rank, w_norm,
                                                   width=width)
    copy(str(nicp_vis_path), str(prune_result_path))

#----------------------------- additional functions---------------------------- #
def path_ply_model(r, id_):
    return r / 'ply' / '{}.ply'.format(id_)

def path_ply_landmark(r, id_):
    return r / 'ply' / '{}.pp'.format(id_)

def path_texture_jpg(r, id_):
    return r / 'input_dir' / '{}.jpg'.format(id_)

def path_texture_png(r, id_):
    return r / 'input_dir' / '{}.png'.format(id_)

# ---------------------------- output mesh model ------------------------------ #

#function to write vertices vector into ply format
#written by Bony on 11-7-2019
def ply_from_array(id, mesh, path, landmark_type='ibug68'):
	points = mesh.points
	colours = mesh.colours
	faces = mesh.trilist

	#num_points = int(len(points)/3)
	filename = path + str(id) + '.ply'
	header = '''ply
format ascii 1.0
comment UNRE generated
element vertex {0}
property float x
property float y
property float z
element face {1}
property list uchar int vertex_indices
end_header\n'''.format(mesh.n_points, mesh.n_tris)

	vertice_list=[]
	colours_list=[]
	faces_list=[]
	for item in points:
		vertice_list.append(item)
	for item in colours:
		colours_list.append(item)
	for item in faces:
		faces_list.append(item)
	
	with open(filename, 'w') as f:
		f.writelines(header)
		for idx in range(0, mesh.n_points):
			for i in range(0,3):	
				f.write(str(vertice_list[idx][i]))
				f.write(' ')
			#for j in range(0,3):
			#	f.write(str(int(colours_list[idx][j]*255)))
			#	f.write(' ')
			f.write('\n')
		for idx in range(0, mesh.n_tris):
			f.write('3 ')
			for i in range(0,3):				
				f.write(str(int(faces_list[idx][i])))
				f.write(' ')
			f.write('\n')
	f.close()

	landmarks = mesh.landmarks._landmark_groups[landmark_type].points
	filename_lm = path + str(id) + '.pp'
	header = '<!DOCTYPE PickedPoints> \n<PickedPoints> \n <DocumentData> \n  <DataFileName name="' + filename_lm + '"/> \n  <templateName name=""/> \n </DocumentData>\n'
	count = 1
	with open(filename_lm, 'w') as fpp:
		fpp.write(header)
		for points in landmarks:
			for i in range(0,3):
				fpp.write('\t<point x="' + str(points[0]) + '" y="' + str(points[1]) + '" z="' + str(points[2]) + '" name="' + str(count) + '" active="1"/>\n')
				count = count + 1				
			fpp.write('</PickedPoints>')

def getTriMeshfromPly(path):
    data = []
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=' ')
        for row in csv_reader:
            data.append(row)

    flag = False
    points = []
    trilist = []
    count = 0
    for row in range(len(data)):
        if (data[row][0] == 'element') and (data[row][1] == 'vertex'):
            numOfVertices = int(data[row][2])
        if flag and count < numOfVertices:
            data[row][0] = "{0:.6f}".format(float(data[row][0]))
            data[row][1] = "{0:.6f}".format(float(data[row][1]))
            data[row][2] = "{0:.6f}".format(float(data[row][2]))
            points.append([float(data[row][0]), float(data[row][1]), float(data[row][2])])
            count = count + 1
        elif flag and count >= numOfVertices:
            if data[row][0] == '3':
                trilist.append([int(data[row][1]), int(data[row][2]), int(data[row][3])])
        if (data[row][0] == 'end_header'):
            flag = True
    points_np = np.array(points)
    trilist_np = np.array(trilist)
    return [points_np, trilist_np]


