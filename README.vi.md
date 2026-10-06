# Vietnamese Passphrase

Bộ wordlist tiếng Việt có nguồn gốc từng mục, quy trình xây dựng chạy lại được và bộ sinh passphrase tham chiếu. Dự án ưu tiên dữ liệu để các ứng dụng khác dùng lại qua file UTF-8 hoặc thư viện TypeScript không có phụ thuộc lúc chạy.

[English](README.md) · [Nghiên cứu và so sánh](docs/research.md) · [Mô hình bảo mật](docs/security.md)

Phiên bản 0.1.0 là **bản nghiên cứu thử nghiệm**. Kiểm tra cấu trúc và các phép thử chương trình đã được xây dựng. Dự án chưa có thẩm định ngôn ngữ độc lập, nghiên cứu khả năng ghi nhớ với người dùng Việt hay kiểm toán bảo mật độc lập. Không dùng các danh sách này làm định dạng khôi phục ví BIP-39.

| Danh sách                           | Số mục | Bit mỗi lượt lấy mẫu đều | Số lượt để đạt ít nhất 80 bit | Độ dài trung bình có dấu nối |
| ----------------------------------- | -----: | -----------------------: | ----------------------------: | ---------------------------: |
| [vi](data/lists/vi.txt)             |  3.057 |                  11,5779 |                             7 |              48,29 codepoint |
| [vi-ascii](data/lists/vi-ascii.txt) |  2.464 |                  11,2668 |                             8 |              60,44 codepoint |
| [vi-short](data/lists/vi-short.txt) |  1.293 |                  10,3365 |                             8 |              34,75 codepoint |

Kích thước xuất phát từ các tiêu chí nguồn dữ liệu và lọc từ. `vi` giữ dấu tiếng Việt và chứa từ một hoặc hai tiếng. `vi-ascii` gộp những từ trùng nhau khi bỏ dấu trước khi lấy mẫu. `vi-short` là lựa chọn từ một tiếng để so sánh độ dài. Danh sách ngắn hơn chưa được chứng minh là dễ nhớ hơn. Mục tiêu 80 bit ở bảng là một ví dụ để so sánh, cần chọn mục tiêu phù hợp với hệ thống thực tế.

Từ ghép `bánh mì` được biểu diễn bằng `bánh_mì`. Giữa các mục dùng dấu khác, chẳng hạn `-`. Phải giữ ranh giới này. Không bỏ dấu sau khi sinh, không tự chọn từ yêu thích, không đổi thứ tự và không cắt câu mật khẩu cho vừa ô nhập.

## Dùng thử

Dùng Node 24.21.0 và npm 12.2.0. Gói chưa được phát hành lên npm.

```sh
git clone https://github.com/VINASIG/vietnamese-passphrase.git
cd vietnamese-passphrase
npm ci --ignore-scripts
npm run build
node dist/cli.js verify
node dist/cli.js generate --profile vi --bits 80
node dist/cli.js generate --profile vi-ascii --words 8 --json
```

Lệnh `generate` in bí mật vừa sinh ra màn hình terminal. Chương trình dùng nguồn ngẫu nhiên bảo mật của hệ thống, không tải dữ liệu lên mạng hay tự lưu bí mật. Môi trường terminal và ứng dụng tích hợp vẫn cần xử lý bí mật đúng cách. Không dùng câu trong tài liệu hoặc test làm mật khẩu thật.

## Tích hợp và kiểm chứng

File danh sách nằm ở [data/lists](data/lists/). Thư viện có thể chạy trong Node hoặc trình duyệt bằng Web Crypto. Có API kiểm tra SHA-256 trước khi đọc file, lấy mẫu đều bằng rejection sampling, kiểm tra giới hạn độ dài trước khi sinh và ánh xạ xúc xắc cho kích thước danh sách bất kỳ. Không ép kích thước về 2.048 hay 7.776.

Mỗi lượt phải độc lập và lấy mẫu đều. Với `N` mục và `k` lượt, entropy của mô hình là `k × log2(N)`. Công thức không áp dụng cho một câu người dùng tự nghĩ ra. Dấu nối cố định không làm tăng entropy. Cần phân biệt codepoint với số byte UTF-8 khi hệ thống giới hạn độ dài.

```sh
python scripts/build_data.py --out output/rebuilt
python tests/data_test.py
python scripts/research.py
npm run verify
```

Dữ liệu chứng cứ rút gọn được đưa vào repository để dựng lại danh sách ngoại tuyến. Nguồn đầy đủ, SHA-256, giấy phép, tiêu chí lọc, lý do loại từ, số câu dẫn chứng và các phép so sánh nằm trong [báo cáo nghiên cứu](docs/research.md), [provenance](data/provenance.jsonl) và [sổ quyết định](data/audit/decisions.jsonl). Hai bản Wiktionary có nội dung giao nhau. Tatoeba có thiên lệch câu dịch. Những giới hạn này được ghi rõ.

Mã nguồn dùng LGPL-3.0-or-later để thuận tiện tích hợp. Bộ dữ liệu và tài liệu dùng CC-BY-SA-4.0, giữ thông báo và ghi công các nguồn gốc. Xem [phạm vi giấy phép](LICENSES.md) trước khi phân phối lại hoặc sửa danh sách.
