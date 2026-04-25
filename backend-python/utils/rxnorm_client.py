"""
RxNorm API Client — Drug name normalization via NIH/NLM
Maps brand names → generic names → standard RxCUI codes.
Free API, no key needed. Rate limit: 20 req/sec.
"""

import requests
import time

# In-memory cache to avoid repeated API calls
_rxnorm_cache = {}


class RxNormClient:
    """Drug name normalization using the NLM RxNorm API."""

    BASE_URL = 'https://rxnav.nlm.nih.gov/REST'

    def normalize_drug_name(self, drug_name):
        """
        Normalize a drug name to its standard generic name using RxNorm.
        Returns dict with: generic_name, rxcui, brand_names, drug_class
        """
        if not drug_name or len(drug_name.strip()) < 2:
            return {'generic_name': drug_name, 'rxcui': None, 'source': 'input'}

        drug_key = drug_name.strip().lower()

        # Check cache
        if drug_key in _rxnorm_cache:
            return _rxnorm_cache[drug_key]

        result = {
            'original_name': drug_name.strip(),
            'generic_name': drug_name.strip().title(),
            'rxcui': None,
            'brand_names': [],
            'drug_class': '',
            'source': 'input'
        }

        try:
            # Step 1: Find RxCUI by drug name (approximate match)
            rxcui = self._find_rxcui(drug_name)
            if not rxcui:
                _rxnorm_cache[drug_key] = result
                return result

            result['rxcui'] = rxcui
            result['source'] = 'rxnorm'

            # Step 2: Get properties (generic name)
            props = self._get_properties(rxcui)
            if props:
                result['generic_name'] = props.get('name', drug_name).title()

            # Step 3: Get related brand names
            brands = self._get_related_brands(rxcui)
            if brands:
                result['brand_names'] = brands[:5]

            # Rate limit respect
            time.sleep(0.05)

        except Exception as e:
            print(f"  ⚠ RxNorm error for '{drug_name}': {e}")

        _rxnorm_cache[drug_key] = result
        return result

    def _find_rxcui(self, drug_name):
        """Find RxCUI for a drug name using approximate match."""
        try:
            # Try exact match first
            url = f"{self.BASE_URL}/rxcui.json"
            params = {'name': drug_name.strip(), 'search': 2}  # search=2 for normalized match
            response = requests.get(url, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()
                id_group = data.get('idGroup', {})
                rxnorm_ids = id_group.get('rxnormId', [])
                if rxnorm_ids:
                    return rxnorm_ids[0]

            # Try approximate match
            url_approx = f"{self.BASE_URL}/approximateTerm.json"
            params_approx = {'term': drug_name.strip(), 'maxEntries': 1}
            response2 = requests.get(url_approx, params=params_approx, timeout=5)

            if response2.status_code == 200:
                data2 = response2.json()
                candidates = data2.get('approximateGroup', {}).get('candidate', [])
                if candidates:
                    return candidates[0].get('rxcui')

        except requests.exceptions.Timeout:
            pass
        except Exception:
            pass

        return None

    def _get_properties(self, rxcui):
        """Get drug properties by RxCUI."""
        try:
            url = f"{self.BASE_URL}/rxcui/{rxcui}/properties.json"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('properties', {})
        except Exception:
            pass
        return None

    def _get_related_brands(self, rxcui):
        """Get related brand names for a drug RxCUI."""
        try:
            url = f"{self.BASE_URL}/rxcui/{rxcui}/related.json"
            params = {'tty': 'BN'}  # BN = Brand Name
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                groups = data.get('relatedGroup', {}).get('conceptGroup', [])
                brands = []
                for group in groups:
                    for prop in group.get('conceptProperties', []):
                        brands.append(prop.get('name', ''))
                return brands
        except Exception:
            pass
        return []
