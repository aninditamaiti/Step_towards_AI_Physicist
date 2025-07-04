# -*- coding: utf-8 -*-
"""Data_Generator_AI_Physicist

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1EXWfhvYRpIUaAPG6h9mM_gucu6wqq9Nz

# Data generation


 The following class of functions converts a research paper from arxiv (from its html format to) .txt data --> to create training data for Transformer-based language models. Upto very minor bugs that I am yet to locate and fix, this class has the following features:
 - Cleans noise by removing navbars, ads, footers, sidebars, and script/style tags.
 - Ensures unicode conversion by converting accented and special characters to LaTeX-safe equivalents.
 - Converts equation blocks into LaTeX inline/display math.
 - Produces tokenization-ready inputs, prior to an emdebbing map, by producing consistently spaced and clean .txt file with normalized newlines.
"""

# Required libraries for HTTP requests, HTML parsing, regex, and HTML character decoding
import requests
from bs4 import BeautifulSoup
import re
import html

# Define a class to convert HTML from a URL into cleaned LaTeX-friendly text
class HTMLToLaTeXConverter:
    def __init__(self, url):
        self.url = url # Store the input URL
        self.html_content = self.download_html() # Download raw HTML content
        self.soup = self.clean_html() # Clean and parse the HTML

    # Fetch HTML content from the given URL
    def download_html(self):
        response = requests.get(self.url)
        response.raise_for_status() # Raise an error if request failed
        return response.text # Return the HTML as plain text

    # Parse and clean HTML using BeautifulSoup
    def clean_html(self):
        soup = BeautifulSoup(self.html_content, "html.parser")
        # Remove unwanted tags that are usually non-content (scripts, ads, navigation, etc.)
        for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside", "form", "iframe", "button", "input"]):
            tag.decompose()
        # Remove elements with ad- or cookie-related classes
        for ad in soup.find_all(attrs={"class": re.compile(".*(ad|banner|cookie).*", re.I)}):
            ad.decompose()
        # Remove elements with ad- or cookie-related IDs
        for ad in soup.find_all(attrs={"id": re.compile(".*(ad|banner|cookie).*", re.I)}):
            ad.decompose()
        return soup

    # Remove specific verbose or markup-style tokens that don’t translate to LaTeX
    def remove_verbose_tokens(self, text):
        tokens = [
            r'start_ARG', r'end_ARG',
            r'start_POSTSUPERSCRIPT', r'end_POSTSUPERSCRIPT',
            r'start_POSTSUBSCRIPT', r'end_POSTSUBSCRIPT',
            r'over˙', r'superscript', r'subscript',
            r'start_BOLD', r'end_BOLD'
        ]
        for t in tokens:
            text = re.sub(t, '', text) # Remove each pattern from the text
        return text

    # Convert bold Unicode letters to LaTeX \mathbf{} equivalents
    def unicode_bold_to_latex(self, text):
        def convert_char(c):
            codepoint = ord(c)
            # Capital bold A-Z
            if 0x1D400 <= codepoint <= 0x1D419:
                return '\\mathbf{' + chr(codepoint - 0x1D400 + ord('A')) + '}'
            # Lowercase bold a-z
            if 0x1D41A <= codepoint <= 0x1D433:
                return '\\mathbf{' + chr(codepoint - 0x1D41A + ord('a')) + '}'
            return c # Return character unchanged if not in range

        return ''.join(convert_char(c) for c in text)

    # Replace Unicode math symbols with their LaTeX equivalents
    def replace_unicode_math(self, text):
        math_unicode_map = {
            '𝛼': r'\\alpha', '𝛽': r'\\beta', '𝛾': r'\\gamma', '𝛿': r'\\delta',
            '𝜀': r'\\epsilon', '𝜃': r'\\theta', '𝜆': r'\\lambda', '𝜇': r'\\mu',
            '𝜋': r'\\pi', '𝜌': r'\\rho', '𝜎': r'\\sigma', '𝜏': r'\\tau',
            '𝜙': r'\\phi', '𝜔': r'\\omega',
            '𝛥': r'\\Delta', '𝛤': r'\\Gamma', '𝛮': r'N', '𝛴': r'\\Sigma',
            '𝚨': r'\\Alpha', '𝚩': r'\\Beta', '𝚪': r'\\Gamma', '𝚫': r'\\Delta',
            '𝚻': r'\\Tau', '𝚽': r'\\Phi', '𝛺': r'\\Omega', '𝚯': r'\\Theta',
            '𝛏': r'\\Xi', '𝛙': r'\\Psi',
            '𝐀': r'\\mathbf{A}', '𝐱': r'\\mathbf{x}', '𝐞': r'\\mathbf{e}', '𝐂': r'\\mathbf{C}',
            '𝜼': r'\\bm{\\eta}', '𝟎': r'\\mathbf{0}', '𝐣': r'\\mathbf{j}',
        }
        return ''.join(math_unicode_map.get(c, c) for c in text)

    # Convert special styling tokens (like fake LaTeX macros) to actual LaTeX commands
    def fix_fake_latex_tokens(self, text):
        greek_map = {
            'α': 'alpha', 'β': 'beta', 'γ': 'gamma', 'δ': 'delta', 'ε': 'epsilon', 'ζ': 'zeta', 'η': 'eta',
            'θ': 'theta', 'ι': 'iota', 'κ': 'kappa', 'λ': 'lambda', 'μ': 'mu', 'ν': 'nu', 'ξ': 'xi',
            'ο': 'omicron', 'π': 'pi', 'ρ': 'rho', 'σ': 'sigma', 'τ': 'tau', 'υ': 'upsilon', 'φ': 'phi',
            'χ': 'chi', 'ψ': 'psi', 'ω': 'omega', 'Δ': 'Delta', 'Γ': 'Gamma', 'Θ': 'Theta', 'Λ': 'Lambda',
            'Ξ': 'Xi', 'Π': 'Pi', 'Σ': 'Sigma', 'Υ': 'Upsilon', 'Φ': 'Phi', 'Ψ': 'Psi', 'Ω': 'Omega'
        }
        # Replacement function for regex matches
        def repl(m):
            style, var, suffix = m.group(1), m.group(2), m.group(3)
            latex_var = greek_map.get(var, var)
            result = m.group(0)

            # Map styling to LaTeX
            if style == "bold":
                result = r"\\mathbf{" + latex_var + "}"
            elif style == "italic":
                result = r"\\mathit{" + latex_var + "}"
            elif style == "bold_italic":
                result = r"\\bm{" + latex_var + "}"
            elif style == "roman":
                result = r"\\mathrm{" + latex_var + "}"
            if suffix:
                suffix = suffix.strip()
                if suffix == '⊤':
                    result += r'^\\top'
                else:
                    result += f'^{{{suffix}}}'
            return result

        # Pattern to find fake LaTeX macros
        pattern = r'\\b(bold_italic|bold|italic|roman)_([a-zA-ZͰ-Ͽ])\\b\s*(⊤|[\^\w])?'
        return re.sub(pattern, repl, text)

    # Clean raw text using a series of transformations
    def clean_text_pipeline(self, text):
        text = self.remove_verbose_tokens(text)
        text = html.unescape(text) # Decode HTML entities like &lt; or &amp;
        text = self.replace_unicode_math(text)
        text = self.unicode_bold_to_latex(text)
        text = self.fix_fake_latex_tokens(text)
        return text

    # Extract visible text from the cleaned HTML, convert it to LaTeX-compatible format
    def extract_text_latex(self):
        text_chunks = []
        block_tags = ['p', 'div', 'li', 'blockquote', 'section']

        # Iterate over relevant blocks and extract text
        for block in self.soup.body.find_all(block_tags):
            raw_text = block.get_text(separator=' ', strip=True)
            if raw_text:
                cleaned = self.clean_text_pipeline(raw_text)
                text_chunks.append(cleaned)
        # Join with double line breaks to indicate paragraph boundaries
        return '\n\n'.join(text_chunks)

    # Save the final LaTeX-compatible text to a file
    def save_to_text_file(self, output_path, text):
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)

    # Perform full conversion and save output to a file
    def convert_and_save(self, output_path):
        text = self.extract_text_latex()
        self.save_to_text_file(output_path, text)
        print(f"Saved to {output_path}")