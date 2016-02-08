# -*- coding: utf-8 -*-

__author__ = 'PlanetaryPy Developers'
__email__ = 'contact@planetarypy.com'
__version__ = '0.1.0'


import logging


logger = logging.getLogger('ptu')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s:%(name)s:-%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
