import logging

import azure.functions as func
import os
from azure.storage.blob import ContainerClient
import shutil
import json
from pdf_annotate import PdfAnnotator, Location, Appearance
import tempfile
from PyPDF2 import PdfWriter, PdfReader
from pdf2image import convert_from_path
import fitz


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    storage_account_name = os.getenv('STORAGE_ACCOUNT_NAME', 'afrdemostorage')
    storage_account_key = os.getenv('STORAGE_ACCOUNT_KEY', 'YOUR-STORAGE-KEY')
    storage_account_container = os.getenv('STORAGE_ACCOUNT_CONTAINER', 'testing')
    annotation_container = os.getenv('ANNOTATION_CONTAINER', 'annotations')

    data = json.loads(req.get_json()['data'])
    # data = (req.get_json()['data'])
    blob_name = req.get_json()['blob_name']

    max_height = data["boundingRegions"][0]['polygon'][7]
    max_width = data["boundingRegions"][0]['polygon'][2]

    data = data['fields']

    final_result = {}
    final_result['FILENAME'] = storage_account_container + '/' + blob_name

    container_client = ContainerClient(f'https://{storage_account_name}.blob.core.windows.net/', storage_account_container, credential=storage_account_key)
    blob_client = container_client.get_blob_client(blob_name)
    dir(blob_client)

    tempdir = tempfile.gettempdir()
    with open(f'{tempdir}/{blob_name}', 'wb') as file:
        file.write(blob_client.download_blob().readall())

    # UPDATE THIS LIST WITH THE NAMES OF EXPECTED FIELDS FROM YOUR CUSTOM AFR MODEL
    expected_fields = ['REQUESTED_DELIVERY_DATE', 'ACTUAL_DELIVERY_DATE', 'TANK_NUMBER', 'END_GALLONS']

    delivery_pdf = PdfAnnotator(f'{tempdir}/{blob_name}')

    for field in expected_fields:
        final_result[field] = ''
        try:
            final_result[field]=data[field]['valueString']
            regions = data[field]['boundingRegions']
            pts = []
            for reg in regions:
                page_num = reg['pageNumber']-1
                page_size = delivery_pdf.get_size(page_num)
                for i in range(0, len(reg['polygon']), 2):
                    pts.append([(((reg['polygon'][i] * page_size[0])/max_width)),(page_size[1]-((reg['polygon'][i+1]*page_size[1])/max_height))])
                delivery_pdf.add_annotation(
                    'polygon',
                    Location(points=pts, page=page_num),
                    Appearance(stroke_color=(1, 0, 0, 1), stroke_width=2),
                )
        except Exception as e:
            print(e)
            pass
        
    delivery_pdf.write(f'{tempdir}/{blob_name}'.replace('.pdf', '_ANNOTATED.pdf'))
    images = fitz.open(f'{tempdir}/{blob_name}'.replace('.pdf', '_ANNOTATED.pdf'))
    dpi = 300  # choose desired dpi here
    zoom = dpi / 72  # zoom factor, standard: 72 dpi
    magnify = fitz.Matrix(zoom, zoom)  # magnifies in x, resp. y direction
    for image in images:
        hold = image.get_pixmap(matrix=magnify)
        hold.save(f'{tempdir}/{blob_name}'.replace('.pdf', '_ANNOTATED.pdf').replace('.pdf', '.png'))

    # final_result['ANNOTATED_FILENAME'] = f'annotations/{blob_name}'.replace('.pdf', '_ANNOTATED.pdf').replace('.pdf', '.png')
    final_result['ANNOTATED_FILENAME'] = f'annotations/{blob_name}'.replace('.pdf', '_ANNOTATED.pdf')

    reader = PdfReader(f'{tempdir}/{blob_name}'.replace('.pdf', '_ANNOTATED.pdf'))

    for field in expected_fields:
        final_result[field+'_ANNOTATION'] = ''
        try:
            final_result[field]=data[field]['valueString']
            regions = data[field]['boundingRegions']
            pts = []
            for reg in regions:
                page_num = reg['pageNumber']-1
                page_size = delivery_pdf.get_size(page_num)
                reader = PdfReader(f'{tempdir}/{blob_name}'.replace('.pdf', '_ANNOTATED.pdf'))
                writer = PdfWriter()
                page = reader.pages[page_num]
                xs = []
                ys = []
                for i in range(len(reg['polygon'])):
                    if i % 2:
                        ys.append(reg['polygon'][i])
                    else :
                        xs.append(reg['polygon'][i])
                min_x = (min(xs) * (page_size[0]/max_width))-125
                max_x = (max(xs) * (page_size[0]/max_width))+125
                min_y = page_size[1]-(min(ys) * (page_size[1]/max_height))-125
                max_y = page_size[1]-(max(ys) * (page_size[1]/max_height))+125
                
                page.cropbox.upper_left = (max_x, max_y)
                page.cropbox.lower_right = (min_x, min_y)
                
                writer.add_page(page)
                with open(f'{tempdir}/{blob_name}'.replace('.pdf', f'_{field}.pdf').replace('.pdf', '_ANNOTATED.pdf'), 'wb') as file:
                    writer.write(file)
                
                final_result[field+'_ANNOTATION'] = f'annotations/{blob_name}'.replace('.pdf', f'_{field}.pdf').replace('.pdf', '_ANNOTATED.pdf').replace('.pdf', '.png')
                
                images = fitz.open(f'{tempdir}/{blob_name}'.replace('.pdf', f'_{field}.pdf').replace('.pdf', '_ANNOTATED.pdf'))
                dpi = 300  # choose desired dpi here
                zoom = dpi / 72  # zoom factor, standard: 72 dpi
                magnify = fitz.Matrix(zoom, zoom)  # magnifies in x, resp. y direction
                for image in images:
                    hold = image.get_pixmap(matrix=magnify)
                    hold.save(f'{tempdir}/{blob_name}'.replace('.pdf', f'_{field}.pdf').replace('.pdf', '_ANNOTATED.pdf').replace('.pdf', '.png'))
                    break

                print(min_x)
        except Exception as e:
            print(e)
            pass
        

    container_client = ContainerClient(f'https://{storage_account_name}.blob.core.windows.net/', annotation_container, credential=storage_account_key)

    files = os.listdir(f'{tempdir}')
    for file in files:
        if '.png' in file:
            data = open(f'{tempdir}/{file}', 'rb').read()
            container_client.upload_blob(file, data, overwrite=True)
        if '_ANNOTATED.pdf' in file:
            data = open(f'{tempdir}/{file}', 'rb').read()
            container_client.upload_blob(file, data, overwrite=True)

    logging.info(final_result)

    return func.HttpResponse(json.dumps(final_result), status_code=200)
 
