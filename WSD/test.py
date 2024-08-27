from nltk.corpus import wordnet as wn
 
'''
SYNSETS:
    synsets("word")
    wn.synsets('dog', pos=wn.VERB)

META:
    wn.synset('dog.n.01').definition()
    wn.synset('dog.n.01').examples()
    wn.synset('dog.n.01').lemmas() -> list of lemmas synonyms
    
TREE: 
    wn.synset('dog.n.01').hypernyms() -> up in the tree
    wn.synset('dog.n.01').hyponyms() -> down in the tree
    
'''

def get_synonyms(word):
    synonyms = []
    for syn in wn.synsets(word):
        for lemma in syn.lemmas():
            synonyms.append(lemma.name())
    return set(synonyms)

def get_meta(word):
    synsets = wn.synsets(word)
    if synsets:
        synset = synsets[0]
        return {
            'definition': synset.definition(),
            'examples': synset.examples(),
            'lemmas': synset.lemmas()
        }
    return {}
    
def get_tree(word):
    synsets = wn.synsets(word)
    if synsets:
        synset = synsets[0]
        return {
            'hypernyms': synset.hypernyms(),
            'hyponyms': synset.hyponyms()
        }
    return {}

def main():
    word = 'dog'
    print(get_synonyms(word))
    print(get_meta(word))
    print(get_tree(word))

if __name__ == '__main__':
    main()