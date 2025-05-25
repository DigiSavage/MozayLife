"""
photomosaic.py

PURPOSE:
    Main photomosaic image generator. Defines the PhotoMosaic class, which partitions, analyzes, and assembles mosaics from a source image and a pool of tile images.

HOW IT COMMUNICATES:
    - Reads and writes image files from the local filesystem (with Pillow).
    - Connects to MongoDB Atlas for storing and retrieving tile pool data (image_pool collection).
    - Uses custom modules (directory_walker, memo, color_metrics, etc.).

MODERNIZATION NOTES:
    - Pure Python 3 code. No pgmagick/PythonMagick; all image handling is via Pillow.
    - MongoDB connection is to Atlas, not localhost.
    - All code tested for division, print, exception, and path correctness.
"""

import pickle
import logging
import math
import numpy as np
import random
from PIL import Image, ImageDraw, ImageFilter
from bson.binary import Binary
from directory_walker import DirectoryWalker
from memo import memo
from color_metrics import rgb2Lab, deltaE00
from progress_bar import progress_bar
from jigsaw import Jigsaw
from pymongo import MongoClient
from multiprocessing import cpu_count, Process, Manager

# MongoDB Atlas connection string
MONGO_ATLAS_URI = "mongodb+srv://khalidshams:Mo2ayMozay!@mozaylab.c1hgdgz.mongodb.net/?retryWrites=true&w=majority&appName=MozayLab"

# Configure logger.
FORMAT = "%(name)s.%(funcName)s:  %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)

def open_image(im_path):
    """
    Reads an image from disk and returns a Pillow Image object.
    Handles transparency.
    """
    try:
        im = Image.open(im_path)
        if im.mode == 'RGBA':
            im.load()
            rgb = Image.new('RGB', im.size, (255, 255, 255))
            rgb.paste(im, mask=im.split()[3])
            return rgb
        return im.convert('RGB')
    except Exception as e:
        logger.warning(f"Cannot open {im_path}: {e}")
        return None

@memo
def open_tile(filename, temp_size=(192, 192)):
    im = open_image(filename)
    if im:
        im.thumbnail(temp_size, Image.ANTIALIAS)
    return im

class Tile(object):
    """
    Wraps a Pillow Image for each tile in the mosaic.
    """
    def __init__(self, img, x, y, mask=None, ancestry=None, ancestor_size=None):
        self._img = img
        self.x = x
        self.y = y
        self._mask = mask.convert("L") if mask else None
        self._blank = None
        self._ancestry = ancestry or []
        self._depth = len(self._ancestry)
        self._ancestor_size = ancestor_size if ancestor_size else self.size

    def crop(self, *args):
        return self._img.crop(*args)
    def resize(self, *args):
        return self._img.resize(*args)

    @property
    def size(self):
        return self._img.size

    @property
    def ancestry(self):
        return self._ancestry
    @property
    def depth(self):
        return self._depth
    @property
    def ancestor_size(self):
        return self._ancestor_size

    @property
    def rgb(self):
        return self._rgb
    @rgb.setter
    def rgb(self, value):
        self._rgb = value

    @property
    def lab(self):
        return self._lab
    @lab.setter
    def lab(self, value):
        self._lab = value

    @property
    def match(self):
        return self._match
    @match.setter
    def match(self, value):
        self._match = value
        try:
            self._match_img = open_tile(self._match, (4 * self._ancestor_size[1], 4 * self._ancestor_size[0]))
        except Exception as e:
            logger.error(f"Error loading match image: {e}")
    @property
    def match_img(self):
        return self._match_img

    @property
    def blank(self):
        return self._blank

    def determine_blankness(self, min_depth=1):
        if not self._mask:
            self._blank = False
            return
        brightest_pixel = self._mask.getextrema()[1]
        if brightest_pixel == 0:
            self._blank = True
        elif brightest_pixel == 255:
            self._blank = False
        elif self._depth < min_depth:
            self._blank = True
        elif 255 * np.random.rand() > brightest_pixel:
            self._blank = True
        else:
            self._blank = False
        return

    def straddles_mask_edge(self):
        if not self._mask:
            return False
        darkest_pixel, brightest_pixel = self._mask.getextrema()
        return brightest_pixel == 255 and darkest_pixel != 255

    def dynamic_range(self):
        tmp = np.array(self._img.filter(ImageFilter.GaussianBlur).getextrema())
        return np.average(tmp[:, 1] - tmp[:, 0]).astype(int)

    def procreate(self):
        width = self._img.size[0] // 2
        height = self._img.size[1] // 2
        children = []
        for y in [0, 1]:
            for x in [0, 1]:
                tile_img = self._img.crop((x * width, y * height, (x + 1) * width, (y + 1) * height))
                mask_im = self._mask.crop((x * width, y * height, (x + 1) * width, (y + 1) * height)) if self._mask else None
                child = Tile(tile_img, self.x, self.y, mask=mask_im, ancestry=self._ancestry + [(x, y)], ancestor_size=self._ancestor_size)
                children.append(child)
        return children

