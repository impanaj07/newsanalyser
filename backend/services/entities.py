from collections import Counter
from config import nlp

def extract_entities(results: list[dict]):
    RELEVANT_LABELS = {"PERSON", "ORG", "GPE", "EVENT"}

    all_entities = []

    for r in results:
        doc = nlp(r["headline"])
        entities = []

        for ent in doc.ents:
            if ent.label_ in RELEVANT_LABELS:
                entities.append({
                    "text": ent.text,
                    "label": ent.label_,
                })
                all_entities.append(ent.text)

        r["entities"] = entities

    entity_counts = Counter(all_entities)
    return results, entity_counts