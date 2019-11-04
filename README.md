# Synthesia to MIDI

This is a collection of quickly hacked together scripts to extract MIDI data
from a rendered synthesia-style video as can be found by abundance on Youtube
and the like.

Sometimes people who upload those videos don't supply music sheets, for various
reasons. If you're like me and prefer having printed sheets instead of a video
for reference, then these scripts may be helpful to you.

## Disclaimer

These scripts were literally hacked together on one afternoon with nothing
better to do. I stopped when they did what I wanted. So don't expect too much.

## Dependencies

For the first steps you probably need `youtube-dl` and `ffmpeg`. The python
scripts depend on `cv2` and `python-midi` respectively. And yes, the latter is
a python2-only package. :(

## Usage

First, use `ffmpeg` to convert the video into picture files for every frame. By
the way, `youtube-dl` is your friend to get any video from pretty much any
video hosting platform.

```sh
$ ffmpeg -i input.mp4 out%05d.jpg
```

The first script will now, for every frame, extract the keys that are pressed.
To do this it looks at a single pixel-line, first extracts the pixel columns
corresponding to each individual key being shown, then loops through all frames
and applies a color-heuristic to check which keys are pressed.

Make sure to set the start and end frame such that the frames in between have
valid video data. (No fade outs etc.)

The reference frame should not have any keys pressed, usually you can use the
same one as for the start frame.

All scripts have a `--help` option to see the command line arguments.

```
$ python3 active_notes_per_frame.py --key-detection-frame <reference-frame-number> --start-frame <start-index> --end-frame <end-index>
```

The next script will take the `json` file produced in the previous step and
convert it into a midi file. The usual colors blue and green will be written
into two different tracks in the same MIDI file.

```
$ python2 json_to_midi.py
```

The resulting MIDI file now has the extracted data. This will however not be
aligned to the MIDI-internal tempo / beats. To do that you can either quantize
manually, or use the third script provided. It will take a separate sync-track
(ie. a MIDI file with a note played at every beat) and sync all events to this
track, linearly interpolating between the beat positions.

To use this you can for example import the generated MIDI file in some DAW like
`ardour`. Let it playback the file and live-record a new MIDI track with a note
played at every beat. (The pitch played does not matter, neither does the note
length, only the NoteOn event is evaluated.)

To export a MIDI region in ardour, right-click the region, then
`> <trackname> > export`. To combine several regions into one, route the MIDI
data internally in ardour and re-record into a new MIDI track.

```
$ python2 sync_midi.py
```

Then you can quantize the final MIDI file and import it into a music sheet
editor of your choice.

Good luck, have fun.

## License

The code is licensed under `GPLv3+`.
