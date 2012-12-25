# coding: utf-8
from unittest import main, TestCase
from django.http import HttpRequest
from django.template.base import Template
from django.template.context import RequestContext
import os
import re
import time
import shutil


os.environ["DJANGO_SETTINGS_MODULE"] = "django_scss.tests.django_settings"


class SCSSTestCase(TestCase):

    def setUp(self):
        from django.conf import settings as django_settings
        self.django_settings = django_settings

        output_dir = os.path.join(self.django_settings.STATIC_ROOT,
                                  self.django_settings.SCSS_OUTPUT_DIR)

        # Remove the output directory if it exists to start from scratch
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

    def _get_request_context(self):
        return RequestContext(HttpRequest())

    def test_inline_scss(self):
        template = Template("""
        {% load scss %}
        {% inlinescss %}
            $the-border: 1px;
            #bordered {
                border: $the-border * 2;
            }
        {% endinlinescss %}
        """)
        rendered = """#bordered {
  border: 2px; }"""
        self.assertEqual(template.render(self._get_request_context()).strip(), rendered)

    def test_external_scss(self):

        template = Template("""
        {% load scss %}
        {% scss "styles/test.scss" %}
        """)
        compiled_filename_re = re.compile(r"SCSS_CACHE/styles/test-[a-f0-9]{12}.css")
        compiled_filename = template.render(self._get_request_context()).strip()
        self.assertTrue(bool(compiled_filename_re.match(compiled_filename)))

        compiled_path = os.path.join(self.django_settings.STATIC_ROOT, compiled_filename)
        compiled_content = open(compiled_path).read().strip()
        compiled = """#header h1 {
  background-image: url('/static/images/header.png'); }"""
        self.assertEquals(compiled_content, compiled)

        # Change the modification time
        source_path = os.path.join(self.django_settings.STATIC_ROOT, "styles/test.scss")
        os.utime(source_path, None)

        # The modification time is cached so the compiled file is not updated
        compiled_filename_2 = template.render(self._get_request_context()).strip()
        self.assertTrue(bool(compiled_filename_re.match(compiled_filename_2)))
        self.assertEquals(compiled_filename, compiled_filename_2)

        # Wait to invalidate the cached modification time
        time.sleep(self.django_settings.SCSS_MTIME_DELAY)

        # Now the file is re-compiled
        compiled_filename_3 = template.render(self._get_request_context()).strip()
        self.assertTrue(bool(compiled_filename_re.match(compiled_filename_3)))
        self.assertNotEquals(compiled_filename, compiled_filename_3)

        # Check that we have only one compiled file, old files should be removed

        compiled_file_dir = os.path.dirname(os.path.join(self.django_settings.STATIC_ROOT,
                                                         compiled_filename_3))
        self.assertEquals(len(os.listdir(compiled_file_dir)), 1)

    def test_lookup_in_staticfiles_dirs(self):

        template = Template("""
        {% load scss %}
        {% scss "another_test.scss" %}
        """)
        compiled_filename_re = re.compile(r"SCSS_CACHE/another_test-[a-f0-9]{12}.css")
        compiled_filename = template.render(self._get_request_context()).strip()
        self.assertTrue(bool(compiled_filename_re.match(compiled_filename)))

        compiled_path = os.path.join(self.django_settings.STATIC_ROOT, compiled_filename)
        compiled_content = open(compiled_path).read().strip()
        compiled = """#header-from-staticfiles-dir h1 {
  color: red; }"""
        self.assertEquals(compiled_content, compiled)

        template = Template("""
        {% load scss %}
        {% scss "prefix/another_test.scss" %}
        """)
        compiled_filename_re = re.compile(r"SCSS_CACHE/prefix/another_test-[a-f0-9]{12}.css")
        compiled_filename = template.render(self._get_request_context()).strip()
        self.assertTrue(bool(compiled_filename_re.match(compiled_filename)))

        compiled_path = os.path.join(self.django_settings.STATIC_ROOT, compiled_filename)
        compiled_content = open(compiled_path).read().strip()
        compiled = """#header-from-staticfiles-dir-with-prefix h1 {
  color: red; }"""
        self.assertEquals(compiled_content, compiled)

    def test_non_ascii_content(self):

        template = Template("""
        {% load scss %}
        {% scss "styles/non-ascii.scss" %}
        """)
        compiled_filename = template.render(self._get_request_context()).strip()
        compiled_path = os.path.join(self.django_settings.STATIC_ROOT, compiled_filename)
        compiled_content = open(compiled_path).read().strip()
        compiled = """.external_link:first-child:before {
  content: "Zobacz także:";
  background: url('/static/styles/картинка.png'); }"""
        self.assertEquals(compiled_content, compiled)


if __name__ == '__main__':
    main()
