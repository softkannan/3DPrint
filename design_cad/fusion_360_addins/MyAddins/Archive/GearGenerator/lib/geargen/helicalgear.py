from .spurgear import *
from .misc import *

class HelicalGearSpecification(SpurGearSpecification):
    def __init__(self, plane=None, module=1, toothNumber=17, pressureAngle=math.radians(20), boreDiameter=None, thickness=5, chamferTooth=0, sketchOnly=False, anchorPoint=None, helixAngle=0):
        super().__init__(plane=plane, module=module, toothNumber=toothNumber, pressureAngle=pressureAngle, boreDiameter=boreDiameter, thickness=thickness, chamferTooth=chamferTooth, sketchOnly=sketchOnly, anchorPoint=anchorPoint)
        if helixAngle <= 0:
            raise Exception("helixAngle must be > 0")
        self.helixAngle = helixAngle

    @classmethod
    def to_args(cls, inputs: adsk.core.CommandInputs):
        args = super().to_args(inputs)
        (helixAngle, ok) = cls.get_value(inputs, 'helixAngle')
        if not ok:
            raise Exception('could not get helix angle value')
        args['helixAngle'] = helixAngle
        return args

    @classmethod
    def from_inputs(cls, inputs):
        args = cls.to_args(inputs)
        return HelicalGearSpecification(**args)

class HelicalGearGenerationContext(SpurGearGenerationContext):
    def __init__(self):
        super().__init__()
        self.helixPlane = adsk.fusion.ConstructionPlane.cast(None)
        self.twistedGearProfileSketch = adsk.fusion.Sketch.cast(None)

class HelicalGearCommandConfigurator(SpurGearCommandInputsConfigurator):
    @classmethod
    def configure(cls, cmd):
        input = SpurGearCommandInputsConfigurator.configure(cmd)
        input.addValueInput('helixAngle', 'Helix Angle', 'deg', adsk.core.ValueInput.createByReal(math.radians(14.5)))

    def toSpecificationArgs(self):
        args = super().toSpecificationArgs()
        (helixAngle, ok) = self.getValue('helixAngle')
        if not ok:
            raise Exception("mandatory parameter helix angle not provided")

        if helixAngle <= 0 or helixAngle >= math.radians(180):
            raise Exception("invalid value for helix angle")

        args['helixAngle'] = helixAngle
        return args

    def toSpecification(self, kwargs):
        return HelicalGearSpecification(**kwargs)

    def validate(self):
        (helixAngle, ok) = self.getValue('helixAngle')
        if not ok or helixAngle <= 0 or helixAngle >= math.radians(180):
            raise Exception(f'invalid helix angle: {helixAngle}')
    
        return True

class HelicalGearGenerator(SpurGearGenerator):
    def __init__(self, component: adsk.fusion.Component):
        super().__init__(component)

    def newContext(self):
        return HelicalGearGenerationContext()

    def generateName(self, spec):
        return 'Helical Gear (M={}, Tooth={}, Thickness={}, Angle={})'.format(spec.module, spec.toothNumber, spec.thickness, math.degrees(spec.helixAngle))
    
    def helicalPlaneOffset(self, spec: HelicalGearSpecification):
        return to_cm(spec.thickness)
    
    def chamferWantEdges(self, spec: SpurGearSpecification):
        return 4
    
    def buildSketches(self, ctx: GenerationContext, spec: SpurGearSpecification):
        super().buildSketches(ctx, spec)

        # If we have a helix angle, we can't just extrude the bottom profile
        # and call it a day. We create another sketch on a plane that is
        # spec.thickness away from the bottom profile, and then use loft
        # to create the body
        constructionPlaneInput = self.component.constructionPlanes.createInput()
        constructionPlaneInput.setByOffset(
            spec.plane,
            adsk.core.ValueInput.createByReal(self.helicalPlaneOffset(spec))
        )

        plane = self.component.constructionPlanes.add(constructionPlaneInput)
        ctx.helixPlane = plane
        loftSketch = self.createSketchObject('Twisted Gear Profile', plane=plane)

        # This sketch is rotated for the helix angle
        SpurGearInvoluteToothDesignGenerator(loftSketch, spec).draw(ctx.anchorPoint, angle=spec.helixAngle)
        ctx.twistedGearProfileSketch = loftSketch
    
    def buildTooth(self, ctx: GenerationContext, spec :SpurGearSpecification):
        self.loftTooth(ctx, spec)
        if spec.chamferTooth > 0:
            self.chamferTooth(ctx, spec)

    def loftTooth(self, ctx: GenerationContext, spec :SpurGearSpecification):
        topSketch = ctx.twistedGearProfileSketch
        bottomSketch = ctx.gearProfileSketch

        # loft from the bottom sketch to the top sketch
        lofts = self.component.features.loftFeatures

        bottomProfiles = bottomSketch.profiles
        topProfiles = topSketch.profiles

        def findProfile(profiles):
            for profile in profiles:
                for loop in profile.profileLoops:
                    if loop.profileCurves.count == 6:
                        return profile
            return None

        bottomToothProfile = findProfile(bottomProfiles) # bottomProfiles.item(0)
        topToothProfile = findProfile(topProfiles) # topProfiles.item(0)

        loftInput = lofts.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        loftInput.loftSections.add(bottomToothProfile)
        loftInput.loftSections.add(topToothProfile)
        loftResult = lofts.add(loftInput)
        ctx.toothBody = loftResult.bodies.item(0)
        ctx.toothBody.name = 'Tooth Body'