import json
from pathlib import Path

import nlpaug.augmenter.char as nac
import nlpaug.augmenter.word as naw
import nlpaug.augmenter.sentence as nas
import nlpaug.flow as nafc

from nlpaug.util import Action

# ['data'][0]['paragraphs'][0]
# - ['context']
# - ['qas'][0]
#   - ['questions']
#   - ['answers'][0]
#     - ['text']
#     - ['answer_start']

def read_and_write(path):
    # 1D, context where the model finds answer from.
    contexts = []
    # 2D, for each context, there is a list of questions regarding this context.
    questions_list = []
    # 3D, for each question, there is a list of potential answers. Each of the answer has a character level starting
    # index in the context.
    answers_starts_list_list = []
    # 3D, for each question, there is a list of potential answers. This is the text of the answer.
    texts_list_list = [] # 3D

    f = open(path)
    j = json.load(f)

    for x in j['data']:
        for y in x['paragraphs']:
            contexts.append(y['context'])
            questions = []
            answers_starts_list = []
            texts_list = []
            for z in y['qas']:
                questions.append(z['question'])
                answers_starts = []
                texts = []
                for a in z['answers']:
                    answers_starts.append(a['answer_start'])
                    texts.append(a['text'])
                answers_starts_list.append(answers_starts)
                texts_list.append(texts)
            questions_list.append(questions)
            answers_starts_list_list.append(answers_starts_list)
            texts_list_list.append(texts_list)

    new_contexts, new_questions_list, new_answers_starts_list_list, new_texts_list_list = \
        process(contexts, questions_list, answers_starts_list_list, texts_list_list)

    i, j, k = 0, 0, 0
    for x in range(len(j['data'])):
        for y in range(len(j['data'][x]['paragraphs'])):
            j['data'][x]['paragraphs'][y]['context'] = new_contexts[i]
            for z in range(len(j['data'][x]['paragraphs'][y]['context']['qas'])):
                for a in range(len(j['data'][x]['paragraphs'][y]['context']['qas'][z]['answers'])):
                    j['data'][x]['paragraphs'][y]['context']['qas'][z]['answers'][a]['answer_start'] = \
                        new_answers_starts_list_list[i][j][k]
                    j['data'][x]['paragraphs'][y]['context']['qas'][z]['answers'][a]['text'] = \
                        new_texts_list_list[i][j][k]
                    k += 1
                j += 1
            i += 1

    outfile = str(path) + "_augmented"
    json.dump(j, outfile)

def find_stop_index(sorted_changes, value):
    for i in range(len(sorted_changes)):
        if value < sorted_changes['orig_start_pos']:
            return i
    return len(sorted_changes)

def find_replaced_word(old_start_index, text, sorted_changes):
    old_end_index = old_start_index + len(text)
    delta = 0
    for change in sorted_changes:
        if old_start_index <= change['orig_start_pos'] < old_end_index:
            text = text[:change['orig_start_pos'] + delta] + change['new_token'] + \
                   text[change['orig_start_pos'] + len(change['orig_token']) + delta:]
            delta += len(change['new_token'] - change['orig_token'])
    return text


def process(contexts, questions_list, answers_starts_list_list, texts_list_list):
    new_contexts = []
    new_questions_list = questions_list
    new_answers_starts_list_list = []
    new_texts_list_list = []
    # aug = naw.SynonymAug(aug_src='wordnet', lang='eng')
    aug = naw.ContextualWordEmbsAug(model_path='bert-base-uncased', include_detail=True)
    for i in range(len(contexts)):
        augmented_context, change_log = aug.augment(contexts[i])
        new_contexts.append(augmented_context)
        sorted_changes = sorted(change_log)
        new_answers_starts_list_list.append([])
        new_texts_list_list.append([])
        for j in range(len(questions_list[i])):
            new_answers_starts_list_list[i].append([])
            new_texts_list_list[i].append([])
            for k in range(len(texts_list_list[i][j])):
                idx = find_stop_index(sorted_changes, answers_starts_list_list[i][j][k])
                total_delta = 0
                for l in range(idx):
                    total_delta += sorted_changes[l]['new_start_pos'] - sorted_changes[l]['orig_start_pos']
                new_answers_starts_list_list[i][j].append(answers_starts_list_list[i][j][k] + total_delta)
                new_texts_list_list[i][j].append( \
                    find_replaced_word(answers_starts_list_list[i][j][k], texts_list_list[i][j][k], sorted_changes))
    return new_contexts, new_questions_list, new_answers_starts_list_list, new_texts_list_list

def main():
    print("Generating augment data")
    file_paths = Path('oodomain_train').glob('*')
    for file_path in file_paths:
        print("Processing: " + str(file_path))
        read_and_write(file_path)
        break

if __name__ == '__main__':
    main()