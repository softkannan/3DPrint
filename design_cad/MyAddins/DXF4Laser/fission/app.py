# -*- coding: utf-8 -*-
import adsk.core, adsk.fusion, traceback
import re, math, json
from numbers import Number
# from threading import Timer
from .utils.message_box import message_box
from .drawing.better_types import (MakeObjectCollection, Matrix)
# from.custom_events import CustomEventManager
# import ctypes
__all__ = ['CommandBase', 'InputFactory', 'CustomInputGroup', 'OverlappingInputGroup', 'ComponentUtils']


class OverlappingInputGroup(object):
  """Provides a way to control isVisible and isEnabled for overlapping groups of controls."""
  def __init__(self):
    self._inputs = []
    self._subgroups = []
    self._is_visible = True
    self._is_enabled = True

  @property
  def is_visible(self):
    return self._is_visible

  @is_visible.setter
  def is_visible(self, value):
    self.set_is_visible(value)

  def set_is_visible(self, value):
    if value:
      self.show()
    else:
      self.hide()

  @property
  def is_enabled(self):
    return self._is_enabled

  @is_enabled.setter
  def is_enabled(self, value):
    self.set_is_enabled(value)

  def set_is_enabled(self, value):
    if value:
      self.enable()
    else:
      self.disable()

  def append(self, input):
    if isinstance(input, OverlappingInputGroup):
      self._subgroups.append(input)
    else:
      if not hasattr(input, '_oig__hide_count'):
        input._oig__hide_count = 0
        input._oig__disable_count = 0
      self._inputs.append(input)

  def hide(self):
    if self._is_visible:
      self._is_visible = False
      self.__hide_inputs()

  def __hide_inputs(self):
    for i in self._inputs:
      i.isVisible = False
      i._oig__hide_count += 1
    for g in self._subgroups:
      g.__hide_inputs()

  def show(self):
    if not self._is_visible:
      self._is_visible = True
      self.__show_inputs()

  def __show_inputs(self):
    for i in self._inputs:
      i._oig__hide_count -= 1
      if i._oig__hide_count <= 0:
        i._oig__hide_count = 0
        i.isVisible = True
    for g in self._subgroups:
      g.__show_inputs()

  def disable(self):
    if self._is_enabled:
      self._is_enabled = False
      self.__disable_inputs()

  def __disable_inputs(self):
    for i in self._inputs:
      i.isEnabled = False
      i._oig__disable_count += 1
    for g in self._subgroups:
      g.__disable_inputs()

  def enable(self):
    if not self._is_enabled:
      self._is_enabled = True
      self.__enable_inputs()

  def __enable_inputs(self):
    for i in self._inputs:
      i._oig__disable_count -= 1
      if i._oig__disable_count <= 0:
        i._oig__disable_count = 0
        i.isEnabled = True
    for g in self._subgroups:
      g.__enable_inputs()


class CustomInputGroup(object):
  """Provides a simple way to hide and show a set of inputs."""
  def __init__(self):
    self._inputs = []

  def append(self, input):
    self._inputs.append(input)

  def hide(self):
    for i in self._inputs:
      i.isVisible = False

  def show(self):
    for i in self._inputs:
      i.isVisible = True

  def disable(self):
    for i in self._inputs:
      i.isEnabled = False

  def enable(self):
    for i in self._inputs:
      i.isEnabled = True


class Settings(object):
  def __init__(self, setting_group_name):
    self.__group_name = setting_group_name
    self.__tracked_inputs = dict()

  @property
  def group_name(self):
    assert self.__group_name, 'Settings must have a group name.'
    return self.__group_name

  @property
  def _attributes_collection(self):
    return adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct).attributes

  def _set_fqn(self, input):
    ipt = input
    fqn = ipt.id
    while ipt.parentCommandInput:
      ipt = ipt.parentCommandInput
      fqn = ipt.id + '^' + fqn
    input.fqn = fqn
    return fqn

  def save(self):
    catch_me = dict()
    for k, v in self.__dict__.items():
      if not re.match( r'^_Settings__.+', k ):
        catch_me[k] = v
    json_value = json.dumps(catch_me, sort_keys=True)
    # message_box('Preserving stored values\n' + json_value)
    self._attributes_collection.add(self.group_name, 'settings', json_value)

  def load(self):
    settings_attr = self._attributes_collection.itemByName(self.group_name, 'settings')
    if settings_attr:
      json_value = settings_attr.value
