# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** **Nguyễn Hồ Diệu Linh**

**Nhóm:** **Table D1**

**Ngày:** **05/06/2026**

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> **High cosine similarity (độ tương đồng cosine cao, tiến gần về giá trị 1) nghĩa là** hai vector embedding hướng về cùng một phía trong không gian vector đa chiều. Trong xử lý ngôn ngữ tự nhiên (NLP), điều này biểu thị hai đoạn văn bản có **sự tương đồng rất lớn về mặt ngữ nghĩa, ngữ cảnh hoặc chủ đề**, ngay cả khi chúng không sử dụng chung các từ ngữ cụ thể hoặc được viết bằng các ngôn ngữ khác nhau.

**Ví dụ HIGH similarity:**
- Sentence A: *"Học máy là một nhánh quan trọng của trí tuệ nhân tạo."*
- Sentence B: *"Machine learning đóng vai trò cốt lõi trong sự phát triển của AI."*
- Tại sao tương đồng: Cả hai câu sử dụng tập từ vựng khác nhau (một câu thuần Việt, một câu đan xen thuật ngữ tiếng Anh) nhưng đều truyền tải chung một nội dung cốt lõi: mối quan hệ phụ thuộc và tầm quan trọng của Machine Learning đối với AI.

**Ví dụ LOW similarity:**
- Sentence A: *"Học máy là một nhánh quan trọng của trí tuệ nhân tạo."*
- Sentence B: *"Hôm nay thời tiết Hà Nội rất đẹp và thích hợp để đi dạo."*
- Tại sao khác: Hai câu này hoàn toàn không có sự giao thoa nào về mặt ngữ cảnh hay chủ đề; một câu thuộc lĩnh vực khoa học máy tính, câu còn lại nói về thời tiết và hoạt động đời sống.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> *Cosine similarity* được ưu tiên vì nó chỉ đo góc giữa hai vector mà **không bị ảnh hưởng bởi độ dài (độ lớn)** của chúng, giúp tập trung hoàn toàn vào việc đánh giá sự tương đồng về mặt ngữ nghĩa. Ngược lại, Euclidean distance chịu ảnh hưởng nặng nề bởi độ dài văn bản, khiến hai đoạn văn có cùng nội dung nhưng khác nhau về số lượng từ (độ dài vector khác nhau) bị đánh giá sai lệch là không tương đồng.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> *Đáp án:*

> Gọi:
> - $N = 10,000$ (Tổng số ký tự)
> - $C = 500$ (Kích thước mỗi chunk - `chunk_size`)
> - $O = 50$ (Độ dài phần trùng lặp - `overlap`)

> Mỗi dịch chuyển của một chunk mới (bước nhảy thực tế) có độ dài là: 
> $$C - O = 500 - 50 = 450 \text{ ký tự}$$

> Áp dụng công thức tính tổng số lượng chunks (lấy hàm trần $\lceil \dots \rceil$):
> $$\text{Number of chunks} = \left\lceil \frac{N - O}{C - O} \right\rceil = \left\lceil \frac{10000 - 50}{500 - 50} \right\rceil = \left\lceil \frac{9950}{450} \right\rceil = \left\lceil 22.11 \right\rceil = 23$$

> *Đáp án:* **23 chunks**

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> *Viết 1-2 câu:*
> Khi `overlap` tăng từ 50 lên 100, kích thước bước nhảy giữa các chunk giảm xuống ($500 - 100 = 400$ ký tự), dẫn đến **tổng số lượng chunks tăng lên** (cụ thể là $\lceil 9900 / 400 \rceil = 25$ chunks). 

> Chúng ta muốn tăng `overlap` để **tránh việc ngữ cảnh bị cắt đứt đột ngột tại ranh giới giữa các chunk**, giúp các thông tin mang tính liên kết logic, ngữ pháp hoặc đại từ thay thế không bị mất đi, từ đó tối ưu hóa chất lượng truy vấn cho mô hình RAG.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** [ví dụ: Customer support FAQ, Vietnamese law, cooking recipes, ...]

**Tại sao nhóm chọn domain này?**
> *Viết 2-3 câu:*

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| | | | |
| | | | |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| | FixedSizeChunker (`fixed_size`) | | | |
| | SentenceChunker (`by_sentences`) | | | |
| | RecursiveChunker (`recursive`) | | | |

### Strategy Của Tôi

**Loại:** [FixedSizeChunker / SentenceChunker / RecursiveChunker / custom strategy]

**Mô tả cách hoạt động:**
> *Viết 3-4 câu: strategy chunk thế nào? Dựa trên dấu hiệu gì?*

**Tại sao tôi chọn strategy này cho domain nhóm?**
> *Viết 2-3 câu: domain có pattern gì mà strategy khai thác?*

**Code snippet (nếu custom):**
```python
# Paste implementation here
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| | best baseline | | | |
| | **của tôi** | | | |

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

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> *Viết 2-3 câu: dùng regex gì để detect sentence? Xử lý edge case nào?*

**`RecursiveChunker.chunk` / `_split`** — approach:
> *Viết 2-3 câu: algorithm hoạt động thế nào? Base case là gì?*

### EmbeddingStore

**`add_documents` + `search`** — approach:
> *Viết 2-3 câu: lưu trữ thế nào? Tính similarity ra sao?*

**`search_with_filter` + `delete_document`** — approach:
> *Viết 2-3 câu: filter trước hay sau? Delete bằng cách nào?*

### KnowledgeBaseAgent

**`answer`** — approach:
> *Viết 2-3 câu: prompt structure? Cách inject context?*

### Test Results

```
# Paste output of: pytest tests/ -v
```

**Số tests pass:** __ / __

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | | | high / low | | |
| 2 | | | high / low | | |
| 3 | | | high / low | | |
| 4 | | | high / low | | |
| 5 | | | high / low | | |

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
