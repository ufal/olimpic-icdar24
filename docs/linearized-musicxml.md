# Linearized MusicXML

Design principles:

- **Not a new encoding, only linearize MusicXML (with minimal changes).**
    - e.g. token order is determined by MusicXML element order
    - e.g. token names are determined by MusicXML element names and values
- **Focus on the visual part of MusicXML, not the audio part.** Try to encode graphemes, not semantics (while still sticking to MusicXML)
    - e.g. use `<type>` instead of `<duration>`
    - e.g. ignore `<alter>` pitch element
- **Ignore precise typesetting information, focus on the musical content.**
    - e.g. notehead positions, measure widths, system breaks, page breaks
- **Remove excessive verbosity to make the linearization feasible for ML models.**
    - e.g. represent stem/beam/staff/voice changes, not its value for each note

Additional decisions:

- Based on W3C MusicXML v4.0: https://www.w3.org/2021/06/musicxml40/
- Works with `score-partwise` documents, see [this page](https://www.w3.org/2021/06/musicxml40/tutorial/structure-of-musicxml-files/) for more info.
- Ignores all the metadata (`<part-list>`, `<identification>`), linearizes only the `<part>` element contents (measures with music).
- Linearizes measures "in-parallel", no measure-to-measure dependencies (keeps minimal state information - no assumed key signature or time signature).

The encoding comes in two flavors:

- **Core:** Contains only symbols essential for replayability. If it ain't affect MIDI, it's not present.
    - e.g. notes, rests, measures, beams, duration dots, ties, triplets, staves, voices, clefs, accidentals
- **Extended:** Contains additional ornaments and markings.
    - e.g. slurs, staccato, accents, fermata

Some symbols are omitted even from the extended encoding:
    - e.g. dynamic markings, hairpins, pedal signs, glisando

In this documentation, MusicXML elements are represented by angle brackets (e.g. `<note>`, `<chord>`) and linearized MusicXML token types are represented by square brackets (e.g. `[pitch]`, `[type]`).

At the end of this document, there is a grammar pseudocode that specifies what tokens can be combined in what order.

While MusicXML may allow more freedom in how music is represented (say, voices, backup/forward, staves), we based our decisions based on the data taken from the OpenScore Lieder corpus, when exported to MusicXML through MuseScore 3.6.2. This provides us with additional structure (such as voice order), which is not important in our case, but you should take into consideration if using other sources of MusicXML.


## Pending questions

- Half and whole notes in 3/4 and weird/16 time signatures? How does counting "up" works?
- `print-object="no"` creates invisible objects, check how they are used and why
- double barlines, repeats


## Reference documentation

Here, each section documents a specific part of the encoding.


### Note `<note>`, `<pitch>`, `<type>`

A note is the fundamental building block of music and it consist of three properties: pitch, onset, duration. The onset is encoded implicitly in the linear ordering of notes and their durations. Therefore we only need to encode the pitch and the duration.


#### Pitch `<pitch>`, `[pitch]`

The core token that identifies a note is the pitch token. No other musical symbol contains pitch in MusicXML, you can see that [`<pitch>`](https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/pitch/) element can only be a child of the `<note>` element.

In MusicXML, pitch is by `<octave>`, `<step>`, and `<alter>`. We join the first two values to build the pitch token:

```
C4 E4 G4 F5 ...
```

This is the [scientific pitch notation](https://en.wikipedia.org/wiki/Scientific_pitch_notation).

In MusicXML the octave ranges from 0 to 9 and steps are A, B, C, D, E, F, G.

In the OpenScore Lieder train dataset we encountered these pitches:

```
__ __ __ __ __ __ __
__ __ __ __ __ __ __
C7 D7 E7 F7 G7 A7 B7
C6 D6 E6 F6 G6 A6 B6
C5 D5 E5 F5 G5 A5 B5
C4 D4 E4 F4 G4 A4 B4
C3 D3 E3 F3 G3 A3 B3
C2 D2 E2 F2 G2 A2 B2
C1 D1 E1 F1 G1 A1 B1
__ __ __ F0 G0 A0 B0
```

Since this covers almost the entire range, it makes sense to take all combinations of 0-9 and A-G as the note pitch tokens, which gives us 70 distinct tokens.

The `<alter>` value is ignored during linearization, because:

- It can be reconstructed from the key signature and preceeding accidentals.
- Is not in any way explicitly visually present in the music score.
- If added would introduce a stateful dependency across measures (from the key signature), which would break the encoding's measure-independence feature.


#### Duration `<type>`, `<duration>`, `[type]`

Duration of a note in the linearized MusicXML is represented by the `<type>` element (note type, e.g. half, quarter, half). The `<duration>` element is designed for processing by audio replay software, and can be calculated back from the `<type>` is the given context (time signature, tuplets) is present, so we consciously ignore it.

> We only make sure the `<duration>` value is what we expect, given the musical context.

The reason is that `<type>` is graphically, explicitly represented in the score, whereas `<duration>` is represented implicitly.

These are the `<type>` values [allowed by MusicXML](https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/note-type-value/):

```
1024th 512th 256th 128th 64th
32nd 16th eighth quarter half whole
breve long maxima
```

These are the values present in OpenScore Lieder train set:

```
__ __ __ 128th 64th
32nd 16th eighth quarter half whole
breve __ __
```

Therefore we recommend using all the 14 values specified by MusicXML. This gives us 14 type (duration) tokens.

The conversion between `<type>` and `<duration>` is controlled by the [`divisions`](https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/divisions/) element, stated (usually) at the beginning of a part in `<attributes>`. The `<divisions>` dictates, how many time units does a single quarter note take up. This is a **quarter note**, regardless of the time signature. In a 3/2 time signature one measure takes up 3 half notes, so six quarter notes. So six-times the `<divisions>` value is the duration of a single measure. But one quarter note still takes up one `<divisions>` worth of time.

What DOES affect `<duration>` is tuplets via the `<time-modification>` element. If a note is an eighth note and should take 36 time units, if it's in a 3in2 tuplet, it takes up only 24 time units (while still being an eighth note). See [this MusicXML example](https://www.w3.org/2021/06/musicxml40/musicxml-reference/examples/tuplet-element-regular/).

With nested tuplets, this is a mess, but the `<time-modification>` is relative to the top-most-level, i.e. it can be used directly to compute the proper `<duration>` just from knowing the `<type>` without parsing the complex tuplet nesting. See [this MusicXML example](https://www.w3.org/2021/06/musicxml40/musicxml-reference/examples/tuplet-element-nested/).


#### Rest `<rest>`, `[rest]`

Rest is a kind of notation that behaves like a note without pitch. A note that is not played. Therefore we represent rests like notes, where the pitch token has been replaced by the `rest` token. The `rest` token is immediately followed by the type (duration) token.

Vertical rest position is not encoded (used in polyphony).

If a rest is alone in a measure, it is considered to be a **measure rest** and it always looks like a whole rest, even if the measure contains only three quarter notes at maximum. Because of this, measure rests are encoded in MusicXML with a `measure="yes"` attribute. This rest lacks the `<type>` element (since its meaning is kind of dissolved because of the duration-exception).

For this reason measure rests cannot use the `[type]` token and a new token `rest:measure` is introduced in its place to serve as the new syntactic root of the `[note]` token sequence.

Note that sometimes the measure rest may not even be displayed, because there are multiple staves and this rests applies only to one of the staves. See measure 40 [here](https://musescore.com/user/27638568/scores/5087729).


### Stem `<stem>`, `[stem]`

Linearized MusicXML encodes stem orientation, because MusicXML encodes it via the [`<stem>`](https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/stem/) element.

MusicXML allows four values:

```
down up double none
```

In practise, notes without any stem lack the `<stem>` element completely. Similarly, notes with two stems are represented as two separate `<note>` elements in two different voices, each having its own stem. This means that in the OpenScore Lieder corpus, when exported by MuseScore, only `down` and `up` and missing `<stem>` element are possible values.

Therefore we only define two new tokens and make them optional:

```
stem:up stem:down
```

To cut sequence length, we track stem orientation implicitly in this fashion:
- When we start encoding a measure, we don't have a stem orientation specified and we remember that the stem orientation is `NULL`
- Notes without any stems do not contain any stem tokens.
- The first note that contains a stem, gets the appropriate stem token (always, since we start by tracking `NULL`), and we start tracking that stem orientation as our new "implicit" stem orientation.
- Whenever we hit a note (with a stem) with a different stem orientation than currently tracked, we output the appropriate stem orientation token and start tracking the new orientation.
- The tracked stem orientation is reset to `NULL` whenever:
    - New measure is entered
    - New voice is entered (see the `<backup>` element)


### Chord `<chord>`, `[chord]`

In MusicXML, chord is not an explicit object, but something that emerges from the relationship of multiple notes. If we have a chord with three notes, these three notes are represented almost like individual notes, but the last two notes contain the `<chord>` element. This element indicates, that these notes are additional noteheads for a singular chord.

For noteheads (notes) of a chord, some features are shared, and some are distinct:

- `pitch` - each note has its own pitch
- `type` - all notes typically have the same type, but MusicXML does allow for the variability of type within a chord, so our linearized MusicXML also does. This means that we repeat the `[type]` token for each note even when it's almost always the same.
- `accidental` - each note has its own accidentals, complete independence
- `stem` - stem orientation is tracked as if the notes were independent (so only the first one may have the stem orientation token)
- `beam` - beaming information is always present on the first note, never on a note that contains the `<chord>` element.
- `grace` - grace notes can be chords, then all the grace notes have the `<grace>` element, and chord notation works just like for non-grace notes (grace notes are just notes that have no duration)
- `rest` - rests cannot participate in chords
- `tie` - each note has its own tie notation (chord notes can have ties), usually all have the same
- `dot` - each note has its own dot notation (chord notes can have ties), usually all have the same

Notes within a chord are ordered by MuseScore from the lowest-pitch to the highest. MusicXML does not enforce any order, but we use this order so that the representation is not ambiguous and can be used to train ML models.


### Beam `<beam>`, `[beam]`

Beams in MusicXML are represented by the `<beam>` element on a note, stating whether a beam starts, continues, or ends at that note. It also tracks multiple beams separately, giving them numbers.

We linearize this by converting the start and end (and hooks) to tokens. We ignore the `continue` elements to reduce sequence length and make the encoding stateful in a similar way to how stem orientation is represented.

Also, we ignore the beam numbering, since in most music, the beams are nested (they never cross).

This introduces 4 new tokens (see the [MusicXML spec](https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/beam-value/)):

```
beam:begin beam:end beam:forward-hook beam:backward-hook
```

The token is doubled (tripled, ...) if there are two or more beams running through a note (just like MusicXML has multiple `<beam>` elements).

So a beamed group of 4 eighth C4 notes are represented like this:

```
G4 eighth beam:begin
A4 eighth
G4 eighth
A4 eighth beam:end
```

<img src="https://www.w3.org/2021/06/musicxml40/static/datatypes/beam-value-begin.png">

And if the first two a sixteenth notes and the last two are eighth notes:

```
C4 16th beam:begin beam:begin
C4 16th beam:end
C4 eighth
C4 eighth beam:end
```

There may also be a sixteenth hook, like this:
```
E5 16th beam:begin beam:forward-hook
C5 eighth dot beam:end
```

<img src="https://www.w3.org/2021/06/musicxml40/static/datatypes/beam-value-forward-hook.png">


### Accidental `<accidental>`, `[accidental]`

The `<accidental>` element in MusicXML is present, when there's a graphical accidental visible in the score next to the note. This is the way our linearized MusicXML encodes semitones, not the `<alter>` pitch element, that is ignored.

The OpenScore Lieder corpus uses these accidentals:

```
sharp flat natural
double-sharp flat-flat natural-sharp natural-flat
```

There [are additional values](https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/accidental-value/) possible, but we don't focus on microtonal music, so we choose to ignore them.

This introduces 7 tokens to the linearized MusicXML vocabulary.


### Tie `<tied>`, `[tied]`

The graphical representation of a tie is in MusicXML represented within the `<notations>` element by the presence of a `<tied>` element. There also exists a `<tie>` element, but that has audio meaning, not notation meaning so we ignore it.

The element has one attribute `type` with values `start` and `stop`. We convert this to two tokens that we attach to a note:

```
tied:start tied:stop
```

If a note is both an end and a start of a tie, it contains both of these tokens in this order (the same order is used in MusicXML).


### Duration dot `<dot>`, `[dot]`

Each note can contain zero or many duration dots. Each one of those dots is in MusicXML represented by a `<dot>` element. Each one of these element occurences gets translated to a `dot` token in the linearized MusicXML representation.


### Grace note `<grace>`, `[grace]`

Grace notes are regular notes, that (are smaller) and don't have duration. Other than that, they behave like any other notes from the perspective of MusicXML.

In MusicXML these are represented by an element `<grace>`, that behave similarly to the `<chord>` element. Therefore in the linearized representation, grace notes are represented by a `grace` token.

Grace notes can be slashed, which in MusicXML is represented by an attribute `slash="yes"`. If that attribute is present, then the `"grace"` token is followed by a `"grace:slash"` token.


### Clef `<clef>`

In MusicXML a clef is represented within the `<attributes>` element in between notes. It has three important values:

- `<sign>` - what type of clef is this (G, C, F)
- `<line>` - what staffline it sits on (1, 2, 3, 4, 5 - numbered from the bottom line up)
- `number` - attribute containing the staff number (1 or 2 or missing)

This is the distribution of clefs in the OpenScore Lieder corpus:

```py
Counter({'G2': 4018, 'F4': 2825, 'G1': 4, 'C1': 2, 'F3': 1})
```

Clefs often change at the beginning of a measure. The first measure defines both clefs in one `<attributes>` element (staff 1 first, then staff 2). If the part is not a piano grandstaff, the staff number is omitted.

If a clef changes in the middle of a measure, it is annotated in the first voice of a staff. So second staff clef change is annotated in the sequence of notes of the first voice of the second staff. This is very likely defined by MuseScore, since MusicXML just states that the modification happens score-wise, not MusicXML note-order-wise. If at the beginning of a measure only one clef changes, only that one clef is notated. The other one is not - it is kept implicit from the previous measures. The specific placement of clefs in the note stream for these experiments is driven by the output ordering and formatting of MuseScore.

Sometimes a clef is notated at the end of a system, because it changes at the beginning of the next system. This is only typesetting feature and is not encoded in MusicXML nor its linearization (but the clef change on the next system is of course encoded).

In MusicXML, clefs at the beginning of systems are NOT explicitly encoded. However we train an end-to-end model that only gets systems, without the information of preceeding notation. So to correctly decode a system, we add explicit repetition of clefs at the beginning of each system measure (just like what is done in the actual printed score). (note that this does not apply for time signatures, only clefs and key signatures)


### Key signature `<key>`, `<fifths>`

Key signature is represented in MusicXML by the `<key>` element inside of the `<attributes>` element. It can contain:

- `<fifths>` - encodes the number of sharps or flats
- `<cancel>` - explicit cancelling of the previous key signature, since not used in OpenScore Lieder corpus, we ignore this element
- `<mode>` - specifies the mode of the key (major, minor, dorian, ... unusual ones), here only "major", "minor", and "none" are used in the corpus; but this element is ignored because it encodes a semantic "meaning" or "understanding" of the key with respect to the song - it has no effect on the number, or positioning of the key signature accidentals

The `<fifths>` element value is a number - the number of flats/sharps, in range:

```
-7 -6 -5 ... -2 -1 0 1 2 ... 5 6 7
```

Negative values are flats, zero is no signature, positive are sharps (the number of them). This is the distribution of signatures in the corpus:

```py
Counter({'0': 228, '1': 226, '-1': 212, '-3': 194, '2': 173, '4': 167,
    '-2': 160, '-4': 152, '3': 130, '5': 78, '-5': 77, '-6': 30, '6': 17,
    '7': 4, '-7': 3})
```

Key signature is in MusicXML explicitly notated at the begining of a part even if it's 0. (maybe because MuseScore does that, not that MusicXML requires it). Then it's notated at the beginning of a measure whenever the signature changes.

Key changes mid-measure are not allowed in MuseScore (see [this thread](https://musescore.org/en/node/91516)) and so they will not appear in our data.

Sometimes a key change is notated at the end of a system, because it changes at the beginning of the next system. This is only typesetting feature and is not encoded in MusicXML nor its linearization (but the key change on the next system is of course encoded).

In MusicXML, key signatures at the beginning of systems are NOT explicitly encoded. However we train an end-to-end model that only gets systems, without the information of preceeding notation. So to correctly decode a system, we add explicit repetition of key signatures at the beginning of each system measure (just like what is done in the actual printed score). (note that this does not apply for time signatures, only clefs and key signatures)


### Time signature `<time>`, `[time]`

> **On reading time in music:**<br>
> Time signature consist of two numbers on top of each other (`C` means `4/4` and `crossed C` means `2/2`). The top number states the number *beats* per mesure, the bottom one states the type of the *beat*. `/2` means one beat is one half note, `/4` means one beat is one quarter note. The tempo (e.g. `tempo: 140`) means the number of *beats* per minute. The `<divisions>` MusicXML states the number of time units per *quarter note* (not the *beat*!) - a quarter note may be half a beat in a `2/2` meter. Because of this, whole notes do not fit into less-than whole measures (e.g. `3/4` is filled by a dotted half note, or three quarter notes). Measure rests are an exception! They look like whole restst, but if they are alone in the measure, they are used even if the measure is less-than-whole. This is the only exception and MusicXML encodes them with a special attribute.

When analyzing the OpenScore Lieder corpus, we find these time signatures being used:

```
     1/4  
2/2  2/4  2/8
3/2  3/4  3/8
4/2  4/4  4/8  4/16
     5/4  5/8
     6/4  6/8  6/16
     7/4  7/8
          8/8
     9/4  9/8  9/16


          12/8


          15/8
```

Although the frequency is biased towards a few, the distribution is still quite broad:

```py
Counter({'4/4': 705, '3/4': 546, '2/4': 538, '6/8': 326, '3/8': 149,
    '9/8': 114, '2/2': 83, '12/8': 50, '3/2': 48, '6/4': 40, '4/8': 16,
    '9/4': 10, '5/4': 10, '7/8': 10, '4/2': 7, '2/8': 5, '1/4': 3, '8/8': 3,
    '6/16': 2, '9/16': 2, '15/8': 2, '5/8': 1, '7/4': 1, '4/16': 1})
```

So for this reason and for maximum similarity to MusicXML we decided to code both numbers as separate tokens. This adds these 20 tokens to our vocabulary:

```
beats:1 beats:2 beats:3 ... beats:16
beat-type:2 beat-type:4 beat-type:8 beat-type:16
```

We also add the token `time` that represents the `<time>` XML element, so that it's easier to decode malformed sequences (we can ignore all `beat` and `beat-type` tokens that do not follow a `time` token directly).

So an example 3/4 time signature would be encoded as these three tokens:

```
time beats:3 beat-type:4
```

Which neatly mirrors the XML:

```xml
<time>
    <beats>3</beats>
    <beat-type>4</beat-type>
</time>
```

Time signature in MusicXML is stated at the first measure and then during changes. In notation, the same behaviour occus (another words, time signature is NOT re-stated at the begining of each system). We DO NOT re-state the time signature at the beginning of each system even though we train an end-to-end model on individual systems. We don't do this because the printed notation does not do that AND the model does not need it, because the encoding does not enforce measure durations explicitly and note durations are encoded visually via the note type.

Sometimes the notation setting software places time signature at the end of a line, when the measure on the next line has a different time signature. This cautionary time signature is not encoded, only the next measure's time signature will be encoded.

Here are some interesting scores, time signature-wise, for testing:
- https://musescore.com/score/6196804 (12/8, 6/8, 9/8)
- https://musescore.com/score/6447372 (7/8, 5/8, 3/8)
- https://musescore.com/score/6166579 (4/4, 3/8, 6/8)
- https://musescore.com/score/6156388 (9/16, 3/8, 9/16)
- https://musescore.com/score/5861338 (4/4, 3/2, 2/2, 4/4)


### Tuplets and tremolos `<tuplet>`, `<tremolo>`, `[tuplet]`, `[tremolo]`

TODO: (do it like beams, ignore nested tuplets)

There are tuplets and tremolos, they both use the `<tuplet>` element, but tremolo also has the `<tremolo>` element.

There are (almost?) no nested tuplets in the corpus, so we ignore these.

Interesting scores to test on:
- https://musescore.com/user/27638568/scores/5974308 (sixteenth triplets)
- https://musescore.com/user/27638568/scores/6581327 (tremolos)
- https://musescore.com/user/27638568/scores/5015573 (triplets with invisible numbers - rule of continuation)
- https://musescore.com/user/27638568/scores/4985999 (triplets with invisible numbers - rule of continuation)
- https://musescore.com/openscore-lieder-corpus/scores/5052823 (more tremolos)

Some tuplet statistics:

```xml
<tuplet type="stop" />: 24967
<tuplet type="start" bracket="no" />: 14057
<tuplet type="start" bracket="no" show-number="none" />: 6628
<tuplet type="start" bracket="yes" />: 4471
<tuplet type="start" bracket="yes" show-number="none" />: 96
<tuplet type="stop" number="1" />: 3
<tuplet type="start" number="1" bracket="no" show-number="none" />: 2
<tuplet type="start" number="1" bracket="yes" />: 1

# nested tuplets?
<tuplet type="start" bracket="no" show-number="none">
    <tuplet-actual><tuplet-number>8</tuplet-number><tuplet-type>16th</tuplet-type></tuplet-actual>
    <tuplet-normal><tuplet-number>8</tuplet-number><tuplet-type>16th</tuplet-type></tuplet-normal>
</tuplet>: 16
<tuplet type="start" number="2" bracket="yes">
    <tuplet-actual><tuplet-number>3</tuplet-number><tuplet-type>eighth</tuplet-type></tuplet-actual>
    <tuplet-normal><tuplet-number>2</tuplet-number><tuplet-type>eighth</tuplet-type></tuplet-normal>
</tuplet>: 2
<tuplet type="start" bracket="no" show-number="none">
    <tuplet-actual><tuplet-number>2</tuplet-number><tuplet-type>16th</tuplet-type></tuplet-actual>
    <tuplet-normal><tuplet-number>2</tuplet-number><tuplet-type>16th</tuplet-type></tuplet-normal>
</tuplet>: 2
<tuplet type="start" bracket="no" show-number="none">
    <tuplet-actual><tuplet-number>2</tuplet-number><tuplet-type>16th</tuplet-type></tuplet-actual>
    <tuplet-normal><tuplet-number>4</tuplet-number><tuplet-type>16th</tuplet-type></tuplet-normal>
</tuplet>: 2
<tuplet type="start" bracket="no" show-number="none">
    <tuplet-actual><tuplet-number>2</tuplet-number><tuplet-type>quarter</tuplet-type></tuplet-actual>
    <tuplet-normal><tuplet-number>2</tuplet-number><tuplet-type>quarter</tuplet-type></tuplet-normal>
</tuplet>: 2
<tuplet type="start" number="2" bracket="no">
    <tuplet-actual><tuplet-number>5</tuplet-number><tuplet-type>32nd</tuplet-type></tuplet-actual>
    <tuplet-normal><tuplet-number>4</tuplet-number><tuplet-type>32nd</tuplet-type></tuplet-normal>
</tuplet>: 1
```


### Measure `<measure>`, `[measure]`

Measures begin with a `measure` token, and then a sequence of inner elements continues. So the `measure` token can be used as the measure separator and all information about the measure after the `measure` token and before the next `measure` token.


### Staff `<staff>`, `[staff]`

Monophonic music is typically written on only one-staff systems, whereas piano music is written onto two-staff systems. The piano two-staff system is sometimes called a grandstaff.

There may be even three-staff systems and there is [one example in the corpus](https://musescore.com/openscore-lieder-corpus/scores/6005658)! But these cases are rare and will ignore them.

For single-staff music, there is no need to annotate which staff a given note belongs to. So none of the mentioned tokens are used in such a case. NOT EVEN EXPLICIT `staff:1` TOKENS! (because MusicXML does not include the `<staff>` elements in such a case either)

For grandstaff music, a voice may transition from one staff to the other, so we need explicit notation. A multi-staff part begins its first `<measure>` with a `<staves>` element inside the `<attributes>` element, which contains `2` - the number of staves that will be used. Since stave count changes mid-part are rare, we chose to ignore this element during linearization.

The staff number is tracked in the same way to the stem orientation with tokens `staff:1` and `staff:2` (1 = upper, 2 = lower). The tracking is reset with measure start and voice change (`<backup>`), so the first notes of each voice always include the staff information and then notes that first switch to another staff include staff information.

During decoding, a measure can be checked to see if it contains these tokens and that can be used to disambiguate monophonic music from pianoforms.


### Voices `<voice>`

TODO


#### Backup `<backup>`, `[backup]`

TODO


#### Forward `<forward>`, `[forward]`

important: contains staff and voice information, since it's almost a rest, needed if the voice does not start at the beginning of the measure; but should be encoded?? Can be left to the note... What does MuseScore do?


### Other note notations

First, some statistics to get a sense:

```py
# <notations>
Counter({'slur': 145962, 'tied': 71064, 'articulations': 56520,
'tuplet': 50560, 'arpeggiate': 23582, 'ornaments': 5069, 'fermata': 3691,
'technical': 320, 'non-arpeggiate': 177, 'slide': 12})

# <notations>/<articulations>
Counter({'staccato': 48882, 'accent': 14571, 'strong-accent': 4648,
'tenuto': 4613, 'staccatissimo': 1288, 'detached-legato': 1167,
'breath-mark': 198, 'soft-accent': 32, 'caesura': 12, 'doit': 1, 'scoop': 1})

# <notations>/<ornaments>
Counter({'tremolo': 5652, 'trill-mark': 437, 'wavy-line': 393,
'turn': 80, 'inverted-mordent': 77, 'accidental-mark': 26,
'inverted-turn': 19})

# <notations>/<technical>
Counter({'fingering': 511})

# grace notes (not <notations>, but very similar)
Counter({'grace': 7067})
```


## Pseudo grammar

This is an attempt at modelling the linearized MusicXML by a simple grammar:

> Explainer:
> - whitespace is concatenation
> - parenthesis work as usual
> - `?` means optional (zero or one time)
> - `+` is one or more times
> - `*` is zero or more times
> - `|` is alternation (one or the other)
> - `"asd"` is a terminal
> - `[asd]` is a non-terminal
> - `#` is a line comment

```py
# the whole linearized MusicXML sequecne is a [part] non-terminal
# and it is just a list of measures
[part] = [measure]+

# [measure] starts with the "measure" terminal and then contains notes
# and other notation primitives (noted as measure-item)
[measure] = "measure" [measure-element]*

# an element inside a measure
[measure-element] =
    | [note]
    | [key]
    | [time]
    | [clef]
    | [backup]
    | [forward]

[key] =
    | "key:fifths:-7"
    | "key:fifths:-6"
    | "key:fifths:-5"
    | "key:fifths:-4"
    | "key:fifths:-3"
    | "key:fifths:-2"
    | "key:fifths:-1"
    | "key:fifths:0"
    | "key:fifths:1"
    | "key:fifths:2"
    | "key:fifths:3"
    | "key:fifths:4"
    | "key:fifths:5"
    | "key:fifths:6"
    | "key:fifths:7"

[time] = "time" [beats] [beat-type]

[beats] =
    | "beats:1"
    | "beats:2"
    | "beats:3"
    | "beats:4"
    | "beats:5"
    | "beats:6"
    | "beats:7"
    | "beats:8"
    | "beats:9"
    | "beats:10"
    | "beats:11"
    | "beats:12"
    | "beats:13"
    | "beats:14"
    | "beats:15"
    | "beats:16"

[beat-type] =
    | "beat-type:2"
    | "beat-type:4"
    | "beat-type:8"
    | "beat-type:16"

[clef] =
    | "clef:G1" | "clef:G2" | "clef:G3" | "clef:G4" | "clef:G5"
    | "clef:C1" | "clef:C2" | "clef:C3" | "clef:C4" | "clef:C5"
    | "clef:F1" | "clef:F2" | "clef:F3" | "clef:F4" | "clef:F5"

[backup] = ???? #TODO

[forward] = ???? #TODO

[note] = (
    [grace]?
    [chord]?
    ([rest] | [pitch])
    ([type] | "rest:measure")  # this is the ROOT of a [note], must be present, is used for parsing
    [dot]*
    [accidental]?
    [stem]?
    [staff]?
    [beam]*
    [tied]?

    # EXTENDED encoding

    # TODO: tuplets
    # TODO: EXTENDED encoding symbols
)

# [grace] indicates that the note is a grace note, can be slashed
[grace] = "grace" "grace:slash"?

# [chord] indicates that the note is a chord extension from the previous note
[chord] = "chord"

# [rest] indicates that the note is in fact a rest
[rest] = "rest"

# pitch in the scientific pitch notation
[pitch] =
    | "C0" | "D0" | "E0" | "F0" | "G0" | "A0" | "B0"
    | "C1" | "D1" | "E1" | "F1" | "G1" | "A1" | "B1"
    | "C2" | "D2" | "E2" | "F2" | "G2" | "A2" | "B2"
    | "C3" | "D3" | "E3" | "F3" | "G3" | "A3" | "B3"
    | "C4" | "D4" | "E4" | "F4" | "G4" | "A4" | "B4"
    | "C5" | "D5" | "E5" | "F5" | "G5" | "A5" | "B5"
    | "C6" | "D6" | "E6" | "F6" | "G6" | "A6" | "B6"
    | "C7" | "D7" | "E7" | "F7" | "G7" | "A7" | "B7"
    | "C8" | "D8" | "E8" | "F8" | "G8" | "A8" | "B8"
    | "C9" | "D9" | "E9" | "F9" | "G9" | "A9" | "B9"

# visual type of the note or rest
[type] =
    | "1024th" | "512th" | "256th" | "128th" | "64th"
    | "32nd" | "16th" | "eighth" | "quarter" | "half" | "whole"
    | "breve" | "long" | "maxima"

# [dot] is a duration dot, one occurence for each notated dot
[dot] = "dot"

# possible accidentals
[accidental] =
    # the ususal ones
    | "sharp"
    | "flat"
    | "natural"
    # the weird ones from accidental overriding
    | "double-sharp"
    | "flat-flat"
    | "natural-sharp"
    | "natural-flat"
    # no microtonal music, this is enough
    # https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/accidental-value/

# a change in orientation of stems
[stem] =
    | "stem:up"
    | "stem:down"

# a change in current staff
[staff] =
    | "staff:1"
    | "staff:2"

# beam start or end or a hook
[beam] =
    | "beam:begin"
    | "beam:end"
    | "beam:forward-hook"
    | "beam:backward-hook"

[tied] =
    | "tied:start"
    | "tied:stop"

```


## MusicXML element reference with implementation notes

At [this page](https://www.w3.org/2021/06/musicxml40/musicxml-reference/element-tree/) you can see the list of all MusicXML elements in a tree-structure. Here we list these elements (or element groups) and state, whether they belong to the core encoding, the extended, or are ignored for some reason:


### Used elements

```xml
Root of the MusicXML document
<score-partwise>
```

```xml
Root of the actual musical content
= The thing that we convert back and forth
<part>
```

```xml
Used, Linearization: CORE
<measure> converted to [measure]
<attributes> not explicitly linearized, only its contents
<clef><line><sign> converted to [clef]
<divisions> used but not explicitly linearized
<key><fifths> converted to [key]
<staves> used but not explicitly linearized
<time><beat-type><beats> converted to [time]
<backup> used for voice changes
<duration> used in backup/forward, implicitly used in notes and rests
<forward> used for invisible restst within voices
<note> converted to [note]
<accidental> converted to [accidental]
<beam> converted to [beam]
<chord> converted to [chord]
<dot> converted to [dot]
<grace> converted to [grace]
<pitch><octave><step> converted to [pitch]
<rest> converted to [rest]
<staff> converted to [staff]
<stem> converted to [stem]
<time-modification> used for tuplets
<type> converted to [type], encodes duration
<voice> used but not explicitly linearized
<notations> not explicitly linearized, only its contents
<articulations> not explicitly linearized, only its contents
<ornaments> not explicitly linearized, only its contents
<technical> not explicitly linearized, only its contents
<tied> converted to [tied]

================

<tuplet> TODO
    <tuplet-actual>
    <tuplet-dot>
    <tuplet-number>
    <tuplet-type>
    <tuplet-normal>
    <tuplet-dot>
    <tuplet-number>
    <tuplet-type>
```

```xml
Used, Linearization: EXTENDED
<slur>
<fermata>
<arpeggiate>
<staccato>
<accent>
<strong-accent>
<tenuto>
<tremolo>
<trill-mark>

================

<measure-style> TODO
    <beat-repeat>
    <except-voice>
    <slash-dot>
    <slash-type>
    <measure-repeat>
    <multiple-rest>
    <slash>
    <except-voice>
    <slash-dot>
    <slash-type>
<barline> TODO
    <bar-style>
    <coda>
    <ending>
    <fermata>
    <repeat>
    <segno>
    <wavy-line>
```


### Ignored elements

```xml
Ignored, because they are metadata that do not affect the music itself:
<score-partwise>
<credit>
<defaults>
<identification>
<movement-number>
<movement-title>
<part-list>
<work>
```

```xml
Ignored knowingly - it should never be added for some reason
<directive> deprecated since MXL 2.0
<print> contains layout information only, we DO use it for system slicing, but not for linearization
<sound> contains non-visual data
<alter> pitch alter is linearized implicitly by key signature and accidentals
<play><ipa><mute><other-play><semi-pitched> sound data? (i guess)
<tie> indicates sound, tied indicates notation
```

```xml
Ignored by omission - it is rare, strange, obscure, but may be added in theory
<clef-octave-change> rare
<footnote> contains free text
<for-part>
<instruments>
{key}<cancel><key-accidental><key-alter><key-octave><key-step><mode> key signature features
<level> contains free text
<part-symbol>
<staff-details>
{time}<interchangeable><time-relation><senza-misura> time signature features
<transpose><chromatic><diatonic><double><octave-change>
<bookmark>
<direction> dynamic, hairpins, piano pedals - ignored because it's non essential to notes themselves
<figured-bass>
<grouping><feature>
<harmony>
<link>
<listening><offset><other-listening><sync>
<cue> cue notes
<instrument>
<listen><assess><other-listen><wait>
<lyric> contains free text
<notehead>
<notehead-text><accidental-text><display-text>
{rest}<display-octave><display-step> positional information for rests is not important for reading, only printing
<unpitched><display-octave><display-step> we are not currently interested in drums
{note}<dynamics> MuseScore attaches dynamics to direction, not to notes, so there are none of these elements
```

```xml
Ignored notations - exist, but are too infrequent, pain to implement:
<non-arpeggiate>
<glissando>
<slide>
<fingering>
<staccatissimo>
<detached-legato>
<breath-mark>
<soft-accent>
<caesura>
<wavy-line>
<turn>
<inverted-mordent>
<inverted-turn>
<accidental-mark>
```

```xml
Ignored notations - rare:
<doit>
<scoop>
<falloff>
<other-articulation>
<plop>
<spiccato>
<stress>
<unstress>
<other-notation>
<delayed-inverted-turn>
<delayed-turn>
<haydn>
<inverted-vertical-turn>
<mordent>
<other-ornament>
<schleifer>
<shake>
<vertical-turn>
<technical> all except for fingering, that does occur a bit
```
