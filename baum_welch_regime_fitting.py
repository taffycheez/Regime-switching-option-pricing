"""
Baum-Welch Implementation on S&P500, Classifying into 5 Reigmes 
"""

import numpy as np
import pandas as pd
import yfinance as yf
import torch
from pomegranate.hmm import DenseHMM
from pomegranate.distributions import Normal
from scipy.stats import norm
import warnings
warnings.filterwarnings("ignore")




# 1. Data
#
# Use daily log-returns: r_t = ln(P_t / P_{t-1}).
#
# Log-returns used over simple returns because
#   (a) Time-additive: multi-day log-return = sum of daily log-returns.
#   (b) Closer to normally distributed, suits the Gaussian HMM.
#   (c) Prevent negative prices in GBM simulation (since exp is always > 0).


def fetch_sp500(start="2000-01-01", end="2026-01-01") -> pd.Series:
    """
    Download S&P500 daily log-returns from Yahoo Finance
    
    Parameters
    -------------
    start : str
        Start date(YYY-MM-DD). 2000-01-01 is the start of the available dataset
    end : str
        End date, chose 2026/01/01 arbitrarily
        
        
    Returns
    -------------
    pd.Series
        Daily log-returns, indexed by date.
    """
    
    # yfinance returns OHLCV, we only need 'Cllose'
    # squeeze() converts a single-column DataFrame so a Series.
    
    print("Downloading S&P 500 data...")
    raw     = yf.download("^GSPC", start=start, end=end, progress=True)
    closes  = raw["Close"].squeeze().dropna()
    print("Download complete. Processing returns...")
    
    log_ret = np.log(closes / closes.shift(1)).dropna()
    
    print(f"Loaded {len(log_ret)} daily log-returns  "
          f"({log_ret.index[0].date()} -> {log_ret.index[-1].date()})")
    return log_ret


# 2. Feature Matrix
#
# Makes regime identification within Baum-Welch more reliable, compared to just
# the log-return series
#
# Add 2 features to the observation vector
#
# Feature 0: Raw log-return (r_t)
#       The immediate price signal. Negative in bear regimes, positive in bull.
#
# Feature 1: Rolling reasised volatility (RV_t)
#       std(r_{t-window+1}, ..., r_t) over an approx. 1 month window.
#       High RV clarifies crisis regimes from calm ones, even when the
#       direction of r_t is unclear. Also, RV is persistent
#       (volatility clustering), so it gives the HMM strong sequential signal.
#
# Feature 2: Return z-score (z_t)
#       z_t = (r_t - rolling_mean_t) / RV_t
#       Normalises the return by recent volatility. A z-score of -3 is an
#       extreme negative return (relative to the current volatility environment),
#       which helps contextualise, e.g., a -1% move in a calm market (extreme)
#       from a -1% move during a crash (unremarkable).


def build_features(log_ret, window=21) -> np.ndarray:
    """
    Builds a (T, 3) observation matrix for the HMM fro daily log-returns.
    
    Parameters
    -------------
    log_ret : pd.Series
        Daily log-returns (length T)
    window : int
        Rolling window for volatility and mean estimation (default:21 days)
    
    Returns
    -------------
    Observations Matrix : np.ndarray, shape (T, 3)
        Columns: [log_return, rolling_vol, z_score]
        NaN values in early rows (before window is filled) are back filled
    """
    
    print("Building feature matrix...")
    r = log_ret.values
    print("  Computing rolling volatility...")
    rv = pd.Series(r).rolling(window).std().bfill().values
    print("  Computing rolling mean and z-scores...")
    mu_roll = pd.Series(r).rolling(window).mean().bfill().values
    z = np.where(rv > 1e-10, (r - mu_roll) / rv, 0.0)
    print(f"  Feature matrix complete. Shape: {np.column_stack([r, rv, z]).shape}")
    return np.column_stack([r, rv, z])


# 3. Hidden Markov Model using Baum,-Welch and Viterbi
#
# Setup:
#   Hidden states            S = {0, 1, 2, 3, 4} (extreme bear ... extreme_bull)
#   Observations             x_t                 (feature vector each dat)
#   Transition Probability   P(s_t | s_{t-1}) = P[s_{t-1}, s_t]    (learned)
#   Emission Probabillity    P(x_t | s_t) = N(x_t; mu_k, sigma_k)  (learned)
#
# Baum-Welch (Expectation Maximisation for HMM)
#   - E-step: Given current parameters, compute the probability of being in 
#             each state at each time step (forward-backward algorithm)
#   - M-Step: Update transition matrix and emission partameters to maximise
#             expected log-likelihood
#   - Iterates until convergence. Garunteed to find a local maximum of the
#     likelihood PO(observations | model)
#
# Viterbi Decoding
#   - After fitting, finds the single most probable squence of hidden states
#     (the "Viterbi path") via dynamic programmic.
#   - We use this path so assign each historical day to a regime,
#     then compute mu and sigma per regime from raw returns



REGIME_LABELS = ["extreme_bear", "bear", "nuetral", "bull", "extreme_bull"]
N_REGIMES = 5


