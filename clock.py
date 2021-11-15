#! /usr/bin/env python3.8
#
# Cinderella Clock
# by Dave Thwaites
#
# initially based on clock.py by dionyziz:
# https://gist.github.com/dionyziz/7ed2e158ca2556ac78bab722182aa629


import os
import pygame
from datetime import datetime
import math

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

DIGITAL_H = 100 # height of digital clock
W = 600 # screen width
H = W + DIGITAL_H # screen height
CLOCK_W = W # analog clock width
CLOCK_H = W # analog clock height
MARGIN_H = MARGIN_W = 5 # margin of analog clock from window border
CLOCK_R = (W - MARGIN_W) / 2 # clock radius
HOUR_R = CLOCK_R / 2 # hour hand length
MINUTE_R = CLOCK_R * 7 / 10 # minute hand length
SECOND_R = CLOCK_R * 8 / 10 # second hand length
TEXT_R = CLOCK_R * 9 / 10 # distance of hour markings from center
TICK_R = 2 # stroke width of minute markings
TICK_LENGTH = 5 # stroke length of minute markings
HOUR_STROKE = 5 # hour hand stroke width
MINUTE_STROKE = 2 # minute hand stroke width
SECOND_STROKE = 2 # second hand stroke width
CLOCK_STROKE = 2 # clock circle stroke width
CENTER_W = 10 # clock center mount width
CENTER_H = 10 # clock center mount height
HOURS_IN_CLOCK = 12
MINUTES_IN_HOUR = 60
SECONDS_IN_MINUTE = 60
SIZE = (W, H)

def circle_point(center, radius, theta):
    """Calculates the location of a point of a circle given the circle's
       center and radius as well as the point's angle from the xx' axis"""

    return (center[0] + radius * math.cos(theta),
            center[1] + radius * math.sin(theta))

def line_at_angle(screen, center, radius, theta, color, width):
    """Draws a line from a center towards an angle. The angle is given in
       radians."""
    point = circle_point(center, radius, theta)
    pygame.draw.line(screen, color, center, point, width)

def get_angle(unit, total):
    """Calculates the angle, in radians, corresponding to a portion of the clock
       counting using the given units up to a given total and starting from 12
       o'clock and moving clock-wise."""
    return 2 * math.pi * unit / total - math.pi / 2

def get_angle_deg(unit, total):
    """Calculates the angle, in degrees, corresponding to a portion of the clock
       counting using the given units up to a given total and starting from 12
       o'clock and moving clock-wise."""
    return 90 - (360 * unit / total)

def blitRotate(surf, image, pos, originPos, angle):

    # offset from pivot to center
    image_rect = image.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
    
    # roatated offset from pivot to center
    rotated_offset = offset_center_to_pivot.rotate(-angle)

    # roatetd image center
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    # get a rotated image
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)

    # rotate and blit the image
    surf.blit(rotated_image, rotated_image_rect)
  
    # draw rectangle around the image
    #pygame.draw.rect(surf, (255, 0, 0), (*rotated_image_rect.topleft, *rotated_image.get_size()),2)


pygame.init()
#screen = pygame.display.set_mode(SIZE, pygame.FULLSCREEN)
#screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN, pygame.RESIZABLE)
#screen = pygame.display.set_mode(SIZE)
screen = pygame.display.set_mode(SIZE, pygame.RESIZABLE)
pygame.display.set_caption('Clock')
hour_font = pygame.font.SysFont('Calibri', 25, True, False)
digital_font = pygame.font.SysFont('Calibri', 32, False, False)

current_path = os.path.dirname(__file__)

clock_face = pygame.image.load(os.path.join(current_path, 'Clock Face.jpg')).convert_alpha()
hour_hand = pygame.image.load(os.path.join(current_path, 'Hour Hand.png')).convert_alpha()
minute_hand = pygame.image.load(os.path.join(current_path, 'Minute Hand.png')).convert_alpha()
second_hand = pygame.image.load(os.path.join(current_path, 'Second Hand.png')).convert_alpha()

