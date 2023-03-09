"""Entrypoint of program."""

import argparse
import SimpleITK as sitk
import numpy as np
from PIL import Image
import cv2
import matplotlib.pyplot as plt


OUTPUT_DIR = 'out'
NRRD1_PATH = 'ExampleData/BCP_Dataset_2month_T1w.nrrd'
NRRD2_PATH = 'ExampleData/IBIS_Dataset_12month_T1w.nrrd'
NRRD3_PATH = 'ExampleData/IBIS_Dataset_NotAligned_6month_T1w.nrrd'
NIFTI_PATH = 'ExampleData/MicroBiome_1month_T1w.nii.gz'

NUM_TO_PATH = {
    0:'ExampleData/BCP_Dataset_2month_T1w.nrrd',
    1:'ExampleData/IBIS_Dataset_12month_T1w.nrrd',
    2:'ExampleData/IBIS_Dataset_NotAligned_6month_T1w.nrrd',
    3:'ExampleData/MicroBiome_1month_T1w.nii.gz'
}
"""Map number to path, don't have to type full path to image as CLI arg."""


def main() -> None:
    args = parse_cli()
    reader = sitk.ImageFileReader()
    reader.SetFileName(NUM_TO_PATH[int(args.img)])
    image = reader.Execute()
    rotate_and_export_slice(image, int(args.theta_x), int(args.theta_y), int(args.theta_z), int(args.slice_num))


def rotate_and_export_slice(
    sitk_3Dimg,
    theta_x: float,
    theta_y: float,
    theta_z: float,
    slice_num: int,
    **kwargs) -> None:
    """Rotate 3D image, export 2D slice.
    
    Parameters
    ----------
    sitk_3Dimg
        Result of sitk.ImageFileReader().Execute()
    theta_x, theta_y, theta_z
        Give angles in degrees
    slice_num
        Number of the slice
    filename
        Give extension also
    **kwargs
        'axis'
            'x', 'y', or 'z', defaults to 'z'
    """
    if 'axis' in kwargs and kwargs['axis'].lower() not in {'x', 'y', 'z'}:
        raise Exception(f"Invalid axis {kwargs['axis']} specified. Use 'x', 'y', 'z'.")
    # Create new Euler3DTransform for sitk_img because if there are multiple images, they need multiple Euler3DTransforms
    # Center of rotation is center of the 3D image
    euler_3d_transform = sitk.Euler3DTransform(sitk_3Dimg.TransformContinuousIndexToPhysicalPoint([(sz-1 / 2.0) for sz in sitk_3Dimg.GetSize()]))
    euler_3d_transform.SetRotation(theta_x * np.pi / 180, theta_y * np.pi / 180, theta_z * np.pi / 180)
    rotated_img = sitk.Resample(sitk_3Dimg, euler_3d_transform)
        
    axis = kwargs['axis'] if 'axis' in kwargs else 'z'
    slice = rotated_img[:, :, slice_num] if axis == 'z' else rotated_img[:, slice_num, :] if axis == 'y' else rotated_img[slice_num, :, :]
    temp = sitk.GetArrayFromImage(slice)
    temp = ((temp - temp.min()) / (temp.max() - temp.min()) * 240).astype(np.uint8)
    JPG = Image.fromarray(temp)
    JPG.save(OUTPUT_DIR + "/test.jpg")

def parse_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('img')
    parser.add_argument('theta_x')
    parser.add_argument('theta_y')
    parser.add_argument('theta_z')
    parser.add_argument('slice_num')
    parser.add_argument('-axis')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    main()