# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Thị Hiểu
**Nhóm:** [Tên nhóm]
**Ngày:** 5/6/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> High cosine similarity (gần bằng 1.0) nghĩa là hai vector embedding có cùng hướng trong không gian đa chiều, tức là hai đoạn văn bản mang ý nghĩa ngữ nghĩa tương tự nhau. Chỉ số này không phụ thuộc vào độ dài văn bản mà chỉ phản ánh sự tương đồng về nội dung.

**Ví dụ HIGH similarity:**
- Sentence A: "The cat sat on the mat."
- Sentence B: "A cat is resting on a rug."
- Tại sao tương đồng: Cả hai câu đều mô tả con mèo đang nằm/nghỉ trên một bề mặt phẳng — chủ thể, hành động, và bối cảnh đều giống nhau dù từ ngữ khác nhau.

**Ví dụ LOW similarity:**
- Sentence A: "The stock market crashed yesterday."
- Sentence B: "She baked a chocolate cake for the party."
- Tại sao khác: Hai câu thuộc hai domain hoàn toàn khác nhau (tài chính vs. nấu ăn), không chia sẻ chủ thể, hành động, hay ngữ cảnh nào.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Euclidean distance bị ảnh hưởng bởi độ lớn (magnitude) của vector, nên văn bản dài tự nhiên sẽ có vector lớn hơn và bị coi là "xa" hơn dù nội dung tương tự. Cosine similarity chỉ đo góc giữa hai vector nên độc lập với độ dài văn bản, phản ánh đúng sự tương đồng ngữ nghĩa hơn.

---

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

> **Trình bày phép tính:**
>
> - `step = chunk_size - overlap = 500 - 50 = 450`
> - Số chunks = `ceil((10000 - 500) / 450) + 1`
> - = `ceil(9500 / 450) + 1`
> - = `ceil(21.11) + 1`
> - = `22 + 1`
>
> **Đáp án: 23 chunks**

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**

> Khi overlap tăng lên 100, `step = 500 - 100 = 400`, số chunks tăng lên `ceil(9500 / 400) + 1 = 24 + 1 = 25 chunks`. Overlap lớn hơn giúp đảm bảo các thông tin nằm ở ranh giới giữa hai chunk không bị mất ngữ cảnh — đặc biệt quan trọng khi một ý tưởng trải dài qua nhiều đoạn văn.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Luật thuế doanh nghiệp


**Tại sao nhóm chọn domain này?**
> *Nhằm thực hiện chủ trương của Đảng và Nhà nước về minh bạch hóa tài chính, việc khai và đóng thuế hiện đã trở thành nghĩa vụ bắt buộc áp dụng sâu rộng cho mọi doanh nghiệp. Tuy nhiên, hệ thống văn bản luật thuế vốn rất đồ sộ, phức tạp và liên tục cập nhật khiến nhiều đơn vị gặp khó khăn trong việc tiếp cận và thấu hiểu chính xác quy trình. Việc xây dựng hệ thống RAG cho domain này là giải pháp cấp thiết giúp doanh nghiệp tra cứu thông tin chính thống tức thì, từ đó tối ưu hóa tính tuân thủ pháp luật và giảm thiểu rủi ro vận hành.*

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

| Tài liệu | Strategy | Chunk Count | Avg Length |Preserves Context?|
|---|---|---|---|---|
| 654_TNI-QLDN1_695255.txt | fixed_size | 11 | 500 chars |Kém. Cắt ngang câu, có thể làm đứt đoạn điều khoản|
| 654_TNI-QLDN1_695255.txt | by_sentences | 8 | 624 chars |Khá. Giữ trọn vẹn câu văn nhưng chunk hơi dài|
| 654_TNI-QLDN1_695255.txt | recursive | 14 | 356 chars |Tốt. Cân bằng tốt giữa việc giữ ý và độ dài|
|---|---|---|---|---|
| 806_VLO-QLDN3_698806.txt | fixed_size | 39 | 494 chars |Kém. Nguy cơ chia cắt các mức phạt/hướng dẫn|
| 806_VLO-QLDN3_698806.txt | by_sentences | 25 | 694 chars |Khá. Giữ được ngữ cảnh pháp lý nhưng kích thước không đều|
| 806_VLO-QLDN3_698806.txt | recursive | 56 | 309 chars |Tốt nhất. Cắt nhỏ an toàn, tối ưu cho Embedding model|
|---|---|---|---|---|
| 3418_CT-CS_670764.txt | fixed_size | 13 | 469 chars |Kém. Rủi ro mất context tương tự như trên|
| 3418_CT-CS_670764.txt | by_sentences | 10 | 549 chars |Khá. Dễ đọc, phù hợp cho QA nhưng size chưa tối ưu|
| 3418_CT-CS_670764.txt | recursive | 15 | 365 chars |Tốt. Kích thước đồng đều, giữ ngữ cảnh ổn định|
|---|---|---|---|---|


