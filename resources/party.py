from flask import request
from flask_restful import Resource
from mysql.connector.errors import Error
from mysql_connection import get_connection
from flask_jwt_extended import jwt_required,get_jwt_identity
from utils import check_password, hash_password

class partySearch(Resource):
    def post(self) :
        data = request.get_json()
        
        try :
            connection = get_connection()

            query = '''select pb.*,count(member) as memberCnt 
                    from partyBoard pb left join party p 
                    on pb.partyBoardId = p.partyBoardId 
                    where pb.title like "%'''+data['keyword']+'''%" or pb.service like "%'''+data['service']+'''%"
                    group by partyBoardId;'''
            cursor = connection.cursor(dictionary=True)

            cursor.execute(query)

            partyList = cursor.fetchall()

            i = 0
            for row in partyList :
                partyList[i]['createdAt'] = row['createdAt'].isoformat()
                partyList[i]['finishedAt'] = row['finishedAt'].isoformat()
                i=i+1
            cursor.close()
            connection.close()
        except Error as e :
            print(str(e))
            cursor.close()
            connection.close()
            return {'error':str(e)},500
        
        return {'result': 'success','partyList':partyList},200
            
                

class partyBoard(Resource) :
    @jwt_required()
    def post(self) :
        
#         {
#           "service" : "Netflix",
#           "title" : "넷플릭스 구독자 구함",
#          
#           "serviceId" : "abc@naver.com",
#           "servicePassword" : "12345",
#           "finishedAt" : "2022-03-15"
#       }
        userId = get_jwt_identity()

        data = request.get_json()



        try :
            connection = get_connection()

            query = '''insert into partyBoard(service,title,userId,serviceId,servicePassword,finishedAt)
                    values(%s,%s,%s,%s,%s,%s);'''

            record = (data['service'],data['title'],userId,data['serviceId'],data['servicePassword'],data['finishedAt'])

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

    def get(self) : 
        try :
            connection = get_connection()

            query = '''select partyBoardId,service,title,createdAt,userId from partyBoard '''

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)

            partyBoard_list = cursor.fetchall()

            i = 0
            for row in partyBoard_list :
                partyBoard_list[i]['createdAt'] = row['createdAt'].isoformat()
                i = i+ 1

            cursor.close()
            connection.close()
        except Error as e :
            print(str(e))
            cursor.close()
            connection.close()
            return {'error':str(e)},500
        
        return {'result':'success','partyBoard' : partyBoard_list},200

class partyBoardUD(Resource) :
    @jwt_required()
    def put(self,partyBoardId):
#         {
#     "service" : "Netflix",
#     "title" : "넷플릭스 모집합니다.",
#    
#     "serviceId" : "rrc0777@naver.com",
#     "servicePassword" : "1234"
# }
        userId = get_jwt_identity()
        data = request.get_json()
        password = hash_password(data['servicePassword'])
        
        try : 
            connection = get_connection()

            query = '''update partyBoard
                    set service = %s,title = %s  , serviceId = %s, servicePassword = %s
                    where partyBoardId = %s and userId = %s;'''
            record = (data['service'],data['title'],data['serviceId'],password,partyBoardId,userId)

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
    def delete(self,partyBoardId) :
        
        userId = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''delete from partyBoard
                    where partyBoardId = %s and userId = %s;'''
            record = (partyBoardId,userId)
            
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
    

class party(Resource) :
    @jwt_required()
    def post(self) :

        userId = get_jwt_identity()
        data = request.get_json()
        try : 
            connection = get_connection()

            query = '''insert into party(captain , member , partyBoardId )
                    values(%s,%s,%s);'''
            record = (data['captain'],userId,data['partyBoardId'])

            cursor = connection.cursor()

            cursor.execute(query,record)

            connection.commit()

            partyId = cursor.lastrowid

            cursor.close()

            connection.close()

            connection = get_connection()

            query = '''insert into paymentDetails(partyBoardId,userId,amount,date)
                    values(%s,%s,%s,%s);'''
            record=(data['partyBoardId'],userId,data['pay'],data['finishedAt'])

            cursor = connection.cursor()

            cursor.execute(query,record)

            connection.commit()

            cursor.close()

            connection.close()

        except Error as e:
            print(str(e))

            cursor.close()

            connection.close()

            return {'error' : str(e)},500
        
        return {'result':'success'},200
    
    @jwt_required()
    def get(self) :

        userId = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''select p.captain,p.partyBoardId,p.createdAt,pb.service,pb.title,pb.serviceId,pb.servicePassword,pb.finishedAt
                        from party p 
                        join partyBoard pb 
                        on p.partyBoardId = pb.partyBoardId
                        where member = %s;'''
            record = (userId,)

            cursor = connection.cursor(dictionary=True)

            cursor.execute(query,record)

            party_list = cursor.fetchall()

            i = 0 
            for row in party_list :
                party_list[i]['createdAt'] = row['createdAt'].isoformat()
                party_list[i]['finishedAt'] = row['finishedAt'].isoformat()
                i = i + 1 
            cursor.close()

            connection.close()

        except Error as e :
            print(str(e))
            cursor.close()

            connection.close()
            return {'error',str(e)},500
        
        return {'result': 'success','partyList' : party_list},200
        
class partyD(Resource) :
    @jwt_required()
    def delete(self,partyBoardId):
        userId = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''delete from party
                    where member = %s and partyBoardId = %s;'''
            record = (userId,partyBoardId)

            cursor = connection.cursor()

            cursor.execute(query,record)

            connection.commit()

            cursor.close()
            connection.close()
        except Error as e : 
            print(str(e))
            cursor.close()
            connection.close()
            return {'error',str(e)},500
        
        return {'result':'success'},200

class partycheck(Resource) :
    def get(self,partyBoardId) :
        try :
            connection = get_connection()

            query = '''select count(member) as memberCnt from party
                        where partyBoardId = %s 
                        group by partyBoardId;
                        ;
                        '''
            record = (partyBoardId,)

            cursor = connection.cursor(dictionary=True)

            cursor.execute(query,record) 

            party_member_cnt = cursor.fetchall()

            cursor.close()

            connection.close()

        except Error as e :
            print(str(e))
            cursor.close()

            connection.close()
            return {'error',str(e)},500
        
        return {'result': 'success','memberCnt':party_member_cnt[0]},200