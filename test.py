import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN

if __name__ == '__main__':
    # Create a simple graph that looks like this:
    # http://en.wikipedia.org/wiki/Algebraic_connectivity#mediaviewer/File:6n-graf.svg
    G = nx.Graph()
    G.add_nodes_from(range(1,7))
    G.add_edges_from([(1,5), (1,2), (5,2), (4,5), (4,3), (3,2), (4,6)])

    # Export to graphml for verification
    nx.write_graphml(G, 'clustering-exercise.graphml')

    # Conveniently, networkx has a method for finding the Laplacian
    laplacian = nx.laplacian_matrix(G)

    # Use numpy to compute the Fiedler vector, which corresponds to the
    # second smallest eigenvalue of the Laplacian
    w, v = np.linalg.eig(laplacian.todense())
    algebraic_connectivity = w[1] # Neat measure of how tight the graph is
    fiedler_vector = v[:,1].T

    # NOTE: Apparently nx also does this now
    # fiedler_vector = [nx.fiedler_vector(G)]

    # If we make our basic spectral clustering cut, we split the graph
    # in two at the origin, like this.
    plt.plot(fiedler_vector, range(len(fiedler_vector)), 'ro')
    plt.plot([(0, 0), (-1, 1)])
    plt.axis([-1, 1, 0, 0])
    plt.show()

    # That results in tightly connected nodes 1,2,3 and 5 forming one cluster and more
    # sparsely connected nodes 4 and 6 forming the other.

    # But we can also try to cluster the nodes differently. We'll try to do that along
    # the single dimension Fiedler vector provides, except basing the clusters on a
    # density of 0.15 rather than a simple cut at the origin.
    db = DBSCAN(eps=0.15, min_samples=1).fit(fiedler_vector.T)

    # We won't plot this because it's a pain, but it results in four clusters:
    # points 1, 2 and 5 in one cluster, then points 4, 3 and 6 in separate clusters
    for k in set(db.labels_):
        class_members = [index[0] for index in np.argwhere(db.labels_ == k)]
        for index in class_members:
            print ('Cluster: %s, Point %s: %s' % (int(k), index + 1, fiedler_vector.T[index]))