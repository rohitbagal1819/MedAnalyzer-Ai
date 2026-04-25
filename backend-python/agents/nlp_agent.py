"""
NLP Agent — Medical report analysis using Gemini AI
ALL medical intelligence comes from Gemini — NO hardcoded normal ranges,
NO hardcoded disease keywords, NO regex-based extraction.
"""


class NLPAgent:
    """Extracts structured medical data using Gemini AI."""

    def __init__(self, gemini_client=None):
        """
        Args:
            gemini_client: GeminiClient instance for AI analysis
        """
        self.gemini_client = gemini_client

    def analyze(self, raw_text):
        """
        Analyze raw text and extract structured medical data using Gemini AI.
        Returns dict with lab_values, medications, diseases, etc.

        NO hardcoded data:
        - Normal ranges determined by Gemini's medical knowledge
        - Diseases identified by Gemini's clinical understanding
        - Medications extracted by Gemini's pharmacological knowledge
        """
        empty_result = {
            'lab_values': [],
            'medications': [],
            'diseases': [],
            'doctor_name': '',
            'hospital_name': '',
            'report_type': 'Other',
            'report_date': None,
            'patient_name': '',
            'patient_age': '',
            'patient_gender': '',
            'summary': ''
        }

        if not raw_text or len(raw_text.strip()) < 10:
            print("  [NLP] raw_text is empty or too short, nothing to extract.")
            return empty_result

        if not self.gemini_client:
            print("  [NLP] ⚠ No Gemini client available — cannot analyze report")
            return empty_result

        print(f"  [NLP] Sending {len(raw_text)} characters to Gemini AI for analysis...")

        try:
            result = self.gemini_client.analyze_medical_report(raw_text)

            # Validate and normalize the result
            result = self._validate_result(result, empty_result)

            print(f"  [NLP] Gemini extracted:")
            print(f"    - {len(result.get('lab_values', []))} lab values")
            print(f"    - {len(result.get('medications', []))} medications")
            print(f"    - {len(result.get('diseases', []))} diseases")
            print(f"    - Report type: {result.get('report_type', 'Other')}")
            print(f"    - Report date: {result.get('report_date', 'Not found')}")

            return result

        except Exception as e:
            print(f"  [NLP] ⚠ Gemini analysis failed: {e}")
            return empty_result

    def _validate_result(self, result, empty_result):
        """Validate and normalize Gemini's response."""
        if not isinstance(result, dict):
            return empty_result

        # Ensure all expected keys exist with correct types
        validated = {**empty_result}

        # Lab values
        lab_values = result.get('lab_values', [])
        if isinstance(lab_values, list):
            validated['lab_values'] = []
            for lv in lab_values:
                if isinstance(lv, dict) and lv.get('testName'):
                    validated['lab_values'].append({
                        'testName': str(lv.get('testName', '')).strip(),
                        'value': str(lv.get('value', '')).strip(),
                        'unit': str(lv.get('unit', '')).strip(),
                        'normalRange': str(lv.get('normalRange', '')).strip(),
                        'status': lv.get('status', 'normal') if lv.get('status') in ('normal', 'high', 'low', 'critical') else 'normal'
                    })

        # Medications
        medications = result.get('medications', [])
        if isinstance(medications, list):
            validated['medications'] = []
            for med in medications:
                if isinstance(med, dict) and med.get('name'):
                    validated['medications'].append({
                        'name': str(med.get('name', '')).strip().title(),
                        'dosage': str(med.get('dosage', '')).strip(),
                        'frequency': str(med.get('frequency', '')).strip()
                    })

        # Diseases
        diseases = result.get('diseases', [])
        if isinstance(diseases, list):
            validated['diseases'] = [str(d).strip() for d in diseases if d and str(d).strip()]

        # String fields
        for field in ['doctor_name', 'hospital_name', 'report_type', 'report_date',
                       'patient_name', 'patient_age', 'patient_gender', 'summary']:
            val = result.get(field)
            if val is not None:
                validated[field] = str(val).strip() if val else ''

        # Validate report_type
        valid_types = ['Blood Test', 'X-Ray', 'Prescription', 'Discharge Summary',
                       'Urine Test', 'Lipid Profile', 'Thyroid Test',
                       'Liver Function Test', 'Kidney Function Test', 'Other']
        if validated['report_type'] not in valid_types:
            validated['report_type'] = 'Other'

        return validated
