"""
OpenFDA API Client — Drug labels, interactions, adverse events, active ingredients.
All drug data comes from the FDA — no hardcoded interaction database.
"""

import requests
import time


class OpenFDAClient:
    """Client for OpenFDA drug data API."""

    LABEL_URL = 'https://api.fda.gov/drug/label.json'
    EVENT_URL = 'https://api.fda.gov/drug/event.json'

    def __init__(self, api_key=''):
        self.api_key = api_key

    def _add_key(self, params):
        """Add API key to request params if available."""
        if self.api_key:
            params['api_key'] = self.api_key
        return params

    def check_interaction(self, drug1, drug2):
        """
        Check for drug-drug interaction by searching FDA drug labels.
        Returns interaction dict or None.
        """
        # Try drug1's label mentioning drug2
        interaction = self._search_label_interaction(drug1, drug2)
        if interaction:
            return interaction

        # Try reversed: drug2's label mentioning drug1
        interaction = self._search_label_interaction(drug2, drug1)
        if interaction:
            # Swap drug names for consistency
            interaction['drug1'] = drug1.title()
            interaction['drug2'] = drug2.title()
            return interaction

        return None

    def _search_label_interaction(self, primary_drug, secondary_drug):
        """Search FDA label of primary_drug for mentions of secondary_drug in interactions."""
        try:
            params = self._add_key({
                'search': f'openfda.generic_name:"{primary_drug}" AND drug_interactions:"{secondary_drug}"',
                'limit': 1
            })

            response = requests.get(self.LABEL_URL, params=params, timeout=8)

            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])

                if results:
                    interactions_text = results[0].get('drug_interactions', [''])[0]
                    if secondary_drug.lower() in interactions_text.lower():
                        severity = self._classify_severity(interactions_text)
                        desc = interactions_text[:250]
                        if len(interactions_text) > 250:
                            desc += '...'

                        return {
                            'drug1': primary_drug.title(),
                            'drug2': secondary_drug.title(),
                            'severity': severity,
                            'description': desc,
                            'source': 'openfda'
                        }

            # Also try brand name search
            params_brand = self._add_key({
                'search': f'openfda.brand_name:"{primary_drug}" AND drug_interactions:"{secondary_drug}"',
                'limit': 1
            })

            response2 = requests.get(self.LABEL_URL, params=params_brand, timeout=8)

            if response2.status_code == 200:
                data2 = response2.json()
                results2 = data2.get('results', [])

                if results2:
                    interactions_text = results2[0].get('drug_interactions', [''])[0]
                    if secondary_drug.lower() in interactions_text.lower():
                        severity = self._classify_severity(interactions_text)
                        desc = interactions_text[:250]
                        if len(interactions_text) > 250:
                            desc += '...'

                        return {
                            'drug1': primary_drug.title(),
                            'drug2': secondary_drug.title(),
                            'severity': severity,
                            'description': desc,
                            'source': 'openfda'
                        }

            time.sleep(0.1)

        except requests.exceptions.Timeout:
            pass
        except Exception as e:
            print(f"  ⚠ OpenFDA interaction check error: {e}")

        return None

    def get_drug_info(self, drug_name):
        """
        Look up comprehensive drug information from OpenFDA.
        Returns active ingredients, indications, warnings, drug class.
        """
        info = {
            'name': drug_name.title(),
            'active_ingredients': [],
            'indications': '',
            'warnings': '',
            'drug_class': '',
            'description': '',
            'adverse_reactions': '',
            'source': 'unknown'
        }

        try:
            params = self._add_key({
                'search': f'openfda.brand_name:"{drug_name}" OR openfda.generic_name:"{drug_name}"',
                'limit': 1
            })

            response = requests.get(self.LABEL_URL, params=params, timeout=8)

            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])

                if results:
                    result = results[0]
                    openfda = result.get('openfda', {})

                    # Active ingredients
                    ingredients = openfda.get('substance_name', [])
                    if not ingredients:
                        ingredients = openfda.get('generic_name', [])
                    info['active_ingredients'] = ingredients[:5]

                    # Drug class
                    pharm_class = openfda.get('pharm_class_epc', [])
                    if pharm_class:
                        info['drug_class'] = pharm_class[0]

                    # Indications
                    indications = result.get('indications_and_usage', [''])
                    if indications and indications[0]:
                        text = indications[0]
                        info['indications'] = text[:400] + ('...' if len(text) > 400 else '')

                    # Warnings
                    warnings = result.get('warnings', [''])
                    if warnings and warnings[0]:
                        text = warnings[0]
                        info['warnings'] = text[:300] + ('...' if len(text) > 300 else '')

                    # Description
                    description = result.get('description', [''])
                    if description and description[0]:
                        text = description[0]
                        info['description'] = text[:300] + ('...' if len(text) > 300 else '')

                    # Adverse reactions
                    adverse = result.get('adverse_reactions', [''])
                    if adverse and adverse[0]:
                        text = adverse[0]
                        info['adverse_reactions'] = text[:300] + ('...' if len(text) > 300 else '')

                    info['source'] = 'openfda'

            time.sleep(0.1)

        except requests.exceptions.Timeout:
            print(f"  ⚠ OpenFDA timeout for '{drug_name}'")
        except Exception as e:
            print(f"  ⚠ OpenFDA drug info error for '{drug_name}': {e}")

        return info

    def _classify_severity(self, text):
        """Classify interaction severity from FDA label text."""
        text_lower = text.lower()
        if any(w in text_lower for w in ['contraindicated', 'fatal', 'death', 'do not use',
                                          'never', 'life-threatening', 'serious']):
            return 'severe'
        elif any(w in text_lower for w in ['caution', 'monitor', 'adjust', 'risk', 'may increase',
                                            'may decrease', 'should be', 'carefully']):
            return 'moderate'
        return 'mild'
