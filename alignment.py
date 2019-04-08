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
Code For Computing Axis of Alignment



"""
def align_axis(data):

    #reformat data to report 1 if there is an artifact there and 0 otherwise
    pca_indicator = [[[1 if k != 0 else 0 for k in data[i, j]] for j in range(len(data[i]))] for i in range(len(data))]

    #loop through entire face to determine where the indicator lies
    midpoints = []
    for slice in range(len(pca_indicator)):
        valid_points = []
        count = 0
        for row in range(len(slice)):
            for col in range(len(row)):
                if pca_indicator[slice][row][col] == 1:
                    valid_points.append([col, row, slice])
                    count += 1
        if count > 0:
            mean = np.sum(np.array(valid_points), axis=0)/count
        midpoints.append(mean)
    pca = PCA(n_components=2)
    return pca.fit_transform(np.array(midpoints).T), midpoints[0]

