import adsk.core
import time

class Joints(object):
    def __init__(self, app):
        self.app = app
        self.ui = self.app.userInterface
        self.data = self.app.data
        self.documents = self.app.documents        
        
        self.product = self.app.activeProduct
        self.design = adsk.fusion.Design.cast(self.product)
        self.rootComp = self.design.rootComponent        

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def makeJoints(self, src_selection, jointOrigins, offset: int = 0, angle: int = 0, isFlipped: bool = False, hideJoints: bool = False):

        self.design.timeline
        JointOrigin = None
        if (src_selection[0].entity.objectType == adsk.fusion.JointOrigin.classType()):
            JointOrigin = src_selection[0].entity
        elif (src_selection[0].entity.objectType == adsk.fusion.Occurrence.classType()):
            if hasattr(src_selection[0].entity.component, 'jointOrgins'):
                JointOrigin = src_selection[0].entity.component.jointOrgins[0].createForAssemblyContext(src_selection[0].entity)

        if not JointOrigin:
            self.ui.messageBox('Please select Component with JointOrigin or JointOrigin')
            return

        

        count = len(jointOrigins)
        occurrence = JointOrigin.assemblyContext
        rectangularFeature = self.makePattern(occurrence, self.rootComp.xConstructionAxis, count + 1)

        joints = []
        for j in range(0, count):
            joint = self.makeJoint(
                jointOrigins[j].entity, 
                rectangularFeature.patternElements[j + 1].occurrences[0],
                offset, angle, isFlipped)

            joints.append(joint)
            if hideJoints:
                joint.isLightBulbOn  = False

        if len(joints) > 3:
            self.design.timeline.timelineGroups.add(joints[0].timelineObject.index, joints[len(joints)-1].timelineObject.index)
            

        

    def makeJoint(self, jointOrigin, joinOccurrence, offset: int = 0, angle: int = 0, isFlipped: bool = False):

        joints = self.rootComp.joints
        # joints = joinOccurrence.sourceComponent.joints
        # joints = joinOccurrence.component.joints
        jointOriginEntity = jointOrigin

        if not hasattr(jointOriginEntity, 'objectType'):
            print('no objectType')
            return

        if (jointOriginEntity.objectType == adsk.fusion.SketchPoint.classType() or
                jointOriginEntity.objectType == adsk.fusion.ConstructionPoint.classType() or
                jointOriginEntity.objectType == adsk.fusion.BRepVertex.classType()):
            entity = adsk.fusion.JointGeometry.createByPoint(jointOriginEntity)
        if (jointOriginEntity.objectType == adsk.fusion.JointOrigin.classType()):
            entity = jointOriginEntity
        if (jointOriginEntity.objectType == adsk.fusion.BRepEdge.classType()):
            entity = adsk.fusion.JointGeometry.createByCurve(jointOriginEntity, adsk.fusion.JointKeyPointTypes.CenterKeyPoint)


        # origin = joinOccurrence.component.jointOrgins[0].createForAssemblyContext(joinOccurrence)
        origin = joinOccurrence.component.jointOrgins[0].createForAssemblyContext(joinOccurrence)
        # originB = joinOccurrence.component.jointOrgins[0].createForAssemblyContext(joinOccurrence)
        # originA = joinOccurrence.component.jointOrgins[0]
        # # originC = adsk.fusion.JointGeometry.createByPoint(joinOccurrence.bRepBodies[0].edges[0].pointOnEdge)
        # originC = adsk.fusion.JointGeometry.createByCurve(joinOccurrence.bRepBodies[0].edges[0], adsk.fusion.JointKeyPointTypes.CenterKeyPoint)

        # origin = adsk.fusion.JointGeometry.createByPoint(joinOccurrence.component.originConstructionPoint)

        jointInput = joints.createInput(origin , entity)

        # Set the joint input
        jointInput.angle = adsk.core.ValueInput.createByReal(angle)
        jointInput.offset = adsk.core.ValueInput.createByReal(offset)

        # if (jointOrigin.entity.objectType == adsk.fusion.BRepEdge.classType()):
        #     jointInput.isFlipped = False
        # else:
        #     jointInput.isFlipped = True

        jointInput.isFlipped = isFlipped
        jointInput.setAsRigidJointMotion()

        #Create the joint
        joint = joints.add(jointInput)
        return joint


    def makePattern(self, Component, axis, count: int) -> adsk.fusion.RectangularPatternFeature:
        
        # Create input entities for rectangular pattern
        inputEntites = adsk.core.ObjectCollection.create()
        inputEntites.add(Component)
        
        # Create path for path pattern
        # path = features.createPath(rootComp.xConstructionAxis)
        
        # Quantity and distance
        quantity = adsk.core.ValueInput.createByReal(count)
        patternDistance = adsk.core.ValueInput.createByString('1 cm')

        # Create the input for rectangular pattern
        rectangularPatterns = self.rootComp.features.rectangularPatternFeatures
        rectangularPatternInput = rectangularPatterns.createInput(inputEntites, axis, quantity, patternDistance, adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)

        rectangularPatternInput.setDirectionTwo(self.rootComp.yConstructionAxis, adsk.core.ValueInput.createByReal(1), patternDistance)

        rectangularFeature = rectangularPatterns.add(rectangularPatternInput)
        return rectangularFeature
