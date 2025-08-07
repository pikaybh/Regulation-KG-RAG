
# Knowledge Graph based Retrieval Augmented Generation for Risk Assessment Regulation in Korea

이 프로젝트는 대한민국 산업안전보건 규정의 위험성 평가를 위한 RAG(Retrieval Augmented Generation) 시스템입니다. Neo4j 기반의 지식 그래프와 OpenAI 임베딩을 활용하여 규정 질의에 대해 정확하고 근거 있는 답변을 제공합니다.

## 주요 기능
- 산업안전보건 규정 JSON 데이터로부터 Neo4j 지식 그래프 구축
- 각 조문/항/호/목 노드에 OpenAI 임베딩 벡터 저장
- LangChain 기반 벡터 검색 및 Cypher QA 체인으로 RAG 구현
- 자연어 질의에 대해 관련 규정 근거와 함께 답변 생성

## 설치 및 실행 방법
1. Python 3.11+ 환경 준비
2. Neo4j 서버 설치 및 실행 (기본: bolt://localhost:7687)
3. 필요한 패키지 설치 (uv 사용, pyproject.toml 기반)
   ```bash
   uv venv .venv
   uv pip install --system
   ```
4. 환경변수 설정 (.env 파일)
   ```env
   NEO4J_PROTOCOL=bolt
   NEO4J_URL=localhost
   NEO4J_PORT=7687
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=비밀번호
   OPENAI_API_KEY=발급받은키
   ```
5. 데이터 임포트 및 임베딩 생성
   ```bash
   uv pip run python 2. VectorDB Embedding.py
   ```
6. 질의 테스트
   ```bash
   uv pip run python 3. test.py
   ```

## 사용 예시
```
질문을 입력하세요 (예: '폭염작업이 무엇인가요?'): 추락 방지망은 어떻게 설치해야 해?
답변: 추락 방지망은 ...
```

## 폴더 구조
```
├── data.json                # 산업안전보건 규정 데이터
├── 2. VectorDB Embedding.py # Neo4j 그래프 및 임베딩 생성
├── 3. test.py               # RAG 질의 테스트
├── modules/                 # 서브모듈 및 타입 정의
├── README.md
└── ...
```

## 기술 스택
- Python, Neo4j, LangChain, OpenAI API, py2neo


