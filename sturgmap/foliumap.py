import folium

class Map(folium.Map):
    def _init_(self,center=[20,0], zoom=2, **kwargs):
        super().__init__(location=center, zoom_start=zoom, **kwargs)

    def add_raster(self, data, name="raster", zoom_to_layer=True, **kwargs):
        """Adds a raster to the map and allows the user to input whichever raster 
        they choose to analyze.

        Args:
            data (_type_): _description_
            name (str, optional): _description_. Defaults to "raster".
            zoom_to_layer (bool, optional): _description_. Defaults to True.

        Raises:
            ImportError: _description_
        """


        try:
            from localtileserver import TileClient, get_folium_tile_layer
        except ImportError:
            raise ImportError("Please install the localtileserver package.")

        client = TileClient(data)
        layer = get_folium_tile_layer(client, name=name, **kwargs)
        layer.add_to(self)
        

        if zoom_to_layer:
            self.center = client.center()
            self.zoom = client.default_zoom
