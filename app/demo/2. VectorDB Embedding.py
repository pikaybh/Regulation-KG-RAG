import json

from dotenv import load_dotenv
from py2neo import Graph, Node, Relationship
from langchain_openai import OpenAIEmbeddings
from tqdm import tqdm

from app.utils import clean_label, remove_leading_label



load_dotenv()

# OpenAI 임베딩 인스턴스 생성
embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")

HIERARCHY = {
    '조문': ['항'],
    '항': ['호'],
    '호': ['목'],
    '목': []
}


def _get_name_from_parent_info(data, number_key, label: str, parent_info: dict, cur_no: str) -> tuple[str, str]:
    """상위 계층 정보로부터 이름을 생성
    
    Args:
        data (dict): 현재 노드의 데이터
        number_key (str): 현재 노드의 번호 키
        label (str): 현재 노드의 레이블
        parent_info (dict): 상위 계층의 번호 정보
        cur_no (str): 현재 노드의 번호
        
    Returns:
        tuple[str, str]: 생성된 이름과 현재 번호
    """

    # 상위 계층 번호 추출
    jomun_no = parent_info.get('조문번호') or (data['조문번호'] if '조문번호' in data else None)
    hang_no = parent_info.get('항번호')
    ho_no = parent_info.get('호번호')
    # mok_no = parent_info.get('목번호')

    # 현재 계층 번호
    cur_no = clean_label(data[number_key])

    # 이름 조합
    if label == '조문':
        name = f"제{cur_no}조"
    elif label == '항':
        name = f"제{jomun_no}조 {cur_no}항" if jomun_no else f"{cur_no}항"
    elif label == '호':
        name = f"제{jomun_no}조 {hang_no}항 {cur_no}호" if jomun_no and hang_no else f"{cur_no}호"
    elif label == '목':
        name = f"제{jomun_no}조 {hang_no}항 {ho_no}호 {cur_no}목" if jomun_no and hang_no and ho_no else f"{cur_no}목"
    else:
        name = str(cur_no)

    return name, cur_no


def create_jomun_node(data: dict, parent_info=None) -> Node | None:
    """조문 노드를 생성 (번호가 있을 때만 merge용으로)
    Args:
        data (dict): 노드에 저장할 데이터, 번호와 내용이 포함되어야 함
        parent_info (dict): 상위 계층의 번호 정보
    Returns:
        Node: 생성된 노드 객체, 번호가 없으면 None 반환
    """
    if parent_info is None:
        parent_info = {}
    number_key = "조문번호"
    content_key = "조문내용"
    title_key = "조문제목"
    isit_key = "조문여부"
    if number_key not in data or not data[number_key]:
        return None  # 번호가 없으면 None 반환
    name, cur_no = _get_name_from_parent_info(
        data, number_key, "조문", parent_info,
        clean_label(data[number_key])
    )

    # cur_no가 None이거나 빈 문자열이면 노드 생성하지 않음
    if not cur_no:
        return None
    node_kwargs = {
        "이름": name,
        "번호": cur_no,
        number_key: data[number_key],
        isit_key: data[isit_key]
    }
    # 내용/제목 저장
    content_val = None
    if content_key in data and data[content_key]:
        value = data[content_key]
        if isinstance(value, (list, dict, tuple)):
            value = str(value)
        node_kwargs[content_key] = remove_leading_label(value)
        content_val = node_kwargs[content_key]
    if title_key in data and data[title_key]:
        value = data[title_key]
        if isinstance(value, (list, dict, tuple)):
            value = str(value)
        node_kwargs[title_key] = remove_leading_label(value)
    # 임베딩 생성: 조문여부가 '조문'이면 조문제목, 아니면 조문내용
    embed_text = None
    if data.get(isit_key) == "조문" and title_key in data and data[title_key]:
        embed_text = remove_leading_label(data[title_key])
    elif content_val:
        embed_text = content_val
    if embed_text:
        node_kwargs["내용"] = embed_text
        node_kwargs["text_embedding_3_large"] = embedding_model.embed_query(embed_text)
    return Node("조문", **node_kwargs)


