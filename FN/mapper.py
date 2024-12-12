import json
import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import framenet as fn
import spacy
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import os
import re

# Scaricare i dataset richiesti
# nltk.download('framenet_v17')
# nltk.download('wordnet')
# nltk.download('punkt')
# nltk.download('stopwords')

def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    words = [word for word in tokens if word.isalpha()]
    return set(words) - set(stopwords.words('english'))

def find_synsets(word, nlp, pos=None):
    """
    Trova il synset di WordNet per una parola, calcolando il contesto.
    """
    words = re.split('[ _-]', word)
    if len(words) > 1:
        for conj in [' ', '_', '-', '']:
            synset = wn.synsets(conj.join(words), pos=pos)
            if synset:
                return synset
            
        reggente = find_reggente(' '.join(words), nlp)
        return wn.synsets(reggente, pos=pos)
    else:
        return wn.synsets(words[0], pos=pos)
    

def find_reggente(text, nlp):
    tokens = nlp(text)
    for token in tokens:
        if token.dep_ == "ROOT":
            return token.text
    return None

def get_synsets_with_descriptions(word, nlp, pos=None):
    """
    Trova tutti i synset per una parola e restituisce una lista di tuple (index, synset, descrizione).
    """
    synsets = find_synsets(word, nlp, pos=pos)
    return [(i, synset, f"{synset.name()}: {synset.definition()}") for i, synset in enumerate(synsets)]

def interactive_mapping(frame, nlp):
    """
    Mostra un'interfaccia interattiva per mappare titolo, FEs e LUs di un frame a synset di WordNet.
    """
    mapping = {"title": None, "FEs": {}, "LUs": {}}

    # Mappare il titolo del frame
    print(f"\nFrame: {frame.name}")
    print(f"Definition: {frame.definition}")
    title_synsets = get_synsets_with_descriptions(frame.name, nlp)
    for idx, synset, desc in title_synsets:
        print(f"{idx}: {desc}")
    title_choice = input("Choose synset for title (or press Enter to skip): ")
    if title_choice.isdigit():
        mapping["title"] = title_synsets[int(title_choice)][1].name()  # Salva come stringa

    # Mappare FEs
    for fe_name, fe in frame.FE.items():
        print(f"\nFrame Element: {fe_name}")
        print(f"Definition: {fe.definition}")
        fe_synsets = get_synsets_with_descriptions(fe_name, nlp)
        for idx, synset, desc in fe_synsets:
            print(f"{idx}: {desc}")
        fe_choice = input(f"Choose synset for FE '{fe_name}' (or press Enter to skip): ")
        if fe_choice.isdigit():
            mapping["FEs"][fe_name] = fe_synsets[int(fe_choice)][1].name()  # Salva come stringa

    # Mappare LUs
    for lu_name in frame.lexUnit:
        print(f"\nLexical Unit: {lu_name}")
        print(f"Definition: {frame.lexUnit[lu_name].definition}")
        lu_name_cleaned, pos = lu_name.split(".")
        if pos not in [wn.NOUN, wn.VERB, wn.ADJ, wn.ADV]:
            pos = None
        lu_synsets = get_synsets_with_descriptions(lu_name_cleaned, nlp, pos=pos)
        for idx, synset, desc in lu_synsets:
            print(f"{idx}: {desc}")
        lu_choice = input(f"Choose synset for LU '{lu_name}' (or press Enter to skip): ")
        if lu_choice.isdigit():
            mapping["LUs"][lu_name] = lu_synsets[int(lu_choice)][1].name()  # Salva come stringa

    return mapping

def save_mapping_to_file(filename, mappings):
    with open(filename, 'w') as f:
        json.dump(mappings, f, indent=2)

def load_mapping_from_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        # Convertire le stringhe Synset in oggetti Synset
        for frame_name in data:
            if data[frame_name]["title"]:
                data[frame_name]["title"] = wn.synset(data[frame_name]["title"])
            for fe_name in data[frame_name]["FEs"]:
                if data[frame_name]["FEs"][fe_name]:
                    data[frame_name]["FEs"][fe_name] = wn.synset(data[frame_name]["FEs"][fe_name])
            for lu_name in data[frame_name]["LUs"]:
                if data[frame_name]["LUs"][lu_name]:
                    data[frame_name]["LUs"][lu_name] = wn.synset(data[frame_name]["LUs"][lu_name])
        return data
    return {}

def main():
    nlp = spacy.load('en_core_web_sm')
    output_file = "mappings_by_hand.json"
    existing_mappings = load_mapping_from_file(output_file)

    # Frame set di esempio (sostituire con i propri dati)
    frame_set = {'Part_piece': 142, 'Spatial_co-location': 2905, 'Mental_stimulus_stimulus_focus': 2046, 'Reasoning': 308, 'Avoiding': 274}


    for frame_name, frame_id in frame_set.items():
        if frame_name in existing_mappings:
            print(f"Frame '{frame_name}' already mapped. Skipping.")
            continue

        frame = fn.frame(frame_id)
        mapping = interactive_mapping(frame, nlp)
        existing_mappings[frame_name] = mapping

        save_mapping_to_file(output_file, existing_mappings)
        print(f"Mapping for frame '{frame_name}' saved.")

    print("\nAll frames mapped. Results saved to", output_file)

if __name__ == "__main__":
    main()
