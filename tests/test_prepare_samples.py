"""Invented records only: these tests contain no supplied coursework data."""
import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from prepare_samples import month_bounds, station_means


class PreparationTests(unittest.TestCase):
    def test_month_edges_and_time_of_day(self):
        records = [
            ('2014-05-31', (1, 2), 1),
            (datetime(2014, 6, 1, 0, 0), (1, 2), 4),
            (datetime(2014, 6, 30, 23, 59), (1, 2), 8),
            ('2014-07-01', (1, 2), 20),
        ]
        count, means = station_means(records)
        self.assertEqual(count, 2)
        self.assertEqual(means, {(1.0, 2.0): (6.0, 2)})

    def test_repeated_locations_receive_one_mean(self):
        records = [('2014/06/03', (1, 2), 2), ('2014-06-20', (1, 2), 6),
                   ('2014-06-20', (3, 4), 9)]
        count, means = station_means(records)
        self.assertEqual((count, len(means)), (3, 2))
        self.assertEqual(means[(1, 2)], (4, 2))

    def test_bad_dates_and_nonfinite_or_negative_values_are_excluded(self):
        records = [(d, xy, v) for d, xy, v in [
            ('bad date', (1, 2), 5), ('2014-06-05', (1, 2), None),
            ('2014-06-05', (1, 2), float('nan')),
            ('2014-06-05', (1, 2), float('inf')),
            ('2014-06-05', (float('nan'), 2), 5),
            ('2014-06-05', None, 5), ('2014-06-05', (1, 2), -1),
            ('2014-06-05', (1, 2), 0),
        ]]
        self.assertEqual(station_means(records), (1, {(1.0, 2.0): (0.0, 1)}))

    def test_close_but_unequal_coordinates_are_not_merged(self):
        records = [('2014-06-05', (1, 2), 4),
                   ('2014-06-05', (1.000001, 2), 6)]
        self.assertEqual(len(station_means(records)[1]), 2)

    def test_other_year_is_not_included(self):
        self.assertEqual(station_means([('2015-06-01', (1, 2), 5)]), (0, {}))

    def test_december_rollover(self):
        self.assertEqual(tuple(map(str, month_bounds(2014, 12))),
                         ('2014-12-01', '2015-01-01'))

    def test_invalid_month_fails(self):
        with self.assertRaises(ValueError):
            month_bounds(2014, 13)


if __name__ == '__main__':
    unittest.main()