def create_node_with_content(label: str, data: dict | list, parent_info=None):
    """해당 계층의 노드를 생성 (번호가 있을 때만 merge용으로)
    Args:
        label (str): 노드의 레이블
        data (dict | list): 노드에 저장할 데이터, 번호와 내용이 포함되어야 함
        parent_info (dict): 상위 계층의 번호 정보
    Returns:
        Node: 생성된 노드 객체, 번호가 없으면 None 반환
    """
    if parent_info is None:
        parent_info = {}

    number_key = f"{label}번호"
    content_key = f"{label}내용"

    if number_key not in data or not data[number_key]:
        return None  # 번호가 없으면 None 반환

    name, cur_no = _get_name_from_parent_info(
        data, number_key, label, parent_info,
        clean_label(data[number_key])
    )

    # cur_no가 None이거나 빈 문자열이면 노드 생성하지 않음
    if not cur_no:
        return None

    node_kwargs = {
        "이름": name,
        "번호": cur_no,
        number_key: data[number_key]
    }
    embed_text = None
    if content_key in data and data[content_key]:
        value = data[content_key]
        if isinstance(value, (list, dict, tuple)):
            value = str(value)
        node_kwargs[content_key] = value
        node_kwargs["내용"] = remove_leading_label(value)
        embed_text = node_kwargs[content_key]
    # 조문이 아닌 경우만: label내용 임베딩
    if embed_text:
        node_kwargs["text_embedding_3_large"] = embedding_model.embed_query(embed_text)
    return Node(label, **node_kwargs)


def _get_info(label: str, regulation: dict, info: dict) -> dict:
    if label == '조문':
        info['조문번호'] = clean_label(regulation.get('조문번호', ''))
    elif label == '항':
        info['항번호'] = clean_label(regulation.get('항번호', ''))
    elif label == '호':
        info['호번호'] = clean_label(regulation.get('호번호', ''))
    elif label == '목':
        info['목번호'] = clean_label(regulation.get('목번호', ''))
    return info


def processor(parent_node, regulation_data, label, parent_info=None):
    """주어진 법령 데이터를 처리하여 Neo4j에 저장
    Args:
        parent_node (Node): 부모 노드 객체
        regulation_data (list): 법령 데이터 리스트
        label (str): 노드의 레이블
        parent_info (dict): 상위 계층의 번호 정보
    """
    if parent_info is None:
        parent_info = {}
    for regulation in regulation_data:
        if not isinstance(regulation, dict):
            continue
        # 상위 정보 갱신
        info = parent_info.copy()
        info = _get_info(label, regulation, info)
        regulation_node = create_node_with_content(label, regulation, info)
        if regulation_node:
            primary_key = f"이름"
            graph.merge(regulation_node, label, primary_key)
            graph.merge(Relationship(parent_node, '부모', regulation_node))
            graph.merge(Relationship(regulation_node, '자식', parent_node))
            inner_labels = HIERARCHY.get(label, [])
            for child_label in inner_labels:
                if child_label in regulation and regulation[child_label]:
                    processor(regulation_node, regulation[child_label], child_label, info)


def process_entry_point(regulation_data, label):
    """주어진 법령 데이터를 처리하여 Neo4j에 저장
    Args:
        regulation_data (list): 법령 데이터 리스트
        label (str): 노드의 레이블
    """
    for regulation in tqdm(regulation_data):
        if not isinstance(regulation, dict):
            continue
        info = _get_info(label, regulation, {})
        regulation_node = create_jomun_node(regulation, info)
        if regulation_node:
            primary_key = f"{label}번호"
            graph.merge(regulation_node, label, primary_key)
            inner_labels = HIERARCHY.get(label, [])
            for child_label in inner_labels:
                if child_label in regulation and regulation[child_label]:
                    processor(regulation_node, regulation[child_label], child_label, info)


# Neo4j 연결
graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))

# JSON 파일 로딩
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

jomun_list = data["법령"]["조문"]["조문단위"]
process_entry_point(jomun_list, '조문')

print("조문-항-호-목 전체 구조가 입력되었습니다.")
