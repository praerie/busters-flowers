from maya import cmds 
import math


FIBONACCI_LAYER_SETS = [
        (3, 3, 3), (5, 5, 3), (8, 8, 5), (13, 8, 5), 
        (21, 13, 8), (34, 21, 13), (55, 34, 21)
    ]

PETAL_VERTEX_MOVES = [
        (0.1, 0.13, 0.18), (0.2, 0.15, 0.21), 
        (0.4, 0.17, 0.23), (0.6, 0.15, 0.24),
        (0.8, 0.16, 0.18), (1, 0.2, 0)
    ]

SUNFLOWER = {
    'width': 1, 'height': 0.1, 'depth': 0.2, 
    'subdiv-x': 8, 'subdiv-y': 1, 'subdiv-z': 1,
    'radius': 1, 'petal_edge': 1.4
}

DAISY = {}

ASTER = {}

def create_flower(flower_type=SUNFLOWER, base_petal_count=34):
    """
    creates a flower in Maya with petals arranged around a disk

    parameters:
    - flower_type (str): type of flower; default is 'sunflower'
    - base_petal_count (int): number of petals in base layer

    returns:
    - flower_disk (str): name of created flower disk object in Maya
    - all_petals (list): list of all arranged petal objects in Maya
    """
    all_petals = []
    
    # determine petals per layer 
    petal_base, petal_mid, petal_inner = find_layer_set(base_petal_count)

    # create flower disk based on flower type and number of base petals
    flower_disk = create_disk(flower_type, base_petal_count)

    # define layer types and corresponding petal counts
    layer_types = ['base', 'mid', 'inner']
    petal_counts = [petal_base, petal_mid, petal_inner]

    for layer_type, petal_count in zip(layer_types, petal_counts):
        # create petal shape based on layer and flower type
        petal_shape = create_petal(layer_type, flower_type)

        # arrange petals around disk for current layer type
        arranged_layer = arrange_petals(petal_shape, petal_count, flower_type, layer_type)
        all_petals.append(arranged_layer)

    return flower_disk, all_petals


def find_layer_set(base_petals):
    """
    finds the layer set corresponding to the given number of base petals
    
    parameters:
    - base_petals (int): number of petals in base layer
    
    returns:
    - petal_base (int): number of petals in base layer
    - petal_mid (int): number of petals in mid layer
    - petal_inner (int): number of petals in inner layer
    
    raises:
    - ValueError: if no matching layer set is found for the given base petals
    """
    for layer_set in FIBONACCI_LAYER_SETS:
        if layer_set[0] == base_petals:
            base, mid, inner = layer_set
            return base, mid, inner

    raise ValueError(f"no matching layer set found for petal count: {base_petals}")


def create_disk(flower_type, petal_count):
    """
    creates a flower disk based on flower type and number of petals

    parameters:
    - flower_type (dict): dictionary containing the flower's attributes
    - petal_count (int): number of petals to determine disk's subdivisions
    """
    disk = cmds.polyCylinder(r=flower_type['radius'], h=flower_type['height'], 
                             sx=petal_count, sy=1, sz=1, 
                             ax=(0, 1, 0), rcp=0, cuv=3, ch=1)[0]
    return disk


def create_petal(layer_type, flower_type):
    """
    creates petals based on flower_type dimensions and adjusts them based on layer_type

    parameters:
    - layer_type (str): type of layer ('base', 'mid', 'inner')
    - flower_type (dict): dictionary containing dimensions ('width', 'height', 'depth', 'subdiv-x', 'subdiv-y')

    returns:
    - petal (str): name of created petal object in Maya
    """
    # create shape with dimensions based on flower type
    petal = cmds.polyCube(w=flower_type['width'], h=flower_type['height'], d=flower_type['depth'], 
                          sx=flower_type['subdiv-x'], sy=flower_type['subdiv-y'], name='petal')[0]

    # draw petal curvature based on flower type
    move_vertices(petal, 'L', 12, 17)
    move_vertices(petal, 'R', 21, 26)
    # to-do: 
        # - automatically find vertices
        # - adjust based on flower_type

    return petal


def move_vertices(petal, side, first_vertex, last_vertex):
    """
    moves vertices of a shape to create petal curvature on specified side

    parameters:
    - petal (str): name of the petal object in Maya
    - side (str): side to create curvature ('L' for left, 'R' for right)
    - first_vertex (int): index of the first vertex to move
    - last_vertex (int): index of the last vertex to move
    """
    for i in range(first_vertex, last_vertex + 1):
        # create petal curvature on left
        if side == 'L': 
            pos = PETAL_VERTEX_MOVES[i - first_vertex]
            cmds.move(pos[0], pos[1], pos[2], '{}.vtx[{}]'.format(petal, i))

        # create petal curvature on right
        elif side == 'R': 
            pos = PETAL_VERTEX_MOVES[i - first_vertex]
            cmds.move(pos[0], pos[1], -pos[2], '{}.vtx[{}]'.format(petal, i))


def transform_petal(petal):
    """
    transforms given petal by scaling and tilting it based on the provided parameters

    parameters:
    - petal (str): name of petal object in Maya
    - flower_type (dict): dictionary containing dimensions ('width', 'height', 'depth', 'subdiv-x', 'subdiv-y')
    - scale_factor (float): scale factor to adjust petal size; default is 1.0 (no scaling)
    - tilt_degree (float): tilt angle in degrees to rotate petal; default is 0.0 (no tilt)
    """
    cmds.scale(0.7, 0.5, 0.8, petal) 
    # to-do:
        # more dynamic scaling and tilt, account for flower_type


def arrange_petals(petal, petal_count, flower_type, layer):
    flower_petals = []

    # calculate angle increment to evenly distribute petals around disk
    rotation_increment = 360.0 / petal_count

    # place petals around flower disk
    for i in range(petal_count):
        angle = i * rotation_increment # calculate rotation angle for petal

        petal_instance = cmds.duplicate(petal)[0] # duplicate petal
        cmds.rotate(90, 0, 0, petal_instance) # lay petal flat

        # position petal at edge of flower disk 
            # need to change Z positioning for mid and inner
        radius = flower_type['petal_edge']
        x = radius * math.cos(math.radians(angle))
        z = radius * math.sin(math.radians(angle))
        y = 0 # default

        # to-do scale, tilt, and position petal based on layer type
        if layer == 'inner':
            transform_petal(petal)
        elif layer == 'mid':
            transform_petal(petal)

        cmds.move(x, y, z, petal_instance)

        # rotate petal to align with face of flower disk 
        cmds.rotate(0, -angle, 0, petal_instance)

        # save petal to list
        flower_petals.append(petal_instance)

    # delete original petal used for duplication
    cmds.delete(petal)

    # clear selection
    cmds.select(clear=True)
    
    return flower_petals

