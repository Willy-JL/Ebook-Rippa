import os
import glob
from fpdf import FPDF
from PIL import Image


def makePdf(pdfFileName, listPages):
    cover = Image.open(str(listPages[0]) + '.png')
    width, height = cover.size
    print(f'Identified page sizing: {width}x{height}')

    pdf = FPDF(unit='pt', format=[width, height])

    for j, page in enumerate(listPages):
        name = str(page) + '.png'
        pdf.add_page()
        pdf.image(name, 0, 0)
        print(f'Added file \"{name}\", page number {j+1}')

    print('Saving output PDF...')
    pdf.output(pdfFileName + '.pdf', 'F')


if __name__ == '__main__':
    pngList = glob.glob('*.png')
    for i, file in enumerate(pngList):
        pngList[i] = int(file[:-4])
    pngList = sorted(pngList)
    print(f'Found {len(pngList)} images to process...')
    dirName = os.path.dirname(os.path.realpath(__file__))[os.path.dirname(os.path.realpath(__file__)).rfind('\\')+1:]
    print(f'Starting to compile \"{dirName}.pdf\"')
    makePdf(dirName, pngList)
    input('All Done!')
