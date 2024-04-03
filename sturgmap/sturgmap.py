"""Main module."""

import ipyleaflet
from ipyleaflet import basemaps

class Map(ipyleaflet.Map):
    """_summary_

    Args:
        ipyleaflet (_type_): _description_
    """
    def __init__(self, center=[20, 0], zoom=2, **kwargs):
        """_summary_

        Args:
            center (list, optional): _description_. Defaults to [20, 0].
            zoom (int, optional): _description_. Defaults to 2.
        """
        super().__init__(center=center, zoom=zoom, **kwargs)
        self.add_control(ipyleaflet.LayersControl())
    
    def add_tile_layer(self, url, name, **kwargs):
        layer= ipyleaflet.TileLayer(url=url, name=name, **kwargs)
        self.add(layer)

    def add_basemap(self, name):
        if isinstance(name, str):
            url = eval(f"basemaps.{name}").build_url()
            self.add_tile_layer(url, name)
        else:
            self.add_name()