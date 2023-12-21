\version "2.22.1"

\absolute {
    \clef C \time 4/4
    
    % <cis' d>^>^( e) \bar "|" a'1^2024^> \bar "||" f4 g'4 a'4

    c'4 << { e'4 r4 } \\ { c'2 } >> c'4 |
    
    << { c'2 } \\ { e4 c'4 } >> r2 |

    <e' c'>4 <<{ c'4 }\\{ a4 }>> r2 |

    \clef F \time 3/4
    <<
        { r4 b2 }
    \\
        { g2. }
    \\
        { s4 r4 d'4 }
    >>
}
