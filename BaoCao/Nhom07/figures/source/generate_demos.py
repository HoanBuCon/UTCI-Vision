"""Generate original vector demonstrations from synthetic data, without downloaded images.

Color: sRGB/D65 -> CIELAB, and RGB -> HSV; channel values normalized for display.
Morphology: binary erosion/dilation/opening/closing with a 3x3 square kernel.
References: official OpenCV color-conversion, morphology and contour tutorials.
"""
import colorsys
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
N = 28


def lab(rgb):
    vals = [v / 255 for v in rgb]
    r, g, b = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in vals]
    x = (.4124564*r + .3575761*g + .1804375*b) / .95047
    y = .2126729*r + .7151522*g + .0721750*b
    z = (.0193339*r + .1191920*g + .9503041*b) / 1.08883
    delta = 6/29
    f = lambda t: t**(1/3) if t > delta**3 else t/(3*delta**2) + 4/29
    fx, fy, fz = map(f, (x, y, z))
    return 116*fy-16, 500*(fx-fy), 200*(fy-fz)


def pixels(lines, data, x0, y0, side, color=False):
    step = side/N
    for y, row in enumerate(data):
        for x, value in enumerate(row):
            left, bottom = x0+x*step, y0+(N-y-1)*step
            if color:
                r, g, b = value
                fill = '{rgb,255:red,%d;green,%d;blue,%d}' % (r, g, b)
            else:
                fill = 'black!%.3f' % (100*(1-max(0, min(1, value))))
            lines.append(r'\fill[fill=%s,draw=none] (%.5f,%.5f) rectangle (%.5f,%.5f);' %
                         (fill, left, bottom, left+step+.0004, bottom+step+.0004))
    lines.append(r'\draw[AccentBlue!50,line width=.4pt] (%g,%g) rectangle (%g,%g);' %
                 (x0, y0, x0+side, y0+side))


def color_demo():
    image = []
    for y in range(N):
        row = []
        for x in range(N):
            shade = int(235-80*y/(N-1))
            rgb = (shade, shade, shade)
            if y < 4:
                rgb = tuple(round(v*255) for v in colorsys.hsv_to_rgb(x/N, .9, .95))
            radius = math.hypot(x-16, y-14)
            if radius < 8:
                rgb = (245, 245, 245) if radius < 5.7 else (215, 35, 35)
            if 2 <= x <= 7 and 7 <= y <= 13:
                rgb = (25, 85, 200)
            if 18 <= y <= 25 and abs(x-5) < (y-17)/2:
                rgb = (245, 200, 30)
            row.append(rgb)
        image.append(row)
    channels = [[] for _ in range(9)]
    for row in image:
        output = [[] for _ in range(9)]
        for rgb in row:
            scaled = tuple(v/255 for v in rgb)
            hsv = colorsys.rgb_to_hsv(*scaled)
            ll, aa, bb = lab(rgb)
            for i, value in enumerate((*scaled, *hsv, ll/100, (aa+128)/255, (bb+128)/255)):
                output[i].append(value)
        for i in range(9):
            channels[i].append(output[i])
    assert abs(lab((255,255,255))[0]-100) < .001
    assert abs(lab((0,0,0))[0]) < .001
    lines = [r'\input{style}', r'\begin{document}', r'\begin{tikzpicture}']
    pixels(lines, image, 0, 1.1, 2.8, True)
    lines.append(r'\node at (1.4,.65) {Ảnh RGB tự tạo};')
    labels = [('RGB', ('R','G','B')), ('HSV', ('H','S','V')), ('Lab', ('$L^*$','$a^*$','$b^*$'))]
    for row_id, (title, names) in enumerate(labels):
        y0 = 4.2-row_id*2.25
        lines.append(r'\node[heading] at (3.45,%g) {%s};' % (y0+.775, title))
        for col, name in enumerate(names):
            x0 = 4.1+col*2.15
            pixels(lines, channels[row_id*3+col], x0, y0, 1.55)
            lines.append(r'\node at (%g,%g) {%s};' % (x0+.775, y0-.3, name))
    lines.extend([r'\end{tikzpicture}', r'\end{document}'])
    (ROOT/'fig_1_4_color_spaces.tex').write_text('\n'.join(lines)+'\n', encoding='utf-8')


def morph(mask, erode=False):
    def get(x, y):
        return 0 <= x < N and 0 <= y < N and mask[y][x]
    op = all if erode else any
    return [[op(get(x+dx, y+dy) for dy in (-1,0,1) for dx in (-1,0,1))
             for x in range(N)] for y in range(N)]


def morphology_demo():
    original = [[math.hypot(x-14, y-14) <= 8 for x in range(N)] for y in range(N)]
    for x, y in ((4,4),(23,5),(4,23),(22,23)):
        original[y][x] = True
    original[12][12] = original[14][15] = False
    eroded = morph(original, True)
    dilated = morph(original)
    opened = morph(eroded)
    closed = morph(dilated, True)
    subset = lambda a, b: all(not a[y][x] or b[y][x] for y in range(N) for x in range(N))
    assert subset(eroded, original) and subset(original, dilated)
    assert subset(opened, original) and subset(original, closed)
    assert morph(morph(opened, True)) == opened
    lines = [r'\input{style}', r'\begin{document}', r'\begin{tikzpicture}']
    for i, (name, mask) in enumerate(zip(('Ảnh gốc','Co (erosion)','Giãn (dilation)','Mở (opening)','Đóng (closing)'),
                                        (original, eroded, dilated, opened, closed))):
        pixels(lines, mask, i*2.35, 1.4, 1.9)
        lines.append(r'\node at (%g,1) {%s};' % (i*2.35+.95, name))
    # Lower panel: contour, bounding rectangle, centroid of elementary shapes.
    for x in (1.7,5.65,9.6):
        lines.append(r'\draw[AccentBlue,dashed] (%g,-1.65) rectangle (%g,-.15);' % (x-.75, x+.75))
    lines += [
        r'\draw[red!75!black,line width=1.1pt] (1.7,-.9) circle (.75);',
        r'\draw[red!75!black,line width=1.1pt] (4.9,-1.65)--(5.65,-.15)--(6.4,-1.65)--cycle;',
        r'\draw[red!75!black,line width=1.1pt] (8.85,-.9)--(9.6,-.15)--(10.35,-.9)--(9.6,-1.65)--cycle;',
        r'\fill[black] (1.7,-.9) circle (.045);',
        r'\fill[black] (5.65,-1.15) circle (.045);',
        r'\fill[black] (9.6,-.9) circle (.045);',
        r'\node at (1.7,-2) {Hình tròn};',
        r'\node at (5.65,-2) {Tam giác};',
        r'\node at (9.6,-2) {Hình vuông};',
        r'\draw[red!75!black,line width=1.1pt] (1.1,-2.8)--(1.7,-2.8);',
        r'\node[anchor=west] at (1.9,-2.8) {Biên};',
        r'\draw[AccentBlue,dashed] (4.3,-2.8)--(4.9,-2.8);',
        r'\node[anchor=west] at (5.1,-2.8) {Khung bao};',
        r'\fill[black] (8.3,-2.8) circle (.045);',
        r'\node[anchor=west] at (8.55,-2.8) {Tâm};',
        r'\end{tikzpicture}', r'\end{document}']
    (ROOT/'fig_1_4_morphology_shapes.tex').write_text('\n'.join(lines)+'\n', encoding='utf-8')


if __name__ == '__main__':
    color_demo()
    morphology_demo()
    print('Generated color and morphology demos; numerical and morphology checks passed.')
