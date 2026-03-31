# Verification and Extraction of Information from Semi-Categorized Documents

## Overview
The "Verification and Extraction of Information from Semi-Categorized Documents" project is a web-based application designed to automate the verification and storage of identity documents (Aadhaar and PAN cards) and enable users to submit arbitrary documents with descriptive prompts. Built with a modern tech stack, the application features a dark-themed, responsive interface powered by Flask and Bootstrap, with backend processing for image-based data extraction and validation. The system uses Optical Character Recognition (OCR) and Roboflow’s machine learning models to verify Aadhaar and PAN details, storing validated data in a PostgreSQL database named `minor`. It also supports a prompt-based submission feature for flexible document uploads, making it a versatile tool for document management.

The project provides two main functionalities:
1. **Identity Document Verification**: Users submit Aadhaar and PAN card details (name, date of birth, Aadhaar number, PAN number) along with images, which are verified against extracted data using OCR and Roboflow models.
2. **Prompt-Based Document Submission**: Users upload any document with a textual prompt describing it, which is stored in the database for future processing.

Key features include a responsive navbar with "Home" and "Prompt Submission" tabs, loading spinners for form submissions, error/success feedback via alerts, and a consistent dark theme for enhanced user experience.

## Technologies Used
The project integrates a robust set of technologies for web development, image processing, database management, and machine learning:

### Frontend
- **HTML5**: Structures the web pages (`base.html`, `index.html`, `prompt.html`).
- **Bootstrap 5.3.0**: Provides responsive design, navbar, forms, alerts, and loading spinners, sourced via CDN (`https://cdn.jsdelivr.net/npm/bootstrap@5.3.0`).
- **CSS (`style.css`)**: Customizes the dark theme (background: `#1a1a1a`, navbar: `#1f1f1f`, white text: `#ffffff`) with styles for inputs, buttons, and spinners.
- **JavaScript**: Handles form submission behavior, enabling/disabling buttons and showing/hiding loading spinners.

### Backend
- **Python 3.8+**: Powers the Flask application and verification scripts.
- **Flask 2.3.3**: A lightweight web framework for routing, templating, and request handling.
- **psycopg2-binary 2.9.9**: Connects the Flask app to the PostgreSQL `minor` database.
- **Tesseract OCR 5.3.0**: Extracts text from Aadhaar and PAN card images.
- **OpenCV-Python 4.8.1**: Pre-processes images for OCR accuracy.
- **Roboflow Inference SDK 0.9.20**: Integrates machine learning models for Aadhaar (`aadhar-card-verification-rfy8q/2`) and PAN (`pan-cards/1`) verification.
- **Requests 2.31.0**: Handles API calls to Roboflow for image processing.

### Database
- **PostgreSQL 16**: Stores verified Aadhaar/PAN data and prompt submissions in the `minor` database with tables `users` and `prompt_submissions`.

## Implementation Details
The project is implemented as a Flask web application with a modular structure, integrating frontend, backend, and database components. Below is a detailed breakdown of the implementation:

### Project Structure
```
project/
├── app.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── prompt.html
├── static/
│   ├── css/
│   │   ├── style.css
│   ├── uploads/
├── extract_compare_aadhaar.py
├── extract_compare_pan.py
├── requirements.txt
├── create_table.sql
```

- **`app.py`**: The main Flask application defines routes for the homepage (`/`), prompt submission (`/prompt`), Aadhaar/PAN verification (`/submit`), and prompt submission handling (`/submit_prompt`). It connects to the `minor` PostgreSQL database using `psycopg2` and handles file uploads to `static/uploads`.
- **`templates/base.html`**: A base template providing a dark-themed navbar with "Home" and "Prompt Submission" tabs, styled with Bootstrap and custom CSS.
- **`templates/index.html`**: The homepage with a form for Aadhaar/PAN submission, including fields for name, date of birth, Aadhaar number, PAN number, and image uploads, with a loading spinner.
- **`templates/prompt.html`**: A form for uploading a document and entering a textual prompt, with a loading spinner.
- **`static/css/style.css`**: Custom CSS for the dark theme, styling the navbar, forms, alerts, and spinners.
- **`extract_compare_aadhaar.py` and `extract_compare_pan.py`**: Scripts that use Tesseract OCR and Roboflow to extract and verify Aadhaar/PAN data from images.
- **`create_table.sql`**: Defines the `users` (Aadhaar/PAN data) and `prompt_submissions` (prompts and document paths) tables in the `minor` database.
- **`requirements.txt`**: Lists Python dependencies for the project.

### Workflow
1. **Identity Document Verification**:
   - Users access the homepage (`/`) and submit Aadhaar/PAN details and images via a form.
   - On submission, a loading spinner appears, and the button is disabled to prevent multiple submissions.
   - Images are saved to `static/uploads`.
   - `extract_compare_aadhaar.py` and `extract_compare_pan.py` process the images using Tesseract OCR and Roboflow models, validating name, date of birth, and document numbers.
   - Validated data is stored in the `users` table in the `minor` database.
   - Users receive success or error messages via Bootstrap alerts.

