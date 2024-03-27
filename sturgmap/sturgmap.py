"""Main module."""

import ipyleaflet

class Map(ipyleaflet.Map):

    def __init__(self, center=[20, 0], zoom=2, **kwargs):
        super().__init__(center=center, zoom=zoom, **kwargs)
        self.add_control(ipyleaflet.LayersControl())
    
    def add_tile_layer(self, url, name, **kwargs):
        layer= ipyleaflet.TileLayer(url=url, name=name, **kwargs)
        self.add(layer)