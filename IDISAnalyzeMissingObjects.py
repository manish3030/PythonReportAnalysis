"""Purpose of this file is to analyze and get the missing object information
    from the IDIS report and then find the reason for the missing objects
    and publish them in a file"""

# *************************************IMPORTED PACKAGES****************************************************************

import pandas as pd
import numpy as np
import re
import xml.etree.ElementTree as ET

# *************************************PANDAS OPTIONS*******************************************************************

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 15)

# *************************************DataFrame Definitions************************************************************

dfMissingObjects = pd.DataFrame(columns=["Obis Code", " Class ID", " In Object List?", " In RBAC Object List?",
                                         " IDIS OM Status", " Picasso OM Status", " Conclusion"])
dfTotalMissingObjects = pd.DataFrame(index=["Total Missing Objects"])

# *************************************MACROS IN DICTIONARY*************************************************************
MissingObject_Text = {
    "MISSINGOBJECTLISTSTART": "is missing in Object-List",
    "OBJECTLISTEND": "Test Case 4",
    "PATTERN": "\n****************************************\n",
    "NOT_FOUND": "Value Not Found",
    "FOUND": "Value Found",
    "OPTIONAL": "Optional Object",
    "MANDATORY": "Mandatory Object",
    "MANDATORY_D": "Mandatory Disconnector",
    "MANDATORY_L": "Mandatory Load Management",
    "MANDATORY_M": "Mandatory MBUS",
    "MANDATORY_IP4": "Mandatory IPv4",
    "MANDATORY_IP6": "Mandatory IPv6",
    "MANDATORY_C": "Mandatory Consumer Interface",
    "DEVICE_TYPE": "IDISDeviceType",
    "PRODUCT_TYPE": "Type = '\Landis+Gyr"
}

Result_Text = {
    "DO_NOTHING": "Object is not required to be implemented on this product",
    "IMPLEMENT": "Object needs to be implemented in the firmware",
    "SGL_ISSUE": "Object is implemented in firmware, please update SGL",
    "OPTIONAL_ISSUE": "Check CTI File and remove the object from optional objects",
    "OPTIONAL_IMPLEMENT": "Either remove optional object from CTI or implement it",
    "OTHER": "There seems to be unknown error, please check configurations and files",
    "CHECK_OM": "Object Implemented while it is not in Picasso Object Model, Please check"
}


# ***********************************************CLASS OF THE FILE******************************************************


