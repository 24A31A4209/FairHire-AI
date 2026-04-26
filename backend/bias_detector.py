"""
AI-Powered Fair Hiring — Bias Detection Module
Identifies and redacts demographic/prestige markers to ensure merit-based ranking.
"""

import re

class BiasDetector:
    """
    Identifies biased fields in a resume and produces a
    cleaned version for fair candidate ranking.
    """

    # ── Gender indicators ────────────────────────────────────────────────────
    GENDER_PATTERNS = [
        r'\b(he|she|him|her|his|hers|himself|herself)\b',
        r'\b(male|female|man|woman|boy|girl)\b',
        r'\b(mr\.?|mrs\.?|ms\.?|miss|sir|madam)\b',
        r'\b(gentleman|lady|mother|father|son|daughter)\b',
    ]

    # ── Prestigious / branded institution names ──────────────────────────────
    # Expanded for both Global and Indian hackathon contexts
    ELITE_COLLEGES = [
        # Indian Institutes
        r'\bIIT\b', r'\bIIM\b', r'\bBITS\s*Pilani\b', r'\bNIT\b', r'\bIIS[cC]\b', 
        r'\bVIT\b', r'\bSRM\b', r'\bManipal\b', r'\bBITS\b', r'\bIIIT\b',
        # Global Institutes
        r'\bMIT\b', r'\bStanford\b', r'\bHarvard\b', r'\bYale\b', r'\bPrinceton\b', 
        r'\bCarnegie\s*Mellon\b', r'\bCaltech\b', r'\bUC\s*Berkeley\b', r'\bCornell\b',
        r'\bOxford\b', r'\bCambridge\b', r'\bImperial\s*College\b',
        # Structural Patterns
        r'\bUniversity\s+of\s+[A-Z][a-z]+\b',
        r'\b[A-Z][a-z]+\s+University\b',
        r'\b[A-Z][a-z]+\s+Institute\s+of\s+[A-Z][a-z]+\b',
    ]

    # ── Location indicators ───────────────────────────────────────────────────
    LOCATION_PATTERNS = [
        # Address patterns (e.g., 123 Street Name)
        r'\b\d{1,4}[,\s]+[A-Z][a-z]+\s*(Street|Road|Avenue|Lane|Nagar|Colony|Sector)\b',
        # City List (Expanded)
        r'\b(Mumbai|Delhi|Bangalore|Bengaluru|Hyderabad|Secunderabad|Chennai|Kolkata|Pune|'
        r'Ahmedabad|Jaipur|Lucknow|Kanpur|Nagpur|Bhopal|Indore|Chandigarh|Gurgaon|Noida|'
        r'New\s*York|London|San\s*Francisco|Seattle|Austin|Boston|Singapore|Dubai)\b',
        # States
        r'\b(Telangana|Maharashtra|Karnataka|Tamil\s*Nadu|Andhra\s*Pradesh|'
        r'Uttar\s*Pradesh|West\s*Bengal|Gujarat|Rajasthan|Punjab|California|Texas|NY)\b',
    ]

    def detect_bias(self, raw_text: str, parsed_data: dict) -> dict:
        flags = []
        text_lines = [l.strip() for l in raw_text.split("\n") if l.strip()]

        # 1. Detect candidate name
        detected_name = self._detect_name(raw_text, text_lines)
        if detected_name:
            flags.append({
                "type": "name",
                "value": detected_name,
                "context": f"Candidate name identified: '{detected_name}'",
                "risk": "Names can trigger unconscious bias regarding ethnicity, religion, or gender.",
            })

        # 2. Detect gender markers
        for pattern in self.GENDER_PATTERNS:
            matches = re.findall(pattern, raw_text, re.IGNORECASE)
            for match in set(matches):
                if isinstance(match, tuple): match = match[0]
                flags.append({
                    "type": "gender",
                    "value": match,
                    "context": f"Gendered language: '{match}'",
                    "risk": "Gendered pronouns or titles can skew AI and human evaluation.",
                })

        # 3. Detect institution/college prestige
        for pattern in self.ELITE_COLLEGES:
            matches = re.findall(pattern, raw_text, re.IGNORECASE)
            for match in set(matches):
                flags.append({
                    "type": "college",
                    "value": match,
                    "context": f"Elite institution: '{match}'",
                    "risk": "Institutional prestige often masks actual skill competency.",
                })

        # 4. Detect location
        for pattern in self.LOCATION_PATTERNS:
            matches = re.findall(pattern, raw_text, re.IGNORECASE)
            for match in set(matches[:3]):
                if isinstance(match, tuple): match = match[0]
                flags.append({
                    "type": "location",
                    "value": match,
                    "context": f"Location marker: '{match}'",
                    "risk": "Geographic location can lead to socioeconomic or regional filtering.",
                })

        # De-duplicate
        unique_flags = []
        seen = set()
        for f in flags:
            key = (f["type"], f["value"].lower())
            if key not in seen:
                seen.add(key)
                unique_flags.append(f)

        return {
            "detected_name": detected_name or "Unknown",
            "bias_flags": unique_flags,
            "bias_score": min(100, len(unique_flags) * 12),
            "bias_categories": list(set(f["type"] for f in unique_flags)),
        }

    def remove_bias(self, raw_text: str, bias_report: dict) -> str:
        """Produces a 'blind' version of the resume."""
        clean = raw_text

        # 1. Redact Name
        name = bias_report.get("detected_name", "")
        if name and name != "Unknown":
            # Use escape to ensure names with special chars don't break regex
            clean = re.sub(re.escape(name), "[NAME REDACTED]", clean, flags=re.IGNORECASE)

        # 2. Redact Gender
        for pattern in self.GENDER_PATTERNS:
            clean = re.sub(pattern, "[GENDER REDACTED]", clean, flags=re.IGNORECASE)

        # 3. Redact Institutions
        for pattern in self.ELITE_COLLEGES:
            clean = re.sub(pattern, "[INSTITUTION REDACTED]", clean, flags=re.IGNORECASE)

        # 4. Redact Locations
        for pattern in self.LOCATION_PATTERNS:
            clean = re.sub(pattern, "[LOCATION REDACTED]", clean, flags=re.IGNORECASE)

        # 5. Redact PII (Email/Phone)
        clean = re.sub(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}', '[EMAIL REDACTED]', clean)
        clean = re.sub(r'[\+]?[\d\s\-\(\)]{10,15}', '[PHONE REDACTED]', clean)

        return clean

    def _detect_name(self, raw_text: str, lines: list) -> str:
        """Enhanced name detection logic."""
        # Common headers to ignore when looking for a name
        ignore_list = ["resume", "curriculum vitae", "cv", "page", "contact"]
        
        # Check top of the document
        for line in lines[:8]:
            clean_line = line.strip()
            if not clean_line or clean_line.lower() in ignore_list:
                continue
            
            # Look for 2-3 capitalized words (Typical name structure)
            if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}$', clean_line):
                # Ensure it's not actually a college name we have in our list
                if not any(re.search(p, clean_line, re.I) for p in self.ELITE_COLLEGES):
                    return clean_line

        # Fallback: Explicit labels
        match = re.search(r'(?:Name|Applicant|Candidate)\s*[:\-]\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})', 
                          raw_text, re.I)
        return match.group(1).strip() if match else ""