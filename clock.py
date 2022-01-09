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
W = 500 # screen width
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

    zeroDMX = [0] * 512

    def NewData(data):
        nonlocal receivingDMX, dmxDelay, dmxThen, dmxData
        if data == zeroDMX:
           # completely zero DMX packet - probably a glitch..?
           return
        now = datetime.now()
        # print(now.strftime('%H:%M:%S.%f'), "DMX Data:", address, ":", data[address-1+0], "->", str(round(data[address-1+0]/255,2)).ljust(5,"0"), ",", data[address-1+1], "->", str(round(data[address-1+1]/255,2)).ljust(5,"0"), ",", data[address-1+2], "->", str(round(data[address-1+2]/255,2)).ljust(5,"0"))
        if receivingDMX:
            dmxDelay = now - dmxThen
        else:
            print(now.strftime('%H:%M:%S'), "Started receiving DMX...")
            receivingDMX = True
            dmxDelay = timedelta(seconds=0)
        dmxData = data[address-1:address-1+28]
        dmxThen = now

    def dmxTime(offset):
        return datetime(year=1, month=1, day=1, hour=int(round(dmxData[offset+0] / 255 * 23, 0)), minute=int(round(dmxData[offset+1] / 255 * 59, 0)), second=int(round(dmxData[offset+2] / 255 * 59, 0)))

    def dmxProgress(offset):
        return ((dmxData[offset+0]<<8) + dmxData[offset+1]) / 50

    def calculateHands(now):
        nonlocal dmx_time2_start
        nonlocal hour_theta, minute_theta, second_theta
        nonlocal nextTick, time
        nonlocal time2_start_second_offset

        if receivingDMX:
            # dmx_hour   = round(((dmxData[0]<<8) + dmxData[1]) / 65535 * 23, 0)
            #dmx_hour   = round(dmxData[0] / 255 * 23, 0)
            #dmx_minute = round(dmxData[1] / 255 * 59, 0)
            #dmx_second = round(dmxData[2] / 255 * 59, 0)
            dmx_control    = dmxData[0]
            dmx_progress   = dmxProgress(1)
            dmx_threshold1 = dmxProgress(3)  #  0:00:00  => 1s
            dmx_time1      = dmxTime(5)      #  9:20
            dmx_threshold2 = dmxProgress(8)  #  0:07:30  => 450s
            dmx_time2      = dmxTime(10)     # 11:00
            dmx_threshold3 = dmxProgress(13) #  0:12:00 => 720s
            dmx_time3      = dmxTime(15)     # 11:59:00
            dmx_threshold4 = dmxProgress(18) #  0:12:59 => 779s
            dmx_time4      = dmxTime(20)     # 11:59:59
            dmx_threshold5 = dmxProgress(23) #  0:17:30 => 1050s
            dmx_time5      = dmxTime(25)     # 13:00

            only_move_hands_on_second_tick = False

            if dmx_progress == 0:
                # 0: real time
                time = now
                nextTick = now
            elif dmx_progress < dmx_threshold1:
                # 0 -> threshold 1: seconds continue in real time, hours and minutes 'fade' from real time to time 1
                time_now = datetime(year=1, month=1, day=1, hour=now.hour, minute=now.minute, second=now.second)
                time = time_now + (dmx_time1 - time_now) * (dmx_progress / dmx_threshold1)
                time = time.replace(second=now.second)
                nextTick = nextTick+one_second if only_move_hands_on_second_tick else now
            elif dmx_progress == dmx_threshold1:
                # threshold 1: seconds continue in real time, hours and minutes from time 1 (9:20)
                time = dmx_time1.replace(second=now.second)
                nextTick = nextTick+one_second if only_move_hands_on_second_tick else now
            elif dmx_progress < dmx_threshold2:
                # threshold 1 -> 2: seconds continue in real time, hours and minutes 'fade' from time 1 to time 2
                time = dmx_time1 + (dmx_time2 - dmx_time1) * ((dmx_progress-dmx_threshold1) / (dmx_threshold2-dmx_threshold1))
                time = time.replace(second=now.second)
                nextTick = nextTick+one_second if only_move_hands_on_second_tick else now
            elif dmx_progress == dmx_threshold2:
                # threshold 2: seconds continue in real time, hours and minutes from time 2 (11:00)
                time = dmx_time2.replace(second=now.second)
                dmx_time2_start = time
                time2_start_second_offset = int(((time.second + 29) % 60) - 29)
                nextTick = nextTick+one_second if only_move_hands_on_second_tick else now
            elif dmx_progress < dmx_threshold3:
                # threshold 2 -> 3: seconds 'fade' from real time to time 3, hours and minutes 'fade' from time 2 to time 3
                time = dmx_time2 + (dmx_time3 - dmx_time2) * ((dmx_progress-dmx_threshold2) / (dmx_threshold3-dmx_threshold2))

                phase_duration = dmx_threshold3-dmx_threshold2
                phase_progress = dmx_progress-dmx_threshold2
                dmx_second = time.second
                now_second = now.second

                this_second = time2_start_second_offset + ((round(phase_duration/60)*60 - time2_start_second_offset + dmx_time3.second) / phase_duration * phase_progress)

                time = time.replace(second=int(this_second % 60))
                
                nextTick = nextTick+one_second if only_move_hands_on_second_tick else now
            elif dmx_progress == dmx_threshold3:
                # threshold 3: hours, minutes and seconds from time 3 (11:58:00)
                time = dmx_time3
                nextTick = nextTick+one_second if only_move_hands_on_second_tick else now
            elif dmx_progress < dmx_threshold4:
                # threshold 3 -> 4: hours, minutes and seconds 'fade' from time 3 to time 4
                time = dmx_time3 + (dmx_time4 - dmx_time3) * ((dmx_progress-dmx_threshold3) / (dmx_threshold4-dmx_threshold3))
                nextTick = nextTick+one_second if only_move_hands_on_second_tick else now
            elif dmx_progress == dmx_threshold4:
                # threshold 4: hours, minutes and seconds from time 4 (11:58:59)
                time = dmx_time4
                nextTick = nextTick+one_second if only_move_hands_on_second_tick else now
            elif dmx_progress < dmx_threshold5:
                # threshold 4 -> 5: seconds continue in real time, hours and minutes 'fade' from time 4 to time 5
                time = dmx_time4 + (dmx_time5 - dmx_time4) * ((dmx_progress-dmx_threshold4) / (dmx_threshold5-dmx_threshold4))
                time = time.replace(second=now.second)
                nextTick = nextTick+one_second if only_move_hands_on_second_tick else now
            elif dmx_progress == dmx_threshold5:
                # threshold 5: seconds continue in real time, hours and minutes from time 5 (12:05)
                time = dmx_time5.replace(second=now.second)
                nextTick = nextTick+one_second if only_move_hands_on_second_tick else now
            else:
                # default: freeze!
                nextTick = now

        else:
            # not receiving any DMX
            time = now
            nextTick = now
        hour_theta   = get_angle_deg(time.hour + 1.0 * time.minute / MINUTES_IN_HOUR, HOURS_IN_CLOCK)
        minute_theta = get_angle_deg(time.minute, MINUTES_IN_HOUR)
        second_theta = get_angle_deg(time.second, SECONDS_IN_MINUTE)

    def TickTock():
        nonlocal receivingDMX, redrawThen

        now = datetime.now()
        # print(now.strftime('%H:%M:%S.%f'), "Tick Tock!")
        if receivingDMX and (now - dmxThen) > dmxTimeout:
            print(now.strftime('%H:%M:%S'), "DMX Stream stopped...")
            receivingDMX = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("pygame.QUIT: Stopping Cinderella Clock...")
                olaWrapper.Stop()
                return

        redrawDelay = now - redrawThen

        screen.fill(WHITE)

        # draw clock
        blitRotate(screen, clock_face, center, face_centre, - clock_theta)

        if now > nextTick:
            calculateHands(now)

        # draw hands

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

        digital_text = "Frame length: " + str(redrawDelay)
        text = digital_font.render(digital_text, True, BLACK)
        screen.blit(
            text,
            [
                W / 2 - digital_font.size(digital_text)[0] / 2,
                H - DIGITAL_H / 2 - digital_font.size(digital_text)[1] / 2 - digital_font.size(digital_text)[1]
            ]
        )
        digital_text = str(round(one_second/redrawDelay,2)).ljust(5,"0") + "fps"
        text = digital_font.render(digital_text, True, BLACK)
        screen.blit(
            text,
            [
                W / 2 - digital_font.size(digital_text)[0] / 2,
                H - DIGITAL_H / 2 - digital_font.size(digital_text)[1] / 2 + digital_font.size(digital_text)[1]
            ]
        )

        if receivingDMX:
            try:
                digital_text = "DMX: " + str(round(one_second/dmxDelay,1)) + "fps"
            except ZeroDivisionError:
                digital_text = "DMX: ??? fps"
            text = digital_font.render(digital_text, True, BLACK)
            screen.blit(
                text,
                [
                    W / 2 - digital_font.size(digital_text)[0] / 2,
                    H - DIGITAL_H / 2 - digital_font.size(digital_text)[1] / 2 - digital_font.size(digital_text)[1]*2
                ]
            )

            digital_text = "DMX Data: " + str(address) + ": "
            digital_text += str(dmxData[0]) + "->" + str(round(dmxData[0]/255*100,1)) + "%, "
            digital_text += str(dmxData[1]) + "->" + str(round(dmxData[1]/255*100,1)) + "%, "
            #digital_text += str(dmxData[0]) + "," + str(dmxData[1]) + "->" + str((dmxData[0]<<8) + dmxData[1]) + "=" + str(round(((dmxData[0]<<8) + dmxData[1])/65535*100,2)) + "%, "
            digital_text += str(dmxData[2]) + "->" + str(round(dmxData[2]/255*100,1)) + "%"
            text = digital_font.render(digital_text, True, BLACK)
            screen.blit(
                text,
                [
                    W / 2 - digital_font.size(digital_text)[0] / 2,
                    H - DIGITAL_H / 2 - digital_font.size(digital_text)[1] / 2 - digital_font.size(digital_text)[1]*3
                ]
            )

        pygame.display.flip()

        redrawThen = now
        olaWrapper.AddEvent(1000/60,TickTock)

    pygame.init()
    screen = pygame.display.set_mode(SIZE, pygame.RESIZABLE)
    pygame.display.set_caption('Clock')
    hour_font = pygame.font.SysFont('Calibri', 25, True, False)
    digital_font = pygame.font.SysFont('Calibri', 32, False, False)

    dmxThen = datetime.now()
    dmxDelay = timedelta(seconds=0)
    redrawThen = datetime.now()
    receivingDMX = False
    dmxData = []
    dmx_time2_start = datetime(year=1, month=1, day=1)
    time2_start_second_offset = 0
    hour_theta = 0
    minute_theta = 0
    second_theta = 0
    nextTick = datetime.now()
    time = datetime.now()

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

    c_x, c_y = CLOCK_W / 2, CLOCK_H / 2
    center = (c_x, c_y)

    one_second = timedelta(seconds=1)
    dmxTimeout = timedelta(seconds=1)

    client = olaWrapper.Client()
    client.RegisterUniverse(universe, client.REGISTER, NewData)
    print("Starting Cinderella Clock...")
    olaWrapper.AddEvent(10,TickTock)
    try:
        olaWrapper.Run()
    except KeyboardInterrupt:
        print("KeyboardInterrupt: Stopping Cinderella Clock...")

    pygame.quit()
    sys.exit()



if __name__ == "__main__":
    main()
