from deap import gp
from deap import base
from deap import tools
from deap import creator
from deap import algorithms

from collections import Counter
from itertools import groupby

import numpy as np
import sklearn, json, pickle

import pyglet
import time

'''play the song using EasyABC software - paste the following lines and then the GP output.
X:1
T:Alexa, Compose Music
O:GP
A:The Computer
M:C
L:1/8
Q: "Any"
K:C
V:1
'''

###########################################
# load sample data from DNN and GP output to train a classifier
with open('dnn_sample_output.txt', 'r') as f:
    dnn_df = json.load(f)
with open('gp_sample_output.txt', 'r') as f:
    gp_df = json.load(f)
X_train = dnn_df + gp_df

# convert raw sequence output into features (term frequencies)
from sklearn.feature_extraction.text import CountVectorizer
count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(X_train)
from sklearn.feature_extraction.text import TfidfTransformer
tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
Y_train = [0]*len(dnn_df) + [1]*len(gp_df)

# train a simple Bayes classifier
from sklearn.naive_bayes import MultinomialNB
discriminator = MultinomialNB().fit(X_train_tfidf, Y_train)
###########################################

#making own function set


def play_two(arg1,arg2):
    a = arg1 + arg2
    #a = "".join(a)
    #a = bloat_check(a)
    return a

def add_space(arg1,arg2):
    a = arg1 + " " + arg2
    #a = "-".join(a)
    #print(a)
    #a = bloat_check(a)
    return a

def play_twice(arg1):
    a = 2*arg1
    #a = bloat_check(a)
    return a

def mirror(arg1):
    #a = bloat_check(arg1)
    a = "|1"+arg1+":|"
    return a
    

def play_and_mirror(arg1,arg2,arg3):
    #a = arg1 + arg1[::-1]
    a = "|1"+arg1+arg2+arg3+arg3+arg2+arg1+":|"
    #a = "".join(a)
    #a = bloat_check(a)
    return a
    
    
def evaluate_song(arg):
    
    expr = arg[0]
    #expr = ''.join(str(i) for i in l)
    tree = gp.PrimitiveTree(expr)
    tree = str(tree)
    #print("t:  ",tree)
    song = gp.compile(tree, pset)
    #print(function)
    return song
    
def evaluate_final_pop(arg):
    
    expr = arg
    #expr = ''.join(str(i) for i in l)
    tree = gp.PrimitiveTree(expr)
    tree = str(tree)
    #print("t:  ",tree)
    song = gp.compile(tree, pset)
    #print(function)
    return song

def evaluate_fitness(arg):
    #print(arg)
    
    fitness = 0
    tree = gp.PrimitiveTree(arg)
    tree = str(tree)
    #print("t:  ",tree)
    song = list(gp.compile(tree, pset))

    ###########################################
    str_song = "".join(song)
    # convert sequence into latent embeddings form
    X_new_counts = count_vect.transform([str_song])
    X_new_tfidf = tfidf_transformer.transform(X_new_counts)

    # discriminator predict probability of given sample being generated by DNN or GP
    dnn_prob, gp_prob = discriminator.predict_proba(X_new_tfidf)[0]
    # higher penalty if the sample is considered more like GP outpout
    fitness -= 200 * gp_prob
    ###########################################
    
    if (len(song) <= 3):
        fitness = fitness - 10
    elif (len(song) > 3 and len(song) <= 100):
        fitness += 9
    else:
        fitness -= 70
    c = Counter(song)
    note_count = c.values()
    notes = c.keys()
    for value in note_count:
        if value <= len(song)/3:
            fitness += 10
        if value > len(song)/2:
            fitness = fitness - 20
    
    return fitness,
    


#adding functions to the function set
pset = gp.PrimitiveSet("MAIN", 0)
pset.addPrimitive(play_two, 2)
pset.addPrimitive(add_space, 2)
pset.addPrimitive(play_twice, 1)
pset.addPrimitive(mirror, 1)
pset.addPrimitive(play_and_mirror, 3)


#adding notes to the terminal set
'''C, D, E, F,|G, A, B, C|D E F G|A B c d|e f g a|b c' d' e'|f' g' a' b'|'''

final_list = list()
new_list = list()
# notes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'a', 'b', 'c', 'd', 'f', 'g', 'A,', 'B,', 'C,', 'D,', 'E,', 'F,', 'G,',
        # "a'", "b'", "c'", "d'", "e'", "f'", "g'", '"A"', '"B"', '"C"', '"D"', '"E"', '"F"', '"G"']
# notes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'a', 'b', 'c', 'd', 'f', 'g', 
        # "a'", "b'", "c'", "d'", "e'", "f'", "g'", '"A"', '"B"', '"C"', '"D"', '"E"', '"F"', '"G"']
notes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'a', 'b', 'c', 'd', 'f', 'g', 'A,', 'B,', 'C,', 'D,', 'E,', 'F,', 'G,',
             "a'", "b'", "c'", "d'", "e'", "f'", "g'", '"A"', '"B"', '"C"', '"D"', '"E"', '"F"', '"G"', 'A', 'B', 'C',
             'D', 'E', 'F', 'G', 'a', 'b', 'c', 'd', 'f', 'g', 'A,', 'B,', 'C,', 'D,', 'E,', 'F,', 'G,', "a'", "b'",
             "c'", "d'", "e'", "f'", "g'", '"A"', '"B"', '"C"', '"D"', '"E"', '"F"', '"G"', 'A', 'B', 'C', 'D', 'E',
             'F', 'G', 'a', 'b', 'c', 'd', 'f', 'g', 'A,', 'B,', 'C,', 'D,', 'E,', 'F,', 'G,', "a'", "b'", "c'", "d'",
             "e'", "f'", "g'", '"A"', '"B"', '"C"', '"D"', '"E"', '"F"', '"G"']
#operation_list = ['', '_', '^', '=']
operation_list = ['']
#time_list = ['', '2', '3', '4', '/2', '3/2', '3/4', '/4']
time_list = ['', '2', '/2']

for note in notes:
    for ops in operation_list:
        new_list.append(ops + note)

for value in new_list:
    for time_val in time_list:
        final_list.append(value + time_val)
        pset.addTerminal(value + time_val)

pset.addTerminal("z")
pset.addTerminal("|")
#print(final_list)
#print(len(final_list))

#initializing 
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax, pset=pset)

# Attribute generator
toolbox = base.Toolbox()
toolbox.register("expr_init", gp.genFull, pset=pset, min_=3, max_=5)

# Structure initializers
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr_init)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

'''need to have fitness evaluation to do anything else GP'''
toolbox.register("evaluate", evaluate_fitness)
toolbox.register("select", tools.selDoubleTournament, fitness_size = 5, parsimony_size=1.4,fitness_first = True)
#toolbox.register("select", tools.selBest)
toolbox.register("mate", gp.cxOnePoint)
toolbox.register("expr_mut", gp.genFull, min_=3, max_=5)
toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

#print(toolbox.individual())
population = toolbox.population(n=20)
hof = tools.HallOfFame(1)
#print([toolbox.clone(ind) for ind in population])
cxpb = 0.4
mutpb = 0.6
final_pop,_ = algorithms.eaSimple(population, toolbox, cxpb, mutpb, ngen = 50, halloffame=hof)
#print("final", len(hof))
#print("finalnpop" , final_pop)

final_out = []

for pop in final_pop:
    #print(pop)
    #print(kk)
    final_song = evaluate_final_pop(pop)
    #print(final_song)
    #print("-"*80)
    final_out.append(final_song)

final_song = evaluate_song(hof)
#final_song = ''.join(i for i in final_song_)
print(final_song)
