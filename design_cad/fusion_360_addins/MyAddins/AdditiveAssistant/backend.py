import adsk.core, adsk.fusion, adsk.cam, traceback
import math
import itertools

global good_feedback_img
global med_feedback_img
global bad_feedback_img

good_feedback_img = 'resources/rating/good.png'
med_feedback_img = 'resources/rating/med.png'
bad_feedback_img = 'resources/rating/bad.png'

global green_color
global orange_color
global red_color

green_color = adsk.fusion.CustomGraphicsSolidColorEffect.create(adsk.core.Color.create(0,255,0,255))
orange_color = adsk.fusion.CustomGraphicsSolidColorEffect.create(adsk.core.Color.create(255,165,0,255))
red_color = adsk.fusion.CustomGraphicsSolidColorEffect.create(adsk.core.Color.create(255,0,0,255))
gray_colour = adsk.fusion.CustomGraphicsSolidColorEffect.create(adsk.core.Color.create(128,128,128,255))


def calc_mesh(brepBody, quality):
    try:
        # Setup stuff
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Get mesh data from the B-Rep body.
        meshCalc = brepBody.meshManager.createMeshCalculator()

        if quality == 'Fast':
            meshCalc.setQuality(adsk.fusion.TriangleMeshQualityOptions.LowQualityTriangleMesh)
        elif quality == 'Normal':
            meshCalc.setQuality(adsk.fusion.TriangleMeshQualityOptions.NormalQualityTriangleMesh)
        triangleMesh = meshCalc.calculate()

        return triangleMesh
    except:
        if ui:
            ui.messageBox('Failed to calculate mesh:\n{}'.format(traceback.format_exc()))


def create_overlay(triangleMesh, problem_faces, colour):
    # Setup stuff
    app = adsk.core.Application.get()
    ui = app.userInterface
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)


    # Define the custom graphic groups
    _cgGroups = design.rootComponent.customGraphicsGroups
    MeshcgGroup = adsk.fusion.CustomGraphicsGroup.cast(_cgGroups.add())

    # Assign the variables needed to create the custom graphic mesh
    cgCoords = adsk.fusion.CustomGraphicsCoordinates.create(triangleMesh.nodeCoordinatesAsDouble)
    cgNormal = triangleMesh.normalVectorsAsDouble
    probNormal_index = problem_faces
    probCoords_index = problem_faces

    # Create the custom mesh and apply colour effect for mesh
    problemMesh = drawMesh(MeshcgGroup, cgCoords, probCoords_index, cgNormal, probNormal_index)
    problemMesh.color = colour
    problemMesh.setOpacity(0.5, True)

    return problemMesh


