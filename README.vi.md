# Vietnamese Passphrase

Bộ từ vựng passphrase tiếng Việt thử nghiệm có quyết định của SI agents, phép đo độc lập và bộ sinh tham chiếu lấy mẫu đều. Dùng lại danh sách UTF-8 cùng hồ sơ chứng cứ hoặc thư viện TypeScript không có phụ thuộc lúc chạy.

[English](README.md) · [Nghiên cứu](docs/research.md) · [Mô hình bảo mật](docs/security.md)

## Bản nghiên cứu hiện hành

**[v0.2.4](https://github.com/VINASIG/vietnamese-passphrase/releases/tag/v0.2.4)** là bản nghiên cứu thử nghiệm hiện hành do agent đánh giá. [Metadata phát hành](release.json) ghi tag, file notes và kênh thử nghiệm cụ thể. Chưa có bản ổn định và chưa có profile mặc định tốt nhất cho mọi người. Endpoint latest của GitHub không chọn prerelease, nên dùng liên kết phiên bản cụ thể ở trên.

Theo quy tắc của chủ dự án, SI agents thực hiện công việc và đánh giá. Một agent đã sàng lọc ở mức đầu mục. Chưa có dữ liệu người Việt về khả năng ghi nhớ, mức quen thuộc hay lỗi nhập, chưa có thẩm định ngôn ngữ hoặc kiểm toán bảo mật độc lập. Không dùng các danh sách này làm định dạng khôi phục ví BIP-39. Dự án chưa tuyên bố chuẩn passphrase tiếng Việt hoặc vocabulary tốt nhất.

Đọc [kết quả phản biện](docs/adversarial-review.md), [phạm vi bảo đảm](docs/assurance.md), [cách giới thiệu phiên bản và profile](docs/publication-semantics.md) và [hướng dẫn phân phối lại](docs/downstream.md). [Lộ trình nghiên cứu](docs/research-roadmap.md) phân biệt phần có thể kiểm tra thêm bằng tự động với phần cần quan sát người Việt thật. Báo cáo lỗ hổng qua kênh riêng được ghi trong [SECURITY.md](SECURITY.md).

## Các profile thử nghiệm hiện hành

Tên sử dụng thể hiện mức bằng chứng và mục đích. Tên file cũ được giữ nguyên trong [revision dữ liệu thử nghiệm](research/experimental/2026-10-06.agent-1/) và vẫn là alias CLI đã được đánh dấu cũ. Việc đổi tên không đổi byte dữ liệu hay entropy. Chưa profile nào có đo lường khả năng ghi nhớ hoặc lỗi nhập của người dùng.

| Profile                        | Số mục | Thử nghiệm và giới hạn                                                                      |
| ------------------------------ | -----: | ------------------------------------------------------------------------------------------- |
| `experimental-agent-vi`        |  2.966 | Ứng viên có dấu, sàng lọc ngữ cảnh bởi agent. Chưa xét hết các nghĩa và tổ hợp từ           |
| `experimental-agent-vi-fused`  |  2.966 | Viết liền token trước khi lấy mẫu. Ngắn hơn nhưng không hiện ranh giới tiếng                |
| `experimental-agent-ascii`     |  2.389 | Lấy mẫu đều trên các chuỗi bỏ dấu duy nhất. Phân biệt ngữ nghĩa vẫn bị mất                  |
| `experimental-agent-distance1` |  2.045 | Tập con theo ràng buộc khoảng cách một codepoint. Câu dài hơn và còn các dạng gần nhau khác |

`control-paired-native` gồm 2.389 mục đối chứng có dấu, dùng chung chỉ mục với ASCII. Đây là bộ đối chứng, CLI không cho sinh passphrase. Các baseline lịch sử có tên bắt đầu bằng `historical-`. `diagnostic-short-v1` là bộ ngắn đã rút khỏi cách dùng thông thường vì khoảng 96% token có hàng xóm cách một ký tự. CLI và ví dụ Python từ chối sinh từ bộ này, kể cả alias `vi-short`. Đó là đặc tính cấu trúc, không phải tỷ lệ người dùng gõ sai. File vẫn được giữ để tái lập và chẩn đoán trong [hồ sơ baseline lịch sử](docs/historical-baselines.md).

[Catalog](research/profile-catalog.json) ghi bằng chứng, mục đích và chính sách sinh của đủ tám profile. Thư viện tổng quát vẫn nhận danh sách do ứng dụng truyền vào và không tự thực thi chính sách catalog. Ứng dụng tích hợp cần tự chọn và thực thi yêu cầu phù hợp.

Ranh giới tiếng trong token được mã hóa bằng `_`, trừ thử nghiệm viết liền cụ thể. Giữa các token dùng dấu phân cách được hỗ trợ. Không bỏ dấu sau khi sinh, không tự chọn từ yêu thích, đổi thứ tự hay cắt câu cho vừa ô nhập. Kích thước danh sách là kết quả tiêu chí nguồn và lọc từ, chưa được chứng minh tối ưu.

## Dùng thử

Dùng Node 24.21.0 và npm 12.2.0. Gói chưa được phát hành lên npm.

```sh
git clone https://github.com/VINASIG/vietnamese-passphrase.git
cd vietnamese-passphrase
npm ci --ignore-scripts
npm run build
node dist/cli.js verify
node dist/cli.js profiles
node dist/cli.js info --profile experimental-agent-vi
node dist/cli.js generate --profile experimental-agent-vi --bits 80
node dist/cli.js generate --profile experimental-agent-ascii --words 8 --json
```

Mục tiêu 80 bit chỉ là ví dụ, cần chọn theo hệ thống cụ thể. Lệnh generate in bí mật ra terminal và ghi giới hạn bằng chứng vào standard error. Chương trình dùng nguồn ngẫu nhiên bảo mật của hệ thống, không tải lên mạng hay tự lưu bí mật. Môi trường terminal và ứng dụng tích hợp vẫn cần xử lý bí mật đúng cách. Không dùng câu trong tài liệu hoặc test làm mật khẩu thật.

## Tích hợp và kiểm chứng

Các danh sách hiện hành nằm trong [revision thử nghiệm](research/experimental/2026-10-06.agent-1/). File trong data/lists là baseline lịch sử. Thư viện dùng Web Crypto trong Node hoặc trình duyệt, kiểm tra SHA-256 trước khi đọc file, lấy mẫu đều bằng rejection sampling và kiểm tra giới hạn độ dài trước khi sinh. API xúc xắc hỗ trợ kích thước danh sách bất kỳ. Bảng xúc xắc đã lưu là dữ liệu tái lập v0.1, không phải hướng dẫn dùng profile hiện hành.

Với `N` mục và `k` lượt độc lập lấy mẫu đều, entropy mô hình là `k × log2(N)`. Công thức không đo khả năng ghi nhớ hoặc áp dụng cho câu tự nghĩ ra. Dấu nối cố định không tăng entropy. Cần phân biệt codepoint với số byte UTF-8 khi giới hạn độ dài.

```sh
python scripts/build_data.py --out output/rebuilt
python tests/data_test.py
python tests/vocabulary_test.py
python tests/publication_test.py
python scripts/vocabulary_audit.py
python scripts/experiment_profiles.py
python scripts/compare_methodology.py
python scripts/release_metadata.py
npm run verify
```

Nguồn, giấy phép, hash, quyết định lọc từ và các phép so sánh nằm trong [báo cáo nghiên cứu](docs/research.md), [provenance](data/provenance.jsonl), [quyết định của agent](research/content-policy.json) và [hồ sơ baseline](docs/historical-baselines.md). Corpus là nguồn chứng cứ văn bản, không phải dữ liệu người dùng. Quy trình phát hành kiểm tra đúng tag, notes, artifact và nguồn dựng trong [hướng dẫn xác minh](docs/release-security.md). [Hồ sơ v0.2.3](docs/publication-v0.2.json) và các file đã phát hành giữ nguyên.

Mã nguồn dùng LGPL-3.0-or-later. Dữ liệu và tài liệu dùng CC-BY-SA-4.0 cùng thông báo và ghi công nguồn. Xem [phạm vi giấy phép](LICENSES.md) trước khi phân phối lại hoặc sửa danh sách. Chữ ký bản phát hành chỉ chứng minh nguồn dựng trong phạm vi xác minh, không chứng nhận chất lượng từ vựng.
