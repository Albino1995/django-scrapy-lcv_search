import json
from django.shortcuts import render
from django.views.generic.base import View
from search.models import ArticleType, JobType
from django.http import HttpResponse
from elasticsearch import Elasticsearch
from datetime import datetime

client = Elasticsearch(hosts=["127.0.0.1"])

# Create your views here.

def s_type(search_type):
    if search_type == "job":
        s = JobType.search()
    else:
        s = ArticleType.search()
    return s


def search_for_type(search_type):
    if search_type == "job":
        index = "liepin"
    else:
        index = "jobbole"
    return index

class SearchSuggest(View):

    def get(self, request):
        key_words = request.GET.get('s', '')
        search_type = request.GET.get('s_type', '')
        re_datas = []
        if key_words:
            s = s_type(search_type).suggest('my_suggest', key_words, completion={
                "field": "suggest", "fuzzy": {
                    "fuzziness": 2
                },
                "size": 10
            })
            suggestions = s.execute_suggest()
            for match in suggestions.my_suggest[0].options:
                source = match._source
                re_datas.append(source["title"])
        return HttpResponse(json.dumps(re_datas), content_type="application/json")


class SearchView(View):
    def get(self, request):
        key_words = request.GET.get("q", "")
        page = request.GET.get("p", "1")
        search_type = request.GET.get('s_type', '')
        index = search_for_type(search_type)
        try:
           page = int(page)
        except:
            page = 1

        start_time = datetime.now()
        response = client.search(
            index=index,
            body={
                "query": {
                    "multi_match": {
                        "query": key_words,
                        "fields": ["tags", "title", "content"]
                    }
                },
                "from": (page-1)*10,
                "size": 10,
                "highlight": {
                    "pre_tags": ["<span class='keyWord'>"],
                    "post_tags": ["</span>"],
                    "fields": {
                        "title": {},
                        "content": {},
                    }
                }
            }
        )

        end_time = datetime.now()
        last_seconds = (end_time - start_time).total_seconds()
        total_nums = response["hits"]["total"]
        if (page % 10) > 0:
            page_nums = int(total_nums / 10) + 1
        else:
            page_nums = int(total_nums / 10)
        hit_list = []
        for hit in response["hits"]["hits"]:
            hit_dict = {}
            if "title" in hit["highlight"]:
                hit_dict["title"] = "".join(hit["highlight"]["title"])
            else:
                hit_dict["title"] = hit["_source"]["title"]
            if "content" in hit["highlight"]:
                hit_dict["content"] = "".join(hit["highlight"]["content"])[:500]
            else:
                hit_dict["content"] = hit["_source"]["content"][:500]

            hit_dict["create_date"] = hit["_source"]["create_date"]
            if len(hit["_source"]["url"]) < 50:
                hit_dict["url"] = hit["_source"]["url"]
            else:
                hit_dict["url"] = hit["_source"]["url"][:50] + "..."
            hit_dict["score"] = hit["_score"]

            hit_list.append(hit_dict)

        return render(request, "result.html", {"page_nums": page_nums,
                                               "total_nums": total_nums,
                                               "page": page,
                                               "all_hits": hit_list,
                                               "key_words": key_words,
                                               "last_seconds": last_seconds})
