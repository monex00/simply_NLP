from simplenlg.features import Tense, Feature
from simplenlg.framework import NLGFactory
from simplenlg.lexicon import Lexicon
from simplenlg.realiser.english import Realiser
from simplenlg.phrasespec import SPhraseSpec
import sys
import time

lexicon = Lexicon.getDefaultLexicon()
realiser = Realiser(lexicon)
nlgFactory = NLGFactory(lexicon)


def text_planning():
    return {
        "introduction": {
            "subject": "SimpleNLG",
            "verb": "be",
            "complement": "a software tool for natural language generation"
        },
        "features": {
            "verbs": ["handle", "simplify"],
            "objects": ["syntax", "lexicon management"]
        },
        "use_case": {
            "context": "commonly used",
            "applications": ["academic projects", "commercial software development"]
        }
    }


def sentence_planning(content):
    sentences = {
        "introduction": content['introduction'],
        "features": {
            "subject": content['introduction']['subject'],
            "verb": "can",
            "complement": {
                "verbs": content['features']['verbs'],
                "objects": content['features']['objects']
            }
        },
        "use_case": {
            "clause": nlgFactory.createClause(),
            "context": content['use_case']['context'],
            "applications": content['use_case']['applications']
        }
    }
    return sentences



def realization(plans):
    # Introduzione
    intro = nlgFactory.createClause(plans['introduction']['subject'], plans['introduction']['verb'], plans['introduction']['complement'])
    intro.setFeature(Feature.TENSE, Tense.PRESENT)
    
    # Funzionalità
    features = nlgFactory.createClause(plans['features']['subject'], plans['features']['verb'], None)
    coord = nlgFactory.createCoordinatedPhrase()
    for verb, obj in zip(plans['features']['complement']['verbs'], plans['features']['complement']['objects']):
        phrase = nlgFactory.createVerbPhrase(verb)
        phrase.setObject(obj)
        coord.addCoordinate(phrase)
    features.setObject(coord)
    
    # Casi d'uso
    use_case = nlgFactory.createClause("it", plans['use_case']['context'], "in applications such as " + ", ".join(plans['use_case']['applications']))
    use_case.setFeature(Feature.TENSE, Tense.PRESENT)
    
    # Realizzazione
    introduction_text = realiser.realiseSentence(intro)
    features_text = realiser.realiseSentence(features)
    use_case_text = realiser.realiseSentence(use_case)
    
    return ' '.join([introduction_text, features_text, use_case_text])


def print_slowly(text, delay=0.05):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        if char in '.!?':  
            time.sleep(0.5)
        elif char == ',':
            time.sleep(0.3)
        else:
            time.sleep(delay)
    print()  


content = text_planning()
plan = sentence_planning(content)
final_text = realization(plan)
print_slowly(final_text)