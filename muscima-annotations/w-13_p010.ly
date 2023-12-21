\version "2.20.0"

SU = \once \stemUp
SD = \once \stemDown

UP_STAFF = \change Staff = "up"
DOWN_STAFF = \change Staff = "down"

MUSIC = {
  <<{ \UP_STAFF \oneVoice % START

    \stemUp c''4 c''4 c''4 c''4~
  }\\{ \oneVoice % -------------- [jump]
    \stemDown e'4 e'4 e'4 e'4~
  }\\{ \DOWN_STAFF \oneVoice % -- [STAFF JUMP]
    \stemDown g4 g4 g4 b,4~ % TODO: ties break for the lower staff...
  
  }>> | <<{ \UP_STAFF \oneVoice % NEXT MEASURE

    \stemUp c''4 c''4 g''4 g''4
  }\\{ \oneVoice % -------------- [jump]
    \stemDown e'4 e'4 e'4 e'4
  }\\{ \DOWN_STAFF \oneVoice % -- [STAFF JUMP]
    \stemDown b,4 b,4 r2
  
  }>> % END
}

\new PianoStaff <<
  \new Staff = "up" { \clef G \MUSIC }
  \new Staff = "down" { \clef F }
>>









% DOWN = \change Staff = "down"

% \parallelMusic voiceA,voiceB,voiceC {
%   % Bar 1
%   r8 g'16 c'' e'' g' c'' e'' r8 g'16 c'' e'' g' c'' e''  |
%   r16 e'8.~ 4        r16 e'8.~  4        |
%   c'2                c                   |

%   % Bar 2
%   e''1 |
%   g'8[ c'8 \DOWN \stemUp e8 d8] s2 \change Staff = "up" |
%   r1 |

%   % Bar 3
%   e''1 |
%   e'1 |
%   e1 |
% }

% \new PianoStaff <<
%   \new Staff = "up" << \voiceA \\ \voiceB >>
%   \new Staff = "down" { \clef bass \voiceC }
% >>