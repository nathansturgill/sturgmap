import folium
from ipyleaflet import basemaps
from folium import Map, Marker, TileLayer
from folium.plugins import DualMap
import rasterio as rio
from rasterio.io import MemoryFile
import folium.plugins
from folium.plugins import SideBySideLayers


class Map(folium.Map):

    def __init__(self, center=[20, 0], zoom=2, left_layer=None, right_layer=None, **kwargs):
        super().__init__(location=center, zoom_start=zoom, **kwargs)
        self.left_layers = left_layer or []
        self.right_layers = right_layer or []
        self.basemaps = basemaps 
        self.current_basemap = self.basemaps["OpenStreetMap"]
        self.side_by_side_layers = []
    
    def add_tile_layer(self, url, name, attribution="Custom Tile", **kwargs):
        """
        Adds a tile layer to the current map.

        Args:
            url (str): The URL of the tile layer.
            name (str): The name of the layer.
            attribution (str, optional): The attribution text to be displayed for the layer. Defaults to "Custom Tile".
            **kwargs: Arbitrary keyword arguments for additional layer options.

        Returns:
            None
        """
        layer = folium.TileLayer(tiles=url, name=name, attr=attribution, **kwargs)
        layer.add_to(self)

    def add_basemap(self, name, overlay=True):
        """
        Adds a basemap to the current map.

        Args:
            name (str or object): The name of the basemap as a string, or an object representing the basemap.
            overlay (bool, optional): Whether the basemap is an overlay. Defaults to True.

        Raises:
            TypeError: If the name is neither a string nor an object representing a basemap.

        Returns:
            None
        """

        if isinstance(name, str):
            url = eval(f"basemaps.{name}").build_url()
            self.add_tile_layer(url, name, overlay=overlay)
        else:
            name.add_to(self)

    def to_streamlit(self, width=700, height=500):
        """
        Converts the map to a streamlit component.

        Args:
            width (int, optional): The width of the map. Defaults to 700.
            height (int, optional): The height of the map. Defaults to 500.

        Returns:
            object: The streamlit component representing the map.
        """

        from streamlit_folium import folium_static

        return folium_static(self, width=width, height=height)

    def add_layer_control(self):
        """
        Adds a layer control to the map.

        Returns:
            None
        """

        folium.LayerControl().add_to(self)
    
    def split_map(self):
        """
        Create a split map with layers on left and right sides.

        Returns:
            None
        """
        
        left_pane = folium.map.FeatureGroup(name='Left Pane', overlay=True)
        for layer in self.left_layers:
            if isinstance(layer, str): 
                self.add_raster(layer, name="Left Raster", group="Left Pane")
            else:  
                layer.add_to(left_pane)
       
        right_pane = folium.map.FeatureGroup(name='Right Pane', overlay=True)
        for layer in self.right_layers:
            if isinstance(layer, str):
                self.add_raster(layer, name="Right Raster", group="Right Pane")
            else:
                layer.add_to(right_pane)

        
        self.add_child(left_pane)
        self.add_child(right_pane)

    
        folium.map.LayerControl().add_to(self)

    def add_raster(self, data, name="raster", **kwargs):
        """Adds a raster layer to the map.

        Args:
            data (str): The path to the raster file.
            name (str, optional): The name of the layer. Defaults to "raster".
        """

        
        try:
            from localtileserver import TileClient, get_folium_tile_layer
        except ImportError:
            raise ImportError("Please install the localtileserver package.")

        client = TileClient(data)
        layer = get_folium_tile_layer(client, name=name, **kwargs)
        layer.add_to(self)

    def add_side_by_side_layers(self, layer_left, layer_right):
        sbs = folium.plugins.DualMap(location=self.location, control_scale=True)

        # Add left and right layers to the DualMap
        layer_left.add_to(sbs.m1)
        layer_right.add_to(sbs.m2)

        # Add the DualMap to the main map
        sbs.add_to(self)

        # Append the DualMap to the list of side-by-side layers
        self.side_by_side_layers.append(sbs)