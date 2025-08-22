from flask import Blueprint, request, send_file
import os
import uuid
from datetime import datetime
from app.services.audit_executor import execute_audit_script
from app.services.notice_parser import parse_notices
from app.services.report_generator import generate_report_files
from flask_cors import cross_origin
from werkzeug.utils import secure_filename
from app.services.elastic_service import save_audit_record, get_all_audits, es, AUDIT_INDEX

audit_route = Blueprint('audit_route', __name__)
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'uploads'))

def get_next_audit_id():
    """
    Get the next sequential audit ID based on the last saved audit.
    """
    try:
        res = es.search(
            index=AUDIT_INDEX,
            size=1,
            sort=[{"audit_id": {"order": "desc"}}]
        )
        if res["hits"]["hits"]:
            last_id = int(res["hits"]["hits"][0]["_source"]["audit_id"])
            return last_id + 1
        return 1
    except Exception:
        return 1

@audit_route.route('/api/auditor', methods=['POST', 'OPTIONS'])
@cross_origin()
def run_audit():
    try:
        # --- Extract form data ---
        company = request.form['company']
        solution = request.form['solution']
        auditor = request.form['auditor']
        host = request.form['host']
        port = request.form['port']
        user = request.form['user']
        password = request.form['password']
        dbname = request.form['dbname']
        script = request.files['script']

        print(f"[INFO] Received audit request for company={company}, db={dbname}")
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # --- Save uploaded script ---
        script_filename = secure_filename(script.filename)
        script_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{script_filename}")
        script.save(script_path)
        print(f"[INFO] Script saved at: {script_path}")

        # --- Run audit ---
        notices = execute_audit_script(dbname, user, password, host, port, script_path)
        print(f"[INFO] Notices received: {notices}")
        results = parse_notices(notices)
        audit_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # --- Generate report ZIP ---
        zip_path = generate_report_files(company, solution, auditor, audit_date, results, UPLOAD_FOLDER)
        print(f"[INFO] Report generated: {zip_path}")

        # --- Build audit record for Elasticsearch ---
        audit_id = get_next_audit_id()
        audit_record = {
            "audit_id": audit_id,
            "company": company,
            "solution": solution,
            "auditor": auditor,
            "date": audit_date,
            "status": "Completed" if results else "No Results",
            "results": os.path.basename(zip_path),  # just the report file name
            "script_file": os.path.basename(script_path)  # optional
        }

        # --- Save to Elasticsearch ---
        save_response = save_audit_record(audit_record)
        print(f"[INFO] Elasticsearch save response: {save_response}")
        if save_response.get("status") != "success":
            print(f"[ERROR] Failed to save audit record to Elasticsearch")

        # --- Return ZIP file to frontend ---
        return send_file(zip_path, as_attachment=True)

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return {'error': str(e)}, 500


# Route to serve uploaded script & reports later
@audit_route.route('/api/auditor/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        return {"error": "File not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 500
    

# Get Audit History
@audit_route.route('/api/auditor/history', methods=['GET'])
@cross_origin()
def audit_history():
    try:
        limit = int(request.args.get("limit", 50))
        audits = get_all_audits(limit)
        return {"audits": audits}, 200
    except Exception as e:
        return {"error": str(e)}, 500
