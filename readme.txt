HART LAB - hart-muscle-modeling REPO

This file serves as an introduction for the "hart-muscle-modeling" repo used by the HART lab at UC Berkeley in order to model muscles using ultrasound segmentations. This readme currently focuses mostly on the registration approach to modeling.


File System

Note that the structure may need to be restructured later in order to incorporate proper dependencies between files without simply leaving everything in a single directory. Make sure to update the ".gitignore" file (if you are using one) if this is the case.

Subdirectories
	The two main subdirectories of this repo are the the "registration" and "transformation" directories. Each of these are designed to be self-contained for ease of sharing or publishing, so the code implemented in these bypasses abstractions used elsewhere and does have some redundancies.

	In order to use this code without causing a bunch of git merge errors, it is recommended that you either make a copy of the code external to the repo (which, due to lack of dependencies at the moment, would work), or make a copy of the code or spreadsheet file and update the ".gitignore" file:

		#Run in main directory
		cp registration/registration.py registration_local.py
		echo "registration/registration_local.py" >> .gitignore
		#Now edit and run "registration/registration_local.py"

	registration/
		A self-contained directory of pure registration code

		registration.py:
			A self-contained file template for registration. Simply copy the file to a new location and edit the variables in the main function to run. 

	transform/
		 A sel-contained directory of pure transform code

		 readme-transform.txt
		 	An explanation of how to use the transform code

		 transform.py
		 	A self-contained file template for tranformation. There are two ways to run this code.
		 	Either copy the file location and edit the variables at the bottom of the file,
		 	or run with a copy of the "transform_formatting.xlsx" (see "readme-transform.txt" for more info")

		 transform_formatting.xlsx
		 	A formatting file to run numerous transformations at once (see "readme-transform.txt" for more info")

General Files
	There are some miscellaneous files in the directory. "preprocessing.py" will be explained in further detail below (See "Registration Prepocessing")

	sitkdata.py
		This class abstracts away SITK and numpy functions. It is recommended to work with this abstraction as opposed to directly referencing SITK and numpy as the coordinates are inverted (so (z, y, x)) for arrays coming from sitk images.

	cropping_example.py
		An example of how to crop an image using SITK. Make sure to make a copy before using (and possibly include in ".gitignore") to avoid git merge conflicts

	rename.py
		Code to convert all ".mha" files in a directory into ".nii"

	preprocessing.py
		The first implementation of a pipeline for the registration approach to muscle modeling

	preprocessing_examples.py
		The first test script for running stages of the preprocessing for registation for muscle modeling code

Registration Preprocessing
	Below is the general workflow for how to approach preprocssing for muscle modeling using registration. This is a rough outline and could possibly use some tuning in order to improve runtime.

		-Determine what is considered the image:
			-What voxel values?
				This is harder than one might initially think. From preliminary analysis, I was unable to determine some kind of accurate threshold for what voxels we should include
			-Image smoothing
				This will remove variation, reduce noise, and help make the image more likely to be contiguous
			-Image location
				This generally requires finding a bounding box around the image. This will save on computation time when computing other values.

				This can be sped up by the order we check voxels (e.g. inside out, outside in, left to right) although some of these might have contiguity requirements.
		-Reorient the image:
			-Find principal axis
				We can model a line with the following equations:
					x(t) = x_0 + a*t
					y(t) = y_0 + b*t
					z(t) = z_0 + c*t
					t_0 <= t <= t_1
				We can ignore the bounds on t while we solve for the axis and calculate them afterwards. They would be useful to ensure the image is in frame after transforming.

				This then becomes the following optimization:

				min_{a, b, c, x_0, y_0, z_0} D
				D = min_t (sum_i ((x_i - x(t))^2 + (y_i - y(t))^2 + (z_i - z(t))^2))

				There was mention of this possibly being solved with total least squares. However, as there are infinite solutions to this problem, this might not be the best approach.

				We can simplify this problem to have a unique solution. The principal axis will always pass through the mean point, so (x_0, y_0, z_0) = (x_bar, y_bar, z_bar). We can then let a = 1. This then gives us t_i = x_i - x_0 and allows us to remove the inner most minimization. This problem may be convex, but it isn't linear. However, simplifying it to two variables (b and c) is a great start.
			-Transform + ensure in frame
				Transform principal axis to align with with a coordinate axis. Make sure the entire scan is still in frame, so might need to zoom in or out or perform a translation. This is also a possible reason to delay the bounding box step mentioned above
			-Relocate in image and crop
				Basically the same as "Image location" above
		-Determine the largest area slice and find points along the perimeter:
			-Find largest area slice
				Once the principal axis is aligned to a coordinate axis, this problem becomes much easier. The main issue is determining the boundary of the slice when summing, which relates back to "What voxel values?" above.

				If we look at a function A(z) being the area of slice z and assume it to be concave, we can then take an iterative approach similar to binary search to save on run time
			-Find perimeter points
				This would basically be a variation of finding an area slice. Just check if the voxel is both part of the image (assuming contiguity) and adjacent to a voxel that isn't.
			-Sample perimeter points
				Just use the gathered points and pick somehow. Not hard to do, but sampling method might matter.

Preprocessing Parameters
	In order to ensure functionality, the first priority should be getting some form of preprocessing working. However, ultimately the naive implementation would be too slow to be used practically. For this, a parameter dictionary system is implemented to allow one to choose between various function options. Using a "safe_find" function allows the default choice to be used if one isn't sure what option to pick

	NOTE: Majority of these methods are still being debugged/aren't tested, so the naive (but slow) approach may be the most accurate. So, if you are unsure of what to do, just don't pass in anything (same as using an empty dictionary, so goes to default)

	Parameters:

		"bounding_box_method": The method determining how to find a bounding box around an image using the function "find_bounding_box"
			Default: "naive": Checks every voxel
			"truncate": Assuming contiguity, tries to end early once it "passes" the scan in space. Direction of approach can be changed with "bounding_box_parameters"
			"outsidein": Assuming contiguity, starts from the outside layers and works inward until each side "touches" the image. Good for scans that take up majority of the image space
			Possible other options not yet implemented:
				"insideout": Opposite of "outsidein". Assumes contiguity

		"bounding_box_parameters": A length 2 tuple determining the principal axis (x == 0, y == 1, z == 2) followed by the orientation (low to high == 0, high to low == 1) specifying the direction for the "truncate" option for "bounding_box_method" for the function "find_bounding_box"
			Default: (0, 0)

		"plane_detect": The function "find_bounding_box" with params "truncate" and "outsidein" call the helper function "plane_detect", which checks the parameter "plane_detect" to determine how to work. This function determines if there is a scan value in the specified plane, and depending on the parameters returns the bounds of the scan (assuming contiguity)
			Default: "fast_naive": Checks every pixel and just returns true or false
			"full_naive": Checks every pixel and returns true or false along with bounds on the scan in that plane
			"fast_convex": Mimicking binary search, this function assumes that a function of the sum of the scan values in each line is negatively convex, and uses this to perform binary search like jumps iteratively until the boundary is found
			"full_convex": Not yet implemented, but would be "fast_convex" but returning the scan bounds as well

		"bounding_box_to_largest_area_slice": Parameter determining the approach of the "bounding_box_to_largest_area" function
			Default: "naive": Naive approach, so checks every slice and finds area
			"convex": Assumes a function mapping slice index to area of slice is negatively convex and uses this to perform a modified binary search for the largest area slice

		"plane_area": Parameter determining apprach of the "bounding_box_to_largest_area" function when using the "bounding_box_to_largest_area_slice" setting "convex"
			Default: "naive": Just checks every pixel

		"perimeter_points_to_samples": Takes a set of coordinates in a cross section plane and returns a set of sampled points. 
			Default: "naive": Samples randomly a set amount of points

		"n_samples": A parameter used by "perimeter_points_to_samples". For methods of sampling that define a set amount of samples, this value is used. Make sure to pass in a string of the integer value. safe_find casts as an integer before passing out
			Default: "10"

		"is_filled": Probably the most important parameter. This function determines whether a given value is actually part of the scan or not. This parameter should be inputted as a boolena expression based in "x" (e.g. "x > 0"), which then becomes `lambda x: x > 0`, with the value of the pixel/voxel being passed in. To use other information, such as adjacent values, this would need to be modified (possibly precompute which pixels/voxels are part of the image and just use this function to reference it). Be aware that this function could easily be used to highjack the code, so this should be modified to use preset options at some point in the future. Note also that "safe_find" returns the lambda function, while the dictionary should store the boolean expression
			Default: "x > 0" -> `lambda x : x > 0`


Default Dictionary:
	Currently the best default dictionary is to specify no parameters beyond the "is_filled" one. Update this as time goes on for a good go-to approach for this

	{
		"is_filled" : "x > 100"
	}



