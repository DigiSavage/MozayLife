"""
jigsaw.py

PURPOSE:
    Provides the Jigsaw class, which generates puzzle-piece masks for use in creating jigsaw-style photomosaics.

HOW IT COMMUNICATES:
    - Called by photomosaic.py when generating mosaics with 'puzzle' shapes.
    - Pure algorithmic code; no direct I/O or database access.

PATHS TO CHECK:
    - No file or database paths to configure.
    - Requires that numpy and Pillow (PIL) are installed.

MODERNIZATION NOTES:
    - Uses Python 3: range, float division, updated print/exception style.
    - Platform independent; pure algorithm.
"""

import random
import math
import numpy as np
from PIL import Image, ImageDraw

class Jigsaw:
    """
    Generates jigsaw (puzzle piece) masks for use in photomosaic tiling.
    Each mask can be used to blend tile edges with the 'puzzle' effect.
    """

    tau = 2 * math.pi

    def __init__(self, size, dimensions):
        self.size = size  # (width, height)
        if isinstance(dimensions, int):
            self.dimensions = (dimensions, dimensions)
        else:
            self.dimensions = dimensions
        self._jigsaw = self._create_jigsaw()

    def __getattr__(self, key):
        if key == '_jigsaw':
            raise AttributeError()
        return getattr(self._jigsaw, key)

    def _create_jigsaw(self):
        """
        Draw the jigsaw grid as a reference (RGB, red lines) for puzzle mask generation.
        This is mostly for preview—actual piece masks are made with get_piece().
        """
        cols, rows = self.dimensions
        w, h = self.size
        im = Image.new('RGB', (w, h), (0, 0, 0))
        draw = ImageDraw.Draw(im)
        draw.polygon([(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)], outline='red')

        # Horizontal lines
        for r in range(rows - 1):
            for c in range(cols):
                start = np.array([c * w / cols, (r + 1) * h / rows], dtype=float)
                end = np.array([(c + 1) * w / cols, (r + 1) * h / rows], dtype=float)
                p = self._make_knob(start, end)
                draw.line(p, fill=(255, 0, 0))

        # Vertical lines
        for r in range(rows):
            for c in range(cols - 1):
                start = np.array([(c + 1) * w / cols, r * h / rows], dtype=float)
                end = np.array([(c + 1) * w / cols, (r + 1) * h / rows], dtype=float)
                p = self._make_knob(start, end)
                draw.line(p, fill=(255, 0, 0))

        return im

    @property
    def jigsaw(self):
        return self._jigsaw

    def get_piece(self, box):
        """
        Extract a puzzle piece mask from the full grid.
        Args:
            box (tuple): (left, upper, right, lower) bounds for cropping
        Returns:
            PIL.Image (mode 'L'): Black/white mask for compositing
        """
        piece = self.jigsaw.crop(box)
        # Flood fill center to white (255,255,255), for mask
        mid = (piece.size[0] // 2, piece.size[1] // 2)
        ImageDraw.floodfill(piece, mid, (255, 255, 255))
        w, h = piece.size
        pix = piece.load()

        # Convert all red lines to black (0,0,0)
        for x in range(w):
            for y in range(h):
                if pix[x, y] == (255, 0, 0):
                    piece.putpixel((x, y), (0, 0, 0))
        # Convert to grayscale (L mode) for use as mask
        return piece.convert('L')

    def _make_knob(self, start, end):
        """
        Create the 'knob' (bump) on a puzzle edge.
        Args:
            start, end (np.array): endpoints of the puzzle edge
        Returns:
            list: list of x,y points forming the wavy edge for ImageDraw.line()
        """
        line_length = np.linalg.norm(end - start)
        mid = start + (end - start) * (0.4 + random.random() * 0.2)
        v = (end - start) / np.linalg.norm(end - start)
        direction = random.choice([-1, 1])
        vv = np.array([-v[1], v[0]])  # rotate 90 deg
        n = vv * direction

        knob_start = mid - v * line_length * 0.1
        knob_end = mid + v * line_length * 0.1

        small_radius = line_length * (0.05 + random.random() * 0.01)
        large_radius = small_radius * 1.8

        tri_base = np.linalg.norm(knob_end - knob_start) / 2.0
        tri_hyp = small_radius + large_radius
        tri_height = math.sqrt(tri_hyp**2 - tri_base**2)
        large_center_distance = small_radius + tri_height

        small_start_angle = -Jigsaw.tau / 4.0
        small_end_angle = math.asin(tri_height / tri_hyp)
        large_slice_angle = math.asin(tri_base / tri_hyp)
        large_start_angle = Jigsaw.tau * 3.0 / 4.0 - large_slice_angle
        large_end_angle = -Jigsaw.tau / 4.0 + large_slice_angle

        # Build up the polyline
        p = []
        p.append(start.tolist())
        p.append(knob_start.tolist())
        self._append_circle(p, v, n, knob_start + n * small_radius,
                            small_radius, small_start_angle, small_end_angle)
        self._append_circle(p, v, n, mid + n * large_center_distance,
                            large_radius, large_start_angle, large_end_angle)
        self._append_circle(p, -v, n, knob_end + n * small_radius,
                            small_radius, small_end_angle, small_start_angle)
        p.append(knob_end.tolist())
        p.append(end.tolist())
        # Flatten to list of [x1, y1, x2, y2, ...] for ImageDraw.line
        return [coord for point in p for coord in point]

    @staticmethod
    def _append_circle(p, v, n, center, radius, start_angle, end_angle):
        """
        Append points on a circular arc to p.
        """
        angle_span = end_angle - start_angle
        segment_count = int(math.ceil(20 * abs(angle_span) / Jigsaw.tau))
        for i in range(segment_count + 1):
            th = start_angle + angle_span * i / segment_count
            point = center + v * math.cos(th) * radius + n * math.sin(th) * radius
            p.append(point.tolist())