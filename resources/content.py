from flask import request
from flask_restful import Resource
from mysql.connector.errors import Error
from mysql_connection import get_connection
from flask_jwt_extended import jwt_required,get_jwt_identity

class searchoption() :
    def movieSearch(data) :
        print(data)
        keyword = data["keyword"]
        genre = data["genre"]
        limit = data["limit"]
        rating = data["rating"]
        year = data["year"]
        offset = data["offset"]
        filtering = data["filtering"]
        sort = data["sort"]
        try :
            connection = get_connection()
            query='''select * 
                from content 
                where (title like "%'''+ keyword+'''%" or content like "%'''+ keyword+'''%" ) and type = "movie" and
                genre like "%'''+genre+'''%" and contentRating >= '''+str(rating)+''' and createdYear >= "'''+str(year)+'''"
                order by '''+filtering + ''' '''+sort+'''
                limit '''+ str(offset)+''',''' +str(limit)+''';'''
            print(query)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            movie_list = cursor.fetchall()
            i = 0 
            for row in movie_list :
                movie_list[i]['createdYear'] = row['createdYear'].isoformat()
                i = i + 1
            cursor.close()
            connection.close()
        except Error as e :
                print(e)
                cursor.close()
                connection.close()
                return {"fail" : str(e)},500
        return movie_list

    def tvSearch(data) :
        keyword = data["keyword"]
        genre = data["genre"]
        limit = data["limit"]
        rating = data["rating"]
        year = data["year"]
        offset = data["offset"]
        filtering = data["filtering"]
        sort = data["sort"]
        try :
            connection = get_connection()
            query='''select * 
                    from content 
                    where (title like "%'''+ keyword+'''%" or content like "%'''+ keyword+'''%" ) and type = "tv" and
                    genre like "%'''+genre+'''%" and contentRating >= '''+str(rating)+''' and createdYear >= "'''+str(year)+'''"
                    order by '''+filtering + ''' '''+sort+'''
                    limit '''+ str(offset)+''',''' +str(limit)+''';'''
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            tv_list = cursor.fetchall()
            i = 0 
            for row in tv_list :
                tv_list[i]['createdYear'] = row['createdYear'].isoformat()
                i = i + 1
            cursor.close()
            connection.close()
        except Error as e :
                print(e)
                cursor.close()
                connection.close()
                return {"fail" : str(e)},500
        return tv_list
    
    def actorSearch(keyword) :
        try :
            connection = get_connection()
            query = '''select * from actor where name like "%''' +keyword+'''%" ;  '''
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            actor_list = cursor.fetchall()
            i = 0
            for row in actor_list :
                actor_list[i]['year'] = row['year'].isoformat()
                i = i + 1
            cursor.close()
            connection.close()     

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"fail" : str(e)},500
        
        return actor_list
        

class search(Resource) :
    
    def post(self) :

        data = request.get_json()
        type = request.args.get('type')

        if data["filtering"] == "":
            data["filtering"] = "title"
        if data["filtering"] not in ["title","contentRating","createdYear","Id"] :
            return {"sort_error":"필터 정렬 값 오류."}
        if data["sort"] == "":
            data["sort"] = "asc"
        if data["rating"] == "" : 
            data["rating"] = 0.0
        if data["year"] == "" :
            data["year"] = '1945-01-01'
        if data["limit"] =="" :
            data["limit"] = "10"
        if data["offset"] =="":
            data["offset"] = "0"
        
        if type == 'all' :
            movie_list=searchoption.movieSearch(data)
            tv_list=searchoption.tvSearch(data)
            actor_list=searchoption.actorSearch(data["keyword"])

            return {"movie" : movie_list,
                    "tv":tv_list,
                    "actor":actor_list},200
            
        elif type =='movie' :
            movie_list = searchoption.movieSearch(data)    
            return {'movie' : movie_list},200
        elif type == 'tv' :
            tv_list = searchoption.tvSearch(data)
            return {'tv':tv_list},200
        elif type == 'actor' :
            actor_list = searchoption.actorSearch(data["keyword"])
            return {'actor':actor_list},200
        else :
            return{'error':'type error'},500       
            
class content(Resource) :
    def get(self,contentId) :
        try :
            connection = get_connection()
            query = '''select c.*, if(cl.contentLikeUserId = null  , 0 , 1 ) as 'like'
                    from content c left join contentLike cl
                    on  c.id = cl.contentId
                    where c.id = %s ;'''
            record=(contentId,)
            cursor=connection.cursor(dictionary=True)
            cursor.execute(query,record)
            content = cursor.fetchall()

            cursor.close()
            connection.close()
        except Error as e:
            print(str(e))
            cursor.close()
            connection.close()
            return {'error':str(e)},500
        
        content[0]['createdYear'] = content[0]['createdYear'].isoformat()

        return {'result':'success','content':content},200



