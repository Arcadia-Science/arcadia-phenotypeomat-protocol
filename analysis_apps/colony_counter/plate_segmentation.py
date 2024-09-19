from pathlib import Path

import numpy as np
import skimage as ski
from scipy.ndimage import distance_transform_edt


class PlateSegmenter:
    """Summary.

    More in depth explanation.

    TODO: add support for AVI
    TODO: accept plate radius in mm (or cm?).
        Would first need to somehow know magnification or pixelsize of image.

    Attributes:
        filename:
            Filepath to phenotype-o-mat plate image. Accepted file types include anything
        plate_radius_px:
            Radius of plate in pixels. Default value of 525 was empirically determined from a
            handful of test images.
        plate_radius_padding_px:
            Pad
    """

    def __init__(
        self,
        filename: Path,
        apply_watershed: bool = True,
        plate_radius_px: int = 525,
        plate_radius_padding_px: int = 70,
        footprint_size: int = 10,
        min_colony_size_px2: int = 64,
        max_colony_size_px2: int = 1000,
        min_colony_eccentricity: float = 0.7,
        sigma_low: float = 1.6,
        sigma_high: float = 32,
    ) -> None:
        self.filename = filename
        self.apply_watershed = apply_watershed
        self.plate_radius_px = plate_radius_px
        self.plate_radius_padding_px = plate_radius_padding_px
        self.footprint_size = footprint_size
        self.min_colony_size_px2 = min_colony_size_px2
        self.max_colony_size_px2 = max_colony_size_px2
        self.min_colony_eccentricity = min_colony_eccentricity
        self.sigma_low = sigma_low
        self.sigma_high = sigma_high

    def load_image(self) -> np.ndarray:
        image = ski.io.imread(self.filename)
        # convert RGB image to grayscale
        if image.ndim > 2:
            return ski.color.rgb2gray(image)
        else:
            return image

    def segment(self) -> np.ndarray:
        """"""
        raw_8bit_grayscale_plate_image = self.load_image()

        # detect plate
        detected_plate_center_coords, detected_plate_radius_px = detect_circle(
            raw_8bit_grayscale_plate_image, self.plate_radius_px
        )

        # apply difference of Gaussians filter to remove background artifacts
        # prior to thresholding
        plate_image_dog_filtered = ski.filters.difference_of_gaussians(
            raw_8bit_grayscale_plate_image, self.sigma_low, self.sigma_high
        )
        threshold = ski.filters.threshold_otsu(plate_image_dog_filtered)
        plate_image_segmented_rough = plate_image_dog_filtered < threshold

        # set pixel intensity outside the detected plate (+ optional padding) to 0
        radius_for_mask_px = detected_plate_radius_px - self.plate_radius_padding_px
        plate_image_segmented_masked = apply_circular_mask(
            image=plate_image_segmented_rough,
            center=detected_plate_center_coords,
            radius_px=radius_for_mask_px,
        )

        # # optionally apply watershedding to separate overlapping colonies
        # if self.apply_watershed:
        #     plate_image_watershed_segmentation, peaks = watershed_segmentation(
        #         plate_image_segmented_masked, footprint_size=self.footprint_size
        #     )
        #     return plate_image_watershed_segmentation, peaks
        # else:
        #     plate_image_segmentation = ski.measure.label(plate_image_segmented_masked)
        #     return plate_image_segmentation

        plate_image_segmentation = ski.measure.label(plate_image_segmented_masked)
        return plate_image_segmentation


def detect_circle(image: np.ndarray, radius_px: int) -> tuple[tuple[int, int], int]:
    """"""
    # edge detection
    edges = ski.filters.sobel(image)
    threshold = ski.filters.threshold_otsu(edges)
    edges_binary = edges > threshold

    # detect (circular) plate with (circular) Hough transform
    hough_radii = [radius_px]
    hough_spaces = ski.transform.hough_circle(edges_binary, hough_radii)
    hough_peaks = ski.transform.hough_circle_peaks(
        hspaces=hough_spaces,
        radii=hough_radii,
        total_num_peaks=1,
    )
    center = hough_peaks[1][0], hough_peaks[2][0]
    radius = hough_peaks[3][0]

    return center, radius


def apply_circular_mask(
    image: np.ndarray,
    center: tuple[int, int],
    radius_px: int,
):
    """"""
    Y, X = np.ogrid[: image.shape[0], : image.shape[1]]
    distance_from_center = np.sqrt((X - center[0]) ** 2 + (Y - center[1]) ** 2)
    circular_mask = distance_from_center <= radius_px
    image_masked = np.zeros_like(image)
    image_masked[circular_mask] = image[circular_mask]
    return image_masked


# def watershed_segmentation(binary_image, footprint_size=3):
#     """"""
#     distance_transform_image = distance_transform_edt(binary_image)
#     footprint = np.ones((footprint_size, footprint_size))
#     peaks = ski.feature.peak_local_max(
#         distance_transform_image,
#         footprint=footprint,
#         labels=binary_image,
#     )
#     mask = np.zeros_like(distance_transform_image, dtype=bool)
#     # seed the watershed with peak coordinates
#     mask[tuple(peaks.T)] = True
#     markers = ski.measure.label(mask)
#     watershed_segmentation_image = ski.segmentation.watershed(
#         image=-distance_transform_image, markers=markers, mask=binary_image
#     )
#     return watershed_segmentation_image, peaks


# def 
