from flask import Flask
from flask_restful import Api
from config import Config
from flask_jwt_extended import JWTManager

from resources.content import ContentWatch, ReviewComment, ReviewCommentUD, content, contentLike, contentReview, contentReviewLike, contentReviewUD, contentWatchme, search
from resources.party import party, partyBoard, partyBoardUD, partyD, partySearch, partycheck
from resources.user import UserContentLike, UserGenre, UserIsEmail, UserIsId, UserIsNickname, UserIspassword, UserLoginResource, UserLogoutResource, UserPasswordChanged, UserProfileChange, UserRegisterResource
from resources.user import jwt_blacklist

app = Flask(__name__)

app.config.from_object(Config)

jwt = JWTManager(app)

@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload) :
    jti = jwt_payload['jti']
    return jti in jwt_blacklist

api = Api(app)

# 검색 api
api.add_resource(search,'/search')

# 컨텐츠 api
api.add_resource(content,'/content/<int:contentId>')

# 컨텐츠 찜관련 api
api.add_resource(contentLike,'/contentlike/<int:contentId>')
api.add_resource(UserContentLike,'/contentlike/me')

# 컨텐츠 리뷰 관련 api
api.add_resource(contentReview,'/content/<int:contentId>/review')
api.add_resource(contentReviewUD,'/content/<int:contentId>/review/<int:contentReviewId>')

# 컨텐츠 리뷰 좋아요 api
api.add_resource(contentReviewLike,'/contentReview/<int:contentReviewId>/like')

# 컨텐츠 리뷰 댓글 관련 api
api.add_resource(ReviewComment,'/contentComment/<int:contentReviewId>')
api.add_resource(ReviewCommentUD,'/contentComment/<int:contentReviewId>/<int:commentId>')

# 내가 본 컨텐츠 관련 api
api.add_resource(ContentWatch,'/contentWatch/<int:contentId>')
api.add_resource(contentWatchme,'/contentWatch')

# 유저 로그인관련 api

api.add_resource(UserRegisterResource,"/register")
api.add_resource(UserLoginResource,"/login")
api.add_resource(UserLogoutResource,"/logout")
api.add_resource(UserIsEmail,"/isEmail")
api.add_resource(UserIsId,"/isId")
api.add_resource(UserIsNickname,"/isNickname")
api.add_resource(UserIspassword,"/ispassword")
api.add_resource(UserPasswordChanged,"/changedpassword")
api.add_resource(UserGenre,'/userGenre')

# 파티 글 api
api.add_resource(partyBoard,'/partyBoard')
api.add_resource(partyBoardUD,'/partyBoard/<int:partyBoardId>')

# 파티 맺기 api
api.add_resource(party,'/party')
api.add_resource(partyD,'/party/<int:partyBoardId>')

# 파티 체크 api
api.add_resource(partycheck,'/party/<int:partyBoardId>/check')

# 파티 검색 api
api.add_resource(partySearch,'/search/party')
# 유저 정보 관련 api
api.add_resource(UserProfileChange,'/user')

if __name__ == '__main__' : 
    app.run()