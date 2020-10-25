import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
aucs30 = np.loadtxt("local30.csv")
aucs42 = np.loadtxt("local42.csv")
aucs72 = np.loadtxt("rosetta72.csv")
plt.plot(aucs30, label="local 30 features")
plt.plot(aucs42, label="local 42 features")
plt.plot(aucs72, label="Rosetta vertical federated")
plt.legend()
plt.xlabel("batch num")
plt.ylabel("AUC")
plt.show()
