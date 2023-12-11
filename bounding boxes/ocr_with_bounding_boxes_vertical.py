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

    # Calculate global_left_mean
    global_left_mean = paragraphs['left'].mean()

    # Calculate 'is_right'
    paragraphs['is_right'] = paragraphs['left'] > global_left_mean

    # Identify close blocks
    paragraphs['close_block'] = (paragraphs['top'] - paragraphs['top'].shift(1)).fillna(0).gt(50).cumsum()

    # Count the lines in each close_block
    line_count_per_block = paragraphs.groupby('close_block').size()

    # Update 'close_block' for one-line blocks
    max_close_block = paragraphs['close_block'].max()
    for block, size in line_count_per_block.items():
        if size == 1:
            max_close_block += 1
            paragraphs.loc[paragraphs['close_block'] == block, 'close_block'] = max_close_block

    # # Update the 'is_right' column
    # paragraphs['is_right'] = paragraphs.apply(set_is_right, axis=1)

    # Group paragraphs by 'close_block' and 'is_right'
    grouped = paragraphs.groupby(['close_block', 'is_right']).agg(
        left=pd.NamedAgg(column='left', aggfunc='min'),
        top=pd.NamedAgg(column='top', aggfunc='min'),
        right=pd.NamedAgg(column='left', aggfunc='max'),
        bottom=pd.NamedAgg(column='top', aggfunc='max'),
        first_word=pd.NamedAgg(column='text', aggfunc=lambda x: x.iloc[0].split()[0] if x.iloc[0].split() else "N/A"),
        conf=pd.NamedAgg(column='conf', aggfunc='mean')
    ).reset_index()

    merged_grouped = []

    for i, row in grouped.iterrows():
        merged_grouped.append(row.to_dict())

    merged_grouped_df = pd.DataFrame(merged_grouped)

    draw = ImageDraw.Draw(image)

    execution_order = 1

    # Create a list to hold OCR'ed texts
    ordered_text_list = [None] * len(merged_grouped_df)

    # Existing loop where you draw rectangles and write execution order
    for i, row in merged_grouped_df.iterrows():
        left, top, right, bottom = row['left'], row['top'], row['right'], row['bottom']

        print(f"Image dimensions: {image.width}x{image.height}")
        print(f"Attempting to crop: left={left}, top={top}, right={right}, bottom={bottom}")

        # Make sure coordinates are within image boundaries
        if left >= 0 and top >= 0 and right <= image.width and bottom <= image.height:
            cropped_image = image.crop((left, top, right, bottom))
        else:
            print(f"Skipping invalid coordinates: {left}, {top}, {right}, {bottom}")
            continue

        # Extract text from the rectangle
        rect_text = pytesseract.image_to_string(cropped_image, lang='bul').strip()

        # Store the text at the correct index
        ordered_text_list[execution_order - 1] = rect_text

        # Draw bounding boxes on original image
        draw.rectangle([left, top, right, bottom], outline="red", width=2)
        draw.text((left, top), str(execution_order), fill="red", font=font)

        # Your other logic here
        # For example, writing OCR text to file
        with open('output.txt', 'a') as f:
            f.write(rect_text + '\n')

        execution_order += 1

    # Writing ordered text to a file
    with open("text.txt", "w", encoding="utf-8") as f:
        for text in ordered_text_list:
            f.write(f"{text}\n")

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
