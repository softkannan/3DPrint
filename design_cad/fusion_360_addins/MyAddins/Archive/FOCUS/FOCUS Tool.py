#FOCUS tool (Feedback and Optimisation for CAD Utility Script)
#Version: 1.30
#Developed by Joe Palmer
#Purpose: to provide realtime feedback to CAD students regarding key model metrics
#Tool may be expanded in the future for batch marking of student work
#Initial release builds on previous code release AMR124_general_model_checker3.py which was used by AMR124 module students in the 2019/2020 academic year
#Visaul mockup of this tool was originally developed under the name new_table11.py
#ALL algorithm creation and implementation is the work of Joseph Palmer and is completely unique
#Assistance from Autodesk employee Melisa Kaner was provided during the early development of this tool.
#Copyright Joe Palmer December 2020
#---------------------VERSION HISTORY---------------------------------------
#V0.1 visual mockup only, removed "command executed" prompt when pressing OK button
#V0.2 visual mockup only, added multiple information tabs, corrected command box title, added focus ascii logo
#V0.3 added function to interrogate and score a model relative to the conrod example, scores not yet displayed in the tool
#V0.4 key information displayed by the tool, scores and sliders still paceholder
#V0.5 sliders reporting scores correctly, some issues with algorithm, total score not yet working
#V0.6 Some Scoring algorithm issues corrected, placeholder values still present
#V0.7 changes to import conrod parameters from values.csv
#V0.8 dropdown list now reads model names from CSV file
#V0.9 major changes to class and definition structure to later allow inputchangedeventhandler to be implemented
#V0.91 structure changes ongoing
#V0.92 removed all references to version number in user facing utility. V1.0 targetted for marking algorithm working.
#V0.93 specific slider values displayed, utility updates with ideal values from excel (not user cad file info)
#V0.94 Trying to get inputchangedeventhandler to work.
#V1.00 Merged with working inputchanged event handler example
#V1.01 Tool is now reorting model properties correctly, an additional text box reports which drop down option the user has selected. Sliders and scores are stil placeholders. 
#V1.02 In process of changing all sliders to global vars
#V1.03 Percentage score text updating with selection - dummy values only
#V1.04 Dead end don't use
#V1.05 All sliders and scores updating with dummy data
#V1.06 Scores only updating with correct data
#V1.07 All sliders and scores reporting properly and updating after each user change selection, total score not working
#V1.08 Total score reporting properly. Tool fully working except wordbank and code word.
#V1.09 wordbank and code word definitions written ans semi-working.
#V1.10 save issue
#V1.11 Wordbank feedback is updating properly, wordbank function itself needs review, not making sense.
#V1.12 Codeword functionality semi-working, textbox removed which mirrors user selection
#V1.15 First attempt at converting to add-in
#V1.20 Working as an Add-in, error on empty model and error when clicking hyperlinks remain.
#V1.30 Added exception handler for when the model is empty or contains no sketches (general divide by zero check). increased height of wordbank feedback box. Modified way in which resources are accessed to be Mac compatible.
#---------------------RELEASE HISTORY-----------------------------------------
#AMR124_general_model_checker3.py - Used for intial testing of automated feedback, implemented for 2019/2020 cohort.
#V1.20 Initial app store submission, rejected due to error on empty model.
#V1.30 F360 App Store Release!!!!!
#---------------------LONG TERM DEVELOPMENT----------------------
#change algorithm to count total model parameters rather than sketch dimensions
#create algorithm for 4-word code generator, this needs to be based on a unique identifer such as student user name, this would stop students sharing any codes. VLE quiz may not be capable of this. user username/userid to generate codeword
#centre wordbank and codeword text
#Refinement of scoring algorithm
#Adding hyperlinks to tab 3 causes popup error, investigate.

import adsk.core, adsk.fusion, adsk.cam, traceback, os 

_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)

# Global set of event handlers to keep them referenced for the duration of the command
_handlers = []
_instructionTable = adsk.core.SelectionCommandInput.cast(None) 
_dropdownInput3 = adsk.core.DropDownCommandInput.cast(None)
_selectionTable = adsk.core.SelectionCommandInput.cast(None)
_textBoxInput1 = adsk.core.TextBoxCommandInput.cast(None)
_textBoxInput2 = adsk.core.TextBoxCommandInput.cast(None)

isSavingSnapshot = True
commandId = 'SketchCheckerCmd'
workspaceToUse = 'FusionSolidEnvironment'
panelToUse = 'InspectPanel'



