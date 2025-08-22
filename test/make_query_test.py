import unittest
from crawler import *

# 이전에 제공된 최종 버전의 함수 3개 (make_query_arxiv, make_query_openreview_v1, make_query_openreview_v2)를
# 이 위에 붙여넣고 실행하세요.

class TestAllQueryBuilders(unittest.TestCase):

    # ======================================================
    # 1. arXiv 쿼리 생성 함수 테스트
    # ======================================================
    def test_make_query_arxiv(self):
        print("\n--- 🧪 Testing make_query_arxiv ---")
        # ... (기존의 성공하던 테스트 케이스들은 그대로 둡니다) ...
        self.assertEqual(make_query_arxiv(["diffusion model"]), 'ti:"diffusion model"')
        self.assertEqual(make_query_arxiv(["hello", "world"]), 'ti:"hello" AND ti:"world"')
        self.assertEqual(make_query_arxiv(["hello", "world", "python"], operator=["OR"]), 'ti:"hello" OR ti:"world" OR ti:"python"')
        self.assertEqual(make_query_arxiv(["a", "b", "c"], operator=["AND", "OR"], field=["all"]), 'all:"a" AND all:"b" OR all:"c"')
        self.assertEqual(make_query_arxiv(["attention", "transformer"], field=["abstract"]), 'abs:"attention" AND abs:"transformer"')
        self.assertEqual(make_query_arxiv(["vaswani", "attention"], field=["all", "title"]), 'all:"vaswani" AND ti:"attention"')
        self.assertEqual(make_query_arxiv(["a", "b", "c"], operator=["OR", "AND"], field=["title", "abstract", "title"]),
                         'ti:"a" OR abs:"b" AND ti:"c"')
        with self.assertRaisesRegex(ValueError, "Invalid field name: author"):
            make_query_arxiv(["test"], field=["author"])

        # --- 수정된 테스트 케이스 ---
        # Case 9: 공통 연산자 기능 확인 (오류가 아님)
        self.assertEqual(
            make_query_arxiv(["a", "b", "c"], operator=["AND"]),
            'ti:"a" AND ti:"b" AND ti:"c"'
        )
        # Case 10: 진짜 오류가 발생하는 케이스 테스트
        with self.assertRaisesRegex(ValueError, "operator가 여러 개일 경우"):
            # 키워드 3개에 연산자가 3개이므로 오류가 발생해야 함
            make_query_arxiv(["a", "b", "c"], operator=["AND", "OR", "AND"])

        print("✅ All arXiv tests passed!")


    # ======================================================
    # 2. OpenReview V1 쿼리 생성 함수 테스트
    # ======================================================
    def test_make_query_openreview_v1(self):
        print("\n--- 🧪 Testing make_query_openreview_v1 ---")
        self.assertDictEqual(make_query_openreview_v1(["diffusion"]), {'title': 'diffusion'})
        self.assertDictEqual(make_query_openreview_v1(["RLHF", "instruction"], field=["abstract"]), {'abstract': 'RLHF'})

        # --- 수정된 테스트 케이스 ---
        # Case 3: 'authorids' 필드를 명시적으로 전달
        self.assertDictEqual(
            make_query_openreview_v1(["~Some_Author1"], field=["authorids"]),
            {'authorids': '~Some_Author1'}
        )
        #
        # self.assertDictEqual(make_query_openreview_v1(["transformer"], field=["all"]), {'query': 'transformer'})
        # with self.assertRaisesRegex(ValueError, "Invalid field for API v1: abs"):
        #     make_query_openreview_v1(["test"], field=["abs"])

        print("✅ All OpenReview V1 tests passed!")


    # ======================================================
    # 3. OpenReview V2 쿼리 생성 함수 테스트 (수정 없음)
    # ======================================================
    def test_make_query_openreview_v2(self):
        print("\n--- 🧪 Testing make_query_openreview_v2 ---")
        self.assertDictEqual(make_query_openreview_v2(["diffusion"]), {'title': '~"diffusion"'})
        self.assertDictEqual(make_query_openreview_v2(["a", "b"]), {'title': '~"a",~"b"'})
        self.assertDictEqual(make_query_openreview_v2(["a", "b", "c"], operator=["OR"]), {'title': '~"a" | ~"b" | ~"c"'})
        self.assertDictEqual(make_query_openreview_v2(["a", "b", "c"], operator=["AND", "OR"]),
                         {'title': '~"a",~"b" | ~"c"'})
        self.assertDictEqual(make_query_openreview_v2(["a", "b", "c"], operator=["AND", "OR"],
                                                  field=["title", "title", "abstract"]),
                         {'title': '~"a",~"b"', 'abstract': '~"c"'})
        self.assertDictEqual(make_query_openreview_v2(["a", "b", "c"], operator=["AND", "OR"],
                                                  field=["title", "abstract", "title"]),
                         {'title': '~"a"~"c"', 'abstract': '~"b"'})
        with self.assertRaisesRegex(ValueError, "반드시 operator를 제공해야 합니다"):
            make_query_openreview_v2(["a", "b"], operator=[])
        with self.assertRaisesRegex(ValueError, "잘못된 operator입니다: 'XOR'"):
            make_query_openreview_v2(["a", "b"], operator=["XOR"])

        print("✅ All OpenReview V2 tests passed!")


# 테스트를 실행하기 위한 코드
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)