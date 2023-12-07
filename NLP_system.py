import spacy

# Load English NER model from spaCy
nlp = spacy.load("en_core_web_lg")

def extract_age(entities):
    age = None
    for entity in entities:
        if entity.label_ == "DATE" and "years" in entity.text.lower():
            age_text = ''.join(filter(str.isdigit, entity.text))
            age = int(age_text) if age_text.isdigit() else None
            break  # Stop at the first age-like entity found
    return age

def extract_user_and_parent_info(sentence):
    doc = nlp(sentence)
    user_info = {}
    parent_info = {}
    
    # Process entities for user and parent info
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            if ent.root.dep_ == "nsubj" or ent.root.dep_ == "attr":
                user_info['name'] = ent.text
            elif ent.root.dep_ == "poss":
                parent_info['name'] = ent.text
    
    # Extract user's age
    user_info['age'] = extract_age(doc.ents)

    # Extract parent's age (if mentioned)
    if "dad" in sentence.lower() or "father" in sentence.lower():
        parent_info['age'] = extract_age(doc.ents)

    return user_info, parent_info

# Example sentence
user_sentence = "Hello, I'm Sam Siavoshian, and my dad is 40 years old."

# Extract user and parent information
user_info, parent_info = extract_user_and_parent_info(user_sentence)

# Print extracted information
if user_info:
    print("User's Information:")
    for key, value in user_info.items():
        print(f"{key.capitalize()}: {value}")
else:
    print("No user information found.")

if parent_info:
    print("\nParent's Information:")
    for key, value in parent_info.items():
        print(f"{key.capitalize()}: {value}")
else:
    print("No parent information found.")
