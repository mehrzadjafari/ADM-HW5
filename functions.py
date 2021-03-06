#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import networkx as nx
import csv
from collections import defaultdict
import numpy as np
import pickle 





def create_graph_dict(directory):
    """    
    The function creates a graph using the csv file directory provided as input
    
    Input: 
    directory (string): The directory of the csv file
    
    
    Returns: 
    graph_dict (graph): The graph made with default dictionary
    
    """
    graph_dict = defaultdict(list)
    
    file_handler = open(directory, "r", encoding = "utf-8")
    reader = csv.reader(file_handler, delimiter = "\t", quotechar = '"', 
                           quoting = csv.QUOTE_NONE)
    
    next(reader)
    for record in reader:
        source = int(record[1])
        target = int(record[2])
        
        graph_dict[source].append(target)
        
    return graph_dict








def check_directed(graph):
    """    
    The function to check if a graph is directed
    
    Input: 
    graph (Graph): The graph to be examined
    
    Returns: 
    directed (boolean): True if the graph is directed / False if the graph is not directed
    
    """
    
    for key, value in graph.items():
        for dest in value:
            if key in graph[dest]:
                directed = False
                return directed
            else:
                directed = True
                return directed

            

            
            
            
            
            
def BFS_click(graph, d, v):
    """    
    The recursive function which used to find the pages reachable in a given number of clicks
    
    Inputs:
    graph (Graph): The graph we are examining
    d (int): The number of clicks 
    v (int): The page number
    
    Returns: 
    The touple of all pages that a user can reach within 'd' clicks
    
    """
    
    if d == 1:
        new_visited_nodes = graph[v]
        return visited_nodes, np.array(new_visited_nodes).shape[0]
    if d == 2:
        new_visited_nodes = [elem for i in graph[v] for elem in graph[i] if elem not in graph[v]]
        return graph[v] + new_visited_nodes, np.array(new_visited_nodes).shape[0]
    if d >= 3:
        new_visited_nodes = [elem for i in BFS_click(graph, d-1, v)[0][-BFS_click(graph, d-1, v)[1]:] for elem in graph[i] if elem not in BFS_click(graph, d-1, v)[0]]
        
        return BFS_click(graph, d-1, v)[0] + new_visited_nodes, np.array(new_visited_nodes).shape[0]
    

    
    
    
    
    
    
def find_set_of_pages(graph):
    """    
    The function that use BFS_click function and asks the user:
    
    1. To enter a page number
    2. To enter a number of click
    
    To find the set of the reachable pages
    
    Input: 
    graph (graph): The graph we are examining
    
    Returns:
    set_pages (list): The set with all the pages a user can reach wiith 'd' clicks
    
    """
    
    print('Choose a page number:')
    v = int(input())
    
    print('Choose a number of clicks')
    d = int(input())
    
    set_pages = BFS_click(graph, d, v)[0]
    set_pages = list(set(set_pages))
    set_pages.sort()
    
    return set_pages
    

    
    



def create_subgraph(G, categories, c1=34, c2=646, random_pick=False):
    """
    The function creates a subgraph by using 2 category indexes determined in the input.

    Inputs:
    G (graph): The main graph
    categories (dataframe): The dataframe of categories and their corresponded nodes
    c1 (int): index of the first category. Default at 34
    c2 (int): index of the second category. Default at 646
    random_pick (bool): Whether to take the categories by random. Default set to False

    Returns:
    sub_G (graph): The subgraph created using the nodes of two categories out of the main graph (G)

    """
    df = categories.reset_index()
    n = len(df) + 1

    if random_pick:
        c1, c2 = np.random.randint(0, n, 2)

    print("First index: ", c1)
    print("Second index: ", c2)

    c1_nodes = df.iloc[c1][1]
    c2_nodes = df.iloc[c2][1]

    c1c2_nodes = np.concatenate([c1_nodes, c2_nodes])
    sub_G = G.copy()
    for i in list(sub_G.nodes):
        if i not in c1c2_nodes:
            sub_G.remove_node(i)

    return sub_G



