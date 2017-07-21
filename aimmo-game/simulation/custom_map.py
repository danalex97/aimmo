import abc
import math

from simulation.levels.levels import LEVELS
from simulation.levels.completion_checks import COMPLETION_CHECKS
from simulation.levels.decoders import *

from pprint import pprint

from simulation.location import Location
from simulation.game_state import GameState
from simulation.world_map import WorldMap
<<<<<<< HEAD
from simulation.world_map import DEFAULT_LEVEL_SETTINGS
from simulation.world_map import Cell

import sys
current_module = sys.modules[__name__]
=======
from simulation.world_map import WorldMapStaticSpawnDecorator
from simulation.world_map import DEFAULT_LEVEL_SETTINGS
from simulation.world_map import Cell
>>>>>>> 006af66... Changed the WorldMap static functions to a map generator. Now the whole thing work the same but the responsability is seaprated.

class BaseGenerator(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, settings):
        self.settings = settings

    def get_game_state(self, avatar_manager):
        return GameState(self.get_map(), avatar_manager, self.check_complete)

    def check_complete(self, game_state):
        return False

    @abc.abstractmethod
    def get_map(self):
        pass

class EmptyMapGenerator(BaseGenerator):
    def __init__(self, settings):
        self.height =  self.settings['START_HEIGHT']
        self.width = self.settings['START_WIDTH']
        self.settings = settings

    def __init__(self, height, width, settings):
        self.height = height
        self.width = width
        self.settings = settings

    def get_map(self):
        def _min_max_from_dimensions(height, width):
            max_x = int(math.floor(width / 2))
            min_x = -(width - max_x - 1)
            max_y = int(math.floor(height / 2))
            min_y = -(height - max_y - 1)
            return min_x, max_x, min_y, max_y

        new_settings = DEFAULT_LEVEL_SETTINGS.copy()
        new_settings.update(self.settings)

        (min_x, max_x, min_y, max_y) = _min_max_from_dimensions(self.height, self.width)
        grid = {}
        for x in xrange(min_x, max_x + 1):
            for y in xrange(min_y, max_y + 1):
                location = Location(x, y)
                grid[location] = Cell(location)
        return WorldMap(grid, new_settings)

class BaseLevelGenerator(BaseGenerator):
    __metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        super(BaseLevelGenerator, self).__init__(*args, **kwargs)
        self.settings.update(DEFAULT_LEVEL_SETTINGS)

class TemplateLevelGenerator(BaseLevelGenerator):
    __metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        super(TemplateLevelGenerator, self).__init__(*args, **kwargs)
        self.settings.update(DEFAULT_LEVEL_SETTINGS)

################################################################################

class JsonLevelGenerator(BaseLevelGenerator):
    """
        Workflow:
            - setup the metadata: map dimensions, etc.
            - register the json that represents the map
            - register the decoders that tranform the jsons into WorldMap objects
            - decode the map applying the decoder to each of the jsons

        All the levels can be found in json format in levels.LEVELS.
        To register a level extend this class.
    """
    def __init__(self, *args, **kwargs):
        super(JsonLevelGenerator, self).__init__(*args, **kwargs)

    def _setup_meta(self):
        # Used so that the map dimension does not increase automatically
        self.settings["TARGET_NUM_CELLS_PER_AVATAR"] = -1000

        self.meta = None
        # Finds the json with metaiformation
        for element in self.json_map:
            if element["code"] == "meta":
                self.meta = element

        if not self.meta is None:
            # Sets the empty map to the dimensions of the given level
            minX = - int((self.meta["cols"]) / 2)
            maxX = int((self.meta["cols"] - 1) / 2) + 1
            minY = -int((self.meta["rows"]) / 2)
            maxY = int((self.meta["rows"] - 1) / 2) + 1
            self.world_map = EmptyMapGenerator.get_map_by_corners(
                self.settings,
                (minY, maxY, minX, maxX))

    def _register_json(self, json_map):
        self.json_map = json_map
<<<<<<< HEAD
        self.world_map = WorldMap.generate_empty_map(15, 15, self.settings)
=======
        self.world_map = EmptyMapGenerator(100, 100, self.settings).get_map()
>>>>>>> 006af66... Changed the WorldMap static functions to a map generator. Now the whole thing work the same but the responsability is seaprated.

    def _register_decoders(self):
        self.decoders = DECODERS

    def _json_decode_map(self):
        def find_element_by_code(json, code):
            for element in json:
                if element["code"] == str(code):
                    yield element

        for decoder in self.decoders:
            for element in find_element_by_code(self.json_map, decoder.code):
                decoder.decode(element, self.world_map)

#### Dragons be here

def generate_level_class(level_nbr, LEVELS=LEVELS, COMPLETION_CHECKS=COMPLETION_CHECKS):
    level_name = "Level" + str(level_nbr)
    level_id = "level" + str(level_nbr)

    def get_map_by_level(level_id):
        def get_map(self):
            self._register_json(LEVELS[level_id])

            self._setup_meta()
            self._register_decoders()
            self._json_decode_map()

            return self.world_map

        return get_map

    ret_class = type(level_name, (JsonLevelGenerator,), {
        "get_map": get_map_by_level(level_id),
        "check_complete": COMPLETION_CHECKS[level_id]
    })

    return ret_class

for cur_level in xrange(1, len(LEVELS) + 1):
    gen_class = generate_level_class(cur_level)
    setattr(current_module, gen_class.__name__, gen_class)
