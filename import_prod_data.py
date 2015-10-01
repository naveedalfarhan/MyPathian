__author__ = 'Brad'

from db.uow import UoW
import rethinkdb

class ProdDataImporter:
    def __init__(self):

        self.prod_db = rethinkdb.connect("localhost", 28016)
        self.local_db = rethinkdb.connect("localhost", 28015)

        self.prod_uow = UoW(self.prod_db)
        self.local_uow = UoW(self.local_db)

    def import_components(self):
        components = self.prod_uow.components.get_all()

        self.local_uow.components.insert_bulk(components)

    def import_component_points(self):
        component_points = self.prod_uow.component_points.get_all()

        self.local_uow.component_points.insert_bulk(component_points)

    def import_sic_codes(self):
        sic_codes = self.prod_uow.sic.get_all()

        self.local_uow.sic.insert_batch(sic_codes)

    def import_naics_codes(self):
        naics_codes = self.prod_uow.naics.get_all()

        self.local_uow.naics.insert_batch(naics_codes)

    def import_weather_stations(self):
        weather_stations = self.prod_uow.weather_stations.get_all_list()

        self.local_uow.weather_stations.insert_many(weather_stations)

    def import_groups(self):
        for index in range(0, 250):
            start_position = index * 500
            groups = self.prod_uow.groups.get_batch(500, start_position)

            if len(groups) > 0:
                print index
                self.local_uow.groups.insert_many(groups)
            else:
                print "done"
                return


importer = ProdDataImporter()

importer.import_sic_codes()
importer.import_naics_codes()
importer.import_weather_stations()
importer.import_groups()