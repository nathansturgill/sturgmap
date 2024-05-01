"""Main module."""

import ipyleaflet
from ipyleaflet import Map, basemaps, TileLayer, basemap_to_tiles, SplitMapControl
from ipyleaflet import WidgetControl
import ipywidgets as widgets
import os



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
        self.split_control=None

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

    def add_layers_control(self, position="topright"):
        """Adds a layers control to the map.

        Args:
            position (str, optional): The position of the layers control. Defaults to "topright".
        """
        self.add_control(ipyleaflet.LayersControl(position=position))

    def add_zoom_slider(
        self, description="Zoom level", min=0, max=24, value=10, position="topright"
    ):
        """Adds a zoom slider to the map.

        Args:
            position (str, optional): The position of the zoom slider. Defaults to "topright".
        """
        zoom_slider = widgets.IntSlider(
            description=description, min=min, max=max, value=value
        )

        control = ipyleaflet.WidgetControl(widget=zoom_slider, position=position)
        self.add(control)
        widgets.jslink((zoom_slider, "value"), (self, "zoom"))

    def add_widget(self, widget, position="topright"):
        """Adds a widget to the map.

        Args:
            widget (object): The widget to be added.
            position (str, optional): The position of the widget. Defaults to "topright".
        """
        control = ipyleaflet.WidgetControl(widget=widget, position=position)
        self.add(control)

    def add_opacity_slider(
        self, layer_index=-1, description="Opacity", position="topright"
    ):
        """Adds an opacity slider to the map.

        Args:
            layer (object): The layer to which the opacity slider is added.
            description (str, optional): The description of the opacity slider. Defaults to "Opacity".
            position (str, optional): The position of the opacity slider. Defaults to "topright".
        """
        layer = self.layers[layer_index]
        opacity_slider = widgets.FloatSlider(
            description=description,
            min=0,
            max=1,
            value=layer.opacity,
            style={"description_width": "initial"},
        )
    
    def add_basemap_gui(self, basemaps=None, position="topright"):
        """Adds a basemap GUI to the map.

        Args:
            position (str, optional): The position of the basemap GUI. Defaults to "topright".
        """

        basemap_selector = widgets.Dropdown(
            options=[
                "OpenStreetMap",
                "OpenTopoMap",
                "Esri.WorldImagery",
                "Esri.NatGeoWorldMap",
            ],
            description="Basemap",
        )

        def update_basemap(change):
            """This allows users to add new basemaps based on the options given. Also allows for users to close basemap option.

            Args:
                change (_type_): _description_
            """
            self.add_basemap(change["new"])

        basemap_selector.observe(update_basemap, "value")

        close_button = widgets.Button(icon="times", layout=widgets.Layout(width="auto"), button_style="")

        
        def close_dropdown(_):
            """This adds functionality for the user to close the selected basemap after
        they choose one of the four options for their basemap.

            Args:
                _ (_type_): _description_
            """            
            self.remove_control(basemap_control)  

        close_button.on_click(close_dropdown)

        widget_box = widgets.VBox([basemap_selector, close_button])

        basemap_control = ipyleaflet.WidgetControl(widget=widget_box, position=position)

        self.add_control(basemap_control)

    def add_toolbar(self, position="topright"):
        """Adds a toolbar to the map.

        Args:
            position (str, optional): The position of the toolbar. Defaults to "topright".
        """

        padding = "0px 0px 0px 5px"

        toolbar_button = widgets.ToggleButton(
            value=False,
            tooltip="Toolbar",
            icon="wrench",
            layout=widgets.Layout(width="28px", height="28px", padding=padding),
        )

        close_button = widgets.ToggleButton(
            value=False,
            tooltip="Close the tool",
            icon="times",
            button_style="primary",
            layout=widgets.Layout(height="28px", width="28px", padding=padding),
        )

        toolbar = widgets.VBox([toolbar_button])

        def close_click(change):
            if change["new"]:
                toolbar_button.close()
                close_button.close()
                toolbar.close()

        close_button.observe(close_click, "value")

        rows = 2
        cols = 2
        grid = widgets.GridspecLayout(
            rows, cols, grid_gap="0px", layout=widgets.Layout(width="65px")
        )

        icons = ["folder-open", "map", "info", "question"]

        for i in range(rows):
            for j in range(cols):
                grid[i, j] = widgets.Button(
                    description="",
                    button_style="primary",
                    icon=icons[i * rows + j],
                    layout=widgets.Layout(width="28px", padding="0px"),
                )

        def toolbar_click(change):
            if change["new"]:
                toolbar.children = [widgets.HBox([close_button, toolbar_button]), grid]
            else:
                toolbar.children = [toolbar_button]

        toolbar_button.observe(toolbar_click, "value")
        toolbar_ctrl = WidgetControl(widget=toolbar, position="topright")
        self.add(toolbar_ctrl)

        output = widgets.Output()
        output_control = WidgetControl(widget=output, position="bottomright")
        self.add(output_control)

        def toolbar_callback(change):
            if change.icon == "folder-open":
                with output:
                    output.clear_output()
                    print(f"You can open a file")
            elif change.icon == "map":
                with output:
                    output.clear_output()
                    print(f"You can add a layer")
            else:
                with output:
                    output.clear_output()
                    print(f"Icon: {change.icon}")

        for tool in grid.children:
            tool.on_click(toolbar_callback)
    
    def split_map(self, left_layer, right_layer):
       """
       Creates a split-screen map with two layers side-by-side.


       Args:
           left_layer: The layer to be displayed on the left side of the map.
               This can be a string representing a basemap URL, a TileLayer instance,
               or any other layer object supported by ipyleaflet.
           right_layer: The layer to be displayed on the right side of the map.
               Same format as left_layer.
       """
       if self.split_control is not None:
           self.remove_control(self.split_control)


       if not isinstance(left_layer, ipyleaflet.Layer):
           self.add_tile_layer(left_layer, "Left Layer")
           left_layer = self.layers[-1] 


       if not isinstance(right_layer, ipyleaflet.Layer):
           self.add_tile_layer(right_layer, "Right Layer")
           right_layer = self.layers[-2] 

       split_map = ipyleaflet.SplitMapControl(left_layer=left_layer, right_layer=right_layer)
       self.split_control = split_map
       self.add_control(split_map)

    def add_scale_bar(self, position="bottomleft", **kwargs):
        """Adds a scale bar to the map.

        Args:
        position (str, optional): The position of the scale bar. Defaults to "bottomleft".
        **kwargs: Additional keyword arguments to pass to the ipyleaflet.ScaleControl constructor.
        """
        scale_control = ipyleaflet.ScaleControl(position=position, **kwargs)
        self.add_control(scale_control)


    def add_marker(self, location, popup_text=None, icon=None, **kwargs):
        """Adds a marker to the map.

        Args:
        location (list): The latitude and longitude coordinates of the marker.
        popup_text (str, optional): The text to be displayed in a popup when the marker is clicked. Defaults to None.
        icon (ipyleaflet.Icon, optional): A custom icon for the marker. Defaults to None.
        **kwargs: Additional keyword arguments to pass to the ipyleaflet.Marker constructor.
        """
        marker = ipyleaflet.Marker(location=location, popup=popup_text, icon=icon, **kwargs)
        self.add(marker)

    