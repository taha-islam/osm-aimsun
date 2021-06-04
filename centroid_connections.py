# -*- coding: utf-8 -*-
"""
Created on Mon May 17 22:00:33 2021

@author: islam

Connect centoids within a group to sections within its boundaries. The script 
limits the number of created connections to <max_no_connections> and does not 
create more than one connection to sections having the same name. Connections 
are created to sections that lie within specific layers (specified in 
<layers_ids>)
Need to set up the <scenarioId>, <region>, and <layers_ids> and to check any 
unconnected centroid at the end
"""

max_no_connections = 4
region = "Toronto"
group = model.getCatalog().findByName(region, model.getType("GKGroup"))
assert (group is not None)
centroidType = model.getType("GKCentroid")
scenarioId = 3918919
# tertiary, secondary, primary, trunk
layers_ids = [911, 863, 6864, 2778]

def createCenConnection(model, layer, section, centroid, type):
    '''
    

    Parameters
    ----------
    model : GKModel
        Active model
    layer : GKLayer
        The layer to which the connection will be added
    section : GKSection
        The section that will be connected to the centroid
    centroid : GKCentroid
        The centroid to which the connection will be added
    type : int
        1 --> (attracts) from      {destination}
        2 --> (generates) to      {origin}
        3 --> bidirectional      {origin & destination}

    Returns
    -------
    None.

    '''
    sectionId = section.getId()
    centroidId = centroid.getId()
    #Create a new connection
    connection = GKSystem.getSystem().newObject("GKCenConnection", model)
    #Set the connection's name
    connection.setName("Connection{0}between{1}and{2}".format(
        str(type), str(centroidId), str(sectionId)))
    #Set the connection's type
    #Must set the type before setting the object
    connection.setConnectionType(type)
    #Set the object connected by the connection
    connection.setConnectionObject(section)
    #Add the connection to specific zone (centroid)
    centroid.addConnection(connection)
    #Add the connection to the geoModel in a specific layer to make it visible
    model.getGeoModel().add(layer, connection)


totalConnections = 0
totalCentroids = 0
#Get all objects of that type
for centroid in group.getObjects():
    if not centroid.isA("GKCentroid"):
        continue
    totalCentroids += 1
    centroidConnections = 0
    sec_names = []
    for layerId in layers_ids:
        layer = model.getCatalog().find(layerId)
        for object in centroid.classifyObjects(scenarioId, 
                                               GKPolygon.eOnlyNodesAndSections, 
                                               layer):
            if object.isA("GKSection") and object.getName != "" and \
                object.getName() not in sec_names:
                createCenConnection(model, layer, object, centroid, 3)
                sec_names.append(object.getName())
                centroidConnections += 1
                totalConnections += 1
                if centroidConnections == max_no_connections:
                    break
        if centroidConnections == max_no_connections:
            break
    print("Centroid {0} has {1} connections.".format(centroid.getId(), centroidConnections))

print("Done")
print("Total created connections: {0} for {1} centroids".format(totalConnections, totalCentroids))