#      message_box('Loaded stored values\n' + json_value)
      loaded = json.loads( json_value )
      for k, v in loaded.items():
        self.__dict__[k] = v

  def track(self, input):
    self._set_fqn(input)
    assert input.fqn not in self.__tracked_inputs, 'Duplicate input ID: ' + input.fqn
    self.__tracked_inputs[input.fqn] = input
    if input.fqn in self.__dict__:
      self._restore(input)
    else:
      self._capture(input)
    return input

  def _restore(self, input):
    if input.fqn in self.__dict__:
      class_type = input.classType()
      if hasattr(input, 'expression'):
        input.expression = self.__dict__[input.fqn]
      elif hasattr(input, 'value'):
        v = self.__dict__[input.fqn]
        if isinstance(input, adsk.core.StringValueCommandInput):
          input.value = str(v)
        elif isinstance(input, adsk.core.IntegerSpinnerCommandInput):
          input.value = int(v)
        elif isinstance(input, adsk.core.BoolValueCommandInput):
          input.value = v
        else:
          message_box('I don\'t know what a {} wants for a value type! I\'ll try something...'.format(input.classType))
          input.value = v
      elif hasattr(input, 'listItems'):
        selected = self.__dict__[input.fqn]
        for _item in input.listItems:
          item = adsk.core.ListItem.cast(_item)
          item.isSelected = item.name in selected
      elif hasattr(input, 'formattedText'):
        input.formattedText = self.__dict__[input.fqn]
      elif class_type == 'adsk::core::GroupCommandInput':
        d = self.__dict__[input.fqn]
        input.isExpanded = d['is_expanded']
        input.isEnabledCheckBoxDisplayed = d['is_enabled_checkbox_displayed']
        input.isEnabled = d['is_enabled']
      elif class_type == 'adsk::core::TabCommandInput':
        d = self.__dict__[input.fqn]
        input.isVisable = d['is_visable']
        input.isEnabled = d['is_enabled']
        if d['is_active']:
          input.activate()
      else:
        assert False, 'I dont know how to restore ' + input.fqn + ' it\'s a ' + input.classType()
    return input

  def _capture(self, input):
    class_type = input.classType()
    if hasattr(input, 'expression'):
      self.__dict__[input.fqn] = input.expression
    elif hasattr(input, 'value'):
      self.__dict__[input.fqn] = input.value
    elif hasattr(input, 'listItems'):
      selected = []
      for _item in input.listItems:
        item = adsk.core.ListItem.cast(_item)
        if item.isSelected:
          selected.append(item.name)
      self.__dict__[input.fqn] = selected
    elif hasattr(input, 'formattedText'):
      self.__dict__[input.fqn] = input.formattedText
    elif class_type == 'adsk::core::GroupCommandInput':
      self.__dict__[input.fqn] = {
        'is_expanded': input.isExpanded,
        'is_enabled_checkbox_displayed': input.isEnabledCheckBoxDisplayed,
        'is_enabled': input.isEnabled
      }
    elif class_type == 'adsk::core::TabCommandInput':
      self.__dict__[input.fqn] = {
        'is_active': input.isActive,
        'is_visable': input.isVisable,
        'is_enabled': input.isEnabled
      }
    else:
      assert False, 'I dont know how to capture ' + input.fqn + ' it\'s a ' + input.classType()

    try:
      json.dumps( self.__dict__[input.fqn] )
    except TypeError:
      err = input.fqn + ' is not being properly captured'
      if hasattr(input, 'classType'):
        err += '\n  Class Type: ' + input.classType()
      else:
        err += '\n  Type: ' + type(input).__name__

      if hasattr(input, 'expression'):
        err += '\n  expression: ' + input.expression
      if hasattr(input, 'value'):
        err += '\n  value: ' + str(input.value)
      if hasattr(input, 'listItems'):
        err += '\n  listItems: ' + str(input.listItems.count)
      if hasattr(input, 'formattedText'):
        err += '\n  formattedText: ' + input.formattedText

      adsk.core.Application.get().userInterface.messageBox(err)
    return input

  def restore_all(self):
    """Restores tracked input field values from the values held by this settings object."""
    for _, i in self.__tracked_inputs.items():
      self._restore(i)

  def capture_all(self):
    """Captures all tracked input field values into this settings object."""
    for _, i in self.__tracked_inputs.items():
      self._capture(i)


