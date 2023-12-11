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

    # Sort by 'top' and 'left'
    paragraphs = paragraphs.sort_values(['top', 'left']).copy()

    # Add a new column to identify close blocks
    paragraphs['close_block'] = (paragraphs['top'] - paragraphs['top'].shift(1)).fillna(0).gt(50).cumsum()

    # Calculate global mean of 'left' to set as a threshold
    global_left_mean = paragraphs['left'].mean()

    # Create a new column to identify whether the paragraph is left or right
    paragraphs['is_right'] = paragraphs['left'] > global_left_mean

    # Now group by 'close_block' and 'is_right'
    grouped = paragraphs.groupby(['close_block', 'is_right']).agg(
        left=pd.NamedAgg(column='left', aggfunc='min'),
        top=pd.NamedAgg(column='top', aggfunc='min'),
        right=pd.NamedAgg(column='left', aggfunc='max'),
        bottom=pd.NamedAgg(column='top', aggfunc='max'),
        first_word=pd.NamedAgg(column='text', aggfunc=lambda x: x.iloc[0].split()[0] if x.iloc[0].split() else "N/A"),
        conf=pd.NamedAgg(column='conf', aggfunc='mean')
    ).reset_index()

    draw = ImageDraw.Draw(image)

    execution_order = 1

    for i, row in grouped.iterrows():
        left, top, right, bottom = row['left'], row['top'], row['right'], row['bottom']
        draw.rectangle([left, top, right, bottom], outline="red", width=2)
        draw.text((left, top), str(execution_order), fill="red", font=font)
        print(f"Block: {row['close_block']}, Confidence: {row['conf']}, First Word: {row['first_word']}")
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
