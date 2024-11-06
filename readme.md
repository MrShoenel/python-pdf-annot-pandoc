# Python PDF Annotations Processor using Pandoc

This application does the following things:

* Read in all PDFs in a directory.
* Parse their annotations: For each PDF, it generates a list of comments/annotations (highlights without text are ignored).
* Extra: Extract all text from each PDF and save a separate `.txt`-file with same name.
* Create markdown document with a directory of all PDFs that have or don't have annotations.
    * For each PDF, there is an entry in the TOC.
    * For each PDF, there is a section you can jump to. The section then has all comments/annotations ordered by page.
    * It supports Mathjax so you can make Latex-style annotations.
* The markdown is then converted to HTML or PDF.


# Purpose

Simple: I read a lot of papers and make comments. Sometimes it's hard to remember where I made a comment, but often I do remember at least a keyword. I can then go to the markdown/HTML summary and quickly search there across **all** PDFs and their comments simultaneously.

This program also extracts the textual content of each PDF.
The purpose here is simple, too: Sometimes I remember having read something specific, but I am not sure where exactly.
But then I can go into the directory with all the text-files, run VSCode, and press `ctrl+shift+f` to find **across** all files.
That allows me to quickly find the documents I had in mind.

Also, the TOC is split between papers that I have read and made comments in and those which I have not yet read.


# How to use?

This application is a command line application written in Python.
It is best to use `conda` and to recreate the environment:

```shell
conda env create -f environment.yml
```

This creates the environment `pdf`.
Then, you can run the program like this:

```shell
# First, activate the environment:
conda activate pdf

# Run the app:
python annotate.py
```

There are a number of command line arguments.
One is **mandatory**: `-d`/`--dir`: The path to the directory that contains the PDFs.

```shell
(pdf) C:\mrsh_python-pdf-annot-pandoc>python annotate.py --help
usage: annotate.py [-h] -d DIR [-o OUTPUT] [-f FORMAT] [-j JOBS] [-t]

options:
  -h, --help            show this help message and exit
  -d DIR, --dir DIR     The Directory containing PDF files
  -o OUTPUT, --output OUTPUT
                        The name of the output-file. Defaults to '__Generated-Annotations.md'.
  -f FORMAT, --format FORMAT
                        The output format. Can be any that is supported by Pandoc. Defaults to 'markdown'.
  -j JOBS, --jobs JOBS  Number of jobs for reading and processing PDFs in parallel. Defaults to -1 (no limit).
  -t, --text            If present, will also extract each PDF's text and save it along the original file with the extension .txt.
```