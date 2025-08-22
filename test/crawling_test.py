from crawler import *

print("--- make_query_arxiv 테스트 ---")
# 케이스 1: 기본 (단일 키워드)
keyword_list1 = ["attention"]
field_list1 = ["title"]
operator_list1 = ["AND"]
print("입력:", keyword_list1, field_list1, operator_list1)
query1 = make_query_arxiv(keyword_list1, operator_list1, field_list1)
print("출력:", query1)
print("-" * 10)

# 케이스 2: 기본 (전체 필드)
keyword_list2 = ["language model"]
field_list2 = ["all"]
operator_list2 = ["AND"]
print("입력:", keyword_list2, field_list2, operator_list2)
query2 = make_query_arxiv(keyword_list2, operator_list2, field_list2)
print("출력:", query2)
print("-" * 10)

# 케이스 3: 복합 AND
keyword_list3 = ["large", "language", "model"]
field_list3 = ["title"]
operator_list3 = ["AND"]
print("입력:", keyword_list3, field_list3, operator_list3)
query3 = make_query_arxiv(keyword_list3, operator_list3, field_list3)
print("출력:", query3)
print("-" * 10)

# 케이스 4: 복합 OR
keyword_list4 = ["GAN", "diffusion"]
field_list4 = ["abstract"]
operator_list4 = ["OR"]
print("입력:", keyword_list4, field_list4, operator_list4)
query4 = make_query_arxiv(keyword_list4, operator_list4, field_list4)
print("출력:", query4)
print("-" * 10)

# 케이스 5: 복합 혼합 연산
keyword_list5 = ["robotics", "computer vision", "AI"]
field_list5 = ["all"]
operator_list5 = ["AND", "OR"]
print("입력:", keyword_list5, field_list5, operator_list5)
query5 = make_query_arxiv(keyword_list5, operator_list5, field_list5)
print("출력:", query5)
print("-" * 10)

# 케이스 6: 복합 혼합 필드
keyword_list6 = ["transformer", "google"]
field_list6 = ["title", "abstract"]
operator_list6 = ["AND"]
print("입력:", keyword_list6, field_list6, operator_list6)
query6 = make_query_arxiv(keyword_list6, operator_list6, field_list6)
print("출력:", query6)
print("-" * 10)

# 케이스 7: 엣지 (빈 리스트)
keyword_list7 = []
field_list7 = []
operator_list7 = []
print("입력:", keyword_list7, field_list7, operator_list7)
query7 = make_query_arxiv(keyword_list7, operator_list7, field_list7)
print("출력:", query7)
print("=" * 30)

print("\n--- make_query_openreview_search 테스트 ---")
# 케이스 8: 기본 (단일 키워드)
keyword_list8 = ["ICLR 2024"]
field_list8 = ["venue"]
operator_list8 = []
print("입력:", keyword_list8, field_list8, operator_list8)
query8 = make_query_openreview_search(keyword_list8, operator_list8, field_list8)
print("출력:", query8)
print("-" * 10)

# 케이스 9: 특별 케이스 (all 필드)
keyword_list9 = ["reinforcement", "learning"]
field_list9 = ["all"]
operator_list9 = ["AND"]
print("입력:", keyword_list9, field_list9, operator_list9)
query9 = make_query_openreview_search(keyword_list9, operator_list9, field_list9)
print("출력:", query9)
print("-" * 10)

# 케이스 10: 특별 케이스 (all 필드 + OR)
keyword_list10 = ["BERT", "GPT"]
field_list10 = ["all"]
operator_list10 = ["OR"]
print("입력:", keyword_list10, field_list10, operator_list10)
query10 = make_query_openreview_search(keyword_list10, operator_list10, field_list10)
print("출력:", query10)
print("-" * 10)

# 케이스 11: 복합 AND
keyword_list11 = ["masked", "autoencoder"]
field_list11 = ["title"]
operator_list11 = ["AND"]
print("입력:", keyword_list11, field_list11, operator_list11)
query11 = make_query_openreview_search(keyword_list11, operator_list11, field_list11)
print("출력:", query11)
print("-" * 10)

# 케이스 12: 엣지 (빈 리스트)
keyword_list12 = []
field_list12 = []
operator_list12 = []
print("입력:", keyword_list12, field_list12, operator_list12)
query12 = make_query_openreview_search(keyword_list12, operator_list12, field_list12)
print("출력:", query12)
print("=" * 30)

print("\n--- plan_openreview_v1_queries 테스트 ---")
# 케이스 13: 기본 (단일 키워드)
keyword_list13 = ["deep learning"]
field_list13 = ["title"]
operator_list13 = []
print("입력:", keyword_list13, field_list13, operator_list13)
query13 = plan_openreview_v1_queries(keyword_list13, operator_list13, field_list13)
print("출력:", query13)
print("-" * 10)

# 케이스 14: 복합 AND
keyword_list14 = ["self-supervised", "representation"]
field_list14 = ["title", "abstract"]
operator_list14 = ["AND"]
print("입력:", keyword_list14, field_list14, operator_list14)
query14 = plan_openreview_v1_queries(keyword_list14, operator_list14, field_list14)
print("출력:", query14)
print("-" * 10)

