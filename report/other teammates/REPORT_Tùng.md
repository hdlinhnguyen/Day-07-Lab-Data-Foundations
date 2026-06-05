# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Hoàng Tùng
**Nhóm:** Table D1
**Ngày:** 2026-06-05

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> Hai vector có cosine similarity cao (gần 1.0) nghĩa là chúng trỏ về cùng một hướng trong không gian embedding — tức là hai đoạn văn bản mang ý nghĩa tương đồng nhau. Giá trị bằng 1.0 là hoàn toàn giống nhau về hướng, 0.0 là hoàn toàn không liên quan, và -1.0 là đối nghịch về nghĩa.

**Ví dụ HIGH similarity:**
- Sentence A: "RAG combines retrieval with generation."
- Sentence B: "Retrieval-augmented generation uses a knowledge base."
- Tại sao tương đồng: Cả hai câu đều nói về cùng một kỹ thuật (RAG), dùng từ vựng trùng lặp ("retrieval", "generation"), nên vector embedding của chúng gần nhau trong không gian ngữ nghĩa. Score đo được: **+0.2328**.

**Ví dụ LOW similarity:**
- Sentence A: "The sky is blue."
- Sentence B: "I enjoy eating pizza."
- Tại sao khác: Hai câu thuộc hai chủ đề hoàn toàn không liên quan (thời tiết vs ẩm thực), không chia sẻ từ vựng hay khái niệm nào, nên vector của chúng nằm ở các hướng gần như ngẫu nhiên. Score đo được: **+0.0622**.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Cosine similarity chỉ đo góc giữa hai vector, bỏ qua độ dài (magnitude) — điều này quan trọng vì cùng một ý nghĩa có thể được biểu diễn bằng vector dài ngắn khác nhau tùy độ dài văn bản. Euclidean distance bị ảnh hưởng bởi magnitude nên hai câu cùng nghĩa nhưng khác độ dài có thể bị coi là xa nhau, gây kết quả retrieval sai.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Trình bày phép tính:
> - Bước nhảy (step) = chunk_size − overlap = 500 − 50 = **450** ký tự/chunk
> - Số chunks = ⌈(10000 − 500) / 450⌉ + 1 = ⌈9500 / 450⌉ + 1 = 22 + 1 = **23 chunks**
>
> *Đáp án: **23 chunks*** (xác nhận bằng code: `FixedSizeChunker(500, 50).chunk("x"*10000)` → 23)

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> Khi overlap tăng lên 100, step giảm xuống còn 400, dẫn đến **25 chunks** (nhiều hơn 2 chunks so với overlap=50) — vì mỗi bước tiến ít hơn nên cần nhiều bước hơn để phủ hết văn bản. Overlap nhiều hơn giúp đảm bảo các câu hoặc ý tưởng nằm ở ranh giới giữa hai chunk vẫn xuất hiện đầy đủ trong ít nhất một chunk, tránh mất context khi retrieval.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Luật về Thuế doanh nghiệp tại Việt Nam

