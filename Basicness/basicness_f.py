# import spacy
import math
import nltk
import json
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sklearn.model_selection import KFold, cross_val_score
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from gensim.corpora import Dictionary

from nltk.corpus import wordnet as wn
from nltk.corpus import cmudict

nltk.download('cmudict')
nltk.download('wordnet')
pronouncing_dict = cmudict.dict()

def pronunciation_difficulty(word):
    word = word.lower()
    if word in pronouncing_dict:
        phonemes = pronouncing_dict[word][0]
        difficulty_score = len(phonemes) + sum(1 for p in phonemes if p[-1].isdigit())
        return difficulty_score
    else:
        return len(word)

def read_dataset(file_path):
    rows = []  
    with open(file_path, 'r') as file:
        dataset = json.load(file)
    for i in range(len(dataset["dataset"])):
        entry = dataset["dataset"][i]
        target = 1 if dataset['answers'][i] == "middle" else 0       
        field1, _ = entry.strip().split("|")
        synset, words = field1.strip().split(":")
        words = words.strip().split(",")
        for word in words:
            rows.append({'synset': synset, 'word': word.strip(), 'target': target})
    dataframe = pd.DataFrame(rows)
    return dataframe

def corpus_to_documents(filename):
    with open(filename, 'r') as file:
        dataset = file.read()

    documents = dataset.split("\n\n")
    documents = [word_tokenize(doc.lower()) for doc in documents]
    documents = [[w for w in doc if w not in stopwords.words('english')] for doc in documents]
    documents = [[w for w in doc if w.isalpha()] for doc in documents]
    documents = [[lemmatizer.lemmatize(w) for w in doc] for doc in documents]
    return Dictionary(documents), documents

def calculate_means(df, features):
    mean_features_df = pd.DataFrame(columns=['basic', 'advanced'])
    for feature in features:
        mean_features_df.loc[feature] = [df[df['target'] == 0][feature].mean(), df[df['target'] == 1][feature].mean()]
    return mean_features_df

def calculate_features(df):
    df['word_length'] = df['word'].apply(lambda x: len(x))
    df['pronunciation_difficulty'] = df['word'].apply(pronunciation_difficulty)
    df['synset_depth'] = df['synset'].apply(lambda x: string_to_synset(x).min_depth())
    df['synset_max_depth'] = df['synset'].apply(lambda x: string_to_synset(x).max_depth())
    df['synset_num_hypernyms'] = df['synset'].apply(lambda x: len(string_to_synset(x).hypernyms()))
    df['synset_num_hyponyms'] = df['synset'].apply(lambda x: len(string_to_synset(x).hyponyms()))
    df['synset_num_lemmas'] = df['synset'].apply(lambda x: len(string_to_synset(x).lemmas()))
    df['word_num_senses'] = df['word'].apply(lambda x: len(wn.synsets(x)))
    df['synset_gloss_length'] = df['synset'].apply(lambda x: len(string_to_synset(x).definition()))
    df['synset_examples_length'] = df['synset'].apply(lambda x: sum(len(example) for example in string_to_synset(x).examples()))
    return df 

def string_to_synset(synset_str):
    if synset_str.startswith("Synset('") and synset_str.endswith("')"):
        synset_name = synset_str[8:-2]  # Rimuove "Synset('" e "')"
        return wn.synset(synset_name)
    else:
        raise ValueError("Formato stringa non valido")
    


    
def train_and_evaluate_with_cv(df, output_file="cv_results.csv", detailed_output_file="fold1_results.csv", n_splits=5):
    features = ['word_length', 'pronunciation_difficulty', 'synset_depth', 'word_num_senses',
                'synset_max_depth', 'synset_num_hypernyms', 
                 'synset_num_hyponyms', 'synset_num_lemmas', 'synset_gloss_length', 'synset_examples_length']
    X = df[features].values
    y = df['target'].values

    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    clf = RandomForestClassifier(random_state=42)

    accuracies, precisions, recalls, f1_scores = [], [], [], []

    fold = 1
    for train_index, test_index in kf.split(X):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]

        clf.fit(X_train, y_train)

        y_pred = clf.predict(X_test)
        y_pred_proba = clf.predict_proba(X_test)[:, 1]

        """ if fold == 1:
            detailed_results = pd.DataFrame({
                'synset': df.iloc[test_index]['synset'].values,
                'word': df.iloc[test_index]['word'].values,
                'prob': y_pred_proba,
                'predict': y_pred,
                'target': y_test
            })
            detailed_results.to_csv(detailed_output_file, index=False)
            print(f"Dettagli del primo fold salvati in {detailed_output_file}")
        """
        accuracies.append(accuracy_score(y_test, y_pred))
        precisions.append(precision_score(y_test, y_pred))
        recalls.append(recall_score(y_test, y_pred))
        f1_scores.append(f1_score(y_test, y_pred))

        print(f"Fold {fold}:")
        print("  Accuracy:", accuracies[-1])
        print("  Precision:", precisions[-1])
        print("  Recall:", recalls[-1])
        print("  F1 Score:", f1_scores[-1])
        fold += 1

    avg_accuracy = np.mean(accuracies)
    avg_precision = np.mean(precisions)
    avg_recall = np.mean(recalls)
    avg_f1 = np.mean(f1_scores)

    print("\n--- Media delle Metriche ---")
    print("Accuracy:", avg_accuracy)
    print("Precision:", avg_precision)
    print("Recall:", avg_recall)
    print("F1 Score:", avg_f1)

    return clf

""" df = calculate_features(read_dataset("data/1.json"))
print(df)
mean_for_feature(df)

classifier = train_and_evaluate_with_cv(df)
"""

