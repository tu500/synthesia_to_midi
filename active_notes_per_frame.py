#!/usr/bin/python3

# Copyright (C) 2019  Philip Matura
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import cv2
import json
import statistics

parser = argparse.ArgumentParser()
parser.add_argument('--output-file', default='foo.json')
parser.add_argument('--key-detection-frame', required=True, type=int, help='The frame number from which to extract the pixel range of the keys. Use a frame without any pressed keys.')
parser.add_argument('--detection-row', type=int, default=900, help='Pixel row to use for key detection. Make sure to include both black and white keys.')
parser.add_argument('--frame-file-formatstring', default='out{index:05d}.jpg', help='Format string to use to get the filename for a frame number.')
parser.add_argument('--start-frame', type=int, default=0)
parser.add_argument('--end-frame', type=int, required=True)
args = parser.parse_args()

img = cv2.imread(args.frame_file_formatstring.format(index=args.key_detection_frame)) # an image without any pressed keys
# an unobstructed pixel line, showing the keys
scanned_line_index = args.detection_row
row = img[scanned_line_index]

# distinguish white and black pixels, heuristic
def pixelvalue(p):
    return (int(p[0]) + int(p[1]) + int(p[2])) < 384

# calculate column ranges representing the keys in the row above
ranges = []
current_value = pixelvalue(row[0])
current_start = 0
for i in range(1, len(row)):
    pv = pixelvalue(row[i])
    if pv == current_value:
        continue
    ranges.append(((current_start, i), current_value))
    current_value = pv
    current_start = i
if current_start != len(row)-1:
    ranges.append(((current_start, len(row)), current_value))

ranges = [((start, end), value) for ((start, end), value) in ranges if end-start > 5]


# decide wether pixel value is colored (from HSL value)
# https://en.wikipedia.org/wiki/File:HSL_color_solid_cylinder_saturation_gray.png
def is_color(h,l,s):
    return (50 < l < 205) and s > 50 # heuristic

#img2 = cv2.imread('out00999.jpg')
# return the indices of the ranges (see above) that are colored in a single frame
def colored_ranges_from_image(filename):
    img = cv2.imread(filename)
    row = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)[scanned_line_index]

    colored_ranges = []
    for index, ((start, end), _) in enumerate(ranges):
        l = [is_color(*row[i]) for i in range(start, end)]
        if l.count(True) / len(l) > .5: # heuristic: half the pixels should be colored
            mean_hue = statistics.mean(row[i][0] for i in range(start, end))
            if abs(mean_hue - 105) < 20:
                color = 'blue'
            elif abs(mean_hue - 45) < 20:
                color = 'green'
            else:
                color = None
            colored_ranges.append((index, color))

    return colored_ranges

# call colored_ranges_from_image for every frame and export list to json
keys_per_frame = []
for i in range(args.start_frame, args.end_frame): # range with valid data
    if i % 100 == 0:
        # print progress
        print(i)
    res = colored_ranges_from_image(args.frame_file_formatstring.format(index=i))
    keys_per_frame.append(res)
with open('foo.json', 'w') as f:
    json.dump(keys_per_frame, f)
