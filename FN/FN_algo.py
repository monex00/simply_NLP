import nltk
from nltk.corpus import framenet as fn
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
import json
import os

import spacy
from pprint import pprint


# Scaricare i dataset richiesti
# nltk.download('framenet_v17')
# nltk.download('wordnet')
# nltk.download('stopwords')
# nltk.download('punkt')


def preprocess_text(text):
    """
    Pre-elaborazione di un testo: rimuove stopwords, tokenizza, filtra solo parole alfabetiche.
    """
    tokens = word_tokenize(text.lower())
    words = [word for word in tokens if word.isalpha()]
    return set(words) - set(stopwords.words('english'))

def ctx_s(synset, depth=0):
    """
    Calcola il contesto di un synset, includendo definizione, esempi, e opzionalmente iperonimi/iponimi.
    """
    context = preprocess_text(synset.definition())
    context.update(preprocess_text(" ".join(synset.examples())))
    if depth > 0:
        for related in synset.hypernyms() + synset.hyponyms():
            context.update(ctx_s(related, depth - 1))
    return context

def ctx_w(frame, type, word):
    """
    Calcola il contesto di un frame utilizzando definizione, FEs, e LUs.
    """
    if (type == "title"):
        return preprocess_text(frame.definition)
    elif (type == "FE"):
        return preprocess_text(frame.FE[word].definition)
    elif (type == "LU"):
        return preprocess_text(frame.lexUnit[word].definition)


def calculate_bow_score(s, w, frame, type):
    """
    Calcola lo score tra un synset e un frame, utilizzando il modello bag-of-words.
    """
    synset_context = ctx_s(s, depth=0) # Profondità opzionale
    frame_context = ctx_w(frame, type, w)
    return len(synset_context.intersection(frame_context)) + 1


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


def _eq(obj1, obj2):
    if (obj1 is None and obj2 is not None) or (obj1 is not None and obj2 is None):
        return False
    if obj1 is None and obj2 is None:
        return True
    return obj1 == obj2

def accuracy_score(mappings1, mappings2):
    corrects, count = 0, 0
    for frame_name in mappings1:

        corrects += (mappings1[frame_name]['title'] == mappings2[frame_name]['title']) +\
                    sum(_eq(mappings1[frame_name]['FEs'][fe], mappings2[frame_name]['FEs'][fe]) for fe in mappings1[frame_name]['FEs']) +\
                    sum(_eq(mappings1[frame_name]['LUs'][lu], mappings2[frame_name]['LUs'][lu]) for lu in mappings1[frame_name]['LUs'])
        count += 1 + len(mappings2[frame_name]['FEs']) + len(mappings2[frame_name]['LUs'])

    return corrects / count


def map_frame_to_synsets(frame, nlp):
    """
    Mappa il frame a synset di WordNet, calcolando lo score bag-of-words.
    """
    mapping = {"title": None, "FEs": {}, "LUs": {}}

    # Mappare il nome del frame
    name_synsets = find_synsets(frame.name, nlp)
    mapping["title"] = max(name_synsets, key=lambda syn: calculate_bow_score(syn, "", frame, "title"), default=None)

    # Mappare Frame Elements (FEs)
    for fe_name in frame.FE:
        fe_synsets = find_synsets(fe_name, nlp)
        mapping["FEs"][fe_name] = max(fe_synsets, key=lambda syn: calculate_bow_score(syn, fe_name, frame, "FE"), default=None)

    # Mappare Lexical Units (LUs)
    for lu_name in frame.lexUnit:
        lu_name_cleaned, pos = lu_name.split(".")  # Rimuovi eventuali POS (es. '.n')
        if pos not in [wn.NOUN, wn.VERB, wn.ADJ, wn.ADV]:
            pos = None
        lu_synsets = find_synsets(lu_name_cleaned, nlp, pos)
        mapping["LUs"][lu_name] = max(lu_synsets, key=lambda syn: calculate_bow_score(syn, lu_name, frame, "LU"), default=None)

    return mapping

def load_mapping_from_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        # Convertire le stringhe Synset in oggetti Synset
        for frame_name in data:
            if data[frame_name]["title"] != "None":
                data[frame_name]["title"] = wn.synset(data[frame_name]["title"])
            else:
                data[frame_name]["title"] = None
            for fe_name in data[frame_name]["FEs"]:
                if data[frame_name]["FEs"][fe_name] != "None" :
                    data[frame_name]["FEs"][fe_name] = wn.synset(data[frame_name]["FEs"][fe_name])
                else:
                    data[frame_name]["FEs"][fe_name] = None
            for lu_name in data[frame_name]["LUs"]:
                if data[frame_name]["LUs"][lu_name] != "None":
                    data[frame_name]["LUs"][lu_name] = wn.synset(data[frame_name]["LUs"][lu_name])
                else:
                    data[frame_name]["LUs"][lu_name] = None
        return data
    print("File not found")
    return {}

def main():
    nlp = spacy.load('en_core_web_sm')
    simone_frames = {'Part_piece': 142, 'Spatial_co-location': 2905, 'Mental_stimulus_stimulus_focus': 2046, 'Reasoning': 308, 'Avoiding': 274}
    loris_frames = {'Ground_up': 357, 'Piracy': 123, 'Fire_burning': 2824, 'Location_in_time': 2141, 'Speed_description': 966}
    mattia_frames = {'Conduct': 491, 'Holding_off_on': 1576, 'Chemical-sense_description': 271, 'Endeavor_failure': 2622, 'Physical_artworks': 1656}
    
    mappings_global = {frame_name: map_frame_to_synsets(fn.frame(frame_id), nlp)
            for frame_name, frame_id in (simone_frames | loris_frames | mattia_frames).items()} 
    mapping_simo = {frame_name: map_frame_to_synsets(fn.frame(frame_id), nlp)
            for frame_name, frame_id in simone_frames.items()}
    
    mapping_loris = {frame_name: map_frame_to_synsets(fn.frame(frame_id), nlp)
            for frame_name, frame_id in loris_frames.items()}
    
    mapping_mattia = {frame_name: map_frame_to_synsets(fn.frame(frame_id), nlp)
            for frame_name, frame_id in mattia_frames.items()}
    

    # pprint(mappings, indent=1, sort_dicts=False)

    # load mapping by hand json 
    mappings_by_hand_simo = load_mapping_from_file("mappings_hand_simo.json")
    mappings_by_hand_loris = load_mapping_from_file("mappings_hand_loris.json")
    mappings_by_hand_mattia = load_mapping_from_file("mappings_hand_mattia.json")
    mappings_by_hand = {**mappings_by_hand_simo, **mappings_by_hand_loris, **mappings_by_hand_mattia} # merge dictionaries

    # print(mappings_by_hand)
    
    print(f"Accuracy simo: {round(accuracy_score(mapping_simo, mappings_by_hand_simo) * 100, 2)}%")
    print(f"Accuracy loris: {round(accuracy_score(mapping_loris, mappings_by_hand_loris) * 100, 2)}%")
    print(f"Accuracy mattia: {round(accuracy_score(mapping_mattia, mappings_by_hand_mattia) * 100, 2)}%")
    print(f"Accuracy global: {round(accuracy_score(mappings_global, mappings_by_hand) * 100, 2)}%")

""" if __name__ == "__main__":
    main() """