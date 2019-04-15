import numpy as np
import SimpleITK as sitk
from sklearn.decomposition import PCA


from preprocessing import read_img,img_to_data


def main(inpath):

    #read in data from filepath
    inimage = read_img(inpath)

    #load data into numpy array
    data = img_to_data(inimage)

    align_axis(data)

"""
Code For Computing Axis of Alignment Using Midpoints of Each Slice

Input: 3D Numpy Array (sitk image in numpy array format)
Output: 3D Vector (First PCA Component)
"""
def align_axis_mid_slices(data):

    #reformat data to report 1 if there is an artifact there and 0 otherwise
    pca_indicator = [[[1 if k != 0 else 0 for k in data[i, j]] for j in range(len(data[i]))] for i in range(len(data))]

    #loop through entire face to determine where the indicator lies
    midpoints = []
    for slice in range(len(pca_indicator)):
        valid_points = []
        count = 0
        for row in range(len(pca_indicator[0])):
            for col in range(len(pca_indicator[0][0])):
                if pca_indicator[slice][row][col] == 1:
                    valid_points.append([col, row, slice])
                    count += 1
        if count > 0:
            mean = np.sum(np.array(valid_points), axis=0)/count
        midpoints.append(mean)
    pca = PCA(n_components=1)
    return pca.fit_transform(np.array(midpoints).T)

"""
Code For Computing Axis of Alignment Using PCA

Input: 3D Numpy Array (sitk image in numpy array format)
Output: 3D Vector (First PCA Component)
"""

def align_axis_pca(data):

    points = []
    for slice in range(len(data)):
        for row in range(len(data[0])):
            for col in range(data[0][0]):
                if data[slice][row][col] != 0:
                    points.append([col,row,slice])
    pca = PCA(n_components=1)
    return pca.fit_transform(np.array(points.T))

"""
Code For Computing Axis of Alignment Using Least Squares

Input: 3D Numpy Array (sitk image in numpy array format)
Output: 3D Vector (First PCA Component)
"""
def align_axis_least_squares(data):

    points = []
    for slice in range(len(data)):
        for row in range(len(data[0])):
            for col in range(data[0][0]):
                if data[slice][row][col] != 0:
                    points.append([col, row, slice])
    pca = PCA(n_components=1)
    return pca.fit_transform(np.array(points.T))

