import preprocessing
import sitkdata
import sys




def examples(filename):
	img = sitkdata.read_image(filename)
	data = img_to_data(img)
	size = sitkdata.get_size(data)
	print("Image size: " + str(size))

	test_coord = [x//2 for x in size]
	test_val = sitkdata.get_value(data, test_coord)
	print("Value at test_coord " + str(test_coord) + ": " + str(test_val))

	sitkdata.set_value(data, 255 - test_val, test_coord)
	print("New value at test_coord " + str(test_coord) + ": " + str(255 - test_val))




if __name__ == "__main__":
	if len(sys.argv) > 1:
		examples(sys.argv[1])
