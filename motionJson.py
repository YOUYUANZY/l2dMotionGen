class MotionCurve:
    def __init__(self):
        self.target = 'Parameter'
        self.id = ''
        self.fadeInTime = -1.0
        self.fadeOutTime = -1.0
        self.segments = []
        self.remark = ''
        self.maxValue = 0
        self.minValue = 0

    def loadCurve(self, Curve):
        self.target = Curve['Target']
        self.id = Curve['Id']
        self.fadeInTime = Curve['FadeInTime']
        self.fadeOutTime = Curve['FadeOutTime']
        self.segments = Curve['Segments']


class MotionMeta:
    def __init__(self):
        self.duration = 0
        self.fps = 60.0
        self.loop = True
        self.areBeziersRestricted = True
        self.fadeInTime = 0.0
        self.fadeOutTime = 0.0
        self.curveCount = 0
        self.totalSegmentCount = 0
        self.totalPointCount = 0
        self.userDataCount = 1
        self.totalUserDataSize = 0

    def loadMeta(self, MetaData):
        self.duration = MetaData['Duration']
        self.fps = MetaData['Fps']
        self.loop = MetaData['Loop']
        self.areBeziersRestricted = MetaData['AreBeziersRestricted']
        self.fadeInTime = MetaData['FadeInTime']
        self.fadeOutTime = MetaData['FadeOutTime']
        self.curveCount = MetaData['CurveCount']
        self.totalSegmentCount = MetaData['TotalSegmentCount']
        self.totalPointCount = MetaData['TotalPointCount']
        self.userDataCount = MetaData['UserDataCount']
        self.totalUserDataSize = MetaData['TotalUserDataSize']


class MotionJson:
    def __init__(self):
        self.version = 3
        self.meta = MotionMeta()
        self.curves = []
        self.userData = [{"Time": 0.0, "Value": ""}]

    def loadJson(self, JsonData):
        self.version = JsonData['Version']
        self.meta.loadMeta(JsonData['Meta'])
        self.curves = self.loadCurves(JsonData['Curves'])
        self.userData = JsonData['UserData']

    def loadCurves(self, Curves):
        curves = []
        for curve in Curves:
            tmp = MotionCurve()
            tmp.loadCurve(curve)
            curves.append(tmp)
        return curves
