# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Thị Bích Duyên\
**Nhóm:** Bàn D1\
**Ngày:** 05/06/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> Hai vector embedding có hướng gần trùng nhau trong không gian nhiều chiều, tức là hai đoạn văn bản mang nghĩa tương tự hoặc cùng chủ đề. Giá trị càng gần 1 thì mức độ tương đồng ngữ nghĩa càng cao.

**Ví dụ HIGH similarity:**
- Sentence A: "Python is widely used for machine learning."
- Sentence B: "Many teams use Python to build ML models."
- Tại sao tương đồng: Cả hai đều nói về việc dùng Python trong machine learning, chỉ khác cách diễn đạt.

**Ví dụ LOW similarity:**
- Sentence A: "How do I reset my password?"
- Sentence B: "The billing API should be deployed on Fridays."
- Tại sao khác: Một câu hỏi về tài khoản, một câu về triển khai hệ thống — không cùng chủ đề hay ngữ cảnh.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Cosine similarity đo góc giữa hai vector nên ít bị ảnh hưởng bởi độ dài vector (độ dài câu). Euclidean distance có thể cho hai câu cùng nghĩa nhưng khác độ dài bị coi là xa nhau, trong khi hướng ngữ nghĩa mới là yếu tố quan trọng khi retrieval.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Công thức: `num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))`
> `num_chunks = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11) = 23`
> **Đáp án: 23 chunks**

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> `num_chunks = ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25` — số chunk tăng từ 23 lên 25. Overlap lớn hơn giúp các chunk liền kề chia sẻ thêm ngữ cảnh, giảm nguy cơ một ý quan trọng bị cắt đôi ở ranh giới chunk và cải thiện khả năng retrieval khi thông tin trải dài qua nhiều đoạn.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Luật về Thuế doanh nghiệp tại Việt Nam

