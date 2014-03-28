""" LegoBuilder - Maya Python Module"""

import maya.cmds as cmds
import re

# use the next available id
all_scene_objects = cmds.ls() 
matching_objects = []
for name in all_scene_objects:
    regex = re.compile('\d+')
    match = regex.search(name) 
    if match is not None:
        matching_objects.append(match.group())
used_ids = []
for integer in matching_objects:
    used_ids.append(int(integer))
    
    

next_id = max(used_ids)

Constants = {
  "window_width" : 500,
  "window_height" : 400,
  "window_padding" : 10,
  "block_height_unit" : 1,
  "block_width_unit" : 1,
  "block_depth_unit" : 1,
  "stub_height" : 0.1,
  "stub_radius" : 0.3,
  "perforation_radius" : 0.3,
  "min_block_width" : 2,
  "max_block_width" : 10,
  "min_block_height" : 1,
  "max_block_height" : 3,
  "wheel_min_radius" : 2,
  "wheel_radius_unit" : 1,
  "wheel_ridge_depth" : 0.1,
  "wheel_height_unit" : 0.5,
  "wheel_min_subdivs" : 5,
  "wheel_max_subdivs" : 30
}

Labels = {
  "width_label" : "Width",
  "depth_label" : "Depth",
  "height_label" : "Height",
  "dimensions_label" : "Dimensions",
  "before_kink_label" : "before_kink",
  "after_kink_label" : "after_kink",
  "radius_label" : "Radius",
  "subdivs_label" : "Subdivs",
  "color_label" : "Color"
}

#Functions for readability.
def half(num):
  return num/2.00

def twice(num):
  return num*2.00

def get_unique_name(prefix, identifier):
  global next_id
  next_id += 1
  return prefix + "_" + identifier + "_" + "%03d" % (next_id,)




class Generator:
  """ This class represents and interface that all LegoBuilder generators
      are required to adhere to. """

  @classmethod
  def get_prefix(cls):
    return cls.__name__

  @classmethod
  def draw_ui(cls, *args):
    """ This method is required to be implemented by the superclass, 
        it should handle drawing and calling the UI and setting up 
        listeners to call the generate method on the right class. """
    raise NotImplementedError("Generator did not implement a draw_ui method")
  
  @classmethod
  def generate(cls, *args):
    """ This method should be implemented by the superclass in order to """
    raise NotImplementedError("Generator did not implement a generate method")

# GENERATORS

class Block(Generator):
  """ Generates your standard lego block """
  @classmethod
  def generate(cls, *args):
    components = []
    width = cmds.intSliderGrp(cls.get_prefix() + Labels["width_label"], query=True, value=True)
    height = cmds.intSliderGrp(cls.get_prefix() + Labels["height_label"], query=True, value=True)
    depth = cmds.intSliderGrp(cls.get_prefix() + Labels["depth_label"], query=True, value=True)
    rgb = cmds.colorSliderGrp(cls.get_prefix() + Labels["color_label"], query=True, rgbValue=True)

    block_width = width * Constants["block_width_unit"]
    block_height = height * Constants["block_height_unit"]
    block_depth = depth * Constants["block_depth_unit"]

    #stubs
    for x in range(0, width):
      for z in range(0, depth):
        stub = cmds.polyCylinder(name=get_unique_name(cls.get_prefix(), "Stub"), radius=Constants["stub_radius"], height = Constants["stub_height"])
        components.append(stub[0])
        cmds.move(Constants["block_width_unit"] * x + half(Constants["block_width_unit"]), half(Constants["block_height_unit"]) * height + half(Constants["stub_height"]), Constants["block_depth_unit"] * z + half(Constants["block_depth_unit"]), stub[0])

    cube = cmds.polyCube(name=get_unique_name(cls.get_prefix(), "block"), width=block_width, height=block_height, depth=block_depth)
    components.append(cube[0])
    cmds.move(half(width * Constants["block_width_unit"]), 0, half(depth * Constants["block_depth_unit"]), cube)
    if components.count > 1:
      final = cmds.polyUnite(components, name=get_unique_name(cls.get_prefix(), ""))
    else:
      final = components[0]

    shader = cmds.shadingNode('blinn', asShader=True, name=get_unique_name(cls.get_prefix(),"mat"))
    cmds.setAttr(shader + ".color", rgb[0],rgb[1],rgb[2], type='double3')
    cmds.select(final[0], r=True)
    cmds.hyperShade(assign=shader)

  
  @classmethod
  def draw_ui(cls, *args):
    if cmds.window(cls.get_prefix(), exists=True):
      cmds.deleteUI(cls.get_prefix())
    cmds.window(cls.get_prefix())
    cmds.columnLayout(adjustableColumn=True, width=Constants["window_width"], height=Constants["window_height"])
    cmds.frameLayout(collapsable=True, width=Constants["window_width"], label=Labels["dimensions_label"])
    cmds.columnLayout(width=Constants["window_width"])
    
    cmds.text(Labels["width_label"])
    width_slider = cmds.intSliderGrp(cls.get_prefix() + Labels["width_label"], annotation=Labels["width_label"], width=Constants["window_width"], minValue=Constants["min_block_width"], maxValue=Constants["max_block_width"], value=3, field=True)
    cmds.text(Labels["height_label"])
    height_slider = cmds.intSliderGrp(cls.get_prefix() + Labels["height_label"], annotation=Labels["height_label"], width=Constants["window_width"], minValue=Constants["min_block_height"], maxValue=Constants["max_block_height"], value=3, field=True)
    cmds.text(Labels["depth_label"])
    depth_slider = cmds.intSliderGrp(cls.get_prefix() + Labels["depth_label"], annotation=Labels["depth_label"], width=Constants["window_width"], minValue=Constants["min_block_width"], maxValue=Constants["max_block_width"], value=3, field=True)
    cmds.text(Labels["color_label"])
    color_slider = cmds.colorSliderGrp(cls.get_prefix() + Labels["color_label"], annotation=Labels["color_label"], width=Constants["window_width"])

    cmds.setParent('..')
    cmds.button(command=cls.generate, label="Generate")
    cmds.setParent('..')
    cmds.showWindow(cls.__name__)

