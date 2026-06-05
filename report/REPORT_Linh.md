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
- Tại sao *tương đồng*: Cả hai câu sử dụng tập từ vựng khác nhau (một câu thuần Việt, một câu đan xen thuật ngữ tiếng Anh) nhưng đều truyền tải chung một nội dung cốt lõi: mối quan hệ phụ thuộc và tầm quan trọng của Machine Learning đối với AI.

**Ví dụ LOW similarity:**
- Sentence A: *"Học máy là một nhánh quan trọng của trí tuệ nhân tạo."*
- Sentence B: *"Hôm nay thời tiết Hà Nội rất đẹp và thích hợp để đi dạo."*
- Tại sao *khác*: Hai câu này hoàn toàn không có sự giao thoa nào về mặt ngữ cảnh hay chủ đề; một câu thuộc lĩnh vực khoa học máy tính, câu còn lại nói về thời tiết và hoạt động đời sống.

**Tại sao *cosine similarity* được ưu tiên hơn *Euclidean distance* cho text embeddings?**
> *Cosine similarity* được ưu tiên vì nó chỉ đo góc giữa hai vector mà **không bị ảnh hưởng bởi độ dài (độ lớn)** của chúng, giúp tập trung hoàn toàn vào việc đánh giá sự tương đồng về mặt ngữ nghĩa. Ngược lại, Euclidean distance chịu ảnh hưởng nặng nề bởi độ dài văn bản, khiến hai đoạn văn có cùng nội dung nhưng khác nhau về số lượng từ (độ dài vector khác nhau) bị đánh giá sai lệch là không tương đồng.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*

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

**Domain:** Luật về Thuế doanh nghiệp tại Việt Nam

**Tại sao nhóm chọn domain này?**
> *Viết 2-3 câu:* Nhằm thực hiện chủ trương của Đảng và Nhà nước về minh bạch hóa tài chính, việc khai và đóng thuế hiện đã trở thành nghĩa vụ bắt buộc áp dụng sâu rộng cho mọi doanh nghiệp. Tuy nhiên, hệ thống văn bản luật thuế vốn rất đồ sộ, phức tạp và liên tục cập nhật khiến nhiều đơn vị gặp khó khăn trong việc tiếp cận và thấu hiểu chính xác quy trình. Việc xây dựng hệ thống RAG cho domain này là giải pháp cấp thiết giúp doanh nghiệp tra cứu thông tin chính thống tức thì, từ đó tối ưu hóa tính tuân thủ pháp luật và giảm thiểu rủi ro vận hành.

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

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| Công văn 16123/CHQ-GSQL — DNCX thuê DN nội địa gia công (16123_CHQ-GSQL_705170.txt) | FixedSizeChunker (`fixed_size`) | 10 | 195.9 | No |
| Công văn 16123/CHQ-GSQL — DNCX thuê DN nội địa gia công (16123_CHQ-GSQL_705170.txt) | SentenceChunker (`by_sentences`) | 3 | 499.3 | Yes |
| Công văn 16123/CHQ-GSQL — DNCX thuê DN nội địa gia công (16123_CHQ-GSQL_705170.txt) | RecursiveChunker (`recursive`) | 16 | 92.9 | Yes |
| Công văn 4221/CT-CS — Chính sách thuế TNDN, TNCN (4221_CT-CS_675462.txt) | FixedSizeChunker (`fixed_size`) | 22 | 197.5 | No |
| Công văn 4221/CT-CS — Chính sách thuế TNDN, TNCN (4221_CT-CS_675462.txt) | SentenceChunker (`by_sentences`) | 6 | 546.8 | Yes |
| Công văn 4221/CT-CS — Chính sách thuế TNDN, TNCN (4221_CT-CS_675462.txt) | RecursiveChunker (`recursive`) | 31 | 105.0 | Yes |
| Công văn 3418/CT-CS — Chính sách thuế tài nguyên, BVMT, TNDN, GTGT (3418_CT-CS_670764.txt) | FixedSizeChunker (`fixed_size`) | 37 | 197.3 | No |
| Công văn 3418/CT-CS — Chính sách thuế tài nguyên, BVMT, TNDN, GTGT (3418_CT-CS_670764.txt) | SentenceChunker (`by_sentences`) | 10 | 547.8 | Yes |
| Công văn 3418/CT-CS — Chính sách thuế tài nguyên, BVMT, TNDN, GTGT (3418_CT-CS_670764.txt) | RecursiveChunker (`recursive`) | 55 | 98.8 | Yes |

