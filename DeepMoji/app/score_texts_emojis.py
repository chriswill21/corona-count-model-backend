# -*- coding: utf-8 -*-

""" Use DeepMoji to score texts for emoji distribution.

The resulting emoji ids (0-63) correspond to the mapping
in emoji_overview.png file at the root of the DeepMoji repo.

Writes the result to a csv file.
"""

import DeepMoji.app.app_helper
import json
import csv
import numpy as np
from DeepMoji.deepmoji.sentence_tokenizer import SentenceTokenizer
from DeepMoji.deepmoji.model_def import deepmoji_emojis
from DeepMoji.deepmoji.global_variables import PRETRAINED_PATH, VOCAB_PATH
from flask import Flask
from flask import request

app = Flask(__name__)

@app.route("/")
def evaluate_sentiment():
    comment = [request.args.get('comment')].copy()
    print(comment)
    results = run(comment)
    results = [str(emoji) for emoji in results]
    print(results)
    return "<h1>" + ', '.join(results) + "</h1>"


OUTPUT_PATH = 'test_sentences.csv'


def top_elements(array, k):
    ind = np.argpartition(array, -k)[-k:]
    return ind[np.argsort(array[ind])][::-1]

def run(comment):
    maxlen = 30
    batch_size = 32

    print('Tokenizing using dictionary from {}'.format(VOCAB_PATH))
    with open(VOCAB_PATH, 'r') as f:
        vocabulary = json.load(f)
    st = SentenceTokenizer(vocabulary, maxlen)
    tokenized, _, _ = st.tokenize_sentences(comment)

    print('Loading model from {}.'.format(PRETRAINED_PATH))
    model = deepmoji_emojis(maxlen, PRETRAINED_PATH)
    model.summary()

    print('Running predictions.')
    prob = model.predict(tokenized)

    # Find top emojis for each sentence. Emoji ids (0-63)
    # correspond to the mapping in emoji_overview.png
    # at the root of the DeepMoji repo.
    print('Writing results to {}'.format(OUTPUT_PATH))
    scores = []
    for i, t in enumerate(comment):
        t_tokens = tokenized[i]
        t_score = [t]
        t_prob = prob[i]
        ind_top = top_elements(t_prob, 5)
        t_score.append(sum(t_prob[ind_top]))
        t_score.extend(ind_top)
        t_score.extend([str(t_prob[ind]) for ind in ind_top])
        scores.append(t_score)
        print(t_score)

    return scores[0][2:7]

    # with open(OUTPUT_PATH, 'w') as csvfile:
    #     writer = csv.writer(csvfile, delimiter=',', lineterminator='\n')
    #     writer.writerow(['Text', 'Top5%',
    #                      'Emoji_1', 'Emoji_2', 'Emoji_3', 'Emoji_4', 'Emoji_5',
    #                      'Pct_1',
    #                      'Pct_2',
    #                      'Pct_3',
    #                      'Pct_4',
    #                      'Pct_5'.encode()])
    #     for i, row in enumerate(scores):
    #         try:
    #             writer.writerow(row)
    #         except Exception:
    #             print("Exception at row {}!".format(i))
