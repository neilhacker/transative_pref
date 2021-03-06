#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 12:48:15 2020

@author: neilhacker
"""
import itertools
import random
import networkx as nx 
import matplotlib.pyplot as plt
from collections import defaultdict 

options = ['Rio', 'tokyo', 'venice', 'rome','NYC','oslo','tulum', 'maldives']

x = itertools.combinations(options,2)

combins = []
for i in x:
    combins.append(i)
random.shuffle(combins)    

directed_edges = [] 

indif_edges = []

# gets user to rank pairs of options and then updates directed edges for graph later
# and also g so we can run algorith to find strongly connected components  
print('for the below type 1 or 2 depending on if you prefer the first or second option, or type 0 if indifferent')
for i in combins:
    answer = False
    while not answer:
        pref = input(f'{i[0]}, or, {i[1]}')
        try:
            if int(pref) == 1:
                directed_edges.append((i[0],i[1]))
                answer = True
            elif int(pref) == 2:
                directed_edges.append((i[1],i[0]))
                answer = True
            elif int(pref) == 0:
                indif_edges.append((i[1],i[0]))
                indif_edges.append((i[0],i[1]))
                answer = True
        except:
            continue

# elements of this list are sets of strongly connected components 
        
G_SSC = nx.DiGraph(directed_edges)
connected_nodes = [x for x in nx.kosaraju_strongly_connected_components(G_SSC) if len(x) > 1]

#finds cycles in graph and creates set of edges to represent those cycles
Gr = nx.DiGraph(directed_edges)
cy = list(nx.simple_cycles(Gr))

cycles = []
for i in connected_nodes:
    b = [x for x in cy if all(item in x for item in i) == True]
    if len(b) >0:
        cycles.append(b[0])

def nodes_to_edges(node_list): #this is just taking the ouput of nx.simple_cycles from a list to set of tuples
    edges = ()
    for i in range(len(node_list)-1):
        edge = (node_list[i], node_list[i+1])
        edges = edges + (edge,)
    edges = edges +((node_list[-1], node_list[0]),)
    return edges
        
edge_cycles = []
for i in cycles:
    edge_cycles.append(nodes_to_edges(i))

all_edges = indif_edges + directed_edges #get all edges


########################## plots graph of preferences and shows strict preference cycles ##########################
G = nx.DiGraph()
G.add_edges_from(all_edges)
node_size = [len(v) * 400 for v in G.nodes()]

# edge colours
colours = ['black','red','blue','green','pink']   
             
d = [[] for x in range(len(edge_cycles)+1)]

def edge_colourer(cycleList, edge):
    for cycle in cycleList:
         
        if edge in cycle:
            return cycleList.index(cycle)+1 
    return 0

for edge in directed_edges:
    placement = edge_colourer(edge_cycles, edge)
    if placement>4:
        placement = 1
    d[placement].append(edge)
    

#type of layout
plt.figure(figsize=(9,9))
pos = nx.circular_layout(G)
#edges
nx.draw_networkx_edges(G, pos, edgelist=indif_edges, edge_color='black', alpha = 0.6, 
                   node_size=node_size, width=2, arrows=True, arrowsize=40)

for i in range(len(d)):
    nx.draw_networkx_edges(G, pos, edgelist=d[i], edge_color=colours[i], alpha = 0.6, 
                       node_size=node_size, width=2, arrows=True, arrowsize=40)

#nodes
nx.draw_networkx_nodes(G, pos, node_size = node_size, node_color="Grey")

#labels
nx.draw_networkx_labels(G, pos)
#graph
plt.axis("off")
plt.title("Strict preferences cycles")
plt.show()



################################### Graph showing violations within indifference sets ###################################

direct_edge_copy = directed_edges.copy() #use this so when popping you can still use direct edges elsewhere
# shows strongly connected nodes based on indifferent edges
G_indif = nx.DiGraph(indif_edges)
indif_node_groups = [x for x in nx.kosaraju_strongly_connected_components(G_indif) if len(x) > 1]

# Finds edges of strict preference between nodes in indifference sets
indif_violating_edges = []
for node_set in indif_node_groups:
    for edge in directed_edges:
        if all(x in node_set for x in edge) == True:
            indif_violating_edges.append(edge)
            direct_edge_copy.pop(direct_edge_copy.index(edge))
            break

G = nx.DiGraph()
G.add_edges_from(all_edges)
node_size = [len(v) * 400 for v in G.nodes()]

# edge colours
colours = ['blue','turquoise','lightblue','cyan','pink']   
             
#splits inifference sets into groups so they can get different colours
indif_edge_groups = [[] for x in range(len(indif_node_groups))]

for edge in indif_edges:
    for indif_nodes in indif_node_groups:
        if any(x in edge for x in indif_nodes) == True:
            indif_edge_groups[indif_node_groups.index(indif_nodes)].append(edge)
    
#type of layout
plt.figure(figsize=(9,9))
pos = nx.circular_layout(G)

#edges
#draw strict pref edges
nx.draw_networkx_edges(G, pos, edgelist=direct_edge_copy, edge_color='black', alpha = 0.6, 
                       node_size=node_size, width=2, arrows=True, arrowsize=40)
#draw strict pref edges that are within indifference set
if len(indif_violating_edges) > 0:
    nx.draw_networkx_edges(G, pos, edgelist=indif_violating_edges, edge_color='red', alpha = 0.6, 
                       node_size=node_size, width=2, arrows=True, arrowsize=40)
#draw indif set 
for i in range(len(indif_edge_groups)): #drawing indifferent edges
    nx.draw_networkx_edges(G, pos, edgelist=indif_edge_groups[i], edge_color=colours[i], alpha = 0.6, 
                   node_size=node_size, width=2, arrows=True, arrowsize=40)

#nodes
nx.draw_networkx_nodes(G, pos, node_size = node_size, node_color="Grey")

#labels
nx.draw_networkx_labels(G, pos)
#graph
plt.axis("off")
plt.title("Strict preferences between items in indifference set")
plt.show()

########################## plots graph showing between indifference set cycles ##########################
G_all = nx.DiGraph(all_edges) #find all groups of strongly connected components
all_SSC_nodes = [x for x in nx.kosaraju_strongly_connected_components(G_all) if len(x) > 1]

# rare issue: you have >2 indifference sets that are SCC but the only cycle does
# not go through and indifferent edges so no cycle is found

if len(indif_node_groups) > 1: #only triggers if there multiple indifference sets one could link between
    if len(all_SSC_nodes) < len(indif_node_groups):# only triggers if at least 2 indifference sets are linked 
        #sets up list to hold lists of indifference sets that are in a cycle
        SSC_indif_sets = [[] for x in range(len(all_SSC_nodes))] 

        #populates SSC_indif_sets with lists of indifference sets that are in cycles
        for node_set in indif_node_groups:
            for ssc_set in all_SSC_nodes:
                if all(x in ssc_set for x in node_set) == True:
                    for node in node_set:
                        SSC_indif_sets[all_SSC_nodes.index(ssc_set)].append(node)
                    break
        
        
        #based on strongly connected componenets makes list where sublists are the indifference sets 
        # in the same SCC group      
        
        indif_sets_in_same_SCC = [[] for x in range(len(SSC_indif_sets))]
        
        for node_set in indif_node_groups:
            for i in range(len(SSC_indif_sets)):
                if all(x in SSC_indif_sets[i] for x in node_set) == True:
                    indif_sets_in_same_SCC[i].append(node_set)
        
        
        G_al = nx.DiGraph(all_edges)
        cyc = list(nx.simple_cycles(G_al))
        cyc = sorted(cyc, key=len)

         
        #this finds the shortest cycles that pass through at least one node in indifference 
        # sets that are joined
        good_cycles = [] 
        for group_of_indif_sets in indif_sets_in_same_SCC:
            good_cycle = []
            for cycle in cyc:
                count = 0
                for node_sets in group_of_indif_sets:
                    if any(i in cycle for i in node_sets) == True:
                        count += 1
                if count == len(group_of_indif_sets):
                    #below makes sure that at least one edge in the cycle goes within an indiff set
                    if any(edge in nodes_to_edges(cycle) for edge in indif_edge_groups) == True:
                        good_cycle = cycle
                        break        
            good_cycles.append(good_cycle)
                
                
        edge_cyclez = []
        if len(good_cycles[0]) > 0:
            for node in good_cycles:
                edge_cyclez.append(nodes_to_edges(node))

        directed_edges_graph3 = directed_edges.copy()
        indif_edges_graph3 = indif_edges.copy()
        for cycle in edge_cyclez:
            for edge in cycle:
                if edge in directed_edges_graph3:
                    directed_edges_graph3.pop(directed_edges_graph3.index(edge))
                else:
                    indif_edges_graph3.pop(indif_edges_graph3.index(edge))
  
        # Graph showing violations between indifference sets
        
        # Finds edges of strict preference between nodes in indifference sets
        between_indif_violating_edges = []
        for cycle in edge_cyclez:
            for edge in cycle:
                between_indif_violating_edges.append(edge)
                
        G = nx.DiGraph()
        G.add_edges_from(all_edges)
        node_size = [len(v) * 400 for v in G.nodes()]
        
        # edge colours
        colours = ['blue','turquoise','lightblue','cyan','pink']   
                     
        #splits inifference sets into groups so they can get different colours
        indif_edge_groups = [[] for x in range(len(indif_node_groups))]
        
        for edge in indif_edges_graph3:
            for indif_nodes in indif_node_groups:
                if any(x in edge for x in indif_nodes) == True:
                    indif_edge_groups[indif_node_groups.index(indif_nodes)].append(edge)
                    
            
        #type of layout
        plt.figure(figsize=(9,9))
        pos = nx.circular_layout(G)
        
        #edges
        #draw strict pref edges
        nx.draw_networkx_edges(G, pos, edgelist=directed_edges_graph3, edge_color='black', alpha = 0.6, 
                               node_size=node_size, width=2, arrows=True, arrowsize=40)
        #draw strict pref edges that are within indifference set
        nx.draw_networkx_edges(G, pos, edgelist=between_indif_violating_edges, edge_color='red', alpha = 0.6, 
                               node_size=node_size, width=2, arrows=True, arrowsize=40)
        #draw indif set 
        for i in range(len(indif_edge_groups)): #drawing indifferent edges
            nx.draw_networkx_edges(G, pos, edgelist=indif_edge_groups[i], edge_color=colours[i], alpha = 0.6, 
                           node_size=node_size, width=2, arrows=True, arrowsize=40)
        
        #nodes
        nx.draw_networkx_nodes(G, pos, node_size = node_size, node_color="Grey")
        
        #labels
        nx.draw_networkx_labels(G, pos)
        #graph
        plt.axis("off")
        plt.title("Preferences cycles between indifference sets")
        plt.show()

########################## plots graph showing between indifference set cycles ##########################

G_indif = nx.DiGraph(indif_edges)
indif_node_groups4 = [x for x in nx.kosaraju_strongly_connected_components(G_indif) if len(x) > 1]

G_al = nx.DiGraph(all_edges)
cyc = list(nx.simple_cycles(G_al))
cyc = sorted(cyc, key=len)

# finds shortest cycles for each indif set that contain an edge from indif set
good_cyc = []
for group in indif_node_groups4:
    good_cycle = []
    end = False
    for cycle in cyc:
        cycle_copy = cycle.copy()
        cycle_copy.append(cycle_copy[0])
        if end == False:
            for i in range(len(cycle_copy)-1):
                pair = [cycle_copy[i], cycle_copy[i+1]]
                if all(node in group for node in pair) == True:
                    if all(node in group for node in cycle_copy) == False:
                        good_cycle = cycle_copy[0:-1]
                        end = True
                        print(good_cycle)
                    break
    good_cyc.append(good_cycle)

edge_cyc = []
if len(good_cyc[0]) or len(good_cyc)> 0:
    for nodes in good_cyc:
        if len(nodes) > 0:
            edge_cyc.append(nodes_to_edges(nodes))

directed_edges_graph4 = directed_edges.copy()
print(directed_edges_graph4)
indif_edges_graph4 = indif_edges.copy()
for cycle in edge_cyc:
    for edge in cycle:
        if edge in directed_edges_graph4:
            directed_edges_graph4.pop(directed_edges_graph4.index(edge))
        else:
            indif_edges_graph4.pop(indif_edges_graph4.index(edge))
  
# Graph showing violations between indifference sets

# Finds edges of strict preference between nodes in indifference sets
pref_cycle_w_indif = []
for cycle in edge_cyc:
    for edge in cycle:
        pref_cycle_w_indif.append(edge)
        
G = nx.DiGraph()
G.add_edges_from(all_edges)
node_size = [len(v) * 400 for v in G.nodes()]

# edge colours
# making indiff sets different shades
colours = ['blue','turquoise','lightblue','cyan','pink'] 
            
#splits inifference sets into groups so they can get different colours
indif_edge_groups4 = [[] for x in range(len(indif_node_groups))]

for edge in indif_edges_graph4:
    for indif_nodes in indif_node_groups4:
        if any(x in edge for x in indif_nodes) == True:
            indif_edge_groups4[indif_node_groups4.index(indif_nodes)].append(edge)
 
# making colour list for cycles that have one edge in an indif set
colours_cycle = ['red','orange','yellow']
if len(edge_cyc) > len(colours_cycle): #making sure list is never too long so if > 3 cycles all extra are red
    colours_cycle.append('red') * (len(edge_cyc)-len(colours_cycle))   
    
#type of layout
plt.figure(figsize=(9,9))
pos = nx.circular_layout(G)

#edges
#draw strict pref edges
nx.draw_networkx_edges(G, pos, edgelist=directed_edges_graph4, edge_color='black', alpha = 0.6, 
                       node_size=node_size, width=2, arrows=True, arrowsize=40)


#draw strict pref edges that are within indifference set
for i in range(len(edge_cyc)): #drawing indifferent edges
    nx.draw_networkx_edges(G, pos, edgelist=edge_cyc[i], edge_color=colours_cycle[i], alpha = 0.6, 
                   node_size=node_size, width=2, arrows=True, arrowsize=40)

#draw indif set 
for i in range(len(indif_edge_groups)): #drawing indifferent edges
    nx.draw_networkx_edges(G, pos, edgelist=indif_edge_groups4[i], edge_color=colours[i], alpha = 0.6, 
                   node_size=node_size, width=2, arrows=True, arrowsize=40)


#nodes
nx.draw_networkx_nodes(G, pos, node_size = node_size, node_color="Grey")

#labels
nx.draw_networkx_labels(G, pos)
#graph
plt.axis("off")
plt.title("Pref cycle hitting indifference sets")
plt.show()