# Event handler for the inputChanged event.
class MyInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            changedInput = eventArgs.input

            #--------------------RUN THE MODEL SCORING ROUTINE, ASSIGN VARIABLES------------------
            values, percentages = MarkingFunction(_dropdownInput3.selectedItem.index)    

            body_volume, body_mass, component_material, feature_health_percentage, constrained_sketch_percentage, construction_datums_count, number_bodies, sketch_dims, user_params = values
            volume_score, mass_score, bodies_score, sketch_c_score, dims_score, features_score, feature_health_score, datum_score, user_param_score, total_score = percentages

            written_feedback = WordBank(mass_score, volume_score, bodies_score, total_score)

            code = CodeWord(total_score, body_mass)
            
            #--------------------------------------

            table = eventArgs.inputs.itemById("sliderstable")

            #update mass score and slider
            readonly_txt_cmd = table.getInputAtPosition(0,3)
            readonly_txt_cmd.value = str(mass_score) + '%'

            readonly_txt_cmd = table.getInputAtPosition(0,2)
            readonly_txt_cmd.valueOne = mass_score

            

            #update volume score and slider
            readonly_txt_cmd = table.getInputAtPosition(1,3)
            readonly_txt_cmd.value = str(volume_score) + '%'
         
            readonly_txt_cmd = table.getInputAtPosition(1,2)
            readonly_txt_cmd.valueOne = volume_score

           

            #update bodies score and slider           
            readonly_txt_cmd = table.getInputAtPosition(2,3)
            readonly_txt_cmd.value = str(bodies_score) + '%'

            readonly_txt_cmd = table.getInputAtPosition(2,2)
            readonly_txt_cmd.valueOne = bodies_score



            #update sketches score and slider 
            readonly_txt_cmd = table.getInputAtPosition(3,3)
            readonly_txt_cmd.value = str(sketch_c_score) + '%'

            readonly_txt_cmd = table.getInputAtPosition(3,2)
            readonly_txt_cmd.valueOne = sketch_c_score



            #update health score and slider 
            readonly_txt_cmd = table.getInputAtPosition(4,3)
            readonly_txt_cmd.value = str(feature_health_score) + '%'

            readonly_txt_cmd = table.getInputAtPosition(4,2)
            readonly_txt_cmd.valueOne = feature_health_score



            #update datum score and slider 
            readonly_txt_cmd = table.getInputAtPosition(5,3)
            readonly_txt_cmd.value = str(datum_score) + '%'

            readonly_txt_cmd = table.getInputAtPosition(5,2)
            readonly_txt_cmd.valueOne = datum_score



            #update dimensions score and slider 
            readonly_txt_cmd = table.getInputAtPosition(6,3)
            readonly_txt_cmd.value = str(dims_score) + '%'

            readonly_txt_cmd = table.getInputAtPosition(6,2)
            readonly_txt_cmd.valueOne = dims_score


            #update parameters score and slider 
            readonly_txt_cmd = table.getInputAtPosition(7,3)
            readonly_txt_cmd.value = str(user_param_score) + '%'

            readonly_txt_cmd = table.getInputAtPosition(7,2)
            readonly_txt_cmd.valueOne = user_param_score
            


            #update TOTAL score and slider 
            table = eventArgs.inputs.itemById("Scoretable")
            readonly_txt_cmd = table.getInputAtPosition(0,3)
            readonly_txt_cmd.value = str(total_score) + '%'

            readonly_txt_cmd = table.getInputAtPosition(0,2)
            readonly_txt_cmd.valueOne = total_score

            
            #update written feedback table
            table = eventArgs.inputs.itemById("feedbacktable")
            readonly_txt_cmd = table.getInputAtPosition(0,0)
            readonly_txt_cmd.text = written_feedback

            #update codeword
            readonly_txt_cmd = table.getInputAtPosition(1,0)
            readonly_txt_cmd.text = code
            


            #if changedInput.id == 'dropdown3':
            #_textBoxInput2.text = 'Your selection is ' + _dropdownInput3.selectedItem.name

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the execute event.
class MyExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)         
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the destroy event.
#class MyDestroyHandler(adsk.core.CommandEventHandler):
#    def __init__(self):
#        super().__init__()
#    def notify(self, args):
#        adsk.terminate()
        

