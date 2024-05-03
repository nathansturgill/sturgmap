import folium
from ipyleaflet import basemaps
from folium import Map, Marker, TileLayer
from folium.plugins import DualMap
import rasterio
from rasterio.io import MemoryFile
import folium.plugins
from folium.plugins import SideBySideLayers
from folium import raster_layers
import shapefile
import geopandas as gpd
import json
from folium import Element



class Map(folium.Map):

    def __init__(self, center=[20, 0], zoom=2, left_layer=None, right_layer=None, **kwargs):
        super().__init__(location=center, zoom_start=zoom, **kwargs)
        self.left_layers = left_layer or []
        self.right_layers = right_layer or []
        self.basemaps = basemaps 
        self.current_basemap = self.basemaps["OpenStreetMap"]
        self.side_by_side_layers = []
        self.click_coordinates = []
        
        self.add_child(folium.Element(
            """
            <script>
            var map = document.querySelector('.folium-map');

            map.addEventListener('click', function(e) {
                var latitude = e.latlng.lat;
                var longitude = e.latlng.lng;
                var marker = L.marker([latitude, longitude])
                    .addTo(map)
                    .bindTooltip('Lat: ' + latitude + ', Lon: ' + longitude)
                    .openTooltip();
            });
            </script>
            """
        ))
    
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
    
    #def raster_split_map(self, layer_left_url, layer_right_url, left_name, right_name):
        """
        Create a split map with layers on left and right sides.

        Returns:
            None
        """
        
        
        #bbox = cog_bounds(left_layer)
        #bounds = [(bbox[1], bbox[0]), (bbox[3], bbox[2])]
        left_url = cog_tile(layer_left_url, **left_args)
        bbox = cog_bounds(layer_left_url)
        bounds = [(bbox[1], bbox[0]), (bbox[3], bbox[2])]
        layer_left = folium.raster_layers.TileLayer(
                        tiles=left_url,
                        name=left_name,
                        attr=" ",
                        overlay=True,
        )
        right_url = cog_tile(layer_left_url, **left_args)
        bbox = cog_bounds(layer_left_url)
        bounds = [(bbox[1], bbox[0]), (bbox[3], bbox[2])]
        layer_right = folium.raster_layers.TileLayer(
                        tiles=right_url,
                        name=right_name,
                        attr=" ",
                        overlay=True,
        )

        sbs = folium.plugins.SideBySideLayers(layer_left=layer_left, layer_right=layer_right)
        # Add left and right layers to the DualMap
        layer_left.add_to(self)
        layer_right.add_to(self)

        # Add the DualMap to the main map
        sbs.add_to(self)

        if bounds is not None:
            self.fit_bounds(bounds)

#        left_pane = folium.map.FeatureGroup(name='Left Pane', overlay=True)
#        for layer in self.left_layers:
#            if isinstance(layer, str): 
#                self.add_raster(layer, name="Left Raster", group="Left Pane")
#            else:  
#                layer.add_to(left_pane)
       
#        right_pane = folium.map.FeatureGroup(name='Right Pane', overlay=True)
#        for layer in self.right_layers:
#            if isinstance(layer, str):
#                self.add_raster(layer, name="Right Raster", group="Right Pane")
#            else:
#                layer.add_to(right_pane)

        
#        self.add_child(left_pane)
#        self.add_child(right_pane)

    
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
        #sbs = folium.plugins.SideBySideLayers(location=self.location, control_scale=True)
        sbs = folium.plugins.SideBySideLayers(layer_left=layer_left, layer_right=layer_right)

        # Add left and right layers to the DualMap
        layer_left.add_to(self)
        layer_right.add_to(self)

        # Add the DualMap to the main map
        sbs.add_to(self)

        # Append the DualMap to the list of side-by-side layers
        #self.side_by_side_layers.append(sbs)
    
    def add_geojson(self, data, name="geojson", **kwargs):
        """Adds a GeoJSON layer to the map.

        Args:
            data (str | dict): The GeoJSON data as a string or a dictionary.
            name (str, optional): The name of the layer. Defaults to "geojson".
        """
        if isinstance(data, str):
            with open(data) as f:
                data = json.load(f)

        folium.GeoJson(data, name=name, **kwargs).add_to(self)


    def add_shp(self, data, name="shp", **kwargs):
        """
        Adds a shapefile to the current map.

        Args:
            data (str or dict): The path to the shapefile as a string, or a dictionary representing the shapefile.
            name (str, optional): The name of the layer. Defaults to "shp".
            **kwargs: Arbitrary keyword arguments.
        """
        if isinstance(data, str):
            data = gpd.read_file(data).to_json()

        self.add_geojson(data, name, **kwargs)

    def add_markers(self):
        """
        Adds markers to the map and returns a list of clicked coordinates.

        Returns:
        list: A list of tuples containing the clicked latitude and longitude coordinates.
        """
        def on_click(event, **kwargs):
            """
        Event handler for when a user clicks on the map.
        Adds a marker to the clicked position and appends its coordinates to the list.
        """
        lat, lon = event['coordinates']
        self.click_coordinates.append((lat, lon))
        marker = Marker([lat, lon], tooltip=f'Lat: {lat}, Lon: {lon}')
        marker.add_to(self)

        self.on_click(on_click)

