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
	In order to ensure functionality, the first priority should be getting some form of preprocessing working. However, ultimately the naive implementation would be too slow to be used practically. For this, a parameter dictionary system is implemented to allow one to choose between various function options.