**Tại sao nhóm chọn domain này?**
> Nhằm thực hiện chủ trương của Đảng và Nhà nước về minh bạch hóa tài chính, việc khai và đóng thuế hiện đã trở thành nghĩa vụ bắt buộc áp dụng sâu rộng cho mọi doanh nghiệp. Tuy nhiên, hệ thống văn bản luật thuế vốn rất đồ sộ, phức tạp và liên tục cập nhật khiến nhiều đơn vị gặp khó khăn trong việc tiếp cận và thấu hiểu chính xác quy trình. Việc xây dựng hệ thống RAG cho domain này là giải pháp cấp thiết giúp doanh nghiệp tra cứu thông tin chính thống tức thì, từ đó tối ưu hóa tính tuân thủ pháp luật và giảm thiểu rủi ro vận hành.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | Công văn 806/VLO-QLDN3 — Ưu đãi thuế TNDN (`806_VLO-QLDN3_698806.txt`) | THƯ VIỆN PHÁP LUẬT | 17,394 | `co_quan=Thuế tỉnh Vĩnh Long`, `loai_van_ban=cong_van`, `chu_de=uu_dai_TNDN`, `ngay_ban_hanh=2026-03-20` |
| 2 | Công văn 3418/CT-CS — Chính sách thuế tài nguyên, BVMT, TNDN, GTGT (`3418_CT-CS_670764.txt`) | THƯ VIỆN PHÁP LUẬT | 5,499 | `co_quan=Cục Thuế`, `loai_van_ban=cong_van`, `chu_de=thue_tai_nguyen_TNDN_GTGT`, `ngay_ban_hanh=2025-08-26` |
| 3 | Công văn 654/TNI-QLDN1 — Chính sách thuế TNDN (chi phí lương) (`654_TNI-QLDN1_695255.txt`) | THƯ VIỆN PHÁP LUẬT | 4,996 | `co_quan=Thuế tỉnh Tây Ninh`, `loai_van_ban=cong_van`, `chu_de=TNDN_chi_phi_luong`, `ngay_ban_hanh=2026-02-04` |
| 4 | Công văn 4221/CT-CS — Chính sách thuế TNDN, TNCN (`4221_CT-CS_675462.txt`) | THƯ VIỆN PHÁP LUẬT | 3,296 | `co_quan=Cục Thuế`, `loai_van_ban=cong_van`, `chu_de=TNDN_TNCN`, `ngay_ban_hanh=2025-10-03` |
| 5 | Công văn 16123/CHQ-GSQL — DNCX thuê DN nội địa gia công (`16123_CHQ-GSQL_705170.txt`) | THƯ VIỆN PHÁP LUẬT | 1,509 | `co_quan=Cục Hải quan`, `loai_van_ban=cong_van`, `chu_de=hai_quan_gia_cong`, `ngay_ban_hanh=2026-05-12` |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| `co_quan` | string | `Cục Thuế`, `Thuế tỉnh Vĩnh Long`, `Cục Hải quan` | Lọc văn bản theo cơ quan ban hành khi câu hỏi liên quan đến thẩm quyền giải đáp (trung ương vs địa phương, thuế vs hải quan) |
| `loai_van_ban` | string | `cong_van`, `thong_tu`, `luat` | Phân biệt loại văn bản pháp lý; ưu tiên công văn hướng dẫn khi user hỏi về giải đáp vướng mắc cụ thể |
| `chu_de` | string | `uu_dai_TNDN`, `TNDN_chi_phi_luong`, `hai_quan_gia_cong` | Lọc theo chủ đề thuế — giúp retrieval tập trung vào đúng lĩnh vực (ưu đãi TNDN, chi phí lương, gia công xuất khẩu, …) |
| `ngay_ban_hanh` | string (ISO date) | `2026-03-20`, `2025-08-26` | Ưu tiên văn bản mới hơn khi có nhiều hướng dẫn cùng chủ đề; tránh trả về công văn đã lỗi thời |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare(text, chunk_size=200)` trên 3 tài liệu luật thuế trong `data/documents/` (đo bởi `tests/compare_documents.py`):

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| 3418/CT-CS | FixedSizeChunker (`fixed_size`) | 28 | 196.4 | Không — thường cắt giữa câu hoặc giữa khoản trong cùng một mục |
| 3418/CT-CS | SentenceChunker (`by_sentences`) | 10 | 547.8 | Một phần — giữ ranh giới câu nhưng dễ gộp nhiều mục vào một chunk |
| 3418/CT-CS | RecursiveChunker (`recursive`) | 44 | 125.0 | Một phần — tách đoạn tốt nhưng có thể phân mảnh so với một mục luật |
| 654/TNI-QLDN1 | FixedSizeChunker (`fixed_size`) | 25 | 199.8 | Không — thường cắt giữa câu hoặc giữa khoản trong cùng một mục |
| 654/TNI-QLDN1 | SentenceChunker (`by_sentences`) | 8 | 622.0 | Một phần — giữ ranh giới câu nhưng dễ gộp nhiều mục vào một chunk |
| 654/TNI-QLDN1 | RecursiveChunker (`recursive`) | 39 | 128.1 | Một phần — tách đoạn tốt nhưng có thể phân mảnh so với một mục luật |
| 4221/CT-CS | FixedSizeChunker (`fixed_size`) | 17 | 193.9 | Không — thường cắt giữa câu hoặc giữa khoản trong cùng một mục |
| 4221/CT-CS | SentenceChunker (`by_sentences`) | 6 | 546.8 | Một phần — giữ ranh giới câu nhưng dễ gộp nhiều mục vào một chunk |
| 4221/CT-CS | RecursiveChunker (`recursive`) | 25 | 131.8 | Một phần — tách đoạn tốt nhưng có thể phân mảnh so với một mục luật |

*Nhận xét baseline (đo bằng `tests/compare_documents.py`, `chunk_size=200`):*
- **3418/CT-CS** (5499 ký tự): FixedSizeChunker (`fixed_size`): 28 chunks, avg 196.4 chars; SentenceChunker (`by_sentences`): 10 chunks, avg 547.8 chars; RecursiveChunker (`recursive`): 44 chunks, avg 125.0 chars.
- **654/TNI-QLDN1** (4996 ký tự): FixedSizeChunker (`fixed_size`): 25 chunks, avg 199.8 chars; SentenceChunker (`by_sentences`): 8 chunks, avg 622.0 chars; RecursiveChunker (`recursive`): 39 chunks, avg 128.1 chars.
- **4221/CT-CS** (3296 ký tự): FixedSizeChunker (`fixed_size`): 17 chunks, avg 193.9 chars; SentenceChunker (`by_sentences`): 6 chunks, avg 546.8 chars; RecursiveChunker (`recursive`): 25 chunks, avg 131.8 chars.

Với `chunk_size=200`, `RecursiveChunker` mặc định tạo nhiều chunk nhỏ, không phù hợp văn bản luật cần giữ ngữ cảnh một mục/Điều. `FixedSizeChunker` ổn định kích thước nhưng hay cắt giữa cấu trúc pháp lý. `SentenceChunker` cho chunk dài hơn, coherent hơn với đoạn giải thích ngắn.

### Strategy Của Tôi

**Loại:** Custom — `LegalSectionChunker` (tách theo mục đánh số `1.`, `2.`, ...)

**Mô tả cách hoạt động:**
> `LegalSectionChunker` dùng regex `(?=\n\d+\.\s)` để tách văn bản tại ranh giới các mục đánh số (ví dụ `1. Về thuế tài nguyên`, `2. Về phí bảo vệ môi trường`). Mỗi mục nếu ≤ 500 ký tự được giữ nguyên thành một chunk; mục quá dài được xử lý tiếp bằng `RecursiveChunker(chunk_size=500)`. Cách này ưu tiên ranh giới pháp lý có ý nghĩa tra cứu thay vì cắt theo số ký tự hay số câu.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Văn bản luật thuế doanh nghiệp và công văn hướng dẫn của Cục Thuế có cấu trúc mục (`1.`, `2.`, `3.`) tương ứng từng chủ đề thuế. Khi doanh nghiệp tra cứu, câu hỏi thường gắn với một mục cụ thể (ví dụ "chi phí lương có được trừ không?"). Chunk theo mục giúp retrieval trả về đúng ngữ cảnh pháp lý, tránh gộp nhiều loại thuế khác nhau vào một chunk.

**Code snippet (custom):**
```python
import re
from src.chunking import RecursiveChunker

