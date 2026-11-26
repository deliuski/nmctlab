# Lab 12: HMM - цаг агаар ба үйл ажиллагаа (Алхам 1-8)
import itertools
import numpy as np

# Алхам 1: загвар. 0 = Rainy, 1 = Sunny; 0 = walk, 1 = shop, 2 = clean
states = ["Rainy", "Sunny"]
obs_names = ["walk", "shop", "clean"]
pi = np.array([0.6, 0.4])
A = np.array([[0.7, 0.3],
              [0.4, 0.6]])
B = np.array([[0.1, 0.4, 0.5],
              [0.6, 0.3, 0.1]])


# нормчлолгүй forward, alpha нь T x N
def forward(obs, pi, A, B):
    T, N = len(obs), len(pi)
    alpha = np.zeros((T, N))
    alpha[0] = pi * B[:, obs[0]]
    for t in range(1, T):
        alpha[t] = (alpha[t - 1] @ A) * B[:, obs[t]]
    return alpha


# бүх замыг гүйлгэж P(obs)-ийг шалгах
def brute_force(obs, pi, A, B):
    total = 0.0
    for path in itertools.product(range(len(pi)), repeat=len(obs)):
        p = pi[path[0]] * B[path[0], obs[0]]
        for t in range(1, len(obs)):
            p *= A[path[t - 1], path[t]] * B[path[t], obs[t]]
        total += p
    return total


# alpha-г мөр бүрээр нормчилж P(z_t | o_1..o_t) гаргах
def filtering(obs, pi, A, B):
    alpha = forward(obs, pi, A, B)
    return alpha / alpha.sum(axis=1, keepdims=True)


# Viterbi: max авч backpointer хадгална
def viterbi(obs, pi, A, B):
    T, N = len(obs), len(pi)
    d = np.zeros((T, N))
    bp = np.zeros((T, N), dtype=int)
    d[0] = pi * B[:, obs[0]]
    for t in range(1, T):
        scores = d[t - 1][:, None] * A      # scores[i, j] = d(i) * A[i, j]
        bp[t] = scores.argmax(axis=0)
        d[t] = scores.max(axis=0) * B[:, obs[t]]
    path = [int(d[-1].argmax())]
    for t in range(T - 1, 0, -1):
        path.append(int(bp[t][path[-1]]))
    path.reverse()
    return path, d[-1].max(), d, bp


# масштабтай forward: алхам бүрт нормчилж log c_t-г нэмнэ
def forward_scaled(obs, pi, A, B):
    T, N = len(obs), len(pi)
    filt = np.zeros((T, N))
    c = np.zeros(T)
    a = pi * B[:, obs[0]]
    c[0] = a.sum()
    filt[0] = a / c[0]
    for t in range(1, T):
        a = (filt[t - 1] @ A) * B[:, obs[t]]
        c[t] = a.sum()
        filt[t] = a / c[t]
    return filt, np.log(c).sum(), c


# масштабтай backward, smoothing-д хэрэгтэй
def backward_scaled(obs, A, B, c):
    T, N = len(obs), A.shape[0]
    beta = np.ones((T, N))
    for t in range(T - 2, -1, -1):
        beta[t] = (A @ (B[:, obs[t + 1]] * beta[t + 1])) / c[t + 1]
    return beta


# log Viterbi: үржвэрийн оронд нийлбэр
def viterbi_log(obs, pi, A, B):
    with np.errstate(divide="ignore"):
        lpi, lA, lB = np.log(pi), np.log(A), np.log(B)
    T, N = len(obs), len(pi)
    d = np.zeros((T, N))
    bp = np.zeros((T, N), dtype=int)
    d[0] = lpi + lB[:, obs[0]]
    for t in range(1, T):
        scores = d[t - 1][:, None] + lA
        bp[t] = scores.argmax(axis=0)
        d[t] = scores.max(axis=0) + lB[:, obs[t]]
    path = [int(d[-1].argmax())]
    for t in range(T - 1, 0, -1):
        path.append(int(bp[t][path[-1]]))
    path.reverse()
    return path, d[-1].max()


# загвараас T урттай дараалал үүсгэх
def simulate(T, seed):
    rng = np.random.default_rng(seed)
    z = np.zeros(T, dtype=int)
    o = np.zeros(T, dtype=int)
    z[0] = rng.choice(2, p=pi)
    o[0] = rng.choice(3, p=B[z[0]])
    for t in range(1, T):
        z[t] = rng.choice(2, p=A[z[t - 1]])
        o[t] = rng.choice(3, p=B[z[t]])
    return z, o


def name(path):
    return ", ".join(states[i] for i in path)


if __name__ == "__main__":
    print("== Алхам 1 ==")
    print("A мөрийн нийлбэр:", A.sum(axis=1), " B мөрийн нийлбэр:", B.sum(axis=1))
    print("P(o1 = walk) =", round(float(pi @ B[:, 0]), 4))
    print("Sunny -> Rainy =", A[1, 0])

    print("\n== Алхам 2, 3 ==")
    obs = [0, 1, 2]
    alpha = forward(obs, pi, A, B)
    for t in range(3):
        print(f"t={t+1} {obs_names[obs[t]]:6s} {alpha[t].round(6)}")
    print("forward P =", round(alpha[-1].sum(), 6), " brute force P =", round(brute_force(obs, pi, A, B), 6))

    print("\n== Алхам 4 ==")
    f = filtering(obs, pi, A, B)
    for t in range(3):
        print(f"t={t+1} {obs_names[obs[t]]:6s} {f[t].round(4)}")
    print("маргааш:", (f[-1] @ A).round(4))

    print("\n== Алхам 5 ==")
    path, p, d, bp = viterbi(obs, pi, A, B)
    for t in range(3):
        print(f"t={t+1} d={d[t].round(5)} bp={bp[t] if t else '-'}")
    print("зам:", name(path), " p =", round(p, 5), " хувь:", round(p / alpha[-1].sum() * 100, 1))

    print("\n== Алхам 6 ==")
    obs2 = [2, 2, 0, 0, 1]
    f2 = filtering(obs2, pi, A, B)
    path2, p2, _, _ = viterbi(obs2, pi, A, B)
    for t in range(5):
        print(f"t={t+1} {obs_names[obs2[t]]:6s} P(R)={f2[t,0]:.4f} filt={states[f2[t].argmax()]:5s} vit={states[path2[t]]}")
    print("Viterbi p =", round(p2, 8))

    print("\n== Алхам 7 ==")
    z, o = simulate(1000, 0)
    alpha = forward(o, pi, A, B)
    for t in [100, 300, 500, 700, 900]:
        print(f"t={t}: {alpha[t-1].sum():.3e}")

    print("\n== Алхам 8 ==")
    print("seed  logP      filter  smooth  viterbi baseline")
    for seed in range(5):
        z, o = simulate(1000, seed)
        filt, logp, c = forward_scaled(o, pi, A, B)
        beta = backward_scaled(o, A, B, c)
        smooth = filt * beta
        smooth /= smooth.sum(axis=1, keepdims=True)
        vpath, _ = viterbi_log(o, pi, A, B)
        acc_f = (filt.argmax(1) == z).mean()
        acc_s = (smooth.argmax(1) == z).mean()
        acc_v = (np.array(vpath) == z).mean()
        acc_b = (z == 0).mean()        # үргэлж Rainy гэж таах
        print(f"{seed}  {logp:9.2f}  {acc_f:.3f}   {acc_s:.3f}   {acc_v:.3f}   {acc_b:.3f}")
