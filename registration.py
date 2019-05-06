import time

import os
import sys
import glob

import numpy as np

import SimpleITK as sitk


def main():
    """ EDIT THESE VARIABLES"""
    verbose = True
    unsegmented_image = read_file("", True)
    segmented_image = read_file("", True)
    segmentation = read_file("", True)
    image_out = ""

    #x' = Ax + t for affine transform

    A = np.array([[1.0, 1.0, 1.0],
                    [1.0, 1.0, 1.0],
                    [1.0, 1.0, 1.0]])
    t = np.array([[0.0, 0.0, 0.0]])


    """DON'T EDIT BELOW HERE"""

    segmentation = transform(segmentation, generate_affine_transform(segmentation, A, t), verbose)
    segmented_image = transform(segmented_image, generate_affine_transform(segmented_image, A, t), verbose)



    new_segmentation, transform_parameter_maps = segment(unsegmented_image, segmented_image, segmentation, get_param_maps(), verbose)
    write_file(new_segmentation, image_out)


def transform(img, parameter_maps, verbose=False):
    """Transform an image according to some vector of parameter maps

    :param img: Image to be transformed
    :param parameter_maps: Vector of 3 parameter maps used to dictate the
                           image transformation
    :type image: SimpleITK.Image
    :type parameter_maps: [SimpleITK.ParameterMap]
    :returns: Transformed image
    :rtype: SimpleITK.Image
    """

    transform_filter = sitk.TransformixImageFilter()
    if not verbose:
        transform_filter.LogToConsoleOff()
    transform_filter.SetTransformParameterMap(parameter_maps)
    transform_filter.SetMovingImage(img)
    transform_filter.Execute()
    image = transform_filter.GetResultImage()
    return image

def read_file(filename, ultrasound=True):
    """Reads in an ultrasound image file at the path specified
    :param filename: path to file
    :param ultrasound: Casts image if ultrasound
    :type filename: String
    :type ultrasound: bool 
    :returns: Image
    :rtype: SimpleITK.Image
    """
    img = sitk.ReadImage(filename)
    if ultrasound:
        img = sitk.Cast(img, sitk.sitkUInt16)
    return img

def write_file(img, filename):
    sitk.WriteImage(img, filename)

def generate_affine_transform(img, A, t):
    """Initializes an affine transform parameter map for a given image.

    The transform fits the following format: T(x) = A(x-c) + c + t
    This code uses c == 0 as a one could always find an equivalent translation

    :param img: Image to be transformed
    :param A: 3x3 numpy array consisting of a rotation matrix
    :param t: 1x3 numpy array consisting of the translational values
    :returns: SimpleITK.ParameterMap
    :type img: SimpleITK.Image
    :type A: numpy.ndarray
    :type t: numpy.ndarray
    :rtype: dict
    """
    affine = _get_default_affine_transform()

    f = lambda x: tuple([str(i) for i in x])
    affine['Size'] = f(img.GetSize())
    affine['Spacing'] = f(img.GetSpacing())

    affine['Origin'] = f(img.GetOrigin())
    affine['Direction'] = f(img.GetDirection())

    affine['CenterOfRotationPoint'] = f(np.array([0,0,0]))

    transform = np.concatenate((A, t), axis=0)

    affine['TransformParameters'] = f(transform.ravel())
    return affine

def segment(unsegmented_image,
            segmented_image,
            segmentation,
            parameter_maps,
            verbose=False):
    """Segment image using Elastix

    :param segmented_image: Image with corresponding segmentation passed as
                            the next argument
    :param segmentation: Segmentation to be mapped from segmented_image to
                         unsegmented_image
    :param parameter_maps: Optional vector of 3 parameter maps to be used for
                           registration. If none are provided, a default vector
                           of [rigid, affine, bspline] parameter maps is used.
    :param verbose: Flag to toggle stdout printing from Elastix
    :type unsegmented_image: SimpleITK.Image
    :type segmented_image: SimpleITK.Image
    :type segmentation: SimpleITK.Image
    :type parameter_maps: [SimpleITK.ParameterMap]
    :type verbose: bool
    :returns: Segmentation mapped from segmented_image to unsegmented_image
    :rtype: SimpleITK.Image
    """
    transform_parameter_maps = register(
        unsegmented_image, segmented_image, parameter_maps, verbose=verbose)

    if type(transform_parameter_maps) == type({}):
        transform_parameter_maps['ResampleInterpolator'] = ['FinalNearestNeighborInterpolator']
    else:
        for i in range(len(transform_parameter_maps)):
            transform_parameter_maps[i]['ResampleInterpolator'] = ['FinalNearestNeighborInterpolator']
    return transform(
        segmentation, transform_parameter_maps, verbose=verbose), transform_parameter_maps

