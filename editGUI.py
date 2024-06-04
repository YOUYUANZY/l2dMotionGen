import json
import math
import tkinter as tk
from tkinter import ttk, filedialog

from ProcessJsonData import loadJsonData, saveMotionJson
from motionJson import MotionJson, MotionCurve
from utils.BezierCurve import segmentsIndex
from utils.CurveProcess import getCountInfo
from utils.GUIclasses import GUI_Canvas
from utils.utils import getOvalId, getCurveInit


class MotionJsonEditor(tk.Tk):
    def __init__(self):
        super(MotionJsonEditor, self).__init__()
        self.curves = []
        self.rows = []
        # 当前操作曲线下标
        self.curve_idx = -1

        self._drag_data = {}
        # 曲线编辑画布信息
        self.CurveCanvas_info = GUI_Canvas()
        # 曲线编辑画布操作实例
        self.CurveCanvas_op = None
        # 曲线关键点
        self.keyPoints = []

        self.motion = MotionJson()
        self.title('Motion edit')
        self.bind('<Configure>', self.on_window_resize)
        self.create_widgets()

    def on_window_resize(self, event):
        if self.curve_idx != -1:
            self.edit_Curve(self.curve_idx)

    # 加载Json
    def loadJson(self):
        file_path = filedialog.askopenfilename(
            title="Open JSON File",
            filetypes=(("JSON files", "*.motion3.json"), ("All files", "*.*"))
        )
        if file_path:
            with open(file_path, 'r') as json_file:
                json_data = json.load(json_file)
                self.motion.loadJson(json_data)

                self.version.delete(0, tk.END)
                self.version.insert(0, self.motion.version)
                self.duration.delete(0, tk.END)
                self.duration.insert(0, self.motion.meta.duration)
                self.fps.delete(0, tk.END)
                self.fps.insert(0, self.motion.meta.fps)
                self.loop_var.set(self.motion.meta.loop)

                self.clear_all_rows_and_curves()
                for curve in self.motion.curves:
                    self.curves.append(curve)
                    x, _ = segmentsIndex(curve.segments)
                    self.add_row(default_att=curve.id, default_kpNum=len(x), add_curve=False)
                self.motion.curves = []

    # 保存Json
    def saveJson(self):
        self.motion.meta.loop = self.loop_var.get()
        save_path = filedialog.asksaveasfilename(
            title="Save JSON File",
            defaultextension=".json",
            filetypes=(("JSON files", "*.motion3.json"), ("All files", "*.*"))
        )
        if save_path == '':
            return
        self.motion.curves = self.curves
        curve_count, segment_count, point_count = getCountInfo(self.motion.curves)
        self.motion.meta.curveCount = curve_count
        self.motion.meta.totalSegmentCount = segment_count
        self.motion.meta.totalPointCount = point_count
        saveMotionJson(self.motion, path=save_path)

    # 设置版本
    def set_version(self, event):
        value = event.widget.get()
        self.motion.version = int(value)

    # 设置时长
    def set_duration(self, event):
        value = event.widget.get()
        self.motion.meta.duration = float(value)

    # 设置帧率
    def set_fps(self, event):
        value = event.widget.get()
        self.motion.meta.fps = float(value)

    # 设置循环
    def set_loop(self, event):
        value = event.widget.get()
        self.motion.meta.fps = bool(value)

    # 保存曲线
    def saveCurve(self):
        segment = []
        x, y = self.CurveCanvas_info.getRealPoint(self.keyPoints[0], self.keyPoints[1])
        segment.extend([x, y])
        i = 2
        while i < len(self.keyPoints):
            x, y = self.CurveCanvas_info.getRealPoint(self.keyPoints[i], self.keyPoints[i + 1])
            segment.extend([0, x, y])
            i += 2
        self.curves[self.curve_idx].segments = segment

    # 重置曲线
    def resetCurve(self):
        num = int(len(self.keyPoints) / 2)
        self.curves[self.curve_idx].segments = getCurveInit(num, self.motion.meta.duration)
        self.edit_Curve(self.curve_idx)

    # 基本功能块
    def baseBlock(self, frame):
        # Version
        ttk.Label(frame, text="Version:").grid(column=0, row=0, sticky=tk.W)
        self.version = ttk.Entry(frame)
        self.version.grid(column=1, row=0, sticky=tk.W)
        self.version.insert(0, self.motion.version)
        self.version.bind("<Return>", self.set_version)
        self.version.bind("<FocusOut>", self.set_version)
        # Duration
        ttk.Label(frame, text="Duration:").grid(column=0, row=1, sticky=tk.W)
        self.duration = ttk.Entry(frame)
        self.duration.grid(column=1, row=1, sticky=tk.W)
        self.duration.insert(0, self.motion.meta.duration)
        self.duration.bind("<Return>", self.set_duration)
        self.duration.bind("<FocusOut>", self.set_duration)
        # FPS
        ttk.Label(frame, text="FPS:").grid(column=0, row=2, sticky=tk.W)
        self.fps = ttk.Entry(frame)
        self.fps.grid(column=1, row=2, sticky=tk.W)
        self.fps.insert(0, self.motion.meta.fps)
        self.fps.bind("<Return>", self.set_fps)
        self.fps.bind("<FocusOut>", self.set_fps)
        # Loop
        ttk.Label(frame, text="Loop:").grid(column=0, row=3, sticky=tk.W)
        self.loop_var = tk.BooleanVar()
        self.loop = ttk.Checkbutton(frame, variable=self.loop_var)
        self.loop.grid(column=1, row=3, sticky=tk.W)
        self.loop_var.set(self.motion.meta.loop)
        # save&load
        load_button = ttk.Button(frame, text="Load JSON", command=self.loadJson)
        load_button.grid(column=0, row=4, sticky=tk.W)
        save_button = ttk.Button(frame, text="Save JSON", command=self.saveJson)
        save_button.grid(column=1, row=4, sticky=tk.W)
        # add&remove
        add = ttk.Button(frame, text="Add Row", command=self.add_row)
        remove = ttk.Button(frame, text="Remove Last Row", command=self.remove_last_row)
        add.grid(column=0, row=5, sticky=tk.W)
        remove.grid(column=1, row=5, sticky=tk.W)
        # saveCurve&reset
        saveCurve = ttk.Button(frame, text="Save Curve", command=self.saveCurve)
        resetCurve = ttk.Button(frame, text="Reset Curve", command=self.resetCurve)
        saveCurve.grid(column=0, row=6, sticky=tk.W)
        resetCurve.grid(column=1, row=6, sticky=tk.W)

    # 创建窗口
    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=3)
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=7)
        main_frame.rowconfigure(1, weight=10)

        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky='nsew')
        self.baseBlock(left_frame)

        self.right_frame = ttk.Frame(main_frame)
        self.right_frame.grid(row=0, column=1, sticky='nsew')
        self.right_frame.rowconfigure(0, weight=10)
        self.right_frame.columnconfigure(0, weight=10)
        self.right_frame.columnconfigure(1, weight=0)

        v_scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL)
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        self.canvas = tk.Canvas(self.right_frame, yscrollcommand=v_scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.config(command=self.canvas.yview)

        h_scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.HORIZONTAL)
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        self.canvas.configure(xscrollcommand=h_scrollbar.set)
        h_scrollbar.config(command=self.canvas.xview)

        self.scrollable_frame = ttk.Frame(self.canvas)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)

        self.CurveCanvas_op = tk.Canvas(main_frame, highlightthickness=2, highlightbackground='black')
        self.CurveCanvas_op.grid(row=1, column=0, columnspan=2, sticky='nsew')
        # 在 main_frame 中为滚动条保留空间
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=0)
        main_frame.columnconfigure(2, weight=0)
        curve_v_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.CurveCanvas_op.yview)
        curve_v_scrollbar.grid(row=1, column=2, sticky='ns')
        curve_h_scrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.CurveCanvas_op.xview)
        curve_h_scrollbar.grid(row=2, column=0, columnspan=2, sticky='ew')
        self.CurveCanvas_op.config(xscrollcommand=curve_h_scrollbar.set, yscrollcommand=curve_v_scrollbar.set)
        self.CurveCanvas_op.bind('<Configure>', self.on_curve_configure)
        self.CurveCanvas_op.bind('<MouseWheel>', self.on_mouse_wheel_curve)

        self.add_row()

    # 鼠标滚轮
    def on_mouse_wheel_curve(self, event):
        if event.delta > 0:
            self.CurveCanvas_op.yview_scroll(-2, 'units')  # 向上滚动
        else:
            self.CurveCanvas_op.yview_scroll(2, 'units')

    # 添加一行属性
    def add_row(self, default_att='', default_kpNum=0, add_curve=True):
        index = len(self.rows)
        row_frame = ttk.Frame(self.scrollable_frame)

        ttk.Label(row_frame, text="Attribute:").pack(side=tk.LEFT)
        att = ttk.Entry(row_frame)
        att.insert(0, default_att)
        att.pack(side=tk.LEFT)
        att.bind("<Return>", lambda event, idx=index: self.set_att(event, idx))
        att.bind("<FocusOut>", lambda event, idx=index: self.set_att(event, idx))

        ttk.Label(row_frame, text="KeyPoints:").pack(side=tk.LEFT)
        kpNum = ttk.Entry(row_frame)
        kpNum.insert(0, default_kpNum)
        kpNum.pack(side=tk.LEFT)
        kpNum.bind("<Return>", lambda event, idx=index: self.set_kpNum(event, idx))
        kpNum.bind("<FocusOut>", lambda event, idx=index: self.set_kpNum(event, idx))

        ttk.Button(row_frame, text="edit", command=lambda idx=index: self.edit_Curve(idx)).pack(side=tk.LEFT)
        row_frame.pack(side=tk.TOP, fill=tk.X)

        self.rows.append(row_frame)
        if add_curve:
            self.curves.append(MotionCurve())
        self.update_frame_region()

    # 设置属性
    def set_att(self, event, idx):
        value = event.widget.get()
        self.curves[idx].id = str(value)

    # 设置曲线节点数
    def set_kpNum(self, event, idx):
        value = event.widget.get()
        num = int(value)
        self.curves[idx].segments = getCurveInit(num, self.motion.meta.duration)

    # 绘制曲线
    def draw_curve(self):
        segments = self.curves[self.curve_idx].segments
        self.CurveCanvas_op.delete("all")
        self.CurveCanvas_info.W = self.CurveCanvas_op.winfo_width()
        self.CurveCanvas_info.H = self.CurveCanvas_op.winfo_height()

        x, y = segmentsIndex(segments)
        self.CurveCanvas_info.maxX = max(max(x) * 1.1, 1)
        self.CurveCanvas_info.maxY = max(int(max(y)) * 1.1, 1)
        self.CurveCanvas_info.minY = min(int(min(y)) * 1.1, 0)

        for i in range(0, math.ceil(self.CurveCanvas_info.maxX), 1):
            x1, y1 = self.CurveCanvas_info.getCanvasPoint(i, math.floor(self.CurveCanvas_info.minY)-1)
            x2, y2 = self.CurveCanvas_info.getCanvasPoint(i, math.ceil(self.CurveCanvas_info.maxY)+1)
            self.CurveCanvas_op.create_line([(x1, y1), (x2, y2)], tag='grid_line', fill='gray')

        for i in range(math.floor(self.CurveCanvas_info.minY), math.ceil(self.CurveCanvas_info.maxY), 1):
            x1, y1 = self.CurveCanvas_info.getCanvasPoint(0, i)
            x2, y2 = self.CurveCanvas_info.getCanvasPoint(math.ceil(self.CurveCanvas_info.maxX), i)
            self.CurveCanvas_op.create_line([(x1, y1), (x2, y2)], tag='grid_line', fill='gray')

        self.keyPoints = []
        for i in range(len(x)):
            x_, y_ = self.CurveCanvas_info.getCanvasPoint(x[i], y[i])
            self.keyPoints.extend([x_, y_])
            self.create_edit_oval(x_ - 2.5, y_ - 2.5, x_ + 2.5, y_ + 2.5, f"oval{i}")

        self.CurveCanvas_op.create_line(self.keyPoints, fill="black", tags="curve")

    # 创建编辑节点
    def create_edit_oval(self, x1, y1, x2, y2, tag):
        # 创建空心圆，每个圆有一个唯一的tag
        oval_id = self.CurveCanvas_op.create_oval(x1, y1, x2, y2, outline="black", fill="white",
                                                  tags=(tag, "draggable"))
        # 初始化数据
        oval_center_x = (x1 + x2) / 2
        oval_center_y = (y1 + y2) / 2
        self._drag_data[tag] = {"x": oval_center_x, "y": oval_center_y}
        # 为每个圆分别绑定拖动事件
        self.CurveCanvas_op.tag_bind(oval_id, "<Button-1>",
                                     lambda event, oval_tag=tag: self.on_drag_start(event, oval_tag))
        self.CurveCanvas_op.tag_bind(oval_id, "<B1-Motion>",
                                     lambda event, oval_tag=tag: self.on_drag_move(event, oval_tag))
        self.CurveCanvas_op.tag_bind(oval_id, "<Enter>",
                                     lambda event, oval_tag=tag: self.CurveCanvas_op.itemconfig(oval_tag, fill="grey"))
        self.CurveCanvas_op.tag_bind(oval_id, "<Leave>",
                                     lambda event, oval_tag=tag: self.CurveCanvas_op.itemconfig(oval_tag, fill="white"))

    # 获取节点位置
    def on_drag_start(self, event, tag):
        # 记录开始拖动的圆的起始位置
        self._drag_data[tag] = {"x": event.x, "y": event.y}

    # 节点拖拽
    def on_drag_move(self, event, tag):
        XMaxLimit = self.motion.meta.duration
        XMaxLimit, _ = self.CurveCanvas_info.getCanvasPoint(XMaxLimit, 0)
        idx = getOvalId(tag)
        # 计算限制范围
        tl = f"oval{idx - 1}"
        XL = 0 if idx == 0 else self._drag_data[tl]["x"]
        tr = f"oval{idx + 1}"
        XR = XMaxLimit if idx == (len(self.keyPoints) / 2 - 1) else self._drag_data[tr]["x"]
        # 计算移动的距离
        delta_x = max(XL, min(XR, event.x)) - self._drag_data[tag]["x"]
        delta_y = max(0, min(self.CurveCanvas_info.H, event.y)) - self._drag_data[tag]["y"]
        # 根据tag移动对应的圆
        self.CurveCanvas_op.move(tag, delta_x, delta_y)
        newX = self._drag_data[tag]["x"] + delta_x
        newY = self._drag_data[tag]["y"] + delta_y
        # 更新此圆的位置以备后续拖动
        self._drag_data[tag] = {"x": newX, "y": newY}
        # 每次拖动后都重新绘制曲线
        self.redraw_curve()

    # 重绘曲线
    def redraw_curve(self):
        # 重新构建曲线点列表
        L = int(len(self.keyPoints) / 2)
        self.keyPoints = []
        for tag in range(L):
            # 获取每个圆的位置并加入点列表
            x1, y1, x2, y2 = self.CurveCanvas_op.coords(f"oval{tag}")
            self.keyPoints.extend([(x1 + x2) / 2, (y1 + y2) / 2])
        # 使用新的点列表重新绘制曲线
        self.CurveCanvas_op.delete("curve")
        self.CurveCanvas_op.create_line(self.keyPoints, fill="black", tags="curve")

    # 编辑曲线
    def edit_Curve(self, idx):
        self.curve_idx = idx
        self.draw_curve()
        self.update_curve_region()

    # 删除一行属性
    def remove_last_row(self):
        if self.rows:
            self.curves.pop()
            row = self.rows.pop()
            row.destroy()
            self.update_frame_region()

    # 删除所有属性
    def clear_all_rows_and_curves(self):
        for row_frame in self.rows:
            row_frame.destroy()

        self.rows.clear()
        self.curves.clear()
        self.update_frame_region()

    # 更新属性滑动区域
    def update_frame_region(self):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # 更新曲线滑动区域
    def update_curve_region(self):
        self.CurveCanvas_op.config(scrollregion=self.CurveCanvas_op.bbox("all"))

    def on_curve_configure(self, event):
        self.CurveCanvas_op.config(scrollregion=self.CurveCanvas_op.bbox("all"))


if __name__ == "__main__":
    app = MotionJsonEditor()
    app.mainloop()
