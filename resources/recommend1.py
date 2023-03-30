from flask import jsonify, request
from flask_restful import Resource
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pymysql
from sqlalchemy import create_engine

from engine import get_db_table
from mysql_connection import get_connection
from mysql.connector.errors import Error

class RecommendResource1(Resource):
    
    
    def post(self):
        engine=get_db_table()
        conn = engine.connect()

        movies = pd.read_sql_table('content', conn)
        # # print(movies.head())
        movies = movies.dropna()
        movies = movies.reset_index()
        movies = movies.drop(columns='index')
        movies.head(2)
        # # 장르 데이터 전처리
        # movies['genre'] = movies['genre'].str.replace('|', ' ')

        # TF-IDF 벡터화
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(movies['genre'])

        # 코사인 유사도 계산
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

        # 추천 함수
        # titles=['블랙 팬서: 와칸다 포에버','더 웨일','아바타: 물의 길']
        titles=request.form.getlist("titles")
        print(titles)
        # recommender = joblib.load('movie_recommender.pkl')
        
        indices = pd.Series(movies.index, index=movies['title'])
        idx_list = []
        for title in titles:
            idx = indices[title]
            sim_scores = list(enumerate(cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = sim_scores[1:11]
            movie_indices = [i[0] for i in sim_scores]
            idx_list.extend(movie_indices)
        idx_list = list(set(idx_list))
        df_rec = movies.iloc[idx_list][['Id', 'title', 'genre']].reset_index(drop=True)
        df_rec = df_rec[~df_rec['title'].isin(titles)].head(10)
    

        # contentIdList=recommender.recommend_movies(titles)
        contentIdList=df_rec["Id"].values
        contentIdList=tuple(contentIdList)
        print(contentIdList)
        try :
            connection = get_connection()

            query = '''select * from content
                    where Id in'''+str(contentIdList)+''';'''
            cursor = connection.cursor(dictionary=True)

            cursor.execute(query)

            recommendList = cursor.fetchall()
            i = 0
            for row in recommendList :
                recommendList[i]['createdYear'] = row['createdYear'].isoformat()
                
                i=i+1

            cursor.close()
            connection.close()

        except Error as e :
            print(str(e))
            cursor.close()
            connection.close()
            return {'error':str(e)},500
        
        return {'result': 'success','recommendLis':recommendList},200
        # return {'result':'success',
        #         'items':data2},200
        # return {'result':'success'},200