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
values(553,1);

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


-- 내가 본 컨텐츠 insert
select * from contentWatchme;
insert into contentWatchme(userId,contentId)
values("1","1");

-- 내가 본 컨텐츠 목록 가져오기

select cw.userId,cw.contentId,c.title,c.imgUrl,c.contentRating,c.tmdbcontentId,c.type
from contentWatchme cw 
join content c 
on cw.contentId = c.Id
where cw.userId = 1;

-- 컨텐츠 가져오기
select * from content;
select * from contentLike;
select * from user;

select c.*, if(cl.contentLikeUserId = null  , 0 , 1 ) as 'like'
from content c left join contentLike cl
on  c.id = cl.contentId
where c.id = 553;

-- 컨텐츠 리뷰 가져오기
select * from contentReview;
select * from contentReviewLike;

select cr.*, count(crl.contentReviewLikeUserId) as likeCnt
from contentReview cr left join contentReviewLike crl
on cr.contentReviewId = crl.contentReviewId 
where cr.contentId = 553
group by contentReviewId;


insert into contentReviewLike(contentReviewId,contentReviewLikeUserId)
values(2,3);

select *
from contentReview
where contentId = 553;

-- 컨텐츠 리뷰 댓글 가져오기
select *
from contentReviewComment
where contentReviewId = 1;

-- 파티 글 작성
select * from partyBoard;

insert into partyBoard(service,title,userId,serviceId,servicePassword)
values("Netflix","넷플구독자구함",1,"abc@naver.com","1234");

-- 파티 글 전체 가져오기

select partyBoardId,service,title,content,createdAt,userId from partyBoard; 

-- 내 파티 글 수정
select * from partyBoard where partyBoardId = 1 and userId = 1;

update partyBoard
set service = "",title = "" , content = "" , serviceId = "", servicePassword = ""
where partyBoardId = 1 and userId = 1;

-- 내 파티 글 삭제

select * from partyBoard;

delete from partyBoard
where partyBoardId = 2 and userId = 1;

-- 파티 글 검색
select pb.*,count(member) as memberCnt 
from partyBoard pb left join party p 
on pb.partyBoardId = p.partyBoardId 
where pb.title like "%아마존%" or pb.service like "%Netflix%"
group by partyBoardId;

select * from partyBoard;
delete from partyBoard where partyBoardId = 4;
-- 파티 맺기 ( 결제 완료 )
select * from party;

select userId ,service , finishedAt from partyBoard where partyBoardId = 5;

insert into party(captain , member , partyBoardId )
values(1,5,5);
select * from paymentDetails;

insert into paymentDetails(partyBoardId,userId,amount,date)
values(3,2,4250,'2023-03-04');

select * from paymentDetails;

-- 내가 맺은 파티 항목 전체 가져오기
select p.captain,p.partyBoardId,p.createdAt,pb.service,pb.title,pb.content,pb.serviceId,pb.servicePassword,pb.finishedAt
from party p 
left join partyBoard pb 
on p.partyBoardId = pb.partyBoardId
where member = 3;
-- 내가 맺은 파티 일부 항목 가져오기

-- 파티 맺기 취소 ( 결제 취소 )
delete from party
where member = 2 and partyBoardId = 5;

-- 파티 완료 여부 확인

select count(member) as memberCnt from party
where partyBoardId = 5 
group by partyBoardId;

-- 

select * from contentWatchme;

select cw.userId,cw.contentId,c.title,c.imgUrl,c.contentRating,c.tmdbcontentId,c.type
                    from contentWatchme cw 
                    join content c 
                    on cw.contentId = c.Id
                    where cw.userId = 1;

select * from tag;

select *
from contentReviewComment;

select * from partyBoard;
				