#!/usr/bin/env python3
"""Label generator for Jukebox."""
# (c) François GUILLIER under GNU General License v3

# Image Std = 66 x 29 ---- 2.275 ---- 780 x 342@300ppi
# Image Word = 46.8 x 54  -----  0.866 ---- 552 x 638@300ppi ---- 369 x 425@200ppi

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import sys
import yaml

# Label Width
wl = 70 * mm
# Label height
hl = 50.8 * mm
# Margin
mg = 2 * mm
# Print border
border = False
# Font for Word/Picture cards
# Source : https://www.fontsquirrel.com/fonts/gloria-hallelujah
font_word = 'GloriaHallelujah'


def font_height(font_name, font_size):
    """Get font height details."""
    from reportlab.pdfbase import pdfmetrics
    face = pdfmetrics.getFont(font_name).face
    (ascent, descent) = face.ascent, face.descent
    return ascent * font_size / 1000.0, descent * font_size / 1000.0, (ascent - descent) * font_size / 1000.0


def print_frame(c):
    """Print a label frame."""
    c.setLineWidth(1)
    c.setLineCap(1)
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)
    for i in range(5):
        c.line(0, hl * (i + 1), wl * 3, hl * (i + 1))
    c.rect(0, 0, wl * 3, hl * 5)
    c.line(wl, 0, wl, hl * 5)
    c.line(wl * 2, 0, wl * 2, hl * 5)


def print_label_std(c, pos, data):
    """Print a standard label."""
    # Conversion position to coordinates
    i = (pos - 1) // 3
    j = (pos - 1) % 3

    # First title
    c.setFont("Helvetica-Bold", 10)
    c.drawString(wl * j + mg + 12 * mm,
                 hl * i + 45 * mm - font_height("Helvetica-Bold", 10)[0],
                 data.get('title1'))

    # Second title
    c.setFont("Helvetica", 10)
    c.drawString(wl * j + mg + 12 * mm,
                 hl * i + 40 * mm - font_height("Helvetica", 10)[0],
                 data.get('title2', ''))

    # Category
    # Source of icon: https://www.iconsdb.com/red-icons/speaker-icon.html
    if data.get('category') == 'music1':
        speaker = 'speaker-128-green.gif'
    elif data.get('category') == 'music2':
        speaker = 'speaker-128-red.gif'
    elif data.get('category') == 'story':
        speaker = 'speaker-128-blue.gif'
    c.drawImage(speaker, wl * j + mg + 3, hl * i + 36 * mm, 10 * mm, 10 * mm,
                [250, 255, 250, 255, 250, 255])

    # Main image
    if 'image' in data:
        c.drawInlineImage(data.get('image'), wl * j + mg, hl * i + mg,
                          wl - 2 * mg, 33 * mm - 2 * mg)

    # Duration
    c.setStrokeColorRGB(78 / 255, 48 / 255, 132 / 255)
    c.setLineWidth(2)
    c.setLineCap(1)
    if data.get('duration'):
        dur = data.get('duration')
        dur_width = c.stringWidth(dur, "Helvetica", 10)
        c.line(wl * j + mg, hl * i + 33 * mm,
               wl * (j + 0.5) - dur_width / 2 - 4, hl * i + 33 * mm)
        c.line(wl * (j + 0.5) + dur_width / 2 + 4, hl * i + 33 * mm,
               wl * (j + 1) - mg, hl * i + 33 * mm)
        c.setFillColorRGB(78 / 255, 48 / 255, 132 / 255)
        c.drawString(wl * (j + 0.5) - dur_width / 2, hl * i + 33 * mm - 1, dur)
        c.setFillColorRGB(0, 0, 0)
    else:
        c.line(wl * j + mg, hl * i + 33 * mm,
               wl * (j + 1) - mg, hl * i + 33 * mm)


def print_label_word(c, pos, data):
    """Print a 'word' label."""
    # Conversion position to coordinates
    i = (pos - 1) // 3
    j = (pos - 1) % 3

    c.saveState()
    c.rotate(90)

    # English name
    if len(data.get('name')) > 18:
        size = 8
        offset = 0.55
    else:
        size = 10
        offset = 0.5

    c.setFont(font_word, size)
    c.drawString(hl * (i + offset) - 
        c.stringWidth(data.get('name'), font_word, size) / 2,
        - wl * j - 10 * mm + font_height(font_word, size)[0],
        data.get('name'))

    # French name
    if len(data.get('nom')) > 18:
        size = 8
        offset = 0.6
    else:
        size = 10
        offset = 0.65

    c.setFont(font_word, size)
    c.drawString(hl * (i + offset) - 
        c.stringWidth(data.get('nom'), font_word, size) / 2,
        - wl * j - 15 * mm + font_height(font_word, size)[0],
        data.get('nom'))

    # Category
    # Source of icon: https://www.iconsdb.com/red-icons/saxophone-icon.html
    if data.get('category') == 'instrument':
        speaker = 'saxophone-128.gif'
    c.drawImage(speaker, hl * i + mg, - wl * j - 12 * mm, 10 * mm, 10 * mm,
                [250, 255, 250, 255, 250, 255])

    # Main image
    if 'image' in data:
        c.drawInlineImage(data.get('image'), hl * i + mg, - wl * j + mg - wl,
                          hl - 2 * mg, 58 * mm - 2 * mg)

    c.restoreState()


def open_page(c):
    """Create a new blank page."""
    c.translate(0, 21.5 * mm)


def close_page(c):
    """Finish the completed page."""
    if border:
        print_frame(c)
    c.showPage()


def print_pages(pos, data_list, output_filename):
    """Print pages of labels."""
    pagedef = False

    c = canvas.Canvas("jukebox.pdf")
    pdfmetrics.registerFont(TTFont(font_word, '{}.ttf'.format(font_word)))

    for data in data_list:
        if not data.get('print', True):
            continue
        if not pagedef:
            open_page(c)
            pagedef = True

        if data['category'] in ('music1', 'music2', 'story'):
            print_label_std(c, pos, data)
        elif data['category'] in ('instrument'):
            print_label_word(c, pos, data)
        else:
            raise Exception('Wrong category')
        if pos == 15:
            pos = 1
            close_page(c)
            pagedef = False
        else:
            pos = pos + 1

    if pagedef:
        close_page(c)

    c.save()


def get_first_label_position():
    """Read the position of first label from command line"""
    if len(sys.argv) == 2:
        try:
            start = int(sys.argv[1])
            if start > 0 and start < 16:
                return start
        except:
            pass
    return 1


with open('db.yaml') as f:
    data = yaml.load(f)

print_pages(get_first_label_position(), data, 'jukebox.pdf')
