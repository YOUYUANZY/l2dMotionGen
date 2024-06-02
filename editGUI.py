import json
import tkinter as tk
from tkinter import ttk, filedialog

from ProcessJsonData import loadJsonData, saveMotionJson
from motionJson import MotionJson, MotionCurve
from utils.BezierCurve import segmentsIndex


class MotionJsonEditor:
    def __init__(self, root):
        self.curves = []
        self.rows = []
        self._drag_data = {}

        self.root = root
        self.root.title("Motion Editor")

        self.motion = MotionJson()

        self.create_widgets()

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

    def saveJson(self):
        self.motion.meta.loop = self.loop_var.get()
        save_path = filedialog.asksaveasfilename(
            title="Save JSON File",
            defaultextension=".json",
            filetypes=(("JSON files", "*.motion3.json"), ("All files", "*.*"))
        )
        if save_path == '':
            return
        saveMotionJson(self.motion, path=save_path)

    def set_version(self, event):
        value = event.widget.get()
        self.motion.version = int(value)

    def set_duration(self, event):
        value = event.widget.get()
        self.motion.meta.duration = float(value)

    def set_fps(self, event):
        value = event.widget.get()
        self.motion.meta.fps = float(value)

    def set_loop(self, event):
        value = event.widget.get()
        self.motion.meta.fps = bool(value)

    def baseBlock(self, frame):
        # Version
        ttk.Label(frame, text="Version:").grid(column=0, row=0, sticky=tk.W)
        version = ttk.Entry(frame)
        version.grid(column=1, row=0, sticky=tk.W)
        version.insert(0, self.motion.version)
        version.bind("<Return>", self.set_version)
        version.bind("<FocusOut>", self.set_version)
        # Duration
        ttk.Label(frame, text="Duration:").grid(column=0, row=1, sticky=tk.W)
        duration = ttk.Entry(frame)
        duration.grid(column=1, row=1, sticky=tk.W)
        duration.insert(0, self.motion.meta.duration)
        duration.bind("<Return>", self.set_duration)
        duration.bind("<FocusOut>", self.set_duration)
        # FPS
        ttk.Label(frame, text="FPS:").grid(column=0, row=2, sticky=tk.W)
        fps = ttk.Entry(frame)
        fps.grid(column=1, row=2, sticky=tk.W)
        fps.insert(0, self.motion.meta.fps)
        fps.bind("<Return>", self.set_fps)
        fps.bind("<FocusOut>", self.set_fps)
        # Loop
        ttk.Label(frame, text="Loop:").grid(column=0, row=3, sticky=tk.W)
        self.loop_var = tk.BooleanVar()
        self.loop = ttk.Checkbutton(frame, variable=self.loop_var)
        self.loop.grid(column=1, row=3, sticky=tk.W)
        self.loop_var.set(self.motion.meta.loop)
        # Buttons
        load_button = ttk.Button(frame, text="Load JSON", command=self.loadJson)
        load_button.grid(column=0, row=4, sticky=tk.W)

        save_button = ttk.Button(frame, text="Save JSON", command=self.saveJson)
        save_button.grid(column=1, row=4, sticky=tk.W)

        add = ttk.Button(frame, text="Add Row", command=self.add_row)
        remove = ttk.Button(frame, text="Remove Last Row", command=self.remove_last_row)
        add.grid(column=0, row=5, sticky=tk.W)
        remove.grid(column=1, row=5, sticky=tk.W)

    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
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

        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL)
        scrollbar.grid(row=0, column=1, sticky='nsew')

        self.canvas = tk.Canvas(self.right_frame, yscrollcommand=scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky='nsew')

        scrollbar.config(command=self.canvas.yview)

        self.scrollable_frame = ttk.Frame(self.canvas)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)
        self.bottom_canvas = tk.Canvas(main_frame, highlightthickness=2, highlightbackground='black')
        self.bottom_canvas.grid(row=1, column=0, columnspan=2, sticky='nsew')

        self.add_row()

    def add_row(self):
        index = len(self.rows)
        row_frame = ttk.Frame(self.scrollable_frame)

        ttk.Label(row_frame, text="Attribute:").pack(side=tk.LEFT)
        att = ttk.Entry(row_frame)
        att.pack(side=tk.LEFT)
        att.bind("<Return>", lambda event, idx=index: self.set_att(event, idx))
        att.bind("<FocusOut>", lambda event, idx=index: self.set_att(event, idx))

        ttk.Label(row_frame, text="KeyPoints:").pack(side=tk.LEFT)
        kpNum = ttk.Entry(row_frame)
        kpNum.pack(side=tk.LEFT)
        kpNum.bind("<Return>", lambda event, idx=index: self.set_kpNum(event, idx))
        kpNum.bind("<FocusOut>", lambda event, idx=index: self.set_kpNum(event, idx))

        ttk.Button(row_frame, text="edit", command=lambda idx=index: self.edit_Curve(idx)).pack(side=tk.LEFT)
        row_frame.pack(side=tk.TOP, fill=tk.X)

        self.rows.append(row_frame)
        self.curves.append(MotionCurve())
        self.update_scroll_region()

    def set_att(self, event, idx):
        value = event.widget.get()
        self.curves[idx].id = str(value)

    def set_kpNum(self, event, idx):
        value = event.widget.get()
        num = int(value)
        step = self.motion.meta.duration / (num - 1)
        segment = [0, 0]
        for i in range(num - 1):
            segment.extend([0, (i + 1) * step, 0])
        self.curves[idx].segments = segment
        print(segment)

    def draw_curve(self, canvas, idx):
        segments = self.curves[idx].segments
        canvas.delete("all")
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        x, y = segmentsIndex(segments)
        max_x = max(max(x), 1)
        max_y = 1
        min_y = -1

        points = []
        for i in range(len(x)):
            x_ = (x[i] / max_x) * canvas_width
            y_ = canvas_height - (y[i] - min_y) / (max_y - min_y) * canvas_height
            points.extend([x_, y_])
            self.create_draggable_oval(canvas, x_ - 5, y_ - 5, x_ + 5, y_ + 5, f"oval{i}", len(x))

        canvas.create_line(points, fill="black", tags="curve")

    def create_draggable_oval(self, canvas, x1, y1, x2, y2, tag, l):
        # 创建空心圆，每个圆有一个唯一的tag
        oval_id = canvas.create_oval(x1, y1, x2, y2, outline="black", fill="white", tags=(tag, "draggable"))
        # 为每个圆分别绑定拖动事件
        canvas.tag_bind(oval_id, "<Button-1>", lambda event, oval_tag=tag: self.on_drag_start(event, oval_tag))
        canvas.tag_bind(oval_id, "<B1-Motion>", lambda event, oval_tag=tag: self.on_drag_move(event, oval_tag, l))

    def on_drag_start(self, event, tag):
        # 记录开始拖动的圆的起始位置
        self._drag_data[tag] = {"x": event.x, "y": event.y}

    def on_drag_move(self, event, tag, l):
        # 计算移动的距离
        delta_x = event.x - self._drag_data[tag]["x"]
        delta_y = event.y - self._drag_data[tag]["y"]
        # 根据tag移动对应的圆
        self.bottom_canvas.move(tag, delta_x, delta_y)
        # 更新此圆的位置以备后续拖动
        self._drag_data[tag] = {"x": event.x, "y": event.y}
        # 每次拖动后都重新绘制曲线
        self.redraw_curve(l)

    def redraw_curve(self, l):
        # 重新构建曲线点列表
        points = []
        for tag in range(l):
            # 获取每个圆的位置并加入点列表
            x1, y1, x2, y2 = self.bottom_canvas.coords(f"oval{tag}")
            points.extend([(x1 + x2) / 2, (y1 + y2) / 2])
        # 使用新的点列表重新绘制曲线
        self.bottom_canvas.delete("curve")
        self.bottom_canvas.create_line(points, fill="black", tags="curve")

    def edit_Curve(self, idx):
        self.draw_curve(self.bottom_canvas, idx)

    def remove_last_row(self):
        if self.rows:
            self.curves.pop()
            row = self.rows.pop()
            row.destroy()
            self.update_scroll_region()
        print(len(self.curves))

    def update_scroll_region(self):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


if __name__ == "__main__":
    root = tk.Tk()
    app = MotionJsonEditor(root)
    root.mainloop()
