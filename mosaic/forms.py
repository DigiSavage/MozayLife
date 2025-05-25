"""
forms.py

PURPOSE:
    Defines the ImageForm for uploading the main mosaic source image and configuring mosaic options.

DETAILS:
    - Lets the user upload a file, select shape and quality, set artistic/fading effects, and name the output file.
    - Used by `views.py` to render and process the main upload form.

MODERNIZATION NOTES:
    - Fully Python 3/Django 3+ compatible.
    - You can further enhance with help_text, custom validation, or widgets.

"""
from django import forms

class ImageForm(forms.Form):
    SHAPE_OPTIONS = (
        ("square", "Square/Rectangle"),
        ("hexagons", "Hexagons"),
        ("puzzle", "Puzzle"),
    )

    QUALITY_OPTIONS = (
        ("low", "Mosaic with low quality"),
        ("med", "Mosaic with medium quality"),
        ("high", "Mosaic with high quality"),
    )

    imgfile = forms.ImageField(label='Select the main image (centerpiece)', required=True)
    shape = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=SHAPE_OPTIONS,
        label='Tile Shape',
        required=True
    )
    quality = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=QUALITY_OPTIONS,
        label='Mosaic Quality',
        required=True
    )
    artistic_effect = forms.BooleanField(
        required=False,
        label='Enable artistic tiling effect (advanced)'
    )
    fading = forms.IntegerField(
        max_value=100,
        min_value=0,
        required=False,
        label='Transparency (0–100, optional)',
        help_text='Controls blending with the original. 0 = no fade, 100 = full fade.'
    )
    outfile = forms.CharField(
        max_length=100,
        label='Output image filename (e.g., mosaic.jpg)',
        required=False,
        help_text='You can use .jpg, .png, etc.'
    )
