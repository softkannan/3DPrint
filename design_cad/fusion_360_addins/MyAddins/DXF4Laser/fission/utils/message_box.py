# -*- coding: utf-8 -*-
# from .fission.message_box import message_box
__all__ = ['message_box']
import adsk.core
def message_box(message):
  adsk.core.Application.get().userInterface.messageBox(message)