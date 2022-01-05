#! /usr/bin/env python3
#
# Cinderella Clock
# by Dave Thwaites
#
# initially based on clock.py by dionyziz:
# https://gist.github.com/dionyziz/7ed2e158ca2556ac78bab722182aa629


import os
import pygame
from datetime import datetime
from datetime import timedelta
import math
import getopt
import textwrap
import sys
from ola.ClientWrapper import ClientWrapper

olaWrapper = ClientWrapper()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

DIGITAL_H = 100 # height of digital clock
W = 600 # screen width
H = W + DIGITAL_H # screen height
CLOCK_W = W # analog clock width
CLOCK_H = W # analog clock height
HOURS_IN_CLOCK = 12
MINUTES_IN_HOUR = 60
SECONDS_IN_MINUTE = 60
SIZE = (W, H)


def get_angle_deg(unit, total):
    """Calculates the angle, in degrees, corresponding to a portion of the clock
       counting using the given units up to a given total and starting from 12
       o'clock and moving clock-wise."""
    return 90 - (360 * unit / total)


# this function taken from this stackoverflow answer by Rabbid76:
# https://stackoverflow.com/a/54714144
def blitRotate(surf, image, pos, originPos, angle):

    # offset from pivot to center
    image_rect = image.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
    
    # rotated offset from pivot to center
    rotated_offset = offset_center_to_pivot.rotate(-angle)

    # rotated image center
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    # get a rotated image
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)

    # rotate and blit the image
    surf.blit(rotated_image, rotated_image_rect)


def Usage():
    print(textwrap.dedent("""
    Usage: clock.py --universe <universe> --address <address>
    Display a 'Cinderella' clock, controllable via DMX, via OLA.
    -h, --help                Display this help message and exit.
    -u, --universe <universe> DMX Universe number.
    -a, --address <address>   DMX Address."""))


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:a:", ["help", "universe=", "address="])
    except getopt.GetoptError as err:
        print(str(err))
        Usage()
        sys.exit(2)

    universe = 3
    address = 400
    for o, a in opts:
        if o in ("-h", "--help"):
            Usage()
            sys.exit()
        elif o in ("-u", "--universe"):
            universe = int(a)
        elif o in ("-a", "--address"):
            address = int(a)

    def NewData(data):
        now = datetime.now()
        print(now.strftime('%H:%M:%S.%f'), "DMX Data:", address, ":", data[address-1+0], "->", str(round(data[address-1+0]/255,2)).ljust(5,"0"))

    def TickTock():
        now = datetime.now()
        print(now.strftime('%H:%M:%S.%f'), "Tick Tock!")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Stopping Cinderella Clock...")
                olaWrapper.Stop()

        screen.fill(WHITE)

        pygame.display.flip()

        olaWrapper.AddEvent(1000,TickTock)

    pygame.init()
    screen = pygame.display.set_mode(SIZE, pygame.RESIZABLE)
    pygame.display.set_caption('Clock')
    hour_font = pygame.font.SysFont('Calibri', 25, True, False)
    digital_font = pygame.font.SysFont('Calibri', 32, False, False)

    client = olaWrapper.Client()
    client.RegisterUniverse(universe, client.REGISTER, NewData)
    print("Starting Cinderella Clock...")
    olaWrapper.AddEvent(1000,TickTock)
    try:
        olaWrapper.Run()
    except KeyboardInterrupt:
        print("Stopping Cinderella Clock...")

    pygame.quit()
    sys.exit()



    # load images
    current_path = os.path.dirname(__file__)

    clock_face = pygame.image.load(os.path.join(current_path, 'Clock Face.bmp')).convert_alpha()
    hour_hand = pygame.image.load(os.path.join(current_path, 'Hour Hand.bmp')).convert_alpha()
    minute_hand = pygame.image.load(os.path.join(current_path, 'Minute Hand.bmp')).convert_alpha()
    second_hand = pygame.image.load(os.path.join(current_path, 'Second Hand.bmp')).convert_alpha()

    # scale images to fit our clock size
    face_scale = CLOCK_W / 1284
    face_centre = (int(1284 * 0.5 * face_scale), int(1292 * 0.5 * face_scale))
    face_width = int(1284 * face_scale)
    face_height = int(1292 * face_scale)

    hand_scale = CLOCK_W * 0.5 * 0.9 / (1100 - 250)
    hand_centre = (int(250 * hand_scale), int(100 * hand_scale))
    hand_length = int(1100 * hand_scale)
    hand_width = int(200 * hand_scale)

    clock_face = pygame.transform.scale(clock_face, (face_width, face_height))

    hour_hand = pygame.transform.scale(hour_hand, (hand_length, hand_width))
    minute_hand = pygame.transform.scale(minute_hand, (hand_length, hand_width))
    second_hand = pygame.transform.scale(second_hand, (hand_length, hand_width))

    # rotate the whole clock..?
    clock_theta = 0

    clock = pygame.time.Clock()
    done = False

    c_x, c_y = CLOCK_W / 2, CLOCK_H / 2
    center = (c_x, c_y)

    then = datetime.now()
    one_second = timedelta(seconds=1)

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        screen.fill(WHITE)

        now = datetime.now()

        # draw clock
        blitRotate(screen, clock_face, center, face_centre, - clock_theta)

        # draw hands
        hour_theta = get_angle_deg(now.hour + 1.0 * now.minute / MINUTES_IN_HOUR, HOURS_IN_CLOCK)
        minute_theta = get_angle_deg(now.minute, MINUTES_IN_HOUR)
        second_theta = get_angle_deg(now.second, SECONDS_IN_MINUTE)

        for (hand, theta) in (
            (hour_hand, hour_theta),
            (minute_hand, minute_theta),
            (second_hand, second_theta),
        ):
            blitRotate(screen, hand, center, hand_centre, theta - clock_theta)

        # draw digital clock
        digital_text = now.strftime('%H:%M:%S')
        text = digital_font.render(digital_text, True, BLACK)
        screen.blit(
            text,
            [
                W / 2 - digital_font.size(digital_text)[0] / 2,
                H - DIGITAL_H / 2 - digital_font.size(digital_text)[1] / 2
            ]
        )

        frame_delay = now - then
        digital_text = "Frame length: " + str(frame_delay)
        text = digital_font.render(digital_text, True, BLACK)
        screen.blit(
            text,
            [
                W / 2 - digital_font.size(digital_text)[0] / 2,
                H - DIGITAL_H / 2 - digital_font.size(digital_text)[1] / 2 - digital_font.size(digital_text)[1]
            ]
        )
        digital_text = str(round(one_second/frame_delay,2)).ljust(5,"0") + "fps"
        text = digital_font.render(digital_text, True, BLACK)
        screen.blit(
            text,
            [
                W / 2 - digital_font.size(digital_text)[0] / 2,
                H - DIGITAL_H / 2 - digital_font.size(digital_text)[1] / 2 + digital_font.size(digital_text)[1]
            ]
        )

        then = now

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
