import sys
from PIL import Image, ImageDraw
import pytesseract

def perform_ocr(input_image_path, output_image_path):
    # Load the input image
    image = Image.open(input_image_path)

    # Perform OCR to recognize text
    text = pytesseract.image_to_string(image, lang='bul')

    # Get bounding box information
    boxes = pytesseract.image_to_boxes(image, lang='bul')

    # Create a drawing context
    draw = ImageDraw.Draw(image)

    # Iterate over each bounding box and draw it on the image
    for box in boxes.splitlines():
        box = box.split()
        left, top, right, bottom = int(box[1]), int(box[2]), int(box[3]), int(box[4])
        draw.rectangle([left, top, right, bottom], outline="red", width=2)

    # Save the image with bounding boxes to the specified output path
    image.save(output_image_path)
    print(f"Processed image saved as {output_image_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python ocr_with_bounding_boxes.py input_image output_image")
        sys.exit(1)

    input_image_path = sys.argv[1]
    output_image_path = sys.argv[2]

    perform_ocr(input_image_path, output_image_path)