# 케이스 15: 복합 OR
keyword_list15 = ["NeurIPS", "ICML", "ICLR"]
field_list15 = ["venue", "venue", "venue"]
operator_list15 = ["OR", "OR"]
print("입력:", keyword_list15, field_list15, operator_list15)
query15 = plan_openreview_v1_queries(keyword_list15, operator_list15, field_list15)
print("출력:", query15)
print("-" * 10)

# 케이스 16: 복합 혼합 연산
keyword_list16 = ["graph", "GNN", "transformer"]
field_list16 = ["title", "abstract", "title"]
operator_list16 = ["AND", "OR"]
print("입력:", keyword_list16, field_list16, operator_list16)
query16 = plan_openreview_v1_queries(keyword_list16, operator_list16, field_list16)
print("출력:", query16)
print("=" * 30)

print("\n--- make_query_openreview_v1 테스트 ---")
# 케이스 17: 기본 (첫 번째 요소만 사용)
keyword_list17 = ["yann lecun"]
field_list17 = ["authorids"]
operator_list17 = []
print("입력:", keyword_list17, field_list17, operator_list17)
query17 = make_query_openreview_v1(keyword_list17, field_list17)
print("출력:", query17)
print("-" * 10)

# 케이스 18: 무시되는 요소 확인
keyword_list18 = ["A", "B", "C"]
field_list18 = ["title", "abstract"]
operator_list18 = ["AND", "OR"]
print("입력:", keyword_list18, field_list18, operator_list18)
query18 = make_query_openreview_v1(keyword_list18, field_list18)
print("출력:", query18)
print("=" * 30)

print("\n--- make_query_openreview_v2 테스트 ---")
# 케이스 19: 기본 (단일 키워드)
keyword_list19 = ["bayesian"]
field_list19 = ["title"]
operator_list19 = []
print("입력:", keyword_list19, field_list19, operator_list19)
query19 = make_query_openreview_v2(keyword_list19, operator_list19, field_list19)
print("출력:", query19)
print("-" * 10)

# 케이스 20: 복합 (동일 필드, 공통 OR)
keyword_list20 = ["causal", "inference"]
field_list20 = ["abstract"]
operator_list20 = ["OR"]
print("입력:", keyword_list20, field_list20, operator_list20)
query20 = make_query_openreview_v2(keyword_list20, operator_list20, field_list20)
print("출력:", query20)
print("-" * 10)

# 케이스 21: 복합 (동일 필드, 공통 AND)
keyword_list21 = ["federated", "learning"]
field_list21 = ["title"]
operator_list21 = ["AND"]
print("입력:", keyword_list21, field_list21, operator_list21)
query21 = make_query_openreview_v2(keyword_list21, operator_list21, field_list21)
print("출력:", query21)
print("-" * 10)

# 케이스 22: 복합 (다른 필드)
keyword_list22 = ["meta-learning", "few-shot"]
field_list22 = ["title", "abstract"]
operator_list22 = ["AND"]
print("입력:", keyword_list22, field_list22, operator_list22)
query22 = make_query_openreview_v2(keyword_list22, operator_list22, field_list22)
print("출력:", query22)
print("-" * 10)

# 케이스 23: 복합 (혼합 필드, 순차 연산)
keyword_list23 = ["A", "C", "B"]
field_list23 = ["title", "title", "abstract"]
operator_list23 = ["OR", "AND"]
print("입력:", keyword_list23, field_list23, operator_list23)
query23 = make_query_openreview_v2(keyword_list23, operator_list23, field_list23)
print("출력:", query23)
print("=" * 30)

print("\n--- 오류 케이스 테스트 ---")
print("프로그램이 중단되지 않고 오류 메시지를 출력하는지 확인합니다.")

# Case: make_query_arxiv - 연산자 개수 불일치
try:
    print("\n[make_query_arxiv] - 연산자 개수 불일치")
    make_query_arxiv(["A", "B", "C"], ["AND"], ["title"])
except ValueError as e:
    print(f"오류 발생: {e}")

    # Case: make_query_arxiv - 잘못된 필드명
    try:
        print("\n[make_query_arxiv] - 잘못된 필드명")
        make_query_arxiv(["A"], ["AND"], ["author"])
    except ValueError as e:
        print(f"오류 발생: {e}")

    # Case: plan_openreview_v1_queries - AND 내 필드 중복
    try:
        print("\n[plan_openreview_v1_queries] - AND 내 필드 중복")
        plan_openreview_v1_queries(["graph", "network"], ["AND"], ["title", "title"])
    except ValueError as e:
        print(f"오류 발생: {e}")

    # Case: make_query_openreview_v1 - 잘못된 필드명
    try:
        print("\n[make_query_openreview_v1] - 잘못된 필드명")
        make_query_openreview_v1(["A"], ["all"])
    except ValueError as e:
        print(f"오류 발생: {e}")

    # Case: make_query_openreview_v2 - 연산자 없음
    try:
        print("\n[make_query_openreview_v2] - 연산자 없음")
        make_query_openreview_v2(["A", "B"], [], ["title"])
    except ValueError as e:
        print(f"오류 발생: {e}")

    print("\n--- 모든 테스트 완료 ---")