from scipy.linalg import solve
import numpy as np
import pickle
import math
import eos
import glob
import os
import json
from lsfm.eos_utils import Blendshape, MorphableModel, PcaModel

def recoverModelFromPca(id, path, pca_model, alpha):
    alpha_np = np.array(list(map(float,alpha)))
    eigenvector_linear_sum = np.dot(alpha_np, pca_model.components)
    recovered_model = pca_model.mean_vector + np.dot(alpha_np, pca_model.components)
    filename_ply = str(path) + '/recovered_ply/' + str(id) + '.ply'
    header = '''ply
format ascii 1.0
comment UNRE generated
element vertex {0}
property float x
property float y
property float z
element face {1}
property list uchar int vertex_indices
end_header\n'''.format(int(len(pca_model.components[0]) / 3), len(pca_model.mean().trilist))

    vertice_list = []
    faces_list = []

    with open(filename_ply, 'w') as f:
        f.writelines(header)
        for idx in range(0, len(recovered_model), 3):
            f.write(str(recovered_model[idx]))
            f.write(' ')
            f.write(str(recovered_model[idx + 1]))
            f.write(' ')
            f.write(str(recovered_model[idx + 2]))
            f.write(' ')
            f.write('\n')

        for idx in range(0, len(pca_model.mean().trilist)):
            f.write('3 ')
            for i in range(0, 3):
                f.write(str(int(pca_model.mean().trilist[idx][i])))
                f.write(' ')
            f.write('\n')

def extractAlpha(pca_model, path):
    filelist = glob.glob(path + 'shape_nicp/*.pkl')
    alpha_dict = dict()
    count = 0
    for filepath in filelist:
        base = os.path.basename(filepath)
        filename = os.path.splitext(base)[0]
        fin = open(filepath, 'rb')
        vectices = pickle.load(fin)
        fin.close()
        meanshape = pca_model.mean_vector
        delta = vectices - meanshape
        alpha = np.dot(pca_model.components, delta)
        #recoverModelFromPca(filename, path, pca_model, alpha)
        alpha = alpha / np.sqrt(pca_model.eigenvalues)
        if count == 0:
            with open(path + 'pca_result/alpha.txt', 'w') as fp:
                for ii in range(0, len(alpha)):
                    fp.write(str("{0:.12f}".format(alpha[ii])))
                    fp.write('\n')
        count = count + 1
        alpha_list = []
        for ii in range(0, len(alpha)):
            alpha_list.append(str("{0:.6f}".format(alpha[ii])))
        alpha_dict.update({filename: alpha_list})
    with open(path + 'pca_result/alpha.json', 'w') as fp:
        json.dump(alpha_dict, fp, indent = 4)

    return alpha_dict

def get_obj_vt(filename:str):
    f_pre = open(filename)
    line = f_pre.readline()
    texture_coordinates = []
    while line:
        location = line.find("vt ")
        if location>=0:
            number = line.split()
            texture_coordinates.append([float(number[1]), float(number[2])])
        else:
            pass
        line = f_pre.readline()
    f_pre.close()
    return texture_coordinates

