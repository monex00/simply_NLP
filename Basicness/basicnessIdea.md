Ecco come potresti sfruttare un modello di Machine Learning facendo uso di due corpus (uno di un libro per bambini e uno di un testo per adulti) per calcolare uno score di “basicness” delle parole.

---

## 1. Raccolta e preparazione dei due corpus

1. **Corpus “bambini”** : prendi un testo (o più testi) esplicitamente scritto per un pubblico giovane. L’aspettativa è che contenga parole più comuni e “semplici” (basic).
2. **Corpus “adulti”** : prendi un testo orientato a un pubblico adulto (ad esempio un saggio, un romanzo complesso o articoli di giornale “seri”), che presumibilmente conterrà un vocabolario più ricercato (advanced).
3. **Preprocessing** :

- Tokenizzazione (es. usando spaCy o NLTK)
- Rimozione di segni di punteggiatura, numeri, eventuali stopword.
- Se serve, normalizzazione (minuscole, lemma/stemming).

---

## 2. Definizione delle etichette (label) e creazione del dataset di addestramento

Per addestrare un classificatore, occorre etichettare le parole come “basic” o “advanced”. Ci sono due possibili approcci:

1. **Heuristico-semplificato** :

- Etichetti una parola come “basic” se compare in modo significativo (o con frequenza X volte superiore) nel corpus “bambini” rispetto al corpus “adulti”.
- Etichetti come “advanced” se è molto più frequente nel corpus “adulti” o se non compare affatto nel corpus “bambini”.
- Naturalmente va definita una soglia di frequenza / log-likelihood ratio o un altro criterio statistico che distingua le parole tipiche del corpus bambini vs. adulto.

1. **Manuale / semisupervisionato** :

- Se hai già un insieme di parole annotate come “basic/advanced”, puoi usare i due corpus come feature aggiuntive.
- Oppure puoi validare lo split automatico facendo eventuali correzioni manuali (specie per parole polisemiche).

  **Risultato** : otterrai una lista di (parola, label=basic/advanced) da usare per il training.

---

## 3. Estrazione di feature

Per ogni parola che vuoi classificare calcola le seguenti feature (esempi):

1. **Frequenza nei due corpus**
   - `freq_bambini` e `freq_adulti`, normalizzate in base alla lunghezza totale del corpus (token totali).
2. **Rapporto di frequenza (ratio)**
   - `ratio = (freq_bambini + 1) / (freq_adulti + 1)` (oppure `log(freq_bambini / freq_adulti)`), per catturare se la parola è relativamente più presente nel corpus “bambini” o in quello “adulti”.
3. **Lunghezza della parola**
   - Parole molto lunghe spesso sono meno “basic”.
4. **Profondità in WordNet** (se la lingua è supportata; vedi se usi NLTK e WordNet per l’inglese o OpenMultilingualWordNet per altre lingue).
   - Più la profondità minima di un synset è alta, più la parola può essere specifica e quindi “meno basic”.
5. **Polisemanticità**
   - Numero di synset: termini con più significati potrebbero essere ambigui e spesso “avanzati” (non sempre, ma talvolta).
6. **Frequenza in un corpus generico** (es. Wikipedia)
   - Confrontando frequenza in corpora “generici” si può avere un segnale aggiuntivo di quanto la parola sia comune.

Ovviamente puoi includere altre feature (morfologiche, POS-tag, ecc.). Più dati hai, più robusto sarà il modello.

---

## 4. Scelta e addestramento del modello di ML

### Modello

Un classificatore binario (ad es. logistic regression, random forest o un piccolo feed-forward neural network) con **label = basic/advanced** .

### Pipeline di training

1. **Costruisci il dataset** : (feature_1, feature_2, …, label) per un set di parole su cui hai la label.
2. **Train-Test split** : dividi in training e test per valutare il modello.
3. **Addestramento** : ad esempio con scikit-learn:

```python
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# X: matrice delle feature
# y: label binaria (0 = advanced, 1 = basic)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

clf = LogisticRegression()
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
```

4. **Valutazione** :
   Puoi anche calcolare precision, recall, AUC, ecc.

```python
from sklearn.metrics import accuracy_score, f1_score

print("Accuracy:", accuracy_score(y_test, y_pred))
print("F1-score:", f1_score(y_test, y_pred))
```

---

## 5. Output: Score di “basicness”

Se vuoi un output continuo invece che binario, puoi utilizzare:

In questo modo hai uno score continuo su 0,10,1**0**,**1** che indica quanto la parola è considerata “basic”.