class PerforatedBlock(Generator):
  """ Generates your standard lego block """
  @classmethod
  def generate(cls, *args):
    components = []
    boolean = []
    width = cmds.intSliderGrp(cls.get_prefix() + Labels["width_label"], query=True, value=True)
    rgb = cmds.colorSliderGrp(cls.get_prefix() + Labels["color_label"], query=True, rgbValue=True)

    block_width = width * Constants["block_width_unit"]
    block_height = Constants["block_height_unit"]
    block_depth = Constants["block_depth_unit"]

    for x in range(0, width):
      stub = cmds.polyCylinder(name=get_unique_name(cls.get_prefix(), "Stub"), radius=Constants["stub_radius"], height = Constants["stub_height"])
      components.append(stub[0])
      cmds.move(Constants["block_width_unit"] * x + half(Constants["block_width_unit"]), half(Constants["block_height_unit"]) + half(Constants["stub_height"]), half(Constants["block_depth_unit"]), stub[0])
      
    for x in range(0, width-1):
      hole = cmds.polyCylinder(name=get_unique_name(cls.get_prefix(), "Hole"), radius=Constants["perforation_radius"], height=Constants["block_depth_unit"] + 0.2)
      boolean.append(hole[0])
      cmds.rotate('90deg', 0, 0, hole[0])
      cmds.move(Constants["block_width_unit"] * x + Constants["block_width_unit"], 0, half(Constants["block_depth_unit"]), hole[0])

    cube = cmds.polyCube(sx=5,sy=2,sz=2,name=get_unique_name(cls.get_prefix(), "block"), width=block_width, height=block_height, depth=block_depth)
    components.append(cube[0])
    cmds.move(half(width * Constants["block_width_unit"]), 0, half(Constants["block_depth_unit"]), cube)
    solid = cmds.polyUnite(components, name=get_unique_name(cls.get_prefix(), ""))
    boolean_group = cmds.polyUnite(boolean, name=get_unique_name(cls.get_prefix(),"boolean"))
    final = cmds.polyBoolOp( solid[0], boolean_group[0], op=2, n=get_unique_name(cls.get_prefix(), "") )

    shader = cmds.shadingNode('blinn', asShader=True, name=get_unique_name(cls.get_prefix(),"mat"))
    cmds.setAttr(shader + ".color", rgb[0],rgb[1],rgb[2], type='double3')
    cmds.select(final[0], r=True)
    cmds.hyperShade(assign=shader)
    #cmds.delete(boolean_group)

  
  @classmethod
  def draw_ui(cls, *args):
    if cmds.window(cls.get_prefix(), exists=True):
      cmds.deleteUI(cls.get_prefix())
    cmds.window(cls.get_prefix())
    cmds.columnLayout(adjustableColumn=True, width=Constants["window_width"], height=Constants["window_height"])
    cmds.frameLayout(collapsable=True, width=Constants["window_width"], label=Labels["dimensions_label"])
    cmds.columnLayout(width=Constants["window_width"])
    
    cmds.text(Labels["width_label"])
    width_slider = cmds.intSliderGrp(cls.get_prefix() + Labels["width_label"], annotation=Labels["width_label"], width=Constants["window_width"], minValue=Constants["min_block_width"], maxValue=Constants["max_block_width"], value=3, field=True)
    cmds.text(Labels["color_label"])
    color_slider = cmds.colorSliderGrp(cls.get_prefix() + Labels["color_label"], annotation=Labels["color_label"], width=Constants["window_width"])
    cmds.setParent('..')
    cmds.button(command=cls.generate, label="Generate")
    cmds.setParent('..')
    cmds.showWindow(cls.__name__)


