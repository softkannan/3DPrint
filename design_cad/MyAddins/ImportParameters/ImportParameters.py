import os
import sys
import csv
import adsk.core
import adsk.fusion
import traceback
import io

class UserParameters:

    def __init__(self):
        self.ui = None
        try:
            self.app = adsk.core.Application.get()
            self.ui  = self.app.userInterface
            self.design = self.app.activeProduct
            self.userParams = self.design.userParameters
        except:
            if self.ui:
                self.ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

    def updateFusionUserParameters(self, name, value, units, comments):
        if self.userParams.itemByName(name) == None:
            self.__addNewUserParameter(name, value, units, comments)
        else:
            self.__updateUserParameter(name, value, units, comments)
    
    def __addNewUserParameter(self, name, value, units, comments):
        print("Add parameters: Name: " + name + ", Value: " + value + ", Units: " + units + ", Comments: " + comments)
        aUserValue = adsk.core.ValueInput.createByString(value)
        aUnits = self.design.unitsManager.defaultLengthUnits
        self.userParams.add(name, aUserValue, aUnits, comments)
    
    def __updateUserParameter(self, name, value, units, comments):
        print("Update parameters: Name: " + name + ", Value: " + value + ", Units: " + units + ", Comments: " + comments)
        aUserValue = adsk.core.ValueInput.createByString(value)
        aUnits = self.design.unitsManager.defaultLengthUnits
        self.userParams.itemByName(name).expression = value

class CSVHelper:
    def __init__(self):
        self.currentFolder = os.path.dirname(__file__)
        # self.resourcesPath = os.path.join(self.currentFolder, 'resources/')
        self.resourcesPath = self.currentFolder
        self.fileNameByKey = {
            "M3": "resources/screws/M3.csv",
            "M4": "resources/screws/M4.csv",
            "M5": "resources/screws/M5.csv",
            "B608": "resources/bearings/608.csv",
            "B625": "resources/bearings/625.csv",
            "B626": "resources/bearings/626.csv",
            "B638": "resources/bearings/638.csv",
            "BLinear8": "resources/bearings/linear8.csv",
            "VSlot_2020": "resources/v-slot/VSlot_2020.csv",
            "VProfileNut_M5": "resources/v-slot/VProfileNut_M5.csv",
            "NEMA17_HS2408": "resources/stepper_motor/NEMA17_HS2408.csv",
            "NEMA17_HS4401": "resources/stepper_motor/NEMA17_HS4401.csv",
            "NEMA17_HS8401": "resources/stepper_motor/NEMA17_HS8401.csv",
        }

    def __checkResourcesFolder(self, path):
        print("Check resources folder: " + path)
        if os.path.exists(path):
            print(path + " exists")
            return True
        else:
            print("Error: resources path doesn't exist. \n" + path)
            sys.exit("Exit")
            return False

    def __checkFilePath(self, path):
        if os.path.isfile(path):
            print(path + " exists")
            return True
        else:
            sys.exit("Error: file doesn't exis or it's not a file \n" + path)
            return False

    def printResourcesKeys(self):
        adjustKey = 20
        adjustPath = 30
        print("Key".ljust(adjustKey), "Path".ljust(adjustPath))
        for key in self.fileNameByKey:
            value = self.fileNameByKey[key]
            print(key.ljust(adjustKey), ("./" + value).ljust(adjustPath))

    def importAll(self):
        for key in self.fileNameByKey:
            self.importFromRecousrces(key)

    def importFromRecousrces(self, key):
        fileName = self.fileNameByKey[key]
        if fileName == None:
            fileName = key + ".csv"
        filePath = os.path.join(self.resourcesPath, fileName)

        if self.__checkResourcesFolder(self.resourcesPath) == False:
            return False
        if self.__checkFilePath(filePath) == False:
            return True
        if self.checkCSVFile(filePath) == False:
            return True

    def checkCSVFile(self, filePath):
        # ['Name;Value;Units;Comments']
        print("Start to read CSV, " + filePath)
        csvKeysToCheck = ['Name', 'Value', 'Units', 'Comments']
        file = open(filePath, 'r')
        csv_Dictionary = csv.DictReader(file)
        headers = csv_Dictionary.fieldnames
        if headers != csvKeysToCheck:
            print("Error: - csv file doesn't contain all necessary keys")
            original = ', '.join([str("'"+elem+"'")
                                 for elem in csvKeysToCheck])
            current = ', '.join([str("'"+elem+"'") for elem in headers])
            print("\t original:\t" + original)
            print("\t current:\t" + current)
            sys.exit("Exit")
            return False

        print("Start to update Fusion360 user parameters")
        fusionParameters = UserParameters()
        for row in csv_Dictionary:
            csvRow = dict(row)
            name = csvRow["Name"]
            value = csvRow["Value"]
            units = csvRow["Units"]
            comments = csvRow["Comments"]
            fusionParameters.updateFusionUserParameters(
                name, value, units, comments)
        print(str(csv_Dictionary.line_num) + " parameters where updated")


def run(context):
    ui = None
    try:
        # app = adsk.core.Application.get()
        # ui  = app.userInterface
        # Get all components in the active design.
        # product = app.activeProduct
        # design = adsk.fusion.Design.cast(product)
        # title = 'Import Spline csv'
        # if not design:
        # ui.messageBox('No active Fusion design', title)
        # return

        # dlg = ui.createFileDialog()
        # dlg.title = 'Open CSV File'
        # dlg.filter = 'Comma Separated Values (*.csv);;All Files (*.*)'
        # if dlg.showOpen() != adsk.core.DialogResults.DialogOK :
        # return

        # filename = dlg.filename
        # with io.open(filename, 'r', encoding='utf-8-sig') as f:
        # points = adsk.core.ObjectCollection.create()
        # line = f.readline()
        # data = []
        # while line:
        # pntStrArr = line.split(',')
        # for pntStr in pntStrArr:
        # try:
        # data.append(float(pntStr))
        # except:
        # break

        # if len(data) >= 3 :
        # point = adsk.core.Point3D.create(data[0], data[1], data[2])
        # points.add(point)
        # line = f.readline()
        # data.clear()
        # if points.count:
        # root = design.rootComponent
        # sketch = root.sketches.add(root.xYConstructionPlane)
        # sketch.sketchCurves.sketchFittedSplines.add(points)
        # else:
        # ui.messageBox('No valid points', title)

        csvHelper = CSVHelper()
        csvHelper.importAll()
        csvHelper.printResourcesKeys()
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
