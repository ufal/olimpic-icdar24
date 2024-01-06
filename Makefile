.PHONY: install-lilypond install-musescore install-open-score-lieder-dataset

install-lilypond:
	rm -rf lilypond
	wget https://gitlab.com/lilypond/lilypond/-/releases/v2.24.3/downloads/lilypond-2.24.3-linux-x86_64.tar.gz
	tar -xf lilypond-2.24.3-linux-x86_64.tar.gz
	mv lilypond-2.24.3 lilypond
	rm lilypond-2.24.3-linux-x86_64.tar.gz

install-musescore:
	rm -rf musescore
	mkdir -p musescore
	wget https://github.com/musescore/MuseScore/releases/download/v3.6.2/MuseScore-3.6.2.548021370-x86_64.AppImage
	mv MuseScore-3.6.2.548021370-x86_64.AppImage musescore/musescore.AppImage
	chmod +x musescore/musescore.AppImage

install-open-score-lieder-dataset:
	rm -rf datasets/OpenScore-Lieder
	mkdir -p datasets
	wget https://github.com/apacha/OMR-Datasets/releases/download/datasets/OpenScore-Lieder-Snapshot-2023-10-30.zip
	unzip OpenScore-Lieder-Snapshot-2023-10-30.zip
	mv Lieder-main datasets/OpenScore-Lieder
	rm OpenScore-Lieder-Snapshot-2023-10-30.zip

prepare-lieder-svg-and-mxl-files:
	.venv/bin/python3 -c 'from app.datasets.prepare_open_score_lieder import prepare_open_score_lieder; prepare_open_score_lieder()'
