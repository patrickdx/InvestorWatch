__version__ = "1.0.1"
__author__ = "Patrick"

from investor_watch.Driver import Driver

# Create a single instance of the database driver
db = Driver()

# Register cleanup on program exit
import atexit
atexit.register(db.close)

