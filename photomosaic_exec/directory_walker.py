"""
directory_walker.py

PURPOSE:
    Implements the DirectoryWalker class for recursively iterating through all files in a directory tree.
    Used to collect image files for building the mosaic image pool.

HOW IT COMMUNICATES:
    - Used by photomosaic.py and related modules to scan folders and collect file paths.
    - Does not interact directly with databases or external services.

PATHS TO CHECK:
    - Ensure the input directory passed to DirectoryWalker exists and is accessible on your deployment/server.
    - All paths are local filesystem paths.

MODERNIZATION NOTES:
    - Fully Python 3. Uses os.walk() for safe, efficient directory traversal.
    - Returns a generator for efficient iteration over large file trees.
    - Compatible with most OS platforms.
    - Handles symlinks gracefully (does not follow).
"""

import os

class DirectoryWalker:
    """
    Yields absolute paths to all files (recursively) in a given directory tree.

    Example usage:
        for filepath in DirectoryWalker("/path/to/images"):
            print(filepath)
    """
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def __iter__(self):
        for dirpath, dirnames, filenames in os.walk(self.root_dir, followlinks=False):
            for filename in filenames:
                yield os.path.join(dirpath, filename)