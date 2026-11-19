# sklearn-тэй харьцуулах, хэмжүүр, алдааны шинжилгээ, босго. Алхам 5-9.

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import BernoulliNB, MultinomialNB

from nb_scratch import NaiveBayes, tokenize

df = pd.read_csv('spam_emails_en.csv')
train, test = train_test_split(df, test_size=0.2, random_state=42, stratify=df['label'])

# Алхам 5. token_pattern-ийг өөрийн tokenize-тай ижил тавьсан.
# fit_transform зөвхөн train дээр, эс бөгөөс test-ийн үг сургалтад орно.
cv = CountVectorizer(token_pattern=r"[a-z0-9$%']+")
Xtr = cv.fit_transform(train['text'])
Xte = cv.transform(test['text'])
clf = MultinomialNB(alpha=1.0).fit(Xtr, train['label'])
pred = clf.predict(Xte)

print('== Алхам 5 ==')
print('матриц:', Xtr.shape)
print('sklearn accuracy:', round((pred == test['label']).mean(), 4))

nb = NaiveBayes().fit(train['text'].tolist(), train['label'].tolist())
mine = np.array([nb.predict(t) for t in test['text']])
print('миний accuracy:', round((mine == test['label']).mean(), 4))
print('хоёр таамаглалын таарал:', round((mine == pred).mean(), 4))

# Алхам 6. Confusion matrix, хэмжүүр, smoothing
print('\n== Алхам 6 ==')
cm = confusion_matrix(test['label'], pred, labels=['ham', 'spam'])
print('мөр = бодит, багана = таамаглал\n', cm)
tn, fp, fn, tp = cm.ravel()
print(f'TN={tn} FP={fp} FN={fn} TP={tp}')
print(f'гараар: precision = {tp}/({tp}+{fp}) = {tp / (tp + fp):.4f}, '
      f'recall = {tp}/({tp}+{fn}) = {tp / (tp + fn):.4f}, '
      f'F1 = {2 * tp / (2 * tp + fp + fn):.4f}')
print('sklearn:', round(precision_score(test['label'], pred, pos_label='spam'), 4),
      round(recall_score(test['label'], pred, pos_label='spam'), 4),
      round(f1_score(test['label'], pred, pos_label='spam'), 4))

print('\nalpha  accuracy precision recall  F1')
for a in (0.01, 1, 5):
    c = MultinomialNB(alpha=a).fit(Xtr, train['label'])
    p = c.predict(Xte)
    print(f'{a:<6} {(p == test["label"]).mean():.4f}   '
          f'{precision_score(test["label"], p, pos_label="spam"):.4f}    '
          f'{recall_score(test["label"], p, pos_label="spam"):.4f}  '
          f'{f1_score(test["label"], p, pos_label="spam"):.4f}')

# Алхам 7. Буруу ангилсан имэйлүүдийг хэвлэж, нүдээр уншина
print('\n== Алхам 7 ==')
proba = clf.predict_proba(Xte)
si = list(clf.classes_).index('spam')
mask = pred != test['label']
wrong = test[mask].copy()
wrong['model'] = pred[mask]
wrong['p_spam'] = proba[mask, si]
for _, r in wrong.iterrows():
    print(f"[бодит {r['label']} / модель {r['model']} / P(spam)={r['p_spam']:.4f}] {r['text'][:120]}")

# Алхам 8. Итгэл, онцлог үгс
print('\n== Алхам 8 ==')
mx = proba.max(axis=1)
print(f'0.99-ээс их итгэлтэй: {(mx > 0.99).sum()} / {len(mx)}')
print('дундаж итгэл:', round(mx.mean(), 4))
ratio = clf.feature_log_prob_[si] - clf.feature_log_prob_[1 - si]
vocab = np.array(cv.get_feature_names_out())
print('спам заадаг:', list(vocab[np.argsort(-ratio)[:8]]))
print('энгийн заадаг:', list(vocab[np.argsort(ratio)[:8]]))

# Нэмэлт даалгавар: босго. FP-ийг 10 дахин үнэтэй гэж үзэв.
print('\n== Босго ==')
print('t        TP FP FN  precision recall  зардал')
for t in (0.5, 0.9, 0.99, 0.999, 0.9999):
    p = np.where(proba[:, si] >= t, 'spam', 'ham')
    c2 = confusion_matrix(test['label'], p, labels=['ham', 'spam'])
    tn2, fp2, fn2, tp2 = c2.ravel()
    pr = tp2 / (tp2 + fp2) if tp2 + fp2 else 0
    print(f'{t:<8} {tp2:<2} {fp2:<2} {fn2:<3} {pr:.4f}    {tp2 / (tp2 + fn2):.4f}  {10 * fp2 + fn2}')

# Алхам 9. Өөрийн 10 имэйл. 4 ба 9 дэх нь хэцүү тохиолдол.
print('\n== Алхам 9 ==')
my = [
    ('ham', 'Can we move the standup to 10:30 tomorrow'),
    ('ham', 'The database homework is due on Friday, do you have the slides'),
    ('ham', 'Mom asked you to buy bread on the way home'),
    ('ham', 'The museum has free entry on Sunday, want to go'),
    ('ham', 'Your library book is due next week, please renew it online'),
    ('spam', 'Congratulations you won a $1,000 gift card, click now to claim'),
    ('spam', 'Cheap pills and watches, 70% discount, order today'),
    ('spam', 'Double your bitcoin, guaranteed returns, limited spots'),
    ('spam', 'Hi, I noticed your profile and would like to share an opportunity'),
    ('spam', 'URGENT: verify your bank account or it will be suspended'),
]
X_my = cv.transform([t for _, t in my])
p_my = clf.predict(X_my)
pr_my = clf.predict_proba(X_my)[:, si]
ok = 0
for (lab, text), p, pp in zip(my, p_my, pr_my):
    ok += lab == p
    print(f'{lab:4s} -> {p:4s}  P(spam)={pp:.4f}  {"зөв" if lab == p else "БУРУУ"}  | {text[:52]}')
print(f'accuracy: {ok}/10')

# шинэ үгтэй имэйл ба кирилл
for t in ['Quantum computer entanglement research seminar',
          'Та 1,000,000 төгрөг хожлоо, одоо дарна уу']:
    toks = tokenize(t)
    k = sum(1 for w in toks if w in cv.vocabulary_)
    print(f'P(spam)={clf.predict_proba(cv.transform([t]))[0, si]:.4f} '
          f'(таарсан {k}/{len(toks)} үг) | {t}')

print('\nөөр загвар:')
bnb = BernoulliNB(alpha=1.0).fit(Xtr, train['label'])
print('BernoulliNB:', round((bnb.predict(Xte) == test['label']).mean(), 4))
tv = TfidfVectorizer(token_pattern=r"[a-z0-9$%']+")
tclf = MultinomialNB(alpha=1.0).fit(tv.fit_transform(train['text']), train['label'])
tp_ = tclf.predict(tv.transform(test['text']))
print('TF-IDF:', round((tp_ == test['label']).mean(), 4),
      '| recall:', round(recall_score(test['label'], tp_, pos_label='spam'), 4))
