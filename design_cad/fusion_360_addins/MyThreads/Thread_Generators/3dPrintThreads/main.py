import xml.etree.ElementTree as ET
import math
from abc import ABC, abstractmethod

#THREAD_ALGORITHM = "simple"
#THREAD_ALGORITHM = "Normal"
THREAD_ALGORITHM = "Bottle"
UNIT = "mm"
# **Shape:** 60° trapezoidal
ANGLE = 45.0
SIZES = []
# Outer diameter in millimeter 
if THREAD_ALGORITHM == "Bottle":
    SIZES.extend([(elem, 12) for elem in list(range(3, 15))])
    SIZES.extend([(elem, 8) for elem in list(range(16, 24))])
    SIZES.extend([(elem, 6) for elem in list(range(25, 77))])
    SIZES.extend([(elem, 5) for elem in list(range(78, 120))])
else:
    SIZES = [(elem, 0) for elem in list(range(3, 51))]
# Pitch Diameter Offset, it is subtracted from Outer Diameter to calculate pitch diameter
PITCHES = [1, 1.5, 2, 2.5, 3.5, 5.0]
# Thread tolerances 
OFFSETS = [.0, .1, .2, .3, .4, .8]

THREADS_PER_INCH = []

# Thread Library Name
if THREAD_ALGORITHM == "simple":
    NAME = "3D-Printed Trapezoidal {0:d}".format(int(ANGLE))
else:
    NAME = "3D-Printed Trapezoidal {0:d} {1}".format(int(ANGLE),THREAD_ALGORITHM)

def designator(val: float):
    if int(val) == val:
        return str(int(val))
    else:
        return str(val)


class Thread:
    def __init__(self):
        self.gender = None
        self.clazz = None
        self.majorDia = 0
        self.pitchDia = 0
        self.minorDia = 0
        self.tapDrill = None


class ThreadProfile(ABC):
    @abstractmethod
    def sizes(self):
        pass

    @abstractmethod
    def designations(self, size):
        pass

    @abstractmethod
    def threads(self, designation):
        pass


