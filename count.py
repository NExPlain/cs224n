import json

# ['data'][0]['paragraphs'][0]
# - ['context']
# - ['qas'][0]
#   - ['questions']
#   - ['answers'][0]
#     - ['text']
#     - ['answer_start']

def read(path):
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
        print(x['paragraphs'])
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

    return contexts, questions_list, answers_starts_list_list, texts_list_list

# f = open('duorc')
# j = json.load(f)
#
# lengths = []
#
# for x in j['data']:
#     print(x['paragraphs'])
#     for y in x['paragraphs']:
#         for z in y['qas']:
#             for a in z['answers']:
#                 l = len(a['text'].split())
#                 if l > 10:
#                     print(a['text'])
#                 lengths.append(l)
#
# partial = 0
# total = 0
# for i in lengths:
#     total += 1
#     if i <= 6:
#         partial += 1
#
# print(total)
# print(partial)
# print(partial / total * 100)
