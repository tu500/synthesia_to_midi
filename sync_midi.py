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

import argparse
import midi

parser = argparse.ArgumentParser()
parser.add_argument('input_file', default='foo.mid', nargs='?')
parser.add_argument('sync_file', default='timesync.mid', nargs='?')
parser.add_argument('output_file', default='synced.mid', nargs='?')
args = parser.parse_args()

sync_pattern = midi.read_midifile(args.sync_file)
sync_track = sync_pattern[0]
sync_resolution = sync_pattern.resolution
orig_pattern = midi.read_midifile(args.input_file)
orig_resolution = orig_pattern.resolution

sync_ticks = []
current_tick = 0
for event in sync_track:
    current_tick += event.tick
    if isinstance(event, midi.NoteOnEvent):
        sync_ticks.append(int(float(current_tick) / sync_resolution * orig_resolution)) # convert to resolution of orig_pattern

new_pattern = midi.Pattern(resolution=1920)
new_resolution = 1920

for orig_track in orig_pattern:
    beat_iterator = iter(enumerate(zip([0] + sync_ticks, sync_ticks)))
    beat_index, (beat_start_in_orig, beat_end_in_orig) = next(beat_iterator)
    new_track = midi.Track()
    new_pattern.append(new_track)
    current_tick = 0
    last_tick = 0

    for event in orig_track:
        current_tick += event.tick

        try:
            while current_tick > beat_end_in_orig:
                    beat_index, (beat_start_in_orig, beat_end_in_orig) = next(beat_iterator)
        except:
            print('MIDI event beyond sync beat ignored:', event)
            continue

        orig_beat_length = beat_end_in_orig - beat_start_in_orig
        new_tick = int(beat_index * new_resolution + (current_tick - beat_start_in_orig) / float(orig_beat_length) * new_resolution)
        if isinstance(event, midi.NoteOnEvent):
            #print('on  {pitch} {new_tick}'.format(pitch=event.pitch, new_tick=new_tick))
            on = midi.NoteOnEvent(tick=new_tick - last_tick, velocity=event.velocity, pitch=event.pitch, channel=event.channel)
            new_track.append(on)
        elif isinstance(event, midi.NoteOffEvent):
            #print('off {pitch} {new_tick}'.format(pitch=event.pitch, new_tick=new_tick))
            off = midi.NoteOffEvent(tick=new_tick - last_tick, pitch=event.pitch, channel=event.channel)
            new_track.append(off)
        else:
            pass
        last_tick = new_tick
    
    eot = midi.EndOfTrackEvent(tick=1)
    new_track.append(eot)

midi.write_midifile(args.output_file, new_pattern)
