from maya import cmds
import math

class Flower:
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
        'width': 1, 'height': 0.05, 'depth': 0.2,
        'subdiv-x': 8, 'subdiv-y': 1, 'subdiv-z': 1,
        'radius': 0.8, 'petal_edge':  0.6
    }

    # DAISY = {}
    # ASTER = {}

    def __init__(self, flower_type=SUNFLOWER, base_petal_count=21):
        self.flower_type = flower_type
        self.base_petal_count = base_petal_count
        self.all_petals = [] 

    def create_flower(self):
        """
        Creates a flower in Maya with petals arranged around a disk.

        Parameters:
        - flower_type (dict): type of flower; default is 'SUNFLOWER'
        - base_petal_count (int): number of petals in base layer

        Returns:
        - flower_disk (str): name of created flower disk object in Maya
        - all_petals (list): list of all arranged petal objects in Maya
        """
        print("Creating flower with base petal count:", self.base_petal_count)

        # Determine petals per layer 
        petal_base, petal_mid, petal_inner = self._find_layer_set(self.base_petal_count)
        print("Petal counts for layers - Base:", petal_base, ", Mid:", petal_mid, ", Inner:", petal_inner)

        # Create flower disk based on flower type and number of base petals
        flower_disk = self._create_disk(self.base_petal_count)
        print("Created flower disk:", flower_disk)

        # Define layer types and corresponding petal counts
        layer_types = ['base', 'mid', 'inner']
        petal_counts = [petal_base, petal_mid, petal_inner]

        for layer_type, petal_count in zip(layer_types, petal_counts):
            # Create petal shape based on layer and flower type
            petal_shape = self._create_petal(layer_type) # layer_type is not currently being used in _create_petal
            print(f"Created {layer_type} petal shape:", petal_shape)

            # Arrange petals around disk for current layer type
            arranged_layer = self._arrange_petals(petal_shape, petal_count, layer_type)
            print(f"Arranged {layer_type} layer petals:", arranged_layer)
            self.all_petals.extend(arranged_layer)

        return flower_disk, self.all_petals

    def _find_layer_set(self, base_petals):
        """
        Finds the layer set corresponding to the given number of base petals.

        Parameters:
        - base_petals (int): number of petals in base layer

        Returns:
        - petal_base (int): number of petals in base layer
        - petal_mid (int): number of petals in mid layer
        - petal_inner (int): number of petals in inner layer

        Raises:
        - ValueError: if no matching layer set is found for the given base petals
        """
        for layer_set in Flower.FIBONACCI_LAYER_SETS:
            if layer_set[0] == base_petals:
                print("Found layer set:", layer_set)
                return layer_set
            
        raise ValueError(f"No matching layer set found for petal count: {base_petals}")

    def _create_disk(self, petal_count):
        """
        Creates a flower disk based on flower type and number of petals.

        Parameters:
        - flower_type (dict): dictionary containing the flower's attributes
        - petal_count (int): number of petals to determine disk's subdivisions

        Returns:
        - disk (str): name of the created flower disk object in Maya
        """
        print("Creating disk with petal count:", petal_count)
        
        disk = cmds.polyCylinder(
            r=self.flower_type['radius'], h=self.flower_type['height'],
            sx=petal_count, sy=1, sz=1, 
            ax=(0, 1, 0), rcp=0, cuv=3, ch=1
        )[0]

        # Adjust disk position to align with petals
        cmds.move(0, self.flower_type['height'] + 0.08, 0, disk)
        print("Moved disk to position:", (0, self.flower_type['height'] + 0.08, 0))

        return disk

    def _create_petal(self, layer_type):
        """
        Creates petals based on flower_type dimensions and adjusts them based on layer_type.

        Parameters:
        - layer_type (str): type of layer ('base', 'mid', 'inner')
        - flower_type (dict): dictionary containing dimensions ('width', 'height', 'depth', 'subdiv-x', 'subdiv-y')

        Returns:
        - petal (str): name of the created petal object in Maya
        """
        print("Creating petal for layer type:", layer_type)

        # Create shape with dimensions based on flower type
        petal = cmds.polyCube(
            w=self.flower_type['width'], h=self.flower_type['height'], d=self.flower_type['depth'], 
            sx=self.flower_type['subdiv-x'], sy=self.flower_type['subdiv-y'], name='petal'
        )[0]

        # Save petal vertices to list
        num_vertices = cmds.polyEvaluate(petal, vertex=True)
        print("Number of vertices in petal:", num_vertices)

        # Draw petal curvature based on flower type
        self._move_vertices(petal, num_vertices)

        return petal

    def _move_vertices(self, petal, num_vertices):
        """
        Moves vertices of a shape to create petal curvature on specified side.

        Parameters:
        - petal (str): name of the petal object in Maya
        - num_vertices (int): total number of vertices in the petal
        """
        print("Moving vertices for petal:", petal)
        
        # Split vertices into left and right lists
        left_vertices, right_vertices = self._get_vertex_ranges(num_vertices)
        print("Left vertices:", list(left_vertices), "Right vertices:", list(right_vertices))

        # Create petal curvature on left
        for i, vertex in enumerate(left_vertices):
            pos = Flower.PETAL_VERTEX_MOVES[i % len(Flower.PETAL_VERTEX_MOVES)]
            cmds.move(pos[0], pos[1], pos[2], '{}.vtx[{}]'.format(petal, vertex))
            print(f"Moved left vertex {vertex} to position:", pos)
        
        # Create petal curvature on right
        for i, vertex in enumerate(right_vertices):
            pos = Flower.PETAL_VERTEX_MOVES[i % len(Flower.PETAL_VERTEX_MOVES)]
            cmds.move(pos[0], pos[1], -pos[2], '{}.vtx[{}]'.format(petal, vertex))
            print(f"Moved right vertex {vertex} to position:", (pos[0], pos[1], -pos[2]))

    def _get_vertex_ranges(self, vertex_count):
        """
        Determines vertex ranges for left and right sides.

        Parameter:
        - vertex_count (int): total number of vertices

        Returns:
        - left_vertices (list): list of vertex indices for left side
        - right_vertices (list): list of vertex indices for right side
        """
        print("Getting vertex ranges for vertex count:", vertex_count)

        left_vertices = range(0, vertex_count // 2) # (start, halfway point - 1)
        right_vertices = range(vertex_count // 2, vertex_count) # (halfway point, total - 1)

        print("Left vertex range:", list(left_vertices), "Right vertex range:", list(right_vertices))
        return left_vertices, right_vertices

    def _transform_petal(self, petal, layer):
        """
        Transforms given petal by scaling and tilting it based on layer type.

        Parameters:
        - petal (str): name of petal object in Maya
        - flower_type (dict): dictionary containing dimensions ('width', 'height', 'depth', 'subdiv-x', 'subdiv-y')
        - layer (str): type of layer ('base', 'mid', 'inner')
        """
        print(f"Transforming petal {petal} for layer {layer}")
        
        cmds.scale(0.7, 0.5, 0.8, petal)
        print("Scaled petal:", petal)
        
    def _arrange_petals(self, petal, petal_count, layer):
        """
        Arranges petals around the flower disk.

        Parameters:
        - petal (str): name of the petal object in Maya
        - petal_count (int): number of petals in the layer
        - flower_type (dict): dictionary containing dimensions
        - layer (str): type of layer ('base', 'mid', 'inner')

        Returns:
        - flower_petals (list): list of arranged petal objects in Maya
        """
        flower_petals = []

        # Calculate angle increment to evenly distribute petals around disk
        rotation_increment = 360.0 / petal_count

        # Place petals around flower disk
        for i in range(petal_count):
            angle = i * rotation_increment
            petal_instance = cmds.duplicate(petal)[0]
            cmds.rotate(0, -angle, 0, petal_instance) # Lay petal flat

            # Transform petals with scale and tilt based on layer type
            # self._transform_petal(petal_instance, layer)

            # Position petal at edge of flower disk
            radius = self.flower_type['petal_edge']
            x = radius * math.cos(math.radians(angle))
            z = radius * math.sin(math.radians(angle))
            y = 0 # Default
            cmds.move(x, y, z, petal_instance)
            print(f"Positioned petal instance at: ({x}, {y}, {z}) with rotation angle {angle}")

            # # Rotate petal to align with face of flower disk
            # cmds.rotate(0, -angle, 0, petal_instance)

            # Save petal
            flower_petals.append(petal_instance)

        # Delete original petal used for duplication
        cmds.delete(petal)

        # Clear selection
        cmds.select(clear=True)
        print("Deleted original petal used for duplication.")

        return flower_petals

flower = Flower()
flower_disk, all_petals = flower.create_flower()
print("Created flower with disk:", flower_disk, "and petals:", all_petals)