# Event handler for the commandCreated event.
class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:

            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
                    
            #--------------------CREATE TABS------------------
            
            inputs = adsk.core.CommandInputs.cast(eventArgs.command.commandInputs)

            # Create a tab input.
            tabCmdInput1 = inputs.addTabCommandInput('tab_1', 'Model Data')
            tab1ChildInputs = tabCmdInput1.children
            
            # Create a tab input.
            tabCmdInput2 = inputs.addTabCommandInput('tab_2', 'Further Information')
            tab2ChildInputs = tabCmdInput2.children
            
            # Create a tab input.
            tabCmdInput3 = inputs.addTabCommandInput('tab_3', 'About')
            tab3ChildInputs = tabCmdInput3.children

            #--------------------------------------

            
            #--------------------CREATE TABLE WITH LOGOS------------------       
            table = tab1ChildInputs.addTableCommandInput('logotable', 'Inputs', 1, '1') #way in which tables are added to specific tabs is changed significantly from first visual
            table.minimumVisibleRows = 3
            table.maximumVisibleRows = 3
            table.columnSpacing = 1
            table.rowSpacing = 20
            table.tablePresentationStyle = adsk.core.TablePresentationStyles.itemBorderTablePresentationStyle
            table.hasGrid = False                    
            
            
            ImageInput = inputs.addImageCommandInput('image', 'Image', "resources/logos.png")
            ImageInput.isReadOnly = True
            table.addCommandInput(ImageInput, 0, 0, False, False)
            #--------------------------------------
                        
            #--------------------CREATE TABLE WITH USER INSTRUCTIONS------------------       
            table = tab1ChildInputs.addTableCommandInput('instructionstable', 'Inputs', 1, '1') 
            #table.minimumVisibleRows = 5
            #table.maximumVisibleRows = 10
            table.columnSpacing = 1
            table.rowSpacing = 0
            table.tablePresentationStyle = adsk.core.TablePresentationStyles.itemBorderTablePresentationStyle
            table.hasGrid = False                    
            

            #textboxInput = inputs.addTextBoxCommandInput('readonly_textBox', 'Text Box 1', '<div align="center">This is an automated feedback tool. Please select the example model that you are trying to replicate from the drop down list. Scores for your model, in key categories, will then be displayed below along with a total score for your model. For further information about how your model is scored, please see the information tabs to the right. <a href="https://drive.google.com/drive/folders/1kfaii3EU3ZA750hqTgN6FFgenph2C0Oy?usp=sharing"> All exercises files can be downloaded from here </a></div>', 2, True)
            textboxInput = inputs.addTextBoxCommandInput('readonly_textBox', 'Text Box 1', '<div align="center">This plugin provides feedback on your current, active, Fusion 360 design and is intended for use in conjunction with the accompanying CAD modelling exercises <a href="https://drive.google.com/drive/folders/1kfaii3EU3ZA750hqTgN6FFgenph2C0Oy?usp=sharing">which can be downloaded here</a>. Select the exercise that you are trying to replicate from the drop-down list, percentage scores for a variety of categories will then be calculated for your model and displayed. See the information tabs to the right for an explanation of each scoring category. Please report any issues with this plugin <a href="https://forms.gle/wYs39GCgBCFFJFNF9">using this form</a>. This tool is developed and maintained by <a href="http://j-palmer.me.uk/">Joe Palmer</a>.</div>', 2, True)
            textboxInput.isReadOnly = True


            textboxInput.numRows = 5
            table.addCommandInput(textboxInput, 0, 0, False, False) #row, column, ??, ??

            #--------------------------------------

            #--------------------CREATE TABLE WITH FURTHER INFO INSTRUCTIONS------------------       
            table = tab2ChildInputs.addTableCommandInput('infotable', 'Inputs', 1, '1') #way in which tables are added to specific tabs is changed significantly from first visual
            table.minimumVisibleRows = 1
            table.maximumVisibleRows = 1
            table.columnSpacing = 1
            table.rowSpacing = 10
            table.tablePresentationStyle = adsk.core.TablePresentationStyles.itemBorderTablePresentationStyle
            table.hasGrid = False                    
            
            
            
            textboxInput = inputs.addTextBoxCommandInput('readonly_textBox', 'Text Box 1', '<div align="center">If you would like some more information about how your model has been scored then please see the table below. For each scoring metric and explanation of what the metric is has been given along with tips on how to improve your models score in this area.</div>', 2, True)
            textboxInput.isReadOnly = True
            textboxInput.numRows = 3
            table.addCommandInput(textboxInput, 0, 0, False, False) #row, column, ??, ??

            #--------------------CREATE TABLE WITH FURTHER MODEL INFORMATION------------------       
            table = tab2ChildInputs.addTableCommandInput('modeltable', 'Inputs', 2, '1:5') 
            table.minimumVisibleRows = 1
            table.maximumVisibleRows = 10
            table.columnSpacing = 1
            table.rowSpacing = 10
            table.tablePresentationStyle = adsk.core.TablePresentationStyles.itemBorderTablePresentationStyle
            table.hasGrid = False                    
            
            
            textboxInput = inputs.addTextBoxCommandInput('readonly_textBox', 'Text Box 1', 'Model Mass', 2, True)
            textboxInput.isReadOnly = True
            textboxInput.numRows = 3
            table.addCommandInput(textboxInput, 0, 0, False, False) #row, column, ??, ??

            textboxInput = inputs.addTextBoxCommandInput('readonly_textBox', 'Text Box 1', 'The mass of your component will be reported here, this needs to match example component to be correct.', 2, True)
            textboxInput.isReadOnly = True
            textboxInput.numRows = 3
            table.addCommandInput(textboxInput, 0, 1, False, False) #row, column, ??, ??

            textboxInput = inputs.addTextBoxCommandInput('readonly_textBox', 'Text Box 1', 'Model Volume', 2, True)
            textboxInput.isReadOnly = True
            textboxInput.numRows = 3
            table.addCommandInput(textboxInput, 1, 0, False, False) #row, column, ??, ??

            textboxInput = inputs.addTextBoxCommandInput('readonly_textBox', 'Text Box 1', 'The total material volume of your component will be reported here, this needs to match example component to be correct.', 2, True)
            textboxInput.isReadOnly = True
            textboxInput.numRows = 3
            table.addCommandInput(textboxInput, 1, 1, False, False) #row, column, ??, ??

            textboxInput = inputs.addTextBoxCommandInput('readonly_textBox', 'Text Box 1', 'Number of Bodies', 2, True)
            textboxInput.isReadOnly = True
            textboxInput.numRows = 3
            table.addCommandInput(textboxInput, 2, 0, False, False) #row, column, ??, ??

            textboxInput = inputs.addTextBoxCommandInput('readonly_textBox', 'Text Box 1', 'The number of bodies in your component, for complete singular components this should be no more than 1.', 2, True)
            textboxInput.isReadOnly = True
            textboxInput.numRows = 3
            table.addCommandInput(textboxInput, 2, 1, False, False) #row, column, ??, ??

            textboxInput = inputs.addTextBoxCommandInput('readonly_textBox', 'Text Box 1', 'Constrained Sketches', 2, True)
            textboxInput.isReadOnly = True
            textboxInput.numRows = 3
            table.addCommandInput(textboxInput, 3, 0, False, False) #row, column, ??, ??

            textboxInput = inputs.addTextBoxCommandInput('readonly_textBox', 'Text Box 1', 'The percentage of sketches which are fully constrained, this should be 100%.', 2, True)
            textboxInput.isReadOnly = True
            textboxInput.numRows = 3
            table.addCommandInput(textboxInput, 3, 1, False, False) #row, column, ??, ??

            textboxInput = inputs.addTextBoxCommandInput('readonly_textBox', 'Text Box 1', 'Feature Health', 2, True)
            textboxInput.isReadOnly = True
            textboxInput.numRows = 3
            table.addCommandInput(textboxInput, 4, 0, False, False) #row, column, ??, ??

            textboxInput = inputs.addTextBoxCommandInput('readonly_textBox', 'Text Box 1', 'The percentage of healthy features, this should be 100%.', 2, True)
            textboxInput.isReadOnly = True
            textboxInput.numRows = 3
            table.addCommandInput(textboxInput, 4, 1, False, False) #row, column, ??, ??

            textboxInput = inputs.addTextBoxCommandInput('readonly_textBox', 'Text Box 1', 'Construction Datums', 2, True)
            textboxInput.isReadOnly = True
            textboxInput.numRows = 3
            table.addCommandInput(textboxInput, 5, 0, False, False) #row, column, ??, ??

            textboxInput = inputs.addTextBoxCommandInput('readonly_textBox', 'Text Box 1', 'The number of constructions features, these should be included and used to build your component.', 2, True)
            textboxInput.isReadOnly = True
            textboxInput.numRows = 3
            table.addCommandInput(textboxInput, 5, 1, False, False) #row, column, ??, ??

            textboxInput = inputs.addTextBoxCommandInput('readonly_textBox', 'Text Box 1', 'Number of Dimensions', 2, True)
            textboxInput.isReadOnly = True
            textboxInput.numRows = 3
            table.addCommandInput(textboxInput, 6, 0, False, False) #row, column, ??, ??

            textboxInput = inputs.addTextBoxCommandInput('readonly_textBox', 'Text Box 1', 'The number of dimensions used, this should be a minimum.', 2, True)
            textboxInput.isReadOnly = True
            textboxInput.numRows = 3
            table.addCommandInput(textboxInput, 6, 1, False, False) #row, column, ??, ??

            textboxInput = inputs.addTextBoxCommandInput('readonly_textBox', 'Text Box 1', 'Number of User Parameters', 2, True)
            textboxInput.isReadOnly = True
            textboxInput.numRows = 3
            table.addCommandInput(textboxInput, 7, 0, False, False) #row, column, ??, ??

            textboxInput = inputs.addTextBoxCommandInput('readonly_textBox', 'Text Box 1', 'The number of user parameters used, key part parameters should be included as user parameters.', 2, True)
            textboxInput.isReadOnly = True
            textboxInput.numRows = 3
            table.addCommandInput(textboxInput, 7, 1, False, False) #row, column, ??, ??
            #--------------------------------------




            #--------------------CREATE TABLE WITH ABOUT INFORMATION------------------       
            table = tab3ChildInputs.addTableCommandInput('abouttable', 'Inputs', 1, '1') 
            table.minimumVisibleRows = 2
            table.maximumVisibleRows = 2
            table.columnSpacing = 1
            table.rowSpacing = 10
            table.tablePresentationStyle = adsk.core.TablePresentationStyles.itemBorderTablePresentationStyle
            table.hasGrid = False                    
            
            ImageInput = inputs.addImageCommandInput('image', 'Image', "resources/focuslogo.png")
            ImageInput.isReadOnly = True
            table.addCommandInput(ImageInput, 0, 0, False, False)

            #textboxInput = inputs.addTextBoxCommandInput('readonly_textBox', 'Text Box 1', '<div align="center"><a href="http://j-palmer.me.uk/resources-and-tools/">FOCUS tool</a> developed by <a href="http://j-palmer.me.uk/">Joe Palmer</a> for use by the <a href="https://amrctraining.co.uk/">University of Sheffields AMRC Training Centre</a>. Copyright © 2020, Joe Palmer. This work is licenced under the Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0). <a href="https://creativecommons.org/licenses/by-nc-nd/4.0/">Licence Documentation can be accessed here.</a></div>', 2, True)
            
            textboxInput = inputs.addTextBoxCommandInput('readonly_textBox', 'Text Box 1', '<div align="center">Copyright © 2020, Joe Palmer all rights reserved. The download and installation of this plugin is only permitted through the Autodesk Fusion 360 app store, if you have obtained this app from a different source please report this to the app author using the error reporting form linked on the first tab.</div>', 2, True)
            
            
            textboxInput.isReadOnly = True
            textboxInput.numRows = 3
            table.addCommandInput(textboxInput, 1, 0, False, False) #row, column, ??, ??

            


            #--------------------USER SELECTS WHICH COMPONENT THEY ARE MODELLING------------------
            
            global _dropdownInput3 
            _dropdownInput3 = tab1ChildInputs.addDropDownCommandInput('dropdown3', '             Which component are you attempting to model?          ', adsk.core.DropDownStyles.LabeledIconDropDownStyle); 
            
            scriptDir = os.path.dirname(os.path.realpath(__file__))
            #csv_directory = scriptDir + '\\resources\\values.csv' old code, working in windows, not in MacOS

            csv_directory = scriptDir + '/resources/values.csv'
            

            # Read the csv file.
            cnt = 0
            file = open(csv_directory)
            
                       
            for line in file:
                # Get the values from the csv file.
                pieces = line.split(',')
            
                listname = pieces[0]
                #listname = str(cnt+1)+ '. ' + listname
                listname = str(cnt)+ '. ' + listname
                if cnt == 0:
                    _dropdownInput3.listItems.add(listname, True, '')
                else:
                    _dropdownInput3.listItems.add(listname, False, '')

                cnt=cnt+1

            #userselecteditem = dropdownInput3.selectedItem.index
            #userselecteditem
            
            #--------------------------------------


            #--------------------RUN THE MODEL SCORING ROUTINE, ASSIGN VARIABLES------------------
            # needs to be moved / changed to inputchanged handler
            values, percentages = MarkingFunction(_dropdownInput3.selectedItem.index)    

            body_volume, body_mass, component_material, feature_health_percentage, constrained_sketch_percentage, construction_datums_count, number_bodies, sketch_dims, user_params = values
            volume_score, mass_score, bodies_score, sketch_c_score, dims_score, features_score, feature_health_score, datum_score, user_param_score, total_score = percentages
            
            
            written_feedback = WordBank(mass_score, volume_score, bodies_score, total_score)
    
            #--------------------------------------


            #--------------------CREATE TABLE WITH DATA DISPLAYED ABOUT THE USERS MODEL------------------       
            # needs to be made dynamic and global var
            table = tab1ChildInputs.addTableCommandInput('sliderstable', 'Inputs', 4, '4:3:7:1') #way in which tables are added to specific tabs is changed significantly from first visual
            table.minimumVisibleRows = 3
            table.maximumVisibleRows = 10
            table.columnSpacing = 1
            table.rowSpacing = 1
            table.tablePresentationStyle = adsk.core.TablePresentationStyles.itemBorderTablePresentationStyle
            table.hasGrid = False                    
            
           
            stringInput = inputs.addStringValueInput('mass_label', '', 'Model Mass')
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 0, 0, False, False) 

            stringInput = inputs.addStringValueInput('mass_value', '', str(body_mass)+' g') #body_mass
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 0, 1, False, False)
           
            
            sliderinput = inputs.addIntegerSliderCommandInput('intSlider', 'Integer Slider', 0, 100)
            sliderinput.valueOne = mass_score #mass_score
            sliderinput.isEnabled = False
            sliderinput.isFullWidth = False
            sliderinput.setText(' ', ' ')
            table.addCommandInput(sliderinput, 0, 2, False, False)

        
            stringInput = inputs.addStringValueInput('score', '', str(mass_score) + '%') #mass_score
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 0, 3, False, False)

            
            stringInput = inputs.addStringValueInput('volume_label', '', 'Model Volume')
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 1, 0, False, False)

            stringInput = inputs.addStringValueInput('volume', '', str(body_volume)+' mm^3') #body_volume
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 1, 1, False, False)

            sliderinput3 = inputs.addIntegerSliderCommandInput('intSlider3', 'Integer Slider3', 0, 100)
            sliderinput3.valueOne = volume_score #volume_score
            sliderinput3.isEnabled = False
            sliderinput3.isFullWidth = False
            sliderinput3.setText(' ', ' ')
            table.addCommandInput(sliderinput3, 1, 2, False, False)

            stringInput = inputs.addStringValueInput('score', '', str(volume_score) + '%') #volume_score
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 1, 3, False, False)


            stringInput = inputs.addStringValueInput('no_bodies', '', 'Number of Bodies')
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 2, 0, False, False)

            stringInput = inputs.addStringValueInput('bodies', '', str(number_bodies)) #number_bodies
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 2, 1, False, False)

            sliderinput4 = inputs.addIntegerSliderCommandInput('intSlider4', 'Integer Slider4', 0, 100)
            sliderinput4.valueOne = bodies_score #bodies_score
            sliderinput4.isEnabled = False
            sliderinput4.isFullWidth = False
            sliderinput4.setText(' ', ' ')
            table.addCommandInput(sliderinput4, 2, 2, False, False)

            stringInput = inputs.addStringValueInput('score', '', str(bodies_score) + '%') #bodies_score
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 2, 3, False, False)

            

            stringInput = inputs.addStringValueInput('sketches', '', 'Constrained Sketches')
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 3, 0, False, False)

            stringInput = inputs.addStringValueInput('sketches', '', str(constrained_sketch_percentage)+' %')
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 3, 1, False, False)

            sliderinput5 = inputs.addIntegerSliderCommandInput('intSlider5', 'Integer Slider5', 0, 100)
            sliderinput5.valueOne = sketch_c_score #sketch_c_score
            sliderinput5.isEnabled = False
            sliderinput5.isFullWidth = False
            sliderinput5.setText(' ', ' ')
            table.addCommandInput(sliderinput5, 3, 2, False, False)

            stringInput = inputs.addStringValueInput('score', '', str(sketch_c_score) + '%') #sketch_c_score
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 3, 3, False, False)

            
            
            stringInput = inputs.addStringValueInput('health', '', 'Feature Health')
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 4, 0, False, False)

            stringInput = inputs.addStringValueInput('health', '', str(feature_health_percentage)+' %')
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 4, 1, False, False)

            sliderinput6 = inputs.addIntegerSliderCommandInput('intSlider6', 'Integer Slider6', 0, 100)
            sliderinput6.valueOne = feature_health_score #feature_health_score
            sliderinput6.isEnabled = False
            sliderinput6.isFullWidth = False
            sliderinput6.setText(' ', ' ')
            table.addCommandInput(sliderinput6, 4, 2, False, False)

            stringInput = inputs.addStringValueInput('score', '', str(feature_health_score) + '%') #feature_health_score
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 4, 3, False, False)

            
            stringInput = inputs.addStringValueInput('datums', '', 'Construction Datums')
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 5, 0, False, False)

            stringInput = inputs.addStringValueInput('datums', '', str(construction_datums_count))
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 5, 1, False, False)

            sliderinput7 = inputs.addIntegerSliderCommandInput('intSlider7', 'Integer Slider7', 0, 100)
            sliderinput7.valueOne = datum_score #datum_score
            sliderinput7.isEnabled = False
            sliderinput7.isFullWidth = False
            sliderinput7.setText(' ', ' ')
            table.addCommandInput(sliderinput7, 5, 2, False, False)

            stringInput = inputs.addStringValueInput('score', '', str(datum_score) + '%') #datum_score
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 5, 3, False, False)



            stringInput = inputs.addStringValueInput('dims', '', 'Number of Dimensions')
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 6, 0, False, False)

            stringInput = inputs.addStringValueInput('dims', '', str(sketch_dims)) # sketch_dims
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 6, 1, False, False)

            sliderinput8 = inputs.addIntegerSliderCommandInput('intSlider8', 'Integer Slider8', 0, 100)
            sliderinput8.valueOne = dims_score #dims_score
            sliderinput8.isEnabled = False
            sliderinput8.isFullWidth = False
            sliderinput8.setText(' ', ' ')
            table.addCommandInput(sliderinput8, 6, 2, False, False)

            stringInput = inputs.addStringValueInput('score', '', str(dims_score) + '%') #dims_score
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 6, 3, False, False)




            stringInput = inputs.addStringValueInput('params', '', 'Number of User Parameters')
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 7, 0, False, False)

            stringInput = inputs.addStringValueInput('params', '', str(user_params))
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 7, 1, False, False)

            sliderinput9 = inputs.addIntegerSliderCommandInput('intSlider9', 'Integer Slider9', 0, 100)
            sliderinput9.valueOne = user_param_score #user_param_score
            sliderinput9.isEnabled = False
            sliderinput9.isFullWidth = False
            sliderinput9.setText(' ', ' ')
            table.addCommandInput(sliderinput9, 7, 2, False, False)

            stringInput = inputs.addStringValueInput('score', '', str(user_param_score) + '%') #user_param_score
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 7, 3, False, False)

            #-------------------------------------------------------------------

            #--------------------CREATE TABLE WITH TOTAL SCORE------------------  
            # # needs to be made dynamic and global var      
            table = tab1ChildInputs.addTableCommandInput('Scoretable', 'Inputs', 4, '4:3:7:1') #way in which tables are added to specific tabs is changed significantly from first visual
            table.minimumVisibleRows = 1
            table.maximumVisibleRows = 1
            table.columnSpacing = 1
            table.rowSpacing = 1
            table.tablePresentationStyle = adsk.core.TablePresentationStyles.itemBorderTablePresentationStyle
            table.hasGrid = False                    
         

            stringInput = inputs.addStringValueInput('total_label', '', 'Total Score')
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 0, 0, False, False) 

            stringInput = inputs.addStringValueInput('spcer_value', '', '    ')
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 0, 1, False, False)
            
            sliderinput10 = inputs.addIntegerSliderCommandInput('intSlider10', 'Total Score', 0, 100)
            sliderinput10.valueOne = total_score
            sliderinput10.isEnabled = False
            sliderinput10.isFullWidth = False
            sliderinput10.setText(' ', ' ')
            table.addCommandInput(sliderinput10, 0, 2, False, False)

        
            stringInput = inputs.addStringValueInput('score', '', str(total_score) + '%')
            stringInput.isReadOnly = True
            table.addCommandInput(stringInput, 0, 3, False, False)

            #--------------------------------------

            #--------------------CREATE TABLE WITH WRITTEN FEEDBACK------------------
            # needs to be made dynamic and global var       
            table = tab1ChildInputs.addTableCommandInput('feedbacktable', 'Inputs', 1, '1') #way in which tables are added to specific tabs is changed significantly from first visual
            table.minimumVisibleRows = 1
            table.maximumVisibleRows = 2
            table.columnSpacing = 1
            table.rowSpacing = 10
            table.tablePresentationStyle = adsk.core.TablePresentationStyles.itemBorderTablePresentationStyle
            table.hasGrid = False                    
         
            
            
            #textboxInput = inputs.addTextBoxCommandInput('readonly_textBox', 'Text Box 1', '<div align="center">Overall this looks like a great model, well done! To further improve your score you could, eliminate or fix some of the failed features, ensure that all of your sketches are fully constrained, try to reduce the total number of numerical dimensions that you have used. If you wish to log your score on the e-learning system please enter the code below. </div>', 2, True)
            
            textboxInput = inputs.addTextBoxCommandInput('readonly_textBox', 'Text Box 1', written_feedback, 2, True) #unsure how to centre this.
            textboxInput.isReadOnly = True
            textboxInput.numRows = 5
            table.addCommandInput(textboxInput, 0, 0, False, False) #row, column, ??, ??

            textboxInput = inputs.addTextBoxCommandInput('readonly_textBox', 'Text Box 1', '<div align="center">CORRECT-HORSE-BATTERY-STAPLE</div>', 2, True)
            textboxInput.isReadOnly = True
            textboxInput.numRows = 2
            table.addCommandInput(textboxInput, 1, 0, False, False) #row, column, ??, ??

            #---------------------------------------------------------------------

            #--------------------CREATE TABLE SHOWING SELECTION------------------   
            #global _selectionTable    
            #_selectionTable = tab1ChildInputs.addTableCommandInput('selectiontable', 'Inputs', 1, '1') 
            #_selectionTable.minimumVisibleRows = 3
            #_selectionTable.maximumVisibleRows = 3
            #_selectionTable.columnSpacing = 1
            #_selectionTable.rowSpacing = 10
            #_selectionTable.tablePresentationStyle = adsk.core.TablePresentationStyles.itemBorderTablePresentationStyle
            #_selectionTable.hasGrid = False                    
            
            
            #global _textBoxInput2
            #selectedItem = _dropdownInput3.selectedItem.name
            #_textBoxInput2 = inputs.addTextBoxCommandInput('result_textBox', 'Text Box 2', 'Your selection is ' + selectedItem, 2, True)
            #_textBoxInput2.isReadOnly = True
            #_textBoxInput2.numRows = 3
            #_selectionTable.addCommandInput(_textBoxInput2, 0, 0, False, False)

            #-----------Subscribe to the various command events-------------

            # Connect to command execute.
            onExecute = MyExecuteHandler()
            eventArgs.command.execute.add(onExecute)
            _handlers.append(onExecute)

            # Connect to input changed.
            onInputChanged = MyInputChangedHandler()
            eventArgs.command.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)
            
            # Connect to the command terminate.
            #onDestroy = MyDestroyHandler()
            #eventArgs.command.destroy.add(onDestroy)
            #_handlers.append(onDestroy)      
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
        

