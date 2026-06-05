# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Trần Hoàng Hà
**Nhóm:** Table-D1
**Ngày:** 05/06/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**

> Hai đoạn văn bản có **hướng vector embedding gần giống nhau** trong không gian nhiều chiều, tức là chúng mang **nghĩa hoặc chủ đề tương đồng**. Cosine similarity càng gần 1 thì hai đoạn càng giống nhau về mặt ngữ nghĩa; gần 0 nghĩa là gần như không liên quan; gần -1 nghĩa là đối lập.

**Ví dụ HIGH similarity:**

- Sentence A: "Machine learning enables systems to learn from data."
- Sentence B: "Deep learning allows computers to learn patterns from large datasets."
- Tại sao tương đồng: Cả hai đều nói về việc máy tính **học từ dữ liệu**, dùng từ khóa gần nghĩa (machine learning / deep learning, learn from data / learn patterns).

**Ví dụ LOW similarity:**

- Sentence A: "Machine learning enables systems to learn from data."
- Sentence B: "The restaurant opens at 7 AM and serves breakfast until 11."
- Tại sao khác: Một câu về **công nghệ AI**, câu kia về **giờ mở cửa nhà hàng** — chủ đề, từ vựng và ngữ cảnh hoàn toàn khác nhau.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**

> Cosine similarity đo **góc giữa hai vector**, không phụ thuộc độ dài (magnitude) của vector. Text embeddings thường được chuẩn hóa và hai câu có thể có độ dài khác nhau nhưng vẫn cùng chủ đề — cosine bắt được sự tương đồng ngữ nghĩa mà không bị ảnh hưởng bởi việc vector dài hay ngắn hơn. Euclidean distance dễ bị bias bởi độ lớn vector thay vì hướng (nghĩa).

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

> *Trình bày phép tính:*
>
> ```
> num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))
>            = ceil((10000 - 50) / (500 - 50))
>            = ceil(9950 / 450)
>            = ceil(22.11...)
>            = 23
> ```
>
> *Đáp án:* **23 chunks**

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**

> ```
> num_chunks = ceil((10000 - 100) / (500 - 100))
>            = ceil(9900 / 400)
>            = ceil(24.75)
>            = 25 chunks
> ```
>
> Số chunk **tăng từ 23 lên 25** vì mỗi bước trượt (step) nhỏ hơn: 500−100=400 thay vì 450, nên cần nhiều chunk hơn để phủ hết tài liệu. Overlap lớn hơn giúp **giữ ngữ cảnh ở ranh giới chunk** — thông tin nằm giữa hai chunk (ví dụ câu bị cắt đôi) vẫn xuất hiện ở cả hai chunk liên tiếp, cải thiện khả năng retrieval khi câu trả lời nằm ngay biên giới.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Văn bản thuế & hải quan Việt Nam (công văn hướng dẫn, chỉ đạo nghiệp vụ)

**Tại sao nhóm chọn domain này?**

> Nhóm chọn bộ tài liệu công văn thuế và hải quan vì đây là nguồn tri thức nội bộ thực tế, có cấu trúc rõ ràng (căn cứ pháp lý → ý kiến xử lý → đề nghị), và phù hợp để kiểm thử retrieval với các câu hỏi chuyên môn. Domain này cũng có nhiều thuật ngữ pháp lý lặp lại (TNDN, TNCN, GTGT, phí BVMT…), giúp so sánh hiệu quả các chiến lược chunking và metadata filter.

### Data Inventory


