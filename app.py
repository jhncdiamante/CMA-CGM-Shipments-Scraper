from Application.Website.CMA import CMA
from datetime import datetime
import pandas as pd

cma = CMA("https://www.cma-cgm.com/ebusiness/tracking/search")
cma.start(["SGN2621243"])