def fit_hmm(features, n_regimes=N_REGIMES, n_iter=100) -> DenseHMM:
    """
    Fit a Gaussian HMM to the feature matrix using pomegranate's Baum-Wlech
    
    Each hidden state models its emissions as independent univariate Gaussians
    per feature (correlations between features are ignored). 
    DenseHMM learns a full KxK transition matrix.
    
    Parameters:
    -------------
    features : np.ndarray, shape(T, 3)
        Observation matrix from build_features()
    n_regimes : int
        Number of hidden states. 5 is chosen to model:
        extreme_bear, bear, neutral, bull, extreme_bull
    n_iter : int
        Maximum EM iterations
    
    
    Returns:
    -------------
    DenseHMM
        Fitted pomegranate HMM with learned transition matrix and emissions
    """
    
    print(f"Initialising {n_regimes}-state HMM...")
    # Initialise one Normal distribution per regime (pomegranate will fit mu/sigma)
    distributions = [Normal() for _ in range(n_regimes)]
    
    model = DenseHMM(distributions=distributions, max_iter=n_iter, verbose=False)
    
    # pomegranate expects input shape (n_sequences, T, D)
    # We have one long sequence, so unsqueexe adds the leading dimension (1, T, 3)
    X_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
    # Set seeds for reproducibility
    torch.manual_seed(42)
    np.random.seed(42)
    print("Running Baum-Welch EM...")
    model.fit(X_tensor)
        
    print("HMM fitted via pomegranate Baum-Welch")
    return model


def extract_regime_params(model, log_ret, features):
    """
    Decodes regimes via Viterbi and computes mu_k, sigma_k for all regimes
    
    After Baum-Welch, the HMM's internal state numbering is arbitrary.
    We re-sort states by ascending mean return so that:
        state 0 -> extreme_bear (most negative average return)
        state 4 -> extreme_bull (most positive average return)
    
    Parameters:
    -------------
    model : DenseHMM
        Fitted pomegranate HMM object
    log_ret : pd.Sereis
        Raw daily log-returns (used to compute mu_k, simga_k for each regime
    features : np.ndarray, shape (T, 3)
       Feature matrix passed to model.predict() for Viterbi decoding
       
    
    Returns:
    -------------
    sorted params : dict
        Mapping {regime_index: {"mu": flaot, "simga": float, "count: int}}
        sorted so that index 0 -> most bearish, 4 -> most bullish
    P : np.ndarray, shape (5, 5)
        Transition probability matrix P[i, j] = P(next=j | curent=i),
        re-indexed to match the sorted regime labels
    hidden_sorted : np.ndarray, shape (t, )
        Viterbi state sequence in sorted regime indicies (0, ..., 4)
    """
    
    print("Running Viterbi decoding...")
    X_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
    
    hidden_states = model.predict(X_tensor).squeeze().numpy()
    print("Viterbi complete. Computing per-regime statistics...")
    r = log_ret.values
    K = len(model.distributions)
    
    # Compute (mu, simga) for each raw HMM state
    params = {}
    for k in range(K):
        mask = (hidden_states == k)
        ret_k = r[mask]
        params[k] = {
            "mu":    ret_k.mean() if len(ret_k) > 1 else 0.0,
            "sigma": ret_k.std()  if len(ret_k) > 1 else 1e-4,
            "count": int(mask.sum()),
        }
        
    # Re-sort by ascending mean return
    # 'order' is a list of original state indices sorted by thier mean return
    # 'relabel' maps old index -> new index (0 = lowest mu, 4 = highest mu)
    order   = sorted(params, key=lambda k: params[k]["mu"])
    relabel = {old: new for new, old in enumerate(order)}
    
    # Rebuild params dict with new order
    sorted_params = dict(sorted(
        {relabel[k]: params[k] for k in params}.items()
        ))
    
    # Reindex transition matrix
    # model.dense_transition_matrix() returns a (K+2, K+2) tensor that includes
    # start and end state rows/cols; we slice out only the K×K interior.    
    P_raw = torch.exp(model.edges).numpy()[:K, :K]    
    P     = np.zeros_like(P_raw)
    for old_i, new_i in relabel.items():
        for old_j, new_j in relabel.items():
            P[new_i, new_j] = P_raw[old_i, old_j]
    
    hidden_sorted = np.array([relabel[int(s)] for s in hidden_states])
    
    return sorted_params, P, hidden_sorted


def summarise_regimes(params, P):
    """
    Print a summary of regime parameters and transition matrix
    
    Parameters:
    -------------
    params : dict
        A sorted dict of regimes and their (mu_k, sigma_k, count_k)
    P : np.ndarray
        Transition probability matrix
    """
    ann = 252 # Trading days per year
    
    print("\n-- Regime Parameters -------------------------------------------------")
    print(f"{'Regime':<15} {'mu (ann)':>10} {'sigma (ann)':>12} {'days':>7}")
    print("-" * 48)
    for k, label in enumerate(REGIME_LABELS):
        p = params[k]
        # Annualise: mu * 252, sigma * sqrt(252)
        print(f"{label:<15} {p['mu']*ann:>10.4f} "
              f"{p['sigma']*np.sqrt(ann):>12.4f} {p['count']:>7}")
 
    print("\n-- Transition Matrix P -----------------------------------------------")
    print("  P[i,j] = probability of moving from regime i to regime j tomorrow")
    df_P = pd.DataFrame(P, index=REGIME_LABELS, columns=REGIME_LABELS)
    print(df_P.round(4).to_string())




if __name__ == "__main__":

    log_ret  = fetch_sp500()
    features = build_features(log_ret)

    print("\nFitting 5-regime Gaussian HMM via pomegranate Baum-Welch ...")
    model = fit_hmm(features)

    params, P, hidden = extract_regime_params(model, log_ret, features)
    summarise_regimes(params, P)