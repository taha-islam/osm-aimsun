# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 17:05:25 2021

@author: islam

Merge short sections with upstream or downstream sections if they are not 
connected to any other section
"""
max_no_to_process = None
len_threshold = 15
# Tuple of two lists of road types to consider and types to exclude
# An empty list would be ignored
road_type_ids = ([],[186, 192, 196])

def delete_obj(model, obj):
    cmd = obj.getDelCmd()
    model.getCommander().addCommand(cmd)

def have_same_no_lanes(up_section, down_section):
    """
    Return True if the two (ordered) sections up_section and down_section 
    have the same number of lanes

    Parameters
    ----------
    up_section : GKSection
        Upstream Section.
    down_section : GKSection
        Downstream section.

    Returns
    -------
    bool
        True only if the two sections have the same number of lanes.

    """
    return up_section.getExitLanes()[-1] == down_section.getEntryLanes()[-1]

def is_short_section(section):
    if section is None:
        return False
    result = (section.length2D() <= len_threshold)
    if len(road_type_ids[0]) > 0:
        result = result and (section.getRoadType().getId() in road_type_ids[0])
    if len(road_type_ids[1]) > 0:
        result = result and (section.getRoadType().getId() not in road_type_ids[1])
    return result
    
deleted_sections_count = 0
failed_to_delete_count = 0
section_type = model.getType("GKSection") 
for section_id in model.getCatalog().getObjectsByType(section_type):
    # Check maximum number of short sections to merge (delete)
    if max_no_to_process is not None and \
        deleted_sections_count >= max_no_to_process:
        break
    section = model.getCatalog().find(section_id)
    # Check section's length
    if not is_short_section(section):
        continue
    # Upstream and downstream sections of the short section
    up_sections = section.getEntranceSections()
    down_sections = section.getExitSections()
    # Node to be deleted
    node = None
    # determine which sections to merge
    if section.getNumEntranceSections() == 1 and \
        section.getNumExitSections() == 1:
        # One entering and one exiting sections
        if up_sections[0].getNumExitSections() == 1 and \
            have_same_no_lanes(up_sections[0], section):
            #merge with upstream section
            sections_to_merge = up_sections + [section]
            section_to_keep = up_sections[0]
            #section_to_keep = section
            node = section.getOrigin()
        elif down_sections[0].getNumEntranceSections() == 1 and \
            have_same_no_lanes(section, down_sections[0]):
            #merge with downstream section
            sections_to_merge = [section] + down_sections
            section_to_keep = section
            #section_to_keep = down_sections[0]
            node = section.getDestination()
        else:
            # Cannot delete this short section
            print("Cannot delete short section #{}".format(section_id))
            failed_to_delete_count += 1
            continue
    elif section.getNumEntranceSections() == 1 and \
        up_sections[0].getNumExitSections() == 1 and \
        have_same_no_lanes(up_sections[0], section):
        # One entering section that is connected only to the short section
        #merge with upstream section
        sections_to_merge = up_sections + [section]
        section_to_keep = up_sections[0]
        #section_to_keep = section
        node = section.getOrigin()
    elif section.getNumExitSections() == 1 and \
        down_sections[0].getNumEntranceSections() == 1 and \
            have_same_no_lanes(section, down_sections[0]):
        # One exiting section that is connected only to the short section
        #merge with downstream section
        sections_to_merge = [section] + down_sections
        section_to_keep = section
        #section_to_keep = down_sections[0]
        node = section.getDestination()
    else:
        # Cannot delete this short section
        print("Cannot delete short section #{}".format(section_id))
        failed_to_delete_count += 1
        continue
    # cannot merge sections with different number of lanes
    if sections_to_merge[0].getExitLanes()[-1] != \
        sections_to_merge[1].getEntryLanes()[-1]:
            print("Failed")
            failed_to_delete_count += 1
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
        #active_view = GKGUISystem.getGUISystem().getActiveGui().getActiveView()
        #active_view.selectAll()
        #active_view.inverseSelection()
        active_gui = GKGUISystem.getGUISystem().getActiveGui()
        selection = model.getGeoModel().getSelection()
        selection.clear()
        active_gui.invalidateViews()
        # increment counters
        deleted_sections_count += 1
        if deleted_sections_count % 100 == 0:
            print("Processed {} short sections".format(deleted_sections_count))
print("Removed {} short sections".format(deleted_sections_count))
print("Failed to delete {} short sections".format(failed_to_delete_count))
print("Done!")