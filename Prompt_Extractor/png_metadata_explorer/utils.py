from PIL import Image, ImageDraw

def create_red_x_overlay(size):
    overlay = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.line((0, 0) + overlay.size, fill=(255, 0, 0, 128), width=5)
    draw.line((0, overlay.height, overlay.width, 0), fill=(255, 0, 0, 128), width=5)
    return overlay
