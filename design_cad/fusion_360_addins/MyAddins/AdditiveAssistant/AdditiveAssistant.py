#Author-Daniel Bartlett
#Description-An analysis tool to determine how suitable a part is for the FFF additive manufacturing process.

import adsk.core, adsk.fusion, adsk.cam, traceback
import os.path, sys, math

from . import backend as backend

scriptDir = os.path.dirname(os.path.realpath(__file__))

handlers = []
bodies = []

global good_feedback_img
global med_feedback_img
global bad_feedback_img

good_feedback_img = 'resources/rating/good.png'
med_feedback_img = 'resources/rating/med.png'
bad_feedback_img = 'resources/rating/bad.png'


class inspectButtonPressedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    # Creating the function that runs when the button is pressed.
    def notify(self, args):
        # setup
        app = adsk.core.Application.get()
        ui = app.userInterface
        cmd = args.command
        cmd.isRepeatable = False
        inputs = adsk.core.CommandInputs.cast(cmd.commandInputs)

        try:
            # Set initial size of the ui window
            cmd.setDialogInitialSize(450,300)
            cmd.isOKButtonVisible = False

            """ 
            The add-in is seperated into two tabs
            Tab 1 : Allow user to select their part and to add-in custom values is suitable
            Tab 2 : Provide feedback to the user
            """
            tabCmdInput1 = inputs.addTabCommandInput('tab_setup', 'Setup')
            tab1ChildInputs = tabCmdInput1.children

            tabCmdInput2 = inputs.addTabCommandInput('tab_results', 'Results')
            tab2ChildInputs = tabCmdInput2.children
            tabCmdInput2.isVisible = False

            """
            --------------------------------------- Tab 1 contents ---------------------------------------
            """
            # Adding the part selecion input
            # Asking the user to select the body they would like to inspect
            partSelectionInput = tab1ChildInputs.addSelectionInput('partSelection', 'Body to Inspect', '')
            partSelectionInput.setSelectionLimits(0,1)
            partSelectionInput.tooltip = 'Select the body that you would like to inspect'
            partSelectionInput.addSelectionFilter('SolidBodies')

            # Create dropdown input that lists materials.
            material_dropdown = tab1ChildInputs.addDropDownCommandInput('materialdropdown', 'Select Filament   ',
                                                                       adsk.core.DropDownStyles.TextListDropDownStyle)
            material_dropdown.tooltip = 'Select the material that you will be using.'
            #Add the options for the dropdown menu
            options = material_dropdown.listItems
            options.add('PLA', True, '')
            options.add('ABS', False, '')
            options.add('PET/ PETG/ CPE', False, '')
            options.add('Nylon', False, '')
            options.add('Other', False, '')

            # Create dropdown for mesh quality
            quality_dropdown = tab1ChildInputs.addDropDownCommandInput('qualitydropdown', 'Analysis Approach',
                                                                       adsk.core.DropDownStyles.TextListDropDownStyle)

            quality_dropdown.tooltip = 'Changes the quality of the mesh created for analysis. If you are analysing a complex part, the Fast approach is recommended.'
            #Add the options for the dropdown menu
            options = quality_dropdown.listItems
            options.add('Fast', False, '')
            options.add('Normal', True, '')

            # Printer size
            dimension_table = tab1ChildInputs.addTableCommandInput('table', 'Table', 4, '1:1:1:1')
            dimension_table.maximumVisibleRows = 2
            dimension_table.tablePresentationStyle = 2

            # Get the CommandInputs object associated with the parent command.
            sizecmdInputs = adsk.core.CommandInputs.cast(dimension_table.commandInputs)

            dimension_title =  sizecmdInputs.addTextBoxCommandInput('envelope_title', 'String', 'Build Volume    ', 1, True)
            x_dimension_title =  sizecmdInputs.addTextBoxCommandInput('x_title', 'String', 'X (mm)', 1, True)
            y_dimension_title =  sizecmdInputs.addTextBoxCommandInput('y_title', 'String', 'Y (mm)', 1, True)
            z_dimension_title =  sizecmdInputs.addTextBoxCommandInput('z_title', 'String', 'Z (mm)', 1, True)

            x_val = sizecmdInputs.addIntegerSpinnerCommandInput('volume_x_val', '', 10, 10000, 10, 200)
            x_val.isFullWidth = True
            y_val = sizecmdInputs.addIntegerSpinnerCommandInput('volume_y_val', '', 10, 10000, 10, 200)
            y_val.isFullWidth = True
            z_val = sizecmdInputs.addIntegerSpinnerCommandInput('volume_z_val', '', 10, 10000, 10, 200)
            z_val.isFullWidth = True

            dimension_table.addCommandInput(dimension_title, 1, 0)
            dimension_table.addCommandInput(x_dimension_title, 0, 1)
            dimension_table.addCommandInput(y_dimension_title, 0, 2)
            dimension_table.addCommandInput(z_dimension_title, 0, 3)
            dimension_table.addCommandInput(x_val, 1, 1)
            dimension_table.addCommandInput(y_val, 1, 2)
            dimension_table.addCommandInput(z_val, 1, 3)

            # Preview button
            # Create bool value input with button style that can be clicked.
            inspect_button = tab1ChildInputs.addBoolValueInput('inspectButtonClick', '  Inspect  ', False, 'resources\inspect\\', False )

            inspect_button.isEnabled = False
            """
            --------------------------------------- Tab 2 contents ---------------------------------------
            """
            # Results table 
            tableInput = tab2ChildInputs.addTableCommandInput('table', 'Table', 3, '3:1:1')
            tableInput.maximumVisibleRows = 6
            tableInput.tablePresentationStyle = 2

            # Get the CommandInputs object associated with the parent command.
            cmdInputs = adsk.core.CommandInputs.cast(tableInput.commandInputs)

            # Create three new command inputs.
            titleCol1Input =  cmdInputs.addTextBoxCommandInput('Column1_title', 'String', '<b>Checks<b>', 1, True)
            titleCol2Input =  cmdInputs.addTextBoxCommandInput('Column2_title', 'String', '<b>Results<b>', 1, True)
            titleCol3Input =  cmdInputs.addTextBoxCommandInput('Column3_title', 'String', '<b>Feedback<b>', 1, True)

            overhang_check = cmdInputs.addTextBoxCommandInput('overhang_title', '', 'Overhang', 1, True)
            overhang_result =  cmdInputs.addImageCommandInput('overhang_result', '', bad_feedback_img)
            overhang_overlay = cmdInputs.addBoolValueInput('overhang_overlay_checkbox', '', True, 'resources\check', False)

            warping_check = cmdInputs.addTextBoxCommandInput('warping_title', '', 'Warping', 1, True)
            warping_result =  cmdInputs.addImageCommandInput('warping_result', '', good_feedback_img)
            warping_overlay = cmdInputs.addBoolValueInput('warping_overlay_checkbox', '', True, 'resources\check', False)

            stability_check = cmdInputs.addTextBoxCommandInput('stability_title', '', 'Bed Adhesion', 1, True)
            stability_result =  cmdInputs.addImageCommandInput('stability_result', '', good_feedback_img)
            stability_overlay = cmdInputs.addBoolValueInput('stability_overlay_checkbox', '', True, 'resources\check', False)

            size_check = cmdInputs.addTextBoxCommandInput('size_title', '', 'Part Size', 1, True)
            size_result =  cmdInputs.addImageCommandInput('size_result', '', good_feedback_img)
            size_overlay = cmdInputs.addBoolValueInput('size_overlay_checkbox', '', True, 'resources\check', False)

            environment_check = cmdInputs.addTextBoxCommandInput('environment_title', '', 'Environmental Impact', 1, True)
            environment_result =  cmdInputs.addImageCommandInput('environment_result', '', med_feedback_img)
            environment_overlay = cmdInputs.addBoolValueInput('environmental_overlay_checkbox', '', True, 'resources\check', False)

            # Add the inputs to the table.
            tableInput.addCommandInput(titleCol1Input, 0, 0)
            tableInput.addCommandInput(titleCol2Input, 0, 1)
            tableInput.addCommandInput(titleCol3Input, 0, 2)
            tableInput.addCommandInput(overhang_check, 1, 0)
            tableInput.addCommandInput(overhang_result, 1, 1)
            tableInput.addCommandInput(overhang_overlay, 1, 2)
            tableInput.addCommandInput(warping_check, 2, 0)
            tableInput.addCommandInput(warping_result, 2, 1)
            tableInput.addCommandInput(warping_overlay, 2, 2)
            tableInput.addCommandInput(stability_check, 3, 0)
            tableInput.addCommandInput(stability_result, 3, 1)
            tableInput.addCommandInput(stability_overlay, 3, 2)
            tableInput.addCommandInput(size_check, 4, 0)
            tableInput.addCommandInput(size_result, 4, 1)
            tableInput.addCommandInput(size_overlay, 4, 2)
            tableInput.addCommandInput(environment_check, 5, 0)
            tableInput.addCommandInput(environment_result, 5, 1)
            tableInput.addCommandInput(environment_overlay, 5, 2)

            # Create title
            tab2ChildInputs.addTextBoxCommandInput('Title', '', '', 1, True)
            # Create intro section
            tab2ChildInputs.addTextBoxCommandInput('intro', '', '', 4, True) 
            # Create Feedback message
            tab2ChildInputs.addTextBoxCommandInput('feedback_message', '', '', 2, True) 

            # Add info about sustainability
            sustainability_info = 'Consider all stages of the part life-cycle. This includes selecting the right print settings, ensuring the design of the part is strong enough for its application, and considering how the part will be disassembled and disposed of at the end of life.\n\nTry to understand the properties of the different materials available for the FFF process as they all have different strengths and weaknesses.\n\nOptimise your print settings in order to reduce print times. By selecting an infill structure like gyroid, you can reduce print times and therefore power consumption, whilst still maintaining part strength.'
            sustainability_feedback = tab2ChildInputs.addTextBoxCommandInput('sustainability_message', '', sustainability_info, 10, True)
            sustainability_feedback.isVisible = False

            # learn more link section
            learn_more = tab2ChildInputs.addTextBoxCommandInput('learn_more', '', 'Learn more <a href="https://www.autodesk.com/products/fusion-360/blog/three-environmental-considerations-for-the-fff-3d-printing-process/">here.</a>', 1, True)
            learn_more.isVisible = False

            """
            --------------------------------------- Event handlers ---------------------------------------
            """
            onPartSelect = PartSelectHandler()
            cmd.select.add(onPartSelect)
            handlers.append(onPartSelect) 
            
            onPartUnSelect = PartUnSelectHandler()
            cmd.unselect.add(onPartUnSelect)            
            handlers.append(onPartUnSelect) 

            onExecute = inspectDialogCloseEventHandler()
            cmd.execute.add(onExecute)
            handlers.append(onExecute)

            onExecutePreview = InspectHandler()
            cmd.executePreview.add(onExecutePreview)
            handlers.append(onExecutePreview)

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class PartSelectHandler(adsk.core.SelectionEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            selectedPart = adsk.fusion.BRepBody.cast(args.selection.entity) 
            if selectedPart:
                bodies.append(selectedPart)
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class PartUnSelectHandler(adsk.core.SelectionEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            selectedPart = adsk.fusion.BRepBody.cast(args.selection.entity) 
            if selectedPart:
                bodies.remove(selectedPart)
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class InspectHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

        self.triangleMesh = None
        self.body = None
        self.brepBody = None
        self.overhang_faces = None
        self.stability_colour = None
        self.warping_colour = None
        self.bnd_box = None
        self.requires_support = None
        self.level_of_warping = None
        self.stability_prob_issue = None
        self.size_result = None
        self.dimension_x = None
        self.dimension_y = None
        self.dimension_z = None
        
    def notify(self, args):
        ui = None
        try:
            # Setup stuff
            app = adsk.core.Application.get()
            ui = app.userInterface
            cmd = args.firingEvent.sender
            product = app.activeProduct
            design = adsk.fusion.Design.cast(product)
            root = design.rootComponent

            eventArgs = adsk.core.CommandEventArgs.cast(args)
            inputs = eventArgs.command.commandInputs

            selection_input = cmd.commandInputs.itemById('partSelection')
            inspect_input = cmd.commandInputs.itemById('inspectButtonClick')

            if selection_input.selectionCount == 0:
                inspect_input.isEnabled = False
            else:
                inspect_input.isEnabled = True


            if inputs.itemById('inspectButtonClick').value == True:
                try:
                    self.body = bodies[-1]
                except IndexError:
                    if ui:
                        ui.messageBox('No body selected. Please select a body and try again.')
                        inputs.itemById('inspectButtonClick').value = False
                        return
        
        # ----------------------------- Analyse ------------------------------------------

                if self.triangleMesh == None:

                    material_selection = cmd.commandInputs.itemById('materialdropdown')
                    material_selected = material_selection.selectedItem.name

                    quality_selection = cmd.commandInputs.itemById('qualitydropdown')
                    quality_selected = quality_selection.selectedItem.name

                    # Set styles of progress dialog.
                    progressDialog = ui.createProgressDialog()
                    progressDialog.isBackgroundTranslucent = False
                    progressDialog.isCancelButtonShown = False

                    # Show dialog
                    progressDialog.show('Additive Assistant (FFF)', 'Analysing Part', 0, 10)
                    progressDialog.message = 'Starting Analysis'
                    progressDialog.progressValue = progressDialog.progressValue + 1

                    progressDialog.message = 'Generating Mesh'
                    
                    # retrieves the part used
                    self.body = bodies[-1]
                    self.brepBody = adsk.fusion.BRepBody.cast(self.body)

                    # Calculate the mesh
                    self.triangleMesh = backend.calc_mesh(self.brepBody, quality_selected)

                    num_nodes = self.triangleMesh.nodeCount
                    
    # --------------------------------- Initial inspection process---------------------------------
        # ------------------- Get the bounding box dimensions for the part ------------------------
                    progressDialog.message = 'Calculating Bounding Box'
                    part_dimensions, self.bnd_box = backend.bndBoxDimensions(self.brepBody)
                    progressDialog.progressValue = progressDialog.progressValue + 1

        # ----------------------------- Find the problem faces ---------------------------------------
                    progressDialog.message = 'Analysing Mesh'

                    problem_faces = []
                    overhang_val = 45

                    # Analyse the info and add to the problem list is needed
                    for i in self.triangleMesh.nodeIndices:
                        if backend.overhang_analyse(self.triangleMesh, i, overhang_val):
                            problem_faces.append(i)

                    progressDialog.progressValue = progressDialog.progressValue + 1

        # ----------------------------- Find bottom faces ------------------------------------------
                    progressDialog.message = 'Finding Bottom Faces'
                    lowest_point = backend.find_lowest_point(self.triangleMesh, problem_faces)

                    self.overhang_faces, self.bottom_faces = backend.bottom_face_analysis(self.triangleMesh, problem_faces, lowest_point)

                    progressDialog.progressValue = progressDialog.progressValue + 1
        # ----------------------------- Overhang Inspection ------------------------------------------
                    progressDialog.message = 'Analysing Overhangs'
                    overhang_traffic_light = cmd.commandInputs.itemById('overhang_result')

                    self.requires_support = backend.inspectOverhang(self.overhang_faces, self.triangleMesh.triangleCount, overhang_traffic_light)

                    progressDialog.progressValue = progressDialog.progressValue + 1
        # ---------------------------- warping inspection ---------------------------------------------
                    progressDialog.message = 'Analysing Warping'

                    warping_traffic_light = cmd.commandInputs.itemById('warping_result')

                    # Create a list of x vals and a list of y vals
                    x_list, y_list = backend.create_list_points(self.triangleMesh, self.bottom_faces)

                    base_surface_area = backend.get_triangles_area(x_list, y_list)
                    progressDialog.progressValue = progressDialog.progressValue + 1

                    self.warping_colour, self.level_of_warping = backend.inspectWarping(base_surface_area, warping_traffic_light, part_dimensions, material_selected)

                    progressDialog.progressValue = progressDialog.progressValue + 1
        # ---------------------------- stability inspection ---------------------------------------------
                    progressDialog.message = 'Analysing Stability'

                    stability_traffic_light = cmd.commandInputs.itemById('stability_result')

                    self.stability_colour, self.stability_prob_issue = backend.inspectStability(base_surface_area, stability_traffic_light, part_dimensions)

                    progressDialog.progressValue = progressDialog.progressValue + 1
        # ---------------------------- Size inspection ---------------------------------------------
                    progressDialog.message = 'Analysing Size'
                    # Get the results section in the window.
                    size_traffic_light = cmd.commandInputs.itemById('size_result')
                    self.dimension_x = cmd.commandInputs.itemById('volume_x_val').value
                    self.dimension_y = cmd.commandInputs.itemById('volume_y_val').value
                    self.dimension_z = cmd.commandInputs.itemById('volume_z_val').value

                    # Run inspection
                    self.size_result = backend.inspectSize(self.body, size_traffic_light, part_dimensions, self.dimension_x, self.dimension_y, self.dimension_z)

                    progressDialog.progressValue = progressDialog.progressValue + 1
        # ---------------------------- Environmental Impact inspection ---------------------------------------------
                    progressDialog.message = 'Analysing Environmental Impact'

                    environment_traffic_light = cmd.commandInputs.itemById('environment_result')
                    environment_traffic_light.imageFile = med_feedback_img

                    progressDialog.progressValue = progressDialog.progressValue + 1
                    # Hide the progress dialog at the end.
                    progressDialog.message = 'Finishing'
                    progressDialog.hide()
    # -------------------------------- Show user results tab --------------------------------------------------------------

                gray_colour = adsk.fusion.CustomGraphicsSolidColorEffect.create(adsk.core.Color.create(128,128,128,255))
                volume_overlay, bed_overlay = backend.create_bnd_overlay(self.bnd_box, self.dimension_x, self.dimension_y, self.dimension_z, gray_colour)
                
                # Activate the results tab
                result_tab = cmd.commandInputs.itemById('tab_results')
                result_tab.isVisible = True
                result_tab.activate()

                # Hide the setup tab
                setup_tab = cmd.commandInputs.itemById('tab_setup')
                setup_tab.isVisible = False
                
                # Hide the original body
                self.brepBody.opacity = 0
                cmd.commandInputs.itemById('partSelection').clearSelection()

                # Create the base part graphic that each tool will build on
                backend.create_basic_graphics(self.brepBody)
    
# --------------------------------- Feedback stuff ------------------------------------------
                # create colour effects
                red_color = adsk.fusion.CustomGraphicsSolidColorEffect.create(adsk.core.Color.create(255,0,0,255))
   
                # check box inputs
                overhang_checkbox = inputs.itemById('overhang_overlay_checkbox')
                warping_checkbox = inputs.itemById('warping_overlay_checkbox')
                stability_checkbox = inputs.itemById('stability_overlay_checkbox')
                size_checkbox = inputs.itemById('size_overlay_checkbox')
                environment_checkbox = inputs.itemById('environmental_overlay_checkbox')

                title_text = inputs.itemById('Title')
                intro_text = inputs.itemById('intro')
                feedback_text = inputs.itemById('feedback_message')

                sustainability_info = inputs.itemById('sustainability_message')

                learn_title = inputs.itemById('learn_more')

    # --------------------------------- Overhang ------------------------------------------------
                if overhang_checkbox.value == True:

                    title_text.formattedText = '<div><b>Overhang</b></div>'
                    intro_text.formattedText = 'An overhang on a 3D printed part is an area that is no longer supported by the layer below it. This can lead to faces that sag and sometimes even fail. The areas highlighted in red show where overhangs exist in your part.'
                    feedback_text.isVisible = True

                    if self.requires_support:
                        feedback_text.formattedText = 'This part will require support structures in its current orientation. You can try reorienting the model to minimize overhang areas.'
                    else:
                        feedback_text.formattedText = 'This part is unlikely to require support structures.'

                    if len(self.overhang_faces) == 0:
                        pass
                    else:
                        backend.create_overlay(self.triangleMesh, self.overhang_faces, red_color)

                    sustainability_info.isVisible = False
                    learn_title.isVisible = False

                    overhang_checkbox.value = False
                    warping_checkbox.value = False
                    stability_checkbox.value = False
                    size_checkbox.value = False
                    environment_checkbox.value = False

    # --------------------------------- warping ------------------------------------------------
                elif warping_checkbox.value == True:

                    title_text.formattedText = '<div><b>Warping</b></div>'
                    intro_text.formattedText = 'Warping is when your part begins to curl or deform as the print cools. This can lead to parts seperating from the bed. Warping is common in large parts and when using materials with high shrinkage values, like ABS.'
                    feedback_text.isVisible = True

                    if self.level_of_warping == 'High':
                        feedback_text.formattedText = 'There is a high probability of warping in this part'
                    elif self.level_of_warping == 'Medium':
                        feedback_text.formattedText = 'There is a medium probability of warping in this part'
                    else:
                        feedback_text.formattedText = 'There is a low probability of warping in this part'

                    if len(self.bottom_faces) == 0:
                        pass
                    else:
                        backend.create_overlay(self.triangleMesh, self.bottom_faces, self.warping_colour)

                    sustainability_info.isVisible = False
                    learn_title.isVisible = False

                    overhang_checkbox.value = False
                    warping_checkbox.value = False
                    stability_checkbox.value = False
                    size_checkbox.value = False
                    environment_checkbox.value = False

    # --------------------------------- stability ------------------------------------------------
                elif stability_checkbox.value == True:

                    title_text.formattedText = '<div><b>Bed Adhesion</b></div>'
                    intro_text.formattedText = 'Parts that are tall, thin and with low surface area connecting them to the build plate are at a higher risk of failing due to poor bed adhesion.'
                    feedback_text.isVisible = True

                    if self.stability_prob_issue == 'High':
                        feedback_text.formattedText = 'There is a high probability of bed adhesion issues in this part'
                    elif self.stability_prob_issue == 'Medium':
                        feedback_text.formattedText = 'There is a medium probability of bed adhesion issues in this part'
                    else:
                        feedback_text.formattedText = 'There is a low probability of bed adhesion issues in this part'

                    if len(self.bottom_faces) == 0:
                        pass
                    else:
                        backend.create_overlay(self.triangleMesh, self.bottom_faces, self.stability_colour)

                    sustainability_info.isVisible = False
                    learn_title.isVisible = False

                    overhang_checkbox.value = False
                    warping_checkbox.value = False
                    stability_checkbox.value = False
                    size_checkbox.value = False
                    environment_checkbox.value = False

    # --------------------------------- size ------------------------------------------------
                elif size_checkbox.value == True:

                    title_text.formattedText = '<div><b>Part Size</b></div>'
                    intro_text.formattedText = 'The size of a part that can be printed using the FFF process is restricted by the size of the print volume of your machine. These dimensions can usually be found on the machine manufacturers website.'
                    feedback_text.isVisible = True

                    if self.size_result == 'Good':
                        feedback_text.formattedText = 'The size of this part is suitable for the FFF process.'
                        green_color = adsk.fusion.CustomGraphicsSolidColorEffect.create(adsk.core.Color.create(0,255,0,255))
                        backend.create_bnd_overlay(self.bnd_box, self.dimension_x, self.dimension_y, self.dimension_z, green_color)
                    else:
                        feedback_text.formattedText = 'Part is too large, try to changing orientation or split body into multiple parts.'
                        red_color = adsk.fusion.CustomGraphicsSolidColorEffect.create(adsk.core.Color.create(255,0,0,255))
                        backend.create_bnd_overlay(self.bnd_box, self.dimension_x, self.dimension_y, self.dimension_z, red_color)

                    volume_overlay.isVisible = False
                    bed_overlay.isVisible = False

                    sustainability_info.isVisible = False
                    learn_title.isVisible = False

                    overhang_checkbox.value = False
                    warping_checkbox.value = False
                    stability_checkbox.value = False
                    size_checkbox.value = False
                    environment_checkbox.value = False
                        # --------------------------------- environment ------------------------------------------------
                elif environment_checkbox.value == True:

                    title_text.formattedText = '<div><b>Environmental Impact</b></div>'
                    intro_text.formattedText = 'There are three key aspects that should be considered when analysing the environmental impact, which are part life-cycle, material choice and power consumption.'
                    feedback_text.isVisible = False

                    sustainability_info.isVisible = True
                    learn_title.isVisible = True

                    overhang_checkbox.value = False
                    warping_checkbox.value = False
                    stability_checkbox.value = False
                    size_checkbox.value = False
                    environment_checkbox.value = False

                else:

                    title_text.formattedText = '<div><b>Additive Assistant Tool (FFF)</b></div>'
                    intro_text.formattedText = 'For more information about each area of analysis, select the information icon in the feedback column above.'
                    feedback_text.isVisible = False
                    feedback_text.formattedText = ''

                    sustainability_info.isVisible = False
                    learn_title.isVisible = False
            else:
                pass

        except:
            if ui:
                ui.messageBox('Input Changed Class Failed:\n{}'.format(traceback.format_exc()))


class inspectDialogCloseEventHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        ui = None
        try:
            bodies.clear()
            pass

        except:
            if ui:
                ui.messageBox('command executed failed:\n{}'.format(traceback.format_exc()))


def run(context):
    ui = None
    try:

        app = adsk.core.Application.get()
        ui  = app.userInterface
        command_definitions = ui.commandDefinitions

        # This is where the button will appear, ask some people if thus is the right place for it?
        addins_toolbar_panel = ui.allToolbarPanels.itemById('InspectPanel')

        # defining our command defintion
        inspect_button_definition = command_definitions.addButtonDefinition('additive_assist_fff',
                                                                            'Additive Assistant (FFF)',
                                                                            'An analysis and feedback tool to assist in the design of additively manufactured parts.',
                                                                            'resources')
        # define the button control
        inspect_button_control = addins_toolbar_panel.controls.addCommand(inspect_button_definition,
                                                                          'inspect_button_control')
        # Promote the buuton so it appears in the toolbar
        inspect_button_control.isPromotedByDefault = True
        inspect_button_control.isPromoted = True

        inspect_button_pressed = inspectButtonPressedEventHandler()
        inspect_button_definition.commandCreated.add(inspect_button_pressed)
        handlers.append(inspect_button_pressed)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Delete the control
        inspect_panel = ui.allToolbarPanels.itemById('InspectPanel')
        inspect_control = inspect_panel.controls.itemById('additive_assist_fff')
        if inspect_control:
            inspect_control.deleteMe()

        addin_panel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        inspect_control_backup = addin_panel.controls.itemById('additive_assist_fff')
        if inspect_control_backup:
            inspect_control.deleteMe()

        # Delete the command definition.
        inspect_def = ui.commandDefinitions.itemById('additive_assist_fff')
        if inspect_def:
            inspect_def.deleteMe()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
