#!/usr/bin/env python3


import RPi.GPIO as GPIO

import os
import threading
import time
import vlc
import yaml

import decode

class Player:

    def __init__(self):
        self.idle = True
        self.next = False
        self.medialist = []
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached,
                                        self._end_callback)

    def _end_callback(self, event):
        print(event)
        self.idle = True
        self.next = True if len(self.medialist) else False

    def play_next(self):
        self.next = False
        if len(self.medialist) == 0:
            self.idle = True
            return False
        filename = os.path.expanduser(self.medialist.pop(0))
        self.player.audio_set_volume(60)
        self.player.set_media(self.instance.media_new(filename))
        if self.player.play() == -1:
            self.idle = True
            return False
        self.idle = False
        return True

    def play(self, medialist):
        if medialist is None:
            return
        if isinstance(medialist, list) or isinstance(medialist, tuple):
            self.medialist = list(medialist)
        else:
            self.medialist = [medialist]
        self.play_next()

    def pause(self):
        self.player.pause()


class Albums:

    def __init__(self):
        self.albums = {}

    def _get_info(self, filepath):
        with open(filepath) as f:
            inf = yaml.load(f)

        return (inf.get('card_id'), inf.get('groups', []))
 

    def scan_albums(self, path):
        album_media = []
        album_card_id = None
        album_groups = []
        for entry in os.scandir(path):
            if not entry.name.startswith('.') and entry.is_file():
                filepath = os.path.join(path, entry.name)
                if entry.name == 'info.yaml':
                    (album_card_id, album_groups) = self._get_info(filepath)
                else:
                    if entry.name.lower()[-4:] in \
                    ('.ogg', '.mp3', '.m4a', '.wav'):
                        album_media.append(filepath)
        if album_card_id:
            self.albums[int(album_card_id)] = {'groups': album_groups,
                                               'media': sorted(album_media)}

    def scan_top(self, path):
        for entry in os.scandir(path):
            if not entry.name.startswith('_') and entry.is_dir():
                self.scan_albums(os.path.join(path, entry.name))

    def scan(self):
        self.scan_top('/MUSIC/')
        import pprint
        pprint.pprint(self.albums)

    def get_media(self, id):
        if int(id) in self.albums:
            return self.albums.get(int(id)).get('media')
        else:
            return None


class Button(threading.Thread):

    g_switch = 26
    g_led = 20

    def __init__(self):
        threading.Thread.__init__(self)
        self.btn_pressed = False
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.g_switch, GPIO.IN)
        GPIO.setup(self.g_led, GPIO.OUT)
        GPIO.add_event_detect(self.g_switch, GPIO.FALLING, callback=self.press,
                              bouncetime=500)
        self.led = GPIO.PWM(self.g_led, 1000)
        self.led.start(100)
        self.state = 2

    def stop(self):
        self.state = -1

    def press(self, gpio):
        self.btn_pressed = True

    def pressed(self):
        r = self.btn_pressed
        self.btn_pressed = False
        return r

    def led_on(self):
        self.state = 1

    def led_off(self):
        self.state = 0

    def led_breathe(self):
        self.state = 3

    def led_flash(self):
        self.state = 2

    def run(self):
        _state = -1
        dc = 0
        up = True
        while self.state != -1:
            if self.state == 3:
                _state = 3
                if up:
                    if dc >= 100:
                        up = False
                    else:
                        dc += 1
                else:
                    if dc <= 0:
                        up = True
                    else:
                        dc -= 1
                self.led.ChangeDutyCycle(dc)
                time.sleep(0.01)
                continue
            elif self.state < 2:
                if _state != self.state:
                    _state = self.state
                    self.led.ChangeDutyCycle(_state * 100)
                    dc = _state * 100
                time.sleep(.1)
            else:
                _state = 2
                dc = 0
                self.led.ChangeDutyCycle(100)
                time.sleep(.05)
                self.led.ChangeDutyCycle(0)
                time.sleep(.2)


button = Button()
button.start()

albums = Albums()
albums.scan()

card = decode.Card()
player = Player()


paused = False

try:
  while True:
    if card.read(player.idle):
        player.play(albums.get_media(card.current_id))
        paused = False
        button.led_off()
    if player.next:
        player.play_next()
        paused = False
        button.led_off()
    else:
        if player.idle:
            button.led_on()
    if button.pressed():
        if not player.idle:
            player.pause()
            paused = not paused
            if paused:
                button.led_breathe()
            else:
                button.led_off()
    time.sleep(.05)

except KeyboardInterrupt:
  button.stop()
