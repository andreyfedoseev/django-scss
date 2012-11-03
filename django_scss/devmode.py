from django_scss.utils import compile_scss, logger
from django_scss.settings import SCSS_DEVMODE_WATCH_DIRS, SCSS_OUTPUT_DIR, SCSS_DEVMODE_EXCLUDE
from .utils import STATIC_ROOT
import os
import re
import sys
import time
import threading


WATCHED_FILES = {}
SCSS_IMPORT_RE = re.compile(r"""@import\s+['"](.+?\.scss)['"]\s*;""")


def daemon():

    while True:
        to_be_compiled = set()
        for watched_dir in SCSS_DEVMODE_WATCH_DIRS:
            for root, dirs, files in os.walk(watched_dir):
                for filename in filter(lambda f: f.endswith(".scss"), files):
                    filename = os.path.join(root, filename)
                    f = os.path.relpath(filename, STATIC_ROOT)
                    if f in SCSS_DEVMODE_EXCLUDE:
                        continue
                    mtime = os.path.getmtime(filename)

                    if f not in WATCHED_FILES:
                        WATCHED_FILES[f] = [None, set()]

                    if WATCHED_FILES[f][0] != mtime:
                        WATCHED_FILES[f][0] = mtime
                        # Look for @import statements to update dependecies
                        for line in open(filename):
                            for imported in SCSS_IMPORT_RE.findall(line):
                                imported = os.path.relpath(os.path.join(os.path.dirname(filename), imported), STATIC_ROOT)
                                if imported not in WATCHED_FILES:
                                    WATCHED_FILES[imported] = [None, set([f])]
                                else:
                                    WATCHED_FILES[imported][1].add(f)

                        to_be_compiled.add(f)
                        for importer in WATCHED_FILES[f][1]:
                            to_be_compiled.add(importer)

        for scss_path in to_be_compiled:
            full_path = os.path.join(STATIC_ROOT, scss_path)
            base_filename = os.path.split(scss_path)[-1][:-5]
            output_directory = os.path.join(STATIC_ROOT, SCSS_OUTPUT_DIR, os.path.dirname(scss_path))
            output_path = os.path.join(output_directory, "%s.css" % base_filename)
            if isinstance(full_path, unicode):
                filesystem_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
                full_path = full_path.encode(filesystem_encoding)

            compile_scss(full_path, output_path, scss_path)
            logger.debug("Compiled: %s" % scss_path)


        time.sleep(1)


def start_daemon():
    thread = threading.Thread(target=daemon)
    thread.daemon = True
    thread.start()