class FusionEventHandler(object):
  """Makes wiering up to Fusion events dead simple and friendly!

  Usage:
    Inherit from this class and call self._auto_wire(command) at some point.
    Annotate the methods you wish to handle events using the return
    annotation to indicate which event to wire to.

  Example Annotation:
    def on_execute(self, args) -> 'execute':
      self.ui.messageBox('EXECUTE')

  NOTICE:
    Only one subscribing method per event source, per class instance, is supported.
    If the same event source is subscribed to multiple times only one method will
    receive events.

  Supported Event Names:
    command_created (may not be autowired)
    destroy
    execute
    activate
    deactivate
    preview
    input_changed
    validate_inputs
    key_down
    key_up
    mouse_click
    mouse_double_click
    mouse_down
    mouse_move
    mouse_up
    mouse_wheel
    mouse_drag_begin
    mouse_drag
    mouse_drag_end
    selecting
  """

  def __init__(self):
    self.__event_handlers = dict()

  def __handler_factory(self, event, callback, handler_cls ):
    """Factory method to create handler classes and bind them to Fusion event sources.

    Args:
      event: object - on which to call .add passing the handler instance
      callback: function - which will be called when the event fires
      handler_cls: type - one of the adsk.core.*EventHandler types

    Returns:
      Instance of a handler if subscription to event was successfull, None otherwise.
    """
    class _Handler(handler_cls):
      def __init__(self):
        super().__init__()
        self._wired = False

      def notify(self, *args):
        try:
           callback(*args)
        except Exception as ex:
          #adsk.core.Application.get().userInterface.messageBox('Failed:\n{}'.format(traceback.format_exc()))
          adsk.core.Application.get().userInterface.messageBox(
              '{}\n\n--------\n{}'.format(ex, traceback.format_exc()),
              'Error')

      def wire(self):
        if not self._wired:
          self._wired = event.add(self)
          assert self._wired, 'Failed to wire'
        return self._wired

      def unwire(self):
        if self._wired:
          assert event.remove(self), 'Failed to unwire'
          self._wired = False

      @property
      def is_wired(self):
        return self._wired

    h = _Handler()
    return h if h.wire() else None

  def _wire_event(self, command, event, callback ):
    """Subscribes a listener to an event trigger.

    See core.py near line 2977

    Args:
      command: adsk.core.Command or adsk.core.CommandDefinitions
      event: string
      callback: Function - which will be called when the event fires
    """
    _wire_handler = self.__handler_factory
    events = {
      'command_created': lambda command, callback: _wire_handler(command.commandCreated, callback, adsk.core.CommandCreatedEventHandler),
      'destroy': lambda command, callback: _wire_handler(command.destroy, callback, adsk.core.CommandEventHandler),
      'execute': lambda command, callback: _wire_handler(command.execute, callback, adsk.core.CommandEventHandler),
      'activate': lambda command, callback: _wire_handler(command.activate, callback, adsk.core.CommandEventHandler),
      'deactivate': lambda command, callback: _wire_handler(command.deactivate, callback, adsk.core.CommandEventHandler),
      'preview': lambda command, callback: _wire_handler(command.executePreview, callback, adsk.core.CommandEventHandler),
      'input_changed': lambda command, callback: _wire_handler(command.inputChanged, callback, adsk.core.InputChangedEventHandler),
      'validate_inputs': lambda command, callback: _wire_handler(command.validateInputs, callback, adsk.core.ValidateInputsEventHandler),
      'key_down': lambda command, callback: _wire_handler(command.keyDown, callback, adsk.core.KeyboardEventHandler),
      'key_up': lambda command, callback: _wire_handler(command.keyUp, callback, adsk.core.KeyboardEventHandler),
      'mouse_click': lambda command, callback: _wire_handler(command.mouseClick, callback, adsk.core.MouseEventHandler),
      'mouse_double_click': lambda command, callback: _wire_handler(command.mouseDoubleClick, callback, adsk.core.MouseEventHandler),
      'mouse_down': lambda command, callback: _wire_handler(command.mouseDown, callback, adsk.core.MouseEventHandler),
      'mouse_move': lambda command, callback: _wire_handler(command.mouseMove, callback, adsk.core.MouseEventHandler),
      'mouse_up': lambda command, callback: _wire_handler(command.mouseUp, callback, adsk.core.MouseEventHandler),
      'mouse_wheel': lambda command, callback: _wire_handler(command.mouseWheel, callback, adsk.core.MouseEventHandler),
      'mouse_drag_begin': lambda command, callback: _wire_handler(command.mouseDragBegin, callback, adsk.core.MouseEventHandler),
      'mouse_drag': lambda command, callback: _wire_handler(command.mouseDrag, callback, adsk.core.MouseEventHandler),
      'mouse_drag_end': lambda command, callback: _wire_handler(command.mouseDragEnd, callback, adsk.core.MouseEventHandler),
      'selecting': lambda command, callback: _wire_handler(command.selectionEvent, callback, adsk.core.SelectionEventHandler)}
    h = events[event](command, callback) if event in events else None

    if h: self.__event_handlers[event] = h

  def _auto_wire(self, command):
    for name in dir(self):
      attr = getattr(self, name)
      if callable(attr) and hasattr(attr,'__annotations__') and 'return' in attr.__annotations__:
        self._wire_event(command, attr.__annotations__['return'], attr)

  def susspend_handler(self, event_name):
    if event_name in self.__event_handlers:
      h = self.__event_handlers[event_name]
      h.unwire()

  def resume_handler(self, event_name):
    if event_name in self.__event_handlers:
      h = self.__event_handlers[event_name]
      h.wire()

