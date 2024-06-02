import numpy as np


def linear(x0, y0, x1, y1, x, y):
    if len(x) == 0:
        x.extend([x0, x1])
        y.extend([y0, y1])
    else:
        x.extend([x1])
        y.extend([y1])


def stepped(x0, y0, x1, y1, x, y):
    if len(x) == 0:
        x.extend([x0, x0, x1])
        y.extend([y0, y1, y1])
    else:
        x.extend([x0, x1])
        y.extend([y1, y1])


def inverse_stepped(x0, y0, x1, y1, x, y):
    if len(x) == 0:
        x.extend([x0, x1, x1])
        y.extend([y0, y0, y1])
    else:
        x.extend([x1, x1])
        y.extend([y0, y1])


def bezier(x0, y0, x1, y1, x2, y2, x3, y3, x, y):
    t_values = np.linspace(0, 1, 5)
    bezier_points = np.array([(1 - t) ** 3 * np.array([x0, y0]) +
                              3 * (1 - t) ** 2 * t * np.array([x1, y1]) +
                              3 * (1 - t) * t ** 2 * np.array([x2, y2]) +
                              t ** 3 * np.array([x3, y3]) for t in t_values])
    if len(x) == 0:
        x.extend(bezier_points[:, 0])
        y.extend(bezier_points[:, 1])
    else:
        x.extend(bezier_points[1:, 0])
        y.extend(bezier_points[1:, 1])


def segmentsIndex(segment):
    """
    获得曲线各点的坐标
    :param segment:
    :return:
    """
    x = []
    y = []
    x0, y0 = segment[0], segment[1]
    end_pos = len(segment)
    v = 2
    while v < end_pos:
        identifier = segment[v]
        if identifier == 0 or identifier == 2 or identifier == 3:
            x1, y1 = segment[v + 1], segment[v + 2]
            if identifier == 0:
                linear(x0, y0, x1, y1, x, y)
            if identifier == 2:
                stepped(x0, y0, x1, y1, x, y)
            if identifier == 3:
                inverse_stepped(x0, y0, x1, y1, x, y)
            v += 3
            x0 = x1
            y0 = y1
        elif identifier == 1:
            x1, y1 = segment[v + 1], segment[v + 2]
            x2, y2 = segment[v + 3], segment[v + 4]
            x3, y3 = segment[v + 5], segment[v + 6]
            bezier(x0, y0, x1, y1, x2, y2, x3, y3, x, y)
            v += 7
            x0 = x3
            y0 = y3
        else:
            raise Exception("unknown identifier: %d" % identifier)
    return x, y
