
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from sentence_transformers import util


embedding_dict = dict()

def remove_stopwords(text):
    if(type(text) != str):
        return ""
    words = word_tokenize(text)
    words = [word for word in words if word.isalnum()]
    words = [word for word in words if word not in stopwords.words("english")]
    return " ".join(words)

def count_genus(genus_list):
    genus_count = {}
    for genus in genus_list:
        if genus in genus_count:
            genus_count[genus] += 1
        else:
            genus_count[genus] = 1
    return genus_count

def find_genus(definitions, nlp):
    genus_list = []
    for definition in definitions:
        if definition == "" or definition == None or type(definition) != str:
            continue
        definition = remove_stopwords(definition)
        doc = nlp(definition)
        for token in doc:
            if token.pos_ == "NOUN":  # Cerca il primo nome
                genus_list.append(token.text) 
    return genus_list

def get_max_genus(genus_count, n):
    max_genus = sorted(genus_count.items(), key=lambda x: x[1], reverse=True)[:n]
    return max_genus

def find_max_symilarity_score(symilarity_score, n):
    max_symilarity_score = sorted(symilarity_score.items(), key=lambda x: x[1], reverse=True)[:n]
    return max_symilarity_score

def find_senses(genuses, dataset_definitions, model, max_iter, min_score = 0.6, transformer_weight = 0.5, overlap_weight = 0.5):
    front=[]
    scores = set()
    for genus in genuses:
        for syn in wn.synsets(genus):
            front.append((syn, multiple_similarity(syn, dataset_definitions, model,transformer_weight, overlap_weight)))
    front = sorted(front, key=lambda x: x[1], reverse=True)
    iter = 0
    while len(front) != 0 and iter < max_iter:
        iter += 1
        if front[0][1] >= min_score:
            scores.add((front[0][0], front[0][1]))
        front = front[1:] + expand_frontier(front[0][0], model, dataset_definitions,transformer_weight, overlap_weight)
        front = sorted(front, key=lambda x: x[1], reverse=True)
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    return scores[:10]

def expand_frontier(synset, model, dataset_definitions,transformer_weight, overlap_weight):
    return [(syn[0], multiple_similarity(syn[0], dataset_definitions, model,transformer_weight, overlap_weight)) for syn in find_best_hyponym(synset)]

def find_best_hyponym(syn):
    best_hyponyms = []
    for synset in syn.hyponyms():
        best_hyponyms.append((synset, syn.wup_similarity(synset)))
    sorted_best_hyponyms = sorted(best_hyponyms, key=lambda x: x[1], reverse=True)
    return sorted_best_hyponyms

def similarity_score(synset, dataset_definitions, model):
    synset_definitions = synset.examples()
    synset_definitions.append(synset.definition())
    final_score = 0 
    embedding1,embedding1 = None,None
    nans = 0
    for definition in dataset_definitions:
        score = 0
        if type(definition) != str:
            nans += 1
            continue
        for syn_def in synset_definitions:
            if definition in embedding_dict:
                embedding1 = embedding_dict[definition]
            else:
                embedding1 = model.encode(definition, convert_to_tensor=True)
                embedding_dict[definition] = embedding1
            if syn_def in embedding_dict:
                embedding2 = embedding_dict[syn_def]
            else:
                embedding2 = model.encode(syn_def, convert_to_tensor=True)
                embedding_dict[syn_def] = embedding2
            score += util.cos_sim(embedding1, embedding2).item()
        score /= len(synset_definitions)
        final_score += score
    final_score /= (len(dataset_definitions) - nans)
    return (final_score + 1) / 2

def overlap_similarity(synset, dataset_definitions):
    synset_definitions = synset.examples()
    synset_definitions.append(synset.definition())
    for i in range(len(dataset_definitions) - 1 ):
        if not isinstance(dataset_definitions[i], str):
            dataset_definitions[i] = ""
    final_score = 0
    synset_words = set(word_tokenize(remove_stopwords(synset.definition())))
    definition_words = set(word_tokenize(remove_stopwords(" ".join(dataset_definitions))))
    overlap = synset_words.intersection(definition_words)
    final_score = len(overlap)/len(synset_words)
    return final_score

def multiple_similarity(synset, dataset_definitions, model,transformer_weight, overlap_weight):
    return (((similarity_score(synset, dataset_definitions, model) * transformer_weight)  + (overlap_similarity(synset, dataset_definitions) * overlap_weight)) ) 

def get_genus(definition_list, n , term, nlp):
    genus = find_genus(definition_list, nlp)
    genus_count = count_genus(genus)
    genus_count.pop(term, None)
    max_genus = get_max_genus(genus_count, n)
    genus_words = list(map(lambda x: x[0], max_genus))
    return genus_words
    
#model = SentenceTransformer('all-MiniLM-L6-v2')
#dataset = pd.read_csv("TLN-definitions-24.csv", sep=",")
##remove first column
#dataset = dataset.iloc[:, 1:]
#
## nlp = spacy.load("en_core_web_sm")
#nlp = spacy.load("en_core_web_md")
#
#for column in dataset.columns:
#    print("Analisys for", column)
#    definition_list = dataset[column].tolist()
#    genus = get_genus(definition_list, 3)
#    print("Genus: ", genus)
#
#    symilarity_score = find_senses(genus, definition_list, model, max_iter = 100, min_score=0.5, transformer_weight=1, overlap_weight=0)
#
#    for score in symilarity_score[:10]:
#        print("Score for", score[0], "=", score[1])


