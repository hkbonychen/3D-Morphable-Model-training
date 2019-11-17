from scipy.io import loadmat
from menpo.shape import ColouredTriMesh, PointCloud

import lsfm.io as lio
from . import DATA_DIR, save_template

import csv
import numpy as np


def load_mean_from_basel(path):
    mm = loadmat(str(path))
    trilist = mm['tl'][:, [0, 2, 1]] - 1
    mean_points = mm['shapeMU'].reshape(-1, 3)
    mean_colour = mm['texMU'].reshape(-1, 3) / 255
    return ColouredTriMesh(mean_points, trilist=trilist, colours=mean_colour)


def load_basel_template_metadata():
    return lio.import_pickle(DATA_DIR / 'basel_template_metadata.pkl')


def generate_template_from_basel_and_metadata(basel, meta):
    template = ColouredTriMesh(basel.points[meta['map_tddfa_to_basel']],
                               trilist=meta['tddfa_trilist'],
                               colours=basel.colours[
                                   meta['map_tddfa_to_basel']])

    template.landmarks['ibug68'] = meta['landmarks']['ibug68']
    template.landmarks['nosetip'] = meta['landmarks']['nosetip']

    return template


def save_template_from_basel(path):
    basel = load_mean_from_basel(path)
    meta = load_basel_template_metadata()
    template = generate_template_from_basel_and_metadata(basel, meta)
    save_template(template, overwrite=True)

def save_template_from_mesh(path):
    points, trilist = lio.getTriMeshfromPly(path)
    template = ColouredTriMesh(points, trilist)
    #to obtain landmark
    landmark_68 = []
    landmark_100 = []
    landmark_ear = []
    nosetip = []
    count = 0
    with open('/home/u/workspace/VPE/template/ibug100.pp') as pp_file:
        pp_file = csv.reader(pp_file, delimiter='"')
        for row in pp_file:
            count = count + 1
            if count >= 7 and count < 107:
                landmark_100.append([float(row[1]), float(row[3]), float(row[5])])
                if count < 75:
                    landmark_68.append([float(row[1]), float(row[3]), float(row[5])])
            if count >= 84 and count <= 94:
                landmark_ear.append([float(row[1]), float(row[3]), float(row[5])])
            if count >= 96 and count <= 106:
                landmark_ear.append([float(row[1]), float(row[3]), float(row[5])])
    count = 0
    with open('/home/u/workspace/VPE/template/nosetip.pp') as pp_file:
        pp_file = csv.reader(pp_file, delimiter='"')
        for row in pp_file:
            count = count + 1
            if count >= 7 and count < 8:
                nosetip.append([float(row[1]), float(row[3]), float(row[5])])
    template.landmarks['ibug68'] = PointCloud(np.array(landmark_68))
    template.landmarks['ibug100'] = PointCloud(np.array(landmark_100))
    template.landmarks['ibugEar'] = PointCloud(np.array(landmark_ear))
    template.landmarks['nosetip'] = PointCloud(np.array(nosetip))
    save_template(template, overwrite=True)
