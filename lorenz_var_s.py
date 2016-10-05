from __future__ import division

import os, sys, time
from color import Frame
from numpy import *
from mpi4py import MPI

#sys.path.append('/master/home/niangxiu/lssode')
sys.path.append('/home/niangxiu/Working/lssode')
from lssode import *

comm = MPI.COMM_WORLD

def lorenz(u, rho):
    shp = u.shape
    x, y, z = u.reshape([-1, 3]).T
    sigma, beta = 10, 8./3
    dxdt, dydt, dzdt = sigma*(y-x), x*(rho-z)-y, x*y - beta*z
    return transpose([dxdt, dydt, dzdt]).reshape(shp)

def plot(i, x, y, r, prefix='frame'):
    filename = '{0}_{1:06d}'.format(prefix, i)
    # W, H = 1920 / 8, 1080 / 8
    W, H = 1920, 1080
    y0, y1 = 0, 55

    y = H * (y1 - y) / (y1 - y0)
    x = H * x / (y1 - y0) + W / 2
    wavelength = (r - r[0]) / (r[-1] - r[0]) * (700 - 400) + 400

    f = Frame(filename + '_raw.exr', (W, H))
    f.accumulate(x, y, wavelength)
    return f

if len(sys.argv) > 1 and sys.argv[1] == 'shadowing':
    N = 21
    r = linspace(27, 29, N)
    xyz0 = array([1,1,28])
    dt = 1. / 2 / 60
    t = dt * arange(60*60*2)
    solver = lssSolver(lorenz, xyz0, r[(N-1)//2], t)
    u = [solver.u.copy()]
    for rho in r[(N-1)//2+1:]:
        print('rho = ', rho)
        solver.lss(rho)
        u.append(solver.u.copy())
    solver = lssSolver(lorenz, xyz0, r[(N-1)//2], t)
    for rho in reversed(r[:(N-1)//2]):
        print('rho = ', rho)
        solver.lss(rho)
        u.insert(0, solver.u.copy())
    xyz = array(u)
    for iFrame in range(xyz.shape[1]):
        f = plot(iFrame, xyz[:,iFrame,0] * 1.8, xyz[:,iFrame,2], r,
                 prefix='shadowing')
        f.write()
        f.write_png()
else:
    dt = 1. / 4 / 60
    N = 500000
    xi = linspace(-1,1,N) + (random.rand(N) *2 - 1)/N







    x = 11.99784076 * ones(N)
    y = 6.82321628 * ones(N) 
    z = 36.46795002 * ones(N)
    r = 28.00 *ones(N) + xi * 1e-3

    xyz = array([x, y, z], float).T

    for iFrame in range(1, 60 * 60 * 2):
        t0 = time.time()
        for iStep in range(2):
            f0 = lorenz(xyz, r) * dt
            f1 = lorenz(xyz + 0.5 * f0, r) * dt
            f2 = lorenz(xyz + 0.5 * f1, r) * dt
            f3 = lorenz(xyz + f2, r) * dt
            xyz += (f0 + f3) / 6 + (f1 + f2) / 3
        if iFrame % 1 == 0: # output interval
            t1 = time.time()
            f = plot(iFrame, xyz[:,0] * 1.8, xyz[:,2], r)
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
                print('Time {0} {1} {2} {3} {4}'.format(iFrame, t1-t0, t2-t1, t3-t2, t4-t3))
                sys.stdout.flush()
