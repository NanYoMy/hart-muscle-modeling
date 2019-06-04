HART LAB - hart-muscle-modeling REPO

This file serves as an introduction for the "hart-muscle-modeling" repo used by the HART lab at UC Berkeley in order to model muscles using ultrasound segmentations. This readme currently focuses mostly on the registration approach to modeling.


File System

Note that the structure may need to be restructured later in order to incorporate proper dependencies between files without simply leaving everything in a single directory. Make sure to update the ".gitignore" file if this is the case.

Subdirectories
	The two main subdirectories of this repo are the the "registration" and "transformation" directories. Each of these are designed to be self-contained for ease of sharing or publishing, so the code implemented in these bypasses abstractions used elsewhere and does have some redundancies.

	In order to 

modeling/registration/
	A self-contained directory of pure registration code

	registration.py:
		A self-contained file template for registration. Simply edit the variables in the main function to run. 

		It is recommended that you copy this file to "registration_local.py". The ".gitignore" for this repo includes "registration/registration_local.py", meaing that doing this allows you to edit "registration_local.py" freely for each iteration of registration you do without 