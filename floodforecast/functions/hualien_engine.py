from hms.model import Project
from hms import Hms

myProject = Project.open(
    r"C:\Users\User\Documents\FloodForecastSystem\model\HMS\Hualien\2021.03.17_HLBridge\HLBridge_20210317.hms")
myProject.computeRun('Current')
myProject.close()

Hms.shutdownEngine()