# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 17:05:25 2021

@author: islam

Merge short sections with upstream or downstream sections if they are not 
connected to any other section
"""
max_no_to_process = None
len_threshold = 15

def delete_obj(model, obj):
    cmd = obj.getDelCmd()
    model.getCommander().addCommand(cmd)

deleted_sections_count = 0
section_type = model.getType("GKSection") 
for section_id in model.getCatalog().getObjectsByType(section_type):
    if max_no_to_process is not None and \
        deleted_sections_count >= max_no_to_process:
        break
    section = model.getCatalog().find(section_id)
    if section is None or section.length2D() > len_threshold:
        continue
    up_sections = section.getEntranceSections()
    down_sections = section.getExitSections()
    node = None
    # determine which sections to merge
    if section.getNumEntranceSections() == 1 and \
        section.getNumExitSections() == 1:
        if up_sections[0].length2D() > down_sections[0].length2D() and \
            up_sections[0].getNumExitSections() == 1:
            #merge with upstream section
            sections_to_merge = up_sections + [section]
            section_to_keep = up_sections[0]
            node = section.getOrigin()
        elif down_sections[0].getNumEntranceSections() == 1:
            #merge with downstream section
            sections_to_merge = [section] + down_sections
            section_to_keep = section
            node = section.getDestination()
    elif section.getNumEntranceSections() == 1 and \
        up_sections[0].getNumExitSections() == 1:
        #merge with upstream section
        sections_to_merge = up_sections + [section]
        section_to_keep = up_sections[0]
        node = section.getOrigin()
    elif section.getNumExitSections() == 1 and \
        down_sections[0].getNumEntranceSections() == 1:
        #merge with downstream section
        sections_to_merge = [section] + down_sections
        section_to_keep = section
        node = section.getDestination()
    # cannot merge sections with different number of lanes
    if sections_to_merge[0].getExitLanes()[-1] != \
        sections_to_merge[1].getEntryLanes()[-1]:
            continue
    # merging sections if one of the above tests passed
    if node is not None:
        # delete the turn between the two sections that will be merged
        turn = node.getTurning(sections_to_merge[0], sections_to_merge[1])
        if turn is not None:
            node.removeTurning(turn)
            delete_obj(model, turn)
        # join the two sections
        cmd = GKSectionJoinCmd()
        cmd.setSelection(section_to_keep, sections_to_merge)
        model.getCommander().addCommand(cmd)
        # clear selection
        active_gui = GKGUISystem.getGUISystem().getActiveGui()
        selection = model.getGeoModel().getSelection()
        selection.clear()
        active_gui.invalidateViews()
        # increment counters
        deleted_sections_count += 1
        if deleted_sections_count % 100 == 0:
            print("Processed {} short sections".format(deleted_sections_count))
print("Removed {} short sections".format(deleted_sections_count))
print("Done!")