import folium
from ipyleaflet import basemaps
from folium import Map, Marker, TileLayer
from folium.plugins import DualMap


class Map(folium.Map):

    def __init__(self, center=[20, 0], zoom=2, left_layer=None, right_layer=None, **kwargs):
        super().__init__(location=center, zoom_start=zoom, **kwargs)
        self.left_layers = left_layer or []
        self.right_layers = right_layer or []
        self.basemaps = basemaps or {
            "OpenStreetMap": folium.TileLayer(
                tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                name="OpenStreetMap"
            ),
            "ESRI.World_Imagery": folium.TileLayer(
                tiles="https://server.arcgiserver.com/ArcGIS/rest/services/World_Imagery/BaseMap/tile/{z}/{y}/{x}.jpg",
                name="ESRI.World_Imagery",
                attr="&copy; <a href='https://www.esri.com/'>Esri</a>, &copy; <a href='https://resources.arcgiserver.com/en-us/help/main/topics/web-services-and-api-terms-of-use.htm'>ArcGIS</a>"
            ),
            "USGS National Basemap": folium.TileLayer(
        tiles="https://basemap.nationalatlas.gov/arcgis/rest/services/National_Basemap/National_Basemap/tile/{z}/{y}/{x}.jpg",
        name="USGS National Basemap",
        attr="&copy; <a href='https://www.usgs.gov/'>U.S. Geological Survey</a>"
            ),
        }
        self.current_basemap = self.basemaps["OpenStreetMap"]  
    
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


    def raster_split_map(self, left_map_layer, right_map_layer):
        """
        Create a split map with different basemaps or raster files on left and right sides.

        Args:
            left_map_layer: Basemap or raster file for the left side of the split map.
            right_map_layer: Basemap or raster file for the right side of the split map.

        Returns:
            None
        """

        left_map = folium.Map(location=self.location)
        if isinstance(left_map_layer, str):  
            left_map.add_raster(left_map_layer)
        else: 
            left_map_layer.add_to(left_map)


        right_map = folium.Map(location=self.location)
        if isinstance(right_map_layer, str):  
            right_map.add_raster(right_map_layer)
        else:  
            right_map_layer.add_to(right_map)

        
        split_control = DualMap(left_map, right_map)
        self.add_child(split_control)

    def set_basemap(self, name):
        # Simplified basemap selection (doesn't use dropdown)
        if name in self.basemaps:
            self.current_basemap = self.basemaps[name]
            # Update map elements based on the new basemap (if applicable)
            print(f"Current basemap: {self.current_basemap.name}")
        else:
            print(f"Basemap '{name}' not found.")

    