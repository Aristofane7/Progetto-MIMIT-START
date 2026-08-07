# -*- coding: utf-8 -*-
"""AHP: pesi da matrice di confronto a coppie (media geometrica) + consistenza (CI, CR)."""
import numpy as np
RI_SAATY = {1:0.0,2:0.0,3:0.58,4:0.90,5:1.12}   # Random Index (Saaty)
DIMS = ["env","econ","soc","tech"]

def weights_and_consistency(A):
    A = np.array(A, dtype=float); n = A.shape[0]
    gm = np.prod(A, axis=1)**(1.0/n)          # media geometrica per riga
    w = gm/gm.sum()
    lam_max = float(np.mean((A @ w)/w))
    CI = (lam_max - n)/(n-1)
    CR = CI/RI_SAATY[n] if RI_SAATY[n] > 0 else 0.0
    return w, lam_max, CI, CR

# Matrice DI PROVA documentata (DIMOSTRATIVA) - ordine: env, econ, soc, tech
TRIAL_MATRIX = [
    [1,    3,   3,   1  ],   # env
    [1/3,  1,   2,   1/3],   # econ
    [1/3,  1/2, 1,   1/4],   # soc
    [1,    3,   4,   1  ],   # tech
]

if __name__ == "__main__":
    w, lam, CI, CR = weights_and_consistency(TRIAL_MATRIX)
    print("pesi:", dict(zip(DIMS, np.round(w,4))))
    print(f"lambda_max={lam:.4f} CI={CI:.4f} CR={CR:.4f}  -> {'OK (<=0.10)' if CR<=0.10 else 'REVISIONE'}")
