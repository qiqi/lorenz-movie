import os, sys, time
from color import Frame
from numpy import *
from mpi4py import MPI

if len(sys.argv) > 1:
    prefix = 'frame_' + sys.argv[1]
else:
    prefix = 'frame'

comm = MPI.COMM_WORLD

def lorenz(xyz, r):
    x, y, z = xyz
    sigma, beta = 10., 8./3
    dxdt = sigma * (y - x)
    dydt = (x * (r - z) - y)
    dzdt = (x * y - beta * z)
    return array([dxdt, dydt, dzdt])

def plot(i, x, y, r):
    filename = '{0}_{1:06d}'.format(prefix, i)
    # W, H = 1920 / 8, 1080 / 8
    W, H = 1920, 1080
    y0, y1 = 0, 55

    y = H * (y1 - y) / (y1 - y0)
    x = H * x / (y1 - y0) + W / 2
    wavelength = (r - r[0]) / (r[-1] - r[0]) * (830 - 360) + 360

    f = Frame(filename + '_raw.exr', (W, H))
    f.accumulate(x, y, wavelength)
    return f

for i_repeat in range(2000):
    comm.Barrier()
    if comm.rank == 0:
        print('REPETATION ', i_repeat)
        sys.stdout.flush()

    dt = 1. / 4 / 60
    N = 500000
    x = ones(N)
    y = ones(N)
    z = ones(N) + 28
    r = linspace(27, 29, N) + (random.rand(N) * 2 - 1) / N

    xyz = array([x, y, z], float)

    for iFrame in range(1, 60 * 60 * 5):
        t0 = time.time()
        for iStep in range(2):
            f0 = lorenz(xyz, r) * dt
            f1 = lorenz(xyz + 0.5 * f0, r) * dt
            f2 = lorenz(xyz + 0.5 * f1, r) * dt
            f3 = lorenz(xyz + f2, r) * dt
            xyz += (f0 + f3) / 6 + (f1 + f2) / 3
        t1 = time.time()
        f = plot(iFrame, xyz[0] * 1.8, xyz[2], r)
        t2 = time.time()
        cumm_rgb = zeros_like(f.rgb)
        comm.Reduce(f.rgb, cumm_rgb, op=MPI.SUM, root=0)
        t3 = time.time()
        if comm.rank == 0:
            f.rgb = cumm_rgb
            f.write()
            f.write_png()
        t4 = time.time()
        if comm.rank == 0:
            print('Time {0} {1} {2} {3}'.format(t1-t0, t2-t1, t3-t2, t4-t3))
            sys.stdout.flush()
