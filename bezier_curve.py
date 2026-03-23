import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import lineStyles
from matplotlib.path import Path
from matplotlib.patches import PathPatch

def draw_curve( p0, p1, center, bend=1, lw=2.5):
    fig, ax = plt.subplots(figsize=(8, 8))
    color = "#e85a70"
    BLUE = "#4f88ff"

    p0 = np.array(p0, dtype=float)
    p1 = np.array(p1, dtype=float)
    center = np.array(center, dtype=float)

    mid = (p0 + p1) / 2
    pull = center - mid


    c1 = p0 + 0.5 * (p1 - p0) + bend * pull


    verts = [p0, c1, p1]
    codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
    patch = PathPatch(Path(verts, codes), facecolor="none", edgecolor=color, lw=lw)
    ax.add_patch(patch)

    xs = [v[0] for v in verts]
    ys = [v[1] for v in verts]
    ax.plot(xs, ys, "o", color=BLUE)


    ax.plot([p0[0], center[0]], [p0[1], center[1]], color="blue", linestyle="--")
    ax.plot([p1[0], center[0]], [p1[1], center[1]], color="blue", linestyle="--")
    ax.annotate("p0",(p0[0]+0.2,p0[1]+0))
    ax.annotate("c1",(c1[0]+0.2,c1[1]+0))
    ax.annotate("p1",(p1[0]+0.2,p1[1]+0))


    ax.set_xlim(-1, 7)
    ax.set_ylim(-1, 7)
    ax.axis("off")
    ax.set_aspect("equal")
    plt.show()


draw_curve((0,3), (6,3),(3,0))
