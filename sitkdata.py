import SimpleITK as sitk
import numpy as np


def get_value(data, *args):
	if type(args[0]) == type([]) or type(args[0]) == type(()):
		return data[tuple(args[0][::-1])]
	return data[tuple(args[::-1])]

def set_value(data, value, *args):
	if type(args[0]) == type([]) or type(args[0]) == type(()):
		data[tuple(args[0][::-1])] = value
	else:
		data[tuple(args[::-1])] = value

def get_size(data):
	shape = data.shape
	return shape[::-1]

def get_empty(*args):
	return np.zeros(tuple(args[::-1]))

def copy(data):
	return np.copy(data)

def data_to_img(data):
	return sitk.GetImageFromArray(data)

def img_to_data(img):
	return sitk.GetArrayFromImage(img)


def read_img(path, ultrasound=True):
    """Load image from filepath as SimpleITK.Image

    :param path: Path to .nii file containing image.
    :param ultrasound_slice: Optional. If True, image will be cast as sitkUInt16 for ultrasound images.
    :type path: str
    :returns: Image object from path
    :rtype: SimpleITK.Image
    """
    image = sitk.ReadImage(path)
    if ultrasound:
        image = sitk.Cast(image, sitk.sitkUInt16)
    return image


def write_img(image, path):
    """Write an image to file

    :param image: Image to be written
    :param path: Destination where image will be written to
    :type image: SimpleITK.Image
    :type path: str
    :rtype: None
    """
    sitk.WriteImage(image, path)


'''
Returns a 2d array of the specified slice
:param data: 3d array of image values
:param low: lower bounds of image (inclusive)
:param high: higher bounds of image (exclusive)
:param cs: cross section slice index
:param direction: 0 = x direction, 1 = y direction, 2 = z direction
'''
def get_slice(data, low, high, cs, direction):
	if direction == 0:
		getter = lambda i, j: get_value3d(data, cs, i, j)
		idir = 1
		jdir = 2
	elif direction == 1:
		getter = lambda i, j: get_value3d(data, i, cs, j)
		idir = 0
		jdir = 2
	else:
		getter = lambda i, j: get_value3d(data, i, j, cs)
		idir = 0
		jdir = 1
	ilen = high[idir] - low[idir]
	jlen = high[jdir] - low[jdir]
	d2 = get_empty2d(ilen, jlen)

	for i in range(ilen):
		for j in range(jlen):
			set_value2d(d2, i, j, getter(i + low[idir], j + low[jdir]))
	return d2


'''
Returns trimmed 3d box between low and high coordinates in data
:param data: 3d array of values
:param low: lower bounds (inclusive)
:param high: higher bounds (exclusive)
'''
def get_box(data, low, high):
	return data[low[2]:high[2], low[1]:high[1], low[0]:high[0]]


    

def point_mask_3d(data, points):
	xlim, ylim, zlim = get_size(data)
	data = copy(data)
	for x in range(xlim):
		for y in range(ylim):
			for z in range(zlim):
				if (x, y, z) not in points:
					set_value3d(data, x, y, z, 0)
	return data

def point_mask_2d(data, flat_points):
	ilim, jlim = get_size(data)
	data = copy(data)
	for i in range(ilim):
		for j in range(jlim):
			if (i, j) not in flat_points:
				set_value2d(data, i, j, 0)
	return data
