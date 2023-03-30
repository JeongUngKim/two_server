from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
import numpy as np
import pandas as pd
import joblib

#scikit-surprise 1.1.3 
from surprise import KNNBaseline
from surprise import SVD
from surprise import Dataset, Reader
from surprise import KNNBaseline
from surprise import accuracy
from surprise.model_selection import train_test_split
from surprise import NormalPredictor

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
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

class RecommendResource2(Resource):
    
    @jwt_required()
    def post(self):
        with open('hybrid_model.pkl', 'rb') as f:
            algo_svd, algo_knn, alpha = pickle.load(f)

        user_id = get_jwt_identity()
        rated_movies = request.form.getlist("rateMovies")
        print(rated_movies)
        # rated_movies = request.form['ratings']
        engine=get_db_table()
        conn = engine.connect()
        # cur = connect.cursor()


        # query = "SELECT * FROM content"
        # cur.execute(query)
        # connect.commit()

        new_data = pd.read_sql_table('contentReview', conn)
        print(new_data.head())



        new_data = new_data.rename(columns={'contentReviewUserId':'userId'})
        new_data = new_data.rename(columns={'contentId':'movieId'})
        new_data = new_data.rename(columns={'userRating':'rating'})
        # 기존에 평가한 영화를 제외한 추천 영화 리스트 생성
        recommended_movies = {}
        for movie_id in new_data['movieId'].unique():
            if movie_id not in rated_movies:
                # SVD 모델과 KNN 모델의 예측값 계산
                svd_estimate = algo_svd.predict(user_id, movie_id).est
                knn_estimate = algo_knn.predict(user_id, movie_id).est
                
                # 예측값을 이용해 hybrid 점수 계산
                hybrid_score = alpha * svd_estimate + (1 - alpha) * knn_estimate
                
                recommended_movies[movie_id] = hybrid_score

        # 추천 영화 리스트를 점수(score)를 기준으로 내림차순 정렬
        recommended_movies = sorted(recommended_movies.items(), key=lambda x: x[1], reverse=True)

        top_movies = recommended_movies[:10]
        df = pd.DataFrame(columns=['contentId','contentRating'])
        # print(f"사용자 {user_id}에게 추천하는 영화 리스트:")
        data=[]
        for i, movie in enumerate(top_movies):
            data.append(movie[0])
        
        data = tuple(data)
        # for i, movie in enumerate(top_movies):
        #     print(f"{i+1}. 영화 ID: {movie[0]}, 예측 평점: {movie[1]}")

        # contentIdList = df["contentId"].values
        # # contentIdList=list(set(contentIdList))

        try :
            connection = get_connection()

            query = '''select * from content
                    where Id in'''+str(data)+''';'''
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
        # data1 = jsonify(data)
        # return {'result':'success',
        #         'items':data1},200
        # return{'result','success'}
# if __name__=='__main__':
#     # Objects are being pickled with main_module as the top-level
#     recommend = joblib.load('hybrid_model.pkl')

# new_data = pd.read_csv("C:/Users/5-16/Desktop/two_data-main (1)/two_data-main/영화 & TV 데이터.csv",index_col= 0, encoding='CP949')

# print(new_data)

# recommend = joblib.load('recommend_content.pkl')

# recommend.recommend_movie_list(new_data,title="블랙 팬서: 와칸다 포에버")