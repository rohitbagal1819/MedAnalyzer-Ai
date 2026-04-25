"""
Gemini AI Client — Wrapper for Google Gemini API
Handles text extraction, medical report analysis, and health scoring.
No hardcoded medical data — all intelligence comes from Gemini.
"""

import json
import re
import time
import google.generativeai as genai
from PIL import Image


class GeminiClient:
    """Wrapper for Google Gemini API for medical report analysis."""

    def __init__(self, api_key):
        if not api_key:
            raise ValueError("Gemini API key is required")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.vision_model = genai.GenerativeModel('gemini-2.0-flash')

    def extract_from_image(self, image_path):
        """
        Use Gemini Vision to extract text from a medical report image.
        Returns raw text extracted from the image.
        """
        try:
            img = Image.open(image_path)
            prompt = (
                "You are a medical document OCR expert. Extract ALL text from this medical report image "
                "exactly as written. Preserve the structure, formatting, table layouts, and all numbers. "
                "Include all test names, values, units, reference ranges, patient details, doctor names, "
                "hospital names, dates, and medications. Do not summarize or interpret — just extract the raw text."
            )
            response = self.vision_model.generate_content([prompt, img])
            return response.text if response.text else ''
        except Exception as e:
            print(f"  ⚠ Gemini Vision OCR error: {e}")
            return ''

    def analyze_medical_report(self, raw_text):
        """
        Analyze raw medical report text using Gemini AI.
        Returns structured JSON with lab values, medications, diseases, etc.
        NO hardcoded normal ranges or disease keywords — Gemini uses medical knowledge.
        """
        if not raw_text or len(raw_text.strip()) < 10:
            return self._empty_result()

        prompt = f"""You are an expert medical report analyzer with deep knowledge of clinical medicine, 
laboratory diagnostics, and pharmacology.

Analyze the following medical report text and extract ALL information into this exact JSON structure.

IMPORTANT RULES:
1. For lab values: Determine the status (normal/high/low/critical) using YOUR medical knowledge of standard reference ranges. Do NOT guess — only classify if you are confident.
2. For medications: Extract ALL medications mentioned including brand names and generic names. Include dosage and frequency if mentioned.
3. For diseases: Extract ALL diagnoses, conditions, and clinical impressions mentioned.
4. For report_date: Extract the actual date of the test/report, NOT today's date. Use ISO format (YYYY-MM-DD).
5. For report_type: Classify as one of: "Blood Test", "X-Ray", "Prescription", "Discharge Summary", "Urine Test", "Lipid Profile", "Thyroid Test", "Liver Function Test", "Kidney Function Test", "Other"
6. Be thorough — extract everything, even from messy or poorly formatted text.

Return ONLY valid JSON (no markdown, no explanation, no code blocks):

{{
  "lab_values": [
    {{
      "testName": "Full test name",
      "value": "numeric value as string",
      "unit": "unit of measurement",
      "normalRange": "min-max unit (standard reference range)",
      "status": "normal|high|low|critical"
    }}
  ],
  "medications": [
    {{
      "name": "Drug name (capitalize properly)",
      "dosage": "e.g. 500mg",
      "frequency": "e.g. twice daily"
    }}
  ],
  "diseases": ["list of diagnosed conditions/diseases"],
  "doctor_name": "name or empty string",
  "hospital_name": "name or empty string",
  "report_type": "one of the types listed above",
  "report_date": "YYYY-MM-DD or null",
  "patient_name": "name or empty string",
  "patient_age": "age or empty string",
  "patient_gender": "Male/Female or empty string",
  "summary": "2-3 line clinical summary of the report findings"
}}

Medical Report Text:
---
{raw_text}
---"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()

            # Clean up response - remove markdown code blocks if present
            text = re.sub(r'^```(?:json)?\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
            text = text.strip()

            result = json.loads(text)
            return result

        except json.JSONDecodeError as e:
            print(f"  ⚠ Gemini returned invalid JSON: {e}")
            print(f"  Raw response: {text[:500] if text else 'empty'}")
            return self._empty_result()
        except Exception as e:
            print(f"  ⚠ Gemini analysis error: {e}")
            return self._empty_result()

    def calculate_health_score(self, lab_values, medications, diseases, drug_interactions, anomalies):
        """
        Use Gemini to calculate a health score (0-100) based on all extracted data.
        No hardcoded scoring rules — Gemini uses medical judgment.
        """
        data_summary = {
            'lab_values_count': len(lab_values),
            'abnormal_values': [lv for lv in lab_values if lv.get('status') in ('high', 'low', 'critical')],
            'critical_values': [lv for lv in lab_values if lv.get('status') == 'critical'],
            'medications_count': len(medications),
            'diseases': diseases,
            'drug_interactions_count': len(drug_interactions),
            'severe_interactions': [di for di in drug_interactions if di.get('severity') == 'severe'],
            'anomalies_count': len(anomalies)
        }

        prompt = f"""You are a clinical health assessment AI. Based on the following medical data, 
calculate a health score from 0 to 100.

Scoring guidelines:
- 80-100: Excellent health, all values normal, no concerning findings
- 60-79: Good health with minor concerns
- 40-59: Moderate concerns, some abnormal values or conditions
- 20-39: Significant health issues requiring attention
- 0-19: Critical condition, immediate medical attention needed

Medical Data:
- Total lab parameters tested: {data_summary['lab_values_count']}
- Abnormal values ({len(data_summary['abnormal_values'])}): {json.dumps([f"{v['testName']}: {v['value']} ({v['status']})" for v in data_summary['abnormal_values'][:10]])}
- Critical values ({len(data_summary['critical_values'])}): {json.dumps([f"{v['testName']}: {v['value']}" for v in data_summary['critical_values'][:5]])}
- Medications: {data_summary['medications_count']}
- Diagnosed conditions: {json.dumps(data_summary['diseases'][:10])}
- Drug interactions found: {data_summary['drug_interactions_count']}
- Severe drug interactions: {len(data_summary['severe_interactions'])}

Return ONLY a JSON object with two fields (no markdown, no explanation):
{{"score": <number 0-100>, "reasoning": "brief 1-line explanation"}}"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            text = re.sub(r'^```(?:json)?\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
            result = json.loads(text)
            score = max(0, min(100, int(result.get('score', 50))))
            return score
        except Exception as e:
            print(f"  ⚠ Gemini scoring error: {e}")
            # Fallback: simple calculation
            return self._fallback_score(data_summary)

    def _fallback_score(self, data):
        """Fallback scoring when Gemini fails — basic math, no hardcoded medical data."""
        score = 85
        score -= len(data['abnormal_values']) * 5
        score -= len(data['critical_values']) * 15
        score -= data['drug_interactions_count'] * 8
        score -= len(data['severe_interactions']) * 10
        score -= min(len(data['diseases']), 5) * 3
        return max(0, min(100, score))

    def _empty_result(self):
        """Return empty result structure."""
        return {
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
