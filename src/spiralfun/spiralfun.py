#!/usr/bin/env python3
import math
import imageio
import io
import tkinter as tki
from typing import List

STEP_SIZE = math.radians(1) * 0.05
REDRAW_STEP = math.radians(5)


def calc_distance(point1, point2):
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    return math.sqrt(dx ** 2 + dy ** 2)


def calc_angle(origin, point):
    dy = point[1] - origin[1]
    r = calc_distance(origin, point)

    if dy > r:
        dy = r
    if dy < -r:
        dy = -r

    angle = math.asin(dy / r)

    if point[0] > origin[0]:
        return angle

    return math.pi - angle


class Circle:
    def __init__(self, space, center, radius) -> None:
        self.__space = space
        self.__center = center
        self.__radius = radius
        self.__draw = False
        canvas = space.get_canvas()
        canvas_center = space.space2canvas(center)
        x1 = canvas_center[0] - radius
        y1 = canvas_center[1] - radius
        x2 = canvas_center[0] + radius
        y2 = canvas_center[1] + radius
        self.__id = canvas.create_oval(x1, y1, x2, y2, outline='lightgreen')

    def get_center(self):
        return self.__center

    def get_radius(self):
        return self.__radius

    def set_draw(self, draw: bool):
        self.__draw = draw

    def moveto(self, new_center):
        canvas = self.__space.get_canvas()
        canvas_new_center = self.__space.space2canvas(new_center)

        if self.__draw:
            canvas_old_center = self.__space.space2canvas(self.__center)
            canvas.create_line(canvas_old_center[0], canvas_old_center[1], canvas_new_center[0], canvas_new_center[1])

        self.__center = new_center
        x = canvas_new_center[0] - self.__radius
        y = canvas_new_center[1] - self.__radius
        canvas.moveto(self.__id, x, y)

    def rotate(self, rotation_center, clockwise=True):
        angle = calc_angle(rotation_center, self.__center)
        angle += -STEP_SIZE if clockwise else STEP_SIZE
        d = calc_distance(rotation_center, self.__center)
        x = math.cos(angle) * d + rotation_center[0]
        y = math.sin(angle) * d + rotation_center[1]
        self.moveto((x, y))


class Space:
    def __init__(self, width: int, height: int) -> None:
        self.__movie_writer = None
        self.__width = width
        self.__height = height
        self.__canvas = tki.Canvas(width=width, height=height, bg='white')
        self.__canvas.pack(expand=tki.YES, fill=tki.BOTH)
        self.__circles: List[Circle] = []

    def get_canvas(self):
        return self.__canvas

    def space2canvas(self, point):
        x = self.__width / 2.0 + point[0]
        y = self.__height / 2.0 - point[1]
        return (x, y)

    def canvas2space(self, point):
        x = point[0] - self.__width / 2.0
        y = self.__height / 2.0 - point[1]
        return (x, y)

    def add_circle(self, radius, draw_line=False):
        if not self.__circles:
            circle = Circle(self, (0.0, 0.0), radius)
        else:
            prev_circle = self.__circles[-1]
            center = prev_circle.get_center()
            center = (center[0], center[1] + prev_circle.get_radius() + radius)
            circle = Circle(self, center, radius)

        circle.set_draw(draw_line)
        self.__circles.append(circle)

    def rotate_circle(self, index, nsteps):
        rotation_center = self.__circles[index - 1].get_center()
        clockwise = nsteps > 0

        for i in range(index, len(self.__circles)):
            circle = self.__circles[i]

            for n in range(0, abs(nsteps)):
                circle.rotate(rotation_center, clockwise)

    def redraw(self):
        self.__canvas.update()

    def save_image(self, file_name):
        self.__canvas.postscript(file=file_name + '.ps')

    def add_movie_frame(self, file_name):
        if not self.__movie_writer:
            self.__movie_writer = imageio.get_writer(file_name + '.gif', mode='I')

        # self.save_image(file_name)
        ps = self.__canvas.postscript()
        # image = imageio.imread(file_name + '.ps')
        byte_stream = io.BytesIO(ps.encode('utf-8'))
        image = imageio.imread(byte_stream)
        self.__movie_writer.append_data(image)


def main() -> int:
    space = Space(1000, 1000)
    space.add_circle(150)
    space.add_circle(100)
    space.add_circle(50)
    space.add_circle(11)
    space.add_circle(1, draw_line=True)

    redraw = 0.0
    for r in range(0, int(math.pi * 2 / STEP_SIZE)):
        space.rotate_circle(1, 1)
        space.rotate_circle(2, -7)
        space.rotate_circle(3, 13)
        space.rotate_circle(4, -41)
        redraw += STEP_SIZE

        if redraw > REDRAW_STEP:
            space.redraw()
            # space.add_movie_frame('aap')
            redraw = 0

    # space.save_image('foo')

    tki.mainloop()
    return 0
