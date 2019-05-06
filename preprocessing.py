 import SimpleITK as sitk
import numpy as np
from sitkdata import *

'''
Brief overview of the file:

*Read doc for functions before using them
*Helper functions at the bottom are useful (eg convert image to 3darray, etc)
**This is especially helpful since sitk indexing is (z, y, x), so this abstracts that away
*"data" param generally refers to an array as opposed to an image
*I implemented a parameter system to a basic degree (similar to sitk's parameters).
	If you aren't sure about which one to use, just pass in an empty dictionary.
	This defaults to the most naive approach, which will take longer but has the
	least implicit assumptions.
	**The main parameter you might wanna change is "checker". As of now, safe_find
		defaults to params["checker"] = lambda x: x > 0.
		This is used to determine if we are looking at a said pixel (aka part of image)
		or not. So for example, you might want to set a threshold, 
		or perhaps a specific value if looking 



'''




'''
Function to implement some workflow, still not fully implemented.
Could be useful to see how things are called.
:param inpath: Image file to read in
:param outpath: Place to save output slice
:ptype inpath: string
:ptype outpath: string
'''
def main(inpath, outpath):
	pass



'''
Applies the given kernel function to every voxel in data
:param data: 3d array of image values
:param kernel: lambda function (data, x, y, z) -> value

'''
def smoothing(data, kernel):
	xlen, ylen, zlen = get_shape(data)
	outdata = get_empty(xlen, ylen, zlen)
	for x in range(xlen):
		for y in range(ylen):
			for z in range(zlen):
				set_value(outdata, kernel(data, x, y, z), x, y, z)

	return outdata


'''
A basic kernel function to average values in an image
:param data: 3d array of image values
:param x: x coordinate
:param y: y coordinate
:param z: z coordinate
:returns: 3d array of image values with kernel applied
'''
def average_kernel(data, x, y, z):
	points = set()
	xlen, ylen, zlen = get_shape(data)
	for i in range(max(x-1, 0), min(x+2, xlen)):
		for j in range(max(y-1, 0), min(y+2, ylen)):
			for k in range(max(z-1, 0), min(z+2, zlen)):
				points.add((i, j, k))
	if len(set) == 0:
		return 0
	return sum([get_value(data, i, j, k) for i, j, k in points]) / len(set)


'''
Checks if image is contiguous.
As of now only naive implementation, so will take a long time to run.
Set parameter "contiguous" to specify method of computation
:param data: 3d array of image values
:param params: dictionary specifying methods
'''
def check_contiguous(data, params):
	method = safe_find(params, "contiguous")
	if method is "naive":
		return _check_contiguous_naive(data, params)



'''
Finds a bounding box around all voxels such that checker(value) == true
"checker" defaults to lambda value: value > 0
Bounds are beginning inclusive and end exclusive
Change "bb_method" parameter to change implementation. Default is naive
	-"naive": Checks every pixel 
	-"truncate": Stops checking internal values once extremes are reached. Basically a generic, slightly optimized approach
	-"outsidein": Starts from outer layer and works inward until hits the image. Good for large images
:param data: 3d array of image values
:param params: dictionary of parameters
'''
def find_bounding_box(data, params):
	method = safe_find(params, "bb_method")

	#untested
	if method is "naive":
		return _find_bounding_box_naive(data, params)
	#untested
	elif method == "truncate":
		return _find_bounding_box_truncate(data, params)
	#untested
	elif method == "outsidein":
		return _find_bounding_box_outsidein(data, params)

'''
Namely just a helper function for find_bounding_box. Not designed to be used outside of it.
Default uses "checker" value of lambda value: value > 0

"plane_detect" parameter values:
*"fast_naive": Just gets true or false naively as fast as possible
*"full_naive": (Default) Naive approach to get true/false and also plane boundaries (in i,j coords)
*Convex ones assume along axis k, -1*area(slice_k) is convex
**"fast_convex" is fast_naive with convex assumption
**"full_convex" is full_naive with convex assumption 


:param getter: lambda i, j: value at (i, j)
:param ilen: length in i direction
:param jlen: length in j direction
:param params: dictionary of parameters


'''
def plane_detect(getter, ilen, jlen, params):
	method = safe_find(params, "plane_detect")
	#untested
	if method == "fast_naive":	
		return _plane_detect_fast_naive(getter, ilen, jlen, params)
	#untested
	elif method == "full_naive":
		return _plane_detect_full_naive(getter, ilen, jlen, params)
	#untested
	elif method == "fast_convex":
		return _plane_detect_fast_convex(getter, ilen, jlen, params)
	elif method == "full_convex":
		pass