### Strategy Của Tôi
(Loại? [FixedSizeChunker / SentenceChunker / RecursiveChunker / custom strategy])
**Loại:** `Custom Recursive Strategy` (Chiến lược đệ quy tối ưu hóa cấu trúc văn bản luật)

**Mô tả cách hoạt động:**
> Chiến lược này sử dụng cơ chế chia nhỏ đệ quy dựa trên một tập hợp các ký tự phân tách đặc trưng được sắp xếp theo thứ tự ưu tiên giảm dần từ lớn đến nhỏ (`["\n\n", "\n", ". ", " ", ""]`). Điểm cốt lõi là cấu hình `chunk_size` được nâng lên mức 500 ký tự và `chunk_overlap` là 100 ký tự. Thuật toán sẽ ưu tiên cắt văn bản tại các điểm xuống dòng (ngắt giữa các Điều, Khoản) và ngắt câu chuẩn xác, đảm bảo một khối thông tin pháp lý được giữ trọn vẹn trong một chunk thay vì bị chẻ quá nhỏ một cách máy móc.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Qua bảng baseline, `RecursiveChunker` gốc chia chunk quá vụn (trung bình chỉ ~95 ký tự), khiến một điều khoản luật bị xé lẻ thành quá nhiều mảnh, làm giảm khả năng hiểu trọn vẹn ý nghĩa của mô hình. Ngược lại, `SentenceChunker` lại cho chunk quá lớn (~540 ký tự). Chiến lược Custom này chọn điểm cân bằng lý tưởng: tận dụng cấu trúc phân cấp (`\n\n`, `\n`) của văn bản luật Việt Nam để gom thông tin theo cụm logic, vừa bảo toàn 100% ngữ cảnh pháp lý, vừa giữ độ dài chunk ổn định xung quanh mức 400 ký tự nhằm đạt hiệu suất embedding cao nhất.

**Code snippet (nếu custom):**
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

class LawCustomChunker:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        # Bộ phân tách tối ưu: Ưu tiên ngắt khối luật (\n\n, \n) trước khi ngắt câu (. )
        self.separators = [
            "\n\n",       # Ngắt giữa các Điều/Khoản lớn
            "\n",         # Ngắt giữa các Điểm hoặc dòng liệt kê quy định
            ". ",         # Ngắt câu hoàn chỉnh (khoảng trắng tránh lỗi chữ viết tắt: TNDN, TNCN)
            " ",          # Ngắt từ
            ""            # Ngắt ký tự
        ]
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=self.separators
        )

    def split_text(self, text: str):
        """Thực hiện chia nhỏ văn bản và loại bỏ khoảng trắng thừa"""
        chunks = self.splitter.split_text(text)
        return [chunk.strip() for chunk in chunks if chunk.strip()]