2. **Prompt-Based Document Submission**:
   - Users navigate to the "Prompt Submission" tab (`/prompt`) and upload a document with a textual prompt.
   - A loading spinner appears during submission.
   - The image is saved to `static/uploads`, and the prompt and file path are stored in the `prompt_submissions` table.
   - Success or error messages are displayed.

3. **Database Integration**:
   - The `minor` PostgreSQL database stores data in two tables:
     - `users`: Stores `id`, `name`, `dob`, `aadhar_no`, `pan_no`, `aadhar_photo_path`, `pan_card_path`, and `created_at`.
     - `prompt_submissions`: Stores `id`, `prompt`, `document_path`, and `created_at`.
   - `psycopg2` handles database connections and queries.

4. **Dark Theme**:
   - The interface uses a dark theme (background: `#1a1a1a`, navbar: `#1f1f1f`, text: `#ffffff`) with high-contrast elements for readability.
   - Custom CSS overrides Bootstrap defaults to ensure a consistent look across navbar, forms, alerts, and spinners.

### Setup Instructions
1. **Install PostgreSQL**:
   - Download and install PostgreSQL 16 from [postgresql.org](https://www.postgresql.org/download/windows/).
   - Set the `postgres` user password (e.g., `your_postgres_password`).
   - Verify: `psql -U postgres -h localhost`.

2. **Set Up Database**:
   - Run `create_table.sql` to create tables in the `minor` database:
     ```bash
     psql -U postgres -h localhost -f C:\path\to\create_table.sql
     ```
   - Verify tables: `psql -U postgres -h localhost -d minor`, then `\dt`.

3. **Install Python and Dependencies**:
   - Install Python 3.8+ from [python.org](https://www.python.org/downloads/).
   - Navigate to the project directory: `cd C:\path\to\project`.
   - Install dependencies: `pip install -r requirements.txt`.

4. **Install Tesseract OCR**:
   - Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki).
   - Install to `C:\Program Files\Tesseract-OCR` and add to PATH.
   - Verify: `tesseract --version`.

5. **Configure Roboflow**:
   - Update `extract_compare_aadhaar.py` and `extract_compare_pan.py` with your Roboflow API key (e.g., `api_key="bK81chKOSxNpOOK20jcK"`).

6. **Update Database Configuration**:
   - In `app.py`, set `db_config['password']` to your PostgreSQL password.

7. **Run the Application**:
   - Ensure `static/uploads` exists: `mkdir static\uploads`.
   - Run: `python app.py`.
   - Access at `http://127.0.0.1:5000`.

## Applications
The project has wide-ranging applications in document management and verification:

1. **Identity Verification**:
   - Automates Aadhaar and PAN card verification for banks, financial institutions, and government agencies, reducing manual effort and errors.
   - Ensures compliance with KYC (Know Your Customer) regulations by validating identity documents.

2. **Document Management**:
   - The prompt-based submission feature allows organizations to collect and store miscellaneous documents (e.g., contracts, certificates) with user-provided context, enabling flexible document categorization.

3. **Fraud Prevention**:
   - Validates document authenticity using OCR and machine learning, detecting mismatches or invalid numbers to prevent fraudulent submissions.

4. **Administrative Efficiency**:
   - Streamlines onboarding processes for businesses by automating document verification and storage.
   - Provides a scalable solution for handling large volumes of document submissions.

5. **Extensibility**:
   - The prompt submission feature can be extended to support additional document types or integrate with AI for advanced analysis (e.g., extracting specific data from prompts).
   - The PostgreSQL database supports robust data management for future features like document retrieval or analytics.

## Future Enhancements
- **Advanced Prompt Processing**: Integrate Roboflow or other AI models to analyze prompt submissions and extract structured data.
- **Navbar Enhancements**: Add active tab highlighting for better navigation.
- **Security**: Use a `.env` file for sensitive data (API keys, database password).
- **UI Improvements**: Add progress bars or overlays for loading states.
- **Scalability**: Support multiple file uploads or batch processing for prompt submissions.

## Testing
- **Home Page**: Submit Aadhaar/PAN data with valid images, verify spinner, database storage (`SELECT * FROM minor.users`), and error messages for invalid inputs.
- **Prompt Submission**: Upload a document and prompt, confirm spinner, database storage (`SELECT * FROM minor.prompt_submissions`), and error handling.
- **Dark Theme**: Ensure all pages have consistent dark styling (navbar: `#1f1f1f`, background: `#1a1a1a`).

## Troubleshooting
- **Database Errors**: Verify PostgreSQL is running (`net start postgresql-16`) and `db_config` in `app.py` is correct.
- **Dependency Issues**: Reinstall dependencies (`pip install -r requirements.txt`) or `psycopg2-binary` separately.
- **OCR/Roboflow Failures**: Check API key and model IDs, test scripts standalone (`python extract_compare_aadhaar.py`).
- **Theme Issues**: Clear browser cache or inspect CSS in dev tools (F12).

