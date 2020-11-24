"""Purpose of this file is to find the appropriate object model and then extract the required data frame
    by eliminating the undesired columns and return it to the main function."""

import pandas as pd
import os
import sys

pd.set_option('display.max_colwidth', None)

ObjectModel = {
    "IDIS_OBJECT_MODEL": "IDIS-S02-002 - object model Pack2 Ed2.0 - V2.28.xlsx",
    "IDIS_OBJECT_MODEL_SHEET": "Object model",
    "PICASSO_OBJECT_MODEL": "Picasso2_Object_Model.xlsm",
    "PICASSO_OBJECT_MODEL_SHEET": "Picasso-2 Ref Object Model"
}


# **********************************************************************************************************************


"""Process the Object model to get the data frame values"""


def processObjectModel():
    jobDone = False
    idis_object_model_path = os.path.join(os.getcwd(), ObjectModel.get("IDIS_OBJECT_MODEL"))
    picasso_object_model_path = os.path.join(os.getcwd(), ObjectModel.get("PICASSO_OBJECT_MODEL"))
    if os.path.exists(idis_object_model_path):
        df_idis_object_model = getIDISModelDataFrame(idis_object_model_path)
        if os.path.exists(picasso_object_model_path):
            df_picasso_object_model = getPicassoModelDataFrame(picasso_object_model_path)
            jobDone = True
        else:
            print("No Picasso Object Model Found")
    else:
        print("No IDIS Object Model Found")
    if jobDone:
        return df_idis_object_model, df_picasso_object_model
    else:
        sys.exit("Sorry, appropriate files not found, Exiting....")

# **********************************************************************************************************************


"""Get the approriate columns from idis object model into idis data frame"""


def getIDISModelDataFrame(idis_object_model_path):
    # Import IDIS Excel File
    global df_idis_object_model
    df_idis_object_model = pd.read_excel(idis_object_model_path, ObjectModel.get("IDIS_OBJECT_MODEL_SHEET"),
                                         index_col=None, na_values=["NA"])

    # Change the column names
    df_idis_object_model.columns = ["Id", "Name", "1Ph_Req", "3Ph_Req", "Attribute_type", "ClassId", "Version", "SN",
                                    "Obis/Default", "Public_(AR)", "Preestablished_(AR)", "Management_(AR)",
                                    "Comments"]
    # Remove unwanted columns
    df_idis_object_model.drop(["SN", "Comments"], axis=1, inplace=True)
    return df_idis_object_model

# **********************************************************************************************************************


"""Get the approriate columns from Picasso object model into Picasso data frame"""


def getPicassoModelDataFrame(picasso_object_model_path):
    # Import Picasso Excel File
    global df_picasso_object_model
    df_picasso_object_model = pd.read_excel(picasso_object_model_path, ObjectModel.get("PICASSO_OBJECT_MODEL_SHEET"),
                                            index_col=None, na_values=["NA"])

    # Remove unwanted columns
    df_picasso_object_model.drop(["Classification of Attribute / Method", "Function group",
                                  "Parameter checksum relevant", "Parameter Control in Production",
                                  "Parameter Control in the field", "Change Modules E360\nV2", "Unnamed: 47",
                                  "Change Modules E660\nV2", "Change Modules E660", "Unnamed: 44", "Unnamed: 43",
                                  "Configuration tool Default Value (TBD later)", "Comments",
                                  "Restrictions / Comments", "By", "Date", "3 wire connection-Disabled object list",
                                  "E360-G01", "E360-F02", "E360-F01", "E360-B05", "E360-A05", "E360-A04", "E360-B05",
                                  "E360-B04", "E355-B01", "E355-A01", "E360-E01", "E360-D01", "E360-C01",
                                  "E360-B03", "E360-A03", "Ref_MMI3-A03", "Ref_MMI3-A02", "E660-A02", "Ref_NMS2-A03",
                                  "Ref_NMS2-A02"], axis=1, inplace=True)

    # Change the column names
    df_picasso_object_model.columns = ["Id", "Name", "Type/Class_Info", "Obis/Default", "Security_group",
                                    "Default_MAC", "Actual_MAC", "Firmware_Name", "RefNMS2", "RefMMI3", "RefIMS1",
                                    "IDIS_2.0_1Ph", "IDIS_2.0_3Ph"]
    return  df_picasso_object_model

# **********************************************************************************************************************
