import cv2
import numpy as np
import turtle as t
import threading
import os
import time
import pygame
import tkinter as tk
import sys

IMAGE_PATH = "1.jpg"
AUDIO_PATH = "none"

AUDIO_START_AT = 0
AUDIO_PLAY_FOR = 0
AUDIO_DELAY = 0

MAX_WIDTH = 3500
MAX_CORNERS = 8500
QUALITY = 0.0000000000000005
MIN_DISTANCE = 3

EDGE_THRESHOLD1 = 60
EDGE_THRESHOLD2 = 150
EDGE_POINT_STEP = 5

BG_COLOR = "black"
PEN_SIZE = 0.7
SPEED = 0
TRACER_N = 17000
MAX_VIEW_SIZE = 1200

DRAW_DELAY = 0.5


def setup_window():
    screen = t.Screen()
    screen.title("poly_art")
    canvas = screen.getcanvas()
    root = canvas.winfo_toplevel()

    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    return screen, canvas, root, screen_width, screen_height


def force_front(root, screen_width, screen_height, win_w, win_h):
    x = (screen_width - win_w) // 2
    y = (screen_height - win_h) // 2

    root.geometry(f"{win_w}x{win_h}+{x}+{y}")
    root.update_idletasks()

    if sys.platform == 'darwin':  # macOS
        os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
    elif sys.platform == 'win32':  # Windows
        root.wm_attributes('-topmost', 1)
        root.after_idle(root.attributes, '-topmost', False)

    root.lift()
    root.attributes('-topmost', True)
    root.update()
    root.focus_force()
    root.grab_set()
    root.update()

    def release_topmost():
        root.attributes('-topmost', False)
        root.grab_release()

    root.after(200, release_topmost)


def build_triangles_and_colors(path):
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(path)

    h, w = img.shape[:2]

    if w > MAX_WIDTH:
        scale = MAX_WIDTH / w
        img = cv2.resize(img, (int(w * scale), int(h * scale)))
        h, w = img.shape[:2]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    corners = cv2.goodFeaturesToTrack(
        gray,
        maxCorners=MAX_CORNERS,
        qualityLevel=QUALITY,
        minDistance=MIN_DISTANCE
    ).reshape(-1, 2)

    edges = cv2.Canny(gray, EDGE_THRESHOLD1, EDGE_THRESHOLD2)
    edge_pts = [
        (x, y)
        for y in range(0, h, EDGE_POINT_STEP)
        for x in range(0, w, EDGE_POINT_STEP)
        if edges[y, x] != 0
    ]
    edge_pts = np.array(edge_pts, dtype=np.float32)

    boundary = np.array([
        [0, 0], [w // 2, 0], [w - 1, 0],
        [0, h // 2], [w - 1, h // 2],
        [0, h - 1], [w // 2, h - 1], [w - 1, h - 1]
    ], dtype=np.float32)

    pts = np.vstack([corners, edge_pts, boundary])
    pts = np.unique(np.round(pts).astype(np.int32), axis=0).astype(np.float32)

    subdiv = cv2.Subdiv2D((0, 0, w, h))
    for (x, y) in pts:
        subdiv.insert((float(x), float(y)))

    tri_raw = subdiv.getTriangleList().reshape(-1, 6)

    triangles, colors = [], []
    for x1, y1, x2, y2, x3, y3 in tri_raw:
        if not (0 <= x1 < w and 0 <= y1 < h and
                0 <= x2 < w and 0 <= y2 < h and
                0 <= x3 < w and 0 <= y3 < h):
            continue

        triangles.append([(x1, y1), (x2, y2), (x3, y3)])
        cx = int((x1 + x2 + x3) / 3)
        cy = int((y1 + y2 + y3) / 3)
        b, g, r = img[cy, cx]
        colors.append((int(r), int(g), int(b)))

    return triangles, colors, w, h


def to_turtle(x, y, w, h, scale):
    return (x - w / 2) * scale, (h / 2 - y) * scale


def draw_lowpoly(triangles, colors, w, h):
    ratio = min(MAX_VIEW_SIZE / w, MAX_VIEW_SIZE / h, 1.0)
    win_w = int(w * ratio) + 40
    win_h = int(h * ratio) + 40

    screen, canvas, root, screen_width, screen_height = setup_window()

    t.setup(win_w, win_h)
    t.bgcolor(BG_COLOR)
    t.colormode(255)
    t.pensize(PEN_SIZE)
    t.speed(SPEED)
    t.tracer(TRACER_N, 0)
    t.hideturtle()

    root.update()
    root.update_idletasks()
    force_front(root, screen_width, screen_height, win_w, win_h)
    root.update()
    root.update_idletasks()

    scale = ratio

    time.sleep(DRAW_DELAY)

    for tri, col in zip(triangles, colors):
        (x1, y1), (x2, y2), (x3, y3) = tri
        tx1, ty1 = to_turtle(x1, y1, w, h, scale)
        tx2, ty2 = to_turtle(x2, y2, w, h, scale)
        tx3, ty3 = to_turtle(x3, y3, w, h, scale)

        t.fillcolor(col)
        t.pencolor(col)

        t.penup()
        t.goto(tx1, ty1)
        t.pendown()
        t.begin_fill()
        t.goto(tx2, ty2)
        t.goto(tx3, ty3)
        t.goto(tx1, ty1)
        t.end_fill()
        t.penup()

    t.update()
    t.done()


def play_audio_segment():
    if not os.path.exists(AUDIO_PATH):
        print("Audio not found:", AUDIO_PATH)
        return

    try:
        time.sleep(AUDIO_DELAY)

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        pygame.mixer.music.load(AUDIO_PATH)
        pygame.mixer.music.play(start=AUDIO_START_AT)

        def stop_after():
            time.sleep(AUDIO_PLAY_FOR)
            pygame.mixer.music.stop()

        threading.Thread(target=stop_after, daemon=True).start()

    except pygame.error as e:
        print("Audio error (pygame):", e)


if __name__ == "__main__":
    threading.Thread(target=play_audio_segment, daemon=True).start()
    tris, cols, w, h = build_triangles_and_colors(IMAGE_PATH)
    print(f"Generated {len(tris)} triangles")
    draw_lowpoly(tris, cols, w, h)