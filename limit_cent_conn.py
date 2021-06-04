# -*- coding: utf-8 -*-
"""
Limit the number of centroid connections to specific threshold per centroid

Created on Wed Apr 28 17:18:57 2021

@author: islam
"""

connection_limit = 5
cent_config_id = 3918930
cent_config = model.getCatalog().find(cent_config_id) 
# model.getActiveCentroidConfiguration()
for centroid in cent_config.getCentroids():
    num_conn_from = centroid.getNumberConnectionsFrom()
    num_conn_to = centroid.getNumberConnectionsTo()
    for conn in centroid.getConnections():
        if num_conn_from + num_conn_to <= connection_limit:
            break
        # centroid is conn.getOwner()
        if conn.getConnectionType() == GK.eTo and \
            num_conn_to > connection_limit/2:
            # delet TO connection
            connected_object = conn.getConnectionObject()
            centroid.removeConnection(conn, GK.eDeleteObjects)
            num_conn_to -= 1
        elif conn.getConnectionType() == GK.eFrom and \
            num_conn_from > connection_limit/2:
            # delet TO connection
            connected_object = conn.getConnectionObject()
            centroid.removeConnection(conn, GK.eDeleteObjects)
            num_conn_from -= 1
print("Done!")