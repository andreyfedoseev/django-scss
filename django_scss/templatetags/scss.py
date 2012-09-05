from ..cache import get_cache_key, get_hexdigest, get_hashed_mtime
from ..settings import SCSS_EXECUTABLE, SCSS_USE_CACHE,\
    SCSS_CACHE_TIMEOUT, SCSS_OUTPUT_DIR, SCSS_DEVMODE, SCSS_DEVMODE_WATCH_DIRS
from ..utils import compile_scss
from django.conf import settings
from django.core.cache import cache
from django.template.base import Library, Node
import shlex
import subprocess
import os
import sys


register = Library()


class InlineSCSSNode(Node):

    def __init__(self, nodelist):
        self.nodelist = nodelist

    def compile(self, source):


        args = shlex.split("%s -s --scss -C" % SCSS_EXECUTABLE)

        p = subprocess.Popen(args, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, errors = p.communicate(source)
        if out:
            return out.decode("utf-8")
        elif errors:
            return errors.decode("utf-8")

        return u""

    def render(self, context):
        output = self.nodelist.render(context)

        if SCSS_USE_CACHE:
            cache_key = get_cache_key(get_hexdigest(output))
            cached = cache.get(cache_key, None)
            if cached is not None:
                return cached
            output = self.compile(output)
            cache.set(cache_key, output, SCSS_CACHE_TIMEOUT)
            return output
        else:
            return self.compile(output)


@register.tag(name="inlinescss")
def do_inlinescss(parser, token):
    nodelist = parser.parse(("endinlinescss",))
    parser.delete_first_token()
    return InlineSCSSNode(nodelist)


@register.simple_tag
def scss(path):

    try:
        STATIC_ROOT = settings.STATIC_ROOT
    except AttributeError:
        STATIC_ROOT = settings.MEDIA_ROOT

    encoded_full_path = full_path = os.path.join(STATIC_ROOT, path)
    if isinstance(full_path, unicode):
        filesystem_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
        encoded_full_path = full_path.encode(filesystem_encoding)

    filename = os.path.split(path)[-1]

    output_directory = os.path.join(STATIC_ROOT, SCSS_OUTPUT_DIR, os.path.dirname(path))

    hashed_mtime = get_hashed_mtime(full_path)

    if filename.endswith(".scss"):
        base_filename = filename[:-5]
    else:
        base_filename = filename

    if SCSS_DEVMODE and any(map(lambda watched_dir: full_path.startswith(watched_dir), SCSS_DEVMODE_WATCH_DIRS)):
        output_path = os.path.join(output_directory, "%s.css" % base_filename)

    else:
        output_path = os.path.join(output_directory, "%s-%s.css" % (base_filename, hashed_mtime))
        if not os.path.exists(output_path):
            if not compile_scss(encoded_full_path, output_path, path):
                return path

            # Remove old files
            compiled_filename = os.path.split(output_path)[-1]
            for filename in os.listdir(output_directory):
                if filename.startswith(base_filename) and filename != compiled_filename:
                    os.remove(os.path.join(output_directory, filename))

    return output_path[len(STATIC_ROOT):].replace(os.sep, "/").lstrip("/")
