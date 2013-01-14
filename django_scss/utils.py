from django_scss.settings import SCSS_EXECUTABLE, SCSS_USE_COMPASS, SCSS_ROOT,\
    SCSS_OUTPUT_DIR
from django.conf import settings
import logging
import os
import posixpath
import re
import subprocess


logger = logging.getLogger("django_scss")


STATIC_ROOT = getattr(settings, "STATIC_ROOT", getattr(settings, "MEDIA_ROOT"))
STATIC_URL = getattr(settings, "STATIC_URL", getattr(settings, "MEDIA_URL"))


class URLConverter(object):

    URL_PATTERN = re.compile(r'url\(([^\)]+)\)')

    def __init__(self, content, source_path):
        self.content = content
        self.source_dir = os.path.dirname(source_path)

    def convert_url(self, matchobj):
        url = matchobj.group(1)
        url = url.strip(' \'"')
        if url.startswith(('http://', 'https://', '/', 'data:')):
            return "url('%s')" % url
        full_url = posixpath.normpath("/".join([self.source_dir, url]))
        return "url('%s')" % full_url

    def convert(self):
        return self.URL_PATTERN.sub(self.convert_url, self.content)


def compile_scss(input, output, scss_path):

    scss_root = os.path.join(SCSS_ROOT, SCSS_OUTPUT_DIR)
    if not os.path.exists(scss_root):
        os.makedirs(scss_root)

    args = [SCSS_EXECUTABLE, "-C", input]
    if SCSS_USE_COMPASS:
        args.insert(1, "--compass")

    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=STATIC_ROOT)
    out, errors = p.communicate()

    if errors:
        logger.error(errors)
        return False

    output_directory = os.path.dirname(output)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    compiled_css = URLConverter(
        out.decode(settings.FILE_CHARSET),
        os.path.join(STATIC_URL, scss_path)
    ).convert()
    compiled_file = open(output, "w+")
    compiled_file.write(compiled_css.encode(settings.FILE_CHARSET))
    compiled_file.close()

    return True

