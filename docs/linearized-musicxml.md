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

- Should grace notes be core or extended?
- Tremolo signs?
- Half and whole notes in 3/4 and weird/16 time signatures? How does counting "up" works?


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


### Clef


### Key signature


### Time signature `<time>`


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

```
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

Time signature in MusicXML is stated at the first measure and then during changes. In notation, the same behaviour occus (another words, time signature is NOT re-stated at the begining of each system). Sometimes the notation setting software places time signature at the end of a line, when the measure on the next line has a different time signature. This cautionary time signature is not encoded, only the next measure's time signature will be encoded.

Here are some interesting scores, time signature-wise, for testing:
- https://musescore.com/score/6196804 (12/8, 6/8, 9/8)
- https://musescore.com/score/6447372 (7/8, 5/8, 3/8)
- https://musescore.com/score/6166579 (4/4, 3/8, 6/8)
- https://musescore.com/score/6156388 (9/16, 3/8, 9/16)
- https://musescore.com/score/5861338 (4/4, 3/2, 2/2, 4/4)


### Measure `<measure>`, `[measure]`


### Staff `<staff>`, `[staff]`


### Voices `<voice>`


#### Backup `<backup>`, `[backup]`


#### Forward `<forward>`, `[forward]`


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
[measure] = "measure" # ...TODO

# ... TODO ...

#
[note] = (
    [grace]?
    [chord]?
    ([rest] | [pitch])
    [type]  # this is the ROOT of a [note], must be present, is used for parsing
    [dot]*
    [accidental]?
    [stem]?
    [staff]?
    [beam]*
)

# possible accidentals
[accidental] =
    # the ususal ones
    | sharp
    | flat
    | natural
    # the weird ones from accidental overriding
    | double-sharp
    | flat-flat
    | natural-sharp
    | natural-flat
    # no microtonal music, this is enough
    # https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/accidental-value/

```




---

Remaining undocumented tokens:

backup
forward
dot
grace
measure
staff:1
staff:2