def create_bnd_overlay(bndBox, max_x, max_y, max_z, colour):
    # Setup stuff
    app = adsk.core.Application.get()
    ui = app.userInterface
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)

    # Convert to mm
    user_set_x = int(max_x) / 10
    user_set_y = int(max_y) / 10
    user_set_z = int(max_z) / 10

    # Define the custom graphic groups
    cgGroups = design.rootComponent.customGraphicsGroups

    # -------------------Create build area ----------------
    LinecgGroup = adsk.fusion.CustomGraphicsGroup.cast(cgGroups.add())

    maxZ = bndBox.minPoint.z + user_set_z

    tempx = user_set_x - (bndBox.maxPoint.x - bndBox.minPoint.x)
    minX = bndBox.minPoint.x - (tempx/2)
    maxX = bndBox.maxPoint.x + (tempx/2)

    tempy = user_set_y - (bndBox.maxPoint.y - bndBox.minPoint.y)
    miny = bndBox.minPoint.y - (tempy/2)
    maxy = bndBox.maxPoint.y + (tempy/2)

    minXYZ = [minX, miny, bndBox.minPoint.z]
    minXYmaxZ = [minX, miny, maxZ]
    minXmaxYZ = [minX, maxy, maxZ]
    minXZmaxY = [minX, maxy, bndBox.minPoint.z]
    
    maxXYZ = [maxX, maxy, maxZ]
    maxXYminZ = [maxX, maxy, bndBox.minPoint.z]
    maxXZminY = [maxX, miny, maxZ]
    maxXminYZ = [maxX, miny, bndBox.minPoint.z]

    index = []

    points_list = minXYZ + minXYmaxZ + minXYZ + minXZmaxY + minXZmaxY + minXmaxYZ + minXYmaxZ + minXmaxYZ + maxXYZ + maxXYminZ + maxXYZ + maxXZminY + maxXYminZ + maxXminYZ + maxXZminY + maxXminYZ + minXYZ + maxXminYZ + minXYmaxZ + maxXZminY + minXmaxYZ + maxXYZ + minXZmaxY + maxXYminZ 

    coordinates = adsk.fusion.CustomGraphicsCoordinates.create(points_list)

    build_volume = LinecgGroup.addLines(coordinates, index, False)

    build_volume.color = colour

    # ---------------- Create Bed --------------------
    BedcgGroup = adsk.fusion.CustomGraphicsGroup.cast(cgGroups.add())

    maxZ = bndBox.minPoint.z - 0.5

    minXYZ = [minX, miny, bndBox.minPoint.z]
    minXYmaxZ = [minX, miny, maxZ]
    minXmaxYZ = [minX, maxy, maxZ]
    minXZmaxY = [minX, maxy, bndBox.minPoint.z]

    minYZmaxX = [maxX, miny, bndBox.minPoint.z]
    minYmaxXZ = [maxX, miny, maxZ]
    
    maxXYZ = [maxX, maxy, maxZ]
    maxXYminZ = [maxX, maxy, bndBox.minPoint.z]
    maxXZminY = [maxX, miny, maxZ]
    maxXminYZ = [maxX, miny, bndBox.minPoint.z]

    bed_points_list = minXYZ + minXYmaxZ + minXmaxYZ + minXZmaxY + maxXYZ + maxXYminZ + maxXZminY + maxXminYZ + minYZmaxX + minYmaxXZ
    bed_coordinates = adsk.fusion.CustomGraphicsCoordinates.create(bed_points_list)

    coordinateIndexList = [0, 3, 8, 3, 8, 5, 0, 8, 1, 8, 1, 9, 8, 9, 4, 4, 8, 5, 3, 2, 5, 2, 5, 4, 0, 3, 1, 3, 1, 2, 1, 2, 9, 9, 2, 4]
    normalVectors = []
    normalIndexList = []

    virtual_bed = BedcgGroup.addMesh(bed_coordinates, coordinateIndexList, normalVectors, normalIndexList)

    virtual_bed.color = gray_colour
    virtual_bed.setOpacity(0.05, True)

    return build_volume, virtual_bed


def create_basic_graphics(body):
    # Setup stuff
    app = adsk.core.Application.get()
    ui = app.userInterface
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)

    gray_colour = adsk.fusion.CustomGraphicsSolidColorEffect.create(adsk.core.Color.create(128,128,128,255))
    # Define the custom graphic groups
    _cgGroups = design.rootComponent.customGraphicsGroups
    cgGroup = adsk.fusion.CustomGraphicsGroup.cast(_cgGroups.add())

    cgBody = cgGroup.addBRepBody(body)
    cgBody.color = gray_colour
    cgBody.setOpacity(0.15, True)

    return cgBody


def calculate_build_angle(coords):
    try:
        x = coords[0]
        y = coords[1]
        z = coords[2]

        xy_component = math.sqrt(x*x+y*y)
        return math.atan2(z, xy_component)
    except:
        return float('nan')


def overhang_analyse(triangleMesh, i, overhang_angle):
    coords = []
    coords.append(triangleMesh.normalVectors[i].x)
    coords.append(triangleMesh.normalVectors[i].y)
    coords.append(triangleMesh.normalVectors[i].z)

    angle = calculate_build_angle(coords)

    angleTol = 0.0349066
    minAngle = math.radians(overhang_angle)

    if (0 <= angle + math.pi/2 < minAngle + angleTol):
        return True
    else:
        return False


# Builds a custom graphics mesh.
def drawMesh(cgGroup, node_coords, cgCoords_index, normals, normalIndexList):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        cgMesh = cgGroup.addMesh(node_coords, cgCoords_index, normals, normalIndexList)

        return cgMesh
        
    except Exception as error:
        ui.messageBox("drawMesh Failed: " + str(error)) 
        return None


def inspectSize(body, size_traffic_light, dimensions, max_x, max_y, max_z):

    # Defining the max xyz values to compare against
    max_x = max_x / 10
    max_y = max_y / 10
    max_z = max_z / 10

    # Compare and provide feedback.
    if dimensions[0] < max_x and dimensions[1] < max_y and dimensions[2] < max_z:
        size_result = 'Good'
        size_traffic_light.imageFile = good_feedback_img
    else:
        size_result = 'Bad'
        size_traffic_light.imageFile = bad_feedback_img
    
    return size_result


def bndBoxDimensions(body):
    # Creating the boundry box
    bndBox= body.boundingBox

    x_val = bndBox.maxPoint.x - bndBox.minPoint.x
    y_val = bndBox.maxPoint.y - bndBox.minPoint.y
    z_val = bndBox.maxPoint.z - bndBox.minPoint.z

    dimensions = [x_val, y_val, z_val]

    return dimensions, bndBox