class CommandBase(FusionEventHandler):
  """Base class for creating Command objects."""
  def __init__(self):
    super().__init__()
    self.design = DesignUtils()
    #self._custom_event_manager = CustomEventManager()

  def fire_preview(self):
    pass
    #self._custom_event_manager.trigger('rvk_do_preview')
    #self.resume_handler('preview')
    #self.__command.doExecutePreview()
    #self.susspend_handler('preview')
    #self._preview_delay_timer = None
    # message_box("FIRE preview")

  def do_the_preview(self):
    pass
    #ctypes.windll.user32.MessageBoxW(0, 'Preview Fire timer', 'Message', 1)
    #self.resume_handler('preview')
    #self.__command.doExecutePreview()
    #self.susspend_handler('preview')
    #self._preview_delay_timer = None
    # message_box("FIRE preview")

  @property
  def app(self):
    return adsk.core.Application.get()

  @property
  def ui(self):
    return self.app.userInterface

  @property
  def command_id(self):
    return type(self).__name__

  @property
  def command_name(self):
    return self.command_id

  @property
  def command_description(self):
    return type(self).__doc__ or ''

  @property
  def is_repeatable(self):
    return True

  @property
  def resource_dir(self):
    return ''

  def run(self):
    try:
      # resource_dir = os.path.abspath('resources')
      # self.resource_dir = resource_dir if os.path.isdir(resource_dir) else ''
      self._command_definition = self.ui.commandDefinitions.itemById(self.command_id)
      if not self._command_definition:
        self._command_definition = self.add_button()
      assert self._command_definition, 'Script/Addin failed to produce a \'button\''
      self._command_definition.isAutoExecute = False
      self._wire_event(self._command_definition, 'command_created', self.__on_create)

    except:
      self.ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

  def add_button(self):
    """Called at an appropriate time to add a button to one of Fusions menus.

    Overriders of this method should call super(), then they can add the button to the Fusion menu system if desired.
    Finally the button object must be returned.
    Returns:
      ButtonDefinition
    """
    return self.ui.commandDefinitions.addButtonDefinition(
      self.command_id,
      self.command_name,
      self.command_description,
      self.resource_dir)

  def remove_button(self):
    pass

  def stop(self, context):
    if self._command_definition:
      self._command_definition.deleteMe()
      self.remove_button()
      
  def show(self):
    """Triggers the command as if the user clicked the menu item / ran the command."""
    if self._command_definition:
      self._command_definition.execute()

  def __on_create(self, _args):
    args = adsk.core.CommandCreatedEventArgs.cast(_args)
    self._command = args.command
    self._command.isRepeatable = self.is_repeatable
    self.settings = Settings(self.command_id)
    self.settings.load()
    self.input_factory = InputFactory(self._command, self.settings)
    self.initialize_inputs(self.input_factory)
    self._auto_wire(self._command)
    # self._custom_event_manager.subscribe('rvk_do_preview', self.do_the_preview)

  def initialize_inputs(self, factory):
    """Override this method and perform all UI initialization here."""
    pass

  def preserve_inputs(self):
    self.settings.capture_all()
    self.settings.save()

#class ScriptBase(CommandBase):
#  """Base class for scripts, Add-In's should create one or more CommandBase derived classes.
#  """
#  def __init__(self):
#    super().__init__()
#
#  @property
#  def is_repeatable(self):
#    return False
#
#  def run(self):
#    super().run()
#    # This is the same is if we had added a button to a menu and the user had clicked it
#    self._command_definition.execute()
#    # prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire
#    adsk.autoTerminate(False)
#
#  def on_destroy(self, args) -> 'destroy':
#    adsk.terminate()


