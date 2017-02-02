import csv
import re
import time
import os

class CourseExportCheck:
    def __init__(self):
        self.courseErrors = []
        self.assetName = None
        self.descriptor = None
        self.cpLocation = None
        self.fileType = None

    def errorLogging(self, aName, csvName, desc, cpLoc, error, filetype):
        aName = {'Name': csvName, 'Descriptor': desc, "Content Plan Location": cpLoc, "Error": error, 'Filetype': filetype}
        return aName

    def testCondition(self, rowToReview, metadataType, toCheck, condition, errorCode, exclude = 0, notIn = 0):
#Changing the exclude value from 0 to 1 allows you to test whether the metadata in each row is either
#equal to or not equal to the metadatatype. Changing notIn to 1 or -1 allows you to test the condition
# as either not in the value to check or not equal the value to check, respectively.
        errorTitle = errorCode.split('_')
        if exclude == 0 and notIn == 1:
            if rowToReview == metadataType:
                if condition not in toCheck:
                    self.courseErrorAddition(errorCode, errorTitle[1])
        elif exclude == 0 and notIn == 0:
            if rowToReview == metadataType:
                if condition != toCheck:
                    self.courseErrorAddition(errorCode, errorTitle[1])
        elif exclude == 0 and notIn == -1:
            if rowToReview == metadataType:
                if condition == toCheck:
                    self.courseErrorAddition(errorCode, errorTitle[1])
        elif exclude == 1 and notIn == 1:
            if rowToReview != metadataType:
                if condition not in toCheck:
                    self.courseErrorAddition(errorCode, errorTitle[1])
        elif exclude == 1 and notIn == 0:
            if rowToReview != metadataType:
                if condition != toCheck:
                    self.courseErrorAddition(errorCode, errorTitle[1])
        elif exclude == 1 and notIn == -1:
            if rowToReview != metadataType:
                if condition == toCheck:
                    self.courseErrorAddition(errorCode, errorTitle[1])

    def courseErrorAddition(self, errorCoding, errorTitling):
        self.courseErrors.append(self.errorLogging((self.assetName + errorCoding), self.assetName,
        self.descriptor, self.cpLocation, errorTitling, self.fileType))

    def updateAttr(self, assetN, descrip, cpLoca, fileType):
        self.assetName = assetN
        self.descriptor = descrip
        self.cpLocation = cpLoca
        self.fileType = fileType

class ErrorWriting:
    def __init__(self):
        self.error = None
        self.name = None
        self.filetype = None
        self.descriptor = None
        self.ContentPlanLocation = None
        self.writer = None

    def updateErrorAttributes(self, writer, error, name, filetype, descriptor, ContentPlanLocation):
        self.writer = writer
        self.error = error
        self.name = name
        self.filetype = filetype
        self.descriptor = descriptor
        self.ContentPlanLocation = ContentPlanLocation

    def errorOutput(self, errorDict, errorMessage):
        if self.error == errorDict:
            self.writer.writerow({"Error": errorMessage,'Name': self.name, "Filetype": self.filetype,
            "Descriptor": self.descriptor, "Content Plan Location": self.ContentPlanLocation})


def main(currentExportcsv, courseExportDir, finalTime):

    descriptor = 'Descriptor'
    mediaType = 'Mediatype'
    contentType = 'Contenttype'
    downRestr = 'Download Restrictions'
    url = 'Url'
    hideFromSt = 'Hide From Student'
    thumb = '2x Thumbnail'

    newCourseExport = CourseExportCheck()

    with open(currentExportcsv) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row[mediaType] == 'Learning Model': continue
            assetName = row['Name']
            cpLocation = re.findall(':(.*)', row['Index Code'])
            cpLocation = "".join(cpLocation)
            newCourseExport.updateAttr(assetName, row[descriptor], cpLocation, row['Filetype'])
            newCourseExport.testCondition(row[mediaType], 'Document', row[downRestr], 'Stream/View/Download', '_docFail')
            newCourseExport.testCondition(row[contentType], 'Assessment',row[hideFromSt], 'TRUE', '_assessFail')
            newCourseExport.testCondition(row[contentType], 'Sequence', row[url], "", '_fileLocFail', exclude = 1, notIn = -1)
            newCourseExport.testCondition(row[contentType], 'Sequence', row[url], 'http', '_fileLocFail', exclude = 1, notIn = 1)
            newCourseExport.testCondition(row[contentType], 'Sequence', row[thumb], "", '_thumbnailFail', exclude = 1, notIn = -1)

    courseErrorsFname = os.path.join(courseExportDir, '{}_Course_errors_{}.csv'.format(currentExportcsv.rstrip('.csv'), finalTime))
    courseErrorWriter = ErrorWriting()

    with open(courseErrorsFname, 'w') as output:
        writer = csv.DictWriter(output, fieldnames=['Error', 'Name', 'Filetype','Descriptor', 'Content Plan Location'])
        writer.writeheader()
        for item in newCourseExport.courseErrors:
            courseErrorWriter.updateErrorAttributes(writer, item['Error'], item['Name'], item['Filetype'], item['Descriptor'], item['Content Plan Location'])
            courseErrorWriter.errorOutput('docFail', "Document not set as stream/view/download.")
            courseErrorWriter.errorOutput('assessFail', "Assessment not set as hide from student = True")
            courseErrorWriter.errorOutput('fileLocFail', "There is no file location for this asset.")
            courseErrorWriter.errorOutput('thumbnailFail', "There are missing thumbnails for this asset.")
        #errorOutput('filenameFail', "There might be a question mark in the filename for this asset.")

if __name__ == '__main__':
    currentTime = time.gmtime()
    finalTime = str(currentTime[0])+str(currentTime[1])+str(currentTime[2])+str(currentTime[3])+str(currentTime[4])
    main(input('Enter the course export you would like to check: '), os.getcwd(), finalTime)
