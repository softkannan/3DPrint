import adsk.core
import adsk.fusion
from ....lib import fusion360utils as futil


CMD_NAME = 'Resizer Modifier'
app = adsk.core.Application.get()
ui = app.userInterface

class ResizerModifierExecute():
    futil.log(f'{CMD_NAME} function exe testtest')
