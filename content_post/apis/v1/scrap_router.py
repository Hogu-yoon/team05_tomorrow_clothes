from typing import Any, Dict

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from ninja import Router
from content_post.models.contents import Feeds
from user_admission.models.user import User

content = Router(tags=["Scrap"])


@content.post("/scrap/{feed_id}/", url_name="scrap")
# @login_required(login_url="/login/")
@transaction.atomic
def post_scrap(request: HttpRequest, feed_id: int) ->Dict[str,int]:
    login_user = request.user.is_authenticated
    if login_user:
        user_id: Any = request.user.id
        # 로그인한 유저의 정보가져오기
        user: User = User.objects.get(id=user_id)
        # user = 로그인한 객체
        feed: Feeds = Feeds.objects.select_for_update().get(id=feed_id)
        # feed = 스크랩할 피드의 객체
        # exist_check = feed.scrape.filter(id=user_id)  # type : ignore장
        #select_for_update()트랜잭션 데코레이터와 사용가능
        #디비에 락걸린걸 줄세워서 처리? 순서대로 처리? 라고 이해했습니다 공부가 더 필요합니다
        exist_check = feed.scrape.select_for_update().filter(id=user_id)
        # scrape필드에 로그인한 유저가있는지 체크
        if exist_check.exists():
            # 만약 있다면
            feed.scrape.remove(user)
            # scrape필드에서 유저를 제거
            feed.scrapes -= 1
            # 스크랩카운트 -1
            feed.save()
            # 저장
            scrap_count = feed.scrapes
            # 저장된 스크립카운트
            ajax = {"scrap_count": scrap_count}
            # 딕셔너리형태로 제이슨으로 보낸다
            return ajax
        else:
            # 없다면
            feed.scrape.add(user)
            # scrape필드에 유저를 추가
            feed.scrapes += 1
            # 스크랩카운트+1
            feed.save()
            # 저장
            scrap_count = feed.scrapes
            # 저장된카운트
            ajax = {"scrap_count": scrap_count}
            # 딕셔너리형태로 제이슨으로 보낸다
            return ajax
    else:
        return {"error": 1}


# @content.delete("/scrap/{feed_id}/")
# @login_required(login_url="/login/")
# def scrap_off(request: HttpRequest, feed_id: int, user_id: int) -> HttpResponse:
#     Feeds.objects.get(id=feed_id).scrape.remove(User.objects.get(id=user_id))
#     return redirect("/")
