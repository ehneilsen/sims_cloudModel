import os
import sqlite3
import unittest

from lsst.sims.cloudModel import CloudModel
from lsst.sims.cloudModel import TimeHandler

class TestCloudModel(unittest.TestCase):

    def setUp(self):
        self.th = TimeHandler("2020-01-01")
        self.cloud = CloudModel(self.th)
        self.num_original_values = 29200

    def test_basic_information_after_creation(self):
        self.assertIsNone(self.cloud.cloud_db)
        self.assertIsNone(self.cloud.cloud_dates)
        self.assertIsNone(self.cloud.cloud_values)
        self.assertEqual(self.cloud.offset, 0)

    def test_information_after_initialization(self):
        self.cloud.initialize()
        self.assertEqual(self.cloud.cloud_values.size, self.num_original_values)
        self.assertEqual(self.cloud.cloud_dates.size, self.num_original_values)

    def test_get_clouds(self):
        self.cloud.initialize()
        self.assertEqual(self.cloud.get_cloud(700000), 0.5)
        self.assertEqual(self.cloud.get_cloud(701500), 0.5)
        self.assertEqual(self.cloud.get_cloud(705000), 0.375)
        self.assertEqual(self.cloud.get_cloud(630684000), 0.0)

    def test_get_clouds_using_different_start_month(self):
        cloud1 = CloudModel(TimeHandler("2020-05-24"))
        self.assertEqual(cloud1.offset, 12441600)
        cloud1.initialize()
        self.assertEqual(cloud1.get_cloud(700000), 0.0)
        self.assertEqual(cloud1.get_cloud(701500), 0.0)
        self.assertEqual(cloud1.get_cloud(705000), 0.0)
        self.assertEqual(cloud1.get_cloud(630684000), 0.25)

    def test_alternate_db(self):
        cloud_dbfile = "alternate_cloud.db"

        cloud_table = []
        cloud_table.append("cloudId INTEGER PRIMARY KEY")
        cloud_table.append("c_date INTEGER")
        cloud_table.append("cloud DOUBLE")

        with sqlite3.connect(cloud_dbfile) as conn:
            cur = conn.cursor()
            cur.execute("DROP TABLE IF EXISTS Cloud")
            cur.execute("CREATE TABLE Cloud({})".format(",".join(cloud_table)))
            cur.executemany("INSERT INTO Cloud VALUES(?, ?, ?)", [(1, 9997, 0.5), (2, 10342, 0.125)])
            cur.close()

        self.cloud.initialize(cloud_dbfile)
        self.assertEqual(self.cloud.cloud_values.size, 2)
        self.assertEqual(self.cloud.cloud_values[1], 0.125)

        os.remove(cloud_dbfile)