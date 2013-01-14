from ..cache import get_cache_key, get_hexdigest, get_hashed_mtime
from ..settings import SCSS_EXECUTABLE, SCSS_USE_CACHE,\
    SCSS_CACHE_TIMEOUT, SCSS_ROOT, SCSS_OUTPUT_DIR, SCSS_DEVMODE,\
    SCSS_DEVMODE_WATCH_DIRS
from ..utils import compile_scss, STATIC_ROOT
from django.conf import settings
from django.core.cache import cache
from django.contrib.staticfiles import finders
from django.template.base import Library, Node, TemplateSyntaxError
import logging
import shlex
import subprocess
import os
import sys


logger = logging.getLogger("django_scss")


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
            return out.decode(settings.FILE_CHARSET)
        elif errors:
            return errors.decode(settings.FILE_CHARSET)

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


def scss_paths(path):

    full_path = os.path.join(STATIC_ROOT, path)

    if settings.DEBUG and not os.path.exists(full_path):
        # while developing it is more confortable
        # searching for the scss files rather then
        # doing collectstatics all the time
        full_path = finders.find(path)

        if full_path is None:
            raise TemplateSyntaxError("Can't find staticfile named: {}".format(path))

    file_name = os.path.split(path)[-1]
    output_dir = os.path.join(SCSS_ROOT, SCSS_OUTPUT_DIR, os.path.dirname(path))

    return full_path, file_name, output_dir


@register.simple_tag
def scss(path):

    logger.info("processing file %s" % path)

    full_path, file_name, output_dir = scss_paths(path)
    base_file_name = os.path.splitext(file_name)[0]

    if SCSS_DEVMODE and any(map(lambda watched_dir: full_path.startswith(watched_dir), SCSS_DEVMODE_WATCH_DIRS)):
        return os.path.join(os.path.dirname(path), "%s.css" % base_file_name)

    hashed_mtime = get_hashed_mtime(full_path)
    output_file = "%s-%s.css" % (base_file_name, hashed_mtime)
    output_path = os.path.join(output_dir, output_file)

    encoded_full_path = full_path
    if isinstance(full_path, unicode):
        filesystem_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
        encoded_full_path = full_path.encode(filesystem_encoding)

    if not os.path.exists(output_path):
        if not compile_scss(encoded_full_path, output_path, path):
            return path

        # Remove old files
        compiled_filename = os.path.split(output_path)[-1]
        for filename in os.listdir(output_dir):
            if filename.startswith(base_file_name) and filename != compiled_filename:
                os.remove(os.path.join(output_dir, filename))

    return os.path.join(SCSS_OUTPUT_DIR, os.path.dirname(path), output_file)