class PerforatedBar(Generator):
  """ Generates your standard lego block """
  @classmethod
  def generate(cls, *args):
    components = []
    boolean = []
    width = cmds.intSliderGrp(cls.get_prefix() + Labels["width_label"], query=True, value=True)
    rgb = cmds.colorSliderGrp(cls.get_prefix() + Labels["color_label"], query=True, rgbValue=True)

    block_width = width * Constants["block_width_unit"]
    block_height = Constants["block_height_unit"]
    block_depth = Constants["block_depth_unit"]

    for x in range(0, width + 1):
      hole = cmds.polyCylinder(name=get_unique_name(cls.get_prefix(), "Hole"), radius=Constants["perforation_radius"], height=Constants["block_depth_unit"] + 0.2)
      boolean.append(hole[0])
      cmds.rotate('90deg', 0, 0, hole[0])
      cmds.move(Constants["block_width_unit"] * x , 0, half(Constants["block_depth_unit"]), hole[0])

    cube = cmds.polyCube(sx=5,sy=2,sz=2,name=get_unique_name(cls.get_prefix(), "block"), width=block_width, height=block_height, depth=block_depth)
    components.append(cube[0])
    cmds.delete(cube[0] + ".f[40:47]")
    cmds.move(half(width * Constants["block_width_unit"]), 0, half(Constants["block_depth_unit"]), cube)

    #caps
    cap_one = cmds.polyCylinder(sc=1, sy=2, radius=half(Constants["block_height_unit"]), height=Constants["block_depth_unit"],name=get_unique_name(cls.get_prefix(), "cap"))
    cmds.rotate('90deg',0,0,cap_one[0])
    cmds.move(0,0,half(Constants["block_depth_unit"]),cap_one[0])
    cmds.delete(cap_one[0] + ".f[0:3]", cap_one[0] + ".f[14:23]", cap_one[0] + ".f[34:43]", cap_one[0] + ".f[54:63]", cap_one[0] + ".f[74:79]")
    components.append(cap_one[0])

    #caps
    cap_two = cmds.polyCylinder(sc=1, sy=2, radius=half(Constants["block_height_unit"]), height=Constants["block_depth_unit"])
    cmds.rotate('90deg','180deg',0,cap_two[0])
    cmds.delete(cap_two[0] + ".f[0:3]", cap_two[0] + ".f[14:23]", cap_two[0] + ".f[34:43]", cap_two[0] + ".f[54:63]", cap_two[0] + ".f[74:79]")
    cmds.move(block_width,0,half(Constants["block_depth_unit"]),cap_two[0])
    components.append(cap_two[0])

    solid = cmds.polyUnite(components, name=get_unique_name(cls.get_prefix(), ""))
    boolean_group = cmds.polyUnite(boolean, name=get_unique_name(cls.get_prefix(),"boolean"))
    cmds.polyMergeVertex( solid[0], d=0.15 )
    cmds.delete(solid[0],ch=1)
    final = cmds.polyBoolOp( solid[0], boolean_group[0], op=2, n=get_unique_name(cls.get_prefix(), "") )

    shader = cmds.shadingNode('blinn', asShader=True, name=get_unique_name(cls.get_prefix(),"mat"))
    cmds.setAttr(shader + ".color", rgb[0],rgb[1],rgb[2], type='double3')
    cmds.select(final[0], r=True)
    cmds.hyperShade(assign=shader)

  
  @classmethod
  def draw_ui(cls, *args):
    if cmds.window(cls.get_prefix(), exists=True):
      cmds.deleteUI(cls.get_prefix())
    cmds.window(cls.get_prefix())
    cmds.columnLayout(adjustableColumn=True, width=Constants["window_width"], height=Constants["window_height"])
    cmds.frameLayout(collapsable=True, width=Constants["window_width"], label=Labels["dimensions_label"])
    cmds.columnLayout(width=Constants["window_width"])
    
    cmds.text(Labels["width_label"])
    width_slider = cmds.intSliderGrp(cls.get_prefix() + Labels["width_label"], annotation=Labels["width_label"], width=Constants["window_width"], minValue=Constants["min_block_width"], maxValue=Constants["max_block_width"], value=3, field=True)
    cmds.text(Labels["color_label"])
    color_slider = cmds.colorSliderGrp(cls.get_prefix() + Labels["color_label"], annotation=Labels["color_label"], width=Constants["window_width"])
    cmds.setParent('..')
    cmds.button(command=cls.generate, label="Generate")
    cmds.setParent('..')
    cmds.showWindow(cls.__name__)

