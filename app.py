from flask import Flask, render_template, request, flash, redirect, url_for
import psycopg2
import os
from extract_compare_aadhaar import compare_aadhaar_data
from extract_compare_pan import compare_pan_data

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'webp'}

# PostgreSQL configuration
db_config = {
    'user': 'postgres',
    'password': 'dumb',
    'host': 'localhost',
    'database': 'document_verification',
    'port': '5432'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/prompt')
def prompt():
    return render_template('prompt.html')

@app.route('/submit_prompt', methods=['POST'])
def submit_prompt():
    document = request.files['document']
    prompt_text = request.form['prompt']

    if not (document and prompt_text):
        flash('Document and prompt are required!', 'error')
        return redirect(url_for('prompt'))

    if not allowed_file(document.filename):
        flash('Invalid file format! Only PNG, JPG, JPEG, WEBP allowed.', 'error')
        return redirect(url_for('prompt'))

    # Save uploaded file
    document_path = os.path.join(app.config['UPLOAD_FOLDER'], document.filename)
    document.save(document_path)

    # Store in database
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        query = """
        INSERT INTO prompt_submissions (prompt, document_path)
        VALUES (%s, %s)
        """
        cursor.execute(query, (prompt_text, document_path))
        conn.commit()
    except psycopg2.Error as err:
        flash(f'Database error: {err}', 'error')
        return redirect(url_for('prompt'))
    finally:
        cursor.close()
        conn.close()

    # Redirect to scanfile.html on success
    return redirect(url_for('scanfile'))

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    dob = request.form['dob']
    aadhar_no = request.form['aadhar_no']
    pan_no = request.form['pan_no']
    aadhar_photo = request.files['aadhar_photo']
    pan_card = request.files['pan_card']

    if not all([name, dob, aadhar_no, pan_no, aadhar_photo, pan_card]):
        flash('All fields are required!', 'error')
        return redirect(url_for('index'))

    if not (allowed_file(aadhar_photo.filename) and allowed_file(pan_card.filename)):
        flash('Invalid file format! Only PNG, JPG, JPEG, WEBP allowed.', 'error')
        return redirect(url_for('index'))

    # Save uploaded files
    aadhar_path = os.path.join(app.config['UPLOAD_FOLDER'], aadhar_photo.filename)
    pan_path = os.path.join(app.config['UPLOAD_FOLDER'], pan_card.filename)
    aadhar_photo.save(aadhar_path)
    pan_card.save(pan_path)

    # Verify Aadhaar
    aadhar_results = compare_aadhaar_data(aadhar_path, name, dob, aadhar_no)
    if 'error' in aadhar_results:
        flash(f'Aadhaar verification failed: {aadhar_results["error"]}', 'error')
        return redirect(url_for('index'))
    if not (aadhar_results['name_match'] and aadhar_results['dob_match'] and 
            aadhar_results['aadhaar_match'] and aadhar_results['aadhaar_valid']):
        flash('Aadhaar verification failed: Data mismatch or invalid Aadhaar number!', 'error')
        return redirect(url_for('index'))

    # Verify PAN
    pan_results = compare_pan_data(pan_path, name, dob, pan_no)
    if 'error' in pan_results:
        flash(f'PAN verification failed: {pan_results["error"]}', 'error')
        return redirect(url_for('index'))
    if not (pan_results['name_match'] and pan_results['dob_match'] and 
            pan_results['pan_match'] and pan_results['pan_valid']):
        flash('PAN verification failed: Data mismatch or invalid PAN number!', 'error')
        return redirect(url_for('index'))

    # Store in database
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        query = """
        INSERT INTO users (name, dob, aadhar_no, pan_no, aadhar_photo_path, pan_card_path)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, dob, aadhar_no, pan_no, aadhar_path, pan_path))
        conn.commit()
    except psycopg2.Error as err:
        flash(f'Database error: {err}', 'error')
        return redirect(url_for('index'))
    finally:
        cursor.close()
        conn.close()

    # Redirect to scanfile.html on success
    return redirect(url_for('scanfile'))

@app.route('/scanfile')
def scanfile():
    return render_template('scanfile.html')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)