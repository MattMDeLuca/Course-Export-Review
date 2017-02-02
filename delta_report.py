import csv
import re
import os

def main(cExport, pExport, currDirectory):
    preExportDict = {}
    currExportDict = {}
    errorDict = {}
    preExport = pExport
    print("previous export", preExport)
    currExport = cExport
    print("current export", currExport)
    courseName = None
    with open(preExport) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row[reader.fieldnames[0]] == 'TRUE': courseName = row['Name']
            preExportDict[row['External Id']] = {}
            for k, v in row.items():
                preExportDict[row['External Id']][k] = v
    with open(currExport) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            currExportDict[row['External Id']] = {}
            for k, v in row.items():
                currExportDict[row['External Id']][k] = v
    print(len(preExportDict), len(currExportDict))
    for k, v in preExportDict.items():
        try:
            currentExportData = currExportDict[k]
        except:
            errorDict[k] = {'External Id': (k, 'Not found in current export')}
            continue
        if v == currentExportData: continue
        for key, value in v.items():
            if currentExportData[key] != value:
                errorDict[k] = {key: (value, currentExportData[key])}

    for key in currExportDict.keys():
        if key not in preExportDict.keys():
            errorDict[key] = {key: (None, 'Added since last export')}

    fileName = os.path.join(currDirectory, '{}_delta_report.csv'.format(courseName))

    with open(fileName, 'w') as csvWriteFile:
        writer = csv.DictWriter(csvWriteFile, fieldnames=['Error', 'Name', 'External Id', 'Index Code','Previous Value', 'Current Value'])
        writer.writeheader()
        for k, v in errorDict.items():
            try:
                currIndexCode = currExportDict[k]['Index Code']
                lsIndexCode = re.findall(':(.*)', currIndexCode)
                printableIndexCode = "".join(lsIndexCode)
            except:
                currIndexCode = preExportDict[k]['Index Code']
                lsIndexCode = re.findall(':(.*)', currIndexCode)
                printableIndexCode = "".join(lsIndexCode)
            for key, value in v.items():
                try:
                    if value[0] is None:
                        writer.writerow({'Error': value[1], 'Name':currExportDict[k]['Name'],'External Id': k, 'Index Code': printableIndexCode, 'Previous Value': value[0], 'Current Value': value[0]})
                        continue
                    writer.writerow({'Error': "{} doesn't match".format(key), 'Name':currExportDict[k]['Name'],'External Id': k, 'Index Code': printableIndexCode, 'Previous Value': value[0], 'Current Value': value[1]})
                except:
                    writer.writerow({'Error': "{} doesn't match".format(key), 'Name':preExportDict[k]['Name'],'External Id': k, 'Index Code': printableIndexCode, 'Previous Value': value[0], 'Current Value': value[1]})


if __name__ == '__main__':
    main(input('Enter filename of previous export:'),input('Enter filename of your current export:'), os.getcwd())