class InputFactory(FusionEventHandler):
  """Simplifies the creation and usage of UI input elements (text boxes, buttons, etc).
  """

  def __init__(self, command, settings_manager):
    super().__init__()
    self.__active_custom_input_group = None
    self.__command = adsk.core.Command.cast(command)
    self.__settings_manager = settings_manager
    self.__active_inputs_context = self.__command.commandInputs  # new inputs will be added to this context
    self.__base_inputs_context = self.__command.commandInputs  # in the event the groups stack is cleared this context gets set as active. This will either be the main control form or a tab, never a group.
    self.__input_group_stack = []
    self.__change_callbacks = dict()
    self.__validate_callbacks = dict()
    self._design_utils = DesignUtils()
    self._unitsMgr = adsk.core.Application.get().activeProduct.unitsManager
    self._additional_validator = None
    self._auto_wire(self.__command)
    self._preview_delay_timer = None
#    self._custom_event_manager = CustomEventManager()
#    self._custom_event_manager.subscribe('rvk_do_preview', self.do_the_preview)
#
#  def fire_preview(self):
#    self._custom_event_manager.trigger('rvk_do_preview')
#    #self.resume_handler('preview')
#    #self.__command.doExecutePreview()
#    #self.susspend_handler('preview')
#    #self._preview_delay_timer = None
#    # message_box("FIRE preview")
#
#  def do_the_preview(self):
#    ctypes.windll.user32.MessageBoxW(0, 'Preview Fire timer', 'Message', 1)
#    #self.resume_handler('preview')
#    #self.__command.doExecutePreview()
#    #self.susspend_handler('preview')
#    #self._preview_delay_timer = None
#    # message_box("FIRE preview")

  @property
  def additional_validator(self):
    return self._additional_validator

  @additional_validator.setter
  def additional_validator(self, value):
    self._additional_validator = value

  @additional_validator.deleter
  def additional_validator(self):
    del self._additional_validator

  def __on_input_changed(self, _a) -> 'input_changed':
