import pandas as pd
import numpy as np
import requests
import json
import subprocess


NUM_RETRIES = 3

# START UTILS FUNCTIONS
def udipipe_api(text):
    baseUlr = "http://lindat.mff.cuni.cz/services/udpipe/api/process?tokenizer&tagger&parser&model=italian-isdt-ud-2.12-230717&data="
    response = requests.get(baseUlr + text)
    data = response.json()
    result = data["result"]

    return result


def execute_subcommand(text, intention):
    application="java"
    # print(text)
    result = subprocess.run([application,"-cp", "./simpleNLG-IT/simplenlg-it.jar", "./simpleNLG-IT/SimpleNlgProxyLoris.java", text, intention], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')
    return output

def levenshtein_distance(word1, word2):
    word1 = word1.lower()
    word2 = word2.lower()
    dp = np.zeros((len(word1) + 1, len(word2) + 1), dtype=int)

    for i in range(len(word1) + 1):
        dp[i][0] = i
    for j in range(len(word2) + 1):
        dp[0][j] = j

    for i in range(1, len(word1) + 1):
        for j in range(1, len(word2) + 1):
            if word1[i - 1] == word2[j - 1]:
                cost = 0
            else:
                cost = 1
            dp[i][j] = min(dp[i - 1][j] + 1,  
                           dp[i][j - 1] + 1,
                           dp[i - 1][j - 1] + cost)
    
    return dp[len(word1)][len(word2)]
# END UTILS FUNCTIONS

class Record:
    def __init__(self):
        self.words = []
        self.out_context = []
        self.missing_dep = []
        self.score = []
        self.misspells = False

    def add_out_context(self, index, word):
        self.out_context[index].append(word)

    def add_word(self,index, word):
        if index >= len(self.words):
            self.words.append(word)
            self.score.append(0)
            self.out_context.append([])
            self.missing_dep.append(False)
    
    def set_score(self, index, score): 
        self.score[index] = score

    def __str__(self):
        words_str = ""
        for i in range(len(self.words)):
            words_str += self.words[i] + " - " + str(self.score[i]) + "\n"
        out_context_str = ""
        for i in range(len(self.out_context)):
            out_context_str += self.words[i] + " - " + str(self.out_context[i]) + "\n"
        return "Words:\n" + words_str + "Out of context:\n" + out_context_str


class History:
    def __init__(self):
        self.records = []

    def add_record(self, record):
        self.records.append(record)
    
    def __str__(self):
        records_str = ""
        for frame in self.records:
            records_str += frame + "\n"
            for record in self.records[frame]:
                records_str += "\t" + str(record) + "\n"
        return records_str

class Token:
    def __init__(self, id, form, lemma, pos, xpos, feats, head, dep, deps, misc):
        self.id = id
        self.form = form
        self.lemma = lemma
        self.pos = pos
        self.xpos = xpos
        self.feats = feats
        self.head = head
        self.dep = dep
        self.deps = deps
        self.misc = misc
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def __str__(self):
        return self.form
        

class FillQuestion:
    def __init__(self, question, trigger, intention):
        self.question = question
        self.intention = intention
        self.trigger = trigger

    def realize_question(self):
        print(self.intention)
        if len(self.intention) == 0 or self.intention[0] == "MISSPELL":
            return self.question
        q = execute_subcommand(self.question, self.intention[0])
        return q

    def __str__(self):
        return "\t\t\tQuestion: " + self.question + "\n\t\t\tTrigger: " + self.trigger  + "\n\t\t\tIntention: " + str(self.intention)


class RequiredWord:
    def __init__(self, lemma, weight):
        self.lemma = lemma
        self.fill_questions = []
        self.weight = float(weight)
        self.score = 0
        self.triggered = False
        self.dependencies = []

    def add_dependency(self, dep):
        self.dependencies.append(dep)

    def add_fill_question_front(self, question):
        self.fill_questions.insert(0, question)

    def add_fill_question(self, question):
        self.fill_questions.append(question)
    
    def remove_fill_question(self, question):
        removed_intention = ""
        if(len(question.intention) == 0 ):
            self.fill_questions.remove(question)
        else: 
            removed_intention = question.intention.pop(0)
            if(len(question.intention) == 0 ):
                self.fill_questions.remove(question)
        
        return removed_intention

    
    def __str__(self):
        fill_questions_str = ""
        for fill_question in self.fill_questions:
            fill_questions_str += str(fill_question) + "\n"
        dependencies_str = ""
        for dep in self.dependencies:
            dependencies_str += str(dep) + "\n"
        return "\tLemma: " + self.lemma + "\n\tWeight: " + str(self.weight) + "\n\tScore: " + str(self.score) + "\n\tFill Questions:\n" + fill_questions_str + "\n\tDependencies:\n" + dependencies_str
        

class RequiredDependency:
    def __init__(self, to, type, weight):
        self.to = to
        self.type = type
        self.fill_questions = []
        self.weight = float(weight)
        self.score = 0
    
    def add_fill_question(self, question):
        self.fill_questions.append(question)
    
    def add_fill_question_front(self, question):
        self.fill_questions.insert(0, question)
    
    def remove_fill_question(self, question):
        removed_intention = ""
        if(len(question.intention) == 0 ):
            self.fill_questions.remove(question)
        else: 
            removed_intention = question.intention.pop(0)
            if(len(question.intention) == 0 ):
                self.fill_questions.remove(question)

        return removed_intention

    def __str__(self):
        fill_questions_str = ""
        for fill_question in self.fill_questions:
            fill_questions_str += str(fill_question) + "\n"
        return "\t\tTo: " + self.to + "\n\t\tType: " + self.type + "\n\t\tWeight: " + str(self.weight) + "\n\t\tScore: " + str(self.score) + "\n\t\tFill Questions:\n" + fill_questions_str

class Frame:
    def __init__(self, question, answer, name, domain):
        self.name = name
        self.question = question
        self.answer = answer
        self.state = ""
        self.required_slots = []
        self.retries = 0
        self.domain = domain
        self.out_context_words = []

    def add_out_context_word(self, out_context_word):
        self.out_context_words.append(out_context_word)
        
    def add_required_slot(self, required_slot):
        self.required_slots.append(required_slot)
        self.state += '0'
        self.retries +=1

    def add_dependency(self, slot, dep):
        slot.add_dependency(dep)
        self.retries +=1

    def check_frame(self):
        for required_slot in self.required_slots:
            if required_slot.score == 0 and self.retries > 0:
                return False
            for dep in required_slot.dependencies:
                if dep.score == 0 and self.retries > 0:
                    return False
        return True

    def is_triggering(self, trigger):
        for i in range(len(trigger)):
            if trigger[i] == '*':
                continue
            if trigger[i] != self.state[i]:
                return False
        return True
    
    def get_final_score(self):
        score = 0
        tot_req = 0
        for required_slot in self.required_slots:
            score += required_slot.score * required_slot.weight
            tot_req += 1
            for dep in required_slot.dependencies:
                score += dep.score * dep.weight
                tot_req += 1

        """ out of context """
        for _ in self.out_context_words:
            if(score - ((1 / tot_req) / 2) < 0):
                return 0 
            else:
                score -= (1 / tot_req) / 2
        return score
    
    def get_fill_questions(self):
        for required_slot in self.required_slots:
            if required_slot.score == 0 and self.retries > 0:
                for question in required_slot.fill_questions:
                    if(self.is_triggering(question.trigger)):
                        question_text = question.realize_question()
                        intention = required_slot.remove_fill_question(question)
                        if intention != "MISSPELL":
                            self.retries -=1
                        return question_text, None, required_slot, intention, None
                
            for dep in required_slot.dependencies:
                if dep.score == 0 and self.retries > 0:
                    for question in dep.fill_questions:
                        if(self.is_triggering(question.trigger)):
                            question_text = question.realize_question()
                            intention = dep.remove_fill_question(question)
                            if intention != "MISSPELL":
                                self.retries -=1
                            return question_text, dep, None, intention, required_slot
        return None, None, None, None, None

        
    def __str__(self):
        required_slots_str = ""
        for required_slot in self.required_slots:
            required_slots_str += str(required_slot) + "\n"
        return "Question: " + self.question + "\nAnswer: " + self.answer + "\nState: " + self.state + "\nRetries: " + str(self.retries) + "\nRequired Slots:\n" +  required_slots_str
      

def get_dependencies(text):
    result = udipipe_api(text)
    text = result.split("\n")[7:]

    # Converte il testo in un DataFrame
    data = [line.split("\t") for line in text]
    columns = ["ID", "Form", "Lemma", "POS", "XPOS", "Feats", "Head", "DepRel", "Deps", "Misc"]
    df = pd.DataFrame(data, columns=columns)

    token_dict={}
    tokens = []
    for row in data:
        if(len(row) < 10):
            continue
        
        if(row[6]=='_'):
            continue
        head_index = int(row[6])
        head = None
        if head_index == 0:

            head = Token(0, "ROOT", "ROOT", "ROOT", "ROOT", "ROOT", "ROOT", "ROOT", "ROOT", "ROOT")
            token_dict[0] = head
        else:
            if head_index not in token_dict:
                head = Token(data[head_index - 1][0], data[head_index - 1][1], data[head_index - 1][2], data[head_index - 1][3], data[head_index - 1][4], data[head_index - 1][5], data[head_index - 1][6], data[head_index - 1][7], data[head_index - 1][8], data[head_index - 1][9])
                token_dict[head_index] = head
            else:
                head = token_dict[head_index]

        token = None
        if int(row[0]) in token_dict:
            token = token_dict[int(row[0])]
        else:
            token = Token(row[0], row[1], row[2], row[3], row[4], row[5], head, row[7], row[8], row[9])
            token_dict[int(row[0])] = token
        head.add_child(token)
        tokens.append(token)

    return tokens

def set_score_dep(dependencies, token, removed_intention,record, index_record, single_dep = False ):
    if (single_dep): # single dependency question
        dependencies[0].triggered = True
        if(removed_intention == "YES_NO" and token.lemma == "si"):
            dependencies[0].score = 0.20
        elif(removed_intention == "MISSPELL" and token.lemma == "si"):
            if dependencies[0].triggered == False:
                dependencies[0].score = 1
            else:
                dependencies[0].score = 0.60
        else:
            if token.lemma == dependencies[0].to:
                dependencies[0].score = 0.60
        if dependencies[0].score < 1:
            record.missing_dep[index_record] = True
            
    else: # frame question
        for dep in dependencies:  
            for child in token.children:
                if child.lemma == dep.to and child.dep == dep.type:
                    dep.score = 1

def set_score_slot(frame, required_slots, token, removed_intention, record):
    if (len(required_slots) == 1): # single slot question 
        required_slots[0].triggered = True
        required_slot_index = frame.required_slots.index(required_slots[0])
        if(removed_intention == "YES_NO" and token.lemma == "si"):
            required_slots[0].score = 0.20
            # state change
            frame.state = frame.state[:required_slot_index] + '1' + frame.state[required_slot_index + 1:]
        elif(removed_intention == "MISSPELL" and token.lemma == "si" ):
            if required_slots[0].triggered == False:
                required_slots[0].score = 1
            else:
                required_slots[0].score = 0.60
            # state change
            frame.state = frame.state[:required_slot_index] + '1' + frame.state[required_slot_index + 1:]
        elif(token.lemma == required_slots[0].lemma):
            required_slots[0].score = 0.60
            # state change
            frame.state = frame.state[:required_slot_index] + '1' + frame.state[required_slot_index + 1:]
            set_score_dep(required_slots[0].dependencies, token, '', record, required_slot_index + 1 )
        if required_slots[0].score > 0:
            record.set_score(required_slot_index + 1, required_slots[0].score)
        
    else: # frame question
        for required_slot in required_slots:
            if token.lemma == required_slot.lemma:
                required_slot.score = 1 
                # state change
                required_slot_index = frame.required_slots.index(required_slot)
                frame.state = frame.state[:required_slot_index] + '1' + frame.state[required_slot_index + 1:]
                set_score_dep(required_slot.dependencies, token, removed_intention, record, required_slot_index + 1 )
                record.set_score(required_slot_index + 1, 1)

def fill_frame(frame, tokens, removed_intention, record, record_index, single_slot = None, single_dep = None ):
    for token in tokens:
        if single_slot is not None:
            set_score_slot(frame, [single_slot], token, removed_intention, record)
        elif single_dep is not None:
            set_score_dep([single_dep], token, removed_intention, record, record_index, True)
        else:
            set_score_slot(frame, frame.required_slots, token, removed_intention, record)


def preprocess_answer(tokens, frame, record, index_record):
    """ per ogni token """
    for token in tokens:
        in_required = False
        for required_slot in frame.required_slots:
            slot_index = frame.required_slots.index(required_slot)
            distance = levenshtein_distance(token.lemma, required_slot.lemma)
            if distance <= 2 and distance > 0: # TODO: CREATE COSTANT OR CHANGE IT 
                trigger = "*" * len(frame.state)
                trigger = trigger[:slot_index] + '0' + trigger[slot_index + 1:]
                required_slot.add_fill_question_front(FillQuestion("Per " + token.lemma + " intendi " + required_slot.lemma + "?", trigger, ["MISSPELL"]))
                in_required = True
            for dep in required_slot.dependencies:
                distance = levenshtein_distance(token.lemma, dep.to)
                if distance <= 2 and distance > 0:
                    trigger = "*" * len(frame.state)
                    trigger = trigger[:slot_index] + '1' + trigger[slot_index + 1:]
                    dep.add_fill_question_front(FillQuestion("Per " + token.lemma + " intendi " + dep.to + "?", trigger, ["MISSPELL"]))
                    in_required = True


        if not in_required:
            if token.pos == 'NOUN':
                min_dist = len(token.lemma)
                """ controllo edit distance con il dominio """
                for word in frame.domain:
                    token_len = len(token.lemma)
                    word_len = len(word)
                    max_len = max(token_len, word_len)
                    if (abs(token_len - word_len) <=  max_len / 2):
                        dist = levenshtein_distance(token.lemma, word)
                        if dist < min_dist:
                            min_dist = dist
                if min_dist > 2: # TODO: CREATE COSTANT OR CHANGE IT
                    frame.add_out_context_word(token.lemma)
                    record.add_out_context(index_record, token.lemma)
                    return False
    return True

    
                        

def main():
    f = open('frames.json')
    json_frames = json.load(f)
    frames = []
    history = History()
    for json_frame in json_frames:
        frame = Frame(json_frame['question'], json_frame['answer'], json_frame['name'], json_frame['domain'])
        
        for required_slot in json_frame['required']: # each required slot
            req = RequiredWord(required_slot['lemma'], required_slot['weight'])
            

            for question in required_slot['fill_questions']: # each question in the required slot
                req.add_fill_question(FillQuestion(question['text'], question['trigger'], question["intention"]))
                 
            for dep in required_slot['dependencies']: # each dependency in the required slot
                new_dep = RequiredDependency(dep['to'], dep['type'], dep['weight'])
                for question_dep in dep['fill_questions']: # each question in the dependency
                    new_dep.add_fill_question(FillQuestion(question_dep['text'], question_dep['trigger'], question_dep["intention"]))
                # req.add_dependency(new_dep)
                frame.add_dependency(req, new_dep)
            
            frame.add_required_slot(req)
    
        frames.append(frame)
        
    
    print(frames[1])


    number_of_questions = 1

    total_score = 0


    for i in range(0,number_of_questions):
        record = Record()
        record.add_word(0 , frames[1].name)
        text = input(frames[1].question + "\n")
        answer_dependencies = get_dependencies(text)
       
        # history.add_record(frames[1].name, Record("fill", frames[1].question, text))
        for k in range(0,len(frames[1].required_slots)):
            record.add_word(k + 1, frames[1].required_slots[k].lemma)

            
        preproc = preprocess_answer(answer_dependencies, frames[1], record, 0)
        fill_frame(frames[1], answer_dependencies, '', record, 0)
        while (frames[1].check_frame() == False):
            print("Frame not complete")
            question, dep, slot, removed_intention, dep_slot = frames[1].get_fill_questions()

            if question is None:
                print("GG")
                if not preproc:
                    print("Non hai centrato l'argomento. Andiamo avanti...")
                break
            if not preproc:
                question = "Non hai centrato l'argomento. " +  question #TODO: create a constant array of messages
            
            if slot is not None:
                slot_index = frames[1].required_slots.index(slot)
                j = slot_index + 1
            else:
                slot_index = frames[1].required_slots.index(dep_slot)
                j = slot_index + 1

            text = input(question + "\n")
            # history.add_record(frames[1].name, Record("fill", question, text))
            
            answer_dependencies = get_dependencies(text)
            fill_frame(frames[1], answer_dependencies, removed_intention, record, j, slot, dep)
            preproc = preprocess_answer(answer_dependencies, frames[1],record, j)

        total_score += frames[1].get_final_score()
        record.set_score(0, total_score)
        history.add_record(record)
        print("record", record)
        print(frames[1])
    print("Score: " + str(((total_score * 30) / number_of_questions)))
    


if __name__ == "__main__":
    main()
    # print(execute_subcommand("Una cgf è una grammatica", "WHAT_OBJECT"))
    # print(udipipe_api("Una cgf è una grammatica"))