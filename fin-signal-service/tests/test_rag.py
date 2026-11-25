
# 待實作的資料模型與切塊器（目前尚未實作，預期測試時會出現 ImportError，形成紅燈）
import pytest

from fin_signal.rag import FinancialChunk, FinancialDocumentChunker


def test_financial_chunk_schema():
    """驗證 FinancialChunk 資料契約與必填元數據。"""
    chunk = FinancialChunk(
        chunk_id="2330_2024Q3_p04_c01",
        ticker="2330.TW",
        fiscal_period="2024Q3",
        page_number=4,
        content="本季合併營收達新台幣 7596.9 億元，毛利率為 57.8% 目標達成。",
        token_count=35,
    )
    assert chunk.ticker == "2330.TW"
    assert chunk.page_number == 4
    assert chunk.fiscal_period == "2024Q3"


def test_chunker_preserves_metadata_and_boundaries():
    """驗證切塊器在多頁情境下，精準保留頁碼與期間元數據，且不切斷句子。"""
    pages_data = [
        {
            "page_number": 1,
            "text": (
                "台灣積體電路製造股份有限公司 2024 年第三季財務報告。\n\n"
                "本季營收創歷史新高，先進製程需求維持強勁。"
            ),
        },
        {
            "page_number": 2,
            "text": (
                "第三季資本支出約為新台幣 2070 億元。\n\n"
                "全年資本支出展望維持在 300 億至 320 億美元之間。\n\n"
                "研發費用佔整體營收比重約為 8.5%，持續投入 2 奈米技術開發。"
            ),
        },
    ]

    chunker = FinancialDocumentChunker(
        ticker="2330.TW",
        fiscal_period="2024Q3",
        max_chunk_size=100,
        overlap_size=20,
    )

    chunks = chunker.chunk_pages(pages_data)

    # 1. 確保切出了 Chunk，且沒有空內容
    assert len(chunks) >= 2
    for chunk in chunks:
        assert chunk.ticker == "2330.TW"
        assert chunk.fiscal_period == "2024Q3"
        assert len(chunk.content.strip()) > 0
        assert chunk.page_number in (1, 2)
        assert len(chunk.content) <= 150  # 允許段落邊界微幅彈性，但不應無限制超長

    # 2. 驗證頁碼對應精確性
    page1_chunks = [c for c in chunks if c.page_number == 1]
    page2_chunks = [c for c in chunks if c.page_number == 2]
    assert any("2024 年第三季" in c.content for c in page1_chunks)
    assert any("資本支出" in c.content for c in page2_chunks)


def test_in_memory_vector_store_cosine_similarity():
    """驗證向量資料庫（VectorStore）以餘弦相似度精準檢索語意最相關的 Chunk。"""
    from fin_signal.rag import FinancialVectorStore

    store = FinancialVectorStore()

    # 模擬 2 個 Chunk 的向量特徵（假設 3 維向量）
    # Chunk A：主要談資本支出、建廠 (向量偏向第 1 維度)
    chunk_a = FinancialChunk(
        chunk_id="c_capex",
        ticker="2330.TW",
        fiscal_period="2024Q3",
        page_number=2,
        content="本季資本支出為 2070 億元，用於先進製程擴廠。",
        token_count=20,
    )
    vec_a = [0.9, 0.1, 0.0]

    # Chunk B：主要談配發股利、股東權益 (向量偏向第 2 維度)
    chunk_b = FinancialChunk(
        chunk_id="c_dividend",
        ticker="2330.TW",
        fiscal_period="2024Q3",
        page_number=5,
        content="每股決議配發現金股利 4.0 元。",
        token_count=15,
    )
    vec_b = [0.1, 0.9, 0.0]

    store.add(chunk=chunk_a, embedding=vec_a)
    store.add(chunk=chunk_b, embedding=vec_b)

    # 模擬查詢：「公司蓋廠房擴產投資花多少錢？」（特徵偏向第 1 維度）
    query_vec = [0.85, 0.15, 0.0]

    results = store.similarity_search(query_embedding=query_vec, top_k=1)

    assert len(results) == 1
    top_chunk, score = results[0]
    # 預期第 1 名精確命中資本支出的 chunk_a，且相似度分數接近 1.0
    assert top_chunk.chunk_id == "c_capex"
    assert top_chunk.page_number == 2
    assert score > 0.9


@pytest.mark.asyncio
async def test_financial_rag_qa_with_citation_and_refusal():
    """驗證第 11 課：金融 RAG 問答服務（支援來源引用 Citation 與資料不足拒答機制）。"""
    from fin_signal.rag import (
        FinancialQAResponse,
        FinancialRAGService,
        FinancialVectorStore,
    )

    # 1. 建立測試用向量庫
    store = FinancialVectorStore()
    chunk = FinancialChunk(
        chunk_id="2330_2024Q3_p02_c01",
        ticker="2330.TW",
        fiscal_period="2024Q3",
        page_number=2,
        content="全年資本支出展望維持在 300 億至 320 億美元之間。",
        token_count=25,
    )
    # 模擬該區塊在「資本支出」特徵上的向量
    store.add(chunk=chunk, embedding=[0.95, 0.05, 0.0])

    rag_service = FinancialRAGService(vector_store=store, min_similarity_threshold=0.6)

    # 測試情境 1：資料充足且高度相關（相似向量）
    res_sufficient: FinancialQAResponse = await rag_service.answer_query(
        query="資本支出展望為何？",
        query_embedding=[0.90, 0.10, 0.0],
    )
    assert res_sufficient.is_sufficient is True
    assert "300 億至 320 億美元" in res_sufficient.answer
    assert 2 in res_sufficient.source_pages
    assert len(res_sufficient.citations) >= 1
    assert res_sufficient.citations[0]["page_number"] == 2

    # 測試情境 2：資料庫無相關資料（向量相似度極低）
    res_insufficient: FinancialQAResponse = await rag_service.answer_query(
        query="董事長喜愛的運動是什麼？",
        query_embedding=[0.0, 0.05, 0.95],  # 與資本支出完全無關
    )
    assert res_insufficient.is_sufficient is False
    assert "資料不足" in res_insufficient.answer
    assert len(res_insufficient.source_pages) == 0


