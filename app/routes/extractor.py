# routes/extractor.py
from flask import Blueprint, request, send_file
from app.services.extractor_service import parse_cis_pdf
import io

extractor = Blueprint("extractor", __name__)

@extractor.route("/api/extract", methods=["POST"])
def extract():
    uploaded_file = request.files.get("file")
    if not uploaded_file:
        return "No file uploaded", 400

    try:
        output_stream = io.BytesIO()
        parse_cis_pdf(uploaded_file, output_stream)
        output_stream.seek(0)

        # 🔁 Generate output filename from input PDF
        import os
        original_filename = uploaded_file.filename or "output.pdf"
        base_name = os.path.splitext(original_filename)[0]
        output_filename = f"{base_name}_output.csv"

        return send_file(
            output_stream,
            mimetype="text/csv",
            as_attachment=True,
            download_name=output_filename
        )
    except Exception as e:
        print("❌ Exception during PDF parsing:", str(e))
        return {"error": str(e)}, 500