class PerforatedBarWithKink(Generator):
  """ Generates your standard lego block """
  @classmethod
  def generate(cls, *args):
    before_kink = cmds.intSliderGrp(cls.get_prefix() + Labels["before_kink_label"], query=True, value=True)
    after_kink = cmds.intSliderGrp(cls.get_prefix() + Labels["after_kink_label"], query=True, value=True)
    rgb = cmds.colorSliderGrp(cls.get_prefix() + Labels["color_label"], query=True, rgbValue=True)
    before = cls.generate_kink_peice(before_kink)
    after = cls.generate_kink_peice(after_kink)
    cmds.rotate(0,0,'143.5deg', after[0])
    final = cmds.polyUnite(before[0], after[0])

    shader = cmds.shadingNode('blinn', asShader=True, name=get_unique_name(cls.get_prefix(),"mat"))
    cmds.setAttr(shader + ".color", rgb[0],rgb[1],rgb[2], type='double3')
    cmds.select(final[0], r=True)
    cmds.hyperShade(assign=shader)


  @classmethod
  def generate_kink_peice(cls, block_width):
    components = []
    boolean = []
    for x in range(0, block_width + 1):
      hole = cmds.polyCylinder(name=get_unique_name(cls.get_prefix(), "Hole"), radius=Constants["perforation_radius"], height=Constants["block_depth_unit"] + 0.2)
      boolean.append(hole[0])
      cmds.rotate('90deg', 0, 0, hole[0])
      cmds.move(Constants["block_width_unit"] * x , 0, half(Constants["block_depth_unit"]), hole[0])

    cube = cmds.polyCube(sx=5,sy=2,sz=2,name=get_unique_name(cls.get_prefix(), "block"), width=block_width, height=Constants["block_height_unit"], depth=Constants["block_depth_unit"])
    components.append(cube[0])
    cmds.delete(cube[0] + ".f[40:47]")
    cmds.move(half(block_width * Constants["block_width_unit"]), 0, half(Constants["block_depth_unit"]), cube)

    #caps
    cap_one = cmds.polyCylinder(sc=1, sy=2, radius=half(Constants["block_height_unit"]), height=Constants["block_depth_unit"],name=get_unique_name(cls.get_prefix(), "cap"))
    cmds.rotate('90deg',0,0,cap_one[0])
    cmds.move(0,0,half(Constants["block_depth_unit"]),cap_one[0])
    cmds.delete(cap_one[0] + ".f[0:3]", cap_one[0] + ".f[14:23]", cap_one[0] + ".f[34:43]", cap_one[0] + ".f[54:63]", cap_one[0] + ".f[74:79]")
    components.append(cap_one[0])

    #caps
    cap_two = cmds.polyCylinder(sc=1, sy=2, radius=half(Constants["block_height_unit"]), height=Constants["block_depth_unit"])
    cmds.rotate('90deg','180deg',0,cap_two[0])
    cmds.delete(cap_two[0] + ".f[0:3]", cap_two[0] + ".f[14:23]", cap_two[0] + ".f[34:43]", cap_two[0] + ".f[54:63]", cap_two[0] + ".f[74:79]")
    cmds.move(block_width,0,half(Constants["block_depth_unit"]),cap_two[0])
    components.append(cap_two[0])

    solid = cmds.polyUnite(components, name=get_unique_name(cls.get_prefix(), ""))
    boolean_group = cmds.polyUnite(boolean, name=get_unique_name(cls.get_prefix(),"boolean"))
    cmds.polyMergeVertex( solid[0], d=0.15 )
    cmds.delete(solid[0],ch=1)
    return cmds.polyBoolOp( solid[0], boolean_group[0], op=2, n=get_unique_name(cls.get_prefix(), "") )

  
  @classmethod
  def draw_ui(cls, *args):
    if cmds.window(cls.get_prefix(), exists=True):
      cmds.deleteUI(cls.get_prefix())
    cmds.window(cls.get_prefix())
    cmds.columnLayout(adjustableColumn=True, width=Constants["window_width"], height=Constants["window_height"])
    cmds.frameLayout(collapsable=True, width=Constants["window_width"], label=Labels["dimensions_label"])
    cmds.columnLayout(width=Constants["window_width"])
    
    cmds.text(Labels["before_kink_label"])
    before_kink_slider = cmds.intSliderGrp(cls.get_prefix() + Labels["before_kink_label"], annotation=Labels["before_kink_label"], width=Constants["window_width"], minValue=Constants["min_block_width"], maxValue=Constants["max_block_width"], value=3, field=True)
    cmds.text(Labels["after_kink_label"])
    after_kink_slider = cmds.intSliderGrp(cls.get_prefix() + Labels["after_kink_label"], annotation=Labels["after_kink_label"], width=Constants["window_width"], minValue=Constants["min_block_width"], maxValue=Constants["max_block_width"], value=3, field=True)
    cmds.text(Labels["color_label"])
    color_slider = cmds.colorSliderGrp(cls.get_prefix() + Labels["color_label"], annotation=Labels["color_label"], width=Constants["window_width"])
    cmds.setParent('..')
    cmds.button(command=cls.generate, label="Generate")
    cmds.setParent('..')
    cmds.showWindow(cls.__name__)

