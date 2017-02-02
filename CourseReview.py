import csv
import re
import os
import time
import delta_report
import courseExportCheck


def findLatestExport(courseExportDir):
    exportFiles = os.listdir(courseExportDir)
    exportList = []
    for csv in exportFiles:
        if 'export' in csv:
            csvDate = csv.split('_')
            exportList.append(csvDate[-1])
    sortedList = sorted(exportList, reverse=True)

    for csv_r in exportFiles:
        if "_export_{}".format(sortedList[0]) in csv_r:
            print(sortedList[0])
            return os.path.join(courseExportDir, csv_r)
        else:
            return print('Previous export cannot be found.')


def main():
    fname = input("Enter the file name of the course export you'd like to check: ")

    workingDir = os.getcwd()
    courseExportDir = os.path.join(workingDir, fname.rstrip('.csv'))


    if os.path.exists(courseExportDir) is True:
        delta = input('Would you like to run a delta check on this course export? [Y] or [N]:')
        if delta == 'Y':
            try:
                latestExport = findLatestExport(courseExportDir)
            except:
                print('A previous export cannot be found.')

            delta_report.main(fname, latestExport, courseExportDir)

    if os.path.exists(courseExportDir) is False:
        os.mkdir(courseExportDir)

    currentTime = time.gmtime()
    finalTime = str(currentTime[0])+str(currentTime[1])+str(currentTime[2])+str(currentTime[3])+str(currentTime[4])

    courseExportCheck.main(fname, courseExportDir, finalTime)
    os.rename(os.path.join(os.getcwd(), fname), os.path.join(courseExportDir, "{}_export_{}.csv".format(fname.rstrip('.csv'), finalTime)))

if __name__ == '__main__':
    main()
