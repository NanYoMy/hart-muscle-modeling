import SimpleITK as sitk
from sitkdata import *
import sys

def example(filein, fileout):
	imgin = read_img(filein)
	datain = img_to_data(imgin)

	#Low is end inclusive, high is end exclusive
	#inputs are tuples (x, y, z)
	#Be ware of varying coordinate frames (LPS VS RAS)
	#as that may affect coordinate values
	low = (0, 0, 0)
	high = (1, 1, 1)
	dataout = get_box(datain, low, high)

	imgout = data_to_img(dataout)
	write_img(imgout, fileout)



if __name__ == "__main__":
	if len(sys.argv) > 1:
		example(sys.argv[1], sys.argv[2])