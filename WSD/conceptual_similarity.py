from nltk.corpus import wordnet as wn
import logging

logging.basicConfig(level=logging.INFO)

def main():
    #read input:
    records = read_input()
    eps = 1.3
    for word1, word2, score in records:
        my_score = word_sim(word1, word2)
        if abs(score - my_score) > eps:
            logging.info(f'{word1} -> {word2} = {score} -> {my_score}')
            logging.info("\n")
    # word1, word2 = "telephone", "communication"
    # score = word_sim(word1, word2)
    # map score to 0-10

    print(f'{word1} -> {word2} = {score}')


def read_input():
    records = []
    first = True
    with open("utils/WordSim353.csv", "r") as file: 
        for line in file:
            if first:
                first = False
                continue
            word1, word2, score = line.strip().split(",")
            score = float(score)
            records.append((word1, word2, score))
    return records

def word_sim(word1, word2):
    max_score = 0
    for syn1 in wn.synsets(word1):
        for syn2 in wn.synsets(word2):
            # print(f'{syn1} -> {syn2}')
            depth_hypernyms1 = []
            depth_hypernyms2 = []
            depth1 = depth(syn1, depth_hypernyms1)
            depth2 = depth(syn2, depth_hypernyms2)
            lcs = LCS(depth_hypernyms1, depth_hypernyms2)
            if not lcs:
                continue
            lastLcs = lcs[-1]
            score = wup_similarity(depth1, depth2, lastLcs["depth"])
            score = 10 * score
            if score > max_score:
                comparedScore = syn1.wup_similarity(syn2)
                logging.debug(f'depth1: {depth1}, depth2: {depth2}, depthLcs: {lastLcs["depth"]}')
                logging.debug(f'score: {score}')
                logging.info(f'comparedScore: {comparedScore * 10}')
                logging.debug(f'{syn1} -> {syn2}')
                logging.debug(f'{syn1.definition()} -> {syn2.definition()}')
                logging.debug(f'{lastLcs["synset"].name()} -> {lastLcs["synset"].definition()}')
                logging.debug("\n")
                max_score = score
    return max_score
            

def wup_similarity(depth_hypernyms1, depth_hypernyms2, depth_lcs):
    return 2 * depth_lcs / (depth_hypernyms1 + depth_hypernyms2)

def depth(synset,depth_hypernyms = []):
    if synset.hypernyms():
        # print(f'{synset} -> {synset.hypernyms()}')  
        for h in synset.hypernyms():
            depth_hypernyms.append({
                'synset': h,
                'depth': depth(h, depth_hypernyms)
            })
            
        return 1 + max([h["depth"] for h in depth_hypernyms])
    else:
        return 1
    
def LCS(depth_hypernyms1, depth_hypernyms2):
    lcs = []
    for i in range(min(len(depth_hypernyms1), len(depth_hypernyms2))):
        if depth_hypernyms1[i]["synset"].name() == depth_hypernyms2[i]["synset"].name():
            lcs.append(depth_hypernyms1[i])
    return lcs 


if __name__ == '__main__':
    main()