class Axle(Generator):
  """ Generates your standard lego block """
  @classmethod
  def generate(cls, *args):
    components = []
    width = cmds.intSliderGrp(cls.get_prefix() + Labels["width_label"], query=True, value=True)
    rgb = cmds.colorSliderGrp(cls.get_prefix() + Labels["color_label"], query=True, rgbValue=True)
    block_width = width * Constants["block_width_unit"]
    block_height = twice(Constants["perforation_radius"])
    block_depth = twice(Constants["perforation_radius"])

    cube_one = cmds.polyCube(name=get_unique_name(cls.get_prefix(), "block"), width=block_width, height=half(block_height), depth=block_depth)
    components.append(cube_one[0])
    cmds.move(half(width * Constants["block_width_unit"]), 0, half(Constants["block_depth_unit"]), cube_one[0])

    cube_two = cmds.polyCube(name=get_unique_name(cls.get_prefix(), "block"), width=block_width, height=block_height, depth=half(block_depth))
    components.append(cube_two[0])
    cmds.move(half(width * Constants["block_width_unit"]), 0, half(Constants["block_depth_unit"]), cube_two[0])
    final = cmds.polyUnite(components, name=get_unique_name(cls.get_prefix(), ""))

    shader = cmds.shadingNode('blinn', asShader=True, name=get_unique_name(cls.get_prefix(),"mat"))
    cmds.setAttr(shader + ".color", rgb[0],rgb[1],rgb[2], type='double3')
    cmds.select(final[0], r=True)
    cmds.hyperShade(assign=shader)


  
  @classmethod
  def draw_ui(cls, *args):
    if cmds.window(cls.get_prefix(), exists=True):
      cmds.deleteUI(cls.get_prefix())
    cmds.window(cls.get_prefix())
    cmds.columnLayout(adjustableColumn=True, width=Constants["window_width"], height=Constants["window_height"])
    cmds.frameLayout(collapsable=True, width=Constants["window_width"], label=Labels["dimensions_label"])
    cmds.columnLayout(width=Constants["window_width"])
    
    cmds.text(Labels["width_label"])
    width_slider = cmds.intSliderGrp(cls.get_prefix() + Labels["width_label"], annotation=Labels["width_label"], width=Constants["window_width"], minValue=Constants["min_block_width"], maxValue=Constants["max_block_width"], value=3, field=True)
    cmds.text(Labels["color_label"])
    color_slider = cmds.colorSliderGrp(cls.get_prefix() + Labels["color_label"], annotation=Labels["color_label"], width=Constants["window_width"])
    cmds.setParent('..')
    cmds.button(command=cls.generate, label="Generate")
    cmds.setParent('..')
    cmds.showWindow(cls.__name__)

