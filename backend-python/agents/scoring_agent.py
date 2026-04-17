"""
Scoring Agent — Health Score Calculator
Calculates a composite 0-100 health score based on lab values,
anomalies, drug interactions, and data completeness.
"""


class ScoringAgent:
    """Calculates health scores and detects anomalies."""

    def detect_anomalies(self, lab_values):
        """
        Detect anomalies from lab values.
        Returns list of anomaly dicts.
        """
        anomalies = []

        for lv in lab_values:
            status = lv.get('status', 'normal')
            if status in ('high', 'low', 'critical'):
                severity = 'critical' if status == 'critical' else ('warning' if status == 'high' else 'info')
                message = self._generate_anomaly_message(lv)

                anomalies.append({
                    'parameter': lv.get('testName', 'Unknown'),
                    'value': f"{lv.get('value', '')} {lv.get('unit', '')}",
                    'severity': severity,
                    'message': message
                })

        return anomalies

    def _generate_anomaly_message(self, lv):
        """Generate a human-readable message for an anomaly."""
        test_name = lv.get('testName', 'Unknown')
        value = lv.get('value', '')
        unit = lv.get('unit', '')
        status = lv.get('status', '')
        normal_range = lv.get('normalRange', '')

        messages = {
            'critical': f"{test_name} is at a critical level ({value} {unit}). Normal range: {normal_range}. Immediate medical attention recommended.",
            'high': f"{test_name} is above normal ({value} {unit}). Normal range: {normal_range}. Consult your doctor for evaluation.",
            'low': f"{test_name} is below normal ({value} {unit}). Normal range: {normal_range}. Monitor and consult your doctor."
        }

        return messages.get(status, f"{test_name} value is {value} {unit}.")

    def calculate_score(self, lab_values, anomalies, drug_interactions, raw_text=''):
        """
        Calculate composite health score (0-100).

        Scoring breakdown:
        - Normal lab values:          40 points
        - No critical anomalies:      30 points
        - No severe drug interactions: 20 points
        - Data completeness:           10 points
        """
        score = 0

        # ─── Lab Values Score (40 points max) ─────────
        lab_score = self._score_lab_values(lab_values)
        score += lab_score

        # ─── Anomaly Score (30 points max) ────────────
        anomaly_score = self._score_anomalies(anomalies)
        score += anomaly_score

        # ─── Drug Interaction Score (20 points max) ───
        drug_score = self._score_drug_interactions(drug_interactions)
        score += drug_score

        # ─── Completeness Score (10 points max) ───────
        completeness_score = self._score_completeness(lab_values, raw_text)
        score += completeness_score

        # Ensure within bounds
        score = max(0, min(100, round(score)))

        return score

    def _score_lab_values(self, lab_values):
        """Score based on percentage of normal lab values. Max 40 points."""
        if not lab_values:
            return 20  # No data, give partial score

        total = len(lab_values)
        normal_count = sum(1 for lv in lab_values if lv.get('status') == 'normal')

        percentage_normal = normal_count / total if total > 0 else 0
        return round(percentage_normal * 40)

    def _score_anomalies(self, anomalies):
        """Score based on absence of critical anomalies. Max 30 points."""
        if not anomalies:
            return 30  # No anomalies = perfect score

        critical_count = sum(1 for a in anomalies if a.get('severity') == 'critical')
        warning_count = sum(1 for a in anomalies if a.get('severity') == 'warning')
        info_count = sum(1 for a in anomalies if a.get('severity') == 'info')

        # Deductions
        deduction = 0
        deduction += critical_count * 10  # -10 per critical
        deduction += warning_count * 4    # -4 per warning
        deduction += info_count * 2       # -2 per info

        return max(0, 30 - deduction)

    def _score_drug_interactions(self, drug_interactions):
        """Score based on absence of severe drug interactions. Max 20 points."""
        if not drug_interactions:
            return 20  # No interactions = perfect score

        severe_count = sum(1 for di in drug_interactions if di.get('severity') == 'severe')
        moderate_count = sum(1 for di in drug_interactions if di.get('severity') == 'moderate')
        mild_count = sum(1 for di in drug_interactions if di.get('severity') == 'mild')

        deduction = 0
        deduction += severe_count * 10    # -10 per severe
        deduction += moderate_count * 4   # -4 per moderate
        deduction += mild_count * 1       # -1 per mild

        return max(0, 20 - deduction)

    def _score_completeness(self, lab_values, raw_text=''):
        """Score based on completeness of extracted data. Max 10 points."""
        points = 0

        # At least some text extracted
        if raw_text and len(raw_text) > 50:
            points += 3

        # Lab values extracted
        if lab_values and len(lab_values) > 0:
            points += 3

        # Multiple lab values = more complete
        if lab_values and len(lab_values) >= 5:
            points += 2

        # Very comprehensive
        if lab_values and len(lab_values) >= 10:
            points += 2

        return min(10, points)
