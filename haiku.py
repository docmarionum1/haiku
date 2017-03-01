import json
import pathlib
import random
import re

from bottle import run, route, template, view
import pandas as pd

DICT_FILE = 'phoneme-groups-with-syllables.json'
CORPUS_DIR = 'corpus'



def build_model():
    # Load dictionary of words with syllable counts
    dictionary = {}
    with open(DICT_FILE) as f:
        for l in f:
            j = json.loads(l)
            dictionary[j['word']] = len(j['syllables'])

    # Convert into a DataFrame and drop any with more than 7 syllables.
    dict_df = pd.DataFrame.from_records([(k, dictionary[k]) for k in dictionary])
    dict_df = dict_df[dict_df[1] <= 7]

    # Load training text
    corpus = []
    regex = re.compile("[^A-Z\s'-\.]")
    for path in pathlib.Path(CORPUS_DIR).glob('*'):
        with open(str(path)) as f:
            corpus = corpus + [
                i.split() for i in re.split(
                    r'[\.!\?;]',
                    regex.sub('',
                        f.read().upper().replace(",", "").replace("--", " ")
                    )
                )
            ]


    # 2 word markov model
    model2 = {}
    for c in corpus:
        for i in range(len(c) - 1):
            w1 = c[i]
            w2 = c[i+1]

            if w1 not in model2:
                model2[w1] = {}

            if w2 not in model2[w1]:
                model2[w1][w2] = {'count': 1, 'end': 0, 'start': 0}
            else:
                model2[w1][w2]['count'] += 1

            if i == (len(c) - 2):
                model2[w1][w2]['end'] += 1
            if i == 0:
                model2[w1][w2]['start'] += 1

    records = [
        (
            w1, w2,
            model2[w1][w2]['count'],
            model2[w1][w2]['end'],
            model2[w1][w2]['start']
        )
        for w1 in model2 for w2 in model2[w1]
    ]

    model2_df = pd.DataFrame.from_records(records).rename(columns={
        0: 'word1', 1:'word2', 2:'count', 3: 'end', 4: 'start'}
    )
    model2_df = model2_df.merge(
        dict_df.rename(columns={0: 'word2', 1: 'syllables'}), on='word2'
    )
    model2_df = model2_df.merge(
        dict_df.rename(columns={0: 'word1', 1: 'syllables_word1'}), on='word1'
    )

    g = model2_df.groupby('word2')
    m = g.sum().reset_index()[['word2', 'end']].merge(
        g.sum().reset_index()[['word2', 'count']], on='word2'
    )
    m['end_percent'] = m['end']/m['count']
    model2_df = model2_df.merge(m[['word2', 'end_percent']], on='word2')

    g = model2_df.groupby('word1')
    m = g.sum().reset_index()[['word1', 'start']].merge(
        g.sum().reset_index()[['word1', 'count']], on='word1'
    )
    m['start_percent'] = m['start']/m['count']
    model2_df = model2_df.merge(m[['word1', 'start_percent']], on='word1')

    model3 = {}
    for c in corpus:
        for i in range(len(c) - 2):
            w1 = c[i]
            w2 = c[i+1]
            w3 = c[i+2]

            if w1 not in model3:
                model3[w1] = {}

            if w2 not in model3[w1]:
                model3[w1][w2] = {}

            if w3 not in model3[w1][w2]:
                model3[w1][w2][w3] = {'count': 1, 'end': 0}
            else:
                model3[w1][w2][w3]['count'] += 1

            if i == (len(c) - 3):
                model3[w1][w2][w3]['end'] += 1

    records = []
    for w1 in model3:
        for w2 in model3[w1]:
            for w3 in model3[w1][w2]:
                records.append((
                    w1, w2, w3,
                    model3[w1][w2][w3]['count'], model3[w1][w2][w3]['end']
                ))

    model3_df = pd.DataFrame.from_records(records).rename(columns={
        0: 'word1', 1:'word2', 2: 'word3', 3:'count', 4: 'end'
    })
    model3_df = model3_df.merge(dict_df.rename(columns={
        0: 'word3', 1: 'syllables'}), on='word3'
    )

    g = model3_df.groupby('word3')
    m = g.sum().reset_index()[['word3', 'end']].merge(
        g.sum().reset_index()[['word3', 'count']], on='word3'
    )
    m['end_percent'] = m['end']/m['count']
    model3_df = model3_df.merge(m[['word3', 'end_percent']], on='word3')

    model2_df.to_csv('model2.csv', index=False)
    model3_df.to_csv('model3.csv', index=False)

    return model2_df, model3_df

def uppercase(matchobj):
    return matchobj.group(0).upper()

def capitalize(s):
    return re.sub('^([a-z])|[\.|\?|\!]\s*([a-z])|\s+([a-z])(?=\.)', uppercase, s)

def get_first_word(model2_df):
    subset = model2_df[
        (model2_df['syllables_word1'] <= 5) & (model2_df['start_percent'] > .1)
    ]
    w = subset.sample(n=1).iloc[0]
    return {'word': w['word1'], 'syllables': w['syllables_word1']}

def get_word(previous_words, remaining, line, model2_df, model3_df):
    if len(previous_words) >= 2:
        subset = model3_df[
            (model3_df['word1'] == previous_words[-2]['word']) &
            (model3_df['word2'] == previous_words[-1]['word']) &
            (model3_df['syllables'] <= remaining)
        ]

        if line == 2:
            subset = subset[
                (subset['syllables'] < remaining) | (subset['end_percent'] > .1)
            ]

        if len(subset) == 0:
            return get_word([previous_words[-1]], remaining, line)

        w = subset.sample(n=1, weights='count').iloc[0]

        return {'word': w['word3'], 'syllables': w['syllables']}
    else:
        subset = model2_df[
            (model2_df['word1'] == previous_words[-1]['word']) &
            (model2_df['syllables'] <= remaining)
        ]

        if line == 2:
            subset = subset[
                (subset['syllables'] < remaining) | (subset['end_percent'] > .1)
            ]

        w = subset.sample(n=1, weights='count').iloc[0]

        return {'word': w['word2'], 'syllables': w['syllables']}

def generate_haiku(model2_df, model3_df):
    w = get_first_word(model2_df)
    previous_words = [w]
    haiku = [[w], [], []]
    counts = [5 - w['syllables'], 7, 5]

    for i,l in enumerate(counts):
        remaining = l
        while remaining > 0:
            try:
                w = get_word(previous_words, remaining, i, model2_df, model3_df)
                previous_words.append(w)
                haiku[i].append(w)
                remaining -= w['syllables']
            except Exception as e:
                raise e
                previous = haiku[i].pop()
                previous_words.pop()
                remaining += previous['syllables']


    return capitalize(
        "<br/>".join([" ".join([w['word'] for w in l]) for l in haiku]).lower()
    )

@route('/')
@view('index')
def index():
    return {}

@route('/haiku')
def haiku_api():
    generated = False
    while not generated:
        try:
            haiku = generate_haiku(model2_df, model3_df)
            generated = True
        except:
            pass

    return dict(haiku=haiku)

if __name__ == '__main__':
    try:
        model2_df = pd.read_csv('model2.csv')
        model3_df = pd.read_csv('model3.csv')
    except:
        model2_df, model3_df = build_model()


    run(host='localhost', port=9876)
