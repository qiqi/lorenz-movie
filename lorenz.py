import os
from color import Frame
from numpy import *

def step(x, y, z, r, dt):
    sigma, beta = 10., 8./3
    dxdt = sigma * (y - x)
    dydt = (x * (r - z) - y)
    dzdt = (x * y - beta * z)
    x += dxdt * dt
    y += dydt * dt
    z += dzdt * dt

dt = 0.005
N = 1000000
x = ones(N)
y = ones(N)
z = ones(N) + 28
r = linspace(27, 29, N)

def plot(i, x, y, r):
    filename = 'frame{0:06d}'.format(i)
    W, H = 1920 / 8, 1080 / 8
    y0, y1 = 5, 50

    y = array(H * (y1 - y) / (y1 - y0), int)
    x = array(H * x / (y1 - y0) + W / 2, int)
    wavelength = array((r - r[0]) / (r[-1] - r[0]) * (830 - 360) + 360, int)

    f = Frame(filename + '.exr', (W, H))
    f.accumulate(x, y, wavelength)
    f.close()

    os.system('exrtopng {0}.exr {0}.png'.format(filename))

plot(0, x, z, r)
for iFrame in range(1, 1200):
    for iStep in range(5):
        step(x, y, z, r, dt)
    plot(iFrame, x, z, r)

