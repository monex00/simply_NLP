import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
import nltk.stem.porter as porter
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

nltk.download('averaged_perceptron_tagger_eng')

def lemmatize_sentence(sentence):
    if(type(sentence) != str):
        return ""
    lemmatizer = WordNetLemmatizer()
    words_tags = pos_tag(word_tokenize(sentence))
    words = []
    for word, pos in words_tags:
        if pos.startswith("V"):
            pos = "v"
        elif pos.startswith("N"):
            pos = "n"
        elif pos.startswith("J"): # Adjective
            pos = "a"
        elif pos.startswith("R"): # Adverb
            pos = "r"
        else:
            pos = "n"
        words.append(lemmatizer.lemmatize(word, pos))
   
    return " ".join(words)

def calculate_def_similarity(def1, def2):
    arr_def1 = set(def1.split(" "))
    arr_def2 = set(def2.split(" "))
    return len(arr_def1.intersection(arr_def2)) / min(len(arr_def1), len(arr_def2))

def remove_stopwords(text):
    if(type(text) != str):
        return ""
    words = word_tokenize(text)
    words = [word for word in words if word.isalnum()]
    words = [word for word in words if word not in stopwords.words("english")]
    return " ".join(words)

""" stemmer = porter.PorterStemmer()
lemmatizer = WordNetLemmatizer() """
""" print(lemmatizer.lemmatize("writing"))
print(lemmatizer.lemmatize("writing", pos="v")) """

""" dataset = pd.read_csv("TLN-definitions-24.csv", sep=",")
#remove first column
dataset = dataset.iloc[:, 1:]

dataset_lem = dataset.map(lambda s: lemmatize_sentence(s))

dataset = dataset.map(lambda s: remove_stopwords(s))
dataset_stem = dataset.map(lambda s: " ".join([stemmer.stem(word) for word in word_tokenize(s)]))

dataset_lem = dataset_lem.map(lambda s: remove_stopwords(s))

scores_stem = []
for word in dataset_stem.columns.values:
    word_scores = [calculate_def_similarity(def1, def2) for def1 in dataset_stem[word] for def2 in dataset_stem[word] if id(def1) < id(def2)]
    scores_stem.append(word_scores)

scores_lem = []
for word in dataset_lem.columns.values:
    word_scores = [calculate_def_similarity(def1, def2) for def1 in dataset_lem[word] for def2 in dataset_lem[word] if id(def1) < id(def2)]
    scores_lem.append(word_scores)


df_score_stem = pd.DataFrame(index=dataset_stem.columns.values, columns=['score'])
df_score_stem['score'] = [sum(word_scores) / len(word_scores) for word_scores in scores_stem]
print(df_score_stem)

df_score_lem = pd.DataFrame(index=dataset_lem.columns.values, columns=['score'])
df_score_lem['score'] = [sum(word_scores) / len(word_scores) for word_scores in scores_lem]
print(df_score_lem) """