def min_remove_hyperlinks(G, source_node, target_node):
    
    """
    The function calculates the paths from 'source node' to 'target node' in a graph and determines how many cuts are needed to disconnect them
    
    Inputs:
    G (Graph): The graph that we are working with
    source_node (int): The source node
    target_node (int): The target node
    
    
    Returns:
    Number of cuts required for the disconnection (if available)
    The edges which have to get removed to make sure two nodes would be disconnected
    
    """
    
    if source_node not in G.nodes:
        return("The source node is not in the graph")
    
    elif target_node not in G.nodes:
        return("The target node is not in the graph")
    
    else:
    
        cuts_count = 0
        path_list = []
        n = len(G) - 1
        checked = [source_node]
        collected_nodes = [(target for source, target in G.edges(source_node))]
        while collected_nodes:
            collected_groups = collected_nodes[-1]
            iterator_collected = next(collected_groups, None)
            if iterator_collected is None:
                collected_nodes.pop()
                checked.pop()
            elif len(checked) < n:
                if iterator_collected == target_node:

                    path_list.append(checked + [target_node])

                elif iterator_collected not in checked:
                    checked.append(iterator_collected)
                    collected_nodes.append((target for source, target in G.edges(iterator_collected)))
            else: #len(checked) == n:
                count = ([iterator_collected]+list(collected_groups)).count(target_node)
                for i in range(count):

                    path_list.append(checked + [target_node])

                collected_nodes.pop()
                checked.pop()

        if path_list == []:

            return("Source and Target are disconnected")

        else:
            results = []
            for path in path_list:

                (a,b) = path[0], path[1]
                if (a,b) not in results:
                    results.append((a,b))
                    cuts_count += 1
            print("You need " + str(cuts_count) + " cuts to disconnect them!\n\nThe List of hyperlinks to cut:")
            return(results)


        
def in_degree_centrality(node, in_degree):
    max_deg = max(list(in_degree.values()))
    in_degree_node = in_degree[node]
    return round(in_degree_node/max_deg, 4)        
        
def min_clicks(graph, c_0, categories):
    nodes = categories['pages'][c_0]
    list_centrality = [in_degree_centrality(node, degree_in) for node in nodes]
    v = nodes[np.argmax(np.array(list_centrality))]
    nodes.remove(v)
    clicks = [BFS_shortest_path(graph, v, i) for i in nodes]
    return clicks        


def BFS_shortest_path(graph, start_node, destination):
    count = 1
    visited_nodes = graph[start_node]
    if destination in visited_nodes:
        count = 1
    else:
        new_visited_nodes = [elem for i in visited_nodes for elem in graph[i] if elem not in visited_nodes]
        count += 1
        visited_nodes = visited_nodes + new_visited_nodes
        while destination not in new_visited_nodes:
            if len(visited_nodes) < len_all_vertices:
                new_visited_nodes = [elem for node in new_visited_nodes for elem in graph[node] if elem not in visited_nodes]
                count += 1
                visited_nodes = visited_nodes + new_visited_nodes
            else: 
                count = np.inf
                print('There is no path between the nodes indicated')
                break
    return count


# c_0 and c_1 are indexes of the new_pages_per_category dataframe
def category_shortest_path(graph, c_0, categories):
    source_nodes = categories['pages'][c_0]
    categories_distances = defaultdict(list)

    for i in categories.index:
        if i != c_0:
            destination_nodes = categories['pages'][i]
            paths = [BFS_shortest_path(graph, source, dest) for source in source_nodes for dest in destination_nodes if BFS_shortest_path(graph, source, dest) != np.inf]
            categories_distances[i] = np.median(np.array(paths))
    
    keys = categories_distances.keys()
    values = categories_distances.values()
    results = pd.DataFrame([keys, values]).T
    results.columns = ['categories', 'distance']
    results.sort_values('distance', inplace = True)
    categories_sorted = results['categories']
        
    return categories_sorted    
    
def pagerank(graph, N, iters, lambd = 0.85):
    init = dict(zip(graph.nodes, np.zeros(N)))
    x_0 = np.random.choice(graph.nodes, 1)[0]
    for i in range(iters):
        prob = np.random.random()
        if prob < (1-lambd): #teleport
            next_node = np.random.choice(graph.nodes, 1)[0]
            init[next_node] = init[next_node] + 1/iters
            x_0 = next_node
        else: # out_links
            try:
                next_node = np.random.choice(graph_dict[x_0], 1)[0]
            except ValueError:
                next_node = np.random.choice(graph.nodes, 1)[0]
            init[next_node] = init[next_node] + 1/iters
            x_0 = next_node

    return init
        
        
        
        

