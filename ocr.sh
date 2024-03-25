#!/bin/bash

# Check if at least a JSON file is provided as an argument
if [ $# -lt 1 ]; then
    echo "Usage: $0 <json_file> [number_of_items]"
    exit 1
fi

json_file="$1"
number_of_items="${2:-0}"  # Default to 0, indicating all items
text_dir="$(dirname "$json_file")/text"
output_text_file="$text_dir/all_text.txt"  # New text file to store all OCR results

# Create the text directory if it doesn't exist
mkdir -p "$text_dir"

# Check if the output text file exists; if not, create it
touch "$output_text_file"

# Process a specified number of items from the JSON file, or all if no number is specified
if [ "$number_of_items" -eq 0 ]; then
    items_to_process='.files[]'
else
    items_to_process=".files | .[:$number_of_items][]"
fi

jq -r "$items_to_process" "$json_file" | while read -r link; do
    file_name=$(basename "$link")

    if [ -e "$text_dir/$file_name.txt" ]; then
        echo "File $file_name has already been processed. Skipping."
    else
        echo "Downloading $file_name..."
        wget -q "$link" -O "$text_dir/$file_name"

        echo "Converting $file_name to images..."
        pdftoppm -jpeg -r 300 "$text_dir/$file_name" "$text_dir/${file_name%.*}"

        # Remove the PDF file after conversion to images
        rm "$text_dir/$file_name"

        # for image_file in "$text_dir/${file_name%.*}"*; do
        #     echo "Performing OCR on $image_file..."
        #     # psm 11 separete it too much
        #     tesseract "$image_file" "$text_dir/$(basename ${image_file%.*})" --oem 1 --psm 12 -l bul

        #     cat "$text_dir/$(basename ${image_file%.*}).txt" >> "$output_text_file"

        #     # Remove the image file after OCR
        #     # rm "$image_file"
        # done

        for image_file in "$text_dir/${file_name%.*}"*; do
            for psm in 3 6 11 12; do  # Add other PSM values as needed
                for oem in 0 1 2 3; do  # Iterate over OEM values
                    # Create an output filename with OEM and PSM values included
                    output_base="$text_dir/$(basename ${image_file%.*})_oem${oem}_psm${psm}"

                    echo "Performing OCR on $image_file with OEM $oem and PSM $psm..."
                    tesseract "$image_file" "$output_base" --oem $oem --psm $psm -l bul

                    # Append the recognized text to the all_text file with OEM and PSM noted
                    echo "OCR result for OEM $oem, PSM $psm" >> "$output_text_file"
                    cat "${output_base}.txt" >> "$output_text_file"
                done
            done
        done
    fi

    # If number_of_items is 1 or more, exit after processing the specified number of files
    if [ "$number_of_items" -gt 0 ]; then
        break
    fi
done

echo "All requested files processed."
