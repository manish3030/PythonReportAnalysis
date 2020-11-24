import pandas as pd
from pandas import DataFrame as df
import numpy as np
import re
import os
import xml.etree.ElementTree as ET
import IDIS.IDISAnalyzeMissingObjects as missingObjects

pd.set_option('precision', 0)

Texts = {
    "SNAPSHOTSTART": "PASSED",
    "SNAPSHOTEND": "TOTAL",
    "DEVICETYPE": "Type = '",
    "FAILURE": "FAILED",
    "TEST CASE": "Test Case",
    "MISSINGOBJECTLISTSTART": "is missing in Object-List",
    "OBJECTLISTEND": "Test Case 4",
    "ACCESS_SELECTOR": ": access selectors",
    "ACCESS_RIGHTS": ": Object-List access-rights",
    "PATTERN": "\n****************************************\n"
}

dfMissingObjects = pd.DataFrame(columns=["Obis Code", " Class ID", " In Object List?", " In RBAC Object List?",
                                         "Conclusion"])
dfTotalMissingObjects = pd.DataFrame(index=["Total Missing Objects"])
dfAccSelIssues = pd.DataFrame(columns=["Obis Code", " Class ID", "  Expectation", "  Actual"])
dfTotalAccSelIssues = pd.DataFrame(index=["Total Access Selector Issues"])
dfAccRightIssues = pd.DataFrame(columns=["Obis Code", " Class ID", "  Firmware Value", "  IDIS OM Value"])
dfTotalAccRightIssues = pd.DataFrame(index=["Total Access Right Issues"])


class IdisAnalyzeObjectList:

    def getReportSnapShot(self, filenames, report):
        startWriting = False
        with open(filenames.get("SNAPSHOT"), "w") as snapshot:
            for line in report:
                if Texts.get("SNAPSHOTSTART") in line:
                    startWriting = True
                if startWriting:
                    snapshot.write(line)
                    if Texts.get("SNAPSHOTEND") in line:
                        break
        snapshot.close()

    def getAccessSelectorIssues(self, filenames, report, olissues):
        count = 0
        report.seek(0)
        global dfAccSelIssues
        for line in report:
            if Texts.get("ACCESS_SELECTOR") in line:
                m1 = re.search(r'[0-9-:.]+', line)
                if m1:
                    m2 = re.search(r"[|][0-9]+", line)
                    if m2:
                        dfAccSelIssues = dfAccSelIssues.append({"Obis Code": m1.group(),
                                                                " Class ID":
                                                                    m2.group().split("|")[1]},
                                                               ignore_index=True)
                        count = count + 1
            if Texts.get("OBJECTLISTEND") in line:
                dfTotalAccSelIssues.loc["Total Access Selector Issues", 0] = count
                olissues.write(Texts.get("PATTERN"))
                olissues.write(dfTotalAccSelIssues[0].to_string())
                olissues.write(Texts.get("PATTERN"))
                olissues.write("\n")
                if count > 0:
                    dfAccSelIssues.index = np.arange(1, len(dfAccSelIssues) + 1)
                    olissues.write(str(dfAccSelIssues))
                    olissues.write("\n\n")
                break

    def getAccessRightIssues(self, filenames, report, olissues):
        count = 0
        report.seek(0)
        global dfAccRightIssues
        for line in report:
            if Texts.get("ACCESS_RIGHTS") in line:
                m1 = re.search(r'[0-9-:.]+', line)
                if m1:
                    m2 = re.search(r"[|][0-9]+", line)
                    if m2:
                        dfAccRightIssues = dfAccRightIssues.append({"Obis Code": m1.group(),
                                                                    " Class ID": m2.group().split("|")[1]},
                                                                   ignore_index=True)
                        count = count + 1
            if Texts.get("OBJECTLISTEND") in line:
                dfTotalAccRightIssues.loc["Total Access Right Issues", 0] = count
                olissues.write(Texts.get("PATTERN"))
                olissues.write(dfTotalAccRightIssues[0].to_string())
                olissues.write(Texts.get("PATTERN"))
                olissues.write("\n")
                if count > 0:
                    dfAccRightIssues.index = np.arange(1, len(dfAccRightIssues) + 1)
                    olissues.write(str(dfAccRightIssues))
                    olissues.write("\n\n")
                break


def analyzeReport(filenames, df_idis_object_model, df_picasso_object_model):
    reportObj = IdisAnalyzeObjectList()
    olnormal, olrbac = getObjectList(filenames)
    with open(filenames.get("REPORT_NAME"), "r") as report:
        with open(filenames.get("OBJECT_LIST_ISSUES"), "w") as olissues:
            reportObj.getReportSnapShot(filenames, report)
            missingObjects.getMissingObjects(filenames, df_idis_object_model, df_picasso_object_model)
            # reportObj.getAccessSelectorIssues(filenames, report, olissues)
            # reportObj.getAccessRightIssues(filenames, report, olissues)
    report.close()
    olissues.close()
    olnormal.close()
    olrbac.close()


def getObjectList(filenames):
    if os.path.exists(filenames.get("OBJECT_LIST")) and not os.path.exists(filenames.get("OBJECT_LIST_XML")):
        os.rename(filenames.get("OBJECT_LIST"), filenames.get("OBJECT_LIST_XML"))
    if os.path.exists(filenames.get("OBJECT_LIST_RBAC")) and not os.path.exists(filenames.get("OBJECT_LIST_RBAC_XML")):
        os.rename(filenames.get("OBJECT_LIST_RBAC"), filenames.get("OBJECT_LIST_RBAC_XML"))
    olnormal = open(filenames.get("OBJECT_LIST_XML"), "r")
    olrbac = open(filenames.get("OBJECT_LIST_RBAC_XML"), "r")
    return olnormal, olrbac