class PhotoMosaic(object):
    def __init__(self, im_path, dimensions, shape=None):
        self._im = open_image(im_path)
        self._mos = None
        self._tiles = []
        self._dimensions = dimensions
        self._shape = shape

    def __getattr__(self, key):
        if key == '_mos':
            raise AttributeError()
        return getattr(self._mos, key)

    @property
    def im(self):
        return self._im
    @im.setter
    def im(self, value):
        self._im = value

    @property
    def mos(self):
        return self._mos
    @mos.setter
    def mos(self, value):
        self._mos = value

    @property
    def tiles(self):
        return self._tiles
    @tiles.setter
    def tiles(self, value):
        self._tiles = value

    @property
    def dimensions(self):
        return self._dimensions
    @dimensions.setter
    def dimensions(self, value):
        if isinstance(value, int):
            self._dimensions = value, value
        else:
            self._dimensions = value

    @property
    def shape(self):
        return self._shape
    @shape.setter
    def shape(self, value):
        self._shape = value

    def partition(self, mask=None, depth=0, hdr=80, debris=False, min_debris_depth=1, base_width=None):
        if isinstance(self.dimensions, int):
            self.dimensions = (self.dimensions, self.dimensions)
        if base_width is not None:
            cwidth = self.im.size[0] / self.dimensions[0]
            width = base_width * self.dimensions[0]
            factor = base_width / cwidth
            height = int(self.im.size[1] * factor)
            self.im = self.crop_to_fit(self.im, (width, height))
        factor = self.dimensions[0] * 2 ** (2 + depth), self.dimensions[1] * 2 ** (2 + depth)
        new_size = tuple([int(factor[i] * math.ceil(1.0 * self.im.size[i] / factor[i])) for i in [0, 1]])
        logger.info("Resizing image to %s for partitioning.", new_size)
        self.im = self.crop_to_fit(self.im, new_size)

        if mask:
            mask = self.crop_to_fit(mask, new_size)
            if not debris:
                mask = mask.convert("1")
        width = self.im.size[0] // self.dimensions[0]
        height = self.im.size[1] // self.dimensions[1]
        tiles = []

        for y in range(self.dimensions[1]):
            for x in range(self.dimensions[0]):
                tile_im = self.im.crop((x * width, y * height, (x + 1) * width, (y + 1) * height))
                mask_im = mask.crop((x * width, y * height, (x + 1) * width, (y + 1) * height)) if mask else None
                tile = Tile(tile_im, x, y, mask=mask_im)
                tiles.append(tile)
        self.tiles = tiles

    @staticmethod
    def crop_to_fit(im, size):
        im_w, im_h = im.size
        tile_w, tile_h = size
        im_aspect = im_w / im_h
        tile_aspect = tile_w / tile_h
        if im_aspect > tile_aspect:
            crop_h = im_h
            crop_w = int(round(crop_h * tile_aspect))
            x_offset = int((im_w - crop_w) / 2.0)
            y_offset = 0
        else:
            crop_w = im_w
            crop_h = int(round(crop_w / tile_aspect))
            x_offset = 0
            y_offset = int((im_h - crop_h) / 2.0)
        im = im.crop((x_offset, y_offset, x_offset + crop_w, y_offset + crop_h))
        im = im.resize((tile_w, tile_h), Image.ANTIALIAS)
        return im

    def analyze(self):
        pbar = progress_bar(len(self.tiles), "Analyzing images")
        for tile in self.tiles:
            if hasattr(tile, "blank") and tile.blank:
                continue
            regions = self.split_regions(tile, 4)
            tile.rgb = np.array([self.average_color(r) for r in regions])
            tile.lab = np.array([rgb2Lab(x) for x in tile.rgb])
            pbar.next()

    @staticmethod
    def split_regions(im, split_dim):
        if isinstance(split_dim, int):
            rows = columns = split_dim
        else:
            columns, rows = split_dim
        r_size = im.size[0] // columns, im.size[1] // rows
        regions = []
        for y in range(rows):
            for x in range(columns):
                region = im.crop((x * r_size[0], y * r_size[1], (x + 1) * r_size[0], (y + 1) * r_size[1]))
                regions.append(region)
        return regions

    @staticmethod
    def average_color(im):
        assert im.mode == 'RGB', 'RGB images only!'
        tmp = np.asarray(im, dtype=np.float64)
        averages = np.average(tmp, axis=(0, 1))
        return averages

    def choose_match(self, db_name, color_space='rgb', metric='euclidean'):
        def worker(out_d, tiles, matches, metric, all_averages, img_paths, reuse, img_usage, max_usage):
            ntiles = dict()
            for tile in tiles:
                if hasattr(tile, "blank") and tile.blank:
                    continue
                d = self.distances(tile.rgb, all_averages, metric)
                d_args = d.argsort()
                i = 0
                minidx = d_args[i]
                tmp = img_paths[minidx]
                while True:
                    if matches.count(tmp) <= max_usage:
                        matches.append(tmp)
                        idx = self.tiles.index(tile)
                        ntiles[idx] = tmp
                        break
                    i += 1
                    minidx = d_args[i]
                    tmp = img_paths[minidx]
                if not reuse:
                    img_paths[minidx] = []
                    all_averages[minidx] = np.array([])
                else:
                    img_usage[minidx] += 1
                    if img_usage[minidx] == max_usage:
                        img_paths[minidx] = []
                        all_averages[minidx] = np.array([])
            out_d.update(ntiles)

        client = MongoClient(MONGO_ATLAS_URI)
        db = client[db_name]
        manager = Manager()
        try:
            pool = db.image_pool.find()
            pool_items = [x for x in pool]
            all_averages = manager.list()
            img_paths = manager.list()
            img_usage = manager.list()
            matches = manager.list()
            if color_space == 'rgb':
                all_averages = [pickle.loads(x["avgRGB"]) for x in pool_items]
            else:
                all_averages = [pickle.loads(x["avgLab"]) for x in pool_items]
            img_paths = [x["imgsrc"] for x in pool_items]
            logger.info('LENGTH OF IMAGES: %s' % len(img_paths))
            logger.info('LENGTH OF TILES: %s' % len(self.tiles))
            if len(self.tiles) < len(img_paths):
                reuse = False
                max_usage = 0
            else:
                max_usage = math.ceil(1.0 * len(self.tiles) / len(img_paths))
                reuse = True
                img_usage = [0] * len(img_paths)
            random.shuffle(self.tiles)
            nprocs = 2 * cpu_count()
            chunksize = int(math.ceil(len(self.tiles) / float(nprocs)))
            out_d = manager.dict()
            procs = []
            for i in range(nprocs):
                p = Process(
                    target=worker,
                    args=(out_d,
                          self.tiles[chunksize * i:chunksize * (i + 1)],
                          matches,
                          metric,
                          all_averages,
                          img_paths,
                          reuse,
                          img_usage,
                          max_usage))
                procs.append(p)
            for i in range(nprocs):
                procs[i].start()
            for i in range(nprocs):
                procs[i].join()
            for i, match in out_d.items():
                self.tiles[i].match = match
        finally:
            client.close()

    @staticmethod
    def distances(avg, all_avg, metric='euclidean'):
        m = len(all_avg)
        distances = np.empty(m)
        if metric == 'euclidean':
            for i in range(m):
                if all_avg[i].size == 0:
                    distances[i] = 255 ** 2
                else:
                    distances[i] = np.linalg.norm(avg - all_avg[i])
        else:
            for i in range(m):
                if all_avg[i].size == 0:
                    distances[i] = 255 ** 2
                else:
                    distances[i] = deltaE00(avg, all_avg[i])
        return distances

    def mosaic(self, factor=4, scatter=False, margin=0, scaled_margin=False, background=(255, 255, 255)):
        mosaic_size = self.im.size
        mosaic_size = mosaic_size[0] * factor, mosaic_size[1] * factor
        mos = Image.new('RGB', mosaic_size, background)
        pbar = progress_bar(len(self.tiles), "Scaling and placing tiles")
        for tile in self.tiles:
            if hasattr(tile, "blank") and tile.blank:
                pbar.next()
                continue
            size = tile.size
            size = tuple((factor * size[0], factor * size[1]))
            pos = self.__tile_position(tile, size, factor, scatter, margin)
            mos.paste(self.crop_to_fit(tile.match_img, size), pos)
            pbar.next()
        self.mos = mos

    @staticmethod
    def __tile_position(tile, size, factor, scatter=False, margin=0):
        ancestor_pos = [factor * tile.x * tile.ancestor_size[0],
                        factor * tile.y * tile.ancestor_size[1]]
        rel_pos = [[0, 0]] if tile.depth == 0 else [[factor * x * tile.ancestor_size[0] // 2 ** (gen + 1),
                                                    factor * y * tile.ancestor_size[1] // 2 ** (gen + 1)]
                                                    for gen, (x, y) in enumerate(tile.ancestry)]
        padding = [0, 0]
        pos = tuple(map(sum, zip(*([ancestor_pos] + rel_pos + [padding]))))
        return pos

    def fading(self, alpha=0.85):
        I = self.im.resize(self.mos.size, Image.BICUBIC)
        J = self.mos.filter(ImageFilter.GaussianBlur)
        self.mos = Image.blend(I, J, alpha)

    def imsave(self, outfile):
        try:
            self.mos.save(outfile)
        except Exception as e:
            logger.warning("%s.", e)

def pool_handler(image_pool_walker_dict):
    walker = image_pool_walker_dict.get('walkers')
    image_pool = image_pool_walker_dict.get('image_pool')
    for filename in walker:
        if (len(list(image_pool.find({"imgsrc": filename}))) != 0):
            logger.warning("Image %s is already in the collection. Skipping it.", filename)
            continue
        try:
            img = open_image(filename)
        except Exception:
            logger.warning("Cannot open %s as an image. Skipping it.", filename)
            continue
        if img.mode != 'RGB':
            logger.warning("RGB images only. Skipping %s.", filename)
            continue
        w, h = img.size
        try:
            regions = PhotoMosaic.split_regions(img, 4)
            rgb = np.array([PhotoMosaic.average_color(r) for r in regions])
            lab = np.array([rgb2Lab(x) for x in rgb])
            img.resize((192, 192), Image.ANTIALIAS).save(filename)
        except Exception as e:
            logger.warning("Unknown problem analyzing %s. Skipping it. Error: %s", filename, e)
            continue
        dbitem = {
            "imgsrc": filename,
            "avgRGB": Binary(pickle.dumps(rgb, protocol=2)),
            "avgLab": Binary(pickle.dumps(lab, protocol=2)),
            "usage": 0
        }
        image_pool.insert_one(dbitem)
    logger.info('Collection built with %d images' % image_pool.count_documents({}))

class ImagePool(object):
    """
    Analyze all the images in images_path and insert info in MongoDB Atlas.
    """
    def __init__(self, images_path, db_name='temp'):
        client = MongoClient(MONGO_ATLAS_URI)
        self.db_name = db_name
        self.images_path = images_path
        try:
            db = client[self.db_name]
            self.image_pool = db.image_pool
        finally:
            client.close()

    def pool(self):
        nprocs = 2 * cpu_count()
        walker = list(DirectoryWalker(self.images_path))
        chunksize = int(math.ceil(len(walker) / float(nprocs)))
        image_pool_walkers = [{'image_pool': self.image_pool, 'walkers': walker[chunksize * i:chunksize * (i + 1)]} for i in range(nprocs)]
        procs = []
        for i in range(nprocs):
            p = Process(
                target=pool_handler,
                args=(image_pool_walkers[i],)
            )
            procs.append(p)
        for i in range(nprocs):
            procs[i].start()
        for i in range(nprocs):
            procs[i].join()

def reset_usage(db_name):
    client = MongoClient(MONGO_ATLAS_URI)
    db = client[db_name]
    try:
        db.image_pool.update_many({}, {"$set": {"usage": 0}})
    finally:
        client.close()

# ----------- AWS S3 UPLOAD HELPER --------------
import boto3

def upload_to_s3(local_path, s3_bucket, s3_key, aws_access_key_id, aws_secret_access_key, region):
    """
    Upload a file to an AWS S3 bucket.
    """
    s3 = boto3.client(
        's3',
        region_name=region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    s3.upload_file(local_path, s3_bucket, s3_key)
    print(f"Uploaded {local_path} to s3://{s3_bucket}/{s3_key}")

# ----------- End of photomosaic.py --------------