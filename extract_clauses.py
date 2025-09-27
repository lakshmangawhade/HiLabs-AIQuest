from pypdf import PdfReader
import pytesseract
from PIL import Image
import io
import re

# --- OCR Configuration ---
# You must install Google's Tesseract-OCR engine and add it to your system's PATH.
# For Windows, you can find the installer here: https://github.com/UB-Mannheim/tesseract/wiki
# After installation, you might need to specify the path to the executable, like this:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Headers to search for, based on the corrected Attribute Dictionary
ATTRIBUTE_HEADERS = {
    "Medicaid Timely Filing": ["Submission and Adjudication of Medicaid Claims"],
    "Medicare Timely Filing": ["Submission and Adjudication of Medicare Advantage Claims", "Medicare Advantage Attachment"],
    "No Steerage/SOC": ["Networks and Provider Panels"],
    "Medicaid Fee Schedule": ["Specific Reimbursement Terms"],
    "Medicare Fee Schedule": ["Specific Reimbursement Terms"],
}

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF, using OCR for scanned pages."""
    try:
        reader = PdfReader(pdf_path)
        full_text = ""
        for i, page in enumerate(reader.pages):
            # First, try direct text extraction
            text = page.extract_text()
            
            # If direct extraction yields little or no text, assume it's a scanned page and use OCR
            if not text or len(text.strip()) < 100:  # Threshold to detect scanned pages
                # Get the images from the page
                try:
                    for image_file_object in page.images:
                        # Convert the image to a PIL Image object
                        image = Image.open(io.BytesIO(image_file_object.data))
                        # Perform OCR on the image
                        ocr_text = pytesseract.image_to_string(image)
                        full_text += ocr_text + "\n"
                except Exception as ocr_error:
                    print(f"Could not perform OCR on page {i} of {pdf_path}: {ocr_error}")
            else:
                full_text += text + "\n"
        return full_text
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return None

def extract_all_clauses(text):
    """Extracts clauses from text based on a dictionary of attributes and section headers."""
    if not text:
        return {}

    extracted_data = {}
    
    for attribute, headers in ATTRIBUTE_HEADERS.items():
        for header in headers:
            # Regex to find a header (potentially with numbering) and capture content until the next header
            pattern = re.compile(f"(^|\n)[\d.A-Z\s]*{re.escape(header)}[\s\n]*(.*?)(?=\n[\d.A-Z\s]*[A-Z][a-z]+[\s:]|$)", re.DOTALL | re.IGNORECASE)
            matches = pattern.finditer(text)
            
            for match in matches:
                clause_text = match.group(2).strip()
                
                # Differentiate between the two Fee Schedule attributes
                if header == "Specific Reimbursement Terms":
                    if attribute == "Medicaid Fee Schedule" and 'medicaid rate' in clause_text.lower():
                        extracted_data[attribute] = clause_text
                        break
                    elif attribute == "Medicare Fee Schedule" and 'medicare advantage rate' in clause_text.lower():
                        extracted_data[attribute] = clause_text
                        break
                else:
                    extracted_data[attribute] = clause_text
                    break # Found it, move to the next attribute
        if attribute in extracted_data:
            continue # Move to the next attribute in the outer loop

    return extracted_data

if __name__ == '__main__':
    # Example usage for testing
    contract_path = 'c:\\Users\\91916\\OneDrive\\Desktop\\hilabs\\HiLabsAIQuest_ContractsAI\\Contracts\\TN\\TN_Contract1_Redacted.pdf'
    
    print(f"Extracting text from: {contract_path}")
    full_text = extract_text_from_pdf(contract_path)
    
    if full_text:
        print("Text extracted. Now finding clauses...")
        clauses = extract_all_clauses(full_text)
        
        if clauses:
            for attribute, content in clauses.items():
                print(f"\n--- Found: {attribute} ---")
                print(content[:500].strip() + "...")
        else:
            print("Could not find any of the specified clauses in the test file.")
