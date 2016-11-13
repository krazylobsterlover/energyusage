import unittest
from energy.tariff import convert_wh_to_w


class TestEnergy(unittest.TestCase):
    """ Tests some functions outside the web app
    """

    def test_energy_to_power(self):
        """ Test wh to w conversion
        """
        self.assertEqual(convert_wh_to_w(Wh=5, hours=1), 5)
        self.assertEqual(convert_wh_to_w(Wh=2.5, hours=0.5), 5)


if __name__ == '__main__':
    unittest.main()
