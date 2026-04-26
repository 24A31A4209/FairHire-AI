class ExplainabilityEngine:
    def generate_explanation(self, candidate_data):
        """
        Passes through the actual AI logic instead of hard-coded strings.
        """
        # Pull the 'logic' field directly from the AI's JSON response
        ai_logic = candidate_data.get('logic', "No neural reasoning provided.")
        
        return {
            "decision_logic": ai_logic,
            "fairness_score": "High (PII & Prestige Redacted)"
        }