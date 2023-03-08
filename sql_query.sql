use two_db;

truncate user;

select * from user;

-- 유저 회원 가입
insert into user(nickname,userEmail,password,gender,age)
values("","","","","");

-- 유저 로그인
select* 
from user
where userEmail="";

-- 유저 아이디 찾기
select * 
from user
where name = "정웅" and questionNum="1" and questionAnswer = "인천";

-- 검색
select * 
from content 
where title like "%%" and type = "movie" and
genre like "%Fantasy%" and genre like "%Ad%" and contentRating >= 0.0 and createdyear >= '2020-05-06'
limit 0, 10
;

select * from actor;
insert into actor(contentId,name,year)
values(1,"범죄입니다","2020-01-02");

-- 컨텐츠 찜하기
select * from contentLike;

insert into contentLike(contentId,contentLikeUserId)
values(1,1);

-- 내가 찜한 컨텐츠 삭제하기
delete from contentLike 
where contentId = 1 and contentLikeUserId = 1 ;

-- 내가 찜한 컨텐츠만 보여주기
select * from contentLike;
 
select cl.contentId,cl.contentLikeUserId,c.title,c.genre,c.content,c.imgUrl,c.contentRating,c.createdYear,c.tmdbcontentId 
from contentLike cl join content c 
on cl.contentId = c.Id; 

-- 컨텐츠 리뷰 작성 
select * from contentReview;

insert into contentReview(contentId,contentReviewUserId, title,content,userRating)
values("1","1","행복합니다 나는 ㅠㅠ","행복한거 맞지?","5");

-- 컨텐츠 리뷰 수정 

update contentReview 
set title = "수정이지롱" ,content = "수정이지!"
where contentReviewId = 1 ;

select * from contentReview ;
 
-- 컨텐츠 리뷰 삭제
delete from contentReview
where contentReviewId = 2 and contentReviewUserId = 1;

select * from contentReview;

-- 컨텐츠 리뷰 좋아요
select * from contentReviewLike;
insert into contentReviewLike(contentReviewId,contentReviewLikeUserId)
values(1,1);

-- 컨텐츠 리뷰 좋아요 취소
delete from contentReviewLike 
where contentReviewId = 1 and contentReviewLikeUserId = 1 ;

-- 컨텐츠 리뷰 댓글 달기
select * from contentReviewComment;

insert into contentReviewComment(contentReviewId , commentUserId , comment )
values ("1","1","완전대박!!!");

-- 컨텐츠 리뷰 댓글 삭제
delete from contentReviewComment
where commentId = 2 and contentReviewId = 1 and commentUserId = 1;

select * from contentReviewComment;
-- 컨텐츠 리뷰 댓글 수정

update contentReviewComment
set comment = ""
where commentId = 1 and contentReviewId = 1 and commentUserId = 1;

-- 회원가입시 유저 장르 설정

insert into userGenre(userId,tagId)
values("1","1");

-- 유저 정보 수정
select * from user;
update user
set nickname="",password = "",profileimgUrl=""
where id = 1;

-- 유저 회원 탈퇴
select * from user;

delete from user
where id = 2;