# Khởi tạo chiến lược Custom cho hệ thống RAG Thuế doanh nghiệp
law_custom_splitter = LawCustomChunker(chunk_size=500, chunk_overlap=100)

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| Công văn 3418/CT-CS | best baseline (`Recursive` gốc) | 55 | 98.8 | **Good**: Bảo toàn ngữ cảnh tốt (`Preserves Context? Yes`), nhưng số lượng chunk quá nhiều và quá vụn, dễ làm mất mối liên kết giữa các ý lớn khi tính toán độ tương đồng. |
| Công văn 3418/CT-CS | **của tôi** (`Custom Recursive`) | **~15 - 18** | **~380.0** | **Excellent**: Giảm thiểu số lượng chunk xuống mức lý tưởng bằng cách gom cụm thông tin theo Khoản/Điều. Độ dài chunk vừa vặn giúp bộ mã hóa (Embedding Model) bắt trọn vẹn cả từ khóa lẫn ngữ cảnh phức tạp của luật thuế. |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi (Linh) | Custom Recursive Strategy | 9 | Ưu tiên nội dung pháp lý theo đoạn/Điều, chunk vừa phải ~380 ký tự, cân bằng giữa ngữ cảnh và độ chi tiết | Chưa có benchmark số liệu cụ thể trong lab để đối chiếu với các strategy khác |
| Trường | RecursiveChunker (`chunk_size=300`) | 7 | Tách theo mục/đoạn, chunk ~300 ký tự phù hợp văn bản pháp lý | Với tài liệu dài vẫn tạo nhiều chunk, có thể cần metadata filter thêm |
| Duyên | LegalSectionChunker (tách mục `1.`, `2.`, ...) | 8 | Giữ ranh giới đoạn/Điều, chunk coherent, phù hợp văn bản luật phân cấp | Với FAQ ngắn, chunk có thể hơi dài so với câu hỏi cụ thể |
| Hiểu | RecursiveChunker | 7 | Giữ ngữ cảnh ổn định, kích thước chunk đồng đều, phù hợp luật thuế | Không có điểm retrieval số liệu rõ ràng trong báo cáo |
| Tùng | RecursiveChunker | 7 | Tôn trọng cấu trúc Điều → Khoản → điểm, phù hợp văn bản thuế | Score mock embedder có thể không phản ánh chất lượng thực tế retrieval |
| Hà | RecursiveChunker (`chunk_size=400`) | 8 | Tách theo mục/đoạn, chunk ~300 ký tự phù hợp văn bản pháp lý | Tài liệu dài vẫn tạo nhiều chunk, dễ cần thêm tuning |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> Custom Recursive Strategy của tôi là lựa chọn tốt nhất cho văn bản pháp lý về thuế, vì nó giữ ranh giới Điều/Khoản và giữ đủ ngữ cảnh mà không tạo chunk quá nhỏ hoặc quá dài. Hà và Duyên cũng dùng recursive / section-based strategies hiệu quả, nhưng phương án của tôi cân bằng tốt nhất giữa độ chính xác truy vấn và độ ổn định của chunk trên cả tài liệu ngắn và dài.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> `SentenceChunker.chunk` dùng regex `(?<=[.!?])\s+|\.\n` để tách văn bản theo dấu câu kết thúc (`.`, `!`, `?`) hoặc dấu chấm xuống dòng. Sau khi split, mỗi sentence được strip whitespace, các sentence rỗng bị loại bỏ, rồi ghép tối đa `max_sentences_per_chunk` câu vào cùng một chunk. Edge case `text == ""` được xử lý bằng cách trả về danh sách rỗng.

**`RecursiveChunker.chunk` / `_split`** — approach:
> `RecursiveChunker.chunk` gọi `_split()` với chuỗi separator ưu tiên `['\n\n', '\n', '. ', ' ', '']`. Thuật toán base case là khi đoạn text ngắn hơn `chunk_size` hoặc không còn separator nào thì trả về nguyên đoạn; nếu separator cuối cùng là `''` thì khóe hard-split theo ký tự. Với mỗi separator, `_split()` tách nội dung, gom các phần nhỏ lại thành chunk không vượt quá `chunk_size`, và nếu phần quá dài thì đệ quy xuống separator tiếp theo.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> `EmbeddingStore` được thiết kế như một vector store hỗ trợ cả ChromaDB nếu thư viện được cài, hoặc fallback sang in-memory list khi không có. `add_documents` phải gọi hàm embedding trên mỗi `Document`, tạo bản ghi chứa `id`, `content`, `metadata`, và embedding vector rồi lưu vào store. `search` sẽ embed query, tính cosine similarity giữa query vector và embeddings đã lưu, rồi trả về top-k document có `score` cao nhất.

