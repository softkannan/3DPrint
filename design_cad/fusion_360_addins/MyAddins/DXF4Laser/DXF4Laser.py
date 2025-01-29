# Author-Ross Korsky
# Version-1.1.0
# Released under the MIT license. See License.txt for full license information.
#
# Description-Generates a Kerf compensated DXF file to produce laser cut parts with dimensions that match your drawings geometry.

import os, tempfile, re, math
import adsk.core, adsk.fusion
from .fission.app import (CommandBase, InputFactory)
from .fission.utils.timers import (Stopwatch, RelayStopwatch, SegmentedStopwatch)
from .fission.drawing.better_types import Point3D
from . import dfx_merge
# import subprocess

SHOW_DBG_PERFORMANCE_INFO = False
RECOLOR_FINAL_SKETCH_LINES = False

class FastPoint2D(object):
  CLOSE_ENOUGH = 0.000001
  def __init__(self, x=0, y=0):
    self.x = x
    self.y = y

  def is_close_to(self, point):
    return abs(self.x - point.x) < FastPoint2D.CLOSE_ENOUGH and abs(self.y - point.y) < FastPoint2D.CLOSE_ENOUGH


class DxfForLaserAddin(CommandBase):
  """Generates a DXF file accounting for the kerf of laser cutting.

  Can also generate a DXF file with layers separating cutouts from the perimeter.
  """
  def __init__(self):
    super().__init__()

  @property
  def resource_dir(self):
    try:
      resource_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')
      return resource_dir if os.path.isdir(resource_dir) else ''
    except:
      return ''

  @property
  def is_repeatable(self):
    return True

  @property
  def command_name(self):
    return 'Save DXF for Laser Cutting'

  def add_button(self):
    self.remove_button()
    button = super().add_button()
    button.toolClipFilename = os.path.join(self.resource_dir, 'captions/Thumb.png')
    panel = self.ui.allToolbarPanels.itemById('SolidCreatePanel')
    panel.controls.addCommand(button)
    panel = self.ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
    panel.controls.addCommand(button)
    button.isPromotedByDefault = True
    button.isPromoted = True
    return button

  def remove_button(self):
    button = self.ui.commandDefinitions.itemById(self.command_id)
    if button: button.deleteMe()
    panel = self.ui.allToolbarPanels.itemById('SolidCreatePanel')
    button_control = panel.controls.itemById(self.command_id)
    if button_control: button_control.deleteMe()
        
    panel = self.ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
    button_control = panel.controls.itemById(self.command_id)
    if button_control: button_control.deleteMe()

  def on_execute(self, args) -> 'execute':
    (component, selection_name, plane, offset_sketch, perimeter_sketch, cutouts_sketch, might_be_nonmanifold) = self.generate_offset_sketch(False)

    plane.isLightBulbOn = False
    if offset_sketch and not might_be_nonmanifold:
      offset_sketch.isVisible = False
    if perimeter_sketch and cutouts_sketch:
      adsk.doEvents()
      file_picker = self.ui.createFileDialog()
      file_picker.isMultiSelectEnabled = False
      file_picker.filter = 'DXF files (*.dxf);;All files (*.*)'
      file_picker.title = 'Save Laser Path to DXF File'
      file_picker.initialFilename = '{}.dxf'.format(selection_name)
      if file_picker.showSave() == adsk.core.DialogResults.DialogOK:
        if self.split_into_layers.eval():
          tmp_dir = tempfile.TemporaryDirectory()
          perimeter_dxf_path = os.path.join(tmp_dir.name, 'perimeter_sketch.dxf')
          cutouts_dxf_path = os.path.join(tmp_dir.name, 'cutouts_sketch.dxf')
          ps_ok = perimeter_sketch.saveAsDXF(perimeter_dxf_path)
          co_ok = cutouts_sketch.saveAsDXF(cutouts_dxf_path)
          #subprocess.Popen(r'explorer /select,"{}"'.format(tmp_dir.name))
          #adsk.doEvents()
          #self.ui.messageBox(tmp_dir.name)

          m = dfx_merge.DxfFileMerger()
          if co_ok:
            m.add_file(cutouts_dxf_path, 'cutouts', 1)
          if ps_ok :
            m.add_file(perimeter_dxf_path, 'perimeter', 5)
          m.save(file_picker.filename)
          tmp_dir.cleanup()
        else:
          # in this case perimeter_sketch and cutouts_sketch point to the same object
          perimeter_sketch.saveAsDXF(file_picker.filename)

        if component and self.cleanup_on_success.eval() and not might_be_nonmanifold:
          component.occurrence.deleteMe()
    self.preserve_inputs()

  def on_preview(self, args) -> 'preview':
    if self.show_preview.value:
      self.generate_offset_sketch(True)

  def generate_offset_sketch(self, is_preview):
    might_be_nonmanifold = False
    overall_clock = Stopwatch()
    create_assets_clock = Stopwatch()
    build_curve_lookup_clock = Stopwatch()
    loop_perf_tracker = RelayStopwatch()
    transcription_segment_tracker = SegmentedStopwatch()
    finalize_clock = Stopwatch()

    overall_clock.run()
    create_assets_clock.run()
    selection = self.face.selection(0)
    if not selection:
      return
    """
    # mock flow for finding coplanar faces of the same body
    selected_face = adsk.fusion.BRepFace.cast(selection.entity)

    faces = selected_face.body.faces
    coplanar_faces = []
    for face in faces:
      if face.geometry.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType: # enum value 0
        if face.geometry.normal.isEqualTo(selected_face.geometry.normal):
          if abs(face_depth(selected_face, face)) < 0.0001:
            coplanar_faces.append(face)

    def face_depth(ref_face, target_face):
      p1 = ref_face.pointOnFace
      p2 = target_face.pointOnFace
      if p1.isEqualTo(p2):
        return 0
      return ref_face.geometry.normal.dotProduct(p1.vectorTo(p2))
    """

    #self.design.ActivateRootComponent()
    half_kerf = self.laser_kerf.value / 2
    face = adsk.fusion.BRepFace.cast(selection.entity)
    selection_name = face.body.parentComponent.name + ' - ' + face.body.name
    component = self.design.CreateNewComponent()
    component.name = 'Laser Path - ' + selection_name

    planeInput = component.constructionPlanes.createInput()
    planeInput.setByOffset(face, InputFactory._ValueInput(0))
    plane = component.constructionPlanes.add(planeInput)
    plane.isLightBulbOn = False

    offset_sketch = component.sketches.add(face)
    #offset_sketch.project(face)
    offset_sketch.name = 'Path Offsets'
    offset_sketch.areProfilesShown = False
    offset_sketch.isComputeDeferred = True

    perimeter_sketch = None
    cutouts_sketch = None
    if not is_preview:
      if self.split_into_layers.eval():
        perimeter_sketch = component.sketches.add(plane)
        perimeter_sketch.name = 'Perimeter'
        perimeter_sketch.isComputeDeferred = True
        perimeter_sketch.areProfilesShown = False

        cutouts_sketch = component.sketches.add(plane)
        cutouts_sketch.name = 'Cutouts'
        cutouts_sketch.isComputeDeferred = True
        cutouts_sketch.areProfilesShown = False
      else:
        cut_all_sketch = component.sketches.add(plane)
        cut_all_sketch.name = 'Cut All'
        cut_all_sketch.isComputeDeferred = True
        cut_all_sketch.areProfilesShown = False
        perimeter_sketch = cut_all_sketch
        cutouts_sketch = cut_all_sketch
    else:
      perimeter_sketch = offset_sketch
      cutouts_sketch = offset_sketch

    t = offset_sketch.modelToSketchSpace
    create_assets_clock.pause()

    #dbg_sketch = component.sketches.add(plane)
    #dbg_sketch.name = 'DEBUG'
    #dbg_sketch.areProfilesShown = False

    # Index the base sketch's points and identify non-manifold points and possible non-manifold circles and ellipses
    build_curve_lookup_clock.run()
    curve_lookup = []
    nonmanifold_points = []
    circle_centers = []
    ellipse_centers = []
    # These min/max's do not encompas the full geometry, they are only the min/max of interesting sketch points.
    min_x = math.pow(2, 30)
    max_x = -math.pow(2, 30)
    min_y = math.pow(2, 30)
    max_y = -math.pow(2, 30)
    for p in offset_sketch.sketchPoints:
      if p.connectedEntities:
        g = p.geometry
        fp = FastPoint2D(g.x, g.y)
        curves = []
        for e in p.connectedEntities:
          c = adsk.fusion.SketchCurve.cast(e)
          if c:
            as_circle = adsk.fusion.SketchCircle.cast(e)
            if as_circle:
              fpt = FastPoint2D(g.x, g.y)
              fpt.connected_circle = as_circle
              circle_centers.append(fpt)
              continue
            as_ellipse = adsk.fusion.SketchEllipse.cast(e)
            if as_ellipse:
              fpt = FastPoint2D(g.x, g.y)
              fpt.connected_ellipse = as_ellipse
              ellipse_centers.append(fpt)
              continue
            as_arc = adsk.fusion.SketchArc.cast(e)
            if as_arc and fp.is_close_to(as_arc.centerSketchPoint.geometry):
              continue
            as_earc = adsk.fusion.SketchEllipticalArc.cast(e)
            if as_earc and fp.is_close_to(as_earc.centerSketchPoint.geometry):
              continue
            curves.append(c)
        if curves:
          if fp.x > max_x: max_x = fp.x
          if fp.y > max_y: max_y = fp.y
          if fp.x < min_x: min_x = fp.x
          if fp.y < min_y: min_y = fp.y
          fp.connected_curves = curves
          curve_lookup.append(fp)
          if len(curves) > 2:
            nonmanifold_points.append(fp)
          #dbg_sketch.sketchCurves.sketchCircles.addByCenterRadius( dbg_sketch.modelToSketchSpace(offset_sketch.sketchToModelSpace(g)), 0.01 * len(curves) )

    def find_curves_with_point(point):
      nonlocal curve_lookup
      for fp in curve_lookup:
        if fp.is_close_to(point):
          return fp.connected_curves
      return []
    build_curve_lookup_clock.pause()

    if nonmanifold_points:
      under_warn_sketch = component.sketches.add(plane)
      under_warn_sketch.name = 'WARNING TEMP'
      under_warn_sketch.areProfilesShown = False
      warn_sketch = component.sketches.add(plane)
      warn_sketch.name = 'WARNING'
      warn_sketch.areProfilesShown = False
      size = max(max_x - min_x, max_y - min_y) / 20
      # pos = fission.Point3D((max_x - min_x)/2 + min_x, (max_y - min_y)/2 + min_y)  # Center(ish)
      pos = Point3D(min_x, max_y + size * 3.1)
      pos = under_warn_sketch.modelToSketchSpace(offset_sketch.sketchToModelSpace(pos))
      text_input = warn_sketch.sketchTexts.createInput('WARNING non-manifold solid.\nTwo or more shapes share an edge.\nProblem vertexes are marked with circles.', size, pos)
      warn_sketch.sketchTexts.add(text_input)
      for p in nonmanifold_points:
        warn_circle = under_warn_sketch.sketchCurves.sketchCircles.addByCenterRadius(
            under_warn_sketch.modelToSketchSpace(offset_sketch.sketchToModelSpace(Point3D(p.x, p.y))), 0.05)
        warn_sketch.project(warn_circle)
      under_warn_sketch.deleteMe()
      if self.ui.messageBox('WARNING non-manifold solid.\nTwo or more shapes share an edge.\nProblem vertexes are marked with circles.\n\nContinuing may cause Fusion to become unresponsive.\nWould you like to continue?', 'Warning', adsk.core.MessageBoxButtonTypes.YesNoButtonType)  == adsk.core.DialogResults.DialogNo:
        return (component, selection_name, plane, offset_sketch, None, None)

    for loop in face.loops:
      loop_perf_tracker.start_section('loop with {} edges'.format(loop.edges.count))
      transcription_segment_tracker.switch_segment('Calc Offset To')
      target_sketch = perimeter_sketch if loop.isOuter else cutouts_sketch
      co_edge = loop.coEdges[0]
      edge = co_edge.edge
      assert co_edge.isParamReversed == co_edge.isOpposedToEdge, 'co-edge reversals are not in agreement.'
      edge_eval = edge.evaluator
      (r, min_param, max_param) = edge_eval.getParameterExtents()
      assert r, 'Failed to getParameterExtents for co-edge.'
      s_param = min_param + ((max_param - min_param) * (0.667 if co_edge.isParamReversed else 0.333))
      (r, sample_point) = edge_eval.getPointAtParameter(s_param)
      assert r, 'Failed to get sample point on edge.'
      (r, tan_vector) = edge_eval.getTangent(s_param)
      assert r, 'Failed to get tangent vector to edge.'
      if co_edge.isOpposedToEdge:
        tan_vector.scaleBy(-1)
      lead_point = sample_point.copy()
      lead_point.translateBy(tan_vector)
      lead_point = t(lead_point)
      sample_point = t(sample_point)
      lead_vector = sample_point.vectorTo(lead_point)
      lead_vector.normalize()
      assert abs(lead_vector.z) < FastPoint2D.CLOSE_ENOUGH, 'expected edge-tangent vector to lay on sketch plane, but it did not!'

      # Rotate the vector "out" (clockwise) 90deg
      out_vector = adsk.core.Vector3D.create(lead_vector.y, -lead_vector.x, 0)
      if lead_vector.z != 0:
        out_vector.normalize()

      offset_v = out_vector.copy()
      offset_v.scaleBy(abs(half_kerf))  # Negative offsets are now supported by Fusion!
      offset_to = sample_point.copy()
      offset_to.translateBy(offset_v)

      loop_sketch_curves = None
      if loop.edges.count == 1:
        curve = edge.geometry
        # circular holes are common - this is MUCH faster than offseting
        if curve.curveType == adsk.core.Curve3DTypes.Circle3DCurveType:
          transcription_segment_tracker.switch_segment('Handle Circles')
          circle = adsk.core.Circle3D.cast(curve)
          rad = circle.radius + half_kerf if loop.isOuter else circle.radius - half_kerf
          assert rad > 0, 'Offset of a circle resulted in no sketch geometry.'
          target_sketch.sketchCurves.sketchCircles.addByCenterRadius(
              target_sketch.modelToSketchSpace(circle.center), rad)
        else:
          # Give special treatment to closed splines - they are hard to find in the sketches curve list
          # This also catches ellipses - that's fine - in fact sometimes projecting an offset ellipse errors out
          transcription_segment_tracker.switch_segment('Handle Other Singltons')
          target_sketch.isComputeDeferred = False
          loop_sketch_curves = target_sketch.project(edge)
          target_sketch.isComputeDeferred = True
          if loop_sketch_curves.count > 1:
            loop_sketch_curves = target_sketch.findConnectedCurves(loop_sketch_curves.item(0))
          offset_curves = target_sketch.offset(loop_sketch_curves, target_sketch.modelToSketchSpace(offset_sketch.sketchToModelSpace(offset_to)), half_kerf)
          for c in loop_sketch_curves:
            c.deleteMe()
      # Try to find an existing curve as projected from the face when the sketch was created.
      else:
        transcription_segment_tracker.switch_segment('Find First Curve')
        first_curve = None
        (r, first_point) = edge_eval.getPointAtParameter( max_param if co_edge.isOpposedToEdge else min_param )
        if r:
          first_point = offset_sketch.modelToSketchSpace(first_point)
          possible_curves = find_curves_with_point(first_point)
          if possible_curves:
            first_curve = possible_curves[0]
        # Last chance - this is an expensive process but it's worth a shot and should virtually never happen
        if not first_curve:
          transcription_segment_tracker.switch_segment('Last Chance Capture')
          for co_edge in loop.coEdges:
            if not first_curve:
              first_curve = offset_sketch.project(co_edge.edge).item(0)
            else:
              offset_sketch.project(co_edge.edge)
        assert first_curve, 'Failed to map an edge of the selected face to a projected sketch curve.'

        transcription_segment_tracker.switch_segment('Find Connected Curves')
        loop_sketch_curves = offset_sketch.findConnectedCurves(first_curve)
        transcription_segment_tracker.switch_segment('Offset Connected Curves')
        offset_curves = offset_sketch.offset(loop_sketch_curves, offset_to, half_kerf)
        if not is_preview:
          transcription_segment_tracker.switch_segment('Project Final Curves')
          for c in offset_curves:
            target_sketch.project(c)
        if loop_sketch_curves.count < loop.edges.count:
          might_be_nonmanifold = True
          for c in offset_curves:
            c.isReference = False
            c.isFixed = True
        #assert loop_sketch_curves.count >= loop.edges.count, 'Encountered unexpected non-manifold geometry.'

    loop_perf_tracker.stop()
    transcription_segment_tracker.stop()

    finalize_clock.run()

    perimeter_sketch.isComputeDeferred = False
    cutouts_sketch.isComputeDeferred = False

    # This looks cool, but it's just too slow :(
    # Change line colors
    if RECOLOR_FINAL_SKETCH_LINES and not is_preview:
      perimeter_sketch.isComputeDeferred = True
      for c in perimeter_sketch.sketchCurves:
        c.isReference = False
      perimeter_sketch.isComputeDeferred = False

      if self.split_into_layers.eval():
        cutouts_sketch.isComputeDeferred = True
        for c in cutouts_sketch.sketchCurves:
          c.isReference = False
          c.isFixed = True
        cutouts_sketch.isComputeDeferred = False

    offset_sketch.isVisible = is_preview
    finalize_clock.pause()
    overall_clock.pause()

    if SHOW_DBG_PERFORMANCE_INFO:
      perf  = selection_name + '\n'
      perf += '=============================================\n'
      perf += 'Overall...........: {}\n'.format(overall_clock.elapsed)
      perf += 'Create Assets.....: {}\n'.format(create_assets_clock.elapsed)
      perf += 'Build Curve Lookup: {}\n'.format(build_curve_lookup_clock.elapsed)
      perf += 'Transcribe Loops\n{}\n'.format(re.sub('^','  ',str(transcription_segment_tracker), flags=re.MULTILINE))
      perf += 'Finalize..........: {}\n'.format(finalize_clock.elapsed)
      perf += '---------------------------------------------\n'
      perf += str(loop_perf_tracker)
      self.ui.messageBox(perf)

    if might_be_nonmanifold:
      self.ui.messageBox('Encountered a problem with the selected face. The face may contain non-manifold geometry or other sketch projection artifacts. Please take a close look at the output sketches before cutting. Paths with a problem will appear as fixed sketch lines (green) on the "Path Offsets" sketch. Pay close attention to where arcs/curves intersect other edges.\n\nTip: Try selecting the other side of the same body instead.')

    return (component, selection_name, plane, offset_sketch, perimeter_sketch, cutouts_sketch, might_be_nonmanifold)

  def initialize_inputs(self, factory):
    self.face = factory.addSelectionInput(
      'face',
      'Face',
      'Select the face you wish to export.',
      filter=[adsk.core.SelectionCommandInput.PlanarFaces])
    self.face.setSelectionLimits(1, 1)

    self.laser_kerf = factory.addValueInput(
      'laser_kerf',
      'Laser Kerf',
      '0.15 mm', 'mm')

    self.show_preview = factory.create_checkbox(
      'show_preview',
      'Preview',
      True)

    self.split_into_layers = factory.create_checkbox(
      'split_into_layers',
      'Output Multiple Layers',
      True,
      help_image='resources/captions/MultiLayer.png',
      description='When set cutouts (holes) and the perimeter will be placed on separate layers (and separate colors) in the DXF file. This feature will allow you to improve the accuracy of your laser cut parts by cutting cutouts first and your perimeter last, if supported by your cutting software.')

    self.cleanup_on_success = factory.create_checkbox(
      'cleanup_on_success',
      'Cleanup on Success',
      True,
      description='Uncheck to keep the temporary sketches that were created after a successful execution.')

    """self.material_thickness = factory.addValueInput(
      'material_thickness',
      'Material Thickness',
      '6 mm', 'mm',
      on_validate=self.validate_material_thickness)"""

def run(context):
  global __addin
  __addin = DxfForLaserAddin()
  __addin.run()

def stop(context):
  global __addin
  if __addin:
    __addin.stop(context)
