# OCR Image to Text Conversion

This guide provides instructions on how to perform Optical Character Recognition (OCR) to convert images to text using Tesseract-OCR and Python.

## Tesseract-OCR Method

### Installation
1. Install Tesseract-OCR: `sudo apt install tesseract-ocr`
2. Download the Bulgarian language dictionary: [bul.traineddata](https://github.com/tesseract-ocr/tessdata/blob/main/bul.traineddata)
3. Move the downloaded dictionary to the Tesseract-OCR data directory: `mv bul.traineddata /usr/share/tesseract-ocr/4.00/tessdata/`
4. Install jq `sudo apt install jq`

### Install Python Libraries
1. pip3 install pytesseract
2. pip3 install pillow
3. pip3 install pandas
4. pip3 install argparse
5. pip3 install pdf2image

### Convert PDF into Images
1. Install ImageMagic: sudo apt install imagemagick
2. Add this policy in  /etc/ImageMagick-6/policy.xml: <policy domain="coder" rights="read | write" pattern="PDF" />
3. Convert it: convert -density 300 input.pdf output.png

### Instructions
1. Run the python file to OCR the pdf file
- python your_script.py your_json_file.json --delete
