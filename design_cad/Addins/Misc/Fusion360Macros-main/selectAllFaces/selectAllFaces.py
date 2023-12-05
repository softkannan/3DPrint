#Author-Jay Deaton
#Description-Select all faces of a body

import adsk.core, adsk.fusion, adsk.cam, traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        design = app.activeProduct
        if not design: return ui.messageBox('No active Fusion design', 'No Design')
        if len(ui.activeSelections) == 0: return ui.messageBox('First select components or bodies')

        faces = []
        for selection in ui.activeSelections:
            selectedEnt = selection.entity
            try:
                if selectedEnt.objectType == adsk.fusion.BRepBody.classType():
                    for face in selectedEnt.faces:
                        faces.append(face)
                elif selectedEnt.objectType == adsk.fusion.Occurrence.classType():
                    for body in selectedEnt.bRepBodies:
                        for face in body.faces: faces.append(face)
            except:
                if ui: ui.messageBox(f'Failed:\n{traceback.format_exc()}')
                continue

        ui.activeSelections.clear()
        for face in faces: ui.activeSelections.add(face)

        ui.messageBox(f'Selected {len(faces)} Faces')
    except:
        if ui: ui.messageBox(f'Failed:\n{traceback.format_exc()}')
