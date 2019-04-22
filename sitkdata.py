

def get_value3d(data, x, y, z):
	return data[z, y, x]

def get_value2d(data, i, j):
	return data[j, i]

def set_value3d(data, x, y, z, value):
	data[z, y, x] = value

def set_value2d(data, i, j, value):
	data[j, i] = value
	
def get_size(data):
	shape = data.shape
	return shape[::-1]

def get_empty2d(ilen, jlen):
	return np.zeros((jlen, ilen))

def get_empty3d(xlen, ylen, zlen):
	return np.zeros((zlen, ylen, xlen))

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
