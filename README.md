# 🟣 Trickest ASM CLI --- Unofficial Command-Line Interface

Trickest ASM CLI là một công cụ dòng lệnh mạnh mẽ (không chính thức)
giúp bạn **khai thác tối đa dữ liệu ASM** từ Trickest thông qua API
Public.

Công cụ mô phỏng phong cách điều khiển của **arsenal-cli (Orange
Cyberdefense)** với giao diện hiện đại (Rich), hỗ trợ truy vấn TQL, phân
trang, chuyển dataset, xem field, export, raw JSON...
Một tool sinh ra cho dân **AppSec / Pentest / Red Team / ASM
operators**.

------------------------------------------------------------------------

# 📌 Tính năng chính

### ✔ Giao diện đẹp, hỗ trợ `rich`

Hiển thị bảng, màu, panel giúp trải nghiệm CLI tốt hơn.

### ✔ Query TQL linh hoạt

Hỗ trợ đầy đủ cú pháp filter của Trickest:

    port != 80
    status_code >= 400
    url LIKE "%admin%"
    tls_expired = true

### ✔ Xem toàn bộ danh sách dataset

    :dataset

### ✔ Xem danh sách field (+ keyword filter)

    :fields
    :fields url
    :fields tls

### ✔ Phân trang / Limit / Offset

    :limit 200
    :offset 0
    :next
    :prev

### ✔ Xem raw JSON dễ phân tích

    :raw
    :json <query>

### ✔ Không phụ thuộc framework ngoài requests + rich

------------------------------------------------------------------------

# 📁 Cấu trúc dự án

    trickest-asm-cli/
    │
    ├── trickest_asm_cli.py     # Source code CLI
    ├── README.md                # Tài liệu này
    └── requirements.txt         # Thư viện cần thiết

------------------------------------------------------------------------

# 🚀 Cài đặt

### 1. Clone repository

``` bash
git clone https://github.com/<your-github>/trickest-asm-cli.git
cd trickest-asm-cli
```

### 2. Cài đặt dependencies

``` bash
pip install -r requirements.txt
```

hoặc:

``` bash
pip install requests rich
```

------------------------------------------------------------------------

# 🔑 Cấu hình API Token

Sửa trực tiếp trong file:

``` python
SOLUTION_ID = "your-solution-id"
TRICKEST_TOKEN = "your-api-token"
```

Hoặc dùng biến môi trường:

``` bash
export TRICKEST_TOKEN="your_token_here"
export TRICKEST_SOLUTION_ID="solution_id_here"
```

------------------------------------------------------------------------

# 🧠 Cách sử dụng

Chạy tool:

``` bash
python trickest_asm_cli.py
```

### Ví dụ truy vấn:

    trickest[Web Servers]> port != 80
    trickest[Web Servers]> status_code >= 500
    trickest[Web Servers]> tls_expired = true

------------------------------------------------------------------------

# 🧩 Hệ thống lệnh đầy đủ

  Lệnh                  Chức năng
  --------------------- ------------------------
  `*`                   Lấy toàn dataset
  `<query>`             Query TQL
  `:limit N`            Đặt số record/trang
  `:offset N`           Đặt offset
  `:next` / `:prev`     Điều hướng trang
  `:raw`                Bật/tắt raw JSON
  `:json <query>`       In raw JSON theo query
  `:dataset`            Chọn dataset khác
  `:fields`             Liệt kê toàn bộ field
  `:fields <keyword>`   Lọc field theo từ khóa
  `:help`               Trợ giúp
  `:quit`               Thoát CLI

------------------------------------------------------------------------

# 📸 Screenshot (giả lập)

    +------------------------------------------------------------+
    | Dataset: Web Servers                                       |
    +------------------------------------------------------------+
    | # | url                         | status_code | tls_expired |
    |----+----------------------------+-------------+-------------|
    | 1 | https://example.com         | 200         | false       |
    | 2 | http://old.example.com      | 301         | true        |
    +------------------------------------------------------------+

------------------------------------------------------------------------

# 🧩 Ví dụ truy vấn thực tế

### Tìm host dùng HTTP nhưng không redirect:

    scheme = "http" AND status_code != 301

### Tìm endpoint lỗi server:

    status_code >= 500

### Tìm TLS hết hạn:

    tls_expired = true

### Tìm URL nhạy cảm:

    url LIKE "%admin%"

------------------------------------------------------------------------

# ⚡ Performance Notes

-   Truy vấn trực tiếp API → dữ liệu luôn mới nhất.
-   Không cache local.
-   Không tải full dataset nếu không cần → tránh 429.

------------------------------------------------------------------------

# 🔐 Security Notes

-   Token API có quyền truy cập ASM → cần bảo mật.
-   Không commit token lên repo public.
-   Nên dùng `.env` hoặc biến môi trường.

------------------------------------------------------------------------

# 📝 Roadmap (đề xuất mở rộng)

-   [ ] Export CSV / JSON
-   [ ] Bookmark query
-   [ ] Auto-complete field name
-   [ ] Search nhiều dataset đồng thời
-   [ ] Plugin system
-   [ ] Lọc TLS nâng cao
-   [ ] Dashboard CLI mini

------------------------------------------------------------------------

# 🤝 Đóng góp

Pull Request luôn được chào đón.
Có thể đóng góp:

-   Thêm tính năng
-   Cải thiện tài liệu
-   Fix bug
-   Tối ưu hiệu năng

------------------------------------------------------------------------

# 📜 License

MIT License --- Free to use & modify.

------------------------------------------------------------------------

# ❤️ Credits

-   Trickest Public API
-   Gợi cảm hứng từ Arsenal CLI (Orange Cyberdefense)
-   Rich Console Framework
