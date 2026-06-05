# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Hoàng Đức Trường
**Nhóm:** Table D1
**Ngày:** 05/06/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> Hai vector embedding có hướng gần nhau trong không gian đa chiều, tức là hai đoạn văn bản mang ý nghĩa tương tự hoặc liên quan chặt chẽ. Giá trị càng gần 1 thì mức độ tương đồng ngữ nghĩa càng cao.

**Ví dụ HIGH similarity:**
- Sentence A: "Doanh nghiệp phải nộp thuế thu nhập doanh nghiệp hàng quý."
- Sentence B: "Tổ chức kinh doanh có nghĩa vụ kê khai và nộp thuế TNDN theo quý."
- Tại sao tương đồng: Cả hai đều nói về nghĩa vụ nộp thuế TNDN theo kỳ quý, chia sẻ chủ đề và thuật ngữ pháp lý liên quan.

**Ví dụ LOW similarity:**
- Sentence A: "Thuế suất thuế thu nhập doanh nghiệp áp dụng cho doanh nghiệp vừa và nhỏ là 15%."
- Sentence B: "Hợp đồng lao động phải được ký bằng văn bản giữa người sử dụng lao động và người lao động."
- Tại sao khác: Một câu về thuế suất TNDN, câu kia về luật lao động — không có chủ đề hay ngữ cảnh chung.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Embeddings thường được chuẩn hóa (normalized) và quan tâm đến *hướng* (ngữ nghĩa) hơn *độ dài* vector. Cosine similarity đo góc giữa hai vector nên ổn định hơn khi magnitude không phản ánh mức độ liên quan nội dung.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> `num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))`
> `= ceil((10000 - 50) / (500 - 50))`
> `= ceil(9950 / 450)`
> `= ceil(22.11...)`
> *Đáp án:* **23 chunks**

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25 chunks`, tăng từ 23 lên 25. Overlap lớn hơn giúp các chunk liền kề chia sẻ ngữ cảnh ở ranh giới, tránh mất thông tin khi một ý bị cắt đôi giữa hai chunk; đổi lại số chunk tăng và có dữ liệu trùng lặp.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Tài liệu luật thuế doanh nghiệp

**Tại sao nhóm chọn domain này?**
> *Viết 2-3 câu:*

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

**3 tài liệu đã chọn:** Công văn 806/VLO-QLDN3 (ưu đãi TNDN), 654/TNI-QLDN1 (chi phí lương), 4221/CT-CS (TNDN, TNCN).

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu (`chunk_size=200`):

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| 806/VLO-QLDN3 (17,394 ký tự) | FixedSizeChunker (`fixed_size`) | 87 | 199.9 | Không — cắt giữa khoản luật |
| 806/VLO-QLDN3 | SentenceChunker (`by_sentences`) | 25 | 694.6 | Có — giữ câu hoàn chỉnh |
| 806/VLO-QLDN3 | RecursiveChunker (`recursive`) | 134 | 146.8 | Một phần — giữ đoạn nhưng chunk nhỏ |
| 654/TNI-QLDN1 (4,996 ký tự) | FixedSizeChunker (`fixed_size`) | 25 | 199.8 | Không |
| 654/TNI-QLDN1 | SentenceChunker (`by_sentences`) | 8 | 623.5 | Có |
| 654/TNI-QLDN1 | RecursiveChunker (`recursive`) | 40 | 136.3 | Một phần |
| 4221/CT-CS (3,296 ký tự) | FixedSizeChunker (`fixed_size`) | 17 | 193.9 | Không |
| 4221/CT-CS | SentenceChunker (`by_sentences`) | 6 | 547.8 | Có |
| 4221/CT-CS | RecursiveChunker (`recursive`) | 26 | 140.3 | Một phần |

### Strategy Của Tôi

**Loại:** RecursiveChunker (tuned `chunk_size=300`)

**Mô tả cách hoạt động:**
> RecursiveChunker thử các separator theo thứ tự ưu tiên: `\n\n` → `\n` → `. ` → ` ` → ký tự. Nếu một mảnh vẫn dài hơn `chunk_size`, đệ quy xuống separator tiếp theo. Khi hết separator, fallback cắt theo ký tự. Kết quả là chunk vừa đủ nhỏ để search chính xác, vừa giữ được cấu trúc đoạn văn.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Công văn thuế có cấu trúc phân mục rõ (1., 2., a), b), căn cứ điều luật). Recursive chunking ưu tiên tách theo xuống dòng và dấu chấm trước khi cắt cứng, giúp mỗi chunk thường chứa một ý pháp lý hoặc một căn cứ trích dẫn. Với `chunk_size=300`, chunk đủ chứa một khoản hướng dẫn ngắn mà không quá dài để làm loãng embedding.

**Code snippet (nếu custom):**
```python
chunker = RecursiveChunker(chunk_size=300)
chunks = chunker.chunk(document_text)
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| 806/VLO-QLDN3 | best baseline (`by_sentences`) | 25 | 694.6 | Tốt — ít chunk, ngữ cảnh đầy đủ cho câu hỏi tổng quan |
| 806/VLO-QLDN3 | **của tôi (recursive, 300)** | 91 | 209.7 | Khá — chunk nhỏ hơn, dễ match điều khoản cụ thể nhưng dễ mất ngữ cảnh |
| 654/TNI-QLDN1 | best baseline (`by_sentences`) | 8 | 623.5 | Tốt — mỗi chunk gần một mục hướng dẫn |
| 654/TNI-QLDN1 | **của tôi (recursive, 300)** | 27 | 192.7 | Khá — tách chi tiết hơn, phù hợp tra cứu điều kiện thanh toán lương |
| 4221/CT-CS | best baseline (`by_sentences`) | 6 | 547.8 | Tốt — văn bản ngắn, ít chunk |
| 4221/CT-CS | **của tôi (recursive, 300)** | 16 | 215.2 | Tương đương — số chunk gấp đôi nhưng vẫn trong ngưỡng hợp lý |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | | | | |
| | | | | |
| | | | | |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> Với văn bản luật thuế dạng công văn, **SentenceChunker** cho baseline tốt nhất về mặt giữ ngữ cảnh pháp lý (ít chunk, avg length cao). Tuy nhiên **RecursiveChunker (300)** phù hợp hơn khi cần tra cứu chi tiết theo từng mục/khoản và kết hợp metadata filter (`chu_de`, `co_quan`). FixedSize không phù hợp vì thường cắt giữa trích dẫn điều luật.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Dùng regex `(?<=[.!?])\s+` để tách sau dấu kết thúc câu (`.`, `!`, `?`) khi theo sau là khoảng trắng — bao gồm cả `.\n`. Gom `max_sentences_per_chunk` câu liên tiếp thành một chunk, strip whitespace. Trả về `[]` nếu text rỗng.

