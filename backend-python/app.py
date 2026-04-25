"""
MedAnalyzer AI — Python AI Microservice
Flask entry point — 100% API-driven, no hardcoded medical data.

APIs used:
- Google Gemini AI (OCR + NLP + Scoring)
- OpenFDA (Drug labels, interactions, ingredients)
- RxNorm / NIH (Drug name normalization)
"""

import os
import tempfile
import traceback
from flask import Flask, request, jsonify

# Agents
from agents.ocr_agent import OCRAgent
from agents.nlp_agent import NLPAgent
from agents.drug_agent import DrugAgent
from agents.scoring_agent import ScoringAgent

# API Clients
from utils.gemini_client import GeminiClient
from utils.openfda_client import OpenFDAClient
from utils.rxnorm_client import RxNormClient

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'MedAnalyzer AI Python Microservice',
        'version': '2.0.0',
        'mode': 'API-driven (Gemini + OpenFDA + RxNorm)'
    })


@app.route('/analyze', methods=['POST'])
def analyze_report():
    """
    Main analysis endpoint.
    Receives a medical report file (PDF or image) via multipart POST,
    runs it through the API-driven AI pipeline, and returns structured JSON.

    ALL intelligence comes from APIs:
    - Gemini AI: OCR, text extraction, lab value analysis, disease detection
    - OpenFDA: Drug interactions, active ingredients, warnings
    - RxNorm: Drug name normalization
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
        gemini_api_key = request.form.get('gemini_api_key', '')
        openfda_api_key = request.form.get('openfda_api_key', '')

        # Save file temporarily
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        print(f"\n{'='*50}")
        print(f"[INFO] Processing report: {file.filename}")
        print(f"  Type: {file_type} | ID: {report_id}")
        print(f"  Gemini API: {'✓ configured' if gemini_api_key else '✗ missing'}")
        print(f"  OpenFDA API: {'✓ configured' if openfda_api_key else '○ no key (limited)'}")
        print(f"{'='*50}")

        # ─── Initialize API Clients ─────────────────────────
        gemini_client = None
        if gemini_api_key:
            try:
                gemini_client = GeminiClient(api_key=gemini_api_key)
                print("  [✓] Gemini AI client initialized")
            except Exception as e:
                print(f"  [✗] Gemini init failed: {e}")

        openfda_client = OpenFDAClient(api_key=openfda_api_key)
        rxnorm_client = RxNormClient()
        print("  [✓] OpenFDA + RxNorm clients initialized")

        # ─── STEP 1: OCR Extract Text (Gemini Vision) ──────
        print("\n  [Step 1] OCR extraction (Gemini Vision)...")
        ocr_agent = OCRAgent(gemini_client=gemini_client)
        raw_text = ocr_agent.extract_text(file_path, file_type)
        print(f"  [OK] Extracted {len(raw_text)} characters of text")

        if len(raw_text.strip()) < 10:
            print("  [WARNING] Very little text extracted.")

        # ─── STEP 2: NLP Analysis (Gemini AI) ──────────────
        print("\n  [Step 2] NLP analysis (Gemini AI)...")
        nlp_agent = NLPAgent(gemini_client=gemini_client)
        nlp_result = nlp_agent.analyze(raw_text)
        print(f"  [OK] Found {len(nlp_result.get('lab_values', []))} lab values, "
              f"{len(nlp_result.get('medications', []))} medications, "
              f"{len(nlp_result.get('diseases', []))} diseases")

        # ─── STEP 3: Drug Interaction Check (OpenFDA) ──────
        print("\n  [Step 3] Drug interaction check (OpenFDA + RxNorm)...")
        drug_agent = DrugAgent(openfda_client=openfda_client, rxnorm_client=rxnorm_client)
        medications = nlp_result.get('medications', [])
        drug_interactions = drug_agent.check_interactions(medications)
        print(f"  [OK] Found {len(drug_interactions)} interactions")

        # ─── STEP 3b: Drug Info Lookup (OpenFDA) ───────────
        drug_info = []
        if medications:
            print("\n  [Step 3b] Drug info lookup (OpenFDA + RxNorm)...")
            drug_info = drug_agent.lookup_drug_info(medications)
            fda_count = sum(1 for d in drug_info if d.get('source') == 'openfda')
            rxn_count = sum(1 for d in drug_info if d.get('rxcui'))
            print(f"  [OK] Got info for {len(drug_info)} drugs ({fda_count} from OpenFDA, {rxn_count} with RxCUI)")

        # ─── STEP 4: Health Score (Gemini AI) ──────────────
        print("\n  [Step 4] Health score calculation (Gemini AI)...")
        scoring_agent = ScoringAgent(gemini_client=gemini_client)
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
            'patient_name': nlp_result.get('patient_name', ''),
            'patient_age': nlp_result.get('patient_age', ''),
            'patient_gender': nlp_result.get('patient_gender', ''),
            'summary': nlp_result.get('summary', ''),
            'drug_interactions': drug_interactions,
            'drug_info': drug_info,
            'anomalies': anomalies,
            'health_score': health_score
        }

        print(f"\n[DONE] Report {report_id} processed successfully!")
        print(f"  Data sources: Gemini AI + OpenFDA + RxNorm (zero hardcoded data)")
        print(f"{'='*50}\n")

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
    print("=" * 55)
    print("  MedAnalyzer AI — Python Microservice v2.0")
    print("  Powered by: Gemini AI + OpenFDA + RxNorm")
    print("  Zero hardcoded medical data")
    print("  Running on http://localhost:5001")
    print("=" * 55)
    print("")
    app.run(host='0.0.0.0', port=5001, debug=True)
