import re
import argparse

def convert_to_new_bulgarian(text):
    # Define character replacements
    replacements = [
        (r'([бвгджзклмнпрстфхцчшщ])ж([бвгджзклмнпрстфхцчшщ])', r'\1ъ\2', re.IGNORECASE),
        (r'([бвгджзклмнпрстфхцчшщ])Ъ([бвгджзклмнпрстфхцчшщ])', r'\1я\2'),
        (r'ѣ', 'е', re.IGNORECASE),
        (r'(ъ|ь) ', ' ', re.IGNORECASE),
        (r'-\n', '', re.IGNORECASE),
        (r'(ъ|ь)([^a-zа-я]+|$)', r'\2', re.IGNORECASE),  # Include the additional rule here
    ]

    # Apply the replacements
    for pattern, replacement, flags in replacements:
        text = re.sub(pattern, replacement, text, flags=flags)

    return text

def main():
    parser = argparse.ArgumentParser(description="Apply regex replacements to a text file.")
    parser.add_argument("input_file", help="Path to the input text file")
    args = parser.parse_args()

    # Read the text from the input file
    with open(args.input_file, "r", encoding="utf-8") as file:
        text = file.read()

    # Apply the regex replacements
    text = convert_to_new_bulgarian(text)

    # Write the modified text back to the same file
    with open(args.input_file, "w", encoding="utf-8") as file:
        file.write(text)

    print(f"Regex replacements applied and saved to {args.input_file}")

if __name__ == "__main__":
    main()
