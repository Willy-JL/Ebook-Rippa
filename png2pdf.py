from PIL import Image
from fpdf import FPDF
import glob
import sys
import os


def make_pdf(output_filename, img_list):
    cover = Image.open(str(img_list[0]) + '.png')
    width, height = cover.size
    print(f'Identified page sizing: {width}x{height}')

    pdf = FPDF(unit='pt', format=[width, height])

    for j, page in enumerate(img_list):
        name = str(page) + '.png'
        pdf.add_page()
        pdf.image(name, 0, 0)
        print(f'Added file \"{name}\", page number {j+1}')

    print('Saving output PDF...')
    pdf.output(output_filename, 'F')


if __name__ == '__main__':
    png_list = glob.glob('*.png')
    for i, filename in enumerate(png_list):
        png_list[i] = int(filename[:-4])
    png_list = sorted(png_list)
    print(f'Found {len(png_list)} images to process...')
    script_path = os.path.realpath(__file__)
    parent_folder = os.path.dirname(script_path)
    os.chdir(parent_folder)
    parent_folder = parent_folder.replace("\\", "/")
    pdf_filename = parent_folder[parent_folder.rfind("/")+1:] + ".pdf"
    print(f'Starting to compile \"{pdf_filename}\"')
    make_pdf(pdf_filename, png_list)
    input('All Done!')
