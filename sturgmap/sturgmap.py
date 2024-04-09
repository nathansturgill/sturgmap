"""Main module."""

import ipyleaflet
from ipyleaflet import basemaps
import pandas

class Map(ipyleaflet.Map):
    """Inherits ipyleaflet.Map map class

    Args:
        ipyleaflet (_type_): The ipyleaflet.map Class
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
        """Adds a basemap based on the basemap options provided from ipyleaflet.

        Args:
            name (_type_): _description_
        """
        if isinstance(name, str):
            url = eval(f"basemaps.{name}").build_url()
            self.add_tile_layer(url, name)
        else:
            self.add_name()

    def add_geojson(self, data, name="geojson", **kwargs):
        """_summary_

        Args:
            data (_type_): _description_
            name (str, optional): _description_. Defaults to "geojson".
        """
        import json

        if isinstance(data, str):
            with open(data) as f:
                data = json.load(f)

            if "style" not in kwargs:
                kwargs["style"] = {"color": "green", "weight": 1, "fillOpacity": 0}

            if "hover_style" not in kwargs:
                kwargs["hover_style"] = {"fillColor": "#00ff00", "fillOpacity": 0.5}

            layer = ipyleaflet.GeoJSON(data=data, name=name, **kwargs)
            self.add(layer)
    
    def add_shp(self, data, name="shp", **kwargs):
        """ Allows users to add shapefiles to the package and load them

        Args:
            data (_type_): _description_
            name (str, optional): _description_. Defaults to "shp".
        """
        import shapefile
        import json

        if isinstance(data, str):
            with shapefile.Reader(data) as shp:
                data = shp.__geo_interface__

        self.add_geojson(data, name, **kwargs)

    def add_vector(self, data, name="vector", **kwargs):
        """
    Adds a vector data layer to the map.

    Parameters:
        data (str or GeoDataFrame): The vector data to be added. It can be either a file path to a vector data file (GeoJSON, shapefile, etc.) or a GeoDataFrame object.
        name (str): The name of the vector data layer. Default is "vector".
        **kwargs: Additional keyword arguments to pass to the add_geojson() method.

    Raises:
        None

    Returns:
        None
    """
        if isinstance(data, str):
            try:
               
                vector_data = gpd.read_file(data)
            except Exception as e:
                print(f"Error reading vector data from file: {e}")
                return
        elif isinstance(data, gpd.GeoDataFrame):
           
            vector_data = data
        else:
            print("Unsupported vector data format.")
            return

        
        geojson_data = vector_data.__geo_interface__

      
        self.add_geojson(geojson_data, name, **kwargs)

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
            from localtileserver import TileClient, get_leaflet_tile_layer
        except ImportError:
            raise ImportError("Please install the localtileserver package.")

        client = TileClient(data)
        layer = get_leaflet_tile_layer(client, name=name, **kwargs)
        self.add(layer)

        if zoom_to_layer:
            self.center = client.center()
            self.zoom = client.default_zoom
    
    def add_image(self, url, bounds, name="image", **kwargs):
        """Adds an image to the map.

        Args:
            url (str): The URL of the image.
            bounds (list): The bounds of the image.
            name (str, optional): The name of the layer. Defaults to "image".
        """
        layer = ipyleaflet.ImageOverlay(url=url, bounds=bounds, name=name, **kwargs)
        self.add(layer)