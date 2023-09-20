import sys
import argparse
import os
from PIL import Image, ImageDraw
import pytesseract
import pandas as pd

def perform_ocr(input_image_path, output_image_path, delete_files):
    # Load the input image
    image = Image.open(input_image_path)

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
    image.save(output_image_path)
    print(f"Processed image saved as {output_image_path}")

    # Save the OCR text to a text file
    with open("text.txt", "w", encoding="utf-8") as text_file:
        text_file.write(text)

    # Delete output files if requested
    if delete_files:
        os.remove(input_image_path)
        os.remove(output_image_path)
        os.remove("text.txt")
        print("Input image, output image, and text file deleted.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Perform OCR and optionally delete files.")
    parser.add_argument("input_image", help="Path to the input image")
    parser.add_argument("output_image", help="Path to the output image")
    parser.add_argument("--delete", action="store_true", help="Delete input, output, and text files")
    args = parser.parse_args()

    perform_ocr(args.input_image, args.output_image, args.delete)
