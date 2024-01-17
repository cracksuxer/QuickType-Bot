import os
from typing import Literal
import threading as th

import cv2 as cv
from matplotlib import pyplot as plt
import numpy as np
import pytesseract

from quicktype.data_manager import DataManager


class OcrManager:
    """Manages the OCR process."""

    _instance = None
    _dataManager = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(OcrManager, cls).__new__(cls)
            app_directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

            # Construye la ruta al directorio 'tesseract' dentro del directorio 'app'
            tesseract_directory = os.path.join(app_directory, "tesseract")

            # Construye la ruta al ejecutable de TesseractOCR
            tesseract_path = os.path.join(
                tesseract_directory,
                r"tesseractWindows\tesseract.exe" if os.name == "nt" else "tesseract",
            )

            # Establece la ruta al ejecutable de TesseractOCR para pytesseract
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

            tessdata_directory = os.path.join(
                tesseract_directory,
                r"tesseractWindows\tessdata" if os.name == "nt" else "tessdata",
            )

            cls._tess_configs = r'--psm 7 --tessdata-dir "' + tessdata_directory + r'"'

        return cls._instance

    def _determine_region_color(self, region, gray_image) -> str:
        """Determines the text color of a region."""
        x, y, w, h = region
        region_of_interest = gray_image[y : y + h, x : x + w]
        average_intensity = np.mean(region_of_interest)

        white_gray_threshold = 65
        if average_intensity > white_gray_threshold:
            return "white"

        return "gray"

    def _preprocess_region(self, region, region_color, gray_image):
        """Preprocesses a text region based on its color."""
        border_size = 2
        x_start = max(region[0] - border_size, 0)
        y_start = max(region[1] - border_size, 0)
        x_end = min(region[0] + region[2] + border_size, gray_image.shape[1])
        y_end = min(region[1] + region[3] + border_size, gray_image.shape[0])

        expanded_region_of_interest = gray_image[y_start:y_end, x_start:x_end]

        if region_color == "white":
            return cv.bitwise_not(expanded_region_of_interest)

        _, mask = cv.threshold(
            expanded_region_of_interest, 60, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU
        )
        background = np.zeros_like(expanded_region_of_interest)
        region_of_interest = cv.bitwise_and(
            expanded_region_of_interest, expanded_region_of_interest, mask=mask
        )

        contrast_level = 5
        region_of_interest = cv.addWeighted(
            region_of_interest, contrast_level, background, 0, 0
        )

        return cv.addWeighted(region_of_interest, contrast_level, background, 0, 0)

    def _segment_text_regions_with_dilation(self, binary_image, kernel_size=(10, 10)):
        """Segments text regions with morphological dilation."""
        kernel = cv.getStructuringElement(cv.MORPH_RECT, kernel_size)
        dilated_image = cv.dilate(binary_image, kernel, iterations=1)

        contours, _ = cv.findContours(
            dilated_image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE
        )
        text_regions = [cv.boundingRect(cnt) for cnt in contours]

        return text_regions

    def _sort_text_regions(self, text_regions):
        """Sorts text regions from top to bottom, left to right."""
        text_regions.sort(key=lambda x: x[1])

        line_clusters = {}
        line_height_threshold = 10

        for region in text_regions:
            _, y, _, h = region
            found_cluster = False

            for line_y, cluster in line_clusters.items():
                if (
                    abs(line_y - y) < line_height_threshold
                    or abs((line_y + cluster[0][3]) - (y + h)) < line_height_threshold
                ):
                    cluster.append(region)
                    found_cluster = True
                    break

            if not found_cluster:
                line_clusters[y] = [region]

        sorted_regions = []
        for line_y in sorted(line_clusters.keys()):
            line_clusters[line_y].sort(key=lambda x: x[0])
            sorted_regions.extend(line_clusters[line_y])

        return sorted_regions

    def link_data_manager(self, dataManager: DataManager) -> None:
        """Links the data manager to the OCR manager."""
        OcrManager._dataManager = dataManager

    def get_image_text(
        self,
        image_path: str,
        lang: Literal["spa", "eng"],
        typer_finished_event: th.Event,
    ) -> None:
        """Gets the text from an image."""
        image = cv.imread(image_path)
        gray_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

        threshold_value = 90
        _, binary_image = cv.threshold(
            gray_image, threshold_value, 255, cv.THRESH_BINARY
        )

        text_regions = self._segment_text_regions_with_dilation(binary_image)
        sorted_regions = self._sort_text_regions(text_regions)
        for region in sorted_regions:
            if typer_finished_event.is_set():
                raise Exception("typer finished")

            region_color = self._determine_region_color(region, gray_image)

            if region_color == "white":
                continue

            preprocessed_region = self._preprocess_region(
                region, region_color, gray_image
            )

            text = pytesseract.image_to_string(
                preprocessed_region, lang=lang, config=self._tess_configs
            ).replace("\n", "")

            if OcrManager._dataManager:
                OcrManager._dataManager.send(text)