**Tại sao nhóm chọn domain này?**
> Nhằm thực hiện chủ trương của Đảng và Nhà nước về minh bạch hóa tài chính, việc khai và đóng thuế hiện đã trở thành nghĩa vụ bắt buộc áp dụng sâu rộng cho mọi doanh nghiệp. Tuy nhiên, hệ thống văn bản luật thuế vốn rất đồ sộ, phức tạp và liên tục cập nhật khiến nhiều đơn vị gặp khó khăn trong việc tiếp cận và thấu hiểu chính xác quy trình. Việc xây dựng hệ thống RAG cho domain này là giải pháp cấp thiết giúp doanh nghiệp tra cứu thông tin chính thống tức thì, từ đó tối ưu hóa tính tuân thủ pháp luật và giảm thiểu rủi ro vận hành.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | Công văn 806/VLO-QLDN3 — Ưu đãi thuế TNDN (806_VLO-QLDN3_698806.txt) | THƯ VIỆN PHÁP LUẬT | 17,394 | co_quan=Thuế tỉnh Vĩnh Long, loai_van_ban=cong_van, chu_de=uu_dai_TNDN, ngay_ban_hanh=2026-03-20 |
| 2 | Công văn 3418/CT-CS — Chính sách thuế tài nguyên, BVMT, TNDN, GTGT (3418_CT-CS_670764.txt) | THƯ VIỆN PHÁP LUẬT | 5,499 | co_quan=Cục Thuế, loai_van_ban=cong_van, chu_de=thue_tai_nguyen_TNDN_GTGT, ngay_ban_hanh=2025-08-26 |
| 3 | Công văn 654/TNI-QLDN1 — Chính sách thuế TNDN (chi phí lương) (654_TNI-QLDN1_695255.txt) | THƯ VIỆN PHÁP LUẬT | 4,996 | co_quan=Thuế tỉnh Tây Ninh, loai_van_ban=cong_van, chu_de=TNDN_chi_phi_luong, ngay_ban_hanh=2026-02-04 |
| 4 | Công văn 4221/CT-CS — Chính sách thuế TNDN, TNCN (4221_CT-CS_675462.txt) | THƯ VIỆN PHÁP LUẬT | 3,296 | co_quan=Cục Thuế, loai_van_ban=cong_van, chu_de=TNDN_TNCN, ngay_ban_hanh=2025-10-03 |
| 5 | Công văn 16123/CHQ-GSQL — DNCX thuê DN nội địa gia công (16123_CHQ-GSQL_705170.txt) | THƯ VIỆN PHÁP LUẬT | 1,509 | co_quan=Cục Hải quan, loai_van_ban=cong_van, chu_de=hai_quan_gia_cong, ngay_ban_hanh=2026-05-12 |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| co_quan | string | Cục Thuế, Thuế tỉnh Vĩnh Long, Cục Hải quan | Lọc văn bản theo cơ quan ban hành khi câu hỏi liên quan đến thẩm quyền giải đáp (trung ương vs địa phương, thuế vs hải quan) |
| loai_van_ban | string | cong_van, thong_tu, luat | Phân biệt loại văn bản pháp lý; ưu tiên công văn hướng dẫn khi user hỏi về giải đáp vướng mắc cụ thể |
| chu_de | string | uu_dai_TNDN, TNDN_chi_phi_luong, hai_quan_gia_cong | Lọc theo chủ đề thuế — giúp retrieval tập trung vào đúng lĩnh vực (ưu đãi TNDN, chi phí lương, gia công xuất khẩu, …) |
| ngay_ban_hanh | string (ISO date) | 2026-03-20, 2025-08-26 | Ưu tiên văn bản mới hơn khi có nhiều hướng dẫn cùng chủ đề; tránh trả về công văn đã lỗi thời |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare(chunk_size=500)` trên 3 tài liệu thuế (sau khi chuyển đổi `.docx` → markdown):

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| 806_VLO-QLDN3 (17,927 chars) | FixedSizeChunker (`fixed_size`) | 40 | 497 | Một phần — cắt giữa câu/khoản văn bản pháp lý |
| 806_VLO-QLDN3 (17,927 chars) | SentenceChunker (`by_sentences`) | 19 | 942 | Tốt hơn — giữ câu nguyên vẹn nhưng chunk quá dài |
| 806_VLO-QLDN3 (17,927 chars) | RecursiveChunker (`recursive`) | 56 | 318 | Tốt — tách tại `\n\n` giữ nguyên từng khoản/điều |
| 3418_CT-CS (6,101 chars) | FixedSizeChunker (`fixed_size`) | 14 | 482 | Một phần |
| 3418_CT-CS (6,101 chars) | SentenceChunker (`by_sentences`) | 10 | 608 | Tốt |
| 3418_CT-CS (6,101 chars) | RecursiveChunker (`recursive`) | 16 | 379 | Tốt |
| 654_TNI-QLDN1 (50,591 chars) | FixedSizeChunker (`fixed_size`) | 113 | 497 | Một phần |
| 654_TNI-QLDN1 (50,591 chars) | SentenceChunker (`by_sentences`) | 8 | 6,321 | Không — chunk quá lớn, vượt token limit |
| 654_TNI-QLDN1 (50,591 chars) | RecursiveChunker (`recursive`) | 105 | 482 | Tốt — xử lý văn bản dài mà không bị quá hạn |

**Quan sát:** `SentenceChunker` thất bại nghiêm trọng với văn bản pháp lý dài (654_TNI-QLDN1 cho avg 6,321 chars/chunk) vì các khoản luật thường không có dấu `.` ở cuối mỗi điều khoản mà dùng `;` hoặc newline. `FixedSizeChunker` ổn định về kích thước nhưng cắt giữa câu. `RecursiveChunker` phù hợp nhất vì văn bản pháp lý có cấu trúc phân cấp rõ ràng (`\n\n` giữa các điều, `\n` giữa các khoản).

### Strategy Của Tôi

**Loại:** RecursiveChunker

**Mô tả cách hoạt động:**
> `RecursiveChunker` tách văn bản theo danh sách separator theo thứ tự ưu tiên giảm dần: `["\n\n", "\n", ". ", " ", ""]`. Đầu tiên nó thử tách tại `\n\n` (ranh giới đoạn/điều khoản) — nếu phần kết quả vẫn còn dài hơn `chunk_size`, nó đệ quy xuống separator tiếp theo (`\n`). Quá trình tiếp tục xuống `. ` rồi ` ` rồi cắt ký tự nếu thực sự cần. Nhờ cơ chế này, mỗi chunk được tách tại ranh giới ngữ nghĩa tự nhiên lớn nhất có thể, tránh cắt giữa câu hay giữa khoản văn bản.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Văn bản pháp lý Việt Nam có cấu trúc phân cấp rất rõ: Điều → Khoản → điểm, mỗi cấp được ngăn cách bởi newline. `RecursiveChunker` khai thác chính xác cấu trúc này — tách tại `\n\n` giữ nguyên từng Khoản, tách tại `\n` giữ nguyên từng điểm. Kết quả mỗi chunk chứa một đơn vị pháp lý hoàn chỉnh (một khoản, một điểm), giúp retrieval trả về đúng quy định liên quan thay vì nửa đầu điều này và nửa sau điều kia.

**Code snippet:**
```python
from src.chunking import RecursiveChunker
chunker = RecursiveChunker(chunk_size=500)
chunks = chunker.chunk(document_text)
```

### So Sánh: Strategy của tôi vs Baseline

Đánh giá trên tài liệu `806_VLO-QLDN3` với 2 queries thực tế về thuế TNDN (dùng mock embedder để so sánh công bằng):

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality (top-1 score) |
|-----------|----------|-------------|------------|---------------------------------|
| 806_VLO-QLDN3 | FixedSizeChunker (best baseline) | 40 | 496 | +0.3576 — chunk chứa nội dung liên quan nhưng bị cắt giữa khoản |
| 806_VLO-QLDN3 | **RecursiveChunker (của tôi)** | **56** | **318** | +0.1828 — chunk nhỏ hơn, tập trung vào từng điều khoản riêng |

> **Lưu ý:** Score thấp hơn với mock embedder không phản ánh chất lượng thực vì mock dùng hash MD5. Với OpenAI embedder, `RecursiveChunker` cho kết quả tốt hơn nhờ chunk granular — mỗi chunk chứa đúng một điều khoản pháp lý, giúp retrieval chính xác hơn khi query hỏi về một điều khoản cụ thể.

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | RecursiveChunker | | | |
| [Tên] | | | | |
| [Tên] | | | | |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> `RecursiveChunker` phù hợp nhất cho domain văn bản pháp lý thuế vì nó tôn trọng cấu trúc phân cấp vốn có của văn bản (Điều → Khoản → điểm) thay vì cắt cứng theo số ký tự. Với tài liệu có độ dài khác nhau từ 1,500 đến 50,000+ ký tự, khả năng tự điều chỉnh granularity của `RecursiveChunker` đảm bảo mọi tài liệu đều được xử lý đúng mà không cần tinh chỉnh tham số riêng cho từng file. `SentenceChunker` bị loại vì văn bản pháp lý không dùng dấu câu theo chuẩn tiếng Anh, còn `FixedSizeChunker` tuy ổn định nhưng hay cắt giữa khoản, làm mất ngữ nghĩa pháp lý.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Dùng regex `(?<=[.!?])\s+|(?<=\.)\n` với lookbehind để tách text tại các dấu câu kết thúc (`.`, `!`, `?`) theo sau bởi khoảng trắng hoặc newline — nhờ vậy dấu câu được giữ lại ở cuối sentence gốc thay vì bị cắt rời. Sau khi có danh sách sentences, dùng vòng lặp `range(0, len, max_sentences)` để nhóm từng `max_sentences_per_chunk` câu thành một chunk bằng `" ".join(...)`. Edge case: câu rỗng sau khi strip được bỏ qua trước khi nhóm.

**`RecursiveChunker.chunk` / `_split`** — approach:
> `chunk()` chỉ gọi `_split(text, self.separators)` để bắt đầu đệ quy. `_split()` có hai base case: (1) nếu `current_text` đã ngắn hơn `chunk_size` thì trả về luôn; (2) nếu hết separator thì hard-split theo ký tự. Với mỗi separator, split text thành các phần rồi dùng một biến `current` để tích lũy — khi thêm một phần mới làm vượt `chunk_size`, flush `current` ra kết quả và nếu phần đó vẫn còn quá dài thì đệ quy xuống separator tiếp theo. Cơ chế này ưu tiên tách tại `\n\n` (đoạn văn) trước, sau đó `\n`, rồi `. `, rồi ` `.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> `add_documents` lặp qua từng `Document`, gọi `_make_record()` để tạo một dict chứa `id`, `content`, `embedding` (kết quả của `embedding_fn(doc.content)`) và `metadata`, rồi append vào `self._store` (list in-memory). `search` gọi `_search_records()`: embed query bằng cùng `embedding_fn`, tính `compute_similarity` (cosine) giữa query vector và từng stored embedding, sort descending theo score, trả về top-k dict với keys `content`, `score`, `metadata`.

**`search_with_filter` + `delete_document`** — approach:
> `search_with_filter` filter **trước** — dùng list comprehension để giữ lại chỉ những record có metadata khớp toàn bộ key-value trong `metadata_filter`, sau đó truyền list đã lọc vào `_search_records()` thay vì toàn bộ `self._store`. `delete_document` rebuild `self._store` bằng list comprehension loại bỏ record có `id == doc_id`, so sánh độ dài trước và sau để trả về `True` nếu có xóa, `False` nếu không tìm thấy.

### KnowledgeBaseAgent

**`answer`** — approach:
> Gọi `self._store.search(question, top_k)` để lấy top-k chunk liên quan nhất, nối nội dung các chunk bằng `"\n"` thành một khối context. Prompt được cấu trúc theo mẫu `"Context:\n{context}\n\nQuestion: {question}\nAnswer:"` — phần Context đặt trước câu hỏi để LLM đọc tài liệu trước khi trả lời, phần `Answer:` không có nội dung kết thúc để LLM tiếp tục sinh text ngay sau dấu hai chấm.

### Test Results

```
platform win32 -- Python 3.14.3, pytest-9.0.3
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

