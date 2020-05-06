import sys
import math
sys.path.append('/VL/space/zhan1624/Matterport3DSimulator/build')
import MatterSim
sim = MatterSim.Simulator()
sim.setNavGraphPath('/VL/space/zhan1624/Matterport3DSimulator/connectivity1')
sim.setDatasetPath('/VL/space/zhan1624/room2room')
sim.setCameraResolution(640, 480)
sim.setCameraVFOV(math.radians(60))
sim.setPreloadingEnabled(True)
sim.setDepthEnabled(True)

sim.initialize()
sim.newEpisode(['17DRP5sb8fy'], ['da5fa65c13e643719a20cbb818c9a85d'], [2.0943951023931953], [0])


import numpy as np
import matplotlib.pyplot as plt

print(sim.getState()[0].scanId)
img = np.array(sim.getState()[0].rgb)
#plt.figure(figsize = (12,10))
plt.imshow(img, aspect='auto')
plt.axis("off")
plt.xticks([])
plt.yticks([])
plt.savefig('/VL/space/zhan1624/Matterport3DSimulator/generated_images/3399_06.png',bbox_inches='tight',pad_inches=0.0)

