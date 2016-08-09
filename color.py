import os
import numpy as np
import OpenEXR, array, Imath, Image

_CIEXYZ_1931_table_rgb = np.array([
    [360, 0.0   , 0.0   , 0.0   ],
    [380, 0.0014, 0.0   , 0.0065],
    [400, 0.0143, 0.0004, 0.0679],
    [420, 0.1344, 0.0040, 0.6456],
    [440, 0.3483, 0.0530, 1.7471],
    [460, 0.2023, 0.3600, 1.7353],
    [480, 0.0870, 0.7720, 1.5909],
    [500, 0.0163, 1.0768, 0.9068],
    [520, 0.0450, 1.6259, 0.1792],
    [540, 0.1363, 1.4332, 0.0304],
    [560, 0.4902, 1.1552, 0.0045],
    [580, 0.9163, 0.8700, 0.0017],
    [600, 1.0622, 0.6310, 0.0008],
    [620, 0.9544, 0.3810, 0.0002],
    [640, 0.8479, 0.2750, 0.0   ],
    [660, 0.7649, 0.0910, 0.0   ],
    [680, 0.6468, 0.0370, 0.0   ],
    [700, 0.2514, 0.0041, 0.0   ],
    [720, 0.0529, 0.0010, 0.0   ],
    [740, 0.0157, 0.0003, 0.0   ],
    [760, 0.0049, 0.0   , 0.0   ],
    [780, 0.0   , 0.    , 0.0   ],
])

_CIEXYZ_1931_table_wl = _CIEXYZ_1931_table_rgb[:,0]
_CIEXYZ_1931_table_rgb = _CIEXYZ_1931_table_rgb[:,1:]

def CIEXYZ_1931_table_rgb(wl):
    rgb = np.empty([wl.shape[0], 3])
    rgb[:,0] = np.interp(wl, _CIEXYZ_1931_table_wl, _CIEXYZ_1931_table_rgb[:,0])
    rgb[:,1] = np.interp(wl, _CIEXYZ_1931_table_wl, _CIEXYZ_1931_table_rgb[:,1])
    rgb[:,2] = np.interp(wl, _CIEXYZ_1931_table_wl, _CIEXYZ_1931_table_rgb[:,2])
    return rgb

class Frame:
    def __init__(self, filename, shape):
        self.filename = str(filename)
        self.nx, self.ny = tuple(shape)

        if os.path.exists(filename):
            exrImage = OpenEXR.InputFile(filename)

            dw = exrImage.header()['dataWindow']
            assert self.nx == dw.max.x - dw.min.x + 1
            assert self.ny == dw.max.y - dw.min.y + 1

            r = np.fromstring(exrImage.channel('R'), dtype=np.float32)
            g = np.fromstring(exrImage.channel('G'), dtype=np.float32)
            b = np.fromstring(exrImage.channel('B'), dtype=np.float32)
            self.rgb = np.rollaxis(np.array([r, g, b]), 1)
            self.rgb = np.array(self.rgb, order='C')
        else:
            self.rgb = np.zeros((self.ny * self.nx, 3), dtype=np.float32)

    def accumulate(self, x, y, wavelength):
        x_int, y_int = np.array(np.round(x), int), np.array(np.round(y), int)
        rgb = CIEXYZ_1931_table_rgb(wavelength)

        dx_int = np.array([-2,-1,-1,-1,0,0,0,0,0,1,1,1,2])
        dy_int = np.array([0,-1,-0,1,-2,-1,0,1,2,-1,0,1,0])
        x_int = x_int[:,np.newaxis] + dx_int
        y_int = y_int[:,np.newaxis] + dy_int

        dx, dy = x_int - x[:,np.newaxis], y_int - y[:,np.newaxis]
        w = np.exp(-(dx**2 + dy**2)) * 1E-30
        rgb = rgb[:,np.newaxis,:] * w[:,:,np.newaxis]

        x, y = np.ravel(x_int), np.ravel(y_int)
        rgb = rgb.reshape([x.size, 3])

        sel = reduce(np.logical_and, (x >= 0, x < self.nx, y >= 0, y < self.ny))
        x, y, rgb = x[sel], y[sel], rgb[sel]

        i = y * self.nx + x
        np.add.at(self.rgb, i, rgb)

    def write(self, fname=None):
        if fname is None:
            fname = self.filename

        r = array.array('f', np.ravel(self.rgb[:,0])).tostring()
        g = array.array('f', np.ravel(self.rgb[:,1])).tostring()
        b = array.array('f', np.ravel(self.rgb[:,2])).tostring()

        exrHeader = OpenEXR.Header(self.nx, self.ny)
        exr = OpenEXR.OutputFile(fname, exrHeader)
        exr.writePixels({'R': r, 'G': g, 'B': b})

    def write_png(self, fname=None):
        if fname is None:
            fname = self.filename.replace('.exr', '.png')
        rgb = self.rgb / self.rgb.max()
        rmax = ((rgb**4).mean())**(1./4)
        rgb = 1 - np.exp(-rgb / rmax)
        rgb = np.array(np.maximum(rgb, 0) * 255, np.uint8)
        im = Image.fromarray(rgb.reshape([self.ny, self.nx, 3]), mode='RGB')
        im.save(fname)

if __name__ == '__main__':
    N = 100000
    H, W = 50, 480

    r = np.random.rand(N)
    x = r * W
    y = np.random.randn(N) * H / 8 + H / 2 - 0.5

    w = r * _CIEXYZ_1931_table_wl[-1] + (1 - r) * _CIEXYZ_1931_table_wl[0]

    f = Frame('test_raw.exr', (W, H))
    f.accumulate(x, y, w)
    f.write()
    f.write_png()