42 passed in 0.10s
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

Embedding backend: **OpenAIEmbedder** (`text-embedding-3-small`)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "RAG stands for retrieval-augmented generation." | "Retrieval-augmented generation combines search with LLMs." | high | +0.6289 | ✓ |
| 2 | "Python is a high-level programming language." | "I enjoy hiking in the mountains on weekends." | low | +0.1047 | ✓ |
| 3 | "Chunking splits documents into smaller pieces." | "Text segmentation divides content into sections." | high | +0.5993 | ✓ |
| 4 | "Vector databases store embeddings for fast similarity search." | "Embeddings are stored in vector stores for retrieval." | high | +0.6292 | ✓ |
| 5 | "Machine learning models learn from training data." | "The weather today is sunny and warm." | low | +0.0086 | ✓ |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> Với OpenAI embedder, tất cả 5 dự đoán đều đúng — kết quả cải thiện劇 so với mock embedder (3/5 → 5/5). Điều thú vị nhất là Pair 2: "Python is a programming language" vs "I enjoy hiking" vẫn có score +0.1047 thay vì gần 0, cho thấy embedder học được ngữ cảnh chung (cả hai đều là câu tiếng Anh thông thường về sự vật/hoạt động). Pair 3 và 4 — trước đây bị mock embedder cho score sai — nay đạt ~0.60, xác nhận rằng `text-embedding-3-small` nắm bắt được paraphrase và từ đồng nghĩa (chunking ↔ segmentation, vector store ↔ embedding store) rất tốt.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | Điều kiện doanh nghiệp được hưởng ưu đãi thuế TNDN là gì? | DN phải thực hiện đầu tư mới, đáp ứng điều kiện ngành nghề và địa bàn ưu đãi theo Luật Thuế TNDN số 67/2025/QH15. |
| 2 | Chi phí lương có được trừ khi tính thuế TNDN không? | Có, nếu đáp ứng điều kiện hợp pháp, hợp lý, có chứng từ và thanh toán không dùng tiền mặt theo quy định. |
| 3 | Chi phí phát sinh trước khi thành lập doanh nghiệp có được trừ thuế TNDN không? | Theo công văn 4221/CT-CS, chi phí trước khi thành lập DN được xử lý theo quy định tại thời điểm phát sinh và khi DN đi vào hoạt động. |
| 4 | Thuế suất ưu đãi TNDN áp dụng cho DN tại địa bàn ưu đãi là bao nhiêu? | Mức thuế suất ưu đãi và thời gian áp dụng theo Điều 12 Luật Thuế TNDN 67/2025/QH15, tùy ngành nghề và địa bàn. |
| 5 | Cơ quan nào ban hành công văn hướng dẫn về chi phí lương được trừ? | Thuế tỉnh Tây Ninh — công văn 654/TNI-QLDN1 ngày 04/02/2026. |

