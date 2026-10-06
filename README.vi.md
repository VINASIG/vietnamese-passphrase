# Vietnamese Passphrase

Bộ wordlist tiếng Việt có nguồn gốc từng mục, quy trình xây dựng chạy lại được và bộ sinh passphrase tham chiếu. Dự án ưu tiên dữ liệu để các ứng dụng khác dùng lại qua file UTF-8 hoặc thư viện TypeScript không có phụ thuộc lúc chạy.

[English](README.md) · [Nghiên cứu và so sánh](docs/research.md) · [Mô hình bảo mật](docs/security.md)

Phiên bản 0.2.2 là **bản nghiên cứu thử nghiệm do SI agents đánh giá**. Theo quy tắc của chủ dự án, công việc và đánh giá do agents thực hiện. Quyết định của agent không thay thế bằng chứng từ người dùng. Kiểm tra cấu trúc và các phép thử chương trình đã được xây dựng. Dự án chưa có thẩm định ngôn ngữ độc lập, nghiên cứu khả năng ghi nhớ với người dùng Việt hay kiểm toán bảo mật độc lập. Không dùng các danh sách này làm định dạng khôi phục ví BIP-39.

[Bản phát hành v0.1.0](https://github.com/VINASIG/vietnamese-passphrase/releases/tag/v0.1.0) có gói tích hợp, các bản chụp nguồn dữ liệu gốc và checksum SHA-256. [Hồ sơ phát hành](docs/publication-plan.json) ghi revision mã nguồn, kết quả kiểm tra file tải lại và thông tin công khai trên các trang liên quan.

| Danh sách                           | Số mục | Bit mỗi lượt lấy mẫu đều | Số lượt để đạt ít nhất 80 bit | Độ dài trung bình có dấu nối |
| ----------------------------------- | -----: | -----------------------: | ----------------------------: | ---------------------------: |
| [vi](data/lists/vi.txt)             |  3.057 |                     11,6 |                             7 |               48,3 codepoint |
| [vi-ascii](data/lists/vi-ascii.txt) |  2.464 |                     11,3 |                             8 |               60,4 codepoint |
| [vi-short](data/lists/vi-short.txt) |  1.293 |                     10,3 |                             8 |               34,7 codepoint |

Kích thước xuất phát từ các tiêu chí nguồn dữ liệu và lọc từ. `vi` giữ dấu tiếng Việt và chứa từ một hoặc hai tiếng. `vi-ascii` gộp những từ trùng nhau khi bỏ dấu trước khi lấy mẫu. `vi-short` là lựa chọn từ một tiếng để so sánh độ dài. Danh sách ngắn hơn chưa được chứng minh là dễ nhớ hơn. Mục tiêu 80 bit ở bảng là một ví dụ để so sánh, cần chọn mục tiêu phù hợp với hệ thống thực tế.

Từ ghép `bánh mì` được biểu diễn bằng `bánh_mì`. Giữa các mục dùng dấu khác, chẳng hạn `-`. Phải giữ ranh giới này. Không bỏ dấu sau khi sinh, không tự chọn từ yêu thích, không đổi thứ tự và không cắt câu mật khẩu cho vừa ô nhập.

## Các profile thử nghiệm riêng

Ba danh sách v0.1 ở trên được giữ nguyên từng byte làm mốc đối chiếu. Kích thước 3.057 là kết quả heuristic, chưa được chứng minh tối ưu. [Báo cáo phản biện và phương pháp mới](docs/adversarial-review.md) tách đo cấu trúc, chứng cứ corpus, quyết định của agent và những điều chưa biết về người dùng.

| Profile            | Số mục | Mục đích và đánh đổi                                                                                                              |
| ------------------ | -----: | --------------------------------------------------------------------------------------------------------------------------------- |
| `vi-display`       |  2.966 | Sàng lọc ngữ cảnh ở mức đầu mục; loại 84 mục có lý do và gộp bảy cặp biến thể. Không bảo đảm mọi nghĩa hoặc tổ hợp từ đều phù hợp |
| `vi-fused`         |  2.966 | Viết liền từ ghép trước khi lấy mẫu, tiết kiệm ký tự nhưng không hiện ranh giới tiếng                                             |
| `vi-ascii-display` |  2.389 | Lấy mẫu đều các chuỗi bỏ dấu duy nhất; mất phân biệt nghĩa vẫn tồn tại                                                            |
| `vi-ascii-native`  |  2.389 | Cặp đối chứng Unicode dùng cùng chỉ mục với profile ASCII                                                                         |
| `vi-distinct`      |  2.045 | Tập con không có cặp cách một codepoint NFC; câu dài hơn và còn các dạng gần nhau khác                                            |

[Phiên bản thử nghiệm riêng](research/experimental/2026-10-06.agent-1/) có manifest, checksum, sổ quyết định và toàn bộ cặp tương tự. Không profile nào được chọn làm mặc định chung. Khoảng 43,4% token bản gốc có hàng xóm cách một ký tự; ở bản ngắn là 96,0%. Đây không phải tỷ lệ người dùng gõ sai. Corpus tin tức VTB đối chiếu được 60,4% token bản gốc; đó không phải điểm quen thuộc.

CLI v0.2 bắt buộc chọn `--profile`. Lệnh kiểm tra chỉ báo `INTEGRITY_PASS` cho byte và định dạng. [Phạm vi bảo đảm](docs/assurance.md), [hướng dẫn phân phối lại](docs/downstream.md) và [xác minh nguồn bản phát hành](docs/release-security.md) nêu rõ từng lớp chứng cứ. Dự án chưa tuyên bố chuẩn passphrase tiếng Việt, khả năng ghi nhớ vượt trội hoặc thẩm định độc lập đã hoàn tất.

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
