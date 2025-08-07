import os
import requests

from .type import RTYPE

LAW_API_BASE_URL = "http://www.law.go.kr"



class LawApiParams(dict):
    """
    법제처 API 요청 파라미터 클래스
    생성자에서 필수 파라미터를 생성하고, add_field 메소드로 필요한 파라미터를 추가
    """
    def __init__(self, target, type: RTYPE = "XML"):
        super().__init__()
        self["OC"] = os.getenv("OC", "")  # ex) abc123@email.com => abc123
        self["type"] = type  # XML or HTML
        self["target"] = target  # API 종류

    def add_field(self, key, value):
        self[key] = value
        return self



def law_api_call(url_path, law_api_params):
    """
    법제처 API 요청

    :param url_path: API URL Path (string)
    :param law_api_params: LawApiParams 객체 (dict)
    :return: JSON(dict) or HTML(str)
    """
    url = LAW_API_BASE_URL + url_path
    try:
        response = requests.get(url, params=law_api_params)
        response.raise_for_status()
        return response.json() if law_api_params.get("type", "XML").upper() == "JSON" else response.text
        # import xmltodict
        # if law_api_params.get("type", "XML").upper() == "XML":
        #     return xml_to_json(response.text)
        # else:
        #     return response.text
    except Exception as e:
        print("Error:", e)
        raise

# def xml_to_json(xml_str):
#     """
#     XML을 JSON(dict)으로 변환
# 
#     :param xml_str: XML 문자열
#     :return: dict
#     """
#     return xmltodict.parse(xml_str)

# 사용 예시:
def main():
    params = LawApiParams(target="law", type="XML")
    params.add_field("LM", "산업안전보건기준에관한규칙")
    # result = law_api_call("/LSO/openApi/guideList.do", params)
    result = law_api_call("/DRF/lawService.do", params)
    print(result)


def 안전보건규칙(rtype="XML") -> str | dict:
    """
    산업안전보건기준에 관한 규칙 API 호출
    :param rtype: 응답 형식 (XML, HTML, JSON)
    :return: API 응답
    """
    params = LawApiParams(target="law", type=rtype)
    params.add_field("LM", "산업안전보건기준에관한규칙")
    return law_api_call("/DRF/lawService.do", params)


__all__ = ["LawApiParams"]