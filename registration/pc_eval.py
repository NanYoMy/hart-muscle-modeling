import time

import SimpleITK as sitk

import amsaf
import numpy as np



def run_amsaf():
    verbose = True
    dirB = "/Users/chris/Desktop/HART/ultrasound_data/SubB/"
    dirC = "/Users/chris/Desktop/HART/ultrasound_data/SubC/"
    unsegmented_image = amsaf.read_image(dirC + "trial6_30_fs_volume.nii")
    ground_truth = None
    segmented_image = amsaf.read_image(dirB + "trial6_30_fs_volume.nii")
    segmentation = amsaf.read_image(dirB + "trial6_30_fs_seg.nii")

    tp = np.array([[1.0, 0, 0],
                    [0, 1.0, 0], 
                    [0, 0.0, 1.0],
                    [0.0, 0.0, 0.0]])
    
    #segmentation = amsaf.transform(segmentation, amsaf.init_affine_transform(segmentation, tp), verbose)
    #segmented_image = amsaf.transform(segmented_image, amsaf.init_affine_transform(segmented_image, tp), verbose)


    amsaf_results = amsaf.amsaf_eval(unsegmented_image, ground_truth, segmented_image, segmentation, get_param_maps(), verbose=verbose)
    amsaf.write_results(amsaf_results, 'test_regis')


def init_affine_transform(img, A, t):
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




def get_param_maps():
  rigid = {
    "AutomaticParameterEstimation": ['true'],
    "AutomaticTransformInitialization": ['true'],
    "BSplineInterpolationOrder": ['3.000000'],
    "CheckNumberOfSamples": ['true'],
    "DefaultPixelValue": ['0.000000'],
    "FinalBSplineInterpolationOrder": ['3.000000'],
    "FixedImagePyramid": ['FixedSmoothingImagePyramid'],#, 'FixedRecursiveImagePyramid'],
    "ImageSampler": ['RandomCoordinate'],
    "Interpolator": ['BSplineInterpolator'],
    "MaximumNumberOfIterations": ['1024.000000'],
    "MaximumNumberOfSamplingAttempts": ['8.000000'],
    "Metric": ['AdvancedMattesMutualInformation'],
    "MovingImagePyramid": ['MovingSmoothingImagePyramid'],#, 'MovingRecursiveImagePyramid'],
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
    #"Scales": ['Float'],
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
    "Interpolator": ['BSplineInterpolator'],#Linear Interpolator
    "MaximumNumberOfIterations": ['1024.000000'],#256
    "MaximumNumberOfSamplingAttempts": ['8.000000'],
    "Metric": ['AdvancedMattesMutualInformation'],
    "MovingImagePyramid": ['MovingSmoothingImagePyramid'],
    "NewSamplesEveryIteration": ['true'],
    "NumberOfHistogramBins": ['32.000000'],#nonexistant
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




def _get_default_affine():
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




if __name__ == '__main__':
  start = time.time()
  run_amsaf()
  end = time.time()
  print("TIME: " + str(end-start))
