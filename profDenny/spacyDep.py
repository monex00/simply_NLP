""" import spacy
from spacy import displacy


nlp = spacy.load("en_core_web_lg")

# Parsing dei documenti
doc1 = nlp("The phases are TextPlanning , SentencePlanning and Realization")
doc2 = nlp("The phases are TextPlanning which is blue, SentencePlanning which is green, and Realization which is red.")

def simple_tree_similarity(doc1, doc2, dep_to_ignore={"punct", "cc", "aux", "det", "prep", "mark"}):
    # Conta le corrispondenze e le discrepanze nei token e nelle dipendenze
    matches = 0
    total = 0
    for token1 in doc1:
        
        if token1.dep_ in dep_to_ignore:
            continue

        total += 1
        for token2 in doc2:
           
            if token1.dep_ == token2.dep_ and token1.head.lemma_ == token2.head.lemma_ and token1.lemma_ == token2.lemma_:
                matches += 1
            elif token1.lemma_ == token2.lemma_:
                print(token1, token1.dep_, token1.head.lemma_, token1.lemma_)
                print(token2, token2.dep_, token2.head.lemma_, token2.lemma_)

    return matches / total if total > 0 else 0

similarity = simple_tree_similarity(doc1, doc2)
print(f"Similarity score: {similarity:.2f}")

displacy.serve(doc1, style="dep", auto_select_port=True)
displacy.serve(doc2, style="dep", auto_select_port=True )
 """

import pandas as pd
import requests

class Token:
    def __init__(self, id, form, lemma, pos, xpos, feats, head, dep, deps, misc):
        self.id = id
        self.form = form
        self.lemma = lemma
        self.pos = pos
        self.xpos = xpos
        self.feats = feats
        self.head = head
        self.dep = dep
        self.deps = deps
        self.misc = misc

    def __str__(self):
        return self.form

    def __repr__(self):
        return self.form

    def __eq__(self, other):
        return self.form == other.form

    def __hash__(self):
        return hash(self.form)




def get_dependencies(text):
    baseUlr = "http://lindat.mff.cuni.cz/services/udpipe/api/process?tokenizer&tagger&parser&model=italian-isdt-ud-2.12-230717&data="
    response = requests.get(baseUlr + text)
    data = response.json()
    result = data["result"]

    text = result.split("\n")[7:]

    # Converte il testo in un DataFrame
    data = [line.split("\t") for line in text]
    columns = ["ID", "Form", "Lemma", "POS", "XPOS", "Feats", "Head", "DepRel", "Deps", "Misc"]
    df = pd.DataFrame(data, columns=columns)

    tokens = []
    for row in data:
        if(len(row) < 10):
            continue

        head_index = int(row[6]) - 1
        head = None
        if head_index < 0:
            head = Token(0, "ROOT", "ROOT", "ROOT", "ROOT", "ROOT", "ROOT", "ROOT", "ROOT", "ROOT")
        else:
            head = Token(data[head_index][0], data[head_index][1], data[head_index][2], data[head_index][3], data[head_index][4], data[head_index][5], data[head_index][6], data[head_index][7], data[head_index][8], data[head_index][9])

        token = Token(row[0], row[1], row[2], row[3], row[4], row[5], head, row[7], row[8], row[9])
        tokens.append(token)

  
    return tokens

def simple_tree_similarity(doc1, doc2, dep_to_ignore={"punct", "cc", "aux", "det", "prep", "mark"}):
    # Conta le corrispondenze e le discrepanze nei token e nelle dipendenze
    matches = 0
    total = 0
    dict1 = {
        "Textplanning": 0,
        "Sentenceplanning": 0,
        "Realization": 0,
    }
    for token1 in doc1:
        if token1.dep in dep_to_ignore:
            continue

        total += 1
        for token2 in doc2:
           
            if token1.dep == token2.dep and token1.head.lemma == token2.head.lemma and token1.lemma == token2.lemma:
                matches += 1
                # fill frame con probabilità 1
                if(token1.lemma in dict1):
                    dict1[token1.lemma] = 1
                # print(token1, token1.dep, token1.head.lemma, token1.lemma, token1.pos)
                # print(token2, token2.dep, token2.head.lemma, token2.lemma, token2.pos)
            elif token1.lemma == token2.lemma:
                print(token1, token1.dep, token1.head.lemma, token1.lemma, token1.pos)
                print(token2, token2.dep, token2.head.lemma, token2.lemma, token2.pos)
                # fill frame con probabilità minore di 1
                if(token1.lemma in dict1):
                    dict1[token1.lemma] = 0.5
    print(dict1)
    return matches / total if total > 0 else 0

doc1 = get_dependencies("Le fasi sono TextPlanning , SentencePlanning e Realization.")
doc2 = get_dependencies("Le fasi sono SentencePlanning, che sono blu, TextPlanning , che sono blu, e Realization che sono blu.")



similarity = simple_tree_similarity(doc1, doc2)
print(f"Similarity score: {similarity:.2f}")

# Stampa il DataFrame
#print(df.to_string(index=False))
