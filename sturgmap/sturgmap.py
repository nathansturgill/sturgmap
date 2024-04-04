"""Main module."""

import ipyleaflet
from ipyleaflet import basemaps
import geopandas as gpd

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