def WordBank(mass_score, volume_score, bodies_score, total_score):
    feedback = " "

    
    if total_score>95: 
        feedback = feedback + 'Overall this looks like an excellent model, well done! '
    elif total_score>75:
        feedback = feedback + 'Overall this looks like a good model, well done! '
    elif total_score>50:
        feedback = feedback + 'Overall this is an average model, please consult the scores above and the information tab to see where and how you can improve. '
    else:
        feedback = feedback + 'This model differs significantly from the sample geometry, please consult the scores above and the information tab to see where and how you can improve. '
    
    
    
    if volume_score>95:
        feedback = feedback + 'The volume of your model is ideal or very near to ideal. Some small features may have inconsistencies. '
    elif volume_score>75:
        feedback = feedback + 'The volume of your model is close to ideal but improvements can still be made. Double check all of your feature sizes. '
    elif volume_score>50:
        feedback = feedback + 'The volume of your model differs signiifcantly from the example component, check that you have not missed any features from your model. '
    else:
        feedback = feedback + 'The volume of your model differs considerably from the example component. Double check that you have interpreted the component form correctly. '


    if mass_score == volume_score:    
        feedback = feedback + 'The applied material type for this component appears to be correct. '
    else:
        feedback = feedback + 'Check that you have applied the correct material type to this component. '

    if bodies_score<100:
        feedback = 'Either multiple bodies exist in this design or the design is empty. This is a serious issue. The total model score will remain at 0 until rectified.'

    feedback = feedback + 'If you wish to log your score on the e-learning system please enter the code below: '    

    if bodies_score<100:
        feedback = 'Either multiple bodies exist in this design or the design is empty. This is a serious issue. The total model score will remain at 0 until rectified.'

    
    
    #feedback = '<div align="center">feedback </div>'
        
    
    #feedback = feedback + str(mass_score) + str(volume_score) + str (bodies_score) + str(total_score) #enable to write out scores and check feedback logic.

    return feedback

