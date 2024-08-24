from simplenlg.features import *
from simplenlg.framework import *
from simplenlg.lexicon import * 
from simplenlg.realiser.english import * 
from simplenlg.phrasespec import SPhraseSpec
import sys
import time

""" lexicon = Lexicon.getDefaultLexicon()
realiser = Realiser(lexicon)
nlgFactory = NLGFactory(lexicon)


sentence = nlgFactory.createClause()
sentence.setSubject("cfg")
sentence.setVerb("be")
sentence.setObject("a grammar")
sentence.setFeature(Feature.INTERROGATIVE_TYPE, InterrogativeType.YES_NO)  

sentence1 = nlgFactory.createClause()
sentence1.setSubject("probability")
sentence1.setVerb("do")
sentence1.setObject("rules have associated with")
sentence1.setFeature(Feature.PASSIVE, Tense.PRESENT)

sentence1.setFeature(Feature.INTERROGATIVE_TYPE, InterrogativeType.WHAT_SUBJECT)  

# Generazione della domanda
output = realiser.realiseSentence(sentence) """


import subprocess
print("Executing the Compiled Code")
application="java"
result = subprocess.run([application,"-cp", "./simpleNLG-IT/simplenlg-it.jar", "./simpleNLG-IT/SimpleNlgProxy.java", "Paolo", "ama", "Francesca", "WHO_SUBJECT" ], stdout=subprocess.PIPE)
output = result.stdout.decode('utf-8')
print("Execution Completed")
print(output)