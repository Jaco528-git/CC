import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
from pathlib import Path
import sys

CONFIG_FILE = Path.home() / ".pomodoro_config.json"
DEFAULT_CONFIG = {
    "work_minutes": 25,
    "short_break_minutes": 5,
    "long_break_minutes": 15,
    "sessions_before_long_break": 4,
    "always_on_top": True,
}

COLORS = {
    "work": "#e74c3c",
    "work_bg": "#2c2c2c",
    "break": "#27ae60",
    "text": "#ecf0f1",
    "button_bg": "#3c3c3c",
    "button_fg": "#ecf0f1",
    "progress_bg": "#1a1a1a",
}


class PomodoroTimer:
    def __init__(self):
        self.config = self._load_config()
        self.mode = "work"
        self.remaining = self._get_mode_seconds("work")
        self.running = False
        self.paused = False
        self.session_count = 0
        self.completed_sessions = 0
        self._stop_flag = False

        self._setup_ui()
        self._update_display()
        self._update_status_bar()

    def _load_config(self):
        if CONFIG_FILE.exists():
            try:
                data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                return {**DEFAULT_CONFIG, **data}
            except Exception:
                pass
        return dict(DEFAULT_CONFIG)

    def _save_config(self):
        CONFIG_FILE.write_text(json.dumps(self.config, indent=2, ensure_ascii=False), encoding="utf-8")

    def _get_mode_seconds(self, mode):
        if mode == "work":
            return self.config["work_minutes"] * 60
        elif mode == "short_break":
            return self.config["short_break_minutes"] * 60
        else:
            return self.config["long_break_minutes"] * 60

    def _setup_ui(self):
        self.root = tk.Tk()
        self.root.title("🍅 番茄钟")
        self.root.geometry("360x520")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS["work_bg"])
        self.root.attributes("-topmost", self.config["always_on_top"])

        self.root.bind("<Button-1>", self._start_move)
        self.root.bind("<B1-Motion>", self._on_move)

        style = ttk.Style()
        style.theme_use("clam")

        # 标题栏
        title_bar = tk.Frame(self.root, bg=COLORS["work_bg"], height=32, cursor="fleur")
        title_bar.pack(fill="x")
        title_bar.bind("<Button-1>", self._start_move)
        title_bar.bind("<B1-Motion>", self._on_move)

        title_label = tk.Label(title_bar, text="🍅 番茄钟", bg=COLORS["work_bg"],
                               fg=COLORS["text"], font=("Microsoft YaHei", 10))
        title_label.pack(side="left", padx=12)
        title_label.bind("<Button-1>", self._start_move)
        title_label.bind("<B1-Motion>", self._on_move)

        close_btn = tk.Label(title_bar, text="✕", bg=COLORS["work_bg"],
                             fg="#888", font=("Segoe UI", 12), cursor="hand2")
        close_btn.pack(side="right", padx=(0, 10))
        close_btn.bind("<Button-1>", lambda e: self._on_close())
        close_btn.bind("<Enter>", lambda e: close_btn.configure(fg=COLORS["text"]))
        close_btn.bind("<Leave>", lambda e: close_btn.configure(fg="#888"))

        min_btn = tk.Label(title_bar, text="─", bg=COLORS["work_bg"],
                           fg="#888", font=("Segoe UI", 12), cursor="hand2")
        min_btn.pack(side="right", padx=(0, 5))
        min_btn.bind("<Button-1>", lambda e: self._minimize_to_tray())
        min_btn.bind("<Enter>", lambda e: min_btn.configure(fg=COLORS["text"]))
        min_btn.bind("<Leave>", lambda e: min_btn.configure(fg="#888"))

        # 主内容区
        main = tk.Frame(self.root, bg=COLORS["work_bg"])
        main.pack(expand=True, fill="both", padx=20, pady=(0, 20))

        self.mode_label = tk.Label(main, text="专注时间", bg=COLORS["work_bg"],
                                   fg=COLORS["work"], font=("Microsoft YaHei", 13, "bold"))
        self.mode_label.pack(pady=(10, 5))

        self.session_label = tk.Label(main, text="", bg=COLORS["work_bg"],
                                      fg="#888", font=("Microsoft YaHei", 9))
        self.session_label.pack()

        # 画布（进度环 + 时间）
        canvas_size = 220
        self.canvas = tk.Canvas(main, width=canvas_size, height=canvas_size,
                                bg=COLORS["work_bg"], highlightthickness=0)
        self.canvas.pack(pady=(10, 10))

        cx, cy, r = canvas_size // 2, canvas_size // 2, 90
        self.progress_arc = self.canvas.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=90, extent=360, outline="", fill="", width=0,
        )
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                outline="#444", width=6)

        self.time_text = self.canvas.create_text(
            cx, cy - 15, text="25:00",
            fill=COLORS["text"], font=("Segoe UI", 46, "bold"),
        )
        self.status_text = self.canvas.create_text(
            cx, cy + 35, text="就绪",
            fill="#888", font=("Microsoft YaHei", 11),
        )

        # 控制按钮
        btn_frame = tk.Frame(main, bg=COLORS["work_bg"])
        btn_frame.pack(pady=(5, 10))

        self.start_btn = self._make_button(btn_frame, "▶ 开始", 12, self._toggle_timer)
        self.start_btn.pack(side="left", padx=5)

        self.reset_btn = self._make_button(btn_frame, "⟳ 重置", 12, self._reset_timer)
        self.reset_btn.pack(side="left", padx=5)

        self.skip_btn = self._make_button(btn_frame, "⏭ 跳过", 12, self._skip_phase)
        self.skip_btn.pack(side="left", padx=5)

        # 底部
        bottom = tk.Frame(self.root, bg=COLORS["work_bg"])
        bottom.pack(fill="x", padx=20, pady=(0, 12))

        settings_frame = tk.Frame(bottom, bg=COLORS["work_bg"])
        settings_frame.pack(fill="x")

        self.pin_var = tk.BooleanVar(value=self.config["always_on_top"])
        pin_cb = tk.Checkbutton(settings_frame, text="置顶", variable=self.pin_var,
                                bg=COLORS["work_bg"], fg="#aaa", selectcolor=COLORS["work_bg"],
                                font=("Microsoft YaHei", 9),
                                activebackground=COLORS["work_bg"], activeforeground=COLORS["text"],
                                command=self._toggle_pin)
        pin_cb.pack(side="left")

        self.progress_frame = tk.Frame(bottom, bg=COLORS["progress_bg"], height=4)
        self.progress_frame.pack(fill="x", pady=(6, 0))
        self.progress_bar = tk.Frame(self.progress_frame, bg=COLORS["work"], height=4)
        self.progress_bar.place(x=0, y=0, width=0, height=4)

        # 键盘快捷键
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.bind("<space>", lambda e: self._toggle_timer())
        self.root.bind("<Escape>", lambda e: self._minimize_to_tray())
        self.root.bind("<r>", lambda e: self._reset_timer())

        self.tray_icon = None
        self._try_init_tray()

    def _make_button(self, parent, text, size, command):
        btn = tk.Button(parent, text=text, command=command,
                        bg=COLORS["button_bg"], fg=COLORS["button_fg"],
                        font=("Microsoft YaHei", size),
                        relief="flat", padx=16, pady=6, cursor="hand2",
                        activebackground="#555", activeforeground=COLORS["text"],
                        bd=0)
        btn.bind("<Enter>", lambda e: btn.configure(bg="#555"))
        btn.bind("<Leave>", lambda e: btn.configure(bg=COLORS["button_bg"]))
        return btn

    def _update_colors(self, mode):
        color = COLORS["work"] if mode == "work" else COLORS["break"]
        self.root.configure(bg=COLORS["work_bg"])
        self.canvas.itemconfig(self.progress_arc, outline=color)
        if hasattr(self, 'progress_bar'):
            self.progress_bar.configure(bg=color)

    def _start_move(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_move(self, event):
        dx = event.x - self._drag_x
        dy = event.y - self._drag_y
        x = self.root.winfo_x() + dx
        y = self.root.winfo_y() + dy
        self.root.geometry(f"+{x}+{y}")

    def _try_init_tray(self):
        try:
            import pystray
            from PIL import Image, ImageDraw
            self._tray_available = True

            img = Image.new("RGBA", (64, 64), (231, 76, 60, 255))
            draw = ImageDraw.Draw(img)
            draw.ellipse([8, 8, 56, 56], fill=(231, 76, 60, 255))
            draw.ellipse([20, 16, 44, 40], fill=(255, 255, 255, 255))

            def on_show(icon, item):
                icon.stop()
                self.root.after(0, self._restore_from_tray)

            def on_exit(icon, item):
                icon.stop()
                self.root.after(0, self._do_quit)

            menu = pystray.Menu(
                pystray.MenuItem("显示窗口", on_show, default=True),
                pystray.MenuItem("退出", on_exit),
            )
            self.tray_icon = pystray.Icon("pomodoro", img, "🍅 番茄钟", menu)
        except ImportError:
            self._tray_available = False

    def _minimize_to_tray(self):
        if self._tray_available and self.tray_icon:
            self.root.withdraw()
            t = threading.Thread(target=self.tray_icon.run, daemon=True)
            t.start()
        else:
            self.root.iconify()

    def _restore_from_tray(self):
        self.root.deiconify()
        self.root.lift()

    def _on_close(self):
        if self.running:
            if not messagebox.askokcancel("关闭", "计时器正在运行，确认关闭？"):
                return
        self._do_quit()

    def _do_quit(self):
        self._stop_flag = True
        self._save_config()
        self.root.destroy()
        sys.exit(0)

    # --- 核心逻辑 ---
    def _toggle_timer(self):
        if not self.running:
            self._start_timer()
        elif self.paused:
            self._resume_timer()
        else:
            self._pause_timer()

    def _start_timer(self):
        self.running = True
        self.paused = False
        self._stop_flag = False
        self.start_btn.configure(text="⏸ 暂停")
        self.canvas.itemconfig(self.status_text, text="运行中")
        self._tick_loop()

    def _pause_timer(self):
        self.paused = True
        self.start_btn.configure(text="▶ 继续")
        self.canvas.itemconfig(self.status_text, text="已暂停")

    def _resume_timer(self):
        self.paused = False
        self.start_btn.configure(text="⏸ 暂停")
        self.canvas.itemconfig(self.status_text, text="运行中")
        self._tick_loop()

    def _reset_timer(self):
        self.running = False
        self.paused = False
        self._stop_flag = True
        self.remaining = self._get_mode_seconds(self.mode)
        self.start_btn.configure(text="▶ 开始")
        self._update_display()
        self.canvas.itemconfig(self.status_text, text="已重置")
        self._update_progress()

    def _skip_phase(self):
        self.running = False
        self.paused = False
        self._stop_flag = True
        self.remaining = 1
        self._tick()

    def _tick_loop(self):
        if self._stop_flag or self.paused:
            return
        self._tick()
        if self.running and not self.paused:
            self.root.after(500, self._tick_loop)

    def _tick(self):
        if self._stop_flag:
            return
        if self.remaining <= 0:
            self._on_phase_complete()
            return
        self.remaining -= 1
        self._update_display()
        self._update_progress()

    def _update_display(self):
        mins, secs = divmod(max(self.remaining, 0), 60)
        self.canvas.itemconfig(self.time_text, text=f"{mins:02d}:{secs:02d}")

        total = self._get_mode_seconds(self.mode)
        pct = 1 - (self.remaining / total) if total > 0 else 0
        self.canvas.itemconfig(self.progress_arc, extent=360 * pct,
                               outline=COLORS["work"] if self.mode == "work" else COLORS["break"])

        prefix = "专注" if self.mode == "work" else "休息"
        self.root.title(f"{prefix} {self.canvas.itemcget(self.time_text, 'text')} - 🍅 番茄钟")

    def _update_progress(self):
        total = self._get_mode_seconds(self.mode)
        pct = 1 - (self.remaining / total) if total > 0 else 0
        w = int(self.progress_frame.winfo_width() * pct) if self.progress_frame.winfo_width() > 0 else 0
        self.progress_bar.place(x=0, y=0, width=w, height=4)

    def _update_status_bar(self):
        self.session_label.configure(
            text=f"已完成 {self.completed_sessions} 个番茄 · "
                 f"第 {self.session_count + 1}/{self.config['sessions_before_long_break']} 个"
        )

    def _on_phase_complete(self):
        self.running = False
        self._stop_flag = True

        if self.mode == "work":
            self.completed_sessions += 1
            self.session_count += 1
            self._show_notification("🍅 专注完成！", "休息一下吧~")
            if self.session_count >= self.config["sessions_before_long_break"]:
                self.mode = "long_break"
                self.session_count = 0
            else:
                self.mode = "short_break"
        else:
            self._show_notification("⏰ 休息结束", "开始新的番茄吧！")
            self.mode = "work"

        self.remaining = self._get_mode_seconds(self.mode)
        self._update_colors(self.mode)
        mode_text = "专注时间" if self.mode == "work" else "休息时间"
        self.mode_label.configure(text=mode_text,
                                  fg=COLORS["work"] if self.mode == "work" else COLORS["break"])
        self._update_status_bar()
        self._update_display()
        self.canvas.itemconfig(self.status_text, text="完成")
        self.start_btn.configure(text="▶ 开始")
        self.root.after(500, self._auto_continue)

    def _auto_continue(self):
        if self.config.get("auto_start", False):
            self._start_timer()

    def _show_notification(self, title, message):
        try:
            from plyer import notification
            notification.notify(title=title, message=message, app_name="🍅 番茄钟", timeout=5)
            return
        except ImportError:
            pass
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, message, title, 0x40 | 0x1000)
        except Exception:
            pass

    def _toggle_pin(self):
        self.config["always_on_top"] = self.pin_var.get()
        self.root.attributes("-topmost", self.config["always_on_top"])

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    PomodoroTimer().run()
