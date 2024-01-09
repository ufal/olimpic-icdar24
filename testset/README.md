# Evaluation test set

This folder contains the definition and collection of the OMR evaluation test set.

We want to take the [Lieder corpus](https://github.com/OpenScore/Lieder), take 10% of its scores, and download the associated PDF. These PDFs, sliced into per-piano staff images, together with MusicXML extracted from the corpus form the evaluation dataset.

In practise we took 140 scores, listed in `test_scores.yaml` and processed their corresponding PDFs and MusicXML files to build this evaluation dataset.


## Downloading the dataset from github releases page

We've already prepared this dataset folder, so you can download its final state by running this command:

```
TODO... this is not done yet
```


## Preparing the dataset from scratch

First, we need to select those 10% of scores. The corpus contains 1356 scores (as of 1st Jan 2024), we will randomly select 140 of them to form the test set (it is 10%, rounded up to a whole 10-multiple). This selection is performed by running the following script in this folder:

```
python3 select_scores.py
```

This produces the `test_scores.yaml` file, which lists all the selected scores in the same format, as the `data/scores.yaml` file in the Lieder corpus.

It also produces `imslp_files.tsv`, a file with URLs and IDs of the IMSLP PDF files needed to be downloaded. These need to be downloaded and saved into the `imslp_files` folder, with the file names as downloaded.

To download a file from IMSLP:

1. Open the link, e.g.: https://imslp.org/wiki/Special:ReverseLookup/09356
2. You might get multiple results, due to IMSPL's fuzzy search. Find the one that has the exact same id as you're looking for (`#09356` in this case).
    - The ID is displayed next to the file size, below the "Complete Score" title.
3. Can click on that ID (it's a link) or on the thumbnail image to open the detail of the PDF file (both methods take you to the same page, in our case: https://imslp.org/wiki/File:Mendelssohn_-_Op.86_-_6_Songs.pdf).
4. On the PDF detail page, click on the large image. This takes you to the download countdown page. Once the countdown finishes, you can click the link. "Click here to continue your download"
5. You are taken to a site, where the PDF is displayed (or downloaded, depending on your browser). For me it's this page: https://vmirror.imslp.org/files/imglnks/usimg/3/39/IMSLP09356-Mendelssohn_-_Op.86_-_6_Songs.pdf
6. Write down these "download URLs" so that we can provide them for automatic download in the future. The ID can be extracted from the URL, so you don't need to keep track of the ID pairing. You can paste these URLs directly into the `imslp_download_urls.txt` file.
7. Download the PDF file (Ctrl + S in your browser) into the `imslp_files` folder.
