"""
Scoring Agent — Health score calculation + anomaly detection
Uses Gemini AI for intelligent scoring. No hardcoded scoring rules.
"""


class ScoringAgent:
    """Calculates health scores and detects anomalies using Gemini AI."""

    def __init__(self, gemini_client=None):
        """
        Args:
            gemini_client: GeminiClient instance for AI-based scoring
        """
        self.gemini_client = gemini_client

    def detect_anomalies(self, lab_values):
        """
        Detect anomalies from lab values.
        Lab value status (normal/high/low/critical) is already determined by Gemini AI
        in the NLP agent, so we just collect the abnormal ones.
        """
        anomalies = []

        for lv in lab_values:
            status = lv.get('status', 'normal')
            if status in ('high', 'low', 'critical'):
                severity = 'critical' if status == 'critical' else 'warning'
                anomalies.append({
                    'parameter': lv.get('testName', 'Unknown'),
                    'value': f"{lv.get('value', '?')} {lv.get('unit', '')}",
                    'severity': severity,
                    'message': self._build_anomaly_message(lv)
                })

        return anomalies

    def _build_anomaly_message(self, lv):
        """Build a descriptive anomaly message."""
        name = lv.get('testName', 'Parameter')
        value = lv.get('value', '?')
        unit = lv.get('unit', '')
        status = lv.get('status', 'abnormal')
        normal_range = lv.get('normalRange', '')

        if status == 'critical':
            msg = f"{name} is critically {'elevated' if status != 'low' else 'low'} at {value} {unit}."
        elif status == 'high':
            msg = f"{name} is elevated at {value} {unit}."
        elif status == 'low':
            msg = f"{name} is below normal at {value} {unit}."
        else:
            msg = f"{name} is {status} at {value} {unit}."

        if normal_range:
            msg += f" Normal range: {normal_range}."
        msg += " Please consult your doctor."

        return msg

    def calculate_score(self, lab_values=None, anomalies=None, drug_interactions=None, raw_text=''):
        """
        Calculate health score using Gemini AI.
        Falls back to simple calculation if Gemini is unavailable.
        """
        lab_values = lab_values or []
        anomalies = anomalies or []
        drug_interactions = drug_interactions or []

        # Try Gemini-based scoring
        if self.gemini_client:
            try:
                medications = []  # Already extracted separately
                diseases = []
                score = self.gemini_client.calculate_health_score(
                    lab_values=lab_values,
                    medications=medications,
                    diseases=diseases,
                    drug_interactions=drug_interactions,
                    anomalies=anomalies
                )
                return score
            except Exception as e:
                print(f"  ⚠ Gemini scoring failed: {e}, using fallback")

        # Fallback: simple math (no hardcoded medical data)
        return self._fallback_score(lab_values, anomalies, drug_interactions)

    def _fallback_score(self, lab_values, anomalies, drug_interactions):
        """Simple fallback scoring — no hardcoded medical data."""
        score = 85

        if not lab_values:
            return 50  # Can't score without data

        total = len(lab_values)
        abnormal = len([lv for lv in lab_values if lv.get('status') in ('high', 'low')])
        critical = len([lv for lv in lab_values if lv.get('status') == 'critical'])

        if total > 0:
            normal_ratio = (total - abnormal - critical) / total
            score = int(normal_ratio * 80) + 10  # Base 10, max 90

        # Deductions for critical findings
        score -= critical * 12
        score -= len(drug_interactions) * 6
        severe = len([di for di in drug_interactions if di.get('severity') == 'severe'])
        score -= severe * 8

        return max(0, min(100, score))
