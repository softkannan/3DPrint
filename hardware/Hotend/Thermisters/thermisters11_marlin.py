import numpy as np
import scipy.optimize
import scipy.interpolate
import matplotlib.pyplot as plt

def monoExp(x, m, t, b):
    return m * np.exp(-t * x) + b


ys = np.array([2399350,213850,145553.125,109778.5714,87763.46154,53935.36585,42438.23529,34710.65574,
29159.85915,26932.23684,20342.1875,17979.71698,16024.56897,12976.83824,10710.57692,9358.77193,7886.649215,
6970.145631,5937.389381,5072.560976,4337.781955,3705.769231,3286.877076,2907.753165,2562.990937,2248.121387,
1959.418283,1779.919137,1609.84252,1448.465473,1295.137157,1149.270073,1078.966346,1010.332542,
943.3098592,877.8422274,813.8761468,751.3605442,690.2466368,630.4878049,572.0394737,514.8590022,458.9055794,
404.1401274,350.5252101,298.024948,246.6049383,196.2321792,146.875])
xs = np.array([-27,9,17,23,28,39,45,51,55,57,65,69,72,79,85,90,95,100,105,111,117,123,128,133,139,144,150,
155,160,165,170,176,179,183,187,190,195,199,204,209,215,221,229,237,247,258,272,290,314])

plt.plot(xs, ys, '.')
plt.title("Original Data")
plt.show()

# interpolation function from scipy
f = scipy.interpolate.interp1d(xs, ys, kind = 'cubic')

# x range for the interpolation function
x_f = np.arange(-27, 314, 1)
y_f_t = f(x_f)   # use interpolation function returned by `interp1d`
y_f = [round(num,1) for num in y_f_t]

for index in range(0,341):
    print("temperature%d:%d" % (index+1,x_f[index]))
    print("resistance%d:%.1f" % (index+1,y_f[index]))

plt.plot(xs, ys, 'o', x_f, y_f, 'r-')
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