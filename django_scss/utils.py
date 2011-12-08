from django_scss.settings import SCSS_EXECUTABLE
from django.conf import settings
import logging
import os
import posixpath
import re
import shlex
import subprocess


logger = logging.getLogger("django_scss")


URL_PATTERN = re.compile(r'url\(([^\)]+)\)')


class URLConverter(object):

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
        return URL_PATTERN.sub(self.convert_url, self.content)


def compile_scss(input, output, scss_path):
    command = "%s -C %s" % (SCSS_EXECUTABLE, input)
    args = shlex.split(command)
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, errors = p.communicate()

    if errors:
        logger.error(errors)
        return False

    try:
        STATIC_URL = settings.STATIC_URL
    except AttributeError:
        STATIC_URL = settings.MEDIA_URL

    output_directory = os.path.dirname(output)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    compiled_file = open(output, "w+")
    compiled_file.write(URLConverter(out, os.path.join(STATIC_URL, scss_path)).convert())
    compiled_file.close()

    return True