class contentLike(Resource) :
    @jwt_required()
    def post(self,contentId):
        userId = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''insert into contentLike(contentId,contentLikeUserId)
                        values(%s,%s);'''
            record = (contentId,userId)

            cursor = connection.cursor()
            cursor.execute(query,record)

            connection.commit()


            cursor.close()

            connection.close()

        except Error as e :
            print(str(e))

            cursor.close()

            connection.close()

            return {'fail',str(e)},500
        
        return {"result":"success"},200

    @jwt_required()
    def delete(self,contentId) :
        userId = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''delete from contentLike 
                    where contentId = %s and contentLikeUserId = %s ;'''
            
            record = (contentId, userId)

            cursor = connection.cursor()

            cursor.execute(query,record)

            connection.commit()

            cursor.close()

            connection.close()
        
        except Error as e : 
            print(str(e))

            cursor.close()

            connection.close()

            return {"error":str(e)},500

        return {"result":"success"},200
            
class contentReview(Resource) :
    def get(self,contentId) :
        try :
            connection = get_connection()
            query = '''select cr.*, count(crl.contentReviewLikeUserId) as likeCnt
                        from contentReview cr left join contentReviewLike crl
                        on cr.contentReviewId = crl.contentReviewId 
                        where cr.contentId = %s
                        group by contentReviewId;'''
            record = (contentId,)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query,record)

            contentReview_list = cursor.fetchall()
            
            cursor.close()
            connection.close()
            i = 0
            for row in contentReview_list :
                contentReview_list[i]['createdAt'] = row['createdAt'].isoformat()
                contentReview_list[i]['updatedAt'] = row['updatedAt'].isoformat()
                i=i+1
        except Error as e :
            print(str(e))
            cursor.close()
            connection.close()
            return {'error',str(e)},500
        
        return {'result':'success','contentReviewList':contentReview_list},200

    @jwt_required()
    def post(self,contentId) :

        userId = get_jwt_identity()

        data = request.get_json()

        try:
            connection = get_connection()

            query = '''insert into contentReview(contentId,contentReviewUserId, title,content,userRating)
                        values(%s,%s,%s,%s,%s);'''
            
            record = (contentId,userId, data["title"],data["content"],data["userRating"])

            cursor = connection.cursor()

            cursor.execute(query,record)

            connection.commit()

            lastId = cursor.lastrowid

            cursor.close()

            connection.close()

        except Error as e :

            print(str(e))
            
            cursor.close()

            connection.close()

            return {"fail":str(e)},500

        return {"result":"success","contentReviewId":lastId},200

    

class contentReviewUD(Resource) :
    @jwt_required()
    def put(self ,contentId , contentReviewId) :
        
        userId = get_jwt_identity()
        
        data = request.get_json()
        
        try : 
            connection = get_connection()

            query = '''update contentReview 
                        set title = %s ,content = %s
                        where contentreviewId = %s and contentReviewUserId = %s
                        ;'''
            
            record = (data['title'],data['content'],contentReviewId,userId)

            cursor = connection.cursor()

            cursor.execute(query,record)

            connection.commit()

            cursor.close()

            connection.close()

        except Error as e :
            str(e)
            cursor.close()
            connection.close()

            return {'error':str(e)},500
        
        return {'result':'success'} , 200

    @jwt_required()
    def delete(self,contentId,contentReviewId) :
        userId = get_jwt_identity()
     
        try : 
            connection = get_connection()

            query = '''delete from contentReview
                    where contentReviewId = %s and contentReviewUserId = %s;
                        ;'''
            
            record = (contentReviewId,userId)

            cursor = connection.cursor()

            cursor.execute(query,record)

            connection.commit()

            cursor.close()

            connection.close()

        except Error as e :
            str(e)
            cursor.close()
            connection.close()

            return {'error':str(e)},500
        
        return {'result':'success'} , 200

