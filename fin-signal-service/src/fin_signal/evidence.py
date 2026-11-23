"""目標價的基本來源檢查；公司、幣別和語意仍需額外評估。"""

import math
import re

from fin_signal.schemas import NewsAnalysisRequest, SignalAnalysisResponse


def validate_target_price_evidence(
    result: SignalAnalysisResponse, request: NewsAnalysisRequest
) -> None:
    """不通過時拒絕結果，避免把沒有來源的數字當成有效分析。"""
    price = result.target_price
    evidence = result.target_price_evidence
    if price is None:
        if evidence is not None:
            raise ValueError("沒有目標價時，原文證據必須為 null")
        return
    if not evidence or not evidence.strip():
        raise ValueError("有目標價時必須提供原文證據")
    if not any(evidence in text for text in (request.headline, request.content)):
        raise ValueError("目標價證據不存在於新聞原文")
    # 僅檢查明確的阿拉伯數字報價；其他寫法先交由人工確認。
    matches = re.finditer(
        r"(?:目標價|target price)\s*(?:調升至|調降至|上調至|下調至|為|至|"
        r"to|of|is)?\s*[:：$]?\s*(\d+(?:,\d{3})*(?:\.\d+)?)(?![\d.])",
        evidence,
        flags=re.IGNORECASE,
    )
    amounts = [float(match.group(1).replace(",", "")) for match in matches]
    if not math.isfinite(price) or price not in amounts:
        raise ValueError("原文證據未包含與結果一致的明確目標價，需人工確認")
