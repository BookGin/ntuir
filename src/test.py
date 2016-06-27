#!/usr/bin/env python3
from src.c_model import model
import src.topic_cluster as tc
from src.helper import issuemodel
from src.helper import knn
from src.helper import bigram
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

import json
import os
import scipy as sp
import random

# issuemodel.load("./src/db")

topic_Xs = [ [] for i in range( tc.N_CLUS ) ]
topic_Ys = [ [] for i in range( tc.N_CLUS ) ]

K = 20

KNN = [ None for i in range( tc.N_CLUS ) ]

for i in range( tc.N_CLUS ):
    cur_Xs = model.Xs[ i ]
    cur_Ys = model.Ys[ i ]
    for j in range( cur_Xs.shape[ 0 ] ):
        topic_Xs[ i ].append( cur_Xs[ j ] )
        topic_Ys[ i ].append( cur_Ys[ j ] )

    KNN[ i ] = NearestNeighbors( n_neighbors=min( K , len( cur_Ys ) ) , metric='cosine' , algorithm='brute' , n_jobs=1 )
    KNN[ i ].fit( cur_Xs )

def knn_predict_post( post ):
    d = tc.vec.transform( [ bigram.get_words( post ) ] )
    topic = tc.clus.predict( d )[ 0 ]

    # print( "topic" , topic , len( topic_Ys[ topic ] ) )

    # knn.nearestNeighbors( topic_Xs[ topic ] )

    # knns = knn.kneighbors( d , K )

    knns = KNN[ topic ].kneighbors( d , return_distance=False )[ 0 ]

    votes = [ 0.0 for i in range( tc.N_CLASS )  ]
    for id in knns:
        labl = topic_Ys[ topic ][ id ]
        if labl >= 0:
            votes[ labl ] += 1 / K
    return votes

def genRandomDocInTopic( topic ):
    id = random.choice( tc.inv_topic[ topic ] )
    return tc.datas[ id ][ 'body' ]

def predict_user( posts , method ):
    acc_pr = [ 0.0 for i in range( tc.N_CLASS ) ]
    all_posts = posts
    # all_posts = [ obj[ 'body' ] for obj in posts ]
    if method == "LR":
        ( topic , tmp ) = model.predict( all_posts )
        for ( prob , classes ) in tmp:
            for ( i , p ) in enumerate( prob[ 0 ] ):
                if classes[ i ] >= 0:
                    acc_pr[ classes[ i ] ] += p / len( all_posts )
    elif method == "KNN":
        now = 0
        for post in all_posts:
            # print( "now  %d" % now )
            now += 1
            votes = knn_predict_post( post )
            for i in range( tc.N_CLASS ):
                acc_pr[ i ] += votes[ i ] / len( all_posts )
    return acc_pr
    
if __name__ == '__main__':

    for path , subdirs , files in os.walk( './validation' ):
        for file in files:
            if file[ -5 : ] == ".json":
                print( "now %s" % path+"::"+file )
                posts = json.load( open( os.path.join( path , file ) , 'r' ) )
                print( "predict" , path+"::"+file , predict_user( posts ) )
        print( path , subdirs , files )