class contentReviewLike(Resource) :
    @jwt_required()
    def post(self,contentReviewId) :
        userId = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''insert into contentReviewLike(contentReviewId,contentReviewLikeUserId)
                        values(%s,%s);'''
            record = (contentReviewId , userId)

            cursor = connection.cursor()
            cursor.execute(query,record)

            connection.commit()

            cursor.close()
            connection.close()

        except Error as e :
            print(str(e))
            cursor.close()
            connection.close()
            return {"error":str(e)},500
        
        return {"result":"success"},200
    
    @jwt_required()
    def delete(self,contentReviewId) :
        userId = get_jwt_identity()

        try :
            connection = get_connection()

            query ='''delete from contentReviewLike 
                    where contentReviewId = %s and contentReviewLikeUserId = %s ;'''
            record = (contentReviewId , userId)

            cursor = connection.cursor()
            cursor.execute(query,record)

            connection.commit()

            cursor.close()
            connection.close()

        except Error as e :
            print(str(e))
            cursor.close()
            connection.close()
            return {"error":str(e)},500
        
        return {"result":"success"},200

class ReviewComment(Resource):
    def get(self,contentReviewId):
        try:
            connection = get_connection()
            query = '''select *
                    from contentReviewComment
                    where contentReviewId = %s ;'''
            record = (contentReviewId,)

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query,record)

            comment_list = cursor.fetchall()

            i = 0
            for row in comment_list :
                comment_list[i]['createdAt'] = row['createdAt'].isoformat()
                comment_list[i]['updatedAt'] = row['updatedAt'].isoformat()
            cursor.close()
            connection.close()
        except Error as e :
            print(str(e))
            cursor.close()
            connection.close()
            return {'error',str(e)},500
        
        return {'result':'success','commentList':comment_list},200
    
    @jwt_required()
    def post(self,contentReviewId) :
        userId = get_jwt_identity()
        data = request.get_json()
        try :
            connection = get_connection()

            query = '''insert into contentReviewComment(contentReviewId , commentUserId , comment )
                        values (%s,%s,%s);'''
            record = (contentReviewId,userId,data['comment'])

            cursor = connection.cursor()

            cursor.execute(query,record)

            connection.commit()

            lastId = cursor.lastrowid
            cursor.close()

            connection.close()
        except Error as e :
            print(str(e))
            cursor.close()
            connection.close()
            return {'error':str(e)},500
        
        return {'result':'success','commentId':lastId},200

class ReviewCommentUD(Resource):
    @jwt_required()
    def delete(self,contentReviewId,commentId) :
        
        userId = get_jwt_identity()

        try : 
            connection = get_connection()

            query = '''delete from contentReviewComment
                    where commentId = %s and contentReviewId = %s and commentUserId = %s ;'''
            record = (commentId,contentReviewId,userId)

            cursor = connection.cursor()

            cursor.execute(query,record)

            connection.commit()

            cursor.close()

            connection.close()

        except Error as e :
            print(str(e))

            cursor.close()

            connection.close()

            return {'error':str(e)},500
        return {'result':'success'},200        

    @jwt_required()
    def put(self,contentReviewId,commentId) :

        userId = get_jwt_identity()

        data = request.get_json()

        try :
            connection = get_connection()

            query = '''update contentReviewComment
                        set comment = %s
                        where commentId = %s and contentReviewId = %s and commentUserId = %s;'''
            record = (data['comment'],commentId,contentReviewId,userId)

            cursor = connection.cursor()

            cursor.execute(query,record)

            connection.commit()

            cursor.close()

            connection.close()

        except Error as e :
            print(str(e))

            cursor.close()

            connection.close()

            return {'error':str(e)},500

        return {'result':'success'},200        

class ContentWatch(Resource) :
    @jwt_required()
    def post(self,contentId):
        userId = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''insert into contentWatchme(userId,contentId)
                        values(%s,%s);'''
            record = (userId,contentId)

            print(record)

            cursor = connection.cursor()

            cursor.execute(query,record)

            connection.commit()

            cursor.close()

            connection.close()

        except Error as e :
            print(str(e))

            cursor.close()

            connection.close()

            return {'error':str(e)},500
        
        return {'result':'success'},200

class contentWatchme(Resource):
    @jwt_required()
    def get(self):
        userId = get_jwt_identity()

        try : 
            connection = get_connection()
            query = '''select cw.userId,cw.contentId,c.title,c.imgUrl,c.contentRating,c.tmdbcontentId,c.type
                    from contentWatchme cw 
                    join content c 
                    on cw.contentId = c.Id
                    where cw.userId = %s;'''
            record = (userId,)

            cursor = connection.cursor(dictionary=True)

            cursor.execute(query,record)

            contentWatch_list = cursor.fetchall()

            print(userId)
            print(contentWatch_list)

            cursor.close()

            connection.close()

        except Error as e :
            print(str(e))

            cursor.close()

            connection.close()

            return {'error':str(e)},500
        


        return {'result':'success','contentWatch_list':contentWatch_list},200



