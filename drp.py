import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch

RED = "#e85a70"
BLUE = "#4f88ff"
EDGE = "#62d9c7"



def ptsOnEdge(a, b, n):
    # interior points only
    ts = np.linspace(0, 1, n + 2)[1:-1]
    pts=[]
    for t in ts: # calculate the place of points on 1 side
        a_=np.array(a, dtype=float)
        b_=np.array(b, dtype=float)
        pts.append((1-t)*a+t*b)

    return pts

def alternating_colors(n, start_red=True):
    out = []
    for i in range(n):
        if ((i % 2) == 0) == start_red:
            out.append(RED)
        else:
            out.append(BLUE)
    return out

def draw_curve(ax, p0, p1, center, color, bend=0.5, lw=2.5):
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


def fill_cycle(ax, pts, center, color, bend=0.5, alpha=0.18):
    """
    Fill one closed same-color cycle made of cubic Bézier segments.
    pts must already be in cycle order.
    """
    if len(pts) < 2:
        return

    center = np.array(center, dtype=float)

    verts = []
    codes = []

    # start at first point
    p0 = np.array(pts[0], dtype=float)
    verts.append(p0)
    codes.append(Path.MOVETO)

    # add one cubic Bézier segment for each consecutive pair
    for i in range(len(pts)):
        p0 = np.array(pts[i], dtype=float)
        p1 = np.array(pts[(i + 1) % len(pts)], dtype=float)

        mid = (p0 + p1) / 2
        pull = center - mid

        c1 = p0 + 0.5 * (p1 - p0) + bend * pull

        verts.extend([c1, p1])
        codes.extend([Path.CURVE3, Path.CURVE3])

    patch = PathPatch(
        Path(verts, codes),
        facecolor=color,
        edgecolor="none",
        alpha=alpha,
        zorder=1
    )
    ax.add_patch(patch)
def draw_cube_frame(ax, pts):
    edges = [
        ("FBL", "FBR"), ("FBR", "FTR"), ("FTR", "FTL"), ("FTL", "FBL"),
        ("BBL", "BBR"), ("BBR", "BTR"), ("BTR", "BTL"), ("BTL", "BBL"),
        ("FBL", "BBL"), ("FBR", "BBR"), ("FTR", "BTR"), ("FTL", "BTL")
    ]
    for u, v in edges:
        p, q = pts[u], pts[v]
        ax.plot([p[0], q[0]], [p[1], q[1]], color=EDGE, lw=2)

def face_boundary_points(A, B, C, D, n, start_map):
    """
    Returns points on edges AB, BC, CD, DA with colors and boundary-order index.
    """
    edges = {
        "AB": ptsOnEdge(A, B, n),
        "BC": ptsOnEdge(B, C, n),
        "CD": ptsOnEdge(C, D, n),
        "DA": ptsOnEdge(D, A, n),
    }

    colors = {
        "AB": alternating_colors(n, start_red=start_map["AB"]),
        "BC": alternating_colors(n, start_red=start_map["BC"]),
        "CD": alternating_colors(n, start_red=start_map["CD"]),
        "DA": alternating_colors(n, start_red=start_map["DA"]),
    }

    ordered = []
    order = 0
    for edge_name in ["AB", "BC", "CD", "DA"]:
        for i, (p, c) in enumerate(zip(edges[edge_name], colors[edge_name])):
            ordered.append({
                "p": np.array(p, dtype=float),
                "color": c,
                "edge": edge_name,
                "idx": i,
                "order": order
            })
            order += 1

    return edges, colors, ordered



def draw_face_cycles(ax, A, B, C, D, n, start_map):


    #draw points
    edges, colors, ordered = face_boundary_points(A, B, C, D, n, start_map)
    for item in ordered:
        p = item["p"]
        ax.plot(p[0], p[1], "o", color=item["color"], ms=5, zorder=5)

    center = (np.array(A) + np.array(B) + np.array(C) + np.array(D)) / 4

    # make one cycle for each color
    for target_color in [RED, BLUE]:
        pts = [item for item in ordered if item["color"] == target_color]
        pts.sort(key=lambda x: x["order"])

        if len(pts) >= 2:
            cycle_pts = [item["p"] for item in pts]

            # fill first
            fill_cycle(ax, cycle_pts, center=center, color=target_color, bend=0.5, alpha=0.18)

            # then draw curve outlines on top
            for i in range(len(cycle_pts)):
                p0 = cycle_pts[i]
                p1 = cycle_pts[(i + 1) % len(cycle_pts)]
                draw_curve(ax, p0, p1, center=center, color=target_color, bend=0.5, lw=2.5)


    return edges, colors



def cube_cycles(n=5):
    fig, ax = plt.subplots(figsize=(8, 8))

    # projected cube
    pts = {
        "FBL": np.array([0.0, 0.0]),
        "FBR": np.array([3.0, 0.0]),
        "FTR": np.array([3.0, 3.0]),
        "FTL": np.array([0.0, 3.0]),
    }
    shift = np.array([1.6, 1.0])
    pts["BBL"] = pts["FBL"] + shift
    pts["BBR"] = pts["FBR"] + shift
    pts["BTR"] = pts["FTR"] + shift
    pts["BTL"] = pts["FTL"] + shift

    draw_cube_frame(ax, pts)

    # FRONT face
    front_edges, front_colors = draw_face_cycles(
        ax,
        pts["FBL"], pts["FBR"], pts["FTR"], pts["FTL"],
        n,
        start_map={
            "AB": True,
            "BC": True,
            "CD": True,
            "DA": True,
        }
    )



    # TOP face
    # top AB is same geometric edge as front CD, but opposite color assignment
    print('front edges:', front_edges, front_colors)
    tab_color=not (front_colors["CD"][-1] == RED)
    top_edges, top_colors = draw_face_cycles(
        ax,
        pts["FTL"], pts["FTR"], pts["BTR"], pts["BTL"],
        n,
        start_map={
            "AB":tab_color,
            "BC":  tab_color,
            "CD": tab_color,
            "DA":  tab_color,
        }
    )

    # RIGHT face
    # right DA = front BC reversed
    # right CD = top BC reversed
    rab_color = not (top_colors["BC"][-1] == RED)
    print(' top_colors:', top_edges, top_colors)
    draw_face_cycles(
        ax,
        pts["FBR"], pts["BBR"], pts["BTR"], pts["FTR"],
        n,
        start_map={
            "AB": tab_color,
            "BC":  tab_color,
            "CD":rab_color,
            "DA":  tab_color#not (front_colors["BC"][0] == RED),
        }
    )

    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-0.5, 5.5)
    ax.set_ylim(-0.5, 5.5)
    plt.tight_layout()
    plt.show()

cube_cycles(n=5)