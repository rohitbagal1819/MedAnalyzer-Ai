import sys
sys.path.insert(0, '.')
from agents.drug_agent import DrugAgent

# These are the medications extracted from the report image
medications = [
    {'name': 'Omeprazole', 'dosage': '20 mg', 'frequency': 'once daily'},
    {'name': 'Clopidogrel', 'dosage': '75 mg', 'frequency': 'once daily'},
]

agent = DrugAgent()
interactions = agent.check_interactions(medications)

print(f"Medications: {[m['name'] for m in medications]}")
print(f"Interactions found: {len(interactions)}")
for i in interactions:
    print(f"  {i['drug1']} <-> {i['drug2']}: {i['severity']} - {i['description']}")