class Metric3Dprinted(ThreadProfile):
    class Desig:
        def __init__(self, size, pitch):
            self.size = size
            self.pitch = pitch
            self.name = "M{}x{}".format(designator(self.size), designator(self.pitch))

        def depth(self):
            return self.pitch

    def __init__(self):
        self.offsets = OFFSETS

    def sizes(self):
        return SIZES

    def radians(self, deg):
        return deg * math.pi / 180

    def degrees(self, rad):
        return rad * 180 / math.pi

    def designations(self, size):
        return [Metric3Dprinted.Desig(size, pitch) for pitch in PITCHES]

    def threads(self, designation):
        ts = []
        for offset in self.offsets:
            offset_decimals = str(offset)[2:]  # skips the '0.' at the start
            # Pitch Offset
            depth = designation.depth()

            # Set the major diameter, the offset is subtracted from major diameter for 3d printer tolerance 
            externalMajorD = designation.size - offset - .25
            # Subtract the pitch offset from major diameter for pitch diameter (depth == pitch offset)
            externalPitchD = designation.size - offset - depth / 2 - .7
            # Subtract the pitch diameter from major diameter for minor diameter
            externalMinorD = designation.size - offset - depth - .8
            # Set the major diameter, the offset is added to major diameter for 3d printer tolerance 
            internalMajorD = designation.size + offset + .4
            # Subtract the pitch offset from major diameter for pitch diameter (depth == pitch offset)
            internalPitchD = designation.size + offset - depth / 2 - .4
            # Subtract the pitch diameter from major diameter for minor diameter
            internalMinorD = designation.size + offset - depth

            # the tolerances below are based on ISO M30x3.5 6g/6H
            t = Thread()
            t.gender = "external"
            t.clazz = "O.{}".format(offset_decimals)
            t.majorDia = externalMajorD
            t.pitchDia = externalPitchD
            t.minorDia = externalMinorD
            ts.append(t)

            t = Thread()
            t.gender = "internal"
            t.clazz = "O.{}".format(offset_decimals)
            t.majorDia = internalMajorD
            t.pitchDia = internalPitchD
            t.minorDia = internalMinorD
            # Set tap drill diameter
            t.tapDrill = internalMinorD
            ts.append(t)
        return ts

    def threadsNormal(self, designation):
        ts = []
        for offset in self.offsets:
            offset_decimals = str(offset)[2:]  # skips the '0.' at the start
            depth = designation.depth()

            radius = size/2
            height = math.tan(self.radians((90-(ANGLE/2)))) * (depth / 2)
            crestH = math.tan(self.radians(90-(ANGLE/2))) * (depth / 8)
            pitchH = math.tan(self.radians(90-(ANGLE/2))) * (depth / 4)
            rootH = math.tan(self.radians(90-(ANGLE/2))) * (depth / 8)

            MajorRadius = radius
            pitchRadius = radius - pitchH + crestH
            minorRadius = radius - height + rootH + crestH

            externalMajorD = (MajorRadius - offset) * 2
            externalPitchD = (pitchRadius - (offset / math.sin(self.radians(ANGLE/2)))) * 2
            externalMinorD = (minorRadius - offset) * 2
            internalMajorD = (MajorRadius + offset) * 2
            internalPitchD = (pitchRadius + (offset / math.sin(self.radians(ANGLE/2)))) *2
            internalMinorD = (minorRadius + offset) * 2

            # the tolerances below are based on ISO M30x3.5 6g/6H
            t = Thread()
            t.gender = "external"
            t.clazz = "O.{}".format(offset_decimals)
            t.majorDia = externalMajorD
            t.pitchDia = externalPitchD
            t.minorDia = externalMinorD
            ts.append(t)

            t = Thread()
            t.gender = "internal"
            t.clazz = "O.{}".format(offset_decimals)
            t.majorDia = internalMajorD
            t.pitchDia = internalPitchD
            t.minorDia = internalMinorD
            t.tapDrill = internalMinorD
            ts.append(t)
        return ts

profile = Metric3Dprinted()


root = ET.Element('ThreadType')
tree = ET.ElementTree(root)

ET.SubElement(root, "Name").text = NAME
ET.SubElement(root, "CustomName").text = NAME
ET.SubElement(root, "Unit").text = UNIT
ET.SubElement(root, "Angle").text = str(ANGLE)
ET.SubElement(root, "SortOrder").text = "3"


for size,tpi in profile.sizes():
    ts = ET.SubElement(root, "ThreadSize")
    ET.SubElement(ts, "Size").text = str(size)
    for des in profile.designations(size):
        deselem = ET.SubElement(ts, "Designation")
        ET.SubElement(deselem, "ThreadDesignation").text = des.name
        ET.SubElement(deselem, "CTD").text = des.name
        ET.SubElement(deselem, "Pitch").text = str(des.pitch)
        if tpi>0:
            ET.SubElement(deselem,"TPI").text = "{:.1g}".format(round(tpi,1)) 
        if THREAD_ALGORITHM == "simple":
            threadData = profile.threads(des)
        elif THREAD_ALGORITHM == "Bottle":
            threadData = profile.threads(des)
        else:
            threadData = profile.threadsNormal(des)
        for t in threadData:
            elem = ET.SubElement(deselem, "Thread")
            ET.SubElement(elem, "Gender").text = t.gender
            ET.SubElement(elem, "Class").text = t.clazz
            ET.SubElement(elem, "MajorDia").text = "{:.4g}".format(round(t.majorDia,3))
            ET.SubElement(elem, "PitchDia").text = "{:.4g}".format(round(t.pitchDia,3))
            ET.SubElement(elem, "MinorDia").text = "{:.4g}".format(round(t.minorDia,3))
            if t.tapDrill:
                ET.SubElement(elem, "TapDrill").text = "{:.4g}".format(round(t.tapDrill,3))

ET.indent(tree)

fileBaseName = NAME.replace(" ","-")

tree.write(fileBaseName + '.xml', encoding='UTF-8', xml_declaration=True)