class Wheel(Generator):
  """ Generates your standard lego block """
  @classmethod
  def generate(cls, *args):
    components = []
    width = cmds.intSliderGrp(cls.get_prefix() + Labels["radius_label"], query=True, value=True)
    height = cmds.intSliderGrp(cls.get_prefix() + Labels["height_label"], query=True, value=True)
    subdivs = cmds.intSliderGrp(cls.get_prefix() + Labels["subdivs_label"], query=True, value=True)
    rgb = cmds.colorSliderGrp(cls.get_prefix() + Labels["color_label"], query=True, rgbValue=True)
    wheel_radius = width * Constants["wheel_radius_unit"]
    wheel_height = height * Constants["wheel_height_unit"]
    
    wheel_component = cmds.polyCylinder(name=get_unique_name(cls.get_prefix(), "cylender"), sx=subdivs, h=wheel_height, r=wheel_radius)
    wheel_extrusion_faces = []
    cmds.select(r=True)

    for i in range(0, subdivs):
      if i % 2 == 1:
        facet_title = wheel_component[0] + ".f[" + str(i) + "]"
        wheel_extrusion_faces.append(facet_title)

    cmds.polyExtrudeFacet(wheel_extrusion_faces, ltz=Constants["wheel_ridge_depth"])
    shader = cmds.shadingNode('blinn', asShader=True, name=get_unique_name(cls.get_prefix(),"mat"))
    cmds.setAttr(shader + ".color", rgb[0],rgb[1],rgb[2], type='double3')
    cmds.select(wheel_component[0], r=True)
    cmds.hyperShade(assign=shader)

  
  @classmethod
  def draw_ui(cls, *args):
    if cmds.window(cls.get_prefix(), exists=True):
      cmds.deleteUI(cls.get_prefix())
    cmds.window(cls.get_prefix())
    cmds.columnLayout(adjustableColumn=True, width=Constants["window_width"], height=Constants["window_height"])
    cmds.frameLayout(collapsable=True, width=Constants["window_width"], label=Labels["dimensions_label"])
    cmds.columnLayout(width=Constants["window_width"])
    
    cmds.text(Labels["radius_label"])
    radius_slider = cmds.intSliderGrp(cls.get_prefix() + Labels["radius_label"], annotation=Labels["radius_label"], width=Constants["window_width"], minValue=Constants["wheel_min_radius"], maxValue=Constants["max_block_width"], field=True)

    cmds.text(Labels["height_label"])
    height_slider = cmds.intSliderGrp(cls.get_prefix() + Labels["height_label"], annotation=Labels["radius_label"], width=Constants["window_width"], minValue=1, maxValue=Constants["max_block_width"], field=True)

    cmds.text(Labels["subdivs_label"])
    height_slider = cmds.intSliderGrp(cls.get_prefix() + Labels["subdivs_label"], annotation=Labels["subdivs_label"], width=Constants["window_width"], minValue=Constants["wheel_min_subdivs"], maxValue=Constants["wheel_max_subdivs"], field=True)

    cmds.text(Labels["color_label"])
    color_slider = cmds.colorSliderGrp(cls.get_prefix() + Labels["color_label"], annotation=Labels["color_label"], width=Constants["window_width"])

    cmds.setParent('..')
    cmds.button(command=cls.generate, label="Generate")
    cmds.setParent('..')
    cmds.showWindow(cls.__name__)