def CodeWord(total_score, body_mass):
    #coded_score_one = "ONE"
    #coded_score_two = "TWO"
    #coded_score_three = "THREE"
    #coded_score_four = "FOUR"
    coded_score = " "

    if total_score>90:
        coded_score = 'CIRCUS-WINDOW-MOSQUITO-TRIANGLE'
    elif total_score>80:
        coded_score = 'SCHOOL-BALLOON-TORCH-SPHERE'
    elif total_score>70:
        coded_score = 'LIQUID-DRILL-MAGNET-CARROT'
    elif total_score>60:
        coded_score = 'JET-PEPPER-TIGER-MAZE'
    elif total_score>50:
        coded_score = 'BALLOON-BOOK-MAGNET-PEBBLE'
    elif total_score>40:
        coded_score = 'RAINBOW-SANDWICH-LIBRARY-PASSPORT'
    elif total_score>30:
        coded_score = 'GARDEN-CLOCK-TYPEWRITER-WEB'
    elif total_score>20:
        coded_score = 'CRYSTAL-SPOON-TUNNEL-MONEY'
    elif total_score>10:
        coded_score = 'PAINT-UMBRELLA-ONION-ALPHABET'
    elif total_score==0:
        coded_score = 'CORRECT-HORSE-BATTERY-STAPLE'
    else:
        coded_score = 'RECORD-TRIANGLE-WATER-SOFTWARE'
    
    #string_score=str(total_score)
    #ones = int(string_score[2])

    #user_name = adsk.core.Application.userId
    #user = str(user_name)

    
    return coded_score

