import re
import spacy
import os

# Auto-download the model if it is missing
try:
    nlp = spacy.load("en_core_web_sm")
except:
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def clean_and_anonymize(text):
    """
    Removes Names and Locations but keeps Dates for experience calculation.
    """
    doc = nlp(text)
    anonymized = text
    
    # Redact Names (PERSON) and Cities/Countries (GPE)
    # Keeping DATE is vital for AI ranking logic.
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "GPE"]:
            anonymized = anonymized.replace(ent.text, "[REDACTED]")
    
    # Redact Emails & Phone Numbers
    anonymized = re.sub(r'\S+@\S+', '[EMAIL REDACTED]', anonymized)
    anonymized = re.sub(r'\b\d{10,12}\b', '[PHONE REDACTED]', anonymized)
    
    return anonymized