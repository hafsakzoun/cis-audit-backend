from flask import Blueprint, request, send_file
import os
import uuid
from datetime import datetime
from app.services.audit_executor import execute_audit_script
from app.services.notice_parser import parse_notices
from app.services.report_generator import generate_report_files
from flask_cors import cross_origin  # ✅ Needed for route-level CORS

audit_route = Blueprint('audit_route', __name__)
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'uploads'))

@audit_route.route('/api/auditor', methods=['POST', 'OPTIONS'])
@cross_origin()   # ✅ Allow Angular dev origin
def run_audit():
    try:
        company = request.form['company']
        solution = request.form['solution']
        auditor = request.form['auditor']
        host = request.form['host']
        port = request.form['port']
        user = request.form['user']
        password = request.form['password']
        dbname = request.form['dbname']
        script = request.files['script']

        print(f"[INFO] Received audit request for company: {company}, DB: {dbname}")
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        script_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.sql")
        script.save(script_path)
        print(f"[INFO] Script saved at: {script_path}")

        notices = execute_audit_script(dbname, user, password, host, port, script_path)
        print(f"[INFO] Notices received: {notices}")

        results = parse_notices(notices)
        audit_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        zip_path = generate_report_files(company, solution, auditor, audit_date, results, UPLOAD_FOLDER)

        print(f"[INFO] Sending file: {zip_path}")
        return send_file(zip_path, as_attachment=True)

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return {'error': str(e)}, 500