### Strategy Của Tôi

**Loại:** RecursiveChunker

**Mô tả cách hoạt động:**
> *Chiến lược này phân chia văn bản dựa trên ranh giới cấu trúc từ lớn đến nhỏ. Đầu tiên, nó ưu tiên cắt ở các cấu trúc lớn như đoạn văn. Chỉ khi đoạn văn vượt quá giới hạn kích thước cho phép, nó mới lùi xuống (fallback) dùng các dấu phân tách nhỏ hơn (như dấu chấm câu, khoảng trắng) để cắt tiếp.*

**Tại sao tôi chọn strategy này cho domain nhóm?**
> *Domain dữ liệu của chúng tôi là Luật Thuế Doanh nghiệp (các công văn hướng dẫn). Văn bản luật thường có các đoạn, điểm, khoản rất dài và phức tạp. Việc cắt đệ quy (recursive) mang lại sự cân bằng tốt nhất: tránh được việc phá vỡ các diễn giải pháp lý liền mạch (như Fixed-size mắc phải), đồng thời kiểm soát được độ dài embedding lý tưởng khoảng 300-400 chars (tốt hơn Sentence-based). Nó trả về các đoạn văn bản (passages) hữu ích nhất cho hệ thống tra cứu RAG.*

**Code snippet (nếu custom):**
```python
# class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        # Nếu text đủ nhỏ, trả về ngay
        if len(current_text) <= self.chunk_size:
            return [current_text]

        # Hết separator thì cắt cứng theo chunk_size
        if not remaining_separators:
            return [
                current_text[i : i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]

        separator = remaining_separators[0]
        next_separators = remaining_separators[1:]

        # Tách theo separator hiện tại
        if separator == "":
            parts = list(current_text)
        else:
            parts = current_text.split(separator)

        chunks: list[str] = []
        current_buffer = ""

        for part in parts:
            candidate = (current_buffer + separator + part) if current_buffer else part

            if len(candidate) <= self.chunk_size:
                current_buffer = candidate
            else:
                # Flush buffer trước
                if current_buffer:
                    chunks.append(current_buffer)
                # Nếu bản thân part vẫn quá lớn, đệ quy sâu hơn
                if len(part) > self.chunk_size:
                    chunks.extend(self._split(part, next_separators))
                    current_buffer = ""
                else:
                    current_buffer = part

        if current_buffer:
            chunks.append(current_buffer)

        return chunks


```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count / Tổng kích thước | Retrieval Quality |
|-----------|----------|------------------------------|-------------------|
| 654_TNI-QLDN1 | Best Baseline (by_sentences) | 8 / 624 chars | Tạm ổn. Đôi khi trả về thông tin dài dòng, lẫn lộn giữa điều kiện A và điều kiện B do chunk quá lớn. |
| 654_TNI-QLDN1 | Đề xuất của tôi (recursive) | 14 / 356 chars | Tốt hơn. Focus chính xác vào đúng điều kiện (ví dụ: điều kiện chi phí lương), giúp câu trả lời ngắn gọn và sát với câu hỏi. |
| 806_VLO-QLDN3 | Best Baseline (by_sentences) | 25 / 694 chars | Hay bị nhiễu do gom chung nhiều khoản ưu đãi thuế khác nhau vào cùng một chunk. |
| 806_VLO-QLDN3 | Đề xuất của tôi (recursive) | 56 / 309 chars | Tốt nhất. Cắt nhỏ từng khoản ưu đãi thuế riêng biệt, giúp truy xuất chính xác khi hỏi về một loại ưu đãi cụ thể. |
| 3418_CT-CS | Best Baseline (by_sentences) | 10 / 549 chars | Khá tốt vì tài liệu gốc ngắn, nhưng đôi khi vẫn chứa thông tin dư thừa không liên quan trực tiếp đến truy vấn. |
| 3418_CT-CS | Đề xuất của tôi (recursive) | 15 / 365 chars | Tốt hơn. Trả về đúng đoạn quy định về thuế tài nguyên hoặc phí bảo vệ môi trường mà không bị lẫn với các nội dung khác. |



### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | | | | |
| [Tên] | | | | |
| [Tên] | | | | |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> *Viết 2-3 câu:*

---

## 4. My Approach — Cá nhân (10 điểm)

# Chunking Functions

## SentenceChunker.chunk — Approach

Dùng Regex:

```python
(?<=\.)\s+|(?<=!)\s+|(?<=\?)\s+|(?<=\.)\n
```

để tách câu. Xử lý edge case bằng cách dùng `.strip()` để xóa khoảng trắng thừa và tự động loại bỏ các chunk rỗng.