```python
y_prob = clf.predict_proba(X_test)
basicness_score = y_prob[:, 1]  # se l'indice 1 corrisponde alla classe "basic"
```

---

## 6. Esempio semplificato di codice (Python)

```python
import spacy
from collections import Counter
import math

# Carichiamo un modello spacy a titolo di esempio (en_core_web_sm, it_core_news_sm, ecc.)
nlp = spacy.load('en_core_web_sm')

def preprocess_text(text):
    doc = nlp(text.lower())
    tokens = []
    for token in doc:
        if token.is_alpha:  # solo caratteri alfabetici
            tokens.append(token.lemma_)
    return tokens

# 1) Carichiamo i due testi
text_bambini = open('bambini.txt').read()
text_adulti = open('adulti.txt').read()

# 2) Preprocessing e conteggio frequenze
tokens_bambini = preprocess_text(text_bambini)
tokens_adulti = preprocess_text(text_adulti)

freq_bambini = Counter(tokens_bambini)
freq_adulti = Counter(tokens_adulti)

# Esempio di estrazione feature per una parola generica
def extract_features(word):
    # Frequenza normalizzata
    freq_b = freq_bambini[word] / len(tokens_bambini) if len(tokens_bambini) > 0 else 0
    freq_a = freq_adulti[word] / len(tokens_adulti) if len(tokens_adulti) > 0 else 0

    # Ratio (un log per stabilizzarlo)
    ratio = math.log((freq_b + 1e-7)/(freq_a + 1e-7))  # se > 0 => più comune in bambini

    # Lunghezza parola
    length_word = len(word)

    return [freq_b, freq_a, ratio, length_word]

# 3) Crei l’insieme di parole su cui vuoi fare label e training
#    - Heuristica per label (semplificato):
#      label = 1 ("basic") se freq_b >> freq_a; altrimenti 0 ("advanced")
dataset = []
parole_uniche = set(tokens_bambini) | set(tokens_adulti)
for w in parole_uniche:
    f_b = freq_bambini[w]
    f_a = freq_adulti[w]
    # Soglia semplice: se freq_b > freq_a => basic
    label = 1 if f_b > f_a else 0
    features = extract_features(w)
    dataset.append((features, label))

# dataset adesso è una lista di ([features], label)
X = [d[0] for d in dataset]
y = [d[1] for d in dataset]

# 4) Addestriamo un classificatore
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
clf = LogisticRegression()
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("F1-score:", f1_score(y_test, y_pred))

# Se vuoi uno score continuo:
y_prob = clf.predict_proba(X_test)[:,1]
```

---

## 7. Miglioramenti possibili

1. **Includere WordNet** : calcolare la profondità di WordNet o i supersensi come ulteriore feature.
2. **Filtrare parole rare** : se una parola appare pochissimo in entrambi i corpus, potresti escluderla dal training o trattarla come “non classificabile”.
3. **Lemmi vs. forme flesse** : se la lingua è molto flessa (es. italiano), assicurati di usare i lemmi per calcolare frequenze coerenti.
4. **Più corpora** : se hai più testi di livelli differenti (es. testo bambini 6-8 anni, testo ragazzi 12-14, testo adulti) potresti ottenere una classificazione più fine.
5. **Integrazione di knowledge base** : potresti sfruttare le definizioni di WordNet (o Wikipedia) e calcolare quanto è “complesso” il gloss di un termine (es. analisi di leggibilità).

---

## Conclusioni

- Se vuoi separare nettamente “basic” vs. “advanced”, utilizzare due corpus a target diverso è un buon punto di partenza.
- **Step principale** : definire correttamente le **etichette** (label) sfruttando i rapporti di frequenza nei due corpus.
- **Estendere** : aggiungendo WordNet e altre fonti, arricchisci le feature e migliori la precisione.

Con questi passaggi, otterrai un modello in grado di stimare uno “score di basicness” (o di classificare parole in basic/advanced) basandosi sulla “vicinanza” lessicale al linguaggio per bambini o per aduti

---

## Features:

- **Profondità in wordnet**
- **Lunghezza parola**
- **Lunghezza glossario e esempi**
- **Polisemanticità**
- **Rapporto di frequenza con sense disambiguation**
- **Spell difficulty**

---

# Features future

- Mettere le feature delle parole con cui cooccore maggiormente o iperonimi/iponimi
- Usare come feature lo score di un modello a bigrammi/trigrammi su due corpus

# Embeddings

### **Step 1: Preparare i Corpus**

