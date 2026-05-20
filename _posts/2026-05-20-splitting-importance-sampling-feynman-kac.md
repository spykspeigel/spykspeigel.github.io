---
layout: post
title: "Splitting, Importance Sampling, and the Feynman--Kac Semigroup"
subtitle: "Notes on cloning algorithms, tilted semigroups, and changes of path measure"
date: 2026-05-20
tags: [large-deviations, stochastic-processes, feynman-kac, importance-sampling, rare-events, python]
mathjax: true
readtime: true
comments: true
social-share: true
share-title: "Splitting, Importance Sampling, and the Feynman--Kac Semigroup"
share-description: "A minimal two-state example showing why splitting acts on a weighted population while importance sampling changes the stochastic process."
thumbnail-img: ""
---

This post explains the difference between two simulation ideas that often appear together in large-deviation theory:

1. **splitting / cloning**, which is a particle algorithm for a Feynman--Kac weighted semigroup;
2. **importance sampling**, which changes the stochastic process itself and then corrects the change of measure.

The distinction is subtle but important. Splitting acts at the level of an **ensemble of weighted trajectories**. Importance sampling acts at the level of the **process law**.

We will use the simplest possible example throughout.

---

## 1. A very simple process

Consider a discrete-time process

$$
X_1, X_2, \ldots, X_n,
$$

where each \(X_t\) is either \(0\) or \(1\). Under the original process \(P\), suppose

$$
P(X_t = 1) = \frac12,
\qquad
P(X_t = 0) = \frac12.
$$

So a trajectory is just a sequence such as

$$
(1,0,0,1,1,0,\ldots).
$$

Let

$$
S_n = \sum_{t=1}^n X_t.
$$

This counts how many times the process visits state \(1\). The time average is

$$
A_n = \frac{1}{n} S_n.
$$

For large \(n\), typical trajectories have approximately half zeros and half ones, so typically

$$
A_n \approx \frac12.
$$

Trajectories with \(A_n\) much larger than \(1/2\) are rare under the original process.

---

## 2. The generating function

In large-deviation theory one often studies the exponential generating function

$$
Z_n(k)
=
\mathbb{E}_P\left[e^{k S_n}\right].
$$

Written as a sum over trajectories,

$$
Z_n(k)
=
\sum_{\text{paths}}
P(\text{path}) e^{k S_n(\text{path})}.
$$

The exponential factor

$$
e^{k S_n(\text{path})}
$$

changes the importance of different trajectories. If \(k>0\), trajectories with many ones receive a large weight. If \(k<0\), trajectories with many zeros receive a large weight.

So the object

$$
P(\text{path}) e^{k S_n(\text{path})}
$$

is a **weighted path measure**. It is not normalized. Its total mass is exactly

$$
Z_n(k).
$$

That is the key Feynman--Kac idea:

$$
\text{Markov path probability}
\quad \times \quad
\text{exponential trajectory weight}.
$$

For this toy model, the exact value is easy to compute. Since the variables are independent,

$$
\mathbb{E}\left[e^{k X_t}\right]
=
\frac12 e^{0} + \frac12 e^k
=
\frac{1+e^k}{2}.
$$

Therefore

$$
Z_n(k)
=
\left(\frac{1+e^k}{2}\right)^n.
$$

We will use this exact answer to check the simulations.

---

## 3. Direct Monte Carlo

The most obvious estimator is direct simulation. Generate many trajectories under the original process \(P\), compute \(e^{kS_n}\), and average.

Mathematically,

$$
Z_n(k)
\approx
\frac{1}{M}\sum_{i=1}^M e^{k S_n^{(i)}},
$$

where each trajectory is sampled from \(P\).

This is simple, but it can have very large variance. For \(k>0\), the estimate is dominated by rare trajectories with unusually many ones. Direct Monte Carlo may not see enough of those rare trajectories.

---

## 4. Splitting / cloning

Splitting, also called cloning, keeps the original dynamics but adds a selection mechanism.

At each time step:

1. particles evolve using the original process \(P\);
2. each particle receives a Feynman--Kac weight;
3. high-weight particles are copied;
4. low-weight particles are killed;
5. the population size is kept approximately fixed.