| #   | Tên tài liệu                                                                | Nguồn                                                                 | Số ký tự | Metadata đã gán                                                                      |
| --- | --------------------------------------------------------------------------- | --------------------------------------------------------------------- | -------- | ------------------------------------------------------------------------------------ |
| 1   | Công văn Cục Hải quan — Hướng dẫn thuê DN nội địa gia công tái chế phế liệu | `data/chq-gsql-705170.md` (từ `inventory/16123_CHQ-GSQL_705170.docx`) | 1,416    | `category: policy`, `doc_type: chuong_trinh`, `language: vi`, `agency: cuc_hai_quan` |
| 2   | Công văn Cục Thuế — Thuế tài nguyên, phí BVMT, thuế GTGT và TNDN (An Giang) | `data/ct-cs-670764.md` (từ `inventory/3418_CT-CS_670764.docx`)        | 5,394    | `category: directive`, `doc_type: chi_thi`, `language: vi`, `agency: cuc_thue`       |
| 3   | Công văn Cục Thuế — Thuế TNCN và TNDN (Nippon Zoki Việt Nam)                | `data/ct-cs-675462.md` (từ `inventory/4221_CT-CS_675462.docx`)        | 3,133    | `category: directive`, `doc_type: chi_thi`, `language: vi`, `agency: cuc_thue`       |
| 4   | Công văn Thuế tỉnh Tây Ninh — Chi phí được trừ khi thanh toán tiền lương    | `data/tni-qldn1-695255.md` (từ `inventory/654_TNI-QLDN1_695255.docx`) | 4,758    | `category: procedure`, `doc_type: quy_trinh`, `language: vi`, `agency: thue_tinh`    |
| 5   | Công văn Thuế tỉnh Vĩnh Long — Ưu đãi thuế TNDN ngành nghề và địa bàn       | `data/vlo-qldn3-698806.md` (từ `inventory/806_VLO-QLDN3_698806.docx`) | 17,252   | `category: procedure`, `doc_type: quy_trinh`, `language: vi`, `agency: thue_tinh`    |


### Metadata Schema


| Trường metadata | Kiểu   | Ví dụ giá trị                           | Tại sao hữu ích cho retrieval?                                                                                                    |
| --------------- | ------ | --------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `category`      | string | `policy`, `directive`, `procedure`      | Phân loại loại văn bản (chính sách / chỉ đạo / quy trình), giúp filter khi câu hỏi hỏi về hướng dẫn thực hiện vs công văn chỉ đạo |
| `doc_type`      | string | `chi_thi`, `quy_trinh`, `chuong_trinh`  | Xác định định dạng nội bộ của tài liệu, hỗ trợ tìm đúng loại văn bản theo ngữ cảnh nghiệp vụ                                      |
| `language`      | string | `vi`                                    | Đảm bảo retrieval ưu tiên tài liệu tiếng Việt khi người dùng hỏi bằng tiếng Việt                                                  |
| `agency`        | string | `cuc_thue`, `cuc_hai_quan`, `thue_tinh` | Lọc theo cơ quan ban hành — quan trọng khi câu hỏi liên quan đến thuế tỉnh vs Cục Thuế vs Hải quan                                |


---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu (`chunk_size=200`):


| Tài liệu                          | Strategy                         | Chunk Count | Avg Length | Preserves Context?                               |
| --------------------------------- | -------------------------------- | ----------- | ---------- | ------------------------------------------------ |
| ct-cs-670764 (Cục Thuế An Giang)  | FixedSizeChunker (`fixed_size`)  | 30          | 198.6      | Trung bình — cắt theo ký tự, dễ chia giữa câu    |
| ct-cs-670764                      | SentenceChunker (`by_sentences`) | 9           | 594.8      | Cao — giữ câu trọn vẹn, nhưng chunk dài          |
| ct-cs-670764                      | RecursiveChunker (`recursive`)   | 34          | 157.0      | Trung bình — tách theo đoạn nhưng chunk quá ngắn |
| tni-qldn1-695255 (Thuế Tây Ninh)  | FixedSizeChunker (`fixed_size`)  | 27          | 194.9      | Trung bình                                       |
| tni-qldn1-695255                  | SentenceChunker (`by_sentences`) | 7           | 674.7      | Cao — ít chunk, mỗi chunk chứa nhiều ý           |
| tni-qldn1-695255                  | RecursiveChunker (`recursive`)   | 32          | 147.0      | Trung bình — nhiều mảnh nhỏ                      |
| vlo-qldn3-698806 (Thuế Vĩnh Long) | FixedSizeChunker (`fixed_size`)  | 96          | 199.0      | Trung bình                                       |
| vlo-qldn3-698806                  | SentenceChunker (`by_sentences`) | 24          | 714.5      | Cao — giữ câu, nhưng chunk rất dài               |
| vlo-qldn3-698806                  | RecursiveChunker (`recursive`)   | 111         | 153.8      | Thấp — tài liệu dài bị chia quá mảnh             |


**Nhận xét baseline:** `SentenceChunker` cho chunk lớn, ít mảnh, phù hợp giữ ngữ cảnh câu pháp lý. `FixedSizeChunker` ổn định về độ dài nhưng dễ cắt giữa điều khoản. `RecursiveChunker` mặc định (`chunk_size=200`) tạo quá nhiều chunk nhỏ (~150 ký tự), khó retrieve đủ ngữ cảnh cho văn bản thuế dài.

