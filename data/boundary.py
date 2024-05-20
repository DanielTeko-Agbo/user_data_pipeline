import random
import numpy as np
import os
import time
import polars as pd
from shapely.geometry import Point, Polygon, GeometryCollection


class BoundaryInfo:
    file_path = os.path.join(os.path.dirname(__file__), "./gadm41_GHA_2.json")

    def __init__(self):
        self.result = self.read_file()

    def read_file(self):
        """Reads the file that contains the boundary information.

        Returns:
            dict: A dictionary of the boundary information.
        """
        with open(self.file_path, "r") as file:
            json = file.read()
        json = eval(json)
        return json

    def main_boundary_names(self) -> list:
        """Retrieves main boundaries or regions in Ghana.

        Returns:
            list: A list of all the regions in Ghana
        """
        return list(
            set(
                [feature["properties"]["NAME_1"] for feature in self.result["features"]]
            )
        )

    def sub_boundary_names(self, boundary) -> list:
        """Retrieve the sub-boundaries (districts/municipalities) in a specified region passed.

        Args:
            boundary (str): A region whose sub-boundaries will be retrieved. One of ['WesternNorth','Bono','Eastern','UpperWest','GreaterAccra','Northern','NorthEast','Western','Ashanti','Oti','BonoEast','Savannah','Volta','UpperEast','Ahafo','Central']

        Returns:
            list: A list of all sub-boundaries.
        """
        boundaries = [
            feature["properties"]["NAME_2"]
            for feature in self.result["features"]
            if feature["properties"]["NAME_1"] == boundary.strip()
        ]
        return boundaries

    def data(self) -> dict:
        """Returns the boundary information read from the file.

        Returns:
            dict: All boundary information.
        """
        return self.result

    def random_main_boundary(self):
        return random.choice(self.main_boundary_names())

    def random_sub_boundary(self, boundary):
        subs = [
            feature["properties"]["NAME_2"]
            for feature in self.result["features"]
            if feature["properties"]["NAME_1"] == boundary.strip()
        ]
        return random.choice(subs)

    def main_boundary_coordinates(self, boundary, named: bool = False) -> list | dict:
        """Retrieve coordinates of all the suburbs or districts within the specified main boundary or region.

        Args:
            boundary (str): The region whose suburbs' coordinates are to be retrieved.
            named (bool, optional): Specify whether the boundary named should be passed as keys to the coordinates. Defaults to False.

        Returns:
            list | dict: Returns a list if the named is False, otherwise returns a dict.
        """
        if named:
            coords = {
                feature["properties"]["NAME_2"]: np.squeeze(
                    feature["geometry"]["coordinates"]
                ).tolist()
                for feature in self.result["features"]
                if feature["properties"]["NAME_1"] == boundary.strip()
            }
            return coords
        else:
            coords = [
                np.squeeze(feature["geometry"]["coordinates"]).tolist()
                for feature in self.result["features"]
                if feature["properties"]["NAME_1"] == boundary.strip()
            ]
            return coords

    def sub_boundary_coordinates(self, boundary, sub, named: bool = False) -> list | dict:
        """Retrieve the coordinates of a specifed suburb, district or subboundary.

        Args:
            boundary (str): The main boundary whose suburb is of interest.
            sub (str): The suburb within the main boundary whose coordinates are to be retrieved.
            named (bool, optional): Specify whether the boundary named should be passed as keys to the coordinates. Defaults to False.. Defaults to False.

        Returns:
            list | dict: Returns a list if the named is False, otherwise return a dict.
        """
        if named:
            coords = {
                sub: np.squeeze(feature["geometry"]["coordinates"]).tolist()
                for feature in self.result["features"]
                if feature["properties"]["NAME_1"] == boundary.strip()
                and feature["properties"]["NAME_2"] == sub
            }
            return coords
        else:
            coords = [
                feature["geometry"]["coordinates"]
                for feature in self.result["features"]
                if feature["properties"]["NAME_1"] == boundary.strip()
                and feature["properties"]["NAME_2"] == sub
            ]
            return np.squeeze(coords).tolist()


if __name__ == "__main__":
    # boundObj = BoundaryInfo()
    # sub = boundObj.random_sub_boundary("GreaterAccra")
    # coords = boundObj.sub_boundary_coordinates("GreaterAccra", sub, named=True)

    # print(coords)

    df = pd.DataFrame()
    now = time.time()

    while time.time() - now <= 300:
        boundObj = BoundaryInfo()

        sub = boundObj.random_sub_boundary("GreaterAccra")
        coords = boundObj.sub_boundary_coordinates("GreaterAccra", sub)
        c1, c2 = np.random.randint(1, len(coords), 2)

        polygon = Polygon(coords)
        x, y = coords[c1]
        x1, y1 = coords[c2]

        lat = np.random.uniform(x, x1)
        long = np.random.uniform(y, y1)
        point = Point([lat, long])

        if point.within(polygon):
            df1 = pd.DataFrame({"Suburb": sub, "Longitude": lat, "Latitude": long})

            df = pd.concat([df, df1])
    # GeometryCollection([polygon, point])
    df.write_csv("./coords.csv", separator=",")
    print(df.head())