def find_lowest_point(mesh, problem_faces):

    # Find the lowest z value
    lowest_z = None
    for i in problem_faces:
        node = mesh.nodeCoordinates[i]

        if lowest_z == None:
            lowest_z = node.z
        elif lowest_z > node.z:
            lowest_z = node.z
        else:
            pass
        
    return lowest_z


def bottom_face_analysis(mesh, problem_indices, lowest_point):

    overhang_indidices = []
    bottom_faces = []
    #added = []

    toll = 0.01

    while True:
        if len(problem_indices) % 3 != 0:
            del problem_indices[0]
            #added.append(problem_indices[0])
            #problem_indices = added + problem_indices
            #added.clear()
        else:
            break

    for item in itertools.zip_longest(*[iter(problem_indices)]*3, fillvalue=''):

        first_node_z = mesh.nodeCoordinates[item[0]].z
        second_node_z = mesh.nodeCoordinates[item[1]].z
        third_node_z = mesh.nodeCoordinates[item[2]].z

        if lowest_point - toll <= first_node_z <= lowest_point + toll or lowest_point - toll <= second_node_z <= lowest_point + toll or lowest_point - toll <= third_node_z <= lowest_point + toll:
            bottom_faces.append(item[0])
            bottom_faces.append(item[1])
            bottom_faces.append(item[2])
        else:
            overhang_indidices.append(item[0])
            overhang_indidices.append(item[1])
            overhang_indidices.append(item[2])

    return overhang_indidices, bottom_faces


def create_list_points(mesh, bottom_faces):
    x_list = []
    y_list = []

    for item in bottom_faces:
        x_list.append(mesh.nodeCoordinates[item].x)
        y_list.append(mesh.nodeCoordinates[item].y)
    
    return x_list, y_list


# I think this is right but not 100% sure. 
# Reach out to someone to check
def get_triangles_area(x, y):

    total_area = 0
    length = int(len(x)/3)

    for i in range(length):
        #calculate area and add to total
        try:
            area = abs(0.5*( (x[0]*(y[1]-y[2])) + (x[1]*(y[2]-y[0])) + (x[2]*(y[0]-y[1]))))
            
            total_area = total_area + area

            # remove used values from list
            x_list.pop(0)
            x_list.pop(1)
            x_list.pop(2)
            y_list.pop(0)
            y_list.pop(1)
            y_list.pop(2)
        except:
            pass

    return total_area


def inspectWarping(area, warping_traffic_light, dimensions, material):
    # Not sure if this is the cleanest way to calculate this but seems to work
    variable = 0
    z_val = dimensions[2]

    if area > 500:
        variable = 2
    elif area > 300 and area < 500:
        variable = 1
    else:
        variable = 0

    if z_val < 1:
        pass
    elif z_val > 1 and z_val < 5:
        variable -= 1
    elif z_val > 5:
        variable -= 2

    if material == 'ABS':
        variable += 1

    if variable <= 0 :
        prob_issue = 'Low'
        warping_traffic_light.imageFile = good_feedback_img
        return green_color, prob_issue
    if variable == 1:
        prob_issue = 'Medium'
        warping_traffic_light.imageFile = med_feedback_img
        return orange_color, prob_issue
    if variable >= 2:
        prob_issue = 'High'
        warping_traffic_light.imageFile = bad_feedback_img
        return red_color, prob_issue


def inspectStability(area, stability_traffic_light, dimensions):
    # Again, not sure if this is the cleanest way to calculate this but seems to work
    variable = 0
    z_val = dimensions[2]

    if area > 5:
        pass
    elif area < 5 and area > 2.5:
        variable = 1
    elif area < 2.5:
        variable = 2

    if z_val < 10:
        variable -= 1
    else:
        pass

    if variable <= 0 :
        prob_issue = 'Low'
        stability_traffic_light.imageFile = good_feedback_img
        return green_color, prob_issue
    if variable == 1:
        prob_issue = 'Medium'
        stability_traffic_light.imageFile = med_feedback_img
        return orange_color, prob_issue
    if variable >= 2:
        prob_issue = 'High'
        stability_traffic_light.imageFile = bad_feedback_img
        return red_color, prob_issue


def inspectOverhang(overhang_faces, triangles, overhang_traffic_light):

    percentage_overhang = (len(overhang_faces) / triangles) * 100

    if percentage_overhang < 10:
        overhang_traffic_light.imageFile = good_feedback_img
        return False
    else:
        overhang_traffic_light.imageFile = bad_feedback_img
        return True
