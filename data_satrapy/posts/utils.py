import os
import re
# import secrets
from PIL import Image
from flask import current_app
from data_satrapy.models import Field
# from data_satrapy.config import basedir


def list_subs():
    subs = [str(field) for field in Field.query.all()]
    subs.sort()
    return subs


def find_field(data):
    return Field.query.filter_by(subject=data).first()


def save_picture(form_picture, filename):
    # random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = filename + f_ext  # random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, "static/thumbnails", picture_fn)
    # picture_path = os.path.join(basedir, "static/thumbnails", picture_fn)

    output_size = (640, 320)  # (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def src_match(string, pattern="(https|http):\S+"):
    try:
        result = re.search(pattern, string)
        link = result.group()
        name = string.replace(link, "").strip()
        return name, link
    except AttributeError:
        pass
