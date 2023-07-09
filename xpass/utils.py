import numpy as np

import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection

import shapely
from shapely import affinity


def create_reception_shape(
    x: float,
    y: float,
    corr_width: float = 2,
    alpha: float = 10,
    length: float = 50,
    rotation_angle: float = None
) -> shapely.Polygon:
    """Create the reception_shape polygon, i.e. the polygon whose players located
    inside are consider potential receivers for the pass.

    Inputs:
        x (float)): the x coordinate of the origin of the pass (point P)
        y (float)): the y coordinate of the origin of the pass (point P)
        corr_width (float): the with of the central corridor in yards
        alpha (float): the angle of the reception shape in degrees
        length (float): the length of the reception shape in yards
        rotation_angle (float): the rotation angle on (x, y), in radiants

    Returns:
        A shapely.Polygon object, representing the reception shape.
    """

    alpha_rad = np.radians(alpha)

    A = (x, y - corr_width)
    D = (x, y + corr_width)

    end_section = 0.5 * corr_width + length * np.tan(alpha_rad)
    B = (x + length, y - end_section)
    C = (x + length, y + end_section)

    reception_shape = shapely.Polygon([A, B, C, D])

    if rotation_angle:
        reception_shape = affinity.rotate(
            geom = reception_shape,
            angle = rotation_angle,
            origin = (x, y),
            use_radians = True
            )

    return reception_shape


def plot_polygon(ax, poly, **kwargs) -> PatchCollection:
    """Plots a Polygon to pyplot `ax`"""
    path = Path.make_compound_path(
        Path(np.asarray(poly.exterior.coords)[:, :2]),
        *[Path(np.asarray(ring.coords)[:, :2]) for ring in poly.interiors])

    patch = PathPatch(path, **kwargs)
    collection = PatchCollection([patch], **kwargs)

    ax.add_collection(collection, autolim=True)
    ax.autoscale_view()
    return collection


def get_players_within_polygon(freeze_frame: list, reception_shape: shapely.Polygon) -> dict:
    """Return the number of teammates and opponents within the reception_shape

    Inputs:
        freeze_frame (list): The Statsbomb freeze frame at the moment of the pass
        reception_shape (shapely.Polygon): The polygon representing the reception shape

    Returns:
        A dictionnary that gives the number of teammates and opponents within the reception_shape
    """

    n_teammates = 0
    n_opponents = 0

    for player in freeze_frame:
        is_within = all([not player["actor"], reception_shape.contains(
            shapely.Point(player["location"][0], player["location"][1]))])
        if is_within:
            if player["teammate"]:
                n_teammates += 1
            else:
                n_opponents += 1

    result = {"teammates" : n_teammates, "opponents" : n_opponents}

    return result
