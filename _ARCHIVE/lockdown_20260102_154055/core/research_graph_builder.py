import networkx as nx, matplotlib.pyplot as plt, json
G=nx.Graph(); G.add_edge('Researcher A','Researcher B')
nx.draw(G,with_labels=True); plt.savefig('output/research_graph.png')
print('✅ research_graph_builder completed → output/research_graph.png')