def saveObjToEos(pca_model, path):
    file_eos_model = path + 'shape.bin'
    file_blendshape = path + 'blendshapes.bin'
    file_py_model = path + 'py_3dmm_shape.bin'
    color_mean = np.zeros(pca_model.mean_vector.shape)
    color_orthogonal_pca_basis = np.zeros(pca_model.components.T.shape)
    color_pca_variance = np.zeros(pca_model.eigenvalues.shape)

    color_model = eos.morphablemodel.PcaModel(color_mean, color_orthogonal_pca_basis, color_pca_variance,
                                              pca_model.mean().trilist)
    shape_model = eos.morphablemodel.PcaModel(pca_model.mean_vector.astype('<f4'), pca_model.components.T.astype('<f4'),
                                              pca_model.eigenvalues.astype('<f4'), pca_model.mean().trilist.astype('int32'))
    model = eos.morphablemodel.MorphableModel(shape_model, color_model, vertex_definitions=None, texture_coordinates=[],
                                              texture_triangle_indices=[])  # uv-coordinates can be added here
    eos.morphablemodel.save_model(model, file_eos_model)

    print("Converted and saved model as ", file_eos_model, ".")
    
    print("updating texture coordinates...")
    texture_coordinates = get_obj_vt(os.path.join('/home/u/workspace/lsfm/', 'vt.txt'))
    print("transfering to {}".format(file_py_model))
    shape_mean = shape_model.get_mean()
    shape_orthonormal_pca_basis = shape_model.get_orthonormal_pca_basis()
    shape_eigenvalues = shape_model.get_eigenvalues()
    shape_triangle_list = shape_model.get_triangle_list()
    py_shape_model = PcaModel.PcaModel(shape_mean, shape_orthonormal_pca_basis, shape_eigenvalues, shape_triangle_list)
    color_mean = color_model.get_mean()
    color_orthonormal_pca_basis = color_model.get_orthonormal_pca_basis()
    color_eigenvalues = color_model.get_eigenvalues()
    color_triangle_list = color_model.get_triangle_list()
    py_color_model = PcaModel.PcaModel(color_mean, color_orthonormal_pca_basis, color_eigenvalues, color_triangle_list)
    py_model = MorphableModel.MorphableModel(py_shape_model, py_color_model, texture_coordinates)
    MorphableModel.save_model(py_model, file_py_model)
    print('shape transfer done!')

    eos_blendshapes = []
    num_principal_components = 1
    for eos_blendshape_id in range(num_principal_components):
        eos_blendshape_coeff = np.zeros(num_principal_components)
        eos_blendshape_coeff[eos_blendshape_id - 1] = 1
        eos_blendshape = eos.morphablemodel.Blendshape(str(eos_blendshape_coeff),
                                                       np.zeros(model.get_shape_model().get_data_dimension()))
        eos_blendshapes.append(eos_blendshape)
    eos.morphablemodel.save_blendshapes(eos_blendshapes, file_blendshape)
    print("Converted and saved blendshape as ", file_blendshape, ".")

def extractObjFromEos(file_eos_model, file_blendshape, path):
    model_load = eos.morphablemodel.load_model(file_eos_model)
    print("Load file ", file_eos_model, " successfully.")
    blendshapes = eos.morphablemodel.load_blendshapes(file_blendshape)
    print("Load file ", file_blendshape, " successfully.")
    shape_model = model_load.get_shape_model()
    color_model = model_load.get_color_model()
    pca_shape_coefficients = np.zeros(shape_model.get_num_principal_components())
    current_pca_shape = shape_model.draw_sample(pca_shape_coefficients)
    blendshape_coefficients = np.zeros([len(blendshapes)])
    blendshapes_as_basis = Blendshape.to_matrix(blendshapes)
    current_combined_shape = current_pca_shape + blendshapes_as_basis.dot(blendshape_coefficients)
    current_mesh = MorphableModel.sample_to_mesh(current_combined_shape, color_model.get_mean(),
                                                 shape_model.get_triangle_list(), color_model.get_triangle_list(),
                                                 model_load.get_texture_coordinates())
    file_obj = path + 'eos_shape.obj'
    obj_file = open(file_obj, 'w')
    for i in range(len(current_mesh.vertices)):
        obj_file.write('v ' + str(current_mesh.vertices[i][0]) + ' ' + str(current_mesh.vertices[i][1]) + ' ' + str(
            current_mesh.vertices[i][2]) + '\n')
    if current_mesh.texcoords:
        for tc in current_mesh.texcoords:
            obj_file.write('vt ' + str(tc[0]) + ' ' + str(tc[1]) + '\n')
    for v in current_mesh.tvi:
        obj_file.write('f ' + str(v[0] + 1) + ' ' + str(v[1] + 1) + ' ' + str(v[2] + 1) + '\n')
    obj_file.close()
    print("Save model shape.obj successfully.")
