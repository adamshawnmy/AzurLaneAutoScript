from .campaign_base import CampaignBase
from module.map.map_base import CampaignMap
from module.map.map_grids import SelectedGrids, RoadGrids
from module.logger import logger

MAP = CampaignMap('SOS')
MAP.shape = 'H7'
MAP.camera_data = ['D3', 'D5']
MAP.camera_data_spawn_point = ['D3', 'D5']
MAP.map_data = """
    ++ ++ ME -- ME -- ME --
    ++ ++ ME ME -- ++ -- ME
    -- Me ME ME SP -- ME ME
    MB Me __ Me ME ME -- ++
    -- ++ ME Me ME -- ME ++
    ME ++ ME ME SP ME -- ME
    -- ME ME -- ME -- ++ ME
"""
MAP.weight_data = """
    50 50 50 50 50 50 50 50
    50 50 13 50 50 50 50 50
    50 11 12 13 50 50 50 50
    10 11 12 12 13 50 50 50
    50 50 12 13 50 50 50 50
    50 50 13 50 50 50 50 50
    50 50 50 50 50 50 50 50
"""
MAP.spawn_data = [
    {'battle': 0, 'enemy': 4},
    {'battle': 1, 'enemy': 2},
    {'battle': 2, 'enemy': 2},
    {'battle': 3, 'enemy': 1},
    {'battle': 4, 'enemy': 2, 'boss': 1},
]
A1, B1, C1, D1, E1, F1, G1, H1, \
A2, B2, C2, D2, E2, F2, G2, H2, \
A3, B3, C3, D3, E3, F3, G3, H3, \
A4, B4, C4, D4, E4, F4, G4, H4, \
A5, B5, C5, D5, E5, F5, G5, H5, \
A6, B6, C6, D6, E6, F6, G6, H6, \
A7, B7, C7, D7, E7, F7, G7, H7, \
    = MAP.flatten()


class Config:
    # ===== Start of generated config =====
    MAP_HAS_MAP_STORY = False
    MAP_HAS_FLEET_STEP = False
    MAP_HAS_AMBUSH = False
    STAR_REQUIRE_1 = 0
    STAR_REQUIRE_2 = 0
    STAR_REQUIRE_3 = 0
    # ===== End of generated config =====

    INTERNAL_LINES_HOUGHLINES_THRESHOLD = 40
    EDGE_LINES_HOUGHLINES_THRESHOLD = 40
    COINCIDENT_POINT_ENCOURAGE_DISTANCE = 1.5
    INTERNAL_LINES_FIND_PEAKS_PARAMETERS = {
        'height': (80, 255 - 24),
        'width': (0.9, 10),
        'prominence': 10,
        'distance': 35,
    }
    EDGE_LINES_FIND_PEAKS_PARAMETERS = {
        'height': (255 - 24, 255),
        'prominence': 10,
        'distance': 50,
        'width': (0, 10),
        'wlen': 1000,
    }


class Campaign(CampaignBase):
    MAP = MAP

    def battle_0(self):
        if self.fleet_2_push_forward():
            return True

        if self.clear_enemy(scale=(2, 3), genre=['light', 'carrier', 'enemy', 'main']):
            return True

        return self.battle_default()

    def battle_4(self):
        self.fleet_boss.clear_boss()
