import numpy as np
import scipy.optimize
import scipy.interpolate
import matplotlib.pyplot as plt

def monoExp(x, m, t, b):
    return m * np.exp(-t * x) + b


ys = np.array([315840,248357.8947,195637.5,155570,121828.9474,99823.91304,79652.63158,64982.6087,52539.28571,
42904.9505,35367.5,29159.85915,24264.45783,20212.43523,16958.10811,14304.34783,12111.53846,10278.50467,8730.446927,
7472.405063,6429.861111,5530,4783.431953,4154.696133,3618.512111,3156.372549,2765.993789,2423.111111,2139.40256,
1886.438356,1668.344371,1480.077121,1317.647059,1177.872861,1051.315789,943.3098592,845.6747405,763.75,690.2466368,
624.5847176,560.5032823,509.2091008,464.4468314,420.4472843,387.9365079,350.5252101,324.137931,298.024948,272.1820062,
251.6992791,231.3846154,211.2359551,196.2321792,181.319797,166.4979757,156.6666667,146.875,132.2613065,127.4096386,117.7354709,108.1])
xs = np.array([0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,
145,150,155,160,165,170,175,180,185,190,195,200,205,210,215,220,225,230,235,240,245,250,255,260,265,270,275,280,285,290,295,300])

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