def getCountInfo(Curves):
    """
    活动曲线数量，段数，关键点数
    :param Curves:
    :return:
    """
    curve_count = len(Curves)
    segment_count = 0
    point_count = 0
    for curve in Curves:
        segment = curve.segments
        end_pos = len(segment)
        point_count += 1
        v = 2
        while v < end_pos:
            identifier = segment[v]
            if identifier == 0 or identifier == 2 or identifier == 3:
                point_count += 1
                v += 3
            elif identifier == 1:
                point_count += 3
                v += 7
            else:
                raise Exception("unknown identifier: %d" % identifier)
            segment_count += 1
    point_count = point_count - curve_count + 1
    return curve_count, segment_count+1, point_count
