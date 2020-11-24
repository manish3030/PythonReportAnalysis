"""Purpose of this file is to get the report unzipped from any location
    and read it into a file and send it back
    If successfully read, file contents are returned
    else None is returned"""

import os
import zipfile


class IdisReport:
    # ******************************************************************************************************************
    """Class constructor"""

    def __init__(self):
        self._latestReport = False
        self._path = None
        self._reportName = None
        self._fileExtracted = False

    # ******************************************************************************************************************
    """Get the path from the user or use the current path directory"""

    def getPath(self):
        count = 0
        retVal = True
        while count < 3:
            print("Enter (Y) for current directory and (N) to enter a path")
            inp = str(input()).upper()
            if inp == "Y":
                self._path = os.getcwd()
                break
            elif inp == "N":
                print("Enter the path")
                self._path = str(input())
                if os.path.exists(self._path):
                    break
                else:
                    print("Invalid path, try again")
                    count = count + 1
            else:
                count = count + 1
                print("Invalid Choice, please enter again")
        else:
            print("Max retires reached, exiting application....")
            retVal = False
        return retVal

    # ******************************************************************************************************************
    """Get the report name or pick the latest report"""

    def getReportName(self):
        retVal = True
        count = 0
        while count < 3:
            print("Enter (Y) for latest report and (N) to enter a report name")
            inp = str(input()).upper()
            if inp == "Y":
                self._latestReport = True
                break
            elif inp == "N":
                print("Enter the path")
                self._reportName = str(input())
                # TODO: This might be case sensitive, need to change that
                if os.path.exists(os.path.join(self._path, self._reportName)):
                    print("Invalid file Name, try again")
                    count = count + 1
                break
            else:
                count = count + 1
                print("Invalid Choice, please enter again")
        else:
            print("Max retires reached, exiting application....")
            retVal = False
        return retVal

    # ******************************************************************************************************************
    """Get the report from the zip file in text form"""

    def getReport(self, filenames):
        if self._latestReport:
            self._reportName = self.getLatestZipFile()
        if self._reportName:
            self.unZipFile(filenames)
        return self._fileExtracted

    # ******************************************************************************************************************
    """Get the latest zip file from the filr path"""

    def getLatestZipFile(self):
        PathOfFiles, zipFile = [], None
        for file in os.listdir(self._path):
            if file.endswith(".zip"):
                PathOfFiles.append(os.path.join(self._path, file))

        if len(PathOfFiles) > 0:
            newestFilePath = max(PathOfFiles, key=os.path.getmtime)
            path, zipFile = os.path.split(newestFilePath)
        else:
            print("File not found")
        return zipFile

    # ******************************************************************************************************************
    """Unzip the to extract the contents"""

    def unZipFile(self, filenames):
        with zipfile.ZipFile(self._reportName, "r") as myZip:
            try:
                myZip.extract(filenames.get("REPORT_NAME"), os.getcwd())
                self._fileExtracted = True
                # if os.path.exists("Report.txt"):
                #     os.remove("Report.txt")
                # os.rename(REPORTNAME, "Report.txt")
                myZip.close()
            except NotImplementedError:
                print("The type of Zip is not implemented")
            except ValueError:
                print("Close Zip File")
            except:
                print("Something went wrong")


# **********************************************************************************************************************
""" Get the IDIS report from the ZIP files in an appropriate form"""


def getIDISReport(filenames):
    reportObj = IdisReport()
    if reportObj.getPath():
        if reportObj.getReportName():
            return reportObj.getReport(filenames)

# **********************************************************************************************************************
