# pip3 install opencv-python
# pip3 install numpy

import cv2
import numpy as np
import os

def extract_images_from_scanned_document(file_path):
    # Load the image
    image = cv2.imread(file_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Adaptive thresholding to get binary image
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # Dilate to connect components
    kernel = np.ones((5,5),np.uint8)
    dilate = cv2.dilate(thresh, kernel, iterations = 2)

    # Finding contours
    contours, _ = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    extracted_images = []
    for i, contour in enumerate(contours):
        # Get bounding box for each contour
        x, y, w, h = cv2.boundingRect(contour)

        # Filtering out the small and very large contours that are likely not images
        if w > 100 and h > 100 and w < 0.9 * image.shape[1] and h < 0.9 * image.shape[0]:
            extracted_img = image[y:y+h, x:x+w]
            extracted_images.append(extracted_img)
            # cv2.imwrite(f'extracted_image_{i+1}.jpg', extracted_img)

    return extracted_images

def main():
    # Create 'extracted' directory if it doesn't exist
    if not os.path.exists('extracted'):
        os.makedirs('extracted')

    # Find all .jpg files in the current directory
    for file_name in os.listdir('.'):
        if file_name.lower().endswith('.jpg'):
            print(f'Processing {file_name}')
            extracted_images = extract_images_from_scanned_document(file_name)

            # Save each extracted image to the 'extracted' directory
            for idx, img in enumerate(extracted_images):
                output_path = os.path.join('extracted', f'extracted_{idx}_{file_name}')
                cv2.imwrite(output_path, img)
                print(f'Saved {output_path}')

if __name__ == "__main__":
    main()