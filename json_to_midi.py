#!/usr/bin/python2
# :/

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

#pip install --user python-midi

ticks_per_second = 2*1920.
midi_note_offset = 9+12 # lowest key shown is an A, plus one octave

color_to_channel_map = {
        'blue': 0,
        'green': 1,
    }

import argparse
import midi
import json

parser = argparse.ArgumentParser()
parser.add_argument('input_file', default='foo.json', nargs='?')
parser.add_argument('output_file', default='foo.mid', nargs='?')
args = parser.parse_args()

with open(args.input_file, 'r') as f:
    active_notes_per_frame = json.load(f)
    active_notes_per_frame = [dict(i) for i in active_notes_per_frame]

# according to python-midi doc:

# Instantiate a MIDI Pattern (contains a list of tracks)
pattern = midi.Pattern(resolution=1920) # use ardour-internal resolution to prevent rounding errors
# Instantiate a MIDI Track (contains a list of MIDI events)
track1 = midi.Track()
track2 = midi.Track()
# Append the track to the pattern
pattern.append(track1)
pattern.append(track2)

def process_notes(track, active_notes_per_frame, color='green'):
    last_notes = set()
    last_frame = 0
    for frame_index, note_dict in enumerate(active_notes_per_frame):

        #note_set = set(note_dict.keys())
        note_set = {note for note, c in note_dict.items() if c == color}

        for note in last_notes.difference(note_set):
            # note off events
            tick = int((frame_index - last_frame) / 60. * ticks_per_second)
            #tick = max(1, tick)
            # Instantiate a MIDI note off event, append it to the track
            off = midi.NoteOffEvent(tick=tick, pitch=note + midi_note_offset, channel=color_to_channel_map[last_dict[note]])
            track.append(off)
            last_frame = frame_index

        for note in note_set.difference(last_notes):
            # note on events
            tick = int((frame_index - last_frame) / 60. * ticks_per_second)
            #tick = max(1, tick)
            # Instantiate a MIDI note on event, append it to the track
            on = midi.NoteOnEvent(tick=tick, velocity=127, pitch=note + midi_note_offset, channel=color_to_channel_map[note_dict[note]])
            track.append(on)
            last_frame = frame_index

        last_notes = note_set
        last_dict = note_dict

    # Add the end of track event, append it to the track
    eot = midi.EndOfTrackEvent(tick=1)
    track.append(eot)

process_notes(track1, active_notes_per_frame, 'green')
process_notes(track2, active_notes_per_frame, 'blue')

#print(pattern)
# Save the pattern to disk
midi.write_midifile(args.output_file, pattern)
