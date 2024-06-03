def getOvalId(tag):
    return int(tag.split("oval")[1])


def getCurveInit(num, length):
    segment = [0, 0]
    step = length / (num - 1)
    for i in range(num - 1):
        segment.extend([0, (i + 1) * step, 0])
    return segment
