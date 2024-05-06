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
import matplotlib.pyplot as plt


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
      
        sbs = folium.plugins.SideBySideLayers(layer_left=layer_left, layer_right=layer_right)

        
        layer_left.add_to(self)
        layer_right.add_to(self)

        
        sbs.add_to(self)

        
    
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

    def display_raster_histogram(self, raster):
        """
        Display histogram of pixel values in the raster.

        Args:
            raster (rasterio.DatasetReader): The raster dataset.
        """
        data = raster.read(1)
        plt.hist(data.flatten(), bins=50, color='b', alpha=0.7)
        plt.xlabel('Pixel Value')
        plt.ylabel('Frequency')
        plt.title('Raster Histogram')
        plt.show()

    def calculate_statistics(self, raster):
        """
        Calculate basic statistics of the raster.

        Args:
            raster (rasterio.DatasetReader): The raster dataset.
        """
        data = raster.read(1)
        print(f"Minimum: {data.min()}")
        print(f"Maximum: {data.max()}")
        print(f"Mean: {data.mean()}")
        print(f"Standard Deviation: {data.std()}")

    def crop_raster(self, raster, bounds):
        """
        Crop the raster to the specified extent.

        Args:
            raster (rasterio.DatasetReader): The raster dataset.
            bounds (tuple): The bounding box to crop to in the format (minx, miny, maxx, maxy).
        """
        crop_window = rasterio.windows.from_bounds(*bounds, transform=raster.transform)

        cropped_data = raster.read(window=crop_window)
        cropped_transform = raster.window_transform(crop_window)

        new_meta = raster.meta.copy()
        new_meta.update({
            'height': crop_window.height,
            'width': crop_window.width,
            'transform': cropped_transform
        })

        return cropped_data, new_meta

    def resample_raster(self, raster, scale_factor):
        """
        Resample the raster to a different spatial resolution.

        Args:
            raster (rasterio.DatasetReader): The raster dataset.
            scale_factor (float): The scaling factor for resampling.
        """
        data = raster.read(
            out_shape=(
                raster.count,
                int(raster.height * scale_factor),
                int(raster.width * scale_factor)
            ),
            resampling=rasterio.enums.Resampling.bilinear
        )

        new_meta = raster.meta.copy()
        new_meta.update({
            'height': int(raster.height * scale_factor),
            'width': int(raster.width * scale_factor),
            'transform': raster.transform * raster.transform.scale(
                (raster.width / data.shape[-1]),
                (raster.height / data.shape[-2])
            )
        })

        return data, new_meta

    def compute_ndvi(self, nir_band, red_band):
        """
        Compute Normalized Difference Vegetation Index (NDVI) from near-infrared and red bands.

        Args:
            nir_band (rasterio.DatasetReader): The near-infrared band raster dataset.
            red_band (rasterio.DatasetReader): The red band raster dataset.
        """
        nir_data = nir_band.read(1).astype(float)
        red_data = red_band.read(1).astype(float)

        ndvi = (nir_data - red_data) / (nir_data + red_data)

        return ndvi

    def display_raster_folium(self, raster):
        """
        Display raster data on a Folium map.

        Args:
            raster (numpy.ndarray): The raster data.
        """
        m = folium.Map(location=[0, 0], zoom_start=2)

        # Convert raster to image overlay
        img = folium.raster_layers.ImageOverlay(
            raster,
            bounds=[[raster.min(), raster.min()], [raster.max(), raster.max()]],
            opacity=0.6,
            name="Raster Image"
        )
