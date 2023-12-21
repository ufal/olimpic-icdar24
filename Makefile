.PHONY: install-lilypond

install-lilypond:
	rm -rf lilypond
	wget https://gitlab.com/lilypond/lilypond/-/releases/v2.24.3/downloads/lilypond-2.24.3-linux-x86_64.tar.gz
	tar -xf lilypond-2.24.3-linux-x86_64.tar.gz
	mv lilypond-2.24.3 lilypond
	rm lilypond-2.24.3-linux-x86_64.tar.gz
