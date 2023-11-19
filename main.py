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
   
    # You will need to set this threshold based on your earlier analysis
    white_gray_threshold = 65  # This is just a placeholder value
    if average_intensity > white_gray_threshold:
        return 'white'
    else:
        return 'gray'

# Function to preprocess the text region based on its color
def preprocess_region(region, region_color, gray_image):
    x, y, w, h = region
    border_size = 2  # This will add 5 pixels on each side

    # Make sure that we don't go out of the image boundaries
    x_start = max(x - border_size, 0)
    y_start = max(y - border_size, 0)
    x_end = min(x + w + border_size, gray_image.shape[1])
    y_end = min(y + h + border_size, gray_image.shape[0])

    # Extract the region of interest with the additional border
    expanded_region_of_interest = gray_image[y_start:y_end, x_start:x_end]
    
    # Apply different preprocessing depending on the color of the region
    if region_color == 'white':
        # Invert colors if the text is white (light on dark)
        region_of_interest = cv2.bitwise_not(expanded_region_of_interest)
        
        # plt.imshow(cv2.cvtColor(region_of_interest, cv2.COLOR_BGR2RGB))
        # plt.show()
        return region_of_interest
    else:
        # Threshold the image to create a mask for the gray text
        # Adjust the threshold value as needed to isolate the gray text
        _, mask = cv2.threshold(expanded_region_of_interest, 60, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Show the mask
        # plt.imshow(mask, cmap='gray')
        # plt.show()

        # Use the mask to create a black background
        background = np.zeros_like(expanded_region_of_interest)
        
        # Place the gray text on the black background
        region_of_interest = cv2.bitwise_and(expanded_region_of_interest, expanded_region_of_interest, mask=mask)

        # Show the region of interest
        # plt.imshow(cv2.cvtColor(region_of_interest, cv2.COLOR_BGR2RGB))
        # plt.show()
        
        # Now, let's increase the contrast to make the gray text white
        # You can adjust the contrast level as needed
        contrast_level = 5 # This value is just an example, adjust as needed
        region_of_interest = cv2.addWeighted(region_of_interest, contrast_level, background, 0, 0)

        # plt.imshow(cv2.cvtColor(region_of_interest, cv2.COLOR_BGR2RGB))
        # plt.show()
        return region_of_interest

# Function to segment text regions
def segment_text_regions_with_dilation(binary_image, kernel_size=(10,10)):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
    dilated_image = cv2.dilate(binary_image, kernel, iterations=1)
    
    contours, _ = cv2.findContours(dilated_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    text_regions = [cv2.boundingRect(cnt) for cnt in contours]

    return text_regions

def sort_text_regions(text_regions):
    # First, sort by the y-coordinate to ensure we process top-to-bottom
    text_regions.sort(key=lambda x: x[1])
    
    # Next, we'll cluster the y-coordinates to find lines of text
    line_clusters = {}
    line_height_threshold = 10  # This threshold can be adjusted

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

    # Now we have clusters of lines, we'll sort each cluster by x-coordinate
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

    # Threshold the image to create a binary image
    # Assuming you have a function to find a suitable threshold value
    threshold_value = 90  # This should be determined by your determine_threshold_value function
    _, binary_image = cv2.threshold(gray_image, threshold_value, 255, cv2.THRESH_BINARY)

    # Segment text regions
    text_regions = segment_text_regions_with_dilation(binary_image)

    # show the image with the text regions outlined
    image_copy = image.copy()
    for region in text_regions:
        x, y, w, h = region
        cv2.rectangle(image_copy, (x, y), (x+w, y+h), (0, 255, 0), 2)

    plt.imshow(cv2.cvtColor(image_copy, cv2.COLOR_BGR2RGB))
    plt.show()
    cv2.imwrite('./outline.png', image_copy)

    sorted_regions = sort_text_regions(text_regions)

    text_results: list[tuple[str, str]] = []

    for region in sorted_regions:
        region_color = determine_region_color(region, gray_image)

        # crop that region from the grayscale image and show it
        x, y, w, h = region
        border_size = 2  # This will add 5 pixels on each side

        # Make sure that we don't go out of the image boundaries
        x_start = max(x - border_size, 0)
        y_start = max(y - border_size, 0)
        x_end = min(x + w + border_size, gray_image.shape[1])
        y_end = min(y + h + border_size, gray_image.shape[0])

        # Extract the region of interest with the additional border
        expanded_region_of_interest = gray_image[y_start:y_end, x_start:x_end]
        # plt.imshow(cv2.cvtColor(expanded_region_of_interest, cv2.COLOR_BGR2RGB))
        # plt.show()

        preprocessed_region = preprocess_region(region, region_color, gray_image)
        
        # Extract the region for OCR
        x, y, w, h = region
        roi = preprocessed_region

        
        # Perform OCR on the preprocessed region of interest
        text: str = pytesseract.image_to_string(roi, config='--psm 7', lang='spa')
        text = str(text).replace('\n', '')
        console.print(text)
        text_results.append((text, region_color))


    console.print(text_results, style='bold green')

    return text_results

class ColorCheckTestCase(unittest.TestCase):
    def test_word_colors(self):
        expected_results: list[tuple[str, str]] = [
            ('el', 'white'),
            (':04', 'white'),
            ('fuego', 'white'),
            ('de', 'white'),
            ('en', 'white'),
            ('varios', 'white'),
            ('uno', 'white'),
            ('a', 'white'),
            ('agua', 'white'),
            ('casa', 'white'),
            ('animal', 'white'),
            ('lado', 'white'),
            ('forma', 'white'),
            ('derecho', 'white'),
            ('luz', 'white'),
            ('en', 'white'),
            ('por', 'white'),
            ('trabajo', 'white'),
            ('era', 'white'),
            ('medio', 'white'),
            ('fin', 'white'),
            ('uso', 'white'),
            ('número', 'white'),
            ('gran', 'white'),
            ('hace', 'white'),
            ('poco', 'white'),
            ('nos', 'white'),
            ('caja', 'white'),
            ('forma', 'white'),
            ('para', 'white'),
            ('luz', 'white'),
            ('venir', 'gray'),
            ('bajo', 'gray'),
            ('lata', 'gray'),
            ('cualquier', 'gray'),
            ('nuevo', 'gray'),
            ('lo', 'gray'),
            ('noche', 'gray'),
            ('me', 'gray'),
            ('acto', 'gray'),
            ('no', 'gray'),
            ('cuando', 'gray'),
            ('día', 'gray'),
            ('trabajo', 'gray'),
            ('tener', 'gray'),
            ('tiene', 'gray'),
            ('forma', 'gray'),
            ('estado', 'gray'),
            ('por', 'gray'),
        ]

        actual_results = get_image_text_and_colors()

        # self.assertEqual(expected_results, actual_results)
        # convert this into a loop with logs
        for i, expected_result in enumerate(expected_results):
            actual_result_text, actual_result_color = actual_results[i]
            expected_result_text, expected_result_color = expected_result

            console.print(f'Expected: {expected_result_text} ({expected_result_color})')
            self.assertEqual(expected_result_text, actual_result_text)

            console.print(f'Actual: {actual_result_text} ({actual_result_color})')
            self.assertEqual(expected_result_color, actual_result_color)

if __name__ == '__main__':
    unittest.main()