#hour_hand = pygame.transform.scale(hour_hand, (550, 100))
#minute_hand = pygame.transform.scale(minute_hand, (550, 100))
#second_hand = pygame.transform.scale(second_hand, (550, 100))

face_scale = CLOCK_W / 1284
face_centre = (1284 * 0.5 * face_scale, 1292 * 0.5 * face_scale)
face_width = 1284 * face_scale
face_height = 1292 * face_scale

hand_scale = CLOCK_W * 0.5 * 0.9 / (1100 - 250)
hand_centre = (250 * hand_scale, 100 * hand_scale)
hand_length = 1100 * hand_scale
hand_width = 200 * hand_scale

clock_face = pygame.transform.scale(clock_face, (face_width, face_height))

clock_theta = 0

hour_hand = pygame.transform.scale(hour_hand, (hand_length, hand_width))
minute_hand = pygame.transform.scale(minute_hand, (hand_length, hand_width))
second_hand = pygame.transform.scale(second_hand, (hand_length, hand_width))

clock = pygame.time.Clock()
done = False

c_x, c_y = CLOCK_W / 2, CLOCK_H / 2
center = (c_x, c_y)

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    screen.fill(WHITE)

    now = datetime.now()


    #pygame.draw.ellipse(
    #    screen,
    #    BLACK,
    #    (50,50,300,500),
    #    CLOCK_STROKE
    #)

    # draw clock
    blitRotate(screen, clock_face, center, face_centre, - clock_theta)

    # draw hands
    hour_theta = get_angle_deg(now.hour + 1.0 * now.minute / MINUTES_IN_HOUR, HOURS_IN_CLOCK)
    minute_theta = get_angle_deg(now.minute, MINUTES_IN_HOUR)
    second_theta = get_angle_deg(now.second, SECONDS_IN_MINUTE)

    #for (radius, theta, color, stroke) in (
    #    (HOUR_R, hour_theta, BLACK, HOUR_STROKE),
    #    (MINUTE_R, minute_theta, BLACK, MINUTE_STROKE),
    #    (SECOND_R, second_theta, RED, SECOND_STROKE),
    #):
    #    line_at_angle(screen, center, radius, theta, color, stroke)

    blitRotate(screen, hour_hand, center, hand_centre, hour_theta - clock_theta)
    blitRotate(screen, minute_hand, center, hand_centre, minute_theta - clock_theta)
    blitRotate(screen, second_hand, center, hand_centre, second_theta - clock_theta)

#    # draw clock
#    pygame.draw.circle(
#        screen,
#        BLACK,
#        center, CLOCK_W / 2 - MARGIN_W / 2,
#        CLOCK_STROKE
#    )
#    # draw clock mount
#    pygame.draw.circle(
#        screen,
#        BLACK,
#        center, CLOCK_W / 2 - MARGIN_W / 2,
#        CLOCK_STROKE
#    )

#    # draw hour markings (text)
#    for hour in range(1, HOURS_IN_CLOCK + 1):
#        theta = get_angle(hour, HOURS_IN_CLOCK)
#        text = hour_font.render(str(hour), True, BLACK)
#        (text_width, text_height) = hour_font.size(str(hour))
#        (point_x, point_y) = circle_point(center, TEXT_R, theta)
#        screen.blit(text, (point_x-text_width/2, point_y-text_height/2))

#    # draw minute markings (lines)
#    for minute in range(0, MINUTES_IN_HOUR):
#        theta = get_angle(minute, MINUTES_IN_HOUR)
#        p1 = circle_point(center, CLOCK_R - TICK_LENGTH, theta)
#        p2 = circle_point(center, CLOCK_R, theta)
#        pygame.draw.line(screen, BLACK, p1, p2, TICK_R)

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

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