Avrai bisogno di due dataset distinti:

1. **Corpus per bambini** (es. Simple English Wikipedia, libri per ragazzi).
2. **Corpus per adulti** (es. articoli scientifici, narrativa complessa).

### **Step 2: Addestrare Word Embeddings**

Puoi usare librerie come **Gensim** per addestrare modelli di embedding come **Word2Vec** o **FastText** .

```python
from gensim.models import Word2Vec
from nltk.tokenize import word_tokenize
import nltk

# Scarica un tokenizer
nltk.download('punkt')

# Carica e pre-elabora i corpus
def preprocess_corpus(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read().lower()
    sentences = [word_tokenize(sent) for sent in text.splitlines() if sent.strip()]
    return sentences

# Corpus per bambini e adulti
child_corpus_sentences = preprocess_corpus("child_corpus.txt")
adult_corpus_sentences = preprocess_corpus("adult_corpus.txt")

# Addestramento Word2Vec per entrambi i domini
child_model = Word2Vec(sentences=child_corpus_sentences, vector_size=100, window=5, min_count=1, sg=1, epochs=10)
adult_model = Word2Vec(sentences=adult_corpus_sentences, vector_size=100, window=5, min_count=1, sg=1, epochs=10)

# Salva i modelli
child_model.save("child_word2vec.model")
adult_model.save("adult_word2vec.model")
```

### Step 3: Confrontare Embeddings

Dopo aver generato i modelli, puoi calcolare la similarità di una parola rispetto ai due domini.

```python
from gensim.models import Word2Vec
from scipy.spatial.distance import cosine

# Carica i modelli
child_model = Word2Vec.load("child_word2vec.model")
adult_model = Word2Vec.load("adult_word2vec.model")

def get_domain_similarity(word):
    if word in child_model.wv and word in adult_model.wv:
        child_vector = child_model.wv[word]
        adult_vector = adult_model.wv[word]
        # Calcola la similarità con cosine similarity
        similarity_child = 1 - cosine(child_vector, child_model.wv.get_mean_vector(child_model.wv.index_to_key))
        similarity_adult = 1 - cosine(adult_vector, adult_model.wv.get_mean_vector(adult_model.wv.index_to_key))
        return similarity_child, similarity_adult
    else:
        return None, None

# Testa con una parola
word = "apple"
similarity_child, similarity_adult = get_domain_similarity(word)
print(f"Similarità per '{word}':")
print(f"  Bambini: {similarity_child:.4f}")
print(f"  Adulti: {similarity_adult:.4f}")

```

### Step 4: Usare Embeddings come Feature

Puoi aggiungere queste similarità come feature nel tuo dataset.

```python
def add_embedding_features(df):
child_similarities = []
adult_similarities = []

    for word in df['word']:
        similarity_child, similarity_adult = get_domain_similarity(word)
        child_similarities.append(similarity_child)
        adult_similarities.append(similarity_adult)

    df['similarity_to_child'] = child_similarities
    df['similarity_to_adult'] = adult_similarities
    return df

# Aggiungi le feature al dataframe

df = add_embedding_features(df)
print(df.head())
```

### Se la parola non è presente:

#### Usa un Modello di Backup

Se la parola non è presente nei tuoi corpus, puoi fare riferimento a un modello pre-addestrato come GloVe o FastText, che hanno vocabolari molto ampi. Questo approccio sfrutta embeddings più generici:

```python
from gensim.models import KeyedVectors

# Carica GloVe o FastText come modello di backup

glove_model = KeyedVectors.load_word2vec_format('glove.6B.100d.txt', binary=False)

def get_domain_similarity_with_backup(word):
   if word in child_model.wv and word in adult_model.wv:
      child_vector = child_model.wv[word]
      adult_vector = adult_model.wv[word]
      similarity_child = 1 - cosine(child_vector, child_model.wv.get_mean_vector(child_model.wv.index_to_key))
      similarity_adult = 1 - cosine(adult_vector, adult_model.wv.get_mean_vector(adult_model.wv.index_to_key))
   return similarity_child, similarity_adult
   elif word in glove_model.key_to_index: # Usa GloVe come backup
      word_vector = glove_model[word]
      similarity_child = 1 - cosine(word_vector, child_model.wv.get_mean_vector(child_model.wv.index_to_key))
      similarity_adult = 1 - cosine(word_vector, adult_model.wv.get_mean_vector(adult_model.wv.index_to_key))
   return similarity_child, similarity_adult
   else:
      return 0.5, 0.5
```
