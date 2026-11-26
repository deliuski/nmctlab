# Lab 12: HMM-ээр үгийн төрөл тэмдэглэх (Алхам 9, нэмэлт 12.8)
import numpy as np
from hmm import viterbi

tags = ["DET", "NOUN", "VERB"]
words = ["the", "a", "dog", "cat", "walk", "barks", "runs"]
w2i = {w: i for i, w in enumerate(words)}

# Алхам 9-ийн загвар
pi = np.array([0.80, 0.15, 0.05])
A = np.array([[0.05, 0.90, 0.05],
              [0.10, 0.10, 0.80],
              [0.50, 0.35, 0.15]])
B = np.array([[0.6, 0.4, 0, 0, 0, 0, 0],
              [0, 0, 0.30, 0.30, 0.20, 0.10, 0.10],
              [0, 0, 0, 0, 0.30, 0.35, 0.35]])

sentences = ["the dog barks", "the walk", "a cat walk", "the barks runs", "the dog walk"]


# өгүүлбэрийг Viterbi-ээр тэмдэглэх
def tag(sentence, pi, A, B):
    obs = [w2i[w] for w in sentence.split()]
    path, p, _, _ = viterbi(obs, pi, A, B)
    return [tags[i] for i in path], p


# 12.8: тэмдэглэсэн өгүүлбэрээс тоолж pi, A, B үнэлэх (k = add-k smoothing)
corpus = [
    "the/DET dog/NOUN barks/VERB",
    "a/DET cat/NOUN runs/VERB",
    "the/DET cat/NOUN walk/VERB",
    "a/DET dog/NOUN runs/VERB",
    "the/DET walk/NOUN",
    "a/DET walk/NOUN barks/VERB",
]


def estimate(corpus, k=0):
    t2i = {t: i for i, t in enumerate(tags)}
    pi_c = np.full(3, k, dtype=float)
    A_c = np.full((3, 3), k, dtype=float)
    B_c = np.full((3, len(words)), k, dtype=float)
    for line in corpus:
        pairs = [x.split("/") for x in line.split()]
        seq = [t2i[t] for _, t in pairs]
        pi_c[seq[0]] += 1
        for a, b in zip(seq, seq[1:]):
            A_c[a, b] += 1
        for (w, _), s in zip(pairs, seq):
            B_c[s, w2i[w]] += 1
    # мөр бүрийг нормчлох (VERB-ээс шилжилт байхгүй бол 0 үлдэнэ)
    norm = lambda M: M / np.where(M.sum(axis=-1, keepdims=True) == 0, 1, M.sum(axis=-1, keepdims=True))
    return norm(pi_c), norm(A_c), norm(B_c)


if __name__ == "__main__":
    print("== Алхам 9 ==")
    for s in sentences:
        t, p = tag(s, pi, A, B)
        print(f"{s:16s} {' '.join(t):16s} {p:.6f}")

    print("\n== 12.8 тоолсон (smoothing-гүй) ==")
    pi1, A1, B1 = estimate(corpus)
    print("pi =", pi1.round(3))
    print("A =\n", A1.round(3))
    print("B =\n", B1.round(3))
    t, p = tag("the barks runs", pi1, A1, B1)
    print("the barks runs ->", t, round(p, 6))

    print("\n== 12.8 add-1 ==")
    pi2, A2, B2 = estimate(corpus, k=1)
    print("pi =", pi2.round(3))
    print("A =\n", A2.round(3))
    print("B =\n", B2.round(3))
    for s in ["the barks runs", "the dog walk"]:
        t, p = tag(s, pi2, A2, B2)
        print(f"{s} -> {t} {p:.6f}")
