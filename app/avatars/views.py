import io
import random

import py_avataaars
from django.http import HttpResponse
from django.utils.cache import add_never_cache_headers, patch_cache_control


def avatar_image(request, seed=None):
    if not seed:
        seed = request.GET.get("seed") or "random"

    if seed != "random":
        random.seed(seed)

    bytes = io.BytesIO()

    def r(enum_):
        return random.choice(list(enum_))

    avatar = py_avataaars.PyAvataaar(
        style=py_avataaars.AvatarStyle.CIRCLE,
        skin_color=r(py_avataaars.SkinColor),
        hair_color=r(py_avataaars.HairColor),
        facial_hair_type=r(py_avataaars.FacialHairType),
        facial_hair_color=r(py_avataaars.HairColor),
        top_type=r(py_avataaars.TopType),
        hat_color=r(py_avataaars.Color),
        mouth_type=r(py_avataaars.MouthType),
        eye_type=r(py_avataaars.EyesType),
        eyebrow_type=r(py_avataaars.EyebrowType),
        nose_type=r(py_avataaars.NoseType),
        accessories_type=r(py_avataaars.AccessoriesType),
        clothe_type=r(py_avataaars.ClotheType),
        clothe_color=r(py_avataaars.Color),
        clothe_graphic_type=r(py_avataaars.ClotheGraphicType),
    )
    avatar.render_png_file(bytes)

    response = HttpResponse(bytes.getvalue())
    response["content-type"] = "image/png"
    if seed == "random":
        add_never_cache_headers(response)
    else:
        patch_cache_control(response, max_age=60, public=True)

    return response