**`RecursiveChunker.chunk` / `_split`** — approach:
> Base case: text rỗng → `[]`; text ≤ `chunk_size` → `[text]`. Với từng separator, split text; mảnh quá dài thì đệ quy với separator tiếp theo; mảnh nhỏ thì gom lại đến khi đạt `chunk_size`. Separator `""` hoặc `separators=[]` → fallback cắt theo ký tự.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> Mỗi `Document` được embed qua `embedding_fn`, lưu record `{id, content, metadata, embedding}` vào `_store` (in-memory). Nếu ChromaDB khả dụng, đồng thời ghi vào collection. `search` embed query, tính dot product với từng embedding (tương đương cosine vì vector đã normalized), sort giảm dần, trả top-k kèm `content`, `score`, `metadata`.

**`search_with_filter` + `delete_document`** — approach:
> Filter **trước**: lọc `_store` theo metadata key-value khớp hoàn toàn, rồi search trên tập đã lọc. `delete_document` xóa mọi record có `id == doc_id` hoặc `metadata['doc_id'] == doc_id`, trả `True` nếu có bản ghi bị xóa.

### KnowledgeBaseAgent

**`answer`** — approach:
> Gọi `store.search(question, top_k)`, ghép các chunk thành context block, build prompt dạng "Use the following context… / Question: … / Answer:", rồi gọi `llm_fn(prompt)`. Pattern RAG chuẩn: retrieve → augment prompt → generate.

### Test Results

