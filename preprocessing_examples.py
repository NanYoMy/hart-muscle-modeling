import preprocessing
import sitkdata
import sys, os
import time




def examples(filename, outpath="example_results"):
	start = time.time()

	if not os.path.isdir(outpath):
		os.makedirs(outpath)

	'''
	Basic sitkdata functionality
	'''

	img = sitkdata.read_img(filename)
	data = sitkdata.img_to_data(img)

	data_backup = sitkdata.copy(data)

	size = sitkdata.get_size(data)
	print("Image size: " + str(size))

	test_coord = [x//2 for x in size]
	test_val = sitkdata.get_value(data, test_coord)
	print("Value at test_coord " + str(test_coord) + ": " + str(test_val))

	sitkdata.set_value(data, 255 - test_val, test_coord)
	print("New value at test_coord " + str(test_coord) + ": " + str(255 - test_val))
	print()


	print("Resetting values....  Done!")
	data = data_backup
	print()

	'''
	Beginning of preprocessing examples
	'''

	'''
	Smoothing
	'''
	k = 1
	print("Smoothing k=" + str(k) + " times...")

	smoothed = data
	for _ in range(k):
	#	smoothed = preprocessing.smoothing(smoothed, preprocessing.average_kernel)
	
	print("Done! " + str(time.time() - start) + " seconds since beginning.")
	print()

	print("Saving smoothed image... " )


	print("Done!")
	print()


	'''
	Parameter Setup
	'''
	params = {}




	param_keys = preprocessing.safe_keys()

	for key in param_keys:
		value = preprocessing.safe_find(params, key)
		if key not in params:
			print("No value for " + str(key) + " found. Using default "\
				+ str(value) + " instead.")
		else:
			print("Param " + str(key) + " set to value " + str(value) + ".")

	'''
	Finding bounding box
	'''

	low, high = preprocessing.find_bounding_box(smoothed, params)

	print("Bounding Box: " + str(low) + ", " + str(high))
















if __name__ == "__main__":
	if len(sys.argv) == 2:
		examples(sys.argv[1])
	elif len(sys.argv) == 3:
		examples(sys.argv[1], sys.argv[2])
