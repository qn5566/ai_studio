from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class FinancialChunk(BaseModel):
    """金融文件檢索切塊（攜帶完整來源追溯元數據）。"""

    model_config = ConfigDict(str_strip_whitespace=True)

    chunk_id: str = Field(..., description="唯一的區塊識別碼，例如 2330_2024Q3_p04_c01")
    ticker: str = Field(..., description="股票代號")
    fiscal_period: str = Field(..., description="財報所屬期間，例如 2024Q3")
    page_number: int = Field(..., ge=1, description="原始 PDF 頁碼（從 1 起算）")
    content: str = Field(..., min_length=1, description="該區塊的文字內文")
    token_count: int = Field(..., ge=0, description="估算的 Token 或字元長度")


class FinancialDocumentChunker:
    """金融財報專用切塊器。

    特點：
    1. 頁碼獨立切分（絕不跨頁混合，確保溯源精確性）
    2. 優先按段落（Paragraph）切分，保留語意完整性
    3. 支援滑動重疊（Overlap），避免邊界資訊遺失
    """

    def __init__(
        self,
        ticker: str,
        fiscal_period: str,
        max_chunk_size: int = 500,
        overlap_size: int = 50,
    ) -> None:
        self.ticker = ticker.upper()
        self.fiscal_period = fiscal_period.upper()
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size

    def chunk_pages(self, pages: list[dict[str, str | int]]) -> list[FinancialChunk]:
        """將多頁財報文字切分為帶有元數據的 FinancialChunk 清單。

        :param pages: 每頁資料字典，格式如 [{'page_number': 1, 'text': '...'}]
        """
        all_chunks: list[FinancialChunk] = []

        for page in pages:
            page_num = int(page["page_number"])
            text = str(page["text"]).strip()
            if not text:
                continue

            page_chunks = self._chunk_single_page(text, page_num)
            all_chunks.extend(page_chunks)

        return all_chunks

    def _chunk_single_page(self, text: str, page_number: int) -> list[FinancialChunk]:
        """對單一頁面進行段落優先的切分。"""
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks: list[FinancialChunk] = []

        current_text = ""
        chunk_idx = 1

        for para in paragraphs:
            if current_text and (len(current_text) + len(para) > self.max_chunk_size):
                p_str = f"p{page_number:02d}_c{chunk_idx:02d}"
                chunk_id = f"{self.ticker}_{self.fiscal_period}_{p_str}"
                chunks.append(
                    FinancialChunk(
                        chunk_id=chunk_id,
                        ticker=self.ticker,
                        fiscal_period=self.fiscal_period,
                        page_number=page_number,
                        content=current_text,
                        token_count=len(current_text),
                    )
                )
                chunk_idx += 1
                # 保留 overlap（取尾段）以銜接語意
                if self.overlap_size > 0 and len(current_text) > self.overlap_size:
                    current_text = current_text[-self.overlap_size :] + "\n" + para
                else:
                    current_text = para
            else:
                if current_text:
                    current_text += "\n\n" + para
                else:
                    current_text = para

        # 處理剩餘的最後一段內容
        if current_text:
            p_str = f"p{page_number:02d}_c{chunk_idx:02d}"
            chunk_id = f"{self.ticker}_{self.fiscal_period}_{p_str}"
            chunks.append(
                FinancialChunk(
                    chunk_id=chunk_id,
                    ticker=self.ticker,
                    fiscal_period=self.fiscal_period,
                    page_number=page_number,
                    content=current_text,
                    token_count=len(current_text),
                )
            )

        return chunks


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """計算兩向量的餘弦相似度 (Cosine Similarity)。

    公式: (v1 · v2) / (||v1|| * ||v2||)
    """
    if len(v1) != len(v2) or not v1:
        return 0.0

    dot_product = sum(a * b for a, b in zip(v1, v2, strict=False))
    norm_v1 = sum(a * a for a in v1) ** 0.5
    norm_v2 = sum(b * b for b in v2) ** 0.5

    if norm_v1 == 0.0 or norm_v2 == 0.0:
        return 0.0

    return dot_product / (norm_v1 * norm_v2)


class FinancialVectorStore:
    """輕量記憶體型金融向量儲存與檢索庫。

    負責儲存 FinancialChunk 及其高維度特徵向量，支援 Top-K 語意相似度檢索。
    """

    def __init__(self) -> None:
        self._entries: list[tuple[FinancialChunk, list[float]]] = []

    def add(self, chunk: FinancialChunk, embedding: list[float]) -> None:
        """新增一個金融區塊與其對應的 Embedding 向量。"""
        self._entries.append((chunk, embedding))

    def similarity_search(
        self, query_embedding: list[float], top_k: int = 3
    ) -> list[tuple[FinancialChunk, float]]:
        """給定查詢向量，以餘弦相似度由高到低回傳最相關的 (Chunk, 相似度分數)。"""
        scored_results: list[tuple[FinancialChunk, float]] = []

        for chunk, emb in self._entries:
            sim = cosine_similarity(query_embedding, emb)
            scored_results.append((chunk, sim))

        # 依照相似度由高至低排序
        scored_results.sort(key=lambda x: x[1], reverse=True)
        return scored_results[:top_k]


class FinancialQAResponse(BaseModel):
    """金融 RAG 結構化問答結果。"""

    model_config = ConfigDict(str_strip_whitespace=True)

    answer: str = Field(..., description="產生的回答內容")
    is_sufficient: bool = Field(..., description="現有財報資料是否足夠回答該問題")
    source_pages: list[int] = Field(
        default_factory=list, description="引用的來源頁碼清單"
    )
    citations: list[dict[str, Any]] = Field(
        default_factory=list, description="詳細引文片段與對應頁碼"
    )


class FinancialRAGService:
    """金融財報 RAG 問答服務（具備來源引用與幻覺拒答防護機制）。"""

    def __init__(
        self,
        vector_store: FinancialVectorStore,
        min_similarity_threshold: float = 0.6,
    ) -> None:
        self.vector_store = vector_store
        self.min_similarity_threshold = min_similarity_threshold

    async def answer_query(
        self,
        query: str,
        query_embedding: list[float],
        top_k: int = 2,
    ) -> FinancialQAResponse:
        """非同步檢索相關財報段落並生成帶有 Citations 的回答。"""
        # 1. 向量相似度檢索
        retrieved_results = self.vector_store.similarity_search(
            query_embedding=query_embedding, top_k=top_k
        )

        # 2. 信心度門檻檢查（Confidence Guard）
        if (
            not retrieved_results
            or retrieved_results[0][1] < self.min_similarity_threshold
        ):
            return FinancialQAResponse(
                answer="根據現有財報資料，未能檢索到相關資訊，資料不足無法回答。",
                is_sufficient=False,
                source_pages=[],
                citations=[],
            )

        # 3. 組合引用與回答
        relevant_chunks = [
            chunk
            for chunk, score in retrieved_results
            if score >= self.min_similarity_threshold
        ]

        citations: list[dict[str, Any]] = []
        source_pages: set[int] = set()

        for c in relevant_chunks:
            source_pages.add(c.page_number)
            citations.append({
                "chunk_id": c.chunk_id,
                "page_number": c.page_number,
                "snippet": c.content,
            })

        # 組合標準回答格式（附帶精準引用）
        joined_context = " ".join([c.content for c in relevant_chunks])
        answer = f"根據財報內容：{joined_context}"

        return FinancialQAResponse(
            answer=answer,
            is_sufficient=True,
            source_pages=sorted(source_pages),
            citations=citations,
        )


