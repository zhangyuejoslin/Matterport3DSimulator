import sys
import os
import math
import json
import numpy as np
import matplotlib.pyplot as plt

sys.path.append('/VL/space/zhan1624/Matterport3DSimulator/build')
import MatterSim

sim1 = MatterSim.Simulator()
sim1.setNavGraphPath('/VL/space/zhan1624/Matterport3DSimulator/connectivity')
sim1.setDatasetPath('/VL/space/zhan1624/room2room')
sim1.setCameraResolution(640, 480)
sim1.setCameraVFOV(math.radians(60))
sim1.setPreloadingEnabled(True)
sim1.setDepthEnabled(True)

sim2 = MatterSim.Simulator()
sim2.setNavGraphPath('/VL/space/zhan1624/Matterport3DSimulator/connectivity')
sim2.setDatasetPath('/VL/space/zhan1624/room2room')
sim2.setCameraResolution(640, 480)
sim2.setCameraVFOV(math.radians(60))
sim1.setPreloadingEnabled(True)
sim2.setDepthEnabled(True)

sim1.initialize()
all_scenery_data = []

def get_exclude_state(scan_id, states):
    """
    To get exclude image_id of each sceneray
    scan_id: "17DRP5sb8fy"
    states: "image_id"
    return: [exlude image_id]
    """
    exclude_list = []
    for each_state in states:
        try: 
            sim1.newEpisode([scan_id], [each_state], [0], [0])
        except ValueError:
            exclude_list.append(each_state)
    return exclude_list

def remove_exclude_state(exclude_state_id, state_dict):
    """
    To delete exclude image_id of each sceneray
    exclude_state_id: [image_id get from get_exclude_state]
    state_dict: {reading connectivity}
    return: [new state list without exclude image_id dict]
    """
    new_state_dict = []
    for each_state in state_dict:
        if each_state['image_id'] not in exclude_state_id:
            new_state_dict.append(each_state['image_id'])
    return new_state_dict

def sceneraty_combine(sceneray_id, states, heading_list, elevation):
    sceneraty_combine = []
    for state in states:
        for heading in heading_list:
            sceneraty_combine.append((sceneray_id, state, heading, elevation))
    return sceneraty_combine

def get_images(sceneray_id, states, heading_list, elevation): 
    sim2.setBatchSize(len(states)) 
    sim2.setCacheSize(len(states)*2)
    sim2.initialize()
    sim2.newEpisode(sceneray_id, states, heading_list, elevation)
    print('Finishing Simulation')
    for id, sim_state in enumerate(sim2.getState()):
        path = 'image_object/generated_images/'+ sim_state.scanId + "/" + sim_state.location.viewpointId
        if not os.path.exists(path):
            os.makedirs(path)
        img = np.array(sim_state.rgb)
        plt.figure(figsize = (12,10))
        plt.imshow(img, aspect='auto')
        plt.axis("off")
        plt.xticks([])
        plt.yticks([])
        plt.savefig(path + "/" + sim_state.location.viewpointId+
             "_"+str(sim_state.heading)+".jpg",bbox_inches='tight',pad_inches=0.0)
        plt.close()
        print("picture" + str(id))
     
        
def get_panomic_heading(start_heading):
    new_headings = []
    new_headings.append(round(start_heading,3))
    num = 0
    while num < 11:
        start_heading += math.pi/6
        if start_heading >= 2 * math.pi:
            start_heading = start_heading - 2 * math.pi
        new_headings.append(round(start_heading, 3))
        num+=1
    return new_headings
  
if __name__ == "__main__":
    allnames  = os.listdir('connectivity')
    all_scenery = [name.split('_')[0] for name in allnames if '_' in name]
 
    # heading list
    with open('tasks/R2R/data/R2R_train.json') as f_train, open('tasks/R2R/data/R2R_val_seen.json') as f_val_seen, open('tasks/R2R/data/R2R_val_unseen.json') as f_val_unseen:
        train_data = json.load(f_train)
        val_seen = json.load(f_val_seen)
        val_unseen = json.load(f_val_unseen)
    all_data = train_data + val_seen + val_unseen
    heading_dict = {}
    print('Starting Getting Heading')
    for data in all_data:
        if data['scan'] not in heading_dict.keys():
            heading_dict[data['scan']] = []
            new_headings = get_panomic_heading(data['heading'])
            heading_dict[data['scan']] += new_headings
        else:
            new_headings = get_panomic_heading(data['heading'])
            if data['heading'] not in heading_dict[data['scan']]:
                new_headings = get_panomic_heading(data['heading'])
                heading_dict[data['scan']] += new_headings

    for scenery_id in all_scenery:
        states = []
        #get states
        with open("connectivity/" + scenery_id + "_connectivity.json") as f_con:
            connectivity = json.load(f_con)
        for state in connectivity:
            states.append(state['image_id'])     
        #get elevation
        elevation = 0
        exclude_state_id = get_exclude_state(scenery_id, states)
        new_states = remove_exclude_state(exclude_state_id, connectivity)
        if heading_dict.get(scenery_id):
            all_scenery_data += sceneraty_combine(scenery_id, new_states, heading_dict[scenery_id], elevation)
        else:
            continue
        print('Finishing Getting '+scenery_id+" data")
        break

    print('Total ' + str(len(all_scenery_data)))
    all_scenery_id = list(list(zip(*all_scenery_data))[0])
    all_states = list(list(zip(*all_scenery_data))[1])
    all_heading = list(list(zip(*all_scenery_data))[2])
    all_elevation = list(list(zip(*all_scenery_data))[3])
    get_images(all_scenery_id, all_states, all_heading, all_elevation)