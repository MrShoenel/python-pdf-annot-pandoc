"""
This application extracts and collects annotations (comments) and the textual content
from PDF files within a directory. It outputs a Markdown-formatted document with all
annotations. It also supports Pandoc for conversion of the Markdown into a more structured
format, such as HTML or PDF.

This is the main entry point for this application. You can pass command-line switches
to to select a directory, output-format, whether to also extract text, etc.
"""

from argparse import ArgumentParser
from pathlib import Path
from lib.helpers import print_green, print_red, print_yellow, ProcessedPdf
from lib.extractor import Extractor
from lib.markdown import MarkdownWithToc
from joblib import Parallel, delayed
from pypandoc import convert_file


parser = ArgumentParser()
parser.add_argument('-d', '--dir', dest='dir', help='The Directory containing PDF files', required=True, type=str)
parser.add_argument('-o', '--output', dest='output', help='The name of the output-file. Defaults to \'__Generated-Annotations.md\'.', type=str, required=False, default='__Generated-Annotations.md')
parser.add_argument('-f', '--format', dest='format', help='The output format. Can be any that is supported by Pandoc. Defaults to \'markdown\'.', default='markdown', type=str)
parser.add_argument('-j', '--jobs', dest='jobs', help='Number of jobs for reading and processing PDFs in parallel. Defaults to -1 (no limit).', type=int, default=-1)
parser.add_argument('-t', '--text', dest='text', help='If present, will also extract each PDF\'s text and save it along the original file with the extension .txt.', action='store_true')

args = parser.parse_args()


dir = Path(args.dir).resolve()
print_yellow('Reading PDF files from: ', str(dir))

pdfs = sorted(dir.glob(pattern='*.pdf'))
print_yellow('\nFound a total of ', f'{len(pdfs)} PDFs:')
for pdf in pdfs:
    print_green(' `- ', pdf.name)


def processPdf(file: Path, print_width: int=60) -> None|ProcessedPdf:
    try:
        ex = Extractor(pdf_file=file)
        annots = list(ex.annotations)
        text_file = file.parent.joinpath(f'./__text/{file.stem}.txt').resolve()
        
        text: str|None = None
        if args.text and not text_file.exists():
            text_file.parent.mkdir(exist_ok=True)
            text = ' '.join(ex.text).strip()
            # Remove non-utf8 characters.
            text = bytes(text, 'raw_unicode_escape').decode('utf-8', 'ignore')
            
            with open(file=text_file, mode='w', encoding='utf-8') as fp:
                fp.write(text)
        
        fname = file.name if len(file.name) < print_width else f'{file.stem[:(print_width - 8)]}...{file.suffix}'
        print_green(f'Finished: {f"{fname},".ljust(print_width)} ', f'found {len(annots)} annotations in file.')
        return ProcessedPdf(pdf_file=file, annotations=annots, text=text)
    except Exception as ex:
        print_red('Failed processing PDF: ', ex)
        return None


print_yellow('\nStarting to process PDF files ...', '')
para = Parallel(n_jobs=args.jobs)
procPdfs = list(para(delayed(processPdf)(pdf) for pdf in pdfs))


######### Let's make the Markdown!
to_pdf = args.format == 'pdf'
markdown = MarkdownWithToc().add_all_processed(procPdfs=procPdfs)
document = markdown.generate_document(generate_md_toc=not to_pdf)

markdown_file = dir.joinpath(f'./{args.output}').resolve()
with open(file=markdown_file, mode='w', encoding='utf-8') as fp:
    fp.write(document)


if args.format != 'markdown':
    output_file = markdown_file.parent.joinpath(f'./{markdown_file.stem}.{args.format}')
    convert_file(source_file=markdown_file, to=args.format, outputfile=output_file, extra_args=['--toc', '--toc-depth=2', '-V toc-title:"Table Of Contents"'])