'''
Finds the largest slice along the longest axis of 3d array
ASSUMPTION: Principal axis parallel to longest bounding box axis.
Other principal axes also parallel to bounding box axes.
Contiguous assumptions as well, at least for convexity
Default "checker" is lambda value: value > 0
Parameter "bb_to_las":
*"naive": Naive appraoach
*"convex": Assumes -area(slicek) is convex in function of k
:param data: 3d array of image values
:param low: lower bounds of data (inclusive)
:param high: higher bounds of data (exclusive)
:param params: dicitonary of parameter values
'''
def bounding_box_to_largest_area(data, low, high, params):
	xlen = high[0] - low[0]
	ylen = high[1] - low[1]
	zlen = high[2] - low[2]

	method = safe_find(params, "bb_to_las")
	checker = safe_find(params, "checker")

	if xlen > ylen:
		if zlen > xlen: #zlen greatest
			getter = lambda cs, i, j : get_value(data, low[0] + i, low[1] + j, low[2] + cs)
			ilen = xlen
			jlen = ylen
			pclen = zlen
			direction = 2
		else: #xlen greatest
			getter = lambda cs, i, j : get_value(data, low[0] + cs, low[1] + i, low[2] + j)
			ilen = ylen
			jlen = zlen
			pclen = xlen
			direction = 0
	else:
		if ylen > zlen: #ylen greatest
			getter = lambda cs, i, j : get_value(data, low[0] + i, low[1] + cs, low[2] + j)
			ilen = xlen
			jlen = zlen
			pclen = ylen
			direction = 1
		else: #zlen greatest
			getter = lambda cs, i, j : get_value(data, low[0] + i, low[1] + j, low[2] + cs)
			ilen = xlen
			jlen = ylen
			pclen = zlen
			direction = 2
	#untested
	if method == "naive":
		return _bounding_box_to_largest_area_naive(low, high, checker, getter, ilen, jlen, pclen, direction)
		
	#cuts down time in half, though still asymptotically the same
	#untested
	elif method == "convex":
		return _bounding_box_to_largest_area_convex(getter, pclen, ilen, jlen, params)


#Helper for "bounding_box_to_largest_area" "convex" setting
def plane_area(getter, cs, ilen, jlen, params):
	method = safe_find(params, "plane_area")
	checker = safe_find(params, "checker")
	if method == "naive":
		return _plane_area_naive(getter, cs, ilen, jlen, params)


'''
Gets a set of points in the given 2d slice that constitute the perimeter
Default "checker" is lambda value: value > 0
:param slc: 2d array of image slice values
:param params: dictionary of parameter values
:returns: set of points in 2d plane
'''
def slice_to_perimeter_points(slc, params):
	flat_points = set()
	shape = get_size(slc)

	checker = safe_find(params, "checker")

	def perim(i0, j0):
		if not checker(get_value(slc, i0, j0)):
			return False
		contact = False
		checks = set()
		if i0 == 0 or j0 == 0 \
			or i0 == shape[0] or j0 == shape[1]:
			return True

		for i in range(i0 - 1, i0 + 2):
			for j in range(j0 - 1, j0 + 2):
				checks.add((i,j))
		checks.remove((i0, j0))

		while not contact or len(checks) > 0:
			i, j = checks.pop()
			contact = contact or checker(get_value(slc, i, j))
		return contact

	for i in range(shape[0]):
		for j in range(shape[1]):
			if perim(i, j):
				flat_points.add((i,j))

	return flat_points


'''
Samples a set of points based on given set of points
:param data: slice
'''
def perimeter_points_to_sampled(data, flat_points, params):
	method = safe_find(params, "pp_to_samp")
	if method == "naive":
		return _points_to_sampled_naive(flat_points, params)


'''
Needs fixing, but not essential

def fp_to_3d(cs, direction, points):
	points = set()
	if direction == 0:
		for fp in slice_points:
			points.add((cs, fp[0], fp[1]))
	elif direction == 1:
		for fp in slice_points:
			points.add((fp[0], cs, fp[1]))
	elif direction == 2:
		for fp in flat_points:
			points.add((fp[0], fp[1], cs))
	return points

'''


'''
A "safe" way to retrieve dictionary values. If key is not found, returns a default
:param d: dictionary
:param key: dictionary key
'''
def safe_find(d, key):
	if d is None or key in d:
		return d[key]
	if key == "bb_method":
		return "naive"
	if key == "bb_params":
		return (0,0)
	if key == "plane_detect":
		return "full_naive"
	if key == "bb_to_las":
		return "convex"
	if key == "plane_area":
		return "naive"
	if key == "pp_to_samp":
		return "naive" 
	if key == "n":
		return 10
	if key == "checker":
		return lambda x: x > 0
	if key == "contiguous":
		return "naive"


