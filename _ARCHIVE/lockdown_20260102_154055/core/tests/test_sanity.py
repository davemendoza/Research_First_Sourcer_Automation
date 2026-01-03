import unittest, os
class Sanity(unittest.TestCase):
    def test_repo_exists(self):
        self.assertTrue(os.path.exists('core'))
if __name__ == '__main__':
    unittest.main()
