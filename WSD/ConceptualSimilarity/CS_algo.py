from nltk.corpus import wordnet as wn
import csv
import nltk
import math
from functools import reduce

import pandas as pd
import math
from scipy.stats import pearsonr, spearmanr


from scipy.stats import spearmanr, pearsonr

max_depth = max(len(hyp_path) for synset in wn.all_synsets() for hyp_path in synset.hypernym_paths())

def read_wordsim353():
    wordsim353 = []
    with open('./utils/wordsim353.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            wordsim353.append((row['Word 1'], row['Word 2'], float(row['Human (mean)'])))
    return wordsim353 

def get_hypernym_paths(synset):
    """Risalire la gerarchia degli hypernyms e instance_hypernyms fino alla radice, evitando ripetizioni."""
    paths = [[synset]]
    
    while True:
        new_paths = []
        for path in paths:
            current = path[-1] 
            hypernyms = set(current.hypernyms() + current.instance_hypernyms()) # hypernyms (is-a) e instance_hypernyms (instance-of)
            if not hypernyms:  
                new_paths.append(path)
            else:
                for hypernym in hypernyms: 
                    if hypernym not in path:  # Avoid loops and repetitions
                        new_paths.append(path + [hypernym])
        
        if new_paths == paths:
            break
        paths = new_paths

    return paths


def find_lowest_common_ancestor(synset1, synset2):
    """Trovare l'antenato comune più basso tra due synset."""
    paths1 = get_hypernym_paths(synset1)
    print(paths1)
    paths2 = get_hypernym_paths(synset2)

    lowest_common_ancestor = None
    deph_lowest_common_ancestor = None
    deph1 = None
    deph2 = None

    for path1 in paths1:
        ancestors1 = set(path1)
        for path2 in paths2:
            for i in range(len(path2)):
                syn = path2[i]
                if syn in ancestors1:
                    lca = syn
                    deph_lca = len(path2) - i
                
                    if (not lowest_common_ancestor or deph_lca > deph_lowest_common_ancestor) and len(path1) >= deph_lca and  len(path2)  >= deph_lca:
                        lowest_common_ancestor = lca
                        deph_lowest_common_ancestor = deph_lca

                        deph1 = len(path1) 
                        deph2 = len(path2) 

    return lowest_common_ancestor, deph_lowest_common_ancestor, deph1, deph2


def wup_similarity(synset1, synset2):
    _, deph_lca, deph1, deph2 = find_lowest_common_ancestor(synset1, synset2)
    if(deph_lca == None):
        return 0
    return (2 * deph_lca) / (deph1 + deph2)

def sph_similarity(synset1, synset2):
    _, deph_lca, deph1, deph2 = find_lowest_common_ancestor(synset1, synset2)
    if(deph_lca == None):
        return 0
    len = deph1 - deph_lca + deph2 - deph_lca

    return (2 * max_depth - len ) / (2 * max_depth)

def lch_similarity(synset1, synset2):
    _, deph_lca, deph1, deph2 = find_lowest_common_ancestor(synset1, synset2)
    if(deph_lca == None):
        return 0
    len = deph1 - deph_lca + deph2 - deph_lca
    #print(synset1, synset2, deph1, deph2, deph_lca, len)  
    return (- math.log((len + 1) / ((2 * max_depth) + 1))) / math.log(2 * max_depth + 1)

def find_lowest_common_ancestor_for_words(word1, word2):
    wup_sim=0
    sph_sim=0
    lch_sim = 0
    for syn1 in wn.synsets(word1):
        for syn2 in wn.synsets(word2):
            wup_score = wup_similarity(syn1, syn2)
            sph_score = sph_similarity(syn1, syn2)
            lch_score = lch_similarity(syn1, syn2)
            if wup_score > wup_sim:
                wup_sim = wup_score
            if sph_score > sph_sim:
                sph_sim = sph_score
            if lch_score > lch_sim:
                lch_sim = lch_score
    return wup_sim, sph_sim, lch_sim



wup_similarities = [] 
target_similarities = []
lch_similarities = []
path_similarities = []

wordsim353 = read_wordsim353()

for word1, word2, target in wordsim353: 
    wup_sim, sph_sim, lch_sim = find_lowest_common_ancestor_for_words(word1, word2)
    target_similarities.append(target/10)
    wup_similarities.append(wup_sim)
    path_similarities.append(sph_sim)
    lch_similarities.append(lch_sim)


""" df = pd.DataFrame({'Word1': [word[0] for word in wordsim353], 'Word2': [word[1] for word in wordsim353], 'Target': target_similarities, 'Wu & Palmer': wup_similarities, 'Leacock & Chodorow': lch_similarities, 'Path': path_similarities})
print(df)
# df.to_csv('results.csv')
print('-----------------------------------------')

pearsonwup = pearsonr(wup_similarities, target_similarities)
pearsonlch = pearsonr(lch_similarities, target_similarities)
pearsonpath = pearsonr(path_similarities, target_similarities)

spearmanwup = spearmanr(wup_similarities, target_similarities)
spearmanlch = spearmanr(lch_similarities, target_similarities)
spearmanpath = spearmanr(path_similarities, target_similarities)

df = pd.DataFrame({'Wu & Palmer': [pearsonwup[0], spearmanwup[0]], 'Leacock & Chodorow': [pearsonlch[0], spearmanlch[0]], 'Path': [pearsonpath[0], spearmanpath[0]]}, index=['Pearson', 'Spearman'])

print(df) """