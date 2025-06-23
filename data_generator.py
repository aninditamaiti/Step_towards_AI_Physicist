# 1. Import the class (assuming it's defined above or in a separate file you imported)
from html_to_tex_converter import HTMLToLaTeXConverter  # replace with the actual file if saved separately


# 2. Define your URL and output path
url = "https://arxiv.org/html/2506.14609v1"
output_path = "dataset2506.14609v1.txt"

# 3. Initialize and run the conversion
converter = HTMLToLaTeXConverter(url)
converter.convert_and_save(output_path)

print(f"Saved to {output_path}")