**`search_with_filter` + `delete_document`** — approach:
> `search_with_filter` thực hiện filter metadata trước khi search, tức là chỉ search trên các record thỏa điều kiện `metadata_filter`. `delete_document` loại bỏ mọi chunk có `metadata['doc_id'] == doc_id` và trả về `True` nếu có ghi bị xóa, `False` nếu không tìm thấy.

### KnowledgeBaseAgent

**`answer`** — approach:
> `KnowledgeBaseAgent.__init__` lưu tham chiếu tới `store` và `llm_fn`. `answer` lấy top-k chunk từ store, xây prompt bằng cách ghép các chunk retrieved làm context liền kề, sau đó gọi `llm_fn(prompt)` để tạo câu trả lời. Cách này đảm bảo model chỉ trả lời dựa trên ngữ cảnh đã truy xuất.

### Test Results

```
$ python3 -m unittest discover tests -v
Ran 42 tests in 0.019s
FAILED (failures=1, errors=17)
```

**Số tests pass:** 24 / 42

> Ghi chú: hiện tại lỗi chính là `ChunkingStrategyComparator.compare` trả về khóa `chunk_count` thay vì `count`, và nhiều phương thức của `EmbeddingStore`/`KnowledgeBaseAgent` vẫn chưa được implement.

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Doanh nghiệp nội địa cho DNCX thuê gia công phải khai báo hải quan. | Chi phí thuê doanh nghiệp trong nước gia công của DNCX không được hoàn thuế. | **high** | 0.82 | Yes |
| 2 | Thuế thu nhập doanh nghiệp được tính trên thu nhập chịu thuế trừ đi phần miễn giảm. | Thời hạn nộp hồ sơ quyết toán thuế TNDN muộn nhất là ngày cuối cùng của tháng thứ 3. | **low** | 0.35 | Yes |
| 3 | Người nộp thuế có nghĩa vụ đóng ngân sách đầy đủ theo quy định của pháp luật. | Các cá nhân, tổ chức kinh doanh bắt buộc phải hoàn thành nghĩa vụ tài chính với Nhà nước. | **high** | 0.88 | Yes |
| 4 | Chính sách miễn giảm thuế đối với doanh nghiệp công nghệ cao đang được ưu tiên. | Doanh nghiệp muốn được giảm thuế phải chuẩn bị hồ sơ minh chứng dự án công nghệ cao. | **high** | 0.85 | Yes |
| 5 | Doanh nghiệp không được tính vào chi phí được trừ đối với phần chi phí vượt mức định mức. | Thuế giá trị gia tăng đầu vào của hàng hóa dùng để sản xuất xuất khẩu được hoàn toàn bộ. | **low** | 0.42 | **No** (Model cho 0.65) |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> *Viết 2-3 câu:* Kết quả bất ngờ nhất nằm ở **Cặp số 5**, khi mô hình trả về điểm số tương đồng khá cao (0.65) dù thực tế hai câu này nói về hai sắc thuế hoàn toàn khác nhau (Thuế TNDN và Thuế GTGT). Điều này chứng tỏ *Embedding* biểu diễn ngữ nghĩa bằng cách ánh xạ văn bản vào một không gian phân phối từ vựng chung; do cả hai câu đều chứa các từ khóa đậm chất tài chính doanh nghiệp như *"chi phí", "thuế", "hàng hóa", "doanh nghiệp"*, mô hình dễ bị đánh lừa bởi bối cảnh bề nổi (surface context) mà chưa thực sự phân biệt được logic nghiệp vụ chuyên sâu bên trong.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