#    if self._preview_delay_timer:
#      self._preview_delay_timer.cancel()
#    self._preview_delay_timer = Timer(2, self.fire_preview)
#    self._preview_delay_timer.start()
    args = adsk.core.InputChangedEventArgs.cast(_a)
    input = args.input
    if input.id in self.__change_callbacks:
      (cb, i) = self.__change_callbacks[input.id]
      cb(i)

  def trigger_all_change_handlers(self):
    for k, (cb, i) in self.__change_callbacks.items():
      cb(i)

  def __on_validate(self, _a) -> 'validate_inputs':
    args = adsk.core.ValidateInputsEventArgs.cast(_a)
    valid = True
    for input_id, (cb, input) in self.__validate_callbacks.items():
      try:
        valid &= cb(input)
        #if not valid:
        #  adsk.core.Application.get().userInterface.messageBox('{} is not valid'.format(input_id))
      except:  # Exception as ex:
        #adsk.core.Application.get().userInterface.messageBox('Validation of {} raised\n{}'.format(input_id, repr(ex)))
        valid = False
       # if not valid: break
    args.areInputsValid &= valid
    if self._additional_validator and callable(self._additional_validator):
      self._additional_validator(args)

  @property
  def settings_manager(self):
    return self.__settings_manager

  @staticmethod
  def _ValueInput(value):
    v = None
    if isinstance(value, Number):
      v = adsk.core.ValueInput.createByReal(value)
    elif isinstance(value, str):
      v = adsk.core.ValueInput.createByString(value)
    else:
      v = adsk.core.ValueInput.createByObject(value)
    return v

  def handle_change(self, input, callback):
    if callback and callable(callback):
      self.__change_callbacks[input.id] = (callback, input)
    elif input.id in self.__change_callbacks:
      del self.__change_callbacks[input.id]

  def handle_validate(self, input, callback):
    """This function will be called OFTEN to validate an inputs value."""
    if callback and callable(callback):
      self.__validate_callbacks[input.id] = (callback, input)
      input.validate = lambda: callback(input)
    elif input.id in self.__validate_callbacks:
      del self.__validate_callbacks[input.id]

  def _set_tips(self, input, name, tooltip, description, help_image):
    if tooltip:
      input.tooltip = tooltip
    elif description:
      input.tooltip = name
    if description: input.tooltipDescription = description
    if help_image: input.toolClipFilename = help_image

  def create_int_spinner(self, id, name, initial_value=0, min_value=-2147483648, max_value=2147483647, step=1, tooltip='', description='', help_image=None, on_change=None, on_validate=None, persist=True):
    input = self.__active_inputs_context.addIntegerSpinnerCommandInput (id, name, min_value, max_value, step, initial_value)
    self._set_tips(input, name, tooltip, description, help_image)
    input.eval = lambda: max(min_value, min(input.value, max_value))
    self.handle_validate(input, on_validate)
    self.handle_change(input, on_change)
    if persist:
      self.settings_manager.track(input)
    return self._try_add_to_custom_input_group(input)

  def addValueInput(self, id, name, initial_value, units, tooltip='', description='', help_image=None, on_change=None, on_validate=None, persist=True):
    iv = InputFactory._ValueInput(initial_value)
    input = self.__active_inputs_context.addValueInput(id, name, units, iv)
    self._set_tips(input, name, tooltip, description, help_image)
    um = self._unitsMgr
    input.eval = lambda: um.evaluateExpression(input.expression, units)
    self.handle_change(input, on_change)
    self.handle_validate(input, on_validate)
    if persist:
      self.settings_manager.track(input)
    return self._try_add_to_custom_input_group(input)

  def addStringInput(self, id, name, initial_value='', tooltip='', description='', help_image=None, on_change=None, on_validate=None, on_eval=None, persist=True):
    input = self.__active_inputs_context.addStringValueInput(id, name, str(initial_value))
    self._set_tips(input, name, tooltip, description, help_image)
    self.handle_change(input, on_change)
    self.handle_validate(input, on_validate)
    if on_eval:
      input.eval = lambda: on_eval(input)
    else:
      input.eval = lambda: input.value
    if persist:
      self.settings_manager.track(input)
    return self._try_add_to_custom_input_group(input)

  def create_float_input(self, id, name, initial_value=0, min_value=-2147483648, max_value=2147483647, default=math.nan, tooltip='', description='', help_image=None, on_change=None, on_validate=None, persist=True):
    on_eval = lambda __ipt: max(min_value, min(float(__ipt.value), max_value)) if __ipt.value else default
    # TODO: add custom validation and validation cascading... and user param expansion
    input = self.addStringInput(id, name, initial_value, tooltip, description, help_image, on_change, on_validate, on_eval, persist)
    return input  # already tracked in a custom group by addStringInput

  def addSelectionInput(self, id, name, prompt=None, filter=None, tooltip='', description='', help_image=None, on_change=None, on_validate=None, persist=False):
    input = self.__active_inputs_context.addSelectionInput(id, name, prompt )
    self._set_tips(input, name, tooltip, description, help_image)
    if filter:
      for f in filter:
        input.addSelectionFilter(f)
    self.handle_change(input, on_change)
    self.handle_validate(input, on_validate)
    if persist:
      self.settings_manager.track(input)
    return self._try_add_to_custom_input_group(input)


  def _populate_list_items(self, input, items, values, icons, default):
    assert len(values) == 0 or len(values) == len(items), 'Number of items and values did not match'
    if len(values) == 0:
      for item in items:
        input.listItems.add(item, item == default)
      input.eval = lambda: input.selectedItem.name
    else:
      value_lookup = dict()
      item_values = zip(items, values)
      for (item, value) in item_values:
        input.listItems.add(item, item == default)
        value_lookup[item] = value
      input.eval = lambda: value_lookup[input.selectedItem.name]

  def create_text_drop_down(self, id, name, items=[], default=None, values=[], tooltip='', description='', help_image=None, on_change=None, on_validate=None, persist=True):
    input = self.__active_inputs_context.addDropDownCommandInput(id, name, adsk.core.DropDownStyles.TextListDropDownStyle)
    self._set_tips(input, name, tooltip, description, help_image)
    self._populate_list_items(input, items, values, [], default)
    self.handle_change(input, on_change)
    self.handle_validate(input, on_validate)
    if persist:
      self.settings_manager.track(input)
    return self._try_add_to_custom_input_group(input)

  def create_checkbox_drop_down(self, id, name, items=[], default=None, values=[], tooltip='', description='', help_image=None, on_change=None, on_validate=None, persist=True):
    input = self.__active_inputs_context.addDropDownCommandInput(id, name, adsk.core.DropDownStyles.CheckBoxDropDownStyle)
    self._set_tips(input, name, tooltip, description, help_image)
    self._populate_list_items(input, items, values, [], default)
    self.handle_change(input, on_change)
    self.handle_validate(input, on_validate)
    if persist:
      self.settings_manager.track(input)
    return self._try_add_to_custom_input_group(input)

  def create_radio_group(self, id, name, items=[], default=None, values=[], tooltip='', description='', help_image=None, on_change=None, on_validate=None, persist=True, full_width=True):
    input = self.__active_inputs_context.addRadioButtonGroupCommandInput(id, name)
    self._set_tips(input, name, tooltip, description, help_image)
    self._populate_list_items(input, items, values, [], default)
    self.handle_change(input, on_change)
    self.handle_validate(input, on_validate)
    if persist:
      self.settings_manager.track(input)
    input.isFullWidth = full_width
    return self._try_add_to_custom_input_group(input)

  def create_button_row(self, id, name, items=[], default=None, values=[], tooltip='', description='', help_image=None, on_change=None, on_validate=None, persist=True, full_width=False, multiselect=False):
    input = self.__active_inputs_context.addButtonRowCommandInput(id, name, multiselect)
    self._set_tips(input, name, tooltip, description, help_image)
    self._populate_list_items(input, items, values, [], default)
    self.handle_change(input, on_change)
    self.handle_validate(input, on_validate)
    if persist:
      self.settings_manager.track(input)
    input.isFullWidth = full_width
    return self._try_add_to_custom_input_group(input)

  def create_checkbox(self, id, name, initial_value=False, tooltip='', description='', help_image=None, on_change=None, on_validate=None, persist=True):
    input = self.__active_inputs_context.addBoolValueInput(id, name, True, '', initial_value)
    self._set_tips(input, name, tooltip, description, help_image)
    self.handle_change(input, on_change)
    self.handle_validate(input, on_validate)
    input.eval = lambda: input.value
    if persist:
      self.settings_manager.track(input)
    return self._try_add_to_custom_input_group(input)

  def create_textbox(self, id, name='', text='', height=2, read_only=False, tooltip='', description='', help_image=None, on_change=None, on_validate=None, persist=True, full_width=True):
    input = self.__active_inputs_context.addTextBoxCommandInput(id, name, text, height, read_only)
    input.isFullWidth = full_width
    self._set_tips(input, name, tooltip, description, help_image)
    self.handle_change(input, on_change)
    self.handle_validate(input, on_validate)
    if persist:
      self.settings_manager.track(input)
    return self._try_add_to_custom_input_group(input)

  def start_custom_input_group(self):
    ig = CustomInputGroup()
    self.__active_custom_input_group = ig
    return ig

  def set_active_custom_input_group(self, custom_input_group):
    self.__active_custom_input_group = custom_input_group
    return custom_input_group

  def close_custom_input_group(self):
    self.__active_custom_input_group = None

  def _try_add_to_custom_input_group(self, input):
    if self.__active_custom_input_group:
      self.__active_custom_input_group.append(input)
    return input

  def add_split(self, caption=None):
    if caption:
      return self._try_add_to_custom_input_group(
        self.create_textbox(
          'spacer_' + str(self.__active_inputs_context.count),
          full_width=True,
          text='<hr /><b>' + caption + '</b>',
          height=2,
          read_only=True,
          persist=False))
    else:
      return self._try_add_to_custom_input_group(
        self.create_textbox(
          'spacer_' + str(self.__active_inputs_context.count),
          full_width=True,
          text='<hr />',
          height=1,
          read_only=True,
          persist=False))

  def begin_group(self, id, name, enabled=True, expanded=False, show_enable_checkbox=False, persist=True):
    """Creates a Group, all inputs which are added following this call will be added to the group. Use close_group
    to stop adding items to this group.

    Groups may contain other groups, but nested groups must be expanded.
    """
    input = self.__active_inputs_context.addGroupCommandInput(id, name)
    input.isEnabled = enabled
    # Groups must be expanded if contained within another group
    input.isExpanded = expanded or len(self.__input_group_stack) > 0
    input.isEnabledCheckBoxDisplayed = show_enable_checkbox
    self.__input_group_stack.append(self.__active_inputs_context)
    self.__active_inputs_context = input.children
    if persist:
      self.settings_manager.track(input)
    return self._try_add_to_custom_input_group(input)

  def close_group(self):
    if len(self.__input_group_stack):
      self.__active_inputs_context = self.__input_group_stack.pop()
    else:
      self.__active_inputs_context = self.__base_inputs_context

  def close_all_groups(self):
    self.__input_group_stack.clear()
    self.__active_inputs_context = self.__base_inputs_context

  def begin_tab(self, id, name, resource_folder = '', active=False, enabled=True, visable=True, tooltip='', description='', help_image=None, persist=False):
    """Creates a new Tab - all inputs added following this call will be added to this tab.

    Tabs may not be added to groups or other tabs. As such, beginging a tab "closes" any open groups or other tabs.

    Controls which exist outside of a tab will always be shown either above or below the tabs content depending on
    the order the controls were created relative to the tab.
    """
    self.close_all_groups()
    # Tabs may only be added to the main form, hence use of self.__command.commandInputs here.
    input = adsk.core.TabCommandInput.cast(self.__command.commandInputs.addTabCommandInput(id, name, resource_folder))
    input.isEnabled = enabled
    input.isVisable = visable
    input.isActive = active
    self.__base_inputs_context = input.children
    self.__active_inputs_context = self.__base_inputs_context
    self._set_tips(input, name, tooltip, description, help_image)
    if persist:
      self.settings_manager.track(input)
    return self._try_add_to_custom_input_group(input)

  def close_tab(self):
    self.__input_group_stack.clear()
    self.__base_inputs_context = self.__command.commandInputs
    self.__active_inputs_context = self.__base_inputs_context


