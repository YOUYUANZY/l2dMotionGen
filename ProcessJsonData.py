import json

from motionJson import MotionJson


def loadJsonData(path):
    data = open(path, 'r')
    data = json.load(data)
    motion = MotionJson()
    motion.loadJson(data)
    return motion


def saveMotionJson(Motion, path):
    data = {
        'Version': Motion.version,
        'Meta': {
            'Duration': Motion.meta.duration,
            'Fps': Motion.meta.fps,
            'Loop': Motion.meta.loop,
            'AreBeziersRestricted': Motion.meta.areBeziersRestricted,
            'FadeInTime': Motion.meta.fadeInTime,
            'FadeOutTime': Motion.meta.fadeOutTime,
            'CurveCount': Motion.meta.curveCount,
            'TotalSegmentCount': Motion.meta.totalSegmentCount,
            'TotalPointCount': Motion.meta.totalPointCount,
            'UserDataCount': Motion.meta.userDataCount,
            'TotalUserDataSize': Motion.meta.totalUserDataSize
        },
        'Curves': [
            {
                'Target': curve.target,
                'Id': curve.id,
                'FadeInTime': curve.fadeInTime,
                'FadeOutTime': curve.fadeOutTime,
                'Segments': curve.segments
            }
            for curve in Motion.curves
        ],
        'UserData': Motion.userData
    }
    with open(path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