class BigWheel(Generator):
  """ Generates your standard lego block """
  @classmethod
  def generate(cls, *args):
    components = []
    radius = cmds.intSliderGrp(cls.get_prefix() + Labels["radius_label"], query=True, value=True)
    height = cmds.intSliderGrp(cls.get_prefix() + Labels["height_label"], query=True, value=True)
    subdivs = cmds.intSliderGrp(cls.get_prefix() + Labels["subdivs_label"], query=True, value=True)
    rgb = cmds.colorSliderGrp(cls.get_prefix() + Labels["color_label"], query=True, rgbValue=True)
    wheel_radius = radius * Constants["wheel_radius_unit"]
    wheel_height = height * Constants["wheel_height_unit"]
    
    wheel_component = cmds.polyPipe(name=get_unique_name(cls.get_prefix(), "cylender"), sh=4, sc=subdivs, h=wheel_height, r=wheel_radius)
    wheel_extrusion_faces = []
    cmds.select(r=True)

    for i in range(0, subdivs):
      if i % 2 == 1:
        facet_title = wheel_component[0] + ".f[" + str(i) + "]"
        wheel_extrusion_faces.append(facet_title)

    #cmds.polyExtrudeFacet(wheel_extrusion_faces, ltz=Constants["wheel_ridge_depth"])
    cmds.delete(ch=1)
    cmds.lattice(wheel_component[0],divisions=[2,3,2], name=get_unique_name(cls.get_prefix(),"lattice"), cp=wheel_component[0])
    shader = cmds.shadingNode('blinn', asShader=True, name=get_unique_name(cls.get_prefix(),"mat"))
    cmds.setAttr(shader + ".color", rgb[0],rgb[1],rgb[2], type='double3')
    cmds.select(wheel_component[0], r=True)
    cmds.hyperShade(assign=shader)

  
  @classmethod
  def draw_ui(cls, *args):
    if cmds.window(cls.get_prefix(), exists=True):
      cmds.deleteUI(cls.get_prefix())
    cmds.window(cls.get_prefix())
    cmds.columnLayout(adjustableColumn=True, width=Constants["window_width"], height=Constants["window_height"])
    cmds.frameLayout(collapsable=True, width=Constants["window_width"], label=Labels["dimensions_label"])
    cmds.columnLayout(width=Constants["window_width"])
    
    cmds.text(Labels["radius_label"])
    radius_slider = cmds.intSliderGrp(cls.get_prefix() + Labels["radius_label"], annotation=Labels["radius_label"], width=Constants["window_width"], minValue=Constants["wheel_min_radius"], maxValue=Constants["max_block_width"], value=3, field=True)

    cmds.text(Labels["height_label"])
    height_slider = cmds.intSliderGrp(cls.get_prefix() + Labels["height_label"], annotation=Labels["radius_label"], width=Constants["window_width"], minValue=1, maxValue=Constants["max_block_width"], value=3, field=True)

    cmds.text(Labels["subdivs_label"])
    height_slider = cmds.intSliderGrp(cls.get_prefix() + Labels["subdivs_label"], annotation=Labels["subdivs_label"], width=Constants["window_width"], minValue=Constants["wheel_min_subdivs"], maxValue=Constants["wheel_max_subdivs"],value=3, field=True)

    cmds.text(Labels["color_label"])
    color_slider = cmds.colorSliderGrp(cls.get_prefix() + Labels["color_label"], annotation=Labels["color_label"], width=Constants["window_width"])

    cmds.setParent('..')
    cmds.button(command=cls.generate, label="Generate")
    cmds.setParent('..')
    cmds.showWindow(cls.__name__)

