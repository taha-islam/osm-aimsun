# -*- coding: utf-8 -*-
"""
Created on Wed May  5 15:53:49 2021

@author: islam

Delete all U-turns in the network if it is not the only turn of its origin or
destination sections. U-turns are identified as the turns with angle greater 
than <UTURN_THRESHOLD>
"""

UTURN_THRESHOLD = 135

def del_obj(object):
    # deletes the given object from the model
    cmd = object.getDelCmd()
    return model.getCommander().addCommand(cmd)

node_type = model.getType('GKNode')
deleted_turn_count = 0
for node_id in model.getCatalog().getObjectsByType(node_type):
    node = model.getCatalog().find(node_id)
    for turn in node.getTurnings():
        if abs(turn.calcAngleSections()) > UTURN_THRESHOLD and \
            turn.getOrigin().getNumExitSections() > 1 and \
            turn.getDestination().getNumEntranceSections() > 1:
            node.removeTurning(turn)
            del_obj(turn)
            deleted_turn_count += 1

print("Deleted {0} U-turns".format(deleted_turn_count))
print("Done!")