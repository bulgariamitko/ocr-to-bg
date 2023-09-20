import os
import json
import requests
import pandas as pd
from urllib.parse import urlparse
from os.path import join, basename, splitext
from pdf2image import convert_from_path
from PIL import Image, ImageDraw
import pytesseract
import argparse

def download_pdf(url, output_path):
    response = requests.get(url)
    with open(output_path, 'wb') as pdf_file:
        pdf_file.write(response.content)

def process_pdf_to_images(pdf_path, output_dir):
    images = convert_from_path(pdf_path, dpi=300)
    for i, image in enumerate(images):
        image.save(os.path.join(output_dir, f'page_{i+1}.jpg'), 'JPEG')

def perform_ocr(image_path, output_path):
    # Load the input image
    image = Image.open(image_path)

    # Perform OCR to recognize text
    text = pytesseract.image_to_string(image, lang='bul')

    # Get bounding box information for paragraphs
    data = pytesseract.image_to_data(image, lang='bul', output_type='data.frame')
    data = pd.DataFrame(data)

    # Filter the data to include only paragraph info
    paragraphs = data[data['block_num'] != 0]

    # Create a drawing context
    draw = ImageDraw.Draw(image)

    # Initialize a counter for the execution order
    execution_order = 1

    # Iterate over each paragraph bounding box and draw it on the image
    for i, row in paragraphs.iterrows():
        left, top, width, height = row['left'], row['top'], row['width'], row['height']

        # Draw a bounding box around the paragraph
        draw.rectangle([left, top, left + width, top + height], outline="red", width=2)

        # Place a number indicating execution order on top of the box
        draw.text((left, top), str(execution_order), fill="red")

        # Increment the execution order for the next paragraph
        execution_order += 1

    # Save the image with bounding boxes and numbers for paragraphs
    image.save(output_path)
    print(f"Processed image saved as {output_path}")

    return text

def main(json_file, delete_files):
    with open(json_file, 'r') as file:
        data = json.load(file)

    text_dir = os.path.join(os.path.dirname(json_file), 'text')
    os.makedirs(text_dir, exist_ok=True)

    for link in data['files']:
        # Extract the file name from the URL
        file_name = basename(urlparse(link).path)

        # Check if the file has already been processed
        if os.path.exists(os.path.join(text_dir, f'{file_name}.txt')):
            print(f'File {file_name} has already been processed. Skipping.')
            continue

        print(f'Downloading {file_name}...')
        pdf_path = os.path.join(text_dir, file_name)
        download_pdf(link, pdf_path)

        print(f'Converting {file_name} to images...')
        process_pdf_to_images(pdf_path, text_dir)

        combined_text = ''

        for image_file in os.listdir(text_dir):
            if image_file.endswith('.jpg'):
                image_path = os.path.join(text_dir, image_file)
                output_image_path = os.path.splitext(image_path)[0] + "_processed.jpg"
                print(f'Performing OCR on {image_file}...')
                ocr_text = perform_ocr(image_path, output_image_path)

                # Append the text from Tesseract to the combined text
                combined_text += ocr_text + '\n'

        text_file_name = f'{file_name}.txt'
        text_file_path = os.path.join(text_dir, text_file_name)

        # Write the combined text to the text file
        with open(text_file_path, 'w', encoding='utf-8') as text_file:
            text_file.write(combined_text)

        if delete_files:
            # Remove the downloaded PDF file to save space
            os.remove(pdf_path)

            # Optionally, you can remove the generated images as well
            for image_file in os.listdir(text_dir):
                if image_file.endswith('.jpg'):
                    os.remove(os.path.join(text_dir, image_file))

            # Remove the text file
            os.remove(text_file_path)

    print('All files processed.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download, OCR, and process PDF files.")
    parser.add_argument("json_file", help="Path to the JSON file containing PDF links")
    parser.add_argument("--delete", action="store_true", help="Delete downloaded PDF and images after processing")
    args = parser.parse_args()

    main(args.json_file, args.delete)