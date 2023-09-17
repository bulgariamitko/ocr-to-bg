# OCR Image to Text Conversion

This guide provides instructions on how to perform Optical Character Recognition (OCR) to convert images to text using Tesseract-OCR or Google Vision AI.

## Tesseract-OCR Method

### Installation
1. Install Tesseract-OCR: `sudo apt install tesseract-ocr`
2. Download the Bulgarian language dictionary: [bul.traineddata](https://github.com/tesseract-ocr/tessdata/blob/main/bul.traineddata)
3. Move the downloaded dictionary to the Tesseract-OCR data directory: `mv bul.traineddata /usr/share/tesseract-ocr/4.00/tessdata/`
4. Install jq `sudo apt-get install jq`

### Instructions
1. Extract images from a PDF: `pdfimages -j file.pdf pages`
2. Execute the OCR script: `./ocr.sh [PATH]/`
3. Perform OCR on an image: `tesseract file001.jpg output-1 -l bul`
4. Create the OCR script: touch ocr.sh

### OCR Script (ocr.sh)
#!/bin/sh

echo -e "path: $1"

touch $1output 2>&1

for f in $1*.jpg; do
    echo -e "$f"
    tesseract "$f" $1output-1 -l bul 2>&1
    cat $1output-1.txt >> $1output 2>&1
done

5. Make the script executable: sudo chmod +x ocr.sh
6. Run it - ./ocr.sh your_json_file.json

### Convert PDF into Images
1. Install ImageMagic: sudo apt install imagemagick
2. Add this policy in  /etc/ImageMagick-6/policy.xml: <policy domain="coder" rights="read | write" pattern="PDF" />
3. Convert it: convert -density 300 input.pdf output.png


### Create bounding boxes
1. Install those python libraries - pip install pytesseract and pip install pillow
2. Run the script - python3 ocr_with_bounding_boxes.py input.png output.png