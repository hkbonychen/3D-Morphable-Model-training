# -*- coding: utf-8 -*-
"""
@author: Tab Lee (UNRE)
@email: tab.lee@unre.com
"""
import pickle
import numpy as np
class Blendshape:
    """
    A class representing a 3D blendshape.
    Attributes:
        name: Name of the blendshape.
        deformation: A 3m x 1 list (xyzxyz...)', where m is the number of model-vertices. Has the same format as PcaModel.mean.
    """
    def __init__(self, name='', deformation=list()):
        self.name = name
        self.deformation = deformation

def load_blendshapes(filename):
    file = open(filename, 'rb')
    blendshapes = pickle.load(file)
    file.close()
    return blendshapes

def to_matrix(blendshapes):
    """
    Copies the blendshapes into a matrix, with each column being a blendshape.
    Args:
        blendshapes: List of blendshapes.
    Returns:
        The resulting matrix, could be list or ndarray.
    """
    assert len(blendshapes)
    blendshapes_as_basis = np.empty([len(blendshapes[0].deformation), len(blendshapes)])
    for i in range(len(blendshapes)):
        # TODO: not sure about the shape of deformation, so this could be problematic
        blendshapes_as_basis[:, i] = blendshapes[i].deformation
    return blendshapes_as_basis

def to_vector(coefficients):
    """
    Maps an std::vector of coefficients with Eigen::Map, so it can be multiplied with a blendshapes matrix.
    Note that the resulting Eigen::Map only lives as long as the data given lives and is in scope.
    Args:
        coefficients: Vector of blendshape coefficients.
    Returns:
        An Eigen::Map pointing to the given coefficients data.
    """
    return np.array(coefficients)