'''
Specialized Methods. DON'T call these directly
'''


def _check_contiguous_naive(data, params):
	xlen, ylen, zlen = get_size(data)
	filled = set()
	connected = set()
	checked = set()
	for x in range(xlen):
		for y in range(ylen):
			for z in range(zlen):
				if get_value(data, x, y, z) > 0:
					start = (x, y, z)
					break

	connected.add(start)
	while len(connected) > 0:
		point = connected.pop()
		checked.add(point)
		for x in range(max(0, point[0]-1, min(xlen, point[0] + 2))):
			for y in range(max(0, point[1]-1, min(ylen, point[1] + 2))):
				for z in range(max(0, point[2]-1, min(zlen, point[2] + 2))):
					new_point = (x, y, z)
					if new_point not in checked and get_value(data, x, y, z) > 0:
						connected.add(new_point)

	for x in range(xlen):
		for y in range(ylen):
			for z in range(zlen):
				if (x, y, z) not in checked and get_value(data, x, y, z) > 0:
					return False

	return True



def _find_bounding_box_naive(data, params):
	xlim, ylim, zlim = get_size(data)
	checker = safe_find(params, "checker")
	found = False
	for x in range(xlim):
		for y in range(ylim):
			for z in range(zlim):
				if checker(get_value(data, x, y, z)):
					if found: 
						xlow = min(x, xlow)
						ylow = min(y, ylow)
						zlow = min(z, zlow)
						xhigh = max(x, xhigh)
						yhigh = max(y, yhigh)
						zhigh = max(z, zhigh)
					else:
						found = True
						xlow = xhigh = x
						ylow = yhigh = y
						zlow = zhigh = z
	if found:
		return (xlow, ylow, zlow), (xhigh, yhigh, zhigh)
	else:
		return (0, 0, 0), (0, 0, 0)



def _find_bounding_box_truncate(data, params):
	xlim, ylim, zlim = get_shape(data)
	checker = safe_find(params, "checker")
	pa, orien = safe_find(params, "bb_params")
	if pa == 0:
		palen = xlim
		ilen = ylim
		jlen = zlim
		getter = lambda i, j: get_value(data, cs, i, j)
		reorder = lambda cs, i, j: (cs, i, j)
	elif pa == 1:
		palen = ylim
		ilen = xlim
		jlen = zlim
		getter = lambda i, j: get_value(data, i, cs, j)
		reorder = lambda cs, i, j: (i, cs, j)
	elif pa == 2:
		palen = zlim
		ilen = xlim
		jlen = ylim
		getter = lambda i, j: get_value(data, i, j, cs)
		reorder = lambda cs, i, j: (i, j, cs)

	steps = range(palen) if orien == 0 else range(palen - 1 , -1, -1)
	first_found = False
	ilow = jlow = cslow = 0
	ihigh = jhigh = cshigh = 0

	for cs in steps:
		found, (i0low, i0high), (j0low, j0high) = plane_detect(getter, ilen, jlen, params)
		
		if found and first_found:
			ilow = min(ilow, i0low)
			ihigh = max(ihigh, i0high)
			jlow = min(jlow, j0low)
			jhigh = max(jhigh, j0high)
			cslow = min(cslow, cs)
			cshigh = min(cshigh, cs)

		elif first_found:
			break

		elif found:
			ilow, ihigh = i0low, i0high
			jlow, jhigh = j0low, j0high
			first_found = True
	if first_found:
		return reorder(cslow, ilow, jlow), reorder(cshigh + 1, ihigh + 1, jhigh + 1)
	return (0, 0, 0), (0, 0, 0)

