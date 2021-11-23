import numpy as np
import scipy.optimize
import scipy.interpolate
import matplotlib.pyplot as plt

def monoExp(x, m, t, b):
    return m * np.exp(-t * x) + b


ys = np.array([331530.7692,125354.0979,52895.83134,24399.43715,12129.78053,6419.822383,
3649.860202,2109.95411,1293.044822,1022.974742,814.0026147,651.0138669,525.0029884,
435.9810289,355.9954573,293.9757785,244.9769623,204.9732211,173.9964318,147.999032,
126.0044766,109.0137126,93.91002632])
xs = np.array([0,20,40,60,80,100,120,140,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300])

plt.plot(xs, ys, '.')
plt.title("Original Data")
plt.show()

# interpolation function from scipy
f = scipy.interpolate.interp1d(xs, ys, kind = 'cubic')

# x range for the interpolation function
x_f = np.arange(0, 300, 1)
y_f_t = f(x_f)   # use interpolation function returned by `interp1d`
y_f = [round(num,1) for num in y_f_t]

for index in range(0,300):
    print("temperature%d:%d" % (index+1,x_f[index]))
    print("resistance%d:%.1f" % (index+1,y_f[index]))

plt.plot(xs, ys, 'o', x_f, y_f, '-')
plt.legend(['data', 'interpolation'])

plt.show()


# # perform the fit
# p0 = (2000, .1, 50) # start with values near those we expect
# params, cv = scipy.optimize.curve_fit(monoExp, xs, ys)
# m, t, b = params
# sampleRate = 20_000 # Hz
# tauSec = (1 / t) / sampleRate

# # determine quality of the fit
# squaredDiffs = np.square(ys - monoExp(xs, m, t, b))
# squaredDiffsFromMean = np.square(ys - np.mean(ys))
# rSquared = 1 - np.sum(squaredDiffs) / np.sum(squaredDiffsFromMean)
# print(f"R² = {rSquared}")

# # plot the results
# plt.plot(xs, ys, '.', label="data")
# plt.plot(xs, monoExp(xs, m, t, b), '--', label="fitted")
# plt.title("Fitted Exponential Curve")
# plt.show()

# # inspect the parameters
# print(f"Y = {m} * e^(-{t} * x) + {b}")
# print(f"Tau = {tauSec * 1e6} µs")