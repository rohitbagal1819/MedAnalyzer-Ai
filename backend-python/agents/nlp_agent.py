"""
NLP Agent — spaCy NER + Rule-based extraction
Processes raw text to extract structured medical data.
"""

import re
import os
from datetime import datetime

try:
    import spacy
    try:
        nlp = spacy.load('en_core_web_sm')
    except OSError:
        nlp = None
except ImportError:
    spacy = None
    nlp = None


class NLPAgent:
    """Extracts structured medical data from raw text using NLP."""

    # Normal ranges for common lab tests
    NORMAL_RANGES = {
        'hemoglobin': {'min': 12.0, 'max': 16.0, 'unit': 'g/dL', 'critical_low': 7.0, 'critical_high': 20.0},
        'hb': {'min': 12.0, 'max': 16.0, 'unit': 'g/dL', 'critical_low': 7.0, 'critical_high': 20.0},
        'wbc': {'min': 4000, 'max': 11000, 'unit': 'cells/cumm', 'critical_low': 2000, 'critical_high': 30000},
        'white blood cells': {'min': 4000, 'max': 11000, 'unit': 'cells/cumm', 'critical_low': 2000, 'critical_high': 30000},
        'rbc': {'min': 4.5, 'max': 5.5, 'unit': 'million/cumm', 'critical_low': 2.5, 'critical_high': 8.0},
        'red blood cells': {'min': 4.5, 'max': 5.5, 'unit': 'million/cumm', 'critical_low': 2.5, 'critical_high': 8.0},
        'platelets': {'min': 150000, 'max': 400000, 'unit': '/cumm', 'critical_low': 50000, 'critical_high': 1000000},
        'hematocrit': {'min': 36, 'max': 46, 'unit': '%', 'critical_low': 20, 'critical_high': 60},
        'hct': {'min': 36, 'max': 46, 'unit': '%', 'critical_low': 20, 'critical_high': 60},
        'mcv': {'min': 80, 'max': 100, 'unit': 'fL', 'critical_low': 50, 'critical_high': 130},
        'mch': {'min': 27, 'max': 33, 'unit': 'pg', 'critical_low': 15, 'critical_high': 45},
        'mchc': {'min': 32, 'max': 36, 'unit': 'g/dL', 'critical_low': 25, 'critical_high': 40},
        'esr': {'min': 0, 'max': 20, 'unit': 'mm/hr', 'critical_low': 0, 'critical_high': 100},
        'fasting blood sugar': {'min': 70, 'max': 100, 'unit': 'mg/dL', 'critical_low': 40, 'critical_high': 500},
        'fbs': {'min': 70, 'max': 100, 'unit': 'mg/dL', 'critical_low': 40, 'critical_high': 500},
        'post prandial blood sugar': {'min': 70, 'max': 140, 'unit': 'mg/dL', 'critical_low': 40, 'critical_high': 500},
        'ppbs': {'min': 70, 'max': 140, 'unit': 'mg/dL', 'critical_low': 40, 'critical_high': 500},
        'hba1c': {'min': 4.0, 'max': 5.7, 'unit': '%', 'critical_low': 3.0, 'critical_high': 15.0},
        'total cholesterol': {'min': 0, 'max': 200, 'unit': 'mg/dL', 'critical_low': 0, 'critical_high': 400},
        'ldl cholesterol': {'min': 0, 'max': 100, 'unit': 'mg/dL', 'critical_low': 0, 'critical_high': 300},
        'ldl': {'min': 0, 'max': 100, 'unit': 'mg/dL', 'critical_low': 0, 'critical_high': 300},
        'hdl cholesterol': {'min': 40, 'max': 200, 'unit': 'mg/dL', 'critical_low': 20, 'critical_high': 200},
        'hdl': {'min': 40, 'max': 200, 'unit': 'mg/dL', 'critical_low': 20, 'critical_high': 200},
        'triglycerides': {'min': 0, 'max': 150, 'unit': 'mg/dL', 'critical_low': 0, 'critical_high': 500},
        'sgot': {'min': 5, 'max': 40, 'unit': 'U/L', 'critical_low': 0, 'critical_high': 200},
        'ast': {'min': 5, 'max': 40, 'unit': 'U/L', 'critical_low': 0, 'critical_high': 200},
        'sgpt': {'min': 7, 'max': 56, 'unit': 'U/L', 'critical_low': 0, 'critical_high': 300},
        'alt': {'min': 7, 'max': 56, 'unit': 'U/L', 'critical_low': 0, 'critical_high': 300},
        'bilirubin': {'min': 0.1, 'max': 1.2, 'unit': 'mg/dL', 'critical_low': 0, 'critical_high': 15},
        'bilirubin total': {'min': 0.1, 'max': 1.2, 'unit': 'mg/dL', 'critical_low': 0, 'critical_high': 15},
        'alkaline phosphatase': {'min': 44, 'max': 147, 'unit': 'U/L', 'critical_low': 0, 'critical_high': 500},
        'creatinine': {'min': 0.7, 'max': 1.3, 'unit': 'mg/dL', 'critical_low': 0, 'critical_high': 10},
        'blood urea': {'min': 7, 'max': 20, 'unit': 'mg/dL', 'critical_low': 0, 'critical_high': 100},
        'bun': {'min': 7, 'max': 20, 'unit': 'mg/dL', 'critical_low': 0, 'critical_high': 100},
        'uric acid': {'min': 3.4, 'max': 7.0, 'unit': 'mg/dL', 'critical_low': 1.0, 'critical_high': 15.0},
        'tsh': {'min': 0.4, 'max': 4.0, 'unit': 'mIU/L', 'critical_low': 0.01, 'critical_high': 50},
        't3': {'min': 0.8, 'max': 2.0, 'unit': 'ng/mL', 'critical_low': 0.2, 'critical_high': 5.0},
        't4': {'min': 5.1, 'max': 14.1, 'unit': 'ug/dL', 'critical_low': 1.0, 'critical_high': 25.0},
    }

    # Disease patterns
    DISEASE_KEYWORDS = [
        'diabetes', 'hypertension', 'hyperthyroidism', 'hypothyroidism',
        'dyslipidemia', 'anemia', 'infection', 'malaria', 'dengue',
        'tuberculosis', 'asthma', 'copd', 'pneumonia', 'covid',
        'hepatitis', 'kidney disease', 'liver disease', 'cancer',
        'arthritis', 'osteoporosis', 'thyroid disorder'
    ]

    def analyze(self, raw_text):
        """
        Analyze raw text and extract structured medical data.
        Returns dict with lab_values, medications, diseases, etc.
        """
        result = {
            'lab_values': [],
            'medications': [],
            'diseases': [],
            'doctor_name': '',
            'hospital_name': '',
            'report_type': 'Other',
            'report_date': None
        }

        if not raw_text or len(raw_text.strip()) < 10:
            print("  [NLP] raw_text is empty or too short, nothing to extract.")
            return result

        print(f"  [NLP] Analyzing {len(raw_text)} characters of text...")

        # Extract lab values
        result['lab_values'] = self._extract_lab_values(raw_text)
        print(f"  [NLP] Found {len(result['lab_values'])} lab values")

        # Extract medications
        result['medications'] = self._extract_medications(raw_text)
        print(f"  [NLP] Found {len(result['medications'])} medications")

        # Extract diseases
        result['diseases'] = self._extract_diseases(raw_text)

        # Extract doctor name
        result['doctor_name'] = self._extract_doctor_name(raw_text)

        # Extract hospital name
        result['hospital_name'] = self._extract_hospital_name(raw_text)

        # Detect report type
        result['report_type'] = self._detect_report_type(raw_text)

        # Extract report date
        result['report_date'] = self._extract_date(raw_text)

        return result

    def _extract_lab_values(self, text):
        """Extract lab values with status (normal/high/low/critical)."""
        lab_values = []

        # Known test name keywords to look for in each line
        known_tests = list(self.NORMAL_RANGES.keys()) + [
            'total cholesterol', 'ldl cholesterol', 'hdl cholesterol',
            'fasting blood sugar', 'post prandial blood sugar',
            'bilirubin total', 'alkaline phosphatase', 'blood urea',
            'uric acid', 'white blood cells', 'red blood cells',
            'sgot', 'sgpt', 'ast', 'alt', 'hemoglobin', 'hematocrit',
            'platelets', 'triglycerides', 'creatinine', 'tsh', 'hba1c',
        ]

        # Process text line by line
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line or len(line) < 5:
                continue

            # Try to find a known test name in this line
            matched_test = None
            matched_pos = -1
            for test in sorted(known_tests, key=len, reverse=True):  # longest first
                pos = line.lower().find(test)
                if pos != -1:
                    matched_test = test
                    matched_pos = pos
                    break

            if matched_test is None:
                continue

            # Extract the actual test name from the line (preserving original case)
            test_name = line[matched_pos:matched_pos + len(matched_test)].strip()
            remainder = line[matched_pos + len(matched_test):].strip()
            # Also check text before test name for full name like "SGOT (AST)"
            prefix = line[:matched_pos].strip()
            if prefix and len(prefix) < 20 and re.match(r'^[A-Za-z\s\(\)]+$', prefix):
                test_name = prefix + ' ' + test_name
            test_name = test_name.strip(' :')

            # Find numeric value and unit in remainder
            # Pattern: number followed by unit
            val_match = re.search(r'[:\s]*(\d+\.?\d*)\s*([a-zA-Z/%]+(?:/[a-zA-Z]+)?)', remainder)
            if not val_match:
                continue

            value_str = val_match.group(1)
            unit = val_match.group(2).strip()

            try:
                value = float(value_str)
            except ValueError:
                continue

            # Try to find reference range in remainder
            ref_remainder = remainder[val_match.end():]
            normal_range = ''
            ref_match = re.search(r'([<>]?\s*\d+\.?\d*(?:\s*-\s*\d+\.?\d*)?)', ref_remainder)
            if ref_match:
                normal_range = ref_match.group(1).strip()

            # Determine status
            status = self._check_status(test_name, value, normal_range)

            # Build normal range string if not provided
            if not normal_range:
                normal_range = self._get_normal_range_str(test_name)

            lab_values.append({
                'testName': test_name,
                'value': value_str,
                'unit': unit,
                'normalRange': normal_range,
                'status': status
            })

        # Deduplicate by test name (keep first match)
        seen = set()
        unique = []
        for lv in lab_values:
            key = lv['testName'].lower().strip()
            if key not in seen:
                seen.add(key)
                unique.append(lv)

        return unique

    def _check_status(self, test_name, value, normal_range_str=''):
        """Determine if a lab value is normal, high, low, or critical."""
        test_key = test_name.lower().strip()

        # Try to match against known ranges
        matched_range = None
        for key, ranges in self.NORMAL_RANGES.items():
            if key in test_key or test_key in key:
                matched_range = ranges
                break

        if matched_range:
            if value <= matched_range.get('critical_low', 0):
                return 'critical'
            elif value >= matched_range.get('critical_high', 99999):
                return 'critical'
            elif value < matched_range['min']:
                return 'low'
            elif value > matched_range['max']:
                return 'high'
            else:
                return 'normal'

        # Try to parse from normal range string
        if normal_range_str:
            range_match = re.search(r'([\d.]+)\s*[-–]\s*([\d.]+)', normal_range_str)
            if range_match:
                try:
                    rmin = float(range_match.group(1))
                    rmax = float(range_match.group(2))
                    if value < rmin:
                        return 'low'
                    elif value > rmax:
                        return 'high'
                    else:
                        return 'normal'
                except ValueError:
                    pass

            # Check for < or > pattern
            lt_match = re.search(r'<\s*([\d.]+)', normal_range_str)
            if lt_match:
                try:
                    threshold = float(lt_match.group(1))
                    return 'normal' if value < threshold else 'high'
                except ValueError:
                    pass

            gt_match = re.search(r'>\s*([\d.]+)', normal_range_str)
            if gt_match:
                try:
                    threshold = float(gt_match.group(1))
                    return 'normal' if value > threshold else 'low'
                except ValueError:
                    pass

        return 'normal'

    def _get_normal_range_str(self, test_name):
        """Get normal range string for a test name."""
        test_key = test_name.lower().strip()
        for key, ranges in self.NORMAL_RANGES.items():
            if key in test_key or test_key in key:
                return f"{ranges['min']}-{ranges['max']} {ranges['unit']}"
        return ''

    def _extract_medications(self, text):
        """Extract medication names, dosages, and frequencies."""
        medications = []

        # Multiple patterns to catch different medication formats
        med_patterns = [
            # Pattern 1: "1. Tab. MedName Dosage - Frequency"
            re.compile(
                r'(?:^|\n)\s*\d+[\.\\)]\s*(?:Tab\.?\s*|Cap\.?\s*|Syr\.?\s*|Inj\.?\s*)?([A-Za-z]+(?:[-\s][A-Za-z]+)?)\s+'
                r'(\d+\s*(?:mg|mcg|ml|g|iu|µg))\s*[-–—]?\s*(.*?)(?:\n|$)',
                re.IGNORECASE | re.MULTILINE
            ),
            # Pattern 2: "1. MedName Dosage Frequency" (no dash, space separated)
            re.compile(
                r'(?:^|\n)\s*\d+[\.\\)]\s*(?:Tab\.?\s*|Cap\.?\s*|Syr\.?\s*|Inj\.?\s*)?([A-Za-z]+(?:[-][A-Za-z]+)?)\s+'
                r'(\d+\s*(?:mg|mcg|ml|g|iu|µg))\s+((?:once|twice|thrice|daily|morning|night|before|after|every|bd|od|tds|hs).*?)(?:\n|$)',
                re.IGNORECASE | re.MULTILINE
            ),
        ]

        for med_pattern in med_patterns:
            matches = med_pattern.finditer(text)
            for match in matches:
                name = match.group(1).strip()
                dosage = match.group(2).strip()
                frequency = match.group(3).strip() if match.group(3) else ''

                # Skip obvious non-medications
                skip_words = ['test', 'result', 'report', 'patient', 'doctor', 'hospital', 'date', 'interaction', 'vital', 'signs', 'gender']
                if name.lower() in skip_words or len(name) < 3:
                    continue

                # Skip if already found
                if any(m['name'].lower() == name.lower() for m in medications):
                    continue

                medications.append({
                    'name': name.title(),
                    'dosage': dosage,
                    'frequency': frequency
                })

        # Also try: "Prescription:" or "Medications:" section line-by-line
        if not medications:
            med_section = re.search(
                r'(?:medication|prescription|prescribed|medicines?|drugs?)[:\s]*\n((?:.*\n)*?)(?:\n\s*\n|diagnosis|remark|interaction|doctor|follow\s*up|$)',
                text, re.IGNORECASE
            )
            if med_section:
                lines = med_section.group(1).strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 3:
                        # Must contain a dosage unit or frequency keyword to be considered a real medication
                        if not re.search(r'(mg|mcg|ml|g|iu|µg|daily|twice|thrice|once|drops|tablet|capsule)', line, re.IGNORECASE):
                            continue
                            
                        # Pattern for section line: optional number, optional prefix, name, optional dosage, optional frequency
                        parts = re.match(r'^(?:\d+[\.\\)])?\s*(?:Tab\.?\s*|Cap\.?\s*|Syr\.?\s*|Inj\.?\s*)?([A-Za-z]+(?:[-][A-Za-z]+)?)\s*([\d.]+\s*(?:mg|mcg|ml|g|iu|µg)?)?\s*[-–—]?\s*(.*)?$', line, re.IGNORECASE)
                        if parts:
                            name = parts.group(1).strip()
                            if len(name) < 3: continue
                            
                            medications.append({
                                'name': name.title(),
                                'dosage': parts.group(2).strip() if parts.group(2) else '',
                                'frequency': parts.group(3).strip() if parts.group(3) else ''
                            })

        return medications

    def _extract_diseases(self, text):
        """Extract diagnosed diseases/conditions."""
        diseases = []
        text_lower = text.lower()

        # Check for diagnosis section
        diag_match = re.search(
            r'(?:diagnosis|diagnosed|condition|impression)[:\s]*(.*?)(?:\n\s*\n|remark|note|$)',
            text, re.IGNORECASE | re.DOTALL
        )

        if diag_match:
            diag_text = diag_match.group(1)
            parts = re.split(r'[,\n]', diag_text)
            for part in parts:
                cleaned = part.strip().strip('.-•*')
                if cleaned and len(cleaned) > 3:
                    diseases.append(cleaned)

        # Also check for keyword matches
        for keyword in self.DISEASE_KEYWORDS:
            if keyword in text_lower and keyword.title() not in diseases:
                pattern = re.compile(rf'\b{keyword}\b[a-z\s]*', re.IGNORECASE)
                match = pattern.search(text)
                if match:
                    disease = match.group(0).strip()
                    if disease and disease not in diseases:
                        diseases.append(disease.title())

        return list(set(diseases))[:10]

    def _extract_doctor_name(self, text):
        """Extract doctor name."""
        patterns = [
            r'(?:Doctor|Dr\.?|Physician|Consultant)[:\s]+(?:Dr\.?\s*)?([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)',
            r'Dr\.?\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        # Try spaCy NER
        if nlp:
            doc = nlp(text[:2000])
            for ent in doc.ents:
                if ent.label_ == 'PERSON':
                    context = text[max(0, ent.start_char - 20):ent.start_char]
                    if re.search(r'Dr\.?|Doctor|Physician', context, re.IGNORECASE):
                        return ent.text

        return ''

    def _extract_hospital_name(self, text):
        """Extract hospital/clinic name."""
        patterns = [
            r'(?:Hospital|Clinic|Medical Center|Lab|Laboratory|Diagnostic)[:\s]*([A-Z][A-Za-z\s]+(?:Hospital|Clinic|Center|Lab|Laboratory)?)',
            r'([A-Z][A-Za-z\s]+(?:Hospital|Clinic|Medical Center|Lab|Laboratory|Diagnostics))',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1).strip()
                if len(name) > 3:
                    return name

        # Try spaCy NER
        if nlp:
            doc = nlp(text[:2000])
            for ent in doc.ents:
                if ent.label_ == 'ORG':
                    name_lower = ent.text.lower()
                    if any(kw in name_lower for kw in ['hospital', 'clinic', 'medical', 'lab', 'diagnostic']):
                        return ent.text

        return ''

    def _detect_report_type(self, text):
        """Detect the type of medical report."""
        text_lower = text.lower()

        if any(kw in text_lower for kw in ['cbc', 'complete blood count', 'hemoglobin', 'wbc', 'rbc', 'blood test', 'hematology']):
            return 'Blood Test'
        elif any(kw in text_lower for kw in ['x-ray', 'xray', 'radiograph', 'chest pa']):
            return 'X-Ray'
        elif any(kw in text_lower for kw in ['prescription', 'prescribed', 'rx', 'medication']):
            return 'Prescription'
        elif any(kw in text_lower for kw in ['discharge', 'discharge summary', 'admitted', 'discharged']):
            return 'Discharge Summary'
        else:
            return 'Other'

    def _extract_date(self, text):
        """Extract report date."""
        date_patterns = [
            r'(?:Date|Report Date|Test Date)[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(?:Date|Report Date|Test Date)[:\s]*(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d', '%m/%d/%Y']:
                    try:
                        return datetime.strptime(date_str, fmt).isoformat()
                    except ValueError:
                        continue

        return datetime.now().isoformat()
