# -*- coding: utf-8 -*-
import adsk.core, adsk.fusion
import traceback
import json
__all__ = ['CustomEventManager']


class _CustomEvent(adsk.core.CustomEventHandler):
  def __init__(self, event_name, callback):
    super().__init__()
    self._event_name = event_name
    self._callback = callback

  def notify(self, args):
    eargs = adsk.core.CustomEventArgs.cast(args)
    if eargs.additionalInfo:
      json_data = json.loads(eargs.additionalInfo)
      self._callback(**json_data)
    else:
       self._callback()

class CustomEventManager(object):
  def __init__(self):
    self._handlers = dict()

  def subscribe(self, event_name, callback):
    assert not(event_name in self._handlers), 'Only one handler per event is supported - ' + event_name

    app = adsk.core.Application.get()
    try:
      ce = app.registerCustomEvent(event_name)
    except:
      pass
    h = _CustomEvent(event_name, callback)
    ce.add(h)
    self._handlers[event_name] = h

  def trigger(self, event_name, **kwargs):
    app = adsk.core.Application.get()
    app.fireCustomEvent(event_name, json.dumps(kwargs))
