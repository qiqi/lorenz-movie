import os
from color import Frame
from numpy import *

def lorenz(xyz, r):
    x, y, z = xyz
    sigma, beta = 10., 8./3
    dxdt = sigma * (y - x)
    dydt = (x * (r - z) - y)
    dzdt = (x * y - beta * z)
    return array([dxdt, dydt, dzdt])

def plot(i, x, y, r):
    filename = 'frame{0:06d}'.format(i)
    # W, H = 1920 / 8, 1080 / 8
    W, H = 1920, 1080
    y0, y1 = 0, 55

    y = H * (y1 - y) / (y1 - y0)
    x = H * x / (y1 - y0) + W / 2
    wavelength = (r - r[0]) / (r[-1] - r[0]) * (830 - 360) + 360

    f = Frame(filename + '_raw.exr', (W, H))
    f.accumulate(x, y, wavelength)
    f.close()

    # os.system('exrnormalize {0}_raw.exr {0}.exr 1'.format(filename))
    os.system('exrtopng {0}_raw.exr {0}.png &'.format(filename))

dt = 1. / 4 / 60
N = 1000000
x = ones(N)
y = ones(N)
z = ones(N) + 28
r = linspace(27, 29, N)

xyz = array([x, y, z], float)

plot(0, xyz[0], xyz[2], r)
for iFrame in range(1, 60 * 60 * 5):
    for iStep in range(2):
        f0 = lorenz(xyz, r) * dt
        f1 = lorenz(xyz + 0.5 * f0, r) * dt
        f2 = lorenz(xyz + 0.5 * f1, r) * dt
        f3 = lorenz(xyz + f2, r) * dt
        xyz += (f0 + f3) / 6 + (f1 + f2) / 3
    plot(iFrame, xyz[0], xyz[2], r)

