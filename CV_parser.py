import spacy
from collections import Counter

nlp = spacy.load("en_core_web_sm")

def extract_name_from_text(cv_text):
    doc = nlp(cv_text)
    
    # Extract all PERSON entities
    person_entities = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    
    # Heuristic: Most likely name appears early and is repeated least
    if person_entities:
        # Count frequency and prioritize first few lines
        top_lines = cv_text.split('\n')[:10]
        top_text = ' '.join(top_lines)
        top_doc = nlp(top_text)
        top_names = [ent.text for ent in top_doc.ents if ent.label_ == "PERSON"]
        
        # Prefer top_names if available
        if top_names:
            return top_names[0]
        else:
            # Fallback to least frequent name
            name_counts = Counter(person_entities)
            return min(name_counts, key=name_counts.get)
    
    return None