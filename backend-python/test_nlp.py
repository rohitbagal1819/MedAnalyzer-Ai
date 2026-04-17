import sys
sys.path.insert(0, '.')
from agents.nlp_agent import NLPAgent

text = """WESTSIDE CLINIC
LIPID PROFILE & LIVER FUNCTION
Patient: Lisa Wong Report Date: 2025-03-05
Age: 2025-03-10
LIPID PROFILE & LIVER FUNCTION

Test Result Unit Reference Range
Total Cholesterol 260 mg/dL <200 (HIGH)
HDL 35 mg/dL 40-200 (LOW)
LDL 175 mg/dL <100 (HIGH)
Triglycerides 190 mg/dL <150 (HIGH)
SGOT (AST) 85 U/L 5-40 (HIGH)
SGPT (ALT) 92 U/L 7-56 (HIGH)
Bilirubin Total 0.8 mg/dL 0.1-1.2 (HIGH)
Fasting Blood Sugar 118 mg/dL 70-100 (HIGH)

Diagnosis:
Dyslipidemia
Non-alcoholic fatty liver disease (NAFLD)
Prediabetes

Medications:
1. Omeprazole 20 mg once daily
2. Clopidogrel 75 mg once daily

Doctor: Dr. James Taylor
Hospital: Westside Clinic"""

agent = NLPAgent()
result = agent.analyze(text)

print("=== LAB VALUES ===")
for lv in result['lab_values']:
    print(f"  {lv['testName']}: {lv['value']} {lv['unit']} (status={lv['status']})")

print("\n=== MEDICATIONS ===")
for m in result['medications']:
    print(f"  {m['name']} {m['dosage']} - {m['frequency']}")

print("\n=== DISEASES ===")
for d in result['diseases']:
    print(f"  {d}")

print(f"\nDoctor: {result['doctor_name']}")
print(f"Hospital: {result['hospital_name']}")
print(f"Type: {result['report_type']}")