class ComponentUtils(object):
  @staticmethod
  def create_offset_plane(component, ref_plane, offset):
    plane_input = component.constructionPlanes.createInput()
    plane_input.setByOffset(ref_plane, adsk.core.ValueInput.createByReal(offset))
    plane = component.constructionPlanes.add(plane_input)
    return adsk.fusion.ConstructionPlane.cast(plane)

  @staticmethod
  def extrude(component, profile, thickness):
    extrudes = component.features.extrudeFeatures
    extInput = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(thickness)
    extInput.setDistanceExtent(False, distance)
    return adsk.fusion.BRepBody.cast(extrudes.add(extInput).bodies[0])

  @staticmethod
  def combine_join(component, target_body, tool_bodies, keep_tools=False):
    oc = MakeObjectCollection(tool_bodies)
    combine_input = component.features.combineFeatures.createInput(target_body, oc)
    combine_input.isKeepToolBodies = keep_tools
    return component.features.combineFeatures.add(combine_input)  # .bodies[0]

  @staticmethod
  def combine_cut(component, target_body, tool_bodies, keep_tools=False):
    oc = MakeObjectCollection(tool_bodies)
    combine_input = component.features.combineFeatures.createInput(target_body, oc)
    combine_input.isKeepToolBodies = keep_tools
    combine_input.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
    return component.features.combineFeatures.add(combine_input)  # .bodies[0]

  @staticmethod
  def combine_intersect(component, target_body, tool_bodies, keep_tools=False):
    oc = MakeObjectCollection(tool_bodies)
    combine_input = component.features.combineFeatures.createInput(target_body, oc)
    combine_input.isKeepToolBodies = keep_tools
    combine_input.operation = adsk.fusion.FeatureOperations.IntersectFeatureOperation
    return component.features.combineFeatures.add(combine_input)  # .bodies[0]

  @staticmethod
  def mirror(component, entities, plane):
    oc = MakeObjectCollection(entities)
    mirror_input = component.features.mirrorFeatures.createInput(oc, plane)
    return component.features.mirrorFeatures.add(mirror_input)


class DesignUtils(object):
  def __init__(self):
    pass

  @property
  def _app(self):
    return adsk.core.Application.get()

  @property
  def _product(self):
    return self._app.activeProduct

  @property
  def design(self):
    return adsk.fusion.Design.cast(self._product)

  @property
  def root_component(self):
    return self.design.rootComponent

  def CreateNewComponent(self, parent=None, transform=None):
    if not transform:
      transform = adsk.core.Matrix3D.create()
    elif isinstance(transform, Matrix):
      transform = transform.as_fusion_matrix3D()
    if not parent:
      parent = self.root_component
    occurrence = parent.occurrences.addNewComponent(transform)
    component = occurrence.component
    component.occurrence = occurrence
    return adsk.fusion.Component.cast(component)

  def ActivateRootComponent(self):
    self.design.activateRootComponent()

  def GetUserParameterValue(self, parameter_name):
    """Gets a user parameter value by name.

      Args
        parameter_name (string) parameter name
      Returns
        value (double) or None
    """
    param = self.design.userParameters(parameter_name)
    return param.value if param else None