def register(fixed_image,
             moving_image,
             parameter_maps,
             verbose=False):
    """Register images using Elastix.

    :param parameter_maps: Vector of 3 parameter maps to be used for
                           registration
    :param verbose: Flag to toggle stdout printing from Elastix
    :type fixed_image: SimpleITK.Image
    :type moving_image: SimpleITK.Image
    :type parameter_maps: [SimpleITK.ParameterMap]
    :type verbose: bool
    :returns: transform_parameter_maps
    :rtype: [SimpleITK.ParameterMap]
    """
    registration_filter = sitk.ElastixImageFilter()
    if not verbose:
        registration_filter.LogToConsoleOff()
    registration_filter.SetFixedImage(fixed_image)
    registration_filter.SetMovingImage(moving_image)

    if type(parameter_maps) == type({}):
        parameter_maps['AutomaticTransformInitialization'] = ['true']
    else:
        for i in range(len(parameter_maps)):
            parameter_maps[i]['AutomaticTransformInitialization'] = ['true']

    registration_filter.SetParameterMap(parameter_maps)
    for m in parameter_maps[1:]:
        registration_filter.AddParameterMap(m)


    registration_filter.Execute()
    result_image = registration_filter.GetResultImage()
    transform_parameter_maps = registration_filter.GetTransformParameterMap()

    return transform_parameter_maps


def write_param(parameter_map, parameter_file_out):
    """Write single amsaf_eval result to path

    Writes parameter maps, segmentation, and score of AMSAF result as individual
    files at path.

    :param amsaf_results: Results in the format of amsaf_eval return value
    :param path: Filepath to write results at
    :type amsaf_result: [SimpleITK.ParameterMap, SimpleITK.Image, float]
    :type path: str
    :rtype: None
    """
    sitk.WriteParameterFile(parameter_map, parameter_file_out)





def _get_default_affine_transform():
    affine = {
    'AutomaticScalesEstimation': ('True'),
    'CenterOfRotationPoint': ('0.0', '0.0', '0.0'), 
    'CompressResultImage': ('false',), 
    'DefaultPixelValue': ('0.000000',), 
    'FinalBSplineInterpolationOrder': ('3',),
    'FixedInternalImagePixelType': ('float',), 
    'Index': ('0', '0', '0'), 
    'NumberOfParameters': ('12',),  
    'ResampleInterpolator': ['FinalNearestNeighborInterpolator'], 
    'Resampler': ('DefaultResampler',), 
    'ResultImageFormat': ('nii',), 
    'ResultImagePixelType': ('float',), 
    'Transform': ('AffineTransform',),
    'UseDirectionCosines': ('true',)
    }
    return affine


