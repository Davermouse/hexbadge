import time
import math

import app
import settings

from tildagonos import tildagonos

from app_components import TextDialog, clear_background
from events.input import BUTTON_TYPES, Buttons
from perf_timer import PerfTimer

class DMHexBadgeApp(app.App):
    name = None

    hex_count = 6

    d_d_d_rot = -0.001
    d_d_rot = 1
    d_rots = []
    rots = [0, 0.2, 0.4, 0.6, 0.8, 1]

    colors = [(1, 1, 1), (0, 1, 0), (1, 1, 0), (0, 0, 1), (1, 0, 0), (0, 1, 1)]
    dims = []

    hex_size = 120

    bg_color = (0, 0, 0)
    fg_color = (255, 255, 255)

    def __init__(self):
        super().__init__()
        self.button_states = Buttons(self)
        self.name = settings.get("name")
        #self.name = "Test name"

        self.d_rots = list(map(lambda i: (i + 1) * 0.01, range(0, self.hex_size)))
        self.dims = list(map(lambda i: self.hex_size - i * 5, range(0, self.hex_size)))

    async def run(self, render_update):
        last_time = time.ticks_ms()
        while True:
            cur_time = time.ticks_ms()
            delta_ticks = time.ticks_diff(cur_time, last_time)
            with PerfTimer(f"Updating {self}"):
                self.update(delta_ticks)
            await render_update()
            last_time = cur_time

            if self.name is None:
                dialog = TextDialog("What is your name?", self)
                self.overlays = [dialog]

                if await dialog.run(render_update):
                    self.name = dialog.text
                    settings.set("name", dialog.text)

                    try:
                        settings.save()
                    except Exception as ex:
                        print("failed to save settings", ex)
                else:
                    self.minimise()

                self.overlays = []

    def update(self, delta):
        self.d_d_rot += self.d_d_d_rot
        if (abs(self.d_d_rot) > 1):
            self.d_d_d_rot *= -1

        self.rots = list(map(lambda r, d_r: r + (self.d_d_rot * d_r), self.rots, self.d_rots))
        
        # TODO: Make LEDS rotate with the hexes
       # tildagonos.leds[0] = (1, 0, 0)

        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            # quit the app
            self.minimise()
            self.button_states.clear()

    def draw_hex(self, ctx, dim, rot, color):
        sides = 6

        points = []

        for s in range(0, sides):
            t = rot + (math.pi * 2) * (s / sides)
            x = dim * math.sin(t)
            y = dim * math.cos(t)

            points.append((x, y))

        startX, startY = points[0]

        ctx.rgb(*color)
        ctx.move_to(startX, startY).begin_path()

        for p in points:
            x, y = p
            ctx.line_to(x, y)

        ctx.line_to(startX, startY)

        ctx.stroke()

    def draw(self, ctx):
        clear_background(ctx)

        for (dim, rot, color) in zip(self.dims, self.rots, self.colors):
            self.draw_hex(ctx, dim, rot, color)

        # This seems to crash with 'TypeError: can't convert str to int' on the badge
        # ctx.text_align = "center"

        ctx.font_size = 36
        ctx.font = "Arimo Bold"
        if self.name is not None:
            w = ctx.text_width(self.name)
            h = 22
            ctx.rgb(*self.fg_color).move_to(-w/2, h / 2).text(self.name)
        
        if self.name is None:
            ctx.font_size = 22
            ctx.font = "Arimo Italic"
            ctx.rgb(*self.fg_color).move_to(-80, -20).text(
                "Set your name in\nthe settings app!"
            )

        self.draw_overlays(ctx)

__app_export__ = DMHexBadgeApp
