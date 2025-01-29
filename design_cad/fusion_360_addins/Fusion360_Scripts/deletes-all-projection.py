#Author-Sam Chaney
#Description-Selects and deletes all projected sketch entities

import adsk.core, adsk.fusion, adsk.cam, traceback, sys

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        active_component = design.activeComponent
        sketches = active_component.sketches
        active_sketch = adsk.core.Application.get().activeEditObject #Use this instead of chosen_sketch if you want to use active sketch
        
        sketch_name, cancelled  = ui.inputBox('Enter exact name of sketch to delete projected entities')
        if cancelled:
            ui.messageBox('Cancelled!')
            sys.exit('Cancelled')
        if sketches.itemByName(sketch_name) is None:
            ui.messageBox(f'Sketch named "{sketch_name}" not found')
            sys.exit('Sketch not found')

        chosen_sketch = sketches.itemByName(sketch_name)
        
        curves = chosen_sketch.sketchCurves
        # ui.messageBox(f'Curve count is {curves.count}')
        lines = curves.sketchLines
        points = chosen_sketch.sketchPoints

        def is_projected(entity):
            if entity.isLinked:
                return True
            else:
                return False

        def delete_projected(collection):
            for entity in list(collection):
                if entity.isLinked:
                    # ui.messageBox('entity was linked')
                    entity.deleteMe()
                
        def delete_all(collection):
            for entity in list(collection):
                entity.deleteMe # should delete all entities in collection no matter what
    
        delete_projected(curves)
        delete_projected(points)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))