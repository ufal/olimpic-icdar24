.PHONY: install-musescore install-open-score-lieder

install-musescore:
	rm -rf musescore
	mkdir -p musescore
	wget https://github.com/musescore/MuseScore/releases/download/v3.6.2/MuseScore-3.6.2.548021370-x86_64.AppImage
	mv MuseScore-3.6.2.548021370-x86_64.AppImage musescore/musescore.AppImage
	chmod +x musescore/musescore.AppImage

install-open-score-lieder:
	rm -rf datasets/OpenScore-Lieder
	mkdir -p datasets
	wget https://github.com/apacha/OMR-Datasets/releases/download/datasets/OpenScore-Lieder-Snapshot-2023-10-30.zip
	unzip OpenScore-Lieder-Snapshot-2023-10-30.zip
	mv Lieder-main datasets/OpenScore-Lieder
	rm OpenScore-Lieder-Snapshot-2023-10-30.zip


.PHONY: install-olimpic-synthetic install-olimpic-scanned install-grandstaff-lmx

install-olimpic-synthetic:
	rm -rf datasets/synthetic
	rm -rf datasets/olimpic-1.0-synthetic.2024-02-12.tar.gz
	wget https://github.com/ufal/olimpic-icdar24/releases/download/datasets/olimpic-1.0-synthetic.2024-02-12.tar.gz
	mv olimpic-1.0-synthetic.2024-02-12.tar.gz datasets/olimpic-1.0-synthetic.tgz
	cd datasets && tar -xf olimpic-1.0-synthetic.tgz
	mv datasets/olimpic-1.0-synthetic datasets/synthetic

install-olimpic-scanned:
	rm -rf datasets/scanned
	rm -rf datasets/olimpic-1.0-scanned.2024-02-12.tar.gz
	wget https://github.com/ufal/olimpic-icdar24/releases/download/datasets/olimpic-1.0-scanned.2024-02-12.tar.gz
	mv olimpic-1.0-scanned.2024-02-12.tar.gz datasets/olimpic-1.0-scanned.tgz
	cd datasets && tar -xf olimpic-1.0-scanned.tgz
	mv datasets/olimpic-1.0-scanned datasets/scanned

install-grandstaff-lmx:
	rm -rf datasets/grandstaff
	rm -rf datasets/grandstaff-lmx.2024-02-12.tar.gz
	rm -rf datasets/grandstaff.tgz
	wget https://github.com/ufal/olimpic-icdar24/releases/download/datasets/grandstaff-lmx.2024-02-12.tar.gz
	mv grandstaff-lmx.2024-02-12.tar.gz datasets/grandstaff-lmx.tar.gz
	cd datasets && tar -xf grandstaff-lmx.tar.gz
	mv datasets/grandstaff-lmx datasets/grandstaff
	wget https://grfia.dlsi.ua.es/musicdocs/grandstaff.tgz
	mv grandstaff.tgz datasets/grandstaff.tgz
	tar -xf datasets/grandstaff.tgz -C datasets/grandstaff
	rm -rf datasets/grandstaff/LICENSE
