from pathlib import Path

import numpy as np
import skimage as ski


class PlateSegmenter:
    """Class for segmenting colonies growing in a Petri dish imaged by the Phenotype-o-mat.

    This class builds off of the script:
    https://github.com/Arcadia-Science/2024-phenotypeomat/blob/main/data_analysis_scripts/colony_segment_figure_chr_fl_fig.py
    developed for the [phenotype-o-mat pub](https://doi.org/10.57844/arcadia-112f-5023).

    TODO: add support for AVI
        Just take first frame, but need AVI files to test on.
    TODO: accept plate radius in mm (or cm?).
        Would first need to somehow know magnification or pixelsize of image.
    TODO: add watershed segmentation if needed.
        Crude implementation in commit history: bb3861f

    Attributes:
        filename:
            Filepath to 8 bit grayscale phenotype-o-mat plate image. Accepted file types include
            anything accepted by `ski.io.imread`.
        plate_radius_px:
            Radius of plate in pixels. Default value of 525 was empirically determined from a
            handful of test images.
        plate_radius_padding_px:
            Pad
    """

    def __init__(
        self,
        filename: Path,
        plate_radius_px: int = 525,
        plate_radius_padding_px: int = 70,
        min_colony_size_px2: int = 64,
        sigma_low: float = 1.6,
        sigma_high: float = 32,
        otsu_fudge_factor: float = -0.05,
    ) -> None:
        self.filename = filename
        self.plate_radius_px = plate_radius_px
        self.plate_radius_padding_px = plate_radius_padding_px
        self.min_colony_size_px2 = min_colony_size_px2
        self.sigma_low = sigma_low
        self.sigma_high = sigma_high
        self.otsu_fudge_factor = otsu_fudge_factor

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
        threshold *= 1 + self.otsu_fudge_factor
        plate_image_segmented_rough = plate_image_dog_filtered < threshold

        # set pixel intensity outside the detected plate (+ optional padding) to 0
        radius_for_mask_px = detected_plate_radius_px - self.plate_radius_padding_px
        plate_image_segmented_masked = apply_circular_mask(
            image=plate_image_segmented_rough,
            center=detected_plate_center_coords,
            radius_px=radius_for_mask_px,
        )

        # remove small objects via a morphological opening
        footprint_size = round(np.sqrt(self.min_colony_size_px2))
        footprint = ski.morphology.disk(footprint_size)
        plate_image_segmented_opened = ski.morphology.opening(
            plate_image_segmented_masked, footprint=footprint
        )

        plate_image_segmentation = ski.measure.label(plate_image_segmented_opened)
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
