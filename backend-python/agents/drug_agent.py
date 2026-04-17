"""
Drug Agent — Drug interaction checker using OpenFDA API
Cross-checks medication pairs for known interactions.
"""

import requests
import time
import itertools


class DrugAgent:
    """Checks drug interactions via OpenFDA API."""

    OPENFDA_URL = 'https://api.fda.gov/drug/label.json'

    # Known common interactions (fallback database)
    KNOWN_INTERACTIONS = {
        ('metformin', 'aspirin'): {
            'severity': 'mild',
            'description': 'Aspirin may slightly enhance the blood sugar-lowering effect of Metformin. Monitor blood glucose levels.'
        },
        ('metformin', 'atorvastatin'): {
            'severity': 'mild',
            'description': 'Atorvastatin may slightly increase Metformin levels. Generally safe, monitor if symptoms occur.'
        },
        ('aspirin', 'warfarin'): {
            'severity': 'severe',
            'description': 'Concurrent use increases risk of bleeding significantly. Avoid combination unless directed by physician.'
        },
        ('aspirin', 'ibuprofen'): {
            'severity': 'moderate',
            'description': 'Ibuprofen may reduce the cardioprotective effect of Aspirin. Separate dosing by at least 2 hours.'
        },
        ('atorvastatin', 'amiodarone'): {
            'severity': 'severe',
            'description': 'Increased risk of rhabdomyolysis. Atorvastatin dose should not exceed 40mg daily with Amiodarone.'
        },
        ('levothyroxine', 'metformin'): {
            'severity': 'mild',
            'description': 'Metformin may reduce TSH levels. Monitor thyroid function periodically.'
        },
        ('levothyroxine', 'calcium'): {
            'severity': 'moderate',
            'description': 'Calcium supplements reduce absorption of Levothyroxine. Take them at least 4 hours apart.'
        },
        ('metformin', 'alcohol'): {
            'severity': 'severe',
            'description': 'Alcohol increases the risk of lactic acidosis with Metformin. Avoid excessive alcohol consumption.'
        },
        ('amlodipine', 'atorvastatin'): {
            'severity': 'moderate',
            'description': 'Amlodipine may increase Atorvastatin plasma levels. Limit Atorvastatin dose to 20mg daily.'
        },
        ('lisinopril', 'potassium'): {
            'severity': 'moderate',
            'description': 'ACE inhibitors can increase potassium levels. Monitor serum potassium regularly.'
        },
        ('omeprazole', 'clopidogrel'): {
            'severity': 'severe',
            'description': 'Omeprazole significantly reduces the antiplatelet effect of Clopidogrel. Use alternative PPI.'
        },
    }

    def check_interactions(self, medications):
        """
        Check all medication pairs for drug interactions.
        Args:
            medications: List of dicts with 'name' key
        Returns:
            List of interaction dicts with drug1, drug2, severity, description
        """
        if not medications or len(medications) < 2:
            return []

        drug_names = [med['name'].strip().lower() for med in medications if med.get('name')]
        drug_names = list(set(drug_names))  # Deduplicate

        interactions = []

        # Check all pairs
        for drug1, drug2 in itertools.combinations(drug_names, 2):
            interaction = self._check_pair(drug1, drug2)
            if interaction:
                interactions.append(interaction)

        return interactions

    def _check_pair(self, drug1, drug2):
        """Check a pair of drugs for interactions."""
        # Check local database first
        key1 = (drug1.lower(), drug2.lower())
        key2 = (drug2.lower(), drug1.lower())

        if key1 in self.KNOWN_INTERACTIONS:
            info = self.KNOWN_INTERACTIONS[key1]
            return {
                'drug1': drug1.title(),
                'drug2': drug2.title(),
                'severity': info['severity'],
                'description': info['description']
            }
        elif key2 in self.KNOWN_INTERACTIONS:
            info = self.KNOWN_INTERACTIONS[key2]
            return {
                'drug1': drug1.title(),
                'drug2': drug2.title(),
                'severity': info['severity'],
                'description': info['description']
            }

        # Try OpenFDA API
        try:
            interaction = self._check_openfda(drug1, drug2)
            if interaction:
                return interaction
        except Exception as e:
            print(f"  ⚠ OpenFDA API error for {drug1} + {drug2}: {e}")

        return None

    def _check_openfda(self, drug1, drug2):
        """Query OpenFDA API for drug interaction information."""
        try:
            # Search for drug1 label mentioning drug2
            params = {
                'search': f'openfda.generic_name:"{drug1}" AND drug_interactions:"{drug2}"',
                'limit': 1
            }

            response = requests.get(self.OPENFDA_URL, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])

                if results:
                    interactions_text = results[0].get('drug_interactions', [''])[0]
                    if drug2.lower() in interactions_text.lower():
                        # Determine severity based on keywords
                        severity = 'mild'
                        text_lower = interactions_text.lower()
                        if any(w in text_lower for w in ['contraindicated', 'fatal', 'death', 'avoid']):
                            severity = 'severe'
                        elif any(w in text_lower for w in ['caution', 'monitor', 'adjust', 'risk']):
                            severity = 'moderate'

                        # Truncate description
                        desc = interactions_text[:200]
                        if len(interactions_text) > 200:
                            desc += '...'

                        return {
                            'drug1': drug1.title(),
                            'drug2': drug2.title(),
                            'severity': severity,
                            'description': desc
                        }

            # Small delay to respect rate limits
            time.sleep(0.1)

        except requests.exceptions.Timeout:
            pass
        except Exception:
            pass

        return None
