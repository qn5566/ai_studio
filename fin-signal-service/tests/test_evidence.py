import json
from pathlib import Path

import pytest

from fin_signal.evidence import validate_target_price_evidence
from fin_signal.schemas import NewsAnalysisRequest, SignalAnalysisResponse

CASES = json.loads(
    (Path(__file__).parents[1] / "examples" / "target_price_cases.json").read_text(
        encoding="utf-8"
    )
)


def make_result(price, evidence):
    # 模擬模型 JSON；這裡驗證程式邊界，不測真實模型的準確率。
    return SignalAnalysisResponse.model_validate_json(
        json.dumps(
            {
                "request_id": "test",
                "ticker": "2330.TW",
                "sentiment": "NEUTRAL",
                "event_category": "GENERAL",
                "signal_score": 0,
                "confidence": 0.5,
                "rationale": "測試用回應",
                "latency_ms": 0,
                "target_price": price,
                "target_price_evidence": evidence,
            }
        )
    )


@pytest.mark.parametrize("case", CASES, ids=[case["name"] for case in CASES])
def test_expected_extraction_has_valid_evidence(case):
    request = NewsAnalysisRequest(
        ticker="2330.TW", headline=case["headline"], content=case["content"]
    )
    result = make_result(case["expected_target_price"], case["example_evidence"])
    validate_target_price_evidence(result, request)


@pytest.mark.parametrize(
    ("case_index", "price", "evidence"),
    [
        (0, 1400, None),  # 有數字卻沒有證據
        (1, 1400, "目標價調升至 1400.0 元"),  # 捏造原文
        (1, 1400, "營收達 1400 億元"),  # 原文存在但只是營收
        (2, 1000, "目前股價為 1000 元"),  # 原文存在但只是股價
        (0, 1500, "目標價調升至 1400.0 元"),  # 金額不一致
        (0, None, "目標價調升至 1400.0 元"),  # 空值與證據不一致
    ],
)
def test_rejects_unsupported_price(case_index, price, evidence):
    case = CASES[case_index]
    request = NewsAnalysisRequest(
        ticker="2330.TW", headline=case["headline"], content=case["content"]
    )
    result = make_result(price, evidence)
    with pytest.raises(ValueError):
        validate_target_price_evidence(result, request)
