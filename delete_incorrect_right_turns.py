# -*- coding: utf-8 -*-
"""
Created on Wed May  5 16:29:51 2021

@author: islam

Delete right turns in signalized intersections if there is a right-turn bay

  |
  |
--N--D--N_d
  |    /
  |   /
  U  S
  | /
  |/
  N_u

for all entering sections U to node N: (where N is any signalized intersection)
    check if U's origin node N_u has another exit section S that is connected 
    to one of N's destination nodes N_d

N: <node>    
U: <section>
N_d: its Id is the key in <node_destinations>
D: corresponding value in <node_destinations>
S: <section2>


if delete_uturns is True, this script will delete u-turns at the beginning and 
end of the RT bay
"""
#2455565, 1521115, 1398519
RTURN_THRESHOLD = -120

delete_uturns = True

def del_obj(object):
    # deletes the given object from the model
    cmd = object.getDelCmd()
    return model.getCommander().addCommand(cmd)

def is_right_turn(turn):
    if turn is None:
        return False
    turn_angle = turn.calcAngleSections()
    return ((turn_angle > RTURN_THRESHOLD) and (turn_angle < 0))

node_type = model.getType('GKNode')
signal_attr = node_type.getColumn('GKNode::signalized', 
                                 GKType.eSearchOnlyThisType)
counter = 0
for node_id in model.getCatalog().getObjectsByType(node_type): #[2455565]:#
    node = model.getCatalog().find(node_id)
    if node is not None and \
        node.getDataValueInt(signal_attr) != 0 and \
        node.getNumEntranceSections() > 2:
        node_destinations = {x.getDestination().getId():x \
                             for x in node.getExitSections() \
                             if x.getDestination() is not None}
        for section in node.getEntranceSections():
            if section.getOrigin() is None:
                print("Section {0} has no origin".format(section.getId()))
                continue
            for section2 in section.getOrigin().getExitSections():
                if section2.getDestination() is None:
                    print("Section {0} has no destination".format(
                        section2.getId()))
                    continue
                section2_destination_id = section2.getDestination().getId()
                if section2_destination_id in node_destinations.keys():
                    turn = node.getTurning(section, 
                        node_destinations[section2_destination_id])
                    # make sure its a right turn
                    if is_right_turn(turn):
                        counter += 1
                        node.removeTurning(turn)
                        del_obj(turn)
                        if delete_uturns:
                            # delete all turns at the end of the RT bay section
                            # other than the correct right turn, e.g. U-turns
                            down_node = section2.getDestination()
                            for i in down_node.getFromTurningsOrderedFromRightToLeft(
                                    section2)[1:]:
                                down_node.removeTurning(i)
                                del_obj(i)
                            # delete all turns at the beginning of the RT bay 
                            # section other than the correct right turn, e.g. 
                            # U-turns
                            up_node = section2.getOrigin()
                            for i in up_node.getToTurningsOrderedFromRightToLeft(
                                    section2)[1:]:
                                up_node.removeTurning(i)
                                del_obj(i)
                    else:
                        print("Check node {0}".format(node.getId()))
                    break
                    
print("Fixed {0} turnings".format(counter))
print("Done!")