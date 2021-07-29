from thefriendlyplanets import *


def test_align():
    i = make_friendly_image(
        "docs/uranus-test-image.fit",
        size=256,
        planet_name="Uranus",
        arcseconds_per_pixel=0.32,
        vmin=1,
        vmax=1e3,
        filter_pixels=5,
        cmap="gray_r",
        suffixes=["pdf", "png"],
        row=1172,
        col=1478,
    )