class IdisMissingObjects:
    # ******************************************************************************************************************
    """Class constructor"""

    def __init__(self):
        self.count = 0

    # ******************************************************************************************************************

    def getMissingObjects(self, filenames, dfIdisOm, dfPicassoOm):

        # Open files
        report, olissues, olnormal, olrbac, rootoln, rootolr = self.initializeMethod(filenames)

        # Start searching through the report
        line = report.readline()

        # While method used instead of for as this allows us to call the tell method on file later
        while line:
            # If missing object is found in object list
            if MissingObject_Text.get("MISSINGOBJECTLISTSTART") in line:
                obis, obisLN, classId = self.getObisCode(line)
                if obis and obisLN:
                    olnFound, olrFound = self.findMissingObisinObjectLists(obisLN, rootoln, rootolr)
                    idisOmStatus, picassoOmStatus = self.getObjectModelsStatus(dfIdisOm, dfPicassoOm, obis, classId,
                                                                               report)
                    finalOutcome, picassoOmStatus, idisOmStatus = self.evaluateResult(olnFound, olrFound, idisOmStatus,
                                                                                      picassoOmStatus)
                    self.appendResultInFile(obis, classId, olnFound, olrFound, idisOmStatus, picassoOmStatus,
                                            finalOutcome)
                    self.count = self.count + 1
            if MissingObject_Text.get("OBJECTLISTEND") in line:
                self.fillReport(olissues)
                break
            line = report.readline()
        report.close()
        olissues.close()
        olnormal.close()
        olrbac.close()

    # ******************************************************************************************************************

    @staticmethod
    def initializeMethod(filenames):
        report = open(filenames.get("REPORT_NAME"), "r")
        olissues = open(filenames.get("OBJECT_LIST_ISSUES"), "w")
        olnormal = open(filenames.get("OBJECT_LIST_XML"), "r")
        olrbac = open(filenames.get("OBJECT_LIST_RBAC_XML"), "r")

        # Seek to starting of the file
        report.seek(0)

        # Parse the xml files to get the root node
        tree = ET.parse(olnormal)
        rootoln = tree.getroot()
        tree = ET.parse(olrbac)
        rootolr = tree.getroot()
        return report, olissues, olnormal, olrbac, rootoln, rootolr

    # ******************************************************************************************************************

    def fillReport(self, olissues):
        global dfMissingObjects
        dfTotalMissingObjects.loc["Total Missing Objects", 0] = self.count
        olissues.write(MissingObject_Text.get("PATTERN"))
        olissues.write(dfTotalMissingObjects[0].to_string())
        olissues.write(MissingObject_Text.get("PATTERN"))
        olissues.write("\n")
        if self.count > 0:
            dfMissingObjects.index = np.arange(1, len(dfMissingObjects) + 1)
            olissues.write(str(dfMissingObjects))
            olissues.write("\n\n")

    # ******************************************************************************************************************

    @staticmethod
    def getObisCode(line):
        obis = obisLN = classId = None
        # Check for the obis code
        m1 = re.search(r'[0-9-:.]+', line)
        if m1:
            # Extract the Obis code in decimal format
            obis = m1.group()
            # Check for the class ID
            m2 = re.search(r"[|][0-9]+", line)
            if m2:
                # Remove the extra elements and get the obis in hex LN form
                obisLN = "".join(["{:02X}".format(int(i)) for i in re.split("\W", obis)])
                # Get class ID
                classId = m2.group().split("|")[1]

        return obis, obisLN, classId

    # ******************************************************************************************************************

    @staticmethod
    def findMissingObisinObjectLists(obisLN, rootoln, rootolr):
        olnFound = olrFound = MissingObject_Text.get("NOT_FOUND")

        for child in rootoln.iter("OctetString"):
            if child.attrib.get("Value") == obisLN:
                olnFound = MissingObject_Text.get("FOUND")
        for child in rootolr.iter("OctetString"):
            if child.attrib.get("Value") == obisLN:
                olrFound = MissingObject_Text.get("FOUND")

        return olnFound, olrFound

    # ******************************************************************************************************************

    def getObjectModelsStatus(self, dfIdisOm, dfPicassoOm, obis, classId, report):

        # Get the series of columns as True or False
        x1 = dfIdisOm["Obis/Default"] == obis
        x2 = dfIdisOm["ClassId"] == classId
        try:
            # Get the row with satisfies the column
            configType = self.getConfigType(report)
            idisOmStatus = dfIdisOm[x1 & x2][configType].iloc[0]
        except IndexError:
            # Continue execution by setting an error
            idisOmStatus = MissingObject_Text.get("NOT_FOUND")
            pass

        # Extract data frame with matching obis code
        x1 = dfPicassoOm[dfPicassoOm["Obis/Default"].isin([obis])]
        # Since there could be many such obis codes in object model, extract the class ID and make another column for it
        x1.insert(loc=0, column="ClassId", value=x1["Type/Class_Info"].str.extract(r'([0-9]+)'))
        x2 = x1["ClassId"] == classId
        try:
            # Get the row/ rows that satisfies the column
            prodType = self.getProductType(report)
            x3 = x1[x2][prodType]
            # Check if all rows are empty
            if x3[x3.iloc[0:].notnull()].empty:
                picassoOmStatus = np.NaN
            else:
                # Assuming only one row will be full and other empty for a product obis and class ID combo
                picassoOmStatus = x3[x3.iloc[0:].notnull()].iloc[0]
        except IndexError:
            # Continue execution by setting an error
            picassoOmStatus = MissingObject_Text.get("NOT_FOUND")
            pass
        return idisOmStatus, picassoOmStatus

    # ******************************************************************************************************************

    @staticmethod
    def getConfigType(report):
        # Store the pointer of file and move it to the beginning
        ptr = report.tell()
        report.seek(0)
        config = None
        for line in report:
            if MissingObject_Text.get("DEVICE_TYPE") in line:
                if re.search(r'[0-9]+', line) == 102:
                    config = "1Ph_Req"
                    break
                else:
                    config = "3Ph_Req"
                    break
        report.seek(ptr)
        return config

    # ******************************************************************************************************************

    @staticmethod
    def getProductType(report):
        # Store the pointer of file and move it to the beginning
        ptr = report.tell()
        report.seek(0)
        product = None

        for line in report:
            if MissingObject_Text.get("PRODUCT_TYPE") in line:
                # m = re.split("\W", line)
                # product = m[m.index("Gyr") + 1]
                if "RefNMS2".upper() in line.upper():
                    product = "RefNMS2"
                    break
                elif "RefMMI3".upper() in line.upper():
                    product = "RefMMI3"
                    break
                elif "RefIMS1".upper() in line.upper():
                    product = "RefIMS1"
                    break
        report.seek(ptr)
        return product

    # ******************************************************************************************************************

    @staticmethod
    def appendResultInFile(obis, classId, olnFound, olrFound, idisOmStatus, picassoOmStatus, finalOutcome):
        global dfMissingObjects
        dfMissingObjects = dfMissingObjects.append({"Obis Code": obis,
                                                    " Class ID": classId,
                                                    " In Object List?": olnFound,
                                                    " In RBAC Object List?": olrFound,
                                                    " IDIS OM Status": idisOmStatus,
                                                    " Picasso OM Status": picassoOmStatus,
                                                    " Conclusion": finalOutcome},
                                                   ignore_index=True)

    # ******************************************************************************************************************

    @staticmethod
    def evaluateResult(olnFound, olrFound, idisOmStatus, picassoOmStatus):
        result = Result_Text.get("OTHER")
        if idisOmStatus is not "O":
            if picassoOmStatus is np.NaN:
                if olnFound == MissingObject_Text.get("FOUND") and olrFound == MissingObject_Text.get("NOT_FOUND"):
                    result = Result_Text.get("CHECK_OM")
                elif olnFound == MissingObject_Text.get("NOT_FOUND") and olrFound == MissingObject_Text.get("FOUND"):
                    result = Result_Text.get("OTHER")
                elif olnFound == MissingObject_Text.get("FOUND") and olrFound == MissingObject_Text.get("FOUND"):
                    result = Result_Text.get("CHECK_OM")
                else:
                    result = Result_Text.get("DO_NOTHING")
                picassoOmStatus = "Not in Object Model"
            else:
                if olnFound == MissingObject_Text.get("FOUND") and olrFound == MissingObject_Text.get("NOT_FOUND"):
                    result = Result_Text.get("SGL_ISSUE")
                elif olnFound == MissingObject_Text.get("NOT_FOUND") and olrFound == MissingObject_Text.get("FOUND"):
                    result = Result_Text.get("OTHER")
                elif olnFound == MissingObject_Text.get("NOT_FOUND") and olrFound == MissingObject_Text.get(
                        "NOT_FOUND"):
                    result = Result_Text.get("IMPLEMENT")
                else:
                    result = Result_Text.get("OTHER")
                picassoOmStatus = "Present in Object Model"
        else:
            if picassoOmStatus is np.NaN:
                if olnFound == MissingObject_Text.get("FOUND") and olrFound == MissingObject_Text.get("NOT_FOUND"):
                    result = Result_Text.get("CHECK_OM")
                elif olnFound == MissingObject_Text.get("NOT_FOUND") and olrFound == MissingObject_Text.get("FOUND"):
                    result = Result_Text.get("OTHER")
                elif olnFound == MissingObject_Text.get("FOUND") and olrFound == MissingObject_Text.get("FOUND"):
                    result = Result_Text.get("CHECK_OM")
                else:
                    result = Result_Text.get("OPTIONAL_ISSUE")
                picassoOmStatus = "Not in Object Model"
            else:
                if olnFound == MissingObject_Text.get("FOUND") and olrFound == MissingObject_Text.get("NOT_FOUND"):
                    result = Result_Text.get("SGL_ISSUE")
                elif olnFound == MissingObject_Text.get("NOT_FOUND") and olrFound == MissingObject_Text.get("FOUND"):
                    result = Result_Text.get("OTHER")
                elif olnFound == MissingObject_Text.get("NOT_FOUND") and olrFound == MissingObject_Text.get(
                        "NOT_FOUND"):
                    result = Result_Text.get("OPTIONAL_IMPLEMENT")
                else:
                    result = Result_Text.get("OTHER")
            idisOmStatus = MissingObject_Text.get("OPTIONAL")
        return result, picassoOmStatus, idisOmStatus


# *************************************FUNCTIONS OF THE FILE************************************************************

def getMissingObjects(filenames, df_idis_object_model, df_picasso_object_model):
    missingObjectsObj = IdisMissingObjects()
    missingObjectsObj.getMissingObjects(filenames, df_idis_object_model, df_picasso_object_model)

# **********************************************************************************************************************
