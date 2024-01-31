import unittest
import os


suite = unittest.TestLoader().discover(
    start_dir=os.path.dirname(__file__),
    top_level_dir=os.path.join(os.path.dirname(__file__), "../"),
    pattern="*Test.py"
)
unittest.TextTestRunner(verbosity=2).run(suite)