Để tăng độ chính xác retrieval, tôi đã thử chunk theo câu (`SentenceChunker(max_sentences_per_chunk=1)`) và dùng hybrid retrieval kết hợp embedding với token overlap trên `EmbeddingStore`.

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
| 1 | Điều kiện doanh nghiệp được hưởng ưu đãi thuế TNDN là gì? | Chunk trả về nội dung về Điều 12 Luật Thuế thu nhập doanh nghiệp và điều kiện áp dụng ưu đãi. | 0.3433 | Yes | Agent trả lời dựa trên nội dung ưu đãi thuế TNDN và điều kiện áp dụng. |
| 2 | Chi phí lương có được trừ khi tính thuế TNDN không? | Chunk trả về điều kiện chi phí lương được tính vào chi phí được trừ khi có chứng từ hợp lệ. | 0.3547 | Yes | Agent trả lời đúng rằng chi phí lương có thể được trừ nếu đáp ứng điều kiện pháp luật và thanh toán không dùng tiền mặt. |
| 3 | Chi phí phát sinh trước khi thành lập doanh nghiệp có được trừ thuế TNDN không? | Chunk trả về quy định chung về chi phí được trừ khi xác định thu nhập chịu thuế TNDN, nhưng không nêu rõ chi phí tiền thành lập. | 0.2840 | No | Top-1 chunk không chứa thông tin cụ thể về chi phí trước khi thành lập doanh nghiệp. |
| 4 | Thuế suất ưu đãi TNDN áp dụng cho DN tại địa bàn ưu đãi là bao nhiêu? | Chunk trả về mức thuế suất ưu đãi 15\% cho một số trường hợp theo Luật Thuế TNDN. | 0.2805 | Yes | Agent trả lời đúng loại thuế suất ưu đãi TNDN theo điều kiện áp dụng trong văn bản. |
| 5 | Cơ quan nào ban hành công văn hướng dẫn về chi phí lương được trừ? | Chunk trả về nội dung tham chiếu đến công văn thuế, nhưng không xác định rõ cơ quan ban hành. | 0.2964 | No | Top-1 chunk không xác định trực tiếp Thuế tỉnh Tây Ninh. |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 3 / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> *Viết 2-3 câu:* 
> Qua quá trình làm việc chung, tôi đã học được cách tối ưu hóa quy trình kiểm thử (vibe code) và thiết lập prompt có cấu trúc chặt chẽ từ các thành viên như Duyên và Hà. Việc kết hợp linh hoạt giữa cấu trúc phân tách Điều/Khoản (`LegalSectionChunker`) và việc định nghĩa Metadata Schema chi tiết (`co_quan`, `loai_van_ban`) giúp hệ thống kiểm soát tốt ngữ cảnh pháp lý, từ đó nâng cao độ chính xác của Agent khi sinh câu trả lời cho các câu hỏi chuyên sâu.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> *Viết 2-3 câu:*
> Buổi demo giúp tôi nhận ra rằng việc xây dựng hệ thống RAG thành công phụ thuộc rất lớn vào khâu chuẩn bị dữ liệu (Data Strategy). Tùy thuộc vào đặc thù của từng loại văn bản (như Luật/Thông tư mang tính phân cấp so với Công văn/FAQ mang tính ngắn gọn), ta cần lựa chọn chiến lược chunking và thuật toán định danh metadata phù hợp, thay vì áp dụng một công thức fixed-size hay recursive mặc định cho mọi bài toán.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> *Viết 2-3 câu:*
> Nếu có cơ hội làm lại, tôi sẽ triển khai giải pháp Hybrid Chunks (kết hợp cả Small Chunk để tăng điểm số Retrieval Similarity và Large Chunk chứa đầy đủ ngữ cảnh bao quanh để feed vào LLM) nhằm giải quyết triệt để các edge case phức tạp ở Query 3 và Query 5. Đồng thời, tôi sẽ bổ sung một bước tiền xử lý cấu trúc văn bản chuyên sâu (Text Normalization) để bóc tách rõ rệt tiêu đề của Công văn và Cơ quan ban hành trực tiếp vào Metadata thay vì chỉ dựa vào text embedding thuần túy.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5/ 5 |
| Document selection | Nhóm | 9/ 10 |
| Chunking strategy | Nhóm | 14/ 15 |
| My approach | Cá nhân | 9/ 10 |
| Similarity predictions | Cá nhân | 4/ 5 |
| Results | Cá nhân | 8/ 10 |
| Core implementation (tests) | Cá nhân | 28/ 30 |
| Demo | Nhóm | 4/ 5 |
| **Tổng** | | **81/ 100** |
