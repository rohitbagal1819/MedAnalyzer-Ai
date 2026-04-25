"""
Drug Agent — Drug interaction checking using OpenFDA API + RxNorm normalization
NO hardcoded interaction database. ALL data from live APIs.
"""

import itertools


class DrugAgent:
    """Checks drug interactions via OpenFDA + RxNorm APIs. Zero hardcoded data."""

    def __init__(self, openfda_client=None, rxnorm_client=None):
        """
        Args:
            openfda_client: OpenFDAClient instance
            rxnorm_client: RxNormClient instance for drug name normalization
        """
        self.openfda = openfda_client
        self.rxnorm = rxnorm_client

    def check_interactions(self, medications):
        """
        Check all medication pairs for drug interactions using OpenFDA.
        No hardcoded interactions — all data from FDA drug labels.

        Args:
            medications: List of dicts with 'name' key
        Returns:
            List of interaction dicts with drug1, drug2, severity, description, source
        """
        if not medications or len(medications) < 2:
            return []

        if not self.openfda:
            print("  ⚠ No OpenFDA client — cannot check interactions")
            return []

        # Get unique drug names
        drug_names = list(set(
            med['name'].strip().lower()
            for med in medications
            if med.get('name') and len(med['name'].strip()) >= 3
        ))

        if len(drug_names) < 2:
            return []

        # Normalize drug names via RxNorm (if available)
        normalized_names = {}
        if self.rxnorm:
            for name in drug_names:
                rxinfo = self.rxnorm.normalize_drug_name(name)
                normalized_names[name] = rxinfo.get('generic_name', name).lower()
                if normalized_names[name] != name:
                    print(f"    RxNorm: {name} → {normalized_names[name]}")
        else:
            for name in drug_names:
                normalized_names[name] = name

        interactions = []

        # Check all pairs using both original and normalized names
        for drug1, drug2 in itertools.combinations(drug_names, 2):
            interaction = self._check_pair(drug1, drug2, normalized_names)
            if interaction:
                interactions.append(interaction)

        return interactions

    def _check_pair(self, drug1, drug2, normalized_names):
        """Check a pair of drugs for interactions via OpenFDA."""
        # Try with original names first
        interaction = self.openfda.check_interaction(drug1, drug2)
        if interaction:
            return interaction

        # Try with normalized (generic) names
        generic1 = normalized_names.get(drug1, drug1)
        generic2 = normalized_names.get(drug2, drug2)

        if generic1 != drug1 or generic2 != drug2:
            interaction = self.openfda.check_interaction(generic1, generic2)
            if interaction:
                return interaction

        return None

    def lookup_drug_info(self, medications):
        """
        Look up drug content/composition from OpenFDA + RxNorm for each medication.
        Returns list of dicts with drug details.
        """
        drug_info_list = []

        for med in medications:
            name = med.get('name', '').strip()
            if not name or len(name) < 3:
                continue

            info = {
                'name': name,
                'generic_name': name,
                'active_ingredients': [],
                'indications': '',
                'warnings': '',
                'drug_class': '',
                'description': '',
                'brand_names': [],
                'rxcui': None,
                'source': 'unknown'
            }

            # Step 1: Normalize via RxNorm
            if self.rxnorm:
                try:
                    rxinfo = self.rxnorm.normalize_drug_name(name)
                    info['generic_name'] = rxinfo.get('generic_name', name)
                    info['rxcui'] = rxinfo.get('rxcui')
                    info['brand_names'] = rxinfo.get('brand_names', [])
                    if rxinfo.get('source') == 'rxnorm':
                        info['source'] = 'rxnorm'
                except Exception as e:
                    print(f"  ⚠ RxNorm lookup error for {name}: {e}")

            # Step 2: Get detailed info from OpenFDA
            if self.openfda:
                try:
                    # Try with generic name first (more likely to find in FDA)
                    search_name = info['generic_name'] if info['generic_name'] != name else name
                    fda_info = self.openfda.get_drug_info(search_name)

                    if fda_info.get('source') == 'openfda':
                        info['active_ingredients'] = fda_info.get('active_ingredients', [])
                        info['indications'] = fda_info.get('indications', '')
                        info['warnings'] = fda_info.get('warnings', '')
                        info['drug_class'] = fda_info.get('drug_class', '')
                        info['description'] = fda_info.get('description', '')
                        info['source'] = 'openfda'
                    elif fda_info.get('source') == 'unknown' and name != search_name:
                        # Retry with original name
                        fda_info2 = self.openfda.get_drug_info(name)
                        if fda_info2.get('source') == 'openfda':
                            info['active_ingredients'] = fda_info2.get('active_ingredients', [])
                            info['indications'] = fda_info2.get('indications', '')
                            info['warnings'] = fda_info2.get('warnings', '')
                            info['drug_class'] = fda_info2.get('drug_class', '')
                            info['description'] = fda_info2.get('description', '')
                            info['source'] = 'openfda'
                except Exception as e:
                    print(f"  ⚠ OpenFDA lookup error for {name}: {e}")

            drug_info_list.append(info)

        return drug_info_list