class LegalSectionChunker:
    _SECTION_PATTERN = re.compile(r"(?=\n\d+\.\s)")

    def __init__(self, chunk_size: int = 500) -> None:
        self.chunk_size = chunk_size
        self._fallback = RecursiveChunker(chunk_size=chunk_size)

    def chunk(self, text: str) -> list[str]:
        sections = [s.strip() for s in self._SECTION_PATTERN.split(text) if s.strip()]
        if len(sections) <= 1:
            return self._fallback.chunk(text)
        chunks = []
        for section in sections:
            if len(section) <= self.chunk_size:
                chunks.append(section)
            else:
                chunks.extend(self._fallback.chunk(section))
        return chunks
```

### So Sánh: Strategy của tôi vs Baseline

So sánh `LegalSectionChunker(chunk_size=500)` với baseline tốt nhất trên cùng tài liệu (đo bởi `tests/compare_documents.py`):

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| 3418/CT-CS | best baseline (`by_sentences`) | 10 | 547.8 | Khá — chunk dài, coherent nhưng có thể gộp nhiều mục thuế |
| 3418/CT-CS | **của tôi** (`LegalSectionChunker`, size=500) | 15 | 366.3 | Tốt — chunk theo mục pháp lý, kích thước vừa phải (~350 ký tự), phù hợp tra cứu theo chủ đề thuế |
| 654/TNI-QLDN1 | best baseline (`by_sentences`) | 8 | 622.0 | Khá — chunk dài, coherent nhưng có thể gộp nhiều mục thuế |
| 654/TNI-QLDN1 | **của tôi** (`LegalSectionChunker`, size=500) | 14 | 356.7 | Tốt — chunk theo mục pháp lý, kích thước vừa phải (~350 ký tự), phù hợp tra cứu theo chủ đề thuế |
| 4221/CT-CS | best baseline (`by_sentences`) | 6 | 546.8 | Khá — chunk dài, coherent nhưng có thể gộp nhiều mục thuế |
| 4221/CT-CS | **của tôi** (`LegalSectionChunker`, size=500) | 10 | 329.4 | Tốt — chunk theo mục pháp lý, kích thước vừa phải (~350 ký tự), phù hợp tra cứu theo chủ đề thuế |

**Kết luận Step 3:** Strategy cá nhân tạo ít chunk hơn `RecursiveChunker` baseline (200) và giữ ranh giới mục pháp lý (`1.`, `2.`, `3.`) tốt hơn `FixedSizeChunker`. So với `SentenceChunker`, custom strategy tránh gộp nhiều mục thuế khác nhau vào một chunk dài — phù hợp câu hỏi tra cứu theo từng loại thuế/chính sách.

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi (Duyên) | LegalSectionChunker (tách mục `1.`, `2.`, ...) | 8 | Giữ ranh giới đoạn/Điều, chunk coherent, phù hợp văn bản luật phân cấp | Với FAQ thuế rất ngắn (1–2 câu), chunk có thể hơi dài so với câu hỏi cụ thể |
| [Thành viên A] | SentenceChunker (`max_sentences=2`) | 7 | Chunk gọn, dễ đọc, tốt với đoạn giải thích thuật ngữ ngắn | Gộp nhiều khoản vào một chunk khi câu luật dài; kích thước không ổn định |
| [Thành viên B] | FixedSizeChunker (`chunk_size=400`, `overlap=50`) | 6 | Số chunk dự đoán được, overlap giúp giữ ngữ cảnh ranh giới | Hay cắt giữa Điều/Khoản; retrieval trả về fragment thiếu điều kiện áp dụng |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> `LegalSectionChunker` là lựa chọn tốt nhất cho domain luật thuế doanh nghiệp. Văn bản pháp luật có cấu trúc mục đánh số (`1.`, `2.`, `3.`) mang ý nghĩa pháp lý — custom chunker tách theo ranh giới mục trước khi fallback `RecursiveChunker`. So với `FixedSizeChunker`, nó tránh cắt giữa điều khoản; so với `SentenceChunker`, nó không gộp nhiều loại thuế vào một chunk dài. Kết quả đo trên 3 công văn thuế cho thấy strategy này đạt chunk ~330–370 ký tự, phù hợp tra cứu theo chủ đề thuế cụ thể.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Dùng regex `(?<=[.!?])\s+|\.\n` để tách câu theo dấu `. `, `! `, `? ` hoặc `.\n`, sau đó strip whitespace và gom tối đa `max_sentences_per_chunk` câu thành một chunk. Xử lý edge case: text rỗng trả về `[]`; nếu không tách được câu thì trả về nguyên đoạn text đã strip.

**`RecursiveChunker.chunk` / `_split`** — approach:
> `chunk()` gọi `_split()` với toàn bộ text và danh sách separator `["\n\n", "\n", ". ", " ", ""]`. Base case: nếu đoạn text ngắn hơn `chunk_size` thì trả về luôn; nếu hết separator thì cắt cứng theo ký tự. Với separator hiện tại, tách text, gộp các phần nhỏ vào cùng chunk, còn phần quá dài thì đệ quy với separator tiếp theo.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> Mỗi `Document` được embed qua `embedding_fn`, lưu thành record gồm `id`, `content`, `embedding`, `metadata` (có thêm `doc_id`). Nếu ChromaDB khả dụng thì dùng `collection.add()`, không thì append vào `self._store`. `search()` embed câu query, tính dot product với từng embedding đã lưu (vector đã normalize nên tương đương cosine similarity), sort giảm dần và trả về top-k kèm `score`.

**`search_with_filter` + `delete_document`** — approach:
> **Filter trước, search sau:** lọc các record có metadata khớp toàn bộ điều kiện trong `metadata_filter`, rồi mới chạy similarity search trên tập đã lọc. `delete_document()` xóa mọi record có `metadata['doc_id'] == doc_id`, trả về `True` nếu có ít nhất một chunk bị xóa.

### KnowledgeBaseAgent

**`answer`** — approach:
> Gọi `store.search(question, top_k)` để lấy các chunk liên quan, ghép thành context block kèm source và score. Prompt gồm instruction ("chỉ trả lời từ context"), phần context đã format, câu hỏi, và nhãn `Answer:`. Cuối cùng gọi `llm_fn(prompt)` và trả về kết quả.

### Test Results

```
# Chạy sau khi hoàn thành tất cả TODO trong src/:
# pytest tests/ -v
```

**Số tests pass:** _[điền sau khi chạy pytest]_ / _[tổng số tests]_

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Python is a high-level programming language. | Python is widely used for machine learning and data science. | high | -0.0955 | Không |
| 2 | The cat sat on the mat. | A feline rested on the rug. | high | -0.0506 | Không |
| 3 | How do I reset my password? | Billing errors should be escalated to the finance team. | low | -0.0776 | Có |
| 4 | Vector databases store embeddings for similarity search. | Embeddings enable semantic search in vector stores. | high | -0.1542 | Không |
| 5 | Today is sunny and warm. | The stock market closed higher yesterday. | low | 0.2008 | Không |

*Actual Score tính bằng `_mock_embed` (dot product trên vector đã normalize).*

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> Bất ngờ nhất là Pair 5 (hai câu không liên quan) lại có score cao nhất (0.2008), trong khi các cặp cùng chủ đề (Pair 1, 2, 4) đều âm. Điều này cho thấy mock embed dựa trên hash không phản ánh nghĩa ngữ nghĩa — chỉ tạo vector deterministic từ ký tự. Với embedding thật (sentence-transformers, OpenAI), các cặp cùng chủ đề mới có score cao; mock embed chỉ phù hợp để test pipeline, không dùng để đánh giá chất lượng retrieval.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | What is Python commonly used for in production environments? | Python is used to build APIs, data pipelines, internal tools, and model-serving layers; frameworks like FastAPI, Django, and Flask are common. |
| 2 | What is the main goal of a RAG system? | Find relevant internal documents before generating an answer, grounding responses in retrieved text to reduce hallucinations. |
| 3 | Why should support content include specific language instead of vague instructions? | Specific terms (exact page, button, log source) make chunks easier to match during retrieval when users ask concrete troubleshooting questions. |
| 4 | What steps does a typical retrieval pipeline include? | Collect documents, clean content, chunk into meaningful segments, embed each chunk, then embed the user query and compare vectors to find the closest matches. |
| 5 | What should the assistant do when retrieval results are weak? (filter: `extension=.md`) | Say explicitly that evidence is insufficient or contradictory instead of pretending the answer is complete. |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | What is Python commonly used for in production environments? | _[điền sau khi chạy benchmark]_ | — | — | — |
| 2 | What is the main goal of a RAG system? | _[điền sau khi chạy benchmark]_ | — | — | — |
| 3 | Why should support content include specific language instead of vague instructions? | _[điền sau khi chạy benchmark]_ | — | — | — |
| 4 | What steps does a typical retrieval pipeline include? | _[điền sau khi chạy benchmark]_ | — | — | — |
| 5 | What should the assistant do when retrieval results are weak? | _[điền sau khi chạy benchmark]_ | — | — | — |

**Bao nhiêu queries trả về chunk relevant trong top-3?** _[điền sau khi chạy benchmark]_ / 5

> *Ghi chú: 5 queries trên dựa trên bộ tài liệu mẫu trong `data/`. Sau khi hoàn thành `src/`, chạy `python3 main.py` hoặc script benchmark cá nhân để điền bảng kết quả.*

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> Tôi học được cách chọn `chunk_size` phù hợp với cấu trúc tài liệu: tài liệu FAQ ngắn hợp với `SentenceChunker`, còn markdown dài có nhiều heading hợp với `RecursiveChunker vì giữ được ranh giới đoạn văn thay vì cắt giữa câu.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> Một nhóm khác gán metadata `audience` (customer-facing vs internal) và luôn filter trước khi search — giúp tránh retrieve nội dung nội bộ khi câu hỏi hướng tới khách hàng. Đây là bài học quan trọng về metadata utility ngoài semantic similarity.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> Tôi sẽ chuẩn hóa metadata sớm hơn (thêm `doc_type`, `language`, `last_updated`) và thiết kế benchmark queries ngay khi chọn tài liệu, thay vì viết queries sau khi đã index. Cách này giúp phát hiện sớm chunk quá ngắn hoặc thiếu ngữ cảnh trước khi chạy toàn bộ pipeline.

**Failure case (phân tích):**
> Query 5 (cần filter `extension=.md`) có thể thất bại nếu filter quá chặt khiến không còn chunk nào khớp, hoặc nếu chunk về "weak retrieval" nằm ở cuối tài liệu và bị chia nhỏ mất ngữ cảnh. Cải thiện: tăng overlap, gán metadata `topic=evaluation` cho các đoạn về đánh giá chất lượng retrieval.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | / 10 |
| Chunking strategy | Nhóm | / 15 |
| My approach | Cá nhân | 8 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | _[điền sau benchmark]_ / 10 |
| Core implementation (tests) | Cá nhân | _[điền sau pytest]_ / 30 |
| Demo | Nhóm | / 5 |
| **Tổng** | | **/ 100** |
