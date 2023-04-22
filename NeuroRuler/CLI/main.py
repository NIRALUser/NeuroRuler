"""
Defines main(), the entrypoint of the CLI (if you want to call it that).
"""
from NeuroRuler.utils.constants import ThresholdFilter
import NeuroRuler.utils.imgproc as imgproc
import NeuroRuler.utils.cli_settings as cli_settings
import SimpleITK as sitk
from pathlib import Path


def main() -> None:
    """Main entrypoint of CLI."""
    print(cli_settings.FILE)
    file_path = Path(cli_settings.FILE)
    reader = sitk.ImageFileReader()
    reader.SetFileName(str(file_path))
    new_img: sitk.Image = reader.Execute()
    new_img: sitk.Image = sitk.DICOMOrientImageFilter().Execute(new_img)
    #new_img = sitk.DICOMOrientImageFilter().Execute(new_img)

    euler = sitk.Euler3DTransform()
    euler.SetRotation(0, 0, 0)
    rotated_image: sitk.Image = sitk.Resample(new_img, euler)
    rotated_slice = rotated_image[:, :, 79] # last is the slice

    binary_contour_slice: np.ndarray = imgproc.contour(
        rotated_slice, ThresholdFilter.Binary
    )

    circumference: float = imgproc.length_of_contour(binary_contour_slice)
    print(circumference)


if __name__ == "__main__":
    import NeuroRuler.utils.parser as parser

    parser.parse_cli_config()
    parser.parse_cli()
    main()