def MarkingFunction(userinput):
    
    return_parameters = []
    scores = []

    #reported parameters
    good_feature = warning_feature = error_feature = constrained_sketch_number = 0
    body_volume = 0
    body_mass = 0
    number_bodies =0
    sketch_dims = 0
    component_material = "a"
    user_params = 0
    feature_health_percentage = 0
    constrained_sketch_percentage = 0
    construction_datums_count = 0


    #scoring parameters
    volume_score = 0
    mass_score = 0
    bodies_score = 0
    sketch_c_score = 0
    dims_score = 0
    features_score = 0
    feature_health_score = 0
    datum_score = 0
    user_param_score = 0
    total_score = 0

    
    
  
    scriptDir = os.path.dirname(os.path.realpath(__file__))
    csv_directory = scriptDir + '/resources/values.csv'
    
    
    # Read the csv file.
    cnt = 0
    file = open(csv_directory)
    for line in file:
        # Get the values from the csv file.
        pieces = line.split(',')
            
        if cnt == userinput: # this is selection-1, stepping through entire file and assigning variables only when user selected line is reached.
            ideal_volume = float(pieces[1])
            ideal_mass = float(pieces[2])
            ideal_bodies = int(pieces[3])
            ideal_dims = int(pieces[4])
            ideal_features = int(pieces[5])
                

        cnt=cnt+1
            
     

    #tolerance bands
    volume_tol = 0.15
    mass_tol = 0.15
    sketch_c_tol = 0.30
    dims_tol = 0.30
    features_tol = 0.30
    features_q_tol = 0.30

    app = adsk.core.Application.get()
    ui  = app.userInterface
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    rootComp = design.rootComponent
        
    #component_material = design.activeComponent.material.name
    
    #report number of bodies
    #this needs changing to only count bodies with mass 
    #this will ensure that any construction surfaces are not counted - this has now been done.
    #number_bodies = design.activeComponent.bRepBodies.count
    
    for body in design.activeComponent.bRepBodies:            
        body_volume = body_volume + round(1000*body.physicalProperties.volume,2)
        body_mass = body_mass + round(1000*body.physicalProperties.mass,2)
        if body.physicalProperties.volume>0:
            number_bodies = number_bodies + 1
    
    
    if body_mass>0:
    
        #report number of user parameters
        user_params = design.userParameters.count

        #originally used user_params = design.activeComponent.modelParameters.count this was incorrect but might be a better way to count dimensions
        
        
        # Features   
        features_number = rootComp.features.count
        
        for i in range(0, features_number):
            # Iterate (can be done with enumerate)
            individual_feature = rootComp.features.item(i)
            each_feature = individual_feature.healthState
            
            if each_feature == 0:
                good_feature+= 1
            if each_feature == 1:
                warning_feature+= 1
            if each_feature == 2:
                error_feature+= 1
        
        # Sketches  
        sketches_count = rootComp.sketches.count
        
        for i in range(0, sketches_count):
            # Iterate (can be done with enumerate)
            sketch = rootComp.sketches.item(i)
            if sketch.isFullyConstrained == True:
                constrained_sketch_number +=1
        
        constrained_sketch_percentage = round((constrained_sketch_number / sketches_count) * 100)
        
        
        # Number of dimensions used
        
        
        for i in range(0, sketches_count):
            # Iterate (can be done with enumerate)
            sketch = rootComp.sketches.item(i)
            sketch_dims = sketch_dims + sketch.sketchDimensions.count
        
        

        # Construction Datums
        # How many construction things?
        construction_axes_count = rootComp.constructionAxes.count
        construction_planes_count = rootComp.constructionPlanes.count
        construction_points_count = rootComp.constructionPoints.count
        # Tally
        construction_datums_count = construction_axes_count + construction_planes_count + construction_points_count
        
        # Tally feature health
        feature_health = [good_feature, warning_feature, error_feature]
        # Convert to percentage
        feature_health_percentage = round((good_feature/features_number)*100)

        #Volume scoring
        
        volume_score = 1-((abs(body_volume-ideal_volume))/ideal_volume)*(1/volume_tol)
        volume_score = volume_score*100
        if volume_score<0:
            volume_score=0
        if volume_score>100:
            volume_score=100
        volume_score = round(volume_score)

        #Mass scoring
        
        mass_score = 1-((abs(body_mass-ideal_mass))/ideal_mass)*(1/mass_tol)
        mass_score = mass_score*100
        if mass_score<0:
            mass_score=0
        if mass_score>100:
            mass_score=100
        mass_score = round(mass_score)

        #Bodies scoring
        
        if number_bodies==ideal_bodies:
            bodies_score=100
        else:
            bodies_score=0

        #Sketches scoring
        
        sketch_c_score = 1-((abs(constrained_sketch_percentage-100))/100)*(1/sketch_c_tol)
        sketch_c_score = sketch_c_score*100
        if sketch_c_score<0:
            sketch_c_score=0
        if sketch_c_score>100:
            sketch_c_score=100
        sketch_c_score = round(sketch_c_score)

        #Dimensions scoring
        
        dims_score = 1-(((sketch_dims-ideal_dims)/ideal_dims)*(1/dims_tol))
        dims_score = dims_score*100
        if dims_score<0:
            dims_score=0
        if dims_score>100:
            dims_score=100
        dims_score = round(dims_score)

        #Features scoring
        
        features_score = 1-(((features_number-ideal_features)/ideal_features)*(1/features_tol))
        features_score = features_score*100
        if features_score<0:
            features_score=0
        if features_score>100:
            features_score=100
        features_score = round(features_score)

        #Feature quality scoring
        
        feature_health_score = 1-((abs(feature_health_percentage-100))/100)*(1/features_q_tol)
        feature_health_score = feature_health_score*100
        if feature_health_score<0:
            feature_health_score=0
        if feature_health_score>100:
            feature_health_score=100
        feature_health_score = round(feature_health_score)

        #Datum Scoring

        if construction_datums_count>0:
            datum_score=100
        else:
            datum_score=0

        #User Parameter scoring

        if user_params>0:
            user_param_score=100
        else:
            user_param_score=0

    
    total_score=(0.4*volume_score) + (0.1*mass_score) + (0.15*sketch_c_score) + (0.1*dims_score) + (0.15*feature_health_score) + (0.05*datum_score) + (0.05*user_param_score)

    if bodies_score<100:
        total_score=0       #This logic needs reviewing

    total_score = round(total_score)

    return_parameters = [body_volume, body_mass, component_material, feature_health_percentage, constrained_sketch_percentage, construction_datums_count, number_bodies, sketch_dims, user_params]
    scores = [volume_score, mass_score, bodies_score, sketch_c_score, dims_score, features_score, feature_health_score, datum_score, user_param_score, total_score]
    return return_parameters, scores



