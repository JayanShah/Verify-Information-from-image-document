from inference_sdk import InferenceHTTPClient
import pytesseract
import cv2
import re
from datetime import datetime

pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

# Roboflow Inference SDK configuration
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="bK81chKOSxNpOOK20jcK"  # Replace with your Roboflow API key
)
ROBOFLOW_MODEL = "pan-cards/1"  # PAN card detection model

def validate_pan(pan_number):
    """
    Validates a PAN number using regex (5 letters, 4 digits, 1 letter).
    """
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    return bool(re.match(pattern, pan_number))

def normalize_string(s):
    """
    Normalize string by removing extra spaces and converting to lowercase.
    """
    return re.sub(r'\s+', ' ', s.strip().lower())

def extract_pan_info(image_path):
    """
    Extract PAN information (Name, DOB, Pan Number) using Roboflow Inference SDK and OCR.
    Returns a dictionary with extracted data and PAN number validation result.
    """
    try:
        result = CLIENT.infer(image_path, model_id=ROBOFLOW_MODEL)
        predictions = result.get('predictions', [])
        img = cv2.imread(image_path)
        extract_dict = {}

        def get_coords(bbox, img):
            x, y, width, height = bbox['x'], bbox['y'], bbox['width'], bbox['height']
            x1 = max(0, int(x - width / 2))
            y1 = max(0, int(y - height / 2))
            x2 = min(img.shape[1], int(x + width / 2))
            y2 = min(img.shape[0], int(y + height / 2))
            return img[y1:y2, x1:x2]

        for elem in predictions:
            if elem['confidence'] > 0.75 and (elem['class_id'] == 0 or elem['class_id'] >= 3):
                cropped_region = get_coords(elem, img)
                extracted_text = pytesseract.image_to_string(cropped_region).strip()
                # Map class names to consistent keys
                class_key = elem['class']
                if class_key == 'Pan Number':
                    class_key = 'pan_number'
                elif class_key == 'Name':
                    class_key = 'name'
                elif class_key == 'DOB':
                    class_key = 'dob'
                extract_dict[class_key] = extracted_text

        # Validate PAN number
        pan_number = extract_dict.get('pan_number', '')
        pan_number = re.sub(r'\s+', '', pan_number).upper()  # Remove spaces, convert to uppercase
        is_valid = validate_pan(pan_number)
        extract_dict['pan_valid'] = is_valid
        return extract_dict
    except Exception as e:
        return {'error': str(e)}

def compare_pan_data(image_path, input_name, input_dob, input_pan_no):
    """
    Extract PAN data and compare with provided textual data.
    Returns a dictionary with comparison results.
    """
    extracted_data = extract_pan_info(image_path)
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
            input_dob_obj.strftime('%Y-%m-%d'),
            input_dob_obj.strftime('%d %b %Y'),
            input_dob_obj.strftime('%d %B %Y')
        ]
        extracted_dob_normalized = normalize_string(extracted_dob)
        results['dob_match'] = any(normalize_string(d) in extracted_dob_normalized for d in dob_formats)
    except:
        results['dob_match'] = False

    # Compare PAN number
    extracted_pan = re.sub(r'\s+', '', extracted_data.get('pan_number', '')).upper()
    input_pan_no = re.sub(r'\s+', '', input_pan_no).upper()
    results['pan_match'] = extracted_pan == input_pan_no
    results['pan_valid'] = extracted_data.get('pan_valid', False)

    # Extracted data for reference
    results['extracted_data'] = {
        'name': extracted_data.get('name', ''),
        'dob': extracted_data.get('dob', ''),
        'pan_number': extracted_pan
    }

    return results

# Example usage
if __name__ == "__main__":
    image_path = r""  # Replace with actual image path
    input_name = ""  # Replace with test name
    input_dob = ""  # Replace with test DOB (YYYY-MM-DD)
    input_pan_no = ""  # Replace with test PAN number

    results = compare_pan_data(image_path, input_name, input_dob, input_pan_no)
    
    if 'error' in results:
        print(f"Error: {results['error']}")
    else:
        print("Comparison Results:")
        print(f"Name Match: {results['name_match']}")
        print(f"DOB Match: {results['dob_match']}")
        print(f"PAN Number Match: {results['pan_match']}")
        print(f"PAN Number Valid: {results['pan_valid']}")
        print("\nExtracted Data:")
        for key, value in results['extracted_data'].items():
            print(f"{key.capitalize()}: {value}")