def get_param_maps():
  rigid = {
    "AutomaticParameterEstimation": ['true'],
    "AutomaticTransformInitialization": ['true'],
    "BSplineInterpolationOrder": ['3.000000'],
    "CheckNumberOfSamples": ['true'],
    "DefaultPixelValue": ['0.000000'],
    "FinalBSplineInterpolationOrder": ['3.000000'],
    "FixedImagePyramid": ['FixedSmoothingImagePyramid'],
    "ImageSampler": ['RandomCoordinate'],
    "Interpolator": ['BSplineInterpolator'],
    "MaximumNumberOfIterations": ['1024.000000'],
    "MaximumNumberOfSamplingAttempts": ['8.000000'],
    "Metric": ['AdvancedMattesMutualInformation'],
    "MovingImagePyramid": ['MovingSmoothingImagePyramid'],
    "NewSamplesEveryIteration": ['true'],
    "NumberOfHistogramBins": ['64.000000'],
    "NumberOfResolutions": ['3.000000'],
    "NumberOfSamplesForExactGradient": ['4096.000000'],
    "NumberOfSpatialSamples": ['2000.000000'],
    "Optimizer": ['AdaptiveStochasticGradientDescent'],
    "Registration": ['MultiResolutionRegistration'],
    "ResampleInterpolator": ['FinalBSplineInterpolator'],
    "Resampler": ['DefaultResampler'],
    "ResultImageFormat": ['nii'],
    "RequiredRatioOfValidSamples": ['0.05'], 
    "Transform": ['EulerTransform'],
    "WriteIterationInfo": ['false'],
    "WriteResultImage": ['true'],
  }
  affine = {
    "AutomaticParameterEstimation": ['true'],
    "AutomaticScalesEstimation": ['true'],
    "CheckNumberOfSamples": ['true'],
    "DefaultPixelValue": ['0.000000'],
    "FinalBSplineInterpolationOrder": ['3.000000'],
    "FixedImagePyramid":
        ['FixedSmoothingImagePyramid'],
    "ImageSampler": ['RandomCoordinate'],
    "Interpolator": ['BSplineInterpolator'],
    "MaximumNumberOfIterations": ['1024.000000'],
    "MaximumNumberOfSamplingAttempts": ['8.000000'],
    "Metric": ['AdvancedMattesMutualInformation'],
    "MovingImagePyramid": ['MovingSmoothingImagePyramid'],
    "NewSamplesEveryIteration": ['true'],
    "NumberOfHistogramBins": ['32.000000'],
    "NumberOfResolutions": ['4.000000'],
    "NumberOfSamplesForExactGradient": ['4096.000000'],
    "NumberOfSpatialSamples": ['2048.000000'],
    "Optimizer": ['AdaptiveStochasticGradientDescent'],
    "Registration": ['MultiResolutionRegistration'],
    "ResampleInterpolator": ['FinalBSplineInterpolator'],
    "Resampler": ['DefaultResampler'],
    "ResultImageFormat": ['nii'],
    "RequiredRatioOfValidSamples": ['0.05'],
    "Transform": ['AffineTransform'],
    "WriteIterationInfo": ['false'],
    "WriteResultImage": ['true'],
  }
  bspline = {
    'AutomaticParameterEstimation': ["true"],
    'CheckNumberOfSamples': ["true"],
    'DefaultPixelValue': ['0.000000'],
    'FinalBSplineInterpolationOrder': ['3.000000'],
    'FinalGridSpacingInPhysicalUnits': ['4.000000'],
    'FixedImagePyramid': ['FixedSmoothingImagePyramid'],
    'GridSpaceSchedule': ['2.803220 1.988100 1.410000 1.000000'],
    'ImageSampler': ['RandomCoordinate'],
    'Interpolator': ['LinearInterpolator'],
    'MaximumNumberOfIterations': ['1024.000000'],
    'MaximumNumberOfSamplingAttempts': ['8.000000'],
    'Metric': ['AdvancedMattesMutualInformation'],
    'Metric0Weight': ['0'],
    'Metric1Weight': ['1.000000'],
    'MovingImagePyramid': ["MovingSmoothingImagePyramid"],
    'NewSamplesEveryIteration': ['true'],
    'NumberOfHistogramBins': ['32.000000'],
    'NumberOfResolutions': ['4.000000'],
    'NumberOfSamplesForExactGradient': ['4096.000000'],
    'NumberOfSpatialSamples': ['2048.000000'],
    'Optimizer': ['AdaptiveStochasticGradientDescent'],
    'Registration': ['MultiMetricMultiResolutionRegistration'],
    'ResampleInterpolator': ['FinalBSplineInterpolator'],
    'Resampler': ['DefaultResampler'],
    'ResultImageFormat': ['nii'],
    "RequiredRatioOfValidSamples": ['0.05'],
    'Transform': ['BSplineTransform'],
    'WriteIterationInfo': ['false'],
    'WriteResultImage': ['true']
  }

  return [rigid, affine, bspline]




if __name__ == '__main__':
  start = time.time()
  main()
  end = time.time()
  print("TIME:" + str(end-start))