## RecursiveChunker.chunk / _split — Approach

Thuật toán đệ quy cắt văn bản theo danh sách separator ưu tiên giảm dần.

**Base case:** Dừng đệ quy khi:

```python
len(text) <= chunk_size
```

Nếu hết separator mà text vẫn dài hơn giới hạn cho phép, thuật toán sẽ fallback sang cắt cứng theo số ký tự.

# EmbeddingStore

## add_documents + search — Approach

Lưu trữ linh hoạt:

* Dùng ChromaDB nếu môi trường đã cài đặt.
* Nếu không có ChromaDB thì sử dụng in-memory list.

Hàm `search()` so sánh vector bằng phép nhân vô hướng (Dot Product), tương đương Cosine Similarity do các vector đã được normalize trước đó, sau đó trả về các kết quả có điểm tương đồng cao nhất (`top-k`).

## search_with_filter + delete_document — Approach

Tối ưu hiệu năng bằng cách filter trước theo metadata rồi mới thực hiện vector search trên tập dữ liệu đã lọc.

Hàm `delete_document()` tìm và xóa bản ghi dựa trên khóa `doc_id` được lưu trong metadata.

# KnowledgeBaseAgent

## answer — Approach

Áp dụng mô hình Retrieval-Augmented Generation (RAG):

```text
Retrieve top-k chunks
→ Nối thành Context [1]... [2]...
→ Inject vào System Prompt
→ Gọi LLM sinh câu trả lời
```

System Prompt kèm theo chỉ thị yêu cầu LLM chỉ được sử dụng thông tin xuất hiện trong context được cung cấp để trả lời câu hỏi.

### Test Results

```
# tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED                                                                    [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                                                                             [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED                                                                      [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED                                                                       [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED                                                                            [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED                                                            [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED                                                                  [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED                                                                   [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED                                                                 [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                                                                                   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED                                                                   [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                                                                              [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED                                                                          [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                                                                                    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED                                                           [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED                                                               [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED                                                         [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED                                                               [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                                                                                   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED                                                                     [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED                                                                       [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                                                                             [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED                                                                  [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED                                                                    [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED                                                        [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED                                                                     [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                                                                              [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                                                                             [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED                                                                        [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED                                                                    [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED                                                               [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED                                                                   [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED                                                                         [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED                                                                   [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED                                                [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED                                                              [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED                                                             [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED                                                 [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED                                                            [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED                                                     [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED                                           [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED                                               [100%]


**Số tests pass:42/ 42**

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

## Semantic Similarity Evaluation

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|------------|------------|----------|-------------|-------|
| 1 | Khoản chi từ 05 triệu đồng trở lên phải có chứng từ thanh toán không dùng tiền mặt. | Hóa đơn trên 5.000.000 VNĐ cần phải chuyển khoản ngân hàng mới được trừ chi phí. | High | 0.8245 | ✓ |
| 2 | Người lao động ủy quyền hợp pháp cho người khác nhận thay tiền lương. | Bùn nạo vét được cơ quan nhà nước xác định là khoáng sản chịu thuế. | Low | 0.1532 | ✓ |
| 3 | Cá nhân không cư trú nộp thuế TNCN 20% trên tổng thu nhập. | Người nước ngoài ở Việt Nam dưới 183 ngày bị áp mức thuế suất 20%. | High | 0.7891 | ✓ |
| 4 | Doanh nghiệp chế xuất thuê doanh nghiệp nội địa gia công hàng hóa. | Chi phí phát sinh trước khi thành lập công ty chưa được khấu trừ. | Low | 0.1124 | ✓ |
| 5 | Dự án đầu tư mở rộng hoàn thành giải ngân được miễn giảm thuế TNDN. | Đầu tư tăng công suất nhà máy sẽ không phải đóng thêm tiền thuế thu nhập. | High | 0.7456 | ✓ |

### Nhận xét

Kết quả đánh giá cho thấy mô hình embedding phân biệt tốt giữa các cặp câu có liên quan và không liên quan về mặt ngữ nghĩa. Các cặp câu mang cùng nội dung pháp lý hoặc cùng quy định thuế đạt điểm tương đồng cao (0.74–0.82), trong khi các cặp câu thuộc các chủ đề hoàn toàn khác nhau chỉ đạt mức tương đồng thấp (0.11–0.15).

Trong 5/5 trường hợp kiểm thử, dự đoán mức độ tương đồng (High/Low) đều phù hợp với điểm similarity thực tế, cho thấy embedding model hoạt động hiệu quả trên tập dữ liệu văn bản pháp lý và thuế.

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> *Viết 2-3 câu:*

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu queries trả về chunk relevant trong top-3?** __ / 5

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
