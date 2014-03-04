""" LegoBuilder - Maya Python Module"""

import maya.cmds as cmds

class Constants:
  """ This class contains any constant numbers that are required
      for constructing the various lego peices """
  def __init__(self):
    raise NotImplementedError("The constants class is a static implementation. Do not initialize it.")

class Generator:
  """ This class represents and interface that all LegoBuilder generators
      are required to adhere to. """
  @staticmethod
  def draw_ui():
    """ This method is required to be implemented by the superclass, 
        it should handle drawing and calling the UI and setting up 
        listeners to call the generate method on the right class. """
    raise NotImplementedError("Generator did not implement a draw_ui method")
  
  @staticmethod
  def generate(params):
    """ This method should be implemented by the superclass in order to """
    raise NotImplementedError("Generator did not implement a generate method")

class Block(Generator):
  """ Generates your standard lego block """

  @staticmethod
  def generate(params):
    print("Hello the world")
  
  @staticmethod
  def draw_ui():
    if cmds.window(__name__, exists=True):
      cmds.deleteUI(__name__)
    cmds.window(__name__)
    cmds.columnLayout(adjustableColumn=True)
    cmds.frameLayout(collapsable=True, label=__name__)
    cmds.flowLayout(wrap=1)
    cmds.button(command=Block.generate, label="test")
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.showWindow(__name__)

Block.draw_ui()




