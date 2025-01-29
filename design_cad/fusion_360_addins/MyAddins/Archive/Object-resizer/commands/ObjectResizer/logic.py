from turtle import distance
from venv import create
import adsk.core
import adsk.fusion
from ... import config
import math
import os
import json
import time
from time import sleep
from ...lib import fusion360utils as futil

app = adsk.core.Application.get()
ui = app.userInterface
skip_validate = False
PALETTE_ID = config.sample_palette_id
PALETTE_URL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'help_palette.html')
PALETTE_URL = PALETTE_URL.replace('\\', '/')

ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')


#Closing palette event
def palette_closed(args: adsk.core.UserInterfaceGeneralEventArgs):
    global _handlers
    _handlers = []
    palette = ui.palettes.itemById(PALETTE_ID)
    # Delete the Palette
    if palette:
        palette.deleteMe()



class ResizerModifierLogic():
    def __init__(self, des: adsk.fusion.Design):
        self.defaultUnits = des.unitsManager.defaultLengthUnits
            
        # Set default values.
        self.set_x = 0
        self.set_y = 0
        self.set_z = 0

        self.print_x = 0
        self.print_y = 0
        self.print_z = 0

        self.scale = 0
        self.des = des
    
    def create_command_inputs(self, inputs: adsk.core.CommandInputs):

        self.visible_inputs = False

        # Create a body selection input.
        self.bodies_to_scale_input = inputs.addSelectionInput(
            'bodies_input', 'Bodies', 'Select the bodies.')
        self.bodies_to_scale_input.addSelectionFilter('Bodies')
        self.bodies_to_scale_input.addSelectionFilter('MeshBodies')
        self.bodies_to_scale_input.setSelectionLimits(1,1)

        # Create a point selection input.
        self.point_to_scale_input = inputs.addSelectionInput(
            'point_input', 'Point', 'Select the point.')
        self.point_to_scale_input.addSelectionFilter('Vertices')
        self.point_to_scale_input.addSelectionFilter('SketchPoints')
        self.point_to_scale_input.addSelectionFilter('ConstructionPoints')
        self.point_to_scale_input.setSelectionLimits(1,1)

        self.inputGroup = inputs.addGroupCommandInput("group_set_dimensions", 'Set dimensions')
        self.inputGroup.isVisible = self.visible_inputs

        # Create a value input.
        self.set_x_dimension = self.inputGroup.children.addValueInput(
            'set_x_dimension', 'Set X Dimension', self.defaultUnits, adsk.core.ValueInput.createByReal(float(self.set_x)))
        self.set_x_dimension.isVisible=self.visible_inputs
        self.set_x_dimension.tooltip ='Write the expected value along the x axis. Other coordinates will be recalculated automatically.'

        self.set_y_dimension = self.inputGroup.children.addValueInput(
            'set_y_dimension', 'Set Y Dimension', self.defaultUnits, adsk.core.ValueInput.createByReal(float(self.set_y)))
        self.set_y_dimension.isVisible=self.visible_inputs
        self.set_y_dimension.tooltip ='Write the expected value along the y axis. Other coordinates will be recalculated automatically.'

        self.set_z_dimension = self.inputGroup.children.addValueInput(
            'set_z_dimension', 'Set Z Dimension', self.defaultUnits, adsk.core.ValueInput.createByReal(float(self.set_z)))
        self.set_z_dimension.isVisible=self.visible_inputs
        self.set_z_dimension.tooltip ='Write the expected value along the z axis. Other coordinates will be recalculated automatically.'

        self.print_group = inputs.addGroupCommandInput("group_print_dimensions", 'Preview')
        self.print_group.isExpanded = False
        self.print_group.isVisible = self.visible_inputs
        # Create a value input field and set the default using 1 unit of the default length unit.
        default_value = adsk.core.ValueInput.createByString('1')
        self.x_dimension = self.print_group.children.addTextBoxCommandInput(
            'x_dimension', 'Dimension in X', '', 1, True)
        self.x_dimension.isVisible = self.visible_inputs

        self.y_dimension = self.print_group.children.addTextBoxCommandInput(
            'y_dimension', 'Dimension in Y', '', 1, True)
        self.y_dimension.isVisible = self.visible_inputs

        self.z_dimension = self.print_group.children.addTextBoxCommandInput(
            'z_dimension', 'Dimension in Z', '', 1, True)
        self.z_dimension.isVisible = self.visible_inputs

        
        helppath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'help_icon', '')
        self.help = inputs.addBoolValueInput('help','Help',False,helppath)


    def handle_selection_event(self, args: adsk.core.CommandEventArgs):
        event_args = adsk.core.SelectionEventArgs.cast(args)
        self.activeSelectionInput = event_args.firingEvent.activeInput
        self.selection = event_args.selection
        
        


        if self.activeSelectionInput.id == 'bodies_input':
            self.point_to_scale_input.hasFocus = False
            self.visible_inputs = True
            ResizerModifierLogic.update_visible_values(self)

            self.body_input = self.selection.entity
            self.selection_point_on_body = self.selection.point
            self.selected_body = self.body_input.boundingBox
            ResizerModifierLogic.calculate_dimensions(self)
            self.body: adsk.fusion.BRepBody = self.body_input
            ResizerModifierLogic.update_values(
                self, self.calculated_x, self.calculated_y, self.calculated_z)
            
            if (self.point_to_scale_input.selectionCount == 0)and (self.body_input.classType() != 'adsk::fusion::MeshBody'):
                self.ponit = ResizerModifierLogic.get_the_clostest_vertice_of_selection(
                self, self.body, self.selection_point_on_body)
                self.point_to_scale_input.addSelection(self.ponit)
                
            if(self.body_input.classType() == 'adsk::fusion::MeshBody'):
                comp: adsk.fusion.Component = self.body.parentComponent
                self.ponit : adsk.fusion.ConstructionPoint = comp.originConstructionPoint
                mesh : adsk.fusion.MeshBody= self.body_input
                ppoint :adsk.fusion.ConstructionPoint= mesh.mesh.nodeCoordinates[0]
                futil.log(str(ppoint.x))
                self.point_to_scale_input.addSelection(self.ponit)

        if self.activeSelectionInput.id == 'point_input':
            self.ponit = self.selection.entity
            


    def handle_unselection_event(self, args: adsk.core.CommandEventArgs):
        event_args = adsk.core.SelectionEventArgs.cast(args)
        self.activeSelectionInput = event_args.firingEvent.activeInput
        if self.activeSelectionInput.id == 'bodies_input':
            self.point_to_scale_input.clearSelection()
            self.visible_inputs = False
            self.point_to_scale_input.hasFocus = False
            ResizerModifierLogic.update_values(self, 0, 0, 0)
            ResizerModifierLogic.update_visible_values(self)
        



    def handle_input_changed(self, args: adsk.core.CommandEventArgs):
        changedInput = args.input

        user_input_x = self.set_x_dimension.value
        user_input_y = self.set_y_dimension.value
        user_input_z = self.set_z_dimension.value

        futil.log(str(changedInput.id))
        if (changedInput.id == 'help'):
            # Creating palette
            self.palette = ui.palettes.itemById(PALETTE_ID)
            if not self.palette: 
                self.palette = ui.palettes.add(PALETTE_ID, 'Object Resizer Help',PALETTE_URL , False, True, True, 600, 500, True)
                #self.palette.setPosition(800, 400)
                self.palette.isVisible = True
                futil.add_handler(self.palette.closed, palette_closed)

        if (changedInput.id == 'set_x_dimension'):
            self.scale = user_input_x/self.calculated_x
            ResizerModifierLogic.calculate_scale(self)
        if (changedInput.id == 'set_y_dimension'):
            self.scale = user_input_y/self.calculated_y
            ResizerModifierLogic.calculate_scale(self)
        if (changedInput.id == 'set_z_dimension'):
            self.scale = user_input_z/self.calculated_z
            ResizerModifierLogic.calculate_scale(self)


    def handle_execute(self, args: adsk.core.CommandEventArgs):
        object_collection = adsk.core.ObjectCollection.create()
        object_collection.add(self.body)
        comp: adsk.fusion.Component = self.body.parentComponent
        scaleFeatures = comp.features.scaleFeatures
        scale_factor = adsk.core.ValueInput.createByReal(self.scale)
        input = scaleFeatures.createInput(
            object_collection, self.ponit, scale_factor)
        scaleFeature = scaleFeatures.add(input)

    def handle_validate_input(self, args: adsk.core.ValidateInputsEventArgs):
        if self.scale == 0:
                args.areInputsValid = False
                return
        if (self.bodies_to_scale_input.commandInputs == 0) and (self.point_to_scale_input.selectionCount == 0):
                args.areInputsValid = False
                return
        if self.scale < 0:
                args.areInputsValid = False
                return

    def handle_pre_select_start(self, args: adsk.core.SelectionEventHandler):
        event_args = adsk.core.SelectionEventArgs.cast(args)
        self.activeSelectionInput = event_args.firingEvent.activeInput

        if (self.activeSelectionInput.id == 'bodies_input') and (self.activeSelectionInput.classType() != 'adsk::fusion::MeshBody') and (self.point_to_scale_input.selectionCount == 0):
            pre_point: adsk.core.Point3D = args.selection.point
            
            pre_body = args.selection.entity
            if(pre_body.classType() == 'adsk::fusion::MeshBody'):
                return
           
            i = ResizerModifierLogic.get_the_clostest_vertice_of_selection(self,
                pre_body, pre_point)
            pre_the_clostest_point = adsk.core.Point3D.create(i.geometry.x,i.geometry.y,i.geometry.z)
            comp: adsk.fusion.Component = pre_body.parentComponent
            group = comp.customGraphicsGroups.add()
            point_array = [pre_the_clostest_point.x,
                           pre_the_clostest_point.y,
                           pre_the_clostest_point.z]
            graphicscoordinates = adsk.fusion.CustomGraphicsCoordinates.create(
                point_array)
            self.cgcurve = group.addPointSet(graphicscoordinates, [0], adsk.fusion.CustomGraphicsPointTypes.UserDefinedCustomGraphicsPointType, ICON_FOLDER + '/icons8-select-10.png')
            
    def handle_pre_select_stop(self, args: adsk.core.SelectionEventHandler):
        event_args = adsk.core.SelectionEventArgs.cast(args)
        self.activeSelectionInput = event_args.firingEvent.activeInput
        
        pre_body = args.selection.entity
        if(pre_body.classType() == 'adsk::fusion::MeshBody'):
                return
        if self.activeSelectionInput.id == 'bodies_input':
            self.cgcurve.deleteMe()

    def calculate_dimensions(self):
        xmin = self.selected_body.minPoint.x
        xmax = self.selected_body.maxPoint.x
        ymin = self.selected_body.minPoint.y
        ymax = self.selected_body.maxPoint.y
        zmin = self.selected_body.minPoint.z
        zmax = self.selected_body.maxPoint.z
        self.calculated_x = xmax - xmin
        self.calculated_y = ymax - ymin
        self.calculated_z = zmax - zmin

    def update_values(self, value_x, value_y, value_z):
        self.set_x_dimension.value = value_x
        self.set_y_dimension.value = value_y
        self.set_z_dimension.value = value_z

        self.x_dimension.text = self.des.unitsManager.formatInternalValue(
            value_x)
        self.y_dimension.text = self.des.unitsManager.formatInternalValue(
            value_y)
        self.z_dimension.text = self.des.unitsManager.formatInternalValue(
            value_z)

    def update_visible_values(self):
        self.set_x_dimension.isVisible=self.visible_inputs
        self.set_y_dimension.isVisible=self.visible_inputs
        self.set_z_dimension.isVisible=self.visible_inputs

        self.x_dimension.isVisible = self.visible_inputs
        self.y_dimension.isVisible = self.visible_inputs
        self.z_dimension.isVisible = self.visible_inputs

        
        self.inputGroup.isVisible = self.visible_inputs
        self.print_group.isVisible = self.visible_inputs

    def calculate_scale(self):
        value_x = self.scale*self.calculated_x
        value_y = self.scale*self.calculated_y
        value_z = self.scale*self.calculated_z
        ResizerModifierLogic.update_values(self, value_x, value_y, value_z)

    def point_distance(x1,y1,z1,x2,y2,z2):
        p1 = [x1, y1 ,z1]
        p2 = [x2, y2, z2]
        distance = math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) +((p1[2]-p2[2])**2))
        return distance

    def get_the_clostest_vertice_of_selection(self,body,point):
        #get all vertices of selected body
        vPoint = body.vertices
        #get coodinate of point selection
        x2= point.x
        y2= point.y
        z2= point.z

        distances_of_pints=[]
        points=[]
        vertexs=[]
        
        for i in vPoint:
            p = ResizerModifierLogic.point_distance(x2,y2,z2,i.geometry.x,i.geometry.y,i.geometry.z)
            distances_of_pints.append(p)
            point_vertex = adsk.core.Point3D.create(i.geometry.x,i.geometry.y,i.geometry.z)
            points.append(point_vertex)
            vertexs.append(i)

        minlist = min(distances_of_pints)
        indexminlist = distances_of_pints.index(minlist)
        
        pre_vertexs = vertexs[indexminlist]

        return pre_vertexs


    