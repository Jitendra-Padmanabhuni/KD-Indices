# -*- coding: utf-8 -*-
"""OMF_Project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ZUeaXmA0ucf00J02Xo-6xfdhcJ70sP3d
"""

import numpy as np
import pandas as pd
import cvxpy as cp

dataframe = pd.read_csv("dataset.csv",header = None)
d_matrix = np.array(dataframe)
d_matrix = d_matrix[1:, 1:]

for i in range(0, d_matrix.shape[0]):
  for j in range(0, d_matrix.shape[1]):
    d_matrix[i,j] = float(d_matrix[i,j])

d_matrix = np.flipud(d_matrix)

(n,m) = d_matrix.shape
print(d_matrix)

r_matrix = np.zeros((n-1, m))
expected_returns = np.zeros(m)
for i in range(0, n-1):
  for j in range(0, m):
    r_matrix[i,j] = (d_matrix[i+1, j] - d_matrix[i,j]) / d_matrix[i,j]

cov_matrix = np.cov(r_matrix,rowvar=False)
expected_returns = np.average(r_matrix,axis = 0)

#Mean Variance Model
G = np.identity(50)
w = cp.Variable(50)
r = expected_returns
e = np.ones(m)

problem = cp.Problem(cp.Minimize((w @ cov_matrix @ w.T)), [e.T @ w == 1, G @ w >= 0])
problem.solve()

w = np.array(w.value)
print("Total Return:", r @ w.T)
print("Variance Risk at the Optimal point: ", w @ cov_matrix @ w.T)

#Calculating KD Index
RSV = np.zeros((n, m))
L = np.copy(d_matrix[0])
R = np.copy(d_matrix[0])

for i in range(1, n):
  for j in range(0,m):
    L[j] = min(L[j], d_matrix[i,j])
    R[j] = max(R[j], d_matrix[i,j])
    RSV[i,j] = ((d_matrix[i,j] - L[j]) / (R[j] - L[j])) * 100

K = np.ones((n, m))
D = np.ones((n, m))

K[0] = np.full((1,m), 50)
D[0] = np.full((1,m), 50)

for i in range(1, n):
  for j in range(0, m):
    K[i,j] = RSV[i,j]* (1/3) + K[i-1,j] * (2/3)
    D[i,j] = K[i,j] * (1/3) + D[i-1,j] * (2/3)

for day in range(50, n, 50):
  W = 2*np.ones(m)
  for i in range(0,m):
    if(K[day-1][i] <= D[day-1][i] and K[day][i]> D[day][i]):
      W[i] = 1
    else:
      W[i] = 0
  print("Day ", day)
  print(W)

W = 2*np.ones(m)
day = n-1
for i in range(0,m):
  if(K[day-1][i] <= D[day-1][i] and K[day][i]> D[day][i]):
    W[i] = 1
  else:
    W[i] = 0
print("Day ", day)
print(W)

#Conservative strategy
Risky_return = 0
Risk_free_rate = 0.06/365
Risk_free_return = 0
w_d = np.zeros(m)
w_f = 0
for i in range(0, m):
  if(W[i]):
    Risky_return += w[i] * expected_returns[i]
    w_d[i] = w[i]
  else:
    Risk_free_return += Risk_free_rate * w[i]
    w_f += w[i]

w_r = 1 - w_f
w_d /= w_r
print('Return', Risky_return + Risk_free_return)
print('Risk', (w_r**2) * w_d @ cov_matrix @ w_d.T)

#Moderate strategy
B = set()
w_ = np.zeros(m)
for i in range(0, m):
  if(w[i] > 0):
    w_[i] = 1
    B.add(expected_returns[i])

Return = 0
if(len(B) != 0):
  for i in range(0, m):
    w_[i] = (1 / len(B))
  for asset in B:
    Return += asset
  Return /= len(B)

print('Return', Return)
print('Risk', w_ @ cov_matrix @ w_.T)

#Aggressive startegy
B = set()
w_ = np.zeros(m)
for i in range(0, m):
  if(W[i] > 0):
    w_[i] = 1
    B.add(expected_returns[i])

Return = 0
if(len(B) != 0):
  for i in range(0, m):
    w_[i] = (1 / len(B))
  for asset in B:
    Return += asset
  Return /= len(B)

print('Return', Return)
print('Risk', w_ @ cov_matrix @ w_.T)