For the toy model, the one-step weight is

$$
w_t = e^{k X_t}.
$$

If \(k>0\), then a particle that lands in state \(1\) gets weight \(e^k\), while a particle that lands in state \(0\) gets weight \(1\).

So particles that visit \(1\) are more likely to be copied.

The algorithm has the structure

$$
\text{mutation by original dynamics}
\quad + \quad
\text{selection by exponential weight}.
$$

This is why splitting is naturally understood as an algorithm for the Feynman--Kac semigroup. It simulates the weighted trajectory ensemble by using a population of particles.

The crucial point is this:

$$
\boxed{\text{splitting does not first replace the process by a new process.}}
$$

Instead, it repeatedly evolves particles under the original dynamics and then performs selection according to the Feynman--Kac weights.

---

## 5. Importance sampling

Importance sampling takes a different route.

Instead of simulating the original process \(P\), we simulate a new process \(Q\). For example, if \(k>0\), trajectories with many ones are important, so we choose

$$
Q(X_t = 1) = q,
\qquad
Q(X_t = 0) = 1-q,
$$

with

$$
q > \frac12.
$$

For example, take \(q=0.75\). Under \(Q\), ones are no longer as rare.

But now the simulated process is not the original process. Therefore we must correct the bias using the likelihood ratio

$$
\frac{P(\text{path})}{Q(\text{path})}.
$$

The exact identity is

$$
Z_n(k)
=
\mathbb{E}_P\left[e^{kS_n}\right]
=
\mathbb{E}_Q\left[
e^{kS_n}\frac{P(\text{path})}{Q(\text{path})}
\right].
$$

This is importance sampling.

So importance sampling changes the process itself:

$$
\boxed{\text{importance sampling modifies the path law.}}
$$

Then the likelihood ratio corrects for that modification.

---

## 6. The distinction in one table

| Method | What is changed? | Main idea |
|---|---|---|
| Direct Monte Carlo | Nothing | Sample the original process and average the exponential weights. |
| Splitting / cloning | The population of trajectories | Keep original dynamics, but clone high-weight trajectories and kill low-weight ones. |
| Importance sampling | The process law | Simulate a different process \(Q\), then correct by \(P/Q\). |

The clean conceptual statement is:

$$
Z_n(k)
=
\sum_{\text{paths}} P(\text{path}) e^{kS_n(\text{path})}.
$$

Splitting tries to represent this weighted sum by a population dynamics.

Importance sampling rewrites the same sum as

$$
Z_n(k)
=
\sum_{\text{paths}} Q(\text{path})
\left[
e^{kS_n(\text{path})}
\frac{P(\text{path})}{Q(\text{path})}
\right].
$$

That is the mathematical difference.

---

## 7. Basic Python code

The following code compares the three estimators.

