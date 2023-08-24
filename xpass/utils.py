import ast

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection
import seaborn as sns

import shapely
from shapely import affinity

from mplsoccer import Pitch


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

    if isinstance(freeze_frame, str):
        freeze_frame = ast.literal_eval(freeze_frame)

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


def get_reception_shape_features(
    row: pd.Series,
    corr_width: float = 2,
    alpha: float = 10,
    length: float = 50):
    """This function takes a dataframe row that represents a pass and returns
    the number of teammates and opponents within the reception shape
    at the moment of the pass

    Inputs:
        row (pd.Series) : a pd.DataFrame row representing a pass
        corr_width (float): the with of the central corridor in yards
        alpha (float): the angle of the reception shape in degrees
        length (float): the length of the reception shape in yards

    Returns:
        A tuple of two integers (i.e. the number of teammates and opponents
        within the reception shape when the pass is made)

    """

    freeze_frame = row["freeze_frame"]
    reception_shape = create_reception_shape(
        x = row["location_x"], y = row["location_y"],
        corr_width = corr_width, alpha = alpha, length = length,
        rotation_angle = row["pass_angle"]
    )

    players = get_players_within_polygon(freeze_frame, reception_shape)
    n_teammates = players["teammates"]
    n_opponents = players["opponents"]

    return n_teammates, n_opponents


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


def plot_pass(
    pass_row: pd.Series, corr_width: float = 2, length: float = 50,
    alpha: float = 10, ax = None
    ):
    """Plot a pass on a football pitch
    Inputs:
        pass_row (pd.Series): a DataFrame row representing a pass (with a freeze frame column)
        corr_width (float): the with of the central corridor in yards
        alpha (float): the angle of the reception shape in degrees
        length (float): the length of the reception shape in yards
        ax (matplotlib.axes): a matplotlib axes (default is None)

    Returns:
        A matplotlib axes
    """

    pitch = Pitch(
        pitch_type = "statsbomb",
        pitch_color = "grass",
        line_color = "white",
        goal_type = "box",
        stripe = True,
        linewidth = 1,
        axis = True,
        label = True
        )

    if ax is None:
        ax = plt.gca()

    pitch.draw(ax = ax)

    freeze_frame = pass_row["freeze_frame"]
    if isinstance(freeze_frame, str):
        freeze_frame = ast.literal_eval(freeze_frame)

    frame_df = pd.DataFrame.from_dict(freeze_frame)
    frame_df["x"] = frame_df["location"].map(lambda x : x[0])
    frame_df["y"] = frame_df["location"].map(lambda x : x[1])

    sns.scatterplot(
        data = frame_df,
        x = "x",
        y = "y",
        hue  = "teammate",
        ax = ax
    )

    start_location = pass_row["location"]
    if isinstance(start_location, str):
        start_location = ast.literal_eval(start_location)
    end_location = pass_row["pass_end_location"]
    if isinstance(end_location, str):
        end_location = ast.literal_eval(end_location)

    ax.arrow(
        start_location[0],
        start_location[1],
        end_location[0] - start_location[0],
        end_location[1] - start_location[1],
        head_width = 3,
        head_length = 2,
        width = 0.2,
        fc = "black",
        ec = "black"
    )

    reception_shape = create_reception_shape(
        x = start_location[0],
        y = start_location[1],
        corr_width = corr_width,
        length = length,
        alpha = alpha,
        rotation_angle = pass_row["pass_angle"]
    )

    plot_polygon(ax, poly = reception_shape, facecolor = "lightblue", alpha = 0.6)

    return ax
