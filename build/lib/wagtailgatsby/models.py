import base64
import os
import tempfile
import urllib.parse

from django.conf import settings
from django.core.files.storage import default_storage as storage
from django.db import models
from django.utils import timezone

from wagtail.images.models import AbstractImage, AbstractRendition, Image

import requests
from grapple.models import GraphQLImage, GraphQLString
from PIL import Image as PILImage


def rgb2hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


class GatsbyImage(AbstractImage):
    traced_SVG_image = models.FileField(default=None, blank=True, null=True)
    traced_SVG_hash = models.CharField(max_length=40, blank=True, editable=False)

    class Meta(AbstractImage.Meta):
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            from grapple.models import GraphQLString

            self.graphql_fields = GraphQLString("traced_SVG")
        except:  # noqa
            pass

    def save(self, *args, **kwargs):
        super(GatsbyImage, self).save(*args, **kwargs)

        # Trace a SVG if file one doesn't exist or file hash changes
        if (
            self.traced_SVG_image.name is None
            or self.traced_SVG_hash != self.get_file_hash()
        ):
            self.trace_image()

    def trace_image(self):
        # Traced SVG Generation:
        from colorthief import ColorThief

        # Temporary image files
        original_file_extension = os.path.splitext(self.file.name)[1]
        original_file = tempfile.NamedTemporaryFile(suffix=original_file_extension).name
        raw_bmp = tempfile.NamedTemporaryFile(suffix=".bmp").name
        grey_bmp = tempfile.NamedTemporaryFile(suffix=".bmp").name
        temp_svg = tempfile.NamedTemporaryFile(suffix=".svg").name
        out_svg = tempfile.NamedTemporaryFile(suffix=".svg").name

        # Access file via local or from S3
        file_object = storage.open(self.file.name)
        img = open(original_file, "wb+")
        img.write(file_object.file.read())
        img.close()

        # Capture colors from original image to color generated SVG.
        color_thief = ColorThief(original_file)
        palette = color_thief.get_palette(color_count=2)
        background = rgb2hex(*palette[0])
        foreground = rgb2hex(*palette[1])

        # Convert uploaded image to greyscaled BMP image
        bitmap_img = PILImage.open(original_file)
        bitmap_img.thumbnail((1200, 800), PILImage.ANTIALIAS)
        bitmap_img.save(raw_bmp)
        os.system("mkbitmap -g {} -o {}".format(raw_bmp, grey_bmp))

        # Trace greyscale image as SVG
        os.system(
            "potrace --invert --color={} --fillcolor={} --opaque -O 0.5 -t 1500 --svg {} -o {}".format(
                foreground, background, grey_bmp, temp_svg
            )
        )

        # Remove trash from SVG to compress it
        os.system(
            "scour -i {} -o {} --enable-viewboxing --enable-id-stripping \
                --enable-comment-stripping --shorten-ids --indent=none".format(
                temp_svg, out_svg
            )
        )

        # Write final output to Django field
        svg = open(out_svg, "rb")

        svg_filename = (
            settings.BASE_DIR + os.path.splitext(self.file.url)[0] + "-traced.svg"
        )
        self.traced_SVG_hash = self.get_file_hash()
        self.traced_SVG_image.save(svg_filename, svg)

    @property
    def traced_SVG(self):
        svg_string = ""
        if self.traced_SVG_image.name is not None:
            try:
                svg_file = storage.open(self.traced_SVG_image.name)
                svg_file_data = svg_file.file.read()
                svg_string = "data:image/svg+xml," + urllib.parse.quote(svg_file_data)
            except:  # noqa
                pass

        return svg_string

    @property
    def base64(self):
        try:
            from io import BytesIO

            rendition = self.get_rendition("fill-20x20|jpegquality-60")
            image_buffer = BytesIO(rendition.file.read())
            image = PILImage.open(image_buffer)
            encoded_string = base64.b64encode(image_buffer.getvalue())

            return "data:image/%s;base64,%s" % (image.format, encoded_string)
        except:  # noqa
            return ""

    admin_form_fields = Image.admin_form_fields


class GatsbyImageRendition(AbstractRendition):
    image = models.ForeignKey(
        GatsbyImage, on_delete=models.CASCADE, related_name="renditions"
    )

    class Meta(AbstractRendition.Meta):
        abstract = True
        unique_together = ("image", "filter_spec", "focal_point_key")

    graphql_fields = (
        GraphQLString("id"),
        GraphQLString("file"),
        GraphQLString("url"),
        GraphQLString("width"),
        GraphQLString("height"),
        GraphQLImage("image"),
    )


class Deployment(models.Model):
    deployment_created = models.DateTimeField(editable=False)
    deployment_time = models.DateTimeField(blank=True, null=True)
    deployment_created_by = models.TextField(blank=True, default="")

    def save(self, *args, **kwargs):
        if self.deployment_created is None:
            self.deployment_created_by = "Admin"

        self.deployment_created = timezone.now()
        if self.deployment_time is None:
            self.deployment_time = self.deployment_created

        deploy()
        super(Deployment, self).save(*args, **kwargs)


def deploy():
    if hasattr(settings, "GATSBY_TRIGGER_URL"):
        try:
            requests.post(settings.GATSBY_TRIGGER_URL)
        except:
            pass
