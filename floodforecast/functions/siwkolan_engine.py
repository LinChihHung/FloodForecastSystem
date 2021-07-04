from hms.model import Project
from hms import Hms

myProject = Project.open(
    r"C:\Users\User\Desktop\HualienRiver_HMS_0917\HualienRiver_0917.hms")
myProject.computeRun('Current')
myProject.close()

Hms.shutdownEngine()