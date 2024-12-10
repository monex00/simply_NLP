import nltk
from nltk.corpus import framenet as fn
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re

import spacy
from pprint import pprint
from fn_mappings_by_hand import mappings_by_hand


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


# Esempio di utilizzo
# frames = getFrameSetForStudent("Mario Rossi")
# results = {}
# 
# for frame in frames:
#     results[frame.name] = map_frame_to_synsets(frame, depth=1)  # Profondità opzionale
# 
# # Output dei risultati
# for frame_name, mapping in results.items():
#     print(f"Frame: {frame_name}")
#     print("Title Synset:", mapping['title'].name() if mapping['title'] else "None")
#     print("Frame Elements:")
#     for fe_name, fe_synset in mapping['FEs'].items():
#         print(f"  {fe_name}: {fe_synset.name() if fe_synset else 'None'}")
#     print("Lexical Units:")
#     for lu_name, lu_synset in mapping['LUs'].items():
#         print(f"  {lu_name}: {lu_synset.name() if lu_synset else 'None'}")
#     print()

def main():
    
    nlp = spacy.load('en_core_web_sm')
    andrea_frames = {'Touring': 1907, 'Cause_fluidic_motion': 920, 'Submitting_documents': 1521, 'Appellations': 2390, 'Evidence': 25}
    fabio_frames = {'Strictness': 75, 'Being_pregnant': 2921, 'Sex': 2913, 'Wearing': 160, 'Dominate_situation': 1795}

    mappings = {frame_name: map_frame_to_synsets(fn.frame(frame_id), nlp)
            for frame_name, frame_id in (andrea_frames | fabio_frames).items()}

    pprint(mappings, indent=1, sort_dicts=False)
    
    print(f"Accuracy: {round(accuracy_score(mappings, mappings_by_hand) * 100, 2)}%")

if __name__ == "__main__":
    main()