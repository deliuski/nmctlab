# Naive Bayes-ийг sklearn ашиглахгүйгээр бичсэн. Алхам 1-4.

import math
import re
from collections import Counter

import pandas as pd
from sklearn.model_selection import train_test_split


# жижиг үсэг болгоод латин үсэг, тоо, $ % ' тэмдэгтээс бүрдэх үгсийг салгана
def tokenize(s):
    return re.findall(r"[a-z0-9$%']+", s.lower())


class NaiveBayes:
    def __init__(self, alpha=1.0):
        self.alpha = alpha
        self.log_prior = {}
        self.counts = {}   # анги бүрт нэг Counter
        self.total = {}
        self.vocab = set()

    def fit(self, texts, labels):
        n = len(texts)
        by_class = Counter(labels)
        for c in by_class:
            self.log_prior[c] = math.log(by_class[c] / n)
            self.counts[c] = Counter()

        for text, c in zip(texts, labels):
            toks = tokenize(text)
            self.counts[c].update(toks)
            self.vocab.update(toks)

        for c in self.counts:
            self.total[c] = sum(self.counts[c].values())
        return self

    # log P(c) + log P(w|c)-уудын нийлбэр. Үгсийн санд байхгүй үгийг алгасна.
    def log_score(self, text, c):
        V = len(self.vocab)
        score = self.log_prior[c]
        for w in tokenize(text):
            if w not in self.vocab:
                continue
            p = (self.counts[c][w] + self.alpha) / (self.total[c] + self.alpha * V)
            score += math.log(p)
        return score

    def predict(self, text):
        return max(self.log_prior, key=lambda c: self.log_score(text, c))

    # хоёр оноог нормчилж P(spam)-ыг гаргана
    def proba(self, text, c='spam'):
        scores = {k: self.log_score(text, k) for k in self.log_prior}
        m = max(scores.values())
        exp = {k: math.exp(v - m) for k, v in scores.items()}
        return exp[c] / sum(exp.values())


if __name__ == '__main__':
    # Алхам 1. Өгөгдөл
    df = pd.read_csv('spam_emails_en.csv')
    print('== Алхам 1 ==')
    print('хэмжээ:', df.shape)
    print(df['label'].value_counts().to_dict())
    df['n_words'] = df['text'].str.split().str.len()
    print('дундаж үгийн тоо:', df.groupby('label')['n_words'].mean().round(2).to_dict())
    print('хамгийн урт:', df['n_words'].max(), 'үг, шошго:',
          df.loc[df['n_words'].idxmax(), 'label'])

    # Алхам 2. Зургаан имэйлийн жишээг кодоор шалгав (гараар бодсон нь тайланд байгаа)
    print('\n== Алхам 2 ==')
    small_texts = ['free money now', 'win free prize now', 'free gift',
                   'meeting at noon', 'project meeting now', 'lunch at noon']
    small_labels = ['spam', 'spam', 'spam', 'ham', 'ham', 'ham']
    nb_small = NaiveBayes().fit(small_texts, small_labels)
    V = len(nb_small.vocab)
    print('V =', V, '| token: spam =', nb_small.total['spam'], ', ham =', nb_small.total['ham'])
    for c in ('spam', 'ham'):
        for w in ('free', 'now'):
            cnt = nb_small.counts[c][w]
            p = (cnt + 1) / (nb_small.total[c] + V)
            print(f'P({w} | {c}) = ({cnt} + 1) / ({nb_small.total[c]} + {V}) = {p:.4f}')
    for m in ('free now', 'meeting now', 'free meeting'):
        print(f'P(spam | "{m}") = {nb_small.proba(m):.4f} -> {nb_small.predict(m)}')

    # Алхам 3. Token, хуваалт
    print('\n== Алхам 3 ==')
    print(tokenize("YOU WON $1,000,000!!! Click NOW"))
    train, test = train_test_split(df, test_size=0.2, random_state=42, stratify=df['label'])
    print('train/test:', len(train), len(test), test['label'].value_counts().to_dict())

    # Алхам 4. Сургах ба шалгах
    print('\n== Алхам 4 ==')
    nb = NaiveBayes().fit(train['text'].tolist(), train['label'].tolist())
    print('үгсийн сан:', len(nb.vocab))
    pred = [nb.predict(t) for t in test['text']]
    acc = sum(p == y for p, y in zip(pred, test['label'])) / len(test)
    print('accuracy:', round(acc, 4))

    for m in ['Congratulations winner, click the link to claim your free prize',
              'What time does the database class start tomorrow',
              'There is a discount book sale on campus, want to go together']:
        print(f'  {nb.predict(m):4s}  P(spam) = {nb.proba(m):.4f}  | {m[:45]}')

    # log хэрэглэхгүй бол урт имэйлд underflow болно
    print('0.001 ** 200 =', 0.001 ** 200)
