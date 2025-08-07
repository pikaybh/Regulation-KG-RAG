import re

def clean_label(text: str) -> str:
    # 1. 마침표, 괄호 등 불필요한 문자 제거 (예: "가.", "1.", "1)", "1 )")
    text = re.sub(r'[\.\)\s]+$', '', text)
    
    # 2. 원형 숫자(①~⑳)를 일반 숫자로 변환
    circled_numbers = {
        '①': '1', '②': '2', '③': '3', '④': '4', '⑤': '5',
        '⑥': '6', '⑦': '7', '⑧': '8', '⑨': '9', '⑩': '10',
        '⑪': '11', '⑫': '12', '⑬': '13', '⑭': '14', '⑮': '15',
        '⑯': '16', '⑰': '17', '⑱': '18', '⑲': '19', '⑳': '20'
    }
    if text in circled_numbers:
        text = circled_numbers[text]
        
    return text


def remove_leading_label(text: str) -> str:
    # 앞쪽에 붙은 번호, 한글, 원형숫자 + 마침표/괄호/공백을 제거
    # 예: "가. ", "1. ", "1)", "① " 등
    text = re.sub(r'^\s*([가-힣]|[0-9]{1,2}|[①-⑳])[\.\)\s]+', '', text)
    # 원형 숫자만 있는 경우도 제거
    text = re.sub(r'^\s*[①-⑳]\s*', '', text)
    return text.strip()


def clean_item(item):
    # '목번호'와 '목내용' 모두 처리
    new_item = dict(item)  # 복사
    new_item["목번호"] = clean_label(item["목번호"])  # 이전에 만든 함수 사용
    new_item["목내용"] = remove_leading_label(item["목내용"])
    return new_item


def main():
    # 예시
    print(clean_label("가."))   # "가"
    print(clean_label("1."))   # "1"
    print(clean_label("①"))    # "1"
    print(clean_label("2 )"))  # "2"
    print(clean_label("⑩"))    # "10"
    
    # 예시 데이터
    item = {
        "목번호": "가.",
        "목내용": "    가. 제526조에 따른 배기관과 제539조제2항에 따른 통화장치"
    }

    cleaned_item = clean_item(item)
    print(cleaned_item)
    # 출력: {'목번호': '가', '목내용': '제526조에 따른 배기관과 제539조제2항에 따른 통화장치'}


__all__ = ['clean_label', 'remove_leading_label']