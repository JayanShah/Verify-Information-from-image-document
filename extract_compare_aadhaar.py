import requests
import cv2
import pytesseract
import re
from datetime import datetime

pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

# Roboflow API configuration
ROBOFLOW_API_KEY = 'bK81chKOSxNpOOK20jcK'  # Replace with your Roboflow API key
ROBOFLOW_MODEL = 'aadhar-card-verification-rfy8q/2'  # Replace with your model path

def verhoeff_check(aadhaar_number):
    """
    Verifies an Aadhaar number using the Verhoeff algorithm.
    """
    d_table = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
        [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
        [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
        [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
        [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
        [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
        [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
        [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
        [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    ]
    p_table = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
        [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
        [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
        [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
        [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
        [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
        [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
    ]
    aadhaar_number = aadhaar_number[::-1]
    c = 0
    for i, digit in enumerate(aadhaar_number):
        c = d_table[c][p_table[i % 8][int(digit)]]
    return c == 0

def normalize_string(s):
    """
    Normalize string by removing extra spaces and converting to lowercase.
    """
    return re.sub(r'\s+', ' ', s.strip().lower())

def extract_aadhaar_info(image_path):
    """
    Extract Aadhaar information (name, DOB, Aadhaar number) using Roboflow API and OCR.
    Returns a dictionary with extracted data and Aadhaar number validation result.
    """
    url = f"https://detect.roboflow.com/{ROBOFLOW_MODEL}?api_key={ROBOFLOW_API_KEY}"
    try:
        with open(image_path, "rb") as image:
            response = requests.post(url, files={"file": image})
        predictions = response.json()
        img = cv2.imread(image_path)
        extract_dict = {}

        def get_coords(bbox, img):
            x, y, width, height = bbox['x'], bbox['y'], bbox['width'], bbox['height']
            x1 = max(0, int(x - width / 2))
            y1 = max(0, int(y - height / 2))
            x2 = min(img.shape[1], int(x + width / 2))
            y2 = min(img.shape[0], int(y + height / 2))
            return img[y1:y2, x1:x2]

        for elem in predictions.get('predictions', []):
            if elem['confidence'] > 0.6 and elem['class_id'] >= 3:
                cropped_region = get_coords(elem, img)
                extracted_text = pytesseract.image_to_string(cropped_region).strip()
                extract_dict[elem['class']] = extracted_text

        # Validate Aadhaar number
        aadhaar_number = extract_dict.get('aadhar_no', '')
        
        aadhaar_number = re.sub(r'\D', '', aadhaar_number)  # Keep only digits
        aadhaar_number = ''.join(aadhaar_number.split())  # Remove extra spaces
        if len(aadhaar_number) > 12:     
            ValueError("Aadhaar number should not exceed 12 digits.")
        is_valid = False
        if len(aadhaar_number) == 12 and aadhaar_number.isdigit():
            is_valid = verhoeff_check(aadhaar_number)
        extract_dict['aadhaar_valid'] = is_valid
        
        return extract_dict
    except Exception as e:
        return {'error': str(e)}

def compare_aadhaar_data(image_path, input_name, input_dob, input_aadhaar_no):
    """
    Extract Aadhaar data and compare with provided textual data.
    Returns a dictionary with comparison results.
    """
    extracted_data = extract_aadhaar_info(image_path)
    if 'error' in extracted_data:
        return {'error': extracted_data['error']}

    results = {}

    # Compare name
    extracted_name = normalize_string(extracted_data.get('name', ''))
    input_name = normalize_string(input_name)
    results['name_match'] = extracted_name == input_name or input_name in extracted_name

    # Compare DOB
    extracted_dob = extracted_data.get('dob', '')
    try:
        input_dob_obj = datetime.strptime(input_dob, '%Y-%m-%d')
        dob_formats = [
            input_dob_obj.strftime('%d/%m/%Y'),
            input_dob_obj.strftime('%d-%m-%Y'),
            input_dob_obj.strftime('%Y/%m/%d'),
            input_dob_obj.strftime('%Y-%m-%d')
        ]
        extracted_dob_normalized = normalize_string(extracted_dob)
        results['dob_match'] = any(normalize_string(d) in extracted_dob_normalized for d in dob_formats)
    except:
        results['dob_match'] = False

    # Compare Aadhaar number
    extracted_aadhaar = re.sub(r'\D', '', extracted_data.get('aadhar_no', ''))
    input_aadhaar_no = re.sub(r'\D', '', input_aadhaar_no)
    results['aadhaar_match'] = extracted_aadhaar == input_aadhaar_no
    results['aadhaar_valid'] = extracted_data.get('aadhaar_valid', False)

    # Extracted data for reference
    results['extracted_data'] = {
        'name': extracted_data.get('name', ''),
        'dob': extracted_data.get('dob', ''),
        'aadhaar_number': extracted_aadhaar
    }

    return results

# Example usage
if __name__ == "__main__":
    image_path = r""  # Replace with actual image path
    input_name = ""  # Replace with test name
    input_dob = "YYYY-MM-DD"  # Replace with test DOB (YYYY-MM-DD)
    input_aadhaar_no = ""  # Replace with test Aadhaar number

    results = compare_aadhaar_data(image_path, input_name, input_dob, input_aadhaar_no)
    
    if 'error' in results:
        print(f"Error: {results['error']}")
    else:
        print("Comparison Results:")
        print(f"Name Match: {results['name_match']}")
        print(f"DOB Match: {results['dob_match']}")
        print(f"Aadhaar Number Match: {results['aadhaar_match']}")
        print(f"Aadhaar Number Valid: {results['aadhaar_valid']}")
        print("\nExtracted Data:")
        for key, value in results['extracted_data'].items():
            print(f"{key.capitalize()}: {value}")