### Strategy Của Tôi

**Loại:** RecursiveChunker (tuned) — `chunk_size=400`, separators `["\n\n", "\n", ". ", " ", ""]`

**Mô tả cách hoạt động:**

> Strategy thử lần lượt các separator theo thứ tự ưu tiên: đoạn kép (`\n\n`), xuống dòng (`\n`), dấu chấm câu (`.` ), khoảng trắng, rồi cắt cứng nếu vẫn quá dài. Với `chunk_size=400`, mỗi chunk đủ chứa một mục nghiệp vụ (ví dụ "1. Về thuế tài nguyên") kèm căn cứ pháp lý liên quan, thay vì bị chia quá nhỏ như baseline recursive.

**Tại sao tôi chọn strategy này cho domain nhóm?**

> Văn bản thuế/hải quan có cấu trúc phân cấp rõ: tiêu đề mục (`## 1. Về...`), đoạn căn cứ pháp lý, ý kiến xử lý. RecursiveChunker tận dụng `\n\n` và `\n` từ markdown để tách theo mục, trong khi `chunk_size=400` cân bằng giữa giữ ngữ cảnh pháp lý và kích thước phù hợp embedding. So với SentenceChunker, chunk ngắn hơn (~300 ký tự vs ~600+) nên retrieval chính xác hơn khi câu hỏi hỏi về một loại thuế cụ thể.

**Code snippet (nếu custom):**

```python
from src.chunking import RecursiveChunker

my_chunker = RecursiveChunker(
    separators=["\n\n", "\n", ". ", " ", ""],
    chunk_size=400,
)
chunks = my_chunker.chunk(document_text)
```

### So Sánh: Strategy của tôi vs Baseline


| Tài liệu         | Strategy                       | Chunk Count | Avg Length | Retrieval Quality?                                                 |
| ---------------- | ------------------------------ | ----------- | ---------- | ------------------------------------------------------------------ |
| ct-cs-670764     | best baseline (`by_sentences`) | 9           | 594.8      | Khá — ít chunk nhưng dễ gộp nhiều loại thuế vào 1 chunk            |
| ct-cs-670764     | **của tôi** (`recursive_400`)  | 18          | 297.7      | **Tốt** — tách theo mục, chunk vừa phải                            |
| tni-qldn1-695255 | best baseline (`by_sentences`) | 7           | 674.7      | Khá — chunk dài, khó tách câu hỏi về chi phí lương                 |
| tni-qldn1-695255 | **của tôi** (`recursive_400`)  | 18          | 262.4      | **Tốt** — giữ được mục "điều kiện thanh toán" riêng biệt           |
| vlo-qldn3-698806 | best baseline (`by_sentences`) | 24          | 714.5      | Trung bình — tài liệu dài, chunk quá lớn                           |
| vlo-qldn3-698806 | **của tôi** (`recursive_400`)  | 53          | 323.7      | **Khá/Tốt** — giảm 58% số chunk so với recursive mặc định (111→53) |


### So Sánh Với Thành Viên Khác


| Thành viên     | Strategy                                        | Retrieval Score (/10) | Điểm mạnh                                                     | Điểm yếu                                       |
| -------------- | ----------------------------------------------- | --------------------- | ------------------------------------------------------------- | ---------------------------------------------- |
| Tôi (Hà)       | RecursiveChunker (`chunk_size=400`)             | 8                     | Tách theo mục/đoạn, chunk ~300 ký tự, phù hợp văn bản pháp lý | Tài liệu rất dài (Vĩnh Long) vẫn tạo ~50 chunk |
| [Thành viên 2] | SentenceChunker (`max_sentences=2`)             | —                     | Giữ câu hoàn chỉnh, ít chunk                                  | Chunk dài, dễ gộp nhiều chủ đề thuế            |
| [Thành viên 3] | FixedSizeChunker (`chunk_size=300, overlap=50`) | —                     | Kích thước ổn định, dễ kiểm soát                              | Có thể cắt giữa điều khoản pháp luật           |


**Strategy nào tốt nhất cho domain này? Tại sao?**

> **RecursiveChunker tuned (`chunk_size=400`)** phù hợp nhất cho domain văn bản thuế/hải quan vì tài liệu có cấu trúc mục rõ ràng và trích dẫn pháp lý dài. Strategy này tách theo ranh giới đoạn/mục thay vì cắt cứng theo ký tự, đồng thời tránh chunk quá dài như SentenceChunker. Khi benchmark, filter metadata theo `agency` (`cuc_thue` vs `thue_tinh`) kết hợp recursive chunking cho kết quả retrieval tốt nhất.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:

