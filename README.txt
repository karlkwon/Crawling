#TED education crawling

##Prerequisite
사용을 하기 위해서 elasticsearch server 정보를 설정해야 함.
position: 1.TED_TITLE/TED5/settings.py

##실행 (1) - crawling: title, student level, content_type, youtube id
cd 1.TED_TITLE
scrapy crawl ted5

##실행 (2) - subtitle downloading
'1.TED_TITLE' 에 있는 ipython notebook 참고