```
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED

============================= 42 passed in 0.09s ==============================
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Doanh nghiệp được hưởng ưu đãi thuế thu nhập doanh nghiệp. | Tổ chức kinh doanh được áp dụng mức thuế suất ưu đãi TNDN. | high | 0.0437 | Không (quá thấp) |
| 2 | Chi phí lương được trừ khi tính thuế TNDN. | Tiền lương trả cho người lao động là chi phí hợp lý được khấu trừ. | high | 0.2676 | Một phần (cao nhất) |
| 3 | Thuế thu nhập doanh nghiệp áp dụng cho doanh nghiệp có thu nhập chịu thuế. | Tôi thích ăn phở vào buổi sáng. | low | 0.1286 | Không (cả hai đều thấp, không phân biệt rõ) |
| 4 | Thanh toán lương không dùng tiền mặt theo quy định. | Chi trả tiền lương qua chuyển khoản ngân hàng. | high | -0.0455 | Không |
| 5 | Công văn của Cục Thuế hướng dẫn chính sách thuế TNDN. | Văn bản của cơ quan thuế giải đáp về thuế doanh nghiệp. | high | -0.0473 | Không |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> Cặp 4 và 5 (paraphrase rõ về thanh toán lương và công văn thuế) lại có score âm — hoàn toàn ngược dự đoán. Cặp 3 (chủ đề khác hẳn) lại có score dương 0.13, cao hơn một số cặp cùng chủ đề. Điều này xác nhận `_mock_embed` không mã hóa ngữ nghĩa tiếng Việt; khi đánh giá retrieval trên văn bản luật thuế, cần dùng embedding model thật hỗ trợ tiếng Việt.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries trên 3 tài liệu đã chọn (`RecursiveChunker(300)` + `EmbeddingStore` + `_mock_embed`). Tổng **134 chunks** được index.

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | Điều kiện doanh nghiệp được hưởng ưu đãi thuế TNDN là gì? | DN phải thực hiện đầu tư mới, đáp ứng điều kiện ngành nghề và địa bàn ưu đãi theo Luật Thuế TNDN số 67/2025/QH15. |
| 2 | Chi phí lương có được trừ khi tính thuế TNDN không? | Có, nếu đáp ứng điều kiện hợp pháp, hợp lý, có chứng từ và thanh toán không dùng tiền mặt theo quy định. |
| 3 | Chi phí phát sinh trước khi thành lập doanh nghiệp có được trừ thuế TNDN không? | Theo công văn 4221/CT-CS, chi phí trước khi thành lập DN được xử lý theo quy định tại thời điểm phát sinh và khi DN đi vào hoạt động. |
| 4 | Thuế suất ưu đãi TNDN áp dụng cho DN tại địa bàn ưu đãi là bao nhiêu? | Mức thuế suất ưu đãi và thời gian áp dụng theo Điều 12 Luật Thuế TNDN 67/2025/QH15, tùy ngành nghề và địa bàn. |
| 5 | Cơ quan nào ban hành công văn hướng dẫn về chi phí lương được trừ? | Thuế tỉnh Tây Ninh — công văn 654/TNI-QLDN1 ngày 04/02/2026. |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Điều kiện ưu đãi thuế TNDN? | Căn cứ Điều 4 Thông tư 96/2015/TT-BTC (từ CV 4221, sai tài liệu) | 0.291 | Không | Answer based on context |
| 2 | Chi phí lương được trừ TNDN? | Mục "Ủy quyền nhận thay lương" — Bộ luật Lao động (filter: `chu_de=TNDN_chi_phi_luong`) | 0.332 | Một phần | Answer based on context |
| 3 | Chi phí trước khi thành lập DN? | Căn cứ Điều 4 Thông tư 96/2015 (filter: `chu_de=TNDN_TNCN`) | 0.220 | Không | Answer based on context |
| 4 | Thuế suất ưu đãi TNDN? | Chunk về chuyển đổi chủ sở hữu DN (filter: `chu_de=uu_dai_TNDN`) | 0.247 | Không | Answer based on context |
| 5 | Cơ quan ban hành CV chi phí lương? | Điều kiện chứng từ thanh toán không dùng tiền mặt (filter: `co_quan=Thuế tỉnh Tây Ninh`) | 0.504 | Không (top-1); Có (top-3) | Answer based on context |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 1 / 5

(Query 5: top-3 có chunk *"Thuế tỉnh Tây Ninh có ý kiến như sau..."* — relevant. Query 2 một phần relevant vì liên quan lương nhưng không trả lời trực tiếp. Các query còn lại retrieval thất bại do mock embedder và chunk bị cắt giữa đoạn.)

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> *Viết 2-3 câu:*

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> *Viết 2-3 câu:*

**Failure Analysis (Ex 3.5):**

- **Query thất bại:** "Điều kiện doanh nghiệp được hưởng ưu đãi thuế TNDN là gì?" — top-1 trả về chunk từ công văn 4221/CT-CS (TNDN/TNCN) thay vì 806/VLO-QLDN3 (ưu đãi TNDN).
- **Nguyên nhân:** Không dùng metadata filter `chu_de=uu_dai_TNDN`; mock embedder không hiểu ngữ nghĩa tiếng Việt nên score dựa trên hash ngẫu nhiên; chunk recursive đôi khi quá ngắn và mất tiêu đề mục.
- **Đề xuất cải thiện:** Luôn filter theo `chu_de` khi query thuộc chủ đề cụ thể; dùng `LocalEmbedder` hỗ trợ tiếng Việt; tăng `chunk_size` hoặc chunk theo mục (1., 2., a), b)) thay vì cắt theo ký tự.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> (1) Gắn metadata `so_hieu_van_ban` và `muc` (mục 1, 2, …) để filter chính xác hơn. (2) Tiền xử lý thêm file `.txt` (chuẩn hóa khoảng trắng, tách theo mục) sau khi convert từ nguồn gốc. (3) Dùng embedding model thật thay vì mock. (4) Thiết kế benchmark queries kèm metadata filter bắt buộc cho mỗi câu hỏi.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | / 10 |
| Chunking strategy | Nhóm | / 15 |
| My approach | Cá nhân | 9 / 10 |
| Similarity predictions | Cá nhân | 4 / 5 |
| Results | Cá nhân | 6 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | / 5 |
| **Tổng** | | **/ 100** |
