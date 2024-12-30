# spell difficulty
import nltk
from nltk.corpus import cmudict

nltk.download('cmudict')

pronouncing_dict = cmudict.dict()

def pronunciation_difficulty(word):
    word = word.lower()
    if word in pronouncing_dict:
        phonemes = pronouncing_dict[word][0]
        difficulty_score = len(phonemes) + sum(1 for p in phonemes if p[-1].isdigit())
        return f"Difficoltà: {difficulty_score}, Fonemi: {phonemes}"
    else:
        return "Parola non trovata nel dizionario CMU."

# Esempio
print(pronunciation_difficulty("backpacker"))