#!/bin/bash

# Check if a JSON file is provided as an argument
if [ $# -ne 1 ]; then
    echo "Usage: $0 <json_file>"
    exit 1
fi

json_file="$1"
text_dir="$(dirname "$json_file")/text"
output_text_file="$text_dir/all_text.txt"  # New text file to store all OCR results

# Create the text directory if it doesn't exist
mkdir -p "$text_dir"

# Check if the output text file exists; if not, create it
touch "$output_text_file"

# Read the JSON file and process one link at a time
cat "$json_file" | jq -r '.files[]' | while read -r link; do
    # Extract the file name from the URL
    file_name=$(basename "$link")

    # Check if the file has already been processed
    if [ -e "$text_dir/$file_name.txt" ]; then
        echo "File $file_name has already been processed. Skipping."
    else
        echo "Downloading $file_name..."
        # Download the PDF file
        wget -q "$link" -O "$text_dir/$file_name"

        # Convert PDF to images using pdftoppm
        echo "Converting $file_name to images..."
        pdftoppm -jpeg -r 300 "$text_dir/$file_name" "$text_dir/${file_name%.*}"

        # Perform OCR using Tesseract on each image
        for image_file in "$text_dir/${file_name%.*}"*; do
            echo "Performing OCR on $image_file..."
            tesseract "$image_file" "$text_dir/$(basename ${image_file%.*})" -l bul

            # Append the text from Tesseract to the output text file
            cat "$text_dir/$(basename ${image_file%.*}).txt" >> "$output_text_file"
        done

        # Remove the downloaded PDF and image files to save space
        rm "$text_dir/$file_name"
        rm "$text_dir/${file_name%.*}"*

        # Exit the loop after processing one PDF
        break
    fi
done

echo "All files processed."
