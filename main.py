# main.py file
import os
from datetime import datetime, timedelta

import requests

URL = '' # TODO place here the api url
DIRNAME = os.path.dirname(__file__)

print('Extracting data from {}...'.format(URL))


def changeFilerPermissions(filePath):
    # Remove read only permissions
    os.system('chmod -R 777 {}'.format(filePath))


def downloadFileFromUlr(url, fileName):
    filePath = '{}/out/{}'.format(DIRNAME, fileName)
    with open(filePath, 'wb') as f:
        response = requests.get(url, stream=True)
        total_length = response.headers.get('content-length')

        if total_length is None:  # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                print('\r[{}{}]'.format('█' * done, ' ' * (50 - done)), end='')
    changeFilerPermissions(filePath)


def dictToCsv(dict, fileName):
    filePath = '{}/out/{}'.format(DIRNAME, fileName)
    with open(filePath, 'w') as f:
        for key, value in dict.items():
            f.write('{},{}\n'.format(key, value))
    changeFilerPermissions(filePath)


def convertToUrl(row):
    # Is row a dict?
    if isinstance(row, dict):
        # for each key in row
        for key in row:
            row[key] = convertToUrl(row[key])
        return row
    # Is row a string?
    elif isinstance(row, str):
        return URL + row


def downloadFiles(row, path, attrName):
    # Is row a dict?
    if isinstance(row, dict):
        # for each key in row
        for key in row:
            downloadFiles(row[key], path, '{}_{}'.format(attrName, key))
        return row
    # Is row a string?
    elif isinstance(row, str):
        downloadFileFromUlr(URL + row, '{}/{}_{}'.format(path, attrName, row.split('/')[-1]))


def askForDateRange():
    print('Please enter the date range you want to download in the format YYYY-MM-DD')
    startDate = input('Start date: ')
    endDate = input('End date: ')
    return startDate, endDate


# create folder if not exists
if not os.path.exists('{}/out/'.format(DIRNAME)):
    os.makedirs('{}/out/'.format(DIRNAME))

startDate, endDate = askForDateRange()
# String date to datetime.date
startDate = datetime.strptime(startDate, '%Y-%m-%d').date()
endDate = datetime.strptime(endDate, '%Y-%m-%d').date()
delta = timedelta(days=1)

while startDate <= endDate:
    url = '{}/api/exportarListadoDeSolicitudesDeBonos.php?date={}'.format(URL, startDate)
    print('\nDownlading data for {}... || {}'.format(startDate, url))

    # retrieving json from URL/api/exportarListadoDeSolicitudesDeBonos.php and save in variable
    response = requests.get(url)
    data = response.json()
    headers = data[0]
    data = data[1:]

    print('Downloading {} rows'.format(len(data)))

    for row in data:
        print('.', end='')
        row = dict(zip(headers, row))

        fileAttributes = [
            'dniAdjunto',
            'documentoDeReservaOriginal',
            'documentoFirmado',
            'documentoDeAprobacion',
            'documentosDeJustificacion'
            'documentoOrdenDeAprobacionDelPago',
            'documentoPoderesEmpresa',
            'documentoMinimisEmpresa',
        ]

        # create folder if not exists
        if not os.path.exists('{}/out/{}'.format(DIRNAME, row['id'])):
            os.makedirs('{}/out/{}'.format(DIRNAME, row['id']))

        for fileAttribute in fileAttributes:
            # Does row[fileAttribute] exists and is not empty?
            if fileAttribute in row and row[fileAttribute] is not None:
                downloadFiles(row[fileAttribute], '/{}'.format(row['id']), fileAttribute)
                row[fileAttribute] = convertToUrl(row[fileAttribute])

        # Create csv file with data
        dictToCsv(row, '{}/bonos_{}.csv'.format(row['id'], row['id']))

    startDate += delta
