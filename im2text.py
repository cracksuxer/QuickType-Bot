import os
os.environ['QT_QPA_PLATFORM'] = 'wayland'

import cv2
import numpy as np
import pytesseract
import unittest

from rich.console import Console
from rich.traceback import install

import matplotlib.pyplot as plt

install()
console = Console()

# Function to determine the color of the text region
def determine_region_color(region, gray_image):
    x, y, w, h = region
    region_of_interest = gray_image[y:y+h, x:x+w]
    average_intensity = np.mean(region_of_interest)
   
    white_gray_threshold = 65
    if average_intensity > white_gray_threshold:
        return 'white'
    else:
        return 'gray'

# Function to preprocess the text region based on its color
def preprocess_region(region, region_color, gray_image):
    x, y, w, h = region
    border_size = 2

    x_start = max(x - border_size, 0)
    y_start = max(y - border_size, 0)
    x_end = min(x + w + border_size, gray_image.shape[1])
    y_end = min(y + h + border_size, gray_image.shape[0])

    expanded_region_of_interest = gray_image[y_start:y_end, x_start:x_end]
    
    if region_color == 'white':
        return cv2.bitwise_not(expanded_region_of_interest)
    else:
        _, mask = cv2.threshold(expanded_region_of_interest, 60, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        background = np.zeros_like(expanded_region_of_interest)
        region_of_interest = cv2.bitwise_and(expanded_region_of_interest, expanded_region_of_interest, mask=mask)

        contrast_level = 5
        region_of_interest = cv2.addWeighted(region_of_interest, contrast_level, background, 0, 0)

        return cv2.addWeighted(region_of_interest, contrast_level, background, 0, 0)

# Function to segment text regions
def segment_text_regions_with_dilation(binary_image, kernel_size=(10,10)):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
    dilated_image = cv2.dilate(binary_image, kernel, iterations=1)

    contours, _ = cv2.findContours(dilated_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    text_regions = [cv2.boundingRect(cnt) for cnt in contours]

    return text_regions

def sort_text_regions(text_regions):
    text_regions.sort(key=lambda x: x[1])
    
    line_clusters = {}
    line_height_threshold = 10

    for region in text_regions:
        _, y, _, h = region
        found_cluster = False
        
        for line_y in line_clusters:
            if abs(line_y - y) < line_height_threshold or abs((line_y + line_clusters[line_y][0][3]) - (y + h)) < line_height_threshold:
                line_clusters[line_y].append(region)
                found_cluster = True
                break

        if not found_cluster:
            line_clusters[y] = [region]

    sorted_regions = []
    for line_y in sorted(line_clusters.keys()):
        line_clusters[line_y].sort(key=lambda x: x[0])
        sorted_regions.extend(line_clusters[line_y])

    return sorted_regions

def get_image_text_and_colors(image_path: str = './test2.png') -> list[tuple[str, str]]:
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    plt.imshow(cv2.cvtColor(gray_image, cv2.COLOR_BGR2RGB))
    plt.show()

    threshold_value = 90
    _, binary_image = cv2.threshold(gray_image, threshold_value, 255, cv2.THRESH_BINARY)

    text_regions = segment_text_regions_with_dilation(binary_image)

    image_copy = image.copy()
    for region in text_regions:
        x, y, w, h = region
        cv2.rectangle(image_copy, (x, y), (x+w, y+h), (0, 255, 0), 2)

    sorted_regions = sort_text_regions(text_regions)

    text_results: list[tuple[str, str]] = []

    for region in sorted_regions:
        region_color = determine_region_color(region, gray_image)
        preprocessed_region = preprocess_region(region, region_color, gray_image)

        text = str(pytesseract.image_to_string(preprocessed_region, config='--psm 7', lang='spa')).replace('\n', '')
        text_results.append((text, region_color))

    console.print(text_results, style='bold green')

    return text_results