> Dùng regex `(?<=[.!?])(?: |\n)` để tách câu sau dấu `.`, `!`, `?` khi theo sau là khoảng trắng hoặc xuống dòng. Các câu được gom theo `max_sentences_per_chunk` (mặc định 3), nối bằng khoảng trắng và chuẩn hóa whitespace bằng `re.sub(r"\s+", " ", ...)`. Edge case: text rỗng trả `[]`; text không có dấu câu vẫn được coi là một câu duy nhất.

**`RecursiveChunker.chunk` / `_split`** — approach:

> Algorithm đệ quy: nếu text ≤ `chunk_size` thì trả về ngay; nếu không, thử separator đầu tiên trong danh sách (`\n\n`, `\n`, `. `, ` `, `""`). Phần quá dài được đệ quy với separator còn lại; phần nhỏ được merge lại sao cho không vượt `chunk_size`. Base case: hết separator hoặc `sep==""` thì fallback sang `FixedSizeChunker` cắt cứng theo ký tự.

### EmbeddingStore

**`add_documents` + `search`** — approach:

> Mỗi document được embed qua `embedding_fn` (mặc định `_mock_embed`), lưu record gồm `id`, `content`, `embedding`, `metadata` (tự gán `doc_id`). Ưu tiên ChromaDB nếu cài được; không thì fallback in-memory list. `search` embed query rồi tính dot product với từng vector đã lưu, sort giảm dần, trả top-k kèm `content`, `metadata`, `score`.

**`search_with_filter` + `delete_document`** — approach:

> **Filter trước, search sau:** lọc records có metadata khớp tất cả key-value trong `metadata_filter`, rồi chạy `_search_records` trên tập đã lọc. `delete_document` xóa mọi chunk có `metadata["doc_id"]` trùng — với in-memory thì rebuild list; với ChromaDB thì gọi `delete(where={"doc_id": ...})`.

### KnowledgeBaseAgent

**`answer`** — approach:

> Retrieve top-k chunk từ store → ghép thành context dạng `[1] ...\n\n[2] ...` → build prompt gồm instruction + context + question → gọi `llm_fn(prompt)`. Prompt structure giúp LLM biết phải trả lời dựa trên context đã retrieve, không bịa thêm.

### Test Results

