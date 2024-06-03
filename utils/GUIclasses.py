class GUI_Canvas:
    def __init__(self):
        self.W = 0
        self.H = 0
        self.maxY = 0
        self.minY = 0
        self.maxX = 0

    def getRealPoint(self, x, y):
        realX = x / self.W * self.maxX
        realY = (self.H - y) / self.H * (self.maxY - self.minY) + self.minY
        return realX, realY

    def getCanvasPoint(self, x, y):
        X = (x / self.maxX) * self.W
        Y = self.H - (y - self.minY) / (self.maxY - self.minY) * self.H
        return X, Y