def _find_bounding_box_outsidein(data, params):
	xlim, ylim, zlim = get_shape(data)
	checker = safe_find(params, "checker")
	xlow = ylow = zlow = 0
	xhigh = xlim - 1
	yhigh = ylim - 1
	zhigh = zlim - 1

	getter = lambda y, z: get_value(data, x, y, z)

	x = 0
	found = False
	while x < xlim and not plane_detect(getter, ylim, zlim, params):
		x += 1

	if x == xlim:
		return (0, 0), (0, 0), (0, 0)
	xlow = x

	x = xhigh
	while x >= xlow and not plane_detect(getter, ylim, zlim, params):
		x -- 1
	xhigh = x

	getter = lambda x, z: get_value(data, xlow + x, y, z)
	
	y = 0
	xlen = xhigh - xlow + 1
	while y < ylim and not plane_detect(getter, xlen, zlim, params):
		y += 1
	ylow = y

	y = yhigh
	while y >= ylow and not plane_detect(getter, xlen, zlim, params):
		y -= 1
	yhigh = y

	getter = lambda x, y: get_value(data, x + xlow, y + ylow, z)

	y = 0
	ylen = yhigh - ylow + 1
	while z < zlim and not plane_detect(getter, xlen, ylen, wparams):
		z += 1
	zlow = z

	z = zhigh
	while z >= zlow and not plane_detect(getter, xlen, wparams):
		z -= 1
	zhigh = y
	return (xlow, xhigh + 1), (ylow, yhigh + 1), (zlow, zhigh + 1)	


def _plane_detect_fast_naive(getter, ilen, jlen, params):
	checker = safe_find(params, "checker")
	for i in range(ilen):
		for j in range(jlen):
			if checker(getter(i, j)):
				return True
		return False

def _plane_detect_full_naive(getter, ilen, jlen, params):
		checker = safe_find(params, "checker")
		found = False
		for i in range(ilen):
			for j in range(jlen):
				if checker(getter(i, j)):
					if found:
						ilow = min(i, ilow)
						ihigh = max(i, ihigh)
						jlow = min(j, jlow)
						jhigh = max(j, jhigh)
					else:
						found = True
						ilow = ihigh = i
						jlow = jhigh = j
		if found:
			return found, (ilow, ihigh + 1), (jlow, jhigh + 1)
		else:
			return found, (0, 0), (0, 0)

def _plane_detect_fast_convex(getter, ilen, jlen, params):
	checker = safe_find(params, "checker")
	def line_detect(i):
			for j in len(jlen):
				if checker(getter(i, j)):
					return True
			return False

	i = max(0, min(ilen - 1, ilen//2))
	if line_detect(i) or line_detect(0) or line_detect(ilen-1):
		return True
	queue = set()
	queue.add((0, i))
	queue.add((i, ilen))
	while len(queue) > 0:
		bounds = queue.pop()
		ilow = bounds[0]
		ihigh = bounds[1]
		i = max(ilow, min(ihigh, (ilow + ihigh)//2))
		if ilow != i and i != ihigh:
			if line_detect(i):
				return True
			queue.add((ilow, i))
			queue.add((i, ihigh))
	return False

def _bounding_box_to_largest_area_naive(low, checker, getter, ilen, jlen, pclen, direction):
	areas = [0]*pclen
	for cs in range(pclen):
		for i in range(ilen):
			for j in range(jlen):
				areas[cs] += checker(getter(cs, i, j) )
	return low[direction] + areas.index(max(areas)), max(areas), direction

def _bounding_box_to_largest_area_convex(getter, pclen, ilen, jlen, params):
	cslow = 0
	cshigh = pclen - 1
	alow = plane_area(getter, cslow, ilen, jlen, params)
	ahigh = plane_area(getter, cshigh, ilen, jlen, params)
	csmid = min(cshigh, max(cslow, (cshigh + cslow)//2))

	while alow != amid and amid != ahigh:
		if alow > amid:
			newcs = min(csmid, max(cslow, (cslow + csmid)//2))
			newa = plane_area(getter, newcs, ilen, jlen, params)
			csmid, amid, cshigh, ahigh = newcs, newa, csmid, amid
		elif ahigh > amid:
			newcs = min(cshigh, max(csmid, (cshigh + csmid)//2))
			newa = plane_area(getter, newcs, ilen, jlen, params)
			cslow, alow, csmid, amid = csmid, amid, newcs, newa
		else:
			mid1cs = min(csmid, max(cslow, (cslow + csmid)//2))
			mid2cs = min(cshigh, max(csmid, (cshigh + csmid)//2))
			mid1a = plane_area(getter, mid1cs, ilen, jlen, params)
			mid2a = plane_area(getter, mid2cs, ilen, jlen, params)
			cslow, alow, cshigh, ahigh = mid1cs, mid1a, mid2cs, mid2a

	return csmid, amid, direction

def _plane_area_naive(getter, cs, ilen, jlen, params):
	area = 0
	for i in range(ilen):
		for j in range(jlen):
			area += checker(getter(cs, i, j))
	return area


def _points_to_sampled_naive(points, params):
	n = safe_find(params, "n")
	samples = set()
	fp = set(flat_points)
	for _ in range(min(max(0, n), len(fp))):
		samples.add(fp.pop())
	return samples



