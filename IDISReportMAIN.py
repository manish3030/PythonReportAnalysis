import IDIS.IDISGetReport as getReport
import IDIS.IDISAnalyzeObjectListIssues as idisObjectList
import IDIS.IDISObjectModel as objectModel
import pandas as pd

Filenames = {
    "REPORT_NAME": "_Report.txt",
    "SNAPSHOT": "Report_Snapshot.txt",
    "OBJECT_LIST_ISSUES": "Report_ObjectListIssues.txt",
    "INCONCLUSIVE_OBJECTS": "Report_InconclusiveObject.txt",
    "INAPPLICABLE_OBJECTS": "Report_InapplicableObject.txt",
    "FATAL_OBJECTS" "Report_FatalObjects.txt"
    "FAILURES": "Report_Failures.txt",
    "OBJECT_LIST": "Object_List_WithoutRBAC.txt",
    "OBJECT_LIST_RBAC": "Object_List_RBAC.txt",
    "OBJECT_LIST_XML": "Object_List_WithoutRBAC.xml",
    "OBJECT_LIST_RBAC_XML": "Object_List_RBAC.xml"

}

# **********************************************************************************************************************

"""Main Program execution"""


def main():

    if getReport.getIDISReport(Filenames):
        df_idis_object_model, df_picasso_object_model = objectModel.processObjectModel()
        idisObjectList.analyzeReport(Filenames, df_idis_object_model, df_picasso_object_model)


# **********************************************************************************************************************

if __name__ == '__main__':
    main()

# **********************************************************************************************************************
