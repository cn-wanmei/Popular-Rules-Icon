from io import BytesIO
from PIL import Image
from popular_rules_icon.styles8 import render_all_styles, STYLES

def test_eight_styles():
    img = Image.new('RGBA', (64, 64), (30, 144, 255, 255))
    buf = BytesIO(); img.save(buf, format='PNG')
    out = render_all_styles(buf.getvalue(), sizes=(128,))
    for s in STYLES:
        assert f'{s}:128:png' in out