```python
import numpy as np


def exact_Z(n, k):
    """
    Exact generating function for the toy model.

    X_t is Bernoulli(1/2), so

        E[exp(k X_t)] = (1 + exp(k)) / 2.

    Therefore

        Z_n(k) = [(1 + exp(k)) / 2]^n.
    """
    return ((1.0 + np.exp(k)) / 2.0) ** n


def direct_monte_carlo(n, k, n_paths, seed=0):
    """
    Direct Monte Carlo under the original process P.

    Original process:
        P(X_t = 1) = 1/2
        P(X_t = 0) = 1/2

    Estimator:
        Z_n(k) ≈ average of exp(k sum_t X_t).
    """
    rng = np.random.default_rng(seed)

    X = rng.binomial(1, 0.5, size=(n_paths, n))
    S = X.sum(axis=1)
    weights = np.exp(k * S)

    return weights.mean()


def importance_sampling(n, k, n_paths, q, seed=1):
    """
    Importance sampling.

    We simulate a biased process Q:

        Q(X_t = 1) = q
        Q(X_t = 0) = 1 - q.

    The correction factor is P(path) / Q(path).
    """
    rng = np.random.default_rng(seed)

    X = rng.binomial(1, q, size=(n_paths, n))
    S = X.sum(axis=1)

    log_P = n * np.log(0.5)
    log_Q = S * np.log(q) + (n - S) * np.log(1.0 - q)

    log_weight = k * S + log_P - log_Q
    weights = np.exp(log_weight)

    return weights.mean()


def splitting_cloning(n, k, n_particles, seed=2):
    """
    Splitting / cloning algorithm.

    At each time step:

    1. mutate particles using the original process P;
    2. assign Feynman--Kac weights w_i = exp(k X_t^i);
    3. resample particles according to those weights;
    4. multiply the running estimate by the average weight.
    """
    rng = np.random.default_rng(seed)

    particles = np.zeros(n_particles, dtype=int)
    Z_estimate = 1.0

    for t in range(n):
        # Mutation under the original process P
        particles = rng.binomial(1, 0.5, size=n_particles)

        # Feynman--Kac weights
        weights = np.exp(k * particles)

        # One-step normalization estimate
        mean_weight = weights.mean()
        Z_estimate *= mean_weight

        # Selection / resampling
        probabilities = weights / weights.sum()
        indices = rng.choice(
            n_particles,
            size=n_particles,
            replace=True,
            p=probabilities,
        )
        particles = particles[indices]

    return Z_estimate


def run_experiment():
    n = 50
    k = 0.5

    n_paths = 50_000
    n_particles = 5_000

    q = 0.75

    Z_true = exact_Z(n, k)
    Z_direct = direct_monte_carlo(n, k, n_paths)
    Z_is = importance_sampling(n, k, n_paths, q)
    Z_split = splitting_cloning(n, k, n_particles)

    print("Parameters")
    print("----------")
    print(f"n = {n}")
    print(f"k = {k}")
    print(f"importance sampling q = {q}")
    print()

    print("Estimates of Z_n(k)")
    print("-------------------")
    print(f"Exact:               {Z_true:.6e}")
    print(f"Direct MC:           {Z_direct:.6e}")
    print(f"Importance sampling: {Z_is:.6e}")
    print(f"Splitting/cloning:   {Z_split:.6e}")
    print()

    print("Relative errors")
    print("---------------")
    print(f"Direct MC:           {(Z_direct - Z_true) / Z_true:.3%}")
    print(f"Importance sampling: {(Z_is - Z_true) / Z_true:.3%}")
    print(f"Splitting/cloning:   {(Z_split - Z_true) / Z_true:.3%}")


if __name__ == "__main__":
    run_experiment()
```

---

## 8. Where the difference appears in the code

In importance sampling, the process is changed here:

```python
X = rng.binomial(1, q, size=(n_paths, n))
```

If \(q\neq 1/2\), the simulated process is no longer the original process.

The correction is here:

```python
log_weight = k * S + log_P - log_Q
```

This is the logarithm of

$$
e^{kS_n} \frac{P(\text{path})}{Q(\text{path})}.
$$

In the splitting algorithm, by contrast, mutation uses the original process:

```python
particles = rng.binomial(1, 0.5, size=n_particles)
```

Then the Feynman--Kac weights are applied:

```python
weights = np.exp(k * particles)
```

and the population is resampled:

```python
indices = rng.choice(
    n_particles,
    size=n_particles,
    replace=True,
    p=weights / weights.sum(),
)
```

Thus splitting does not directly replace \(P\) by a new transition law \(Q\). It uses population selection to represent the weighted Feynman--Kac evolution.

---

## 9. A final conceptual summary

The original object is

$$
Z_n(k)
=
\mathbb{E}_P\left[e^{kS_n}\right].
$$

Direct Monte Carlo samples from \(P\) and averages \(e^{kS_n}\).

Splitting keeps the original dynamics but uses cloning and killing to represent the weighted ensemble

$$
P(\text{path})e^{kS_n(\text{path})}.
$$

Importance sampling introduces a new process \(Q\) and writes

$$
Z_n(k)
=
\mathbb{E}_Q\left[
e^{kS_n}\frac{P(\text{path})}{Q(\text{path})}
\right].
$$

So the shortest correct statement is:

$$
\boxed{\text{Splitting changes the population; importance sampling changes the process.}}
$$

That is the basic distinction behind the statement that splitting is an algorithm for generating the Feynman--Kac semigroup, whereas importance sampling operates at the level of the stochastic process itself.
