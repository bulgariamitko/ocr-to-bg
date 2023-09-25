import sys
import argparse
import os
from PIL import Image, ImageDraw, ImageFont
import pytesseract
import pandas as pd

def perform_ocr(input_image_path, output_image_path, delete_files):
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    image = Image.open(input_image_path)
    text = pytesseract.image_to_string(image, lang='bul')
    data = pytesseract.image_to_data(image, lang='bul', output_type='data.frame')
    data = pd.DataFrame(data)
    paragraphs = data[(data['block_num'] != 0) & (data['conf'] != -1)]

    # New sorting logic
    paragraphs = paragraphs.sort_values(by=['top', 'left'])
    tolerance = 50
    sorted_blocks = []
    current_top = 0

    for _, row in paragraphs.iterrows():
        if abs(current_top - row['top']) > tolerance:
            sorted_blocks.append(row)
            current_top = row['top']
        else:
            sorted_blocks.insert(-1, row)

    draw = ImageDraw.Draw(image)
    execution_order = 1

    for row in sorted_blocks:
        left, top, width, height = row['left'], row['top'], row['width'], row['height']
        first_word = row['text'].split()[0] if pd.notna(row['text']) and row['text'].split() else "N/A"

        draw.rectangle([left, top, left + width, top + height], outline="red", width=2)
        draw.text((left, top), str(execution_order), fill="red", font=font)

        print(f"Block: {row['block_num']}, Confidence: {row['conf']}, First Word: {first_word}")

        execution_order += 1

    image.save(output_image_path)
    print(f"Processed image saved as {output_image_path}")

    with open("text.txt", "w", encoding="utf-8") as text_file:
        text_file.write(text)

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
