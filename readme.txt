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
			-What pixel values?
				This is harder than one might initially think. From preliminary analysis, I was unable to determine some kind of accurate threshold for what pixels we should include
			-Image smoothing
				This will remove variation, reduce noise, and help make the image more likely to be contiguous
			-
		-Reorient the image:

		-Determine the largest area slice and find points along the perimeter:


Preprocessing Parameters
	In order to ensure functionality, the first priority should be getting some form of preprocessing working. However, ultimately the naive implementation would be too slow to be used practically. For this, a parameter dictionary system is implemented to allow one to choose between various function options.