def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui  = _app.userInterface
      
        # Create a command.
        #cmd = _ui.commandDefinitions.itemById('tableTest')
        #if cmd:
        #    cmd.deleteMe()
            
        #cmd = _ui.commandDefinitions.addButtonDefinition('tableTest', 'FOCUS TOOL', 'Table Test', '')
        
        # Get the CommandDefinitions collection.
        cmdDefs = _ui.commandDefinitions
        #returnValue = commandDefinitions_var.addButtonDefinition(id, name, tooltip, resourceFolder)
        # Create a button command definition.
        buttonSample = cmdDefs.addButtonDefinition('FOCUStoolbutton', 
                                                   'FOCUS Tool', 
                                                   'The FOCUS tool scores your CAD model in various categories and suggests areas for improvement',
                                                   './Resources')

        # Connect to the command create event.
        onCommandCreated = MyCommandCreatedHandler()
        buttonSample.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)
        
        # Get the ADD-INS panel in the model workspace. 
        addInsPanel = _ui.allToolbarPanels.itemById('InspectPanel')
        
        # Add the button to the bottom of the panel.
        buttonControl = addInsPanel.controls.addCommand(buttonSample)

        # Execute the command.
        #cmd.execute()
        # Set this so the script continues to run.
        #adsk.autoTerminate(False)



    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))



def stop(context):
    ui = None
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui  = app.userInterface
        #ui.messageBox('Stop addin')

        # Clean up the UI.
        cmdDef = _ui.commandDefinitions.itemById('FOCUStoolbutton')
        if cmdDef:
            cmdDef.deleteMe()
            
        addinsPanel = _ui.allToolbarPanels.itemById('InspectPanel')
        cntrl = addinsPanel.controls.itemById('FOCUStoolbutton')
        if cntrl:
            cntrl.deleteMe()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))