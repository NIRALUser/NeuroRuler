from pathlib import Path
from sortedcontainers import SortedDict
import SimpleITK as sitk

example_data_path = Path("..") / "ExampleData"
reader: sitk.ImageFileReader = sitk.ImageFileReader()
images: SortedDict = SortedDict()
"""Map Path to sitk.Image"""

for img_path in example_data_path.glob("*.nrrd"):
    reader.SetFileName(str(img_path))
    images[img_path] = reader.Execute()

for img_path in images.keys():
    print(f"{img_path.name}")
    print(f"{images[img_path]}")


for img_path in images.keys():
    print(f"{img_path.name}")
    curr_img = images[img_path]
    dimensions = curr_img.GetSize()
    print(f"\tdimensions: {dimensions}")
    print(
        f"\tcenter of rotation: {curr_img.TransformContinuousIndexToPhysicalPoint([((dimension - 1) / 2.0) for dimension in dimensions])}"
    )
