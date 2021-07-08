from hms.model import Project
from hms import Hms

myProject = Project.open(
    r"C:\Users\User\Documents\FloodForecastSystem\model\HMS\Siwkolan\2021.04.05_Siwkolan\Siwkolan_20210405.hms")
myProject.computeRun('Current')
myProject.close()

Hms.shutdownEngine()