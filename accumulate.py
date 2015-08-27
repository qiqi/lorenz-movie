import os
import sys
from color import Frame

W, H = 1920, 1080
frame = Frame('', (W, H))

for fname in reversed(sorted(os.listdir('.'))):
    if fname.endswith('.exr'):
        print(fname)
        sys.stdout.flush()
        f = Frame(fname, (W, H))
        frame.rgb += f.rgb
        if fname.endswith('00_raw.exr'):
            frame.write(fname[:-4] + '_accum.exr')
