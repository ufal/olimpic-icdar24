.PHONY: install-musescore install-open-score-lieder-dataset install-scanned-dataset install-synthetic-dataset

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

install-scanned-dataset:
	rm -rf datasets/scanned
	rm -rf datasets/scanned.tgz
	mkdir -p datasets/scanned
	wget https://github.com/Jirka-Mayer/ICDAR2024/releases/download/datasets/2024-02-07_scanned.tgz
	mv 2024-02-07_scanned.tgz datasets/scanned.tgz
	tar -xf datasets/scanned.tgz -C datasets/scanned

install-synthetic-dataset:
	rm -rf datasets/synthetic
	rm -rf datasets/synthetic.tgz
	mkdir -p datasets/synthetic
	wget https://github.com/Jirka-Mayer/ICDAR2024/releases/download/datasets/2024-02-07_synthetic.tgz
	mv 2024-02-07_synthetic.tgz datasets/synthetic.tgz
	tar -xf datasets/synthetic.tgz -C datasets/synthetic
