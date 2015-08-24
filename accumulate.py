import os
from color import Frame

W, H = 1920, 1080
frame = Frame('', (W, H))

for fname in sorted(os.listdir('.')):
    if fname.endswith('.exr'):
        f = Frame(fname, (W, H))
        frame.rgb += f.rgb
        if fname.endswith('00.exr'):
            fname.write(fname[:-4] + '_accum.exr')
