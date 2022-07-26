from unittest import TestCase
import bank_of_israel_rates


class SingleRateTests(TestCase):
    def setUp(self) -> None:
        self._2021_12_10 = bank_of_israel_rates.get_rate('USD', '2021-12-10')

    def test_2021_12_10(self):
        expected = {'last_update': '2021-12-10', 'name': 'Dollar', 'unit': 1,
                    'currency_code': 'USD', 'country': 'USA', 'rate': 3.103, 'change': -0.032}
        self.assertDictEqual(self._2021_12_10.as_dict(), expected)
        
    def test_fail(self):
        self.fail('meant to fail')
