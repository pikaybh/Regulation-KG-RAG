import os

from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph, Neo4jVector, GraphCypherQAChain
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()

# 환경변수 설정
NEO4J_PROTOCOL = os.getenv("NEO4J_PROTOCOL", "bolt")
NEO4J_URL = os.getenv("NEO4J_URL", "localhost")
NEO4J_PORT = os.getenv("NEO4J_PORT", "7687")
NEO4J_USER = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "password")

# 1. Neo4jGraph 연결
graph = Neo4jGraph(
    url=f"{NEO4J_PROTOCOL}://{NEO4J_URL}:{NEO4J_PORT}",
    username=NEO4J_USER,
    password=NEO4J_PASS,
)

# (원할 경우) 그래프 스키마 새로고침
graph.refresh_schema()

# 2. 벡터 인덱스 구성 (예: Term, Article 노드 embedding 저장)
embedding = OpenAIEmbeddings(model="text-embedding-3-large")
vector_index = Neo4jVector.from_existing_graph(
    embedding,
    url=f"{NEO4J_PROTOCOL}://{NEO4J_URL}:{NEO4J_PORT}",
    username=NEO4J_USER,
    password=NEO4J_PASS,
    index_name="안전보건규칙",
    node_label="항",
    text_node_properties=["이름","항내용"],
    embedding_node_property="text_embedding_3_large",
)

# 3. Cypher QA 체인 생성
cypher_llm = ChatOpenAI(model="gpt-4.1")
qa_llm = ChatOpenAI(model="gpt-4.1")

qa_chain = GraphCypherQAChain.from_llm(
    graph=graph,
    cypher_llm=cypher_llm,
    qa_llm=qa_llm,
    verbose=True,
    return_direct=False,
    allow_dangerous_requests=True
)

# 4. RAG 수행 함수
def ask_question(question: str):
    # 먼저 벡터 유사도 검색으로 관련 '용어'나 '조문' 찾기
    docs = vector_index.similarity_search(question, k=3)
    context_text = "\n".join([d.page_content for d in docs])
    # prompt = f"관련 용어/정의:\n{context_text}\n\n질문: {question}"
    prompt = f"관련 안전보건규칙:\n{context_text}\n\n질문: {question}"
    # Cypher QA Chain 실행
    output = qa_chain.invoke({"query": prompt})
    return output


PROMPT = """
주어진 내용의 근거가 되는 법령을 찾아주세요.

<내용>
  {}
</내용>
"""

# 테스트
def main():
    question = input("질문을 입력하세요 (예: '폭염작업이 무엇인가요?'): ").strip()
    while not question.lower() == "exit":
        res = ask_question(question)
        # res = qa_chain.invoke({"query": PROMPT.format(question)})
        print("\033[94m\033[3m", res, "\033[0m")
        print("답변:", res.get("result", "답변을 찾을 수 없습니다."))
        question = input("질문을 입력하세요 (예: '폭염작업이 무엇인가요?') (종료하려면 'exit' 입력): ").strip()


if __name__ == "__main__":
    main()