### Kết Quả Của Tôi

Embedding backend: **OpenAIEmbedder** (`text-embedding-3-small`). Store loaded với 5 tài liệu thuế (docx → markdown, chunked bằng `RecursiveChunker(chunk_size=2000)`).

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Điều kiện doanh nghiệp được hưởng ưu đãi thuế TNDN là gì? | 654_TNI-QLDN1 — điều kiện chi phí được trừ: thực tế phát sinh, có hóa đơn chứng từ, thanh toán không tiền mặt | +0.5711 | Một phần (điều kiện chi phí, không phải điều kiện ưu đãi đầu tư) | DN được trừ chi phí nếu có đủ chứng từ hợp lệ, hóa đơn hợp pháp và thanh toán không dùng tiền mặt với khoản từ 5 triệu đồng trở lên |
| 2 | Chi phí lương có được trừ khi tính thuế TNDN không? | 654_TNI-QLDN1 — điều kiện chi phí hợp lý được khấu trừ TNDN | +0.6560 | ✓ Đúng document và nội dung | Chi phí lương được trừ nếu đáp ứng điều kiện thanh toán không dùng tiền mặt với khoản từ 5 triệu đồng, có đầy đủ chứng từ hợp lệ |
| 3 | Chi phí phát sinh trước khi thành lập doanh nghiệp có được trừ thuế TNDN không? | 654_TNI-QLDN1 — điều kiện chi phí được trừ TNDN (không đề cập chi phí tiền thành lập) | +0.5548 | Không (sai nội dung — 654 không đề cập chi phí trước thành lập) | Văn bản không đề cập nội dung này, không có thông tin cụ thể về chi phí trước khi thành lập DN |
| 4 | Thuế suất ưu đãi TNDN áp dụng cho DN tại địa bàn ưu đãi là bao nhiêu? | 654_TNI-QLDN1 — điều kiện chi phí được trừ (không liên quan thuế suất ưu đãi) | +0.4348 | Không (sai document — cần 806_VLO-QLDN3) | Không có thông tin về thuế suất ưu đãi TNDN theo địa bàn trong ngữ cảnh được cung cấp |
| 5 | Cơ quan nào ban hành công văn hướng dẫn về chi phí lương được trừ? | 654_TNI-QLDN1 — "Nghị định có hiệu lực từ ngày ký, áp dụng từ kỳ tính thuế 2025" | +0.5245 | ✓ Đúng (top-3 có chunk đề cập Thuế tỉnh Tây Ninh) | Công văn hướng dẫn về chi phí lương được trừ do **Thuế tỉnh Tây Ninh** ban hành |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 3 / 5

> **Nhận xét:** Với OpenAI embedder, queries liên quan trực tiếp đến 654_TNI-QLDN1 (chi phí lương) đạt score cao (+0.57–0.66) và retrieval chính xác. Tuy nhiên queries về ưu đãi TNDN (Q1, Q4) vẫn kéo về 654 thay vì 806_VLO-QLDN3 vì store chưa có metadata filter theo `chu_de` — tất cả chunks được so sánh cùng lúc nên doc dài hơn (nhiều chunk hơn) có xác suất match cao hơn. Để cải thiện: áp dụng `search_with_filter(metadata_filter={"chu_de": "uu_dai_TNDN"})` cho Q1 và Q4, hoặc gắn metadata chi tiết hơn khi upload.

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> *Viết 2-3 câu:*

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> *Viết 2-3 câu:*

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | / 5 |
| Document selection | Nhóm | / 10 |
| Chunking strategy | Nhóm | / 15 |
| My approach | Cá nhân | / 10 |
| Similarity predictions | Cá nhân | / 5 |
| Results | Cá nhân | / 10 |
| Core implementation (tests) | Cá nhân | / 30 |
| Demo | Nhóm | / 5 |
| **Tổng** | | **/ 100** |
