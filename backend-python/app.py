"""
MedAnalyzer AI — Python AI Microservice
Flask entry point
Receives medical report files, processes them through the AI pipeline,
and returns structured JSON with extracted data.
"""

import os
import tempfile
import traceback
from flask import Flask, request, jsonify
from agents.ocr_agent import OCRAgent
from agents.nlp_agent import NLPAgent
from agents.drug_agent import DrugAgent
from agents.scoring_agent import ScoringAgent

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'MedAnalyzer AI Python Microservice',
        'version': '1.0.0'
    })


@app.route('/analyze', methods=['POST'])
def analyze_report():
    """
    Main analysis endpoint.
    Receives a medical report file (PDF or image) via multipart POST,
    runs it through the AI pipeline, and returns structured JSON.
    """
    try:
        # Validate file
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        report_id = request.form.get('report_id', 'unknown')
        file_type = request.form.get('file_type', 'image')

        # Save file temporarily
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        print(f"\n[INFO] Processing report: {file.filename} (type: {file_type}, id: {report_id})")

        # ─── STEP 1: OCR Extract Text ─────────────────────
        print("  [Step 1] OCR extraction...")
        ocr_agent = OCRAgent()
        raw_text = ocr_agent.extract_text(file_path, file_type)
        print(f"  [OK] Extracted {len(raw_text)} characters of text")

        if len(raw_text.strip()) < 10:
            print("  [WARNING] Very little text extracted. The image may be low quality.")

        # ─── STEP 2: NLP Analysis ─────────────────────────
        print("  [Step 2] NLP analysis...")
        nlp_agent = NLPAgent()
        nlp_result = nlp_agent.analyze(raw_text)
        print(f"  [OK] Found {len(nlp_result.get('lab_values', []))} lab values, "
              f"{len(nlp_result.get('medications', []))} medications")

        # ─── STEP 3: Drug Interaction Check ────────────────
        print("  [Step 3] Drug interaction check...")
        drug_agent = DrugAgent()
        medications = nlp_result.get('medications', [])
        drug_interactions = drug_agent.check_interactions(medications)
        print(f"  [OK] Found {len(drug_interactions)} interactions")

        # ─── STEP 4: Health Score Calculation ──────────────
        print("  [Step 4] Health score calculation...")
        scoring_agent = ScoringAgent()
        lab_values = nlp_result.get('lab_values', [])
        anomalies = scoring_agent.detect_anomalies(lab_values)
        health_score = scoring_agent.calculate_score(
            lab_values=lab_values,
            anomalies=anomalies,
            drug_interactions=drug_interactions,
            raw_text=raw_text
        )
        print(f"  [OK] Health score: {health_score}")

        # Clean up temp file
        try:
            os.remove(file_path)
        except:
            pass

        # Build response
        response = {
            'success': True,
            'report_id': report_id,
            'raw_text': raw_text,
            'report_type': nlp_result.get('report_type', 'Other'),
            'report_date': nlp_result.get('report_date', None),
            'lab_values': nlp_result.get('lab_values', []),
            'medications': nlp_result.get('medications', []),
            'diseases': nlp_result.get('diseases', []),
            'doctor_name': nlp_result.get('doctor_name', ''),
            'hospital_name': nlp_result.get('hospital_name', ''),
            'drug_interactions': drug_interactions,
            'anomalies': anomalies,
            'health_score': health_score
        }

        print(f"[DONE] Report {report_id} processed successfully!")
        return jsonify(response)

    except Exception as e:
        print(f"[ERROR] Error processing report: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


if __name__ == '__main__':
    print("")
    print("=" * 50)
    print("  MedAnalyzer AI - Python Microservice")
    print("  Running on http://localhost:5001")
    print("=" * 50)
    print("")
    app.run(host='0.0.0.0', port=5001, debug=True)