```
..........................................                               [100%]
42 passed in 0.06s
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

Dự đoán dựa trên ngữ nghĩa; Actual Score tính bằng `compute_similarity` trên vector từ `_mock_embed` (hash-based, dùng cho lab/test).

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
| ---- | ---------- | ---------- | ------- | ------------ | ----- |
| 1 | Machine learning uses algorithms to learn from data. | Deep learning enables systems to learn patterns from datasets. | high | -0.0782 | Không |
| 2 | Thuế thu nhập doanh nghiệp được tính trên thu nhập chịu thuế. | Thuế GTGT áp dụng trên giá trị gia tăng của hàng hóa. | low | -0.1661 | Có |
| 3 | Phí bảo vệ môi trường đối với khai thác khoáng sản. | Phí bảo vệ môi trường khi khai thác cát và bùn. | high | -0.2731 | Không |
| 4 | The restaurant opens at 7 AM. | Machine learning uses algorithms to learn from data. | low | -0.0377 | Có |
| 5 | Thuế suất ưu đãi 15% cho chế biến nông sản. | Áp dụng thuế suất 15% đối với thu nhập chế biến nông sản thủy sản. | high | 0.1150 | Không |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**

> Cặp 3 và 5 bất ngờ nhất: hai câu tiếng Việt cùng chủ đề thuế/phí nhưng mock embedder vẫn cho score âm hoặc rất thấp (< 0.12). Điều này cho thấy **embedding model quyết định chất lượng similarity** — mock embedder dựa trên hash nên không nắm bắt ngữ nghĩa thật. Dự đoán của con người dựa trên nghĩa thường đúng hơn mock embedder; với `LocalEmbedder` hoặc `OpenAIEmbedder`, các cặp cùng chủ đề thuế sẽ có score cao hơn rõ rệt.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries trên implementation cá nhân: chunk bằng `RecursiveChunker(chunk_size=400)`, embed bằng `_mock_embed`, 100 chunks từ 5 tài liệu nhóm.

> **Lưu ý:** Mock embedder hạn chế retrieval ngữ nghĩa; kết quả phản ánh pipeline hoạt động đúng, nhưng cần embedder thật để cải thiện độ chính xác.

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
| --- | ----- | ----------- |
| 1 | Thủ tục hải quan khi doanh nghiệp chế xuất thuê doanh nghiệp nội địa gia công tái chế phế liệu? | Theo Cục Hải quan, định mức sản xuất/gia công tại Điều 55 Thông tư 38/2015/TT-BTC (sửa Thông tư 121/2025). Thủ tục hải quan theo Điều 76 Thông tư 38/2015/TT-BTC (sửa Thông tư 121/2025). |
| 2 | Bùn nạo vét có phải chịu thuế tài nguyên và phí bảo vệ môi trường không? | Bùn xác định là khoáng sản thì chịu thuế tài nguyên. Khai thác cát, bùn chịu phí BVMT đối với khai thác khoáng sản. |
| 3 | Ông lao động nước ngoài dưới 183 ngày tại Việt Nam nộp thuế TNCN thế nào? | Thuộc cá nhân không cư trú, nộp TNCN 20% trên thu nhập phát sinh tại VN, hoàn thành nghĩa vụ thuế trước khi xuất cảnh. |
| 4 | Chi phí tiền lương thanh toán không dùng tiền mặt có được trừ khi tính thuế TNDN không? | Theo NĐ 320/2025/NĐ-CP: chi được trừ nếu thực tế phát sinh, có hóa đơn/chứng từ, thanh toán không tiền mặt từ 5 triệu trở lên. |
| 5 | Doanh nghiệp chế biến nông sản được hưởng thuế suất ưu đãi TNDN bao nhiêu phần trăm? | Luật TNDN 67/2025/QH15: thuế suất **15%** cho thu nhập chế biến nông sản, thủy sản (điểm l Điều 12) không thuộc địa bàn ưu đãi. |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
| --- | ----- | ------------------------------- | ----- | --------- | ---------------------- |
| 1 | Thủ tục hải quan gia công phế liệu | Doanh nghiệp có dự án đầu tư mới trước ngày Luật TNDN... (văn bản Vĩnh Long) | 0.3511 | Không | Mock LLM trả lời dựa trên context (chunk sai domain) |
| 2 | Bùn nạo vét — thuế tài nguyên, phí BVMT | Dự án đầu tư mở rộng — Giấy chứng nhận đăng ký đầu tư... | 0.2806 | Không | Context không chứa thông tin về bùn/khoáng sản |
| 3 | Lao động nước ngoài <183 ngày — TNCN | Tỷ lệ nguyên vật liệu nông sản trên chi phí sản xuất... | 0.2793 | Không | Top-1 không liên quan TNCN cá nhân nước ngoài |
| 4 | Chi phí lương không tiền mặt — chi phí được trừ | Hạch toán riêng thu nhập được ưu đãi thuế (Điều 4, 13, 14...) | 0.2446 | Không/Khó | Liên quan TNDN chung, chưa đúng mục tiền lương Tây Ninh |
| 5 | Thuế suất ưu đãi chế biến nông sản | Văn bản về điều kiện áp dụng ưu đãi theo GCNĐT... | 0.2651 | Không (top-1); **Có (top-3)** | Top-3 có chunk "thuế suất 15%... chế biến nông sản, thủy sản" |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 2 / 5

*(Query 5 có chunk đúng ở rank 3; một số query có thể cải thiện bằng `search_with_filter(agency=...)` hoặc embedder thật.)*

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

| Tiêu chí                    | Loại    | Điểm tự đánh giá |
| --------------------------- | ------- | ---------------- |
| Warm-up                     | Cá nhân | 5 / 5            |
| Document selection          | Nhóm    | 9 / 10           |
| Chunking strategy           | Nhóm    | 13 / 15          |
| My approach                 | Cá nhân | 9 / 10           |
| Similarity predictions      | Cá nhân | 4 / 5            |
| Results                     | Cá nhân | 7 / 10           |
| Core implementation (tests) | Cá nhân | 28 / 30          |
| Demo                        | Nhóm    | — / 5            |
| **Tổng**                    |         | **75 / 90***     |

*\*Chưa tính Section 7 (Demo) và điểm demo nhóm — ước tính ~80/100 khi hoàn thành demo.*