class PerforatedBarWithRightAngle(Generator):
  """ Generates your standard lego block """
  @classmethod
  def generate(cls, *args):
    
    before_kink = cmds.intSliderGrp(cls.get_prefix() + Labels["before_kink_label"], query=True, value=True)
    after_kink = cmds.intSliderGrp(cls.get_prefix() + Labels["after_kink_label"], query=True, value=True)
    rgb = cmds.colorSliderGrp(cls.get_prefix() + Labels["color_label"], query=True, rgbValue=True)
    before = cls.generate_kink_peice(before_kink)
    after = cls.generate_kink_peice(after_kink)
    cmds.rotate(0,0,'90deg', after[0])
    final = cmds.polyUnite(before[0], after[0])
    shader = cmds.shadingNode('blinn', asShader=True, name=get_unique_name(cls.get_prefix(),"mat"))
    cmds.setAttr(shader + ".color", rgb[0],rgb[1],rgb[2], type='double3')
    cmds.select(final[0], r=True)
    cmds.hyperShade(assign=shader)


  @classmethod
  def generate_kink_peice(cls, block_width):
    components = []
    boolean = []
    for x in range(0, block_width + 1):
      hole = cmds.polyCylinder(name=get_unique_name(cls.get_prefix(), "Hole"), radius=Constants["perforation_radius"], height=Constants["block_depth_unit"] + 0.2)
      boolean.append(hole[0])
      cmds.rotate('90deg', 0, 0, hole[0])
      cmds.move(Constants["block_width_unit"] * x , 0, half(Constants["block_depth_unit"]), hole[0])

    cube = cmds.polyCube(sx=5,sy=2,sz=2,name=get_unique_name(cls.get_prefix(), "block"), width=block_width, height=Constants["block_height_unit"], depth=Constants["block_depth_unit"])
    components.append(cube[0])
    cmds.delete(cube[0] + ".f[40:47]")
    cmds.move(half(block_width * Constants["block_width_unit"]), 0, half(Constants["block_depth_unit"]), cube)

    #caps
    cap_one = cmds.polyCylinder(sc=1, sy=2, radius=half(Constants["block_height_unit"]), height=Constants["block_depth_unit"],name=get_unique_name(cls.get_prefix(), "cap"))
    cmds.rotate('90deg',0,0,cap_one[0])
    cmds.move(0,0,half(Constants["block_depth_unit"]),cap_one[0])
    cmds.delete(cap_one[0] + ".f[0:3]", cap_one[0] + ".f[14:23]", cap_one[0] + ".f[34:43]", cap_one[0] + ".f[54:63]", cap_one[0] + ".f[74:79]")
    components.append(cap_one[0])

    #caps
    cap_two = cmds.polyCylinder(sc=1, sy=2, radius=half(Constants["block_height_unit"]), height=Constants["block_depth_unit"])
    cmds.rotate('90deg','180deg',0,cap_two[0])
    cmds.delete(cap_two[0] + ".f[0:3]", cap_two[0] + ".f[14:23]", cap_two[0] + ".f[34:43]", cap_two[0] + ".f[54:63]", cap_two[0] + ".f[74:79]")
    cmds.move(block_width,0,half(Constants["block_depth_unit"]),cap_two[0])
    components.append(cap_two[0])

    solid = cmds.polyUnite(components, name=get_unique_name(cls.get_prefix(), ""))
    boolean_group = cmds.polyUnite(boolean, name=get_unique_name(cls.get_prefix(),"boolean"))
    cmds.polyMergeVertex( solid[0], d=0.15 )
    cmds.delete(solid[0],ch=1)
    return cmds.polyBoolOp( solid[0], boolean_group[0], op=2, n=get_unique_name(cls.get_prefix(), "") )

  
  @classmethod
  def draw_ui(cls, *args):
    if cmds.window(cls.get_prefix(), exists=True):
      cmds.deleteUI(cls.get_prefix())
    cmds.window(cls.get_prefix())
    cmds.columnLayout(adjustableColumn=True, width=Constants["window_width"], height=Constants["window_height"])
    cmds.frameLayout(collapsable=True, width=Constants["window_width"], label=Labels["dimensions_label"])
    cmds.columnLayout(width=Constants["window_width"])
    
    cmds.text(Labels["before_kink_label"])
    before_kink_slider = cmds.intSliderGrp(cls.get_prefix() + Labels["before_kink_label"], annotation=Labels["before_kink_label"], width=Constants["window_width"], minValue=Constants["min_block_width"], maxValue=Constants["max_block_width"], value=3, field=True)
    cmds.text(Labels["after_kink_label"])
    after_kink_slider = cmds.intSliderGrp(cls.get_prefix() + Labels["after_kink_label"], annotation=Labels["after_kink_label"], width=Constants["window_width"], minValue=Constants["min_block_width"], maxValue=Constants["max_block_width"], value=3,field=True)
    cmds.text(Labels["color_label"])
    color_slider = cmds.colorSliderGrp(cls.get_prefix() + Labels["color_label"], annotation=Labels["color_label"], width=Constants["window_width"])
    cmds.setParent('..')
    cmds.button(command=cls.generate, label="Generate")
    cmds.setParent('..')
    cmds.showWindow(cls.__name__)

class Picker(Generator):
  @classmethod
  def draw_ui(cls):
    if cmds.window(cls.get_prefix(), exists=True):
      cmds.deleteUI(cls.get_prefix())
    cmds.window(cls.get_prefix())
    cmds.columnLayout(adjustableColumn=True, width=Constants["window_width"], height=Constants["window_height"])
    cmds.frameLayout(collapsable=True, width=Constants["window_width"], label="LEGGGOOO")
    cmds.columnLayout(width=Constants["window_width"])
    cmds.button(command=Block.draw_ui, label="Block")
    cmds.button(command=PerforatedBlock.draw_ui, label="Perforated Block")
    cmds.button(command=PerforatedBar.draw_ui, label="Perforated Bar")
    cmds.button(command=PerforatedBarWithKink.draw_ui, label="Perforated Bar With Kink")
    cmds.button(command=Axle.draw_ui, label="Axle")
    cmds.button(command=PerforatedBarWithRightAngle.draw_ui, label="Perforated Bar With Right Angle")
    cmds.button(command=Wheel.draw_ui, label="Wheel")
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.showWindow(cls.__name__)

Picker.draw_ui()



  

