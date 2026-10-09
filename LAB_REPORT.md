# BÁO CÁO THỰC HÀNH

## Deep Research Agent với Deep Agents và Sandbox

### 1. Mục tiêu

Bài thực hành xây dựng một hệ thống nghiên cứu sâu đa tác tử bằng Python. Hệ thống nhận một chủ đề, tự lập kế hoạch, chia công việc cho nhiều researcher subagent, thu thập tài liệu từ nhiều nguồn, tổng hợp báo cáo và kiểm tra tính nhất quán của trích dẫn.

Các mục tiêu chính đã hoàn thành:

- Xây dựng agent bằng `deepagents` và LangChain.
- Sử dụng Daytona làm sandbox cô lập để lưu ghi chú, tạo báo cáo và chạy validator.
- Xây dựng các công cụ tìm kiếm arXiv, Hugging Face và web.
- Cài đặt retry với exponential backoff, jitter và `Retry-After`.
- Điều phối nhiều researcher subagent và citation-checker.
- Sinh báo cáo có trích dẫn, `sources.json` và metadata phục vụ kiểm chứng.
- Chạy thành công toàn bộ năm chủ đề quy định trong `topics.md`.

### 2. Kiến trúc hệ thống

Quy trình xử lý chính:

1. `research.py` nhận chủ đề từ dòng lệnh và mở một Daytona sandbox.
2. Lead agent dùng `write_todos` để lập kế hoạch và chia chủ đề thành ít nhất ba câu hỏi con.
3. Các researcher subagent được gọi qua công cụ `task` để nghiên cứu song song.
4. Subagent sử dụng các công cụ chạy trên host để truy cập arXiv, Hugging Face và Exa; API key không được đưa vào sandbox.
5. Ghi chú được lưu trong `/tmp/work/research/notes` của sandbox.
6. Lead agent hợp nhất nguồn vào `sources.json` và viết phần thân báo cáo.
7. `finalize_citations.py` chuẩn hóa số trích dẫn và sinh phần References.
8. `check_citations.py` kiểm tra sự nhất quán giữa nội dung báo cáo, danh sách tham khảo và `sources.json`.
9. Báo cáo, nguồn và metadata được tải từ sandbox về thư mục `reports/`.

### 3. Các thành phần đã triển khai

#### 3.1. Công cụ nguồn dữ liệu

Tệp `tools.py` cung cấp năm công cụ:

- `arxiv_search`: tìm bài báo arXiv theo từ khóa, chuẩn hóa ID và URL, đồng thời bảo đảm khoảng cách tối thiểu ba giây giữa các request.
- `hf_daily_papers`: lấy các bài đang thịnh hành trên Hugging Face Daily Papers.
- `hf_search_papers`: tìm bài báo theo chủ đề trên Hugging Face.
- `web_search`: tìm nguồn web qua Exa MCP.
- `web_fetch`: đọc nội dung đầy đủ của một URL qua Exa MCP.

Mọi công cụ đều trả về chuỗi, trả `NO RESULTS` khi không có dữ liệu và trả `ERROR: ...` thay vì ném ngoại lệ làm gián đoạn agent. Khóa Exa được che khỏi thông báo lỗi.

#### 3.2. Retry và kiểm soát lỗi

Hàm `with_retry` hỗ trợ:

- Exponential backoff.
- Random jitter.
- Tôn trọng header `Retry-After`.
- Giới hạn thời gian chờ bằng `cap`.
- Không chờ thêm sau lần thử cuối.
- Chỉ retry lỗi mạng, HTTP 429 và các lỗi HTTP 5xx tạm thời.

#### 3.3. Hệ thống đa tác tử

Tệp `agents.py` định nghĩa ba vai trò:

- Lead agent: lập kế hoạch, giao việc, kiểm tra ghi chú, tổng hợp và hoàn thiện báo cáo.
- Researcher: tìm nguồn và ghi lại bằng chứng theo định dạng thống nhất.
- Citation-checker: kiểm tra mẫu các claim với nội dung nguồn.

Hệ thống đặt giới hạn số lần gọi model và tool cho cả lead lẫn subagent. `recursion_limit` cũng được đặt rõ ràng để tránh vòng lặp vô hạn và tiêu thụ token không kiểm soát.

#### 3.4. Sandbox và an toàn

Các thao tác file và validator chạy trong Daytona sandbox. Công cụ mạng và API key nằm ở host. Sandbox luôn được dừng và xóa khi kết thúc, kể cả khi quá trình nghiên cứu gặp lỗi.

`research.py` chỉ ghi output khi report và `sources.json` hợp lệ. Quality gate bổ sung từ chối kết quả nếu:

- Báo cáo hoặc nguồn bị thiếu/rỗng.
- `sources.json` không phải JSON hợp lệ.
- Báo cáo còn ít hơn ba họ nguồn.
- Một URL nguồn chứa khoảng trắng hoặc sai định dạng HTTP(S).

#### 3.5. Kiểm tra trích dẫn

`check_citations.py` kiểm tra:

- `sources.json` không rỗng.
- Số nguồn là số nguyên và không bị trùng.
- URL hợp lệ và không trùng lặp.
- Mọi citation trong thân báo cáo đều tồn tại trong nguồn.
- Mọi nguồn đều được trích dẫn.
- Mỗi nguồn có đúng một dòng References.
- Mỗi dòng References có đúng một URL và khớp với nguồn tương ứng.
- Citation nhóm như `[1, 2]` và khoảng như `[1-3]` được xử lý đúng.

### 4. Kết quả thực nghiệm

| Chủ đề | Model | Thời gian (giây) | Subagent | Số nguồn | Họ nguồn |
|---|---|---:|---:|---:|---|
| World model | `gpt-4o-mini` | 82.0 | 3 | 7 | arxiv, hf-search, web |
| Reinforcement learning for LLM reasoning | `ag/gemini-pro-agent` | 278.5 | 4 | 14 | arxiv, hf-search, web |
| LLM agents and tool use | `ag/gemini-pro-agent` | 331.3 | 5 | 15 | arxiv, hf-daily, hf-search, web |
| Video and multimodal generation | `ag/gemini-pro-agent` | 632.2 | 4 | 14 | arxiv, hf-daily, hf-search, web |
| Efficient inference and small language models | `ag/gemini-pro-agent` | 432.3 | 5 | 15 | arxiv, hf-search, web |

Tổng hợp:

- 5/5 chủ đề đã có đủ bộ ba file `.md`, `.sources.json` và `.meta.json`.
- Tổng cộng 21 lượt gọi researcher/citation subagent được ghi nhận.
- Tổng cộng 65 nguồn được giữ lại sau khi chuẩn hóa trích dẫn.
- Tổng thời gian chạy ghi nhận khoảng 1.756,3 giây, tương đương 29,3 phút.
- Metadata ghi nhận 1.059.751 input token và 35.121 output token của lead agents. Số liệu này không bao gồm phần lớn token của subagent nên thấp hơn mức sử dụng thực tế.

### 5. Kiểm thử và xác nhận

Các bước kiểm tra đã thực hiện:

```powershell
python -m py_compile tools.py agents.py research.py check_citations.py
python self_check.py
git diff --check
```

Kết quả cuối của `self_check.py`:

```text
survey about world model                                     OK
survey about reinforcement learning for LLM reasoning        OK
survey about LLM agents and tool use                          OK
survey about video and multimodal generation                  OK
survey about efficient inference and small language models   OK
git / secrets                                                OK

READY to submit (the manual parts of RUBRIC.md are still graded by a person).
```

Ngoài ra, các kiểm thử nhỏ bằng mock đã xác nhận:

- Retry đúng số lần và không sleep sau lần thất bại cuối.
- Parser arXiv loại bỏ version suffix và chuẩn hóa URL HTTPS.
- Validator xử lý citation đơn, nhóm, khoảng và Markdown link.
- Validator hỗ trợ URL hợp lệ chứa dấu ngoặc.
- `slugify` ngăn topic thoát khỏi thư mục `reports/`.

### 6. Khó khăn và cách xử lý

- OpenAI API hết credit giữa quá trình chạy: hệ thống được chuyển sang 9Router với endpoint OpenAI-compatible.
- Tên model ban đầu thiếu prefix provider: danh sách `/v1/models` được dùng để chọn ID hợp lệ.
- Một số model không hoàn thành được workflow nhiều tool call hoặc bị timeout: `ag/gemini-pro-agent` được chọn vì chạy ổn định hơn với agent workflow.
- Một báo cáo ban đầu mất họ nguồn sau finalizer và một nguồn chứa ngày trong trường URL: quality gate được bổ sung để phát hiện và từ chối các kết quả tương tự.
- Các nguồn đôi lúc bị rate limit: retry/backoff và chiến lược đổi nguồn giúp agent tiếp tục nghiên cứu.

### 7. Kết luận

Hệ thống đã hoàn thành đầy đủ quy trình deep research đa tác tử: lập kế hoạch, phân công subagent, thu thập dữ liệu đa nguồn, tổng hợp báo cáo trong sandbox, hoàn thiện trích dẫn bằng xử lý tất định và kiểm tra kết quả tự động. Cả năm chủ đề bắt buộc đều vượt qua `self_check.py` và sẵn sàng cho bước đánh giá thủ công hoặc nộp repository.

Hướng cải tiến tiếp theo có thể gồm theo dõi token dùng chung cho lead và subagent, checkpoint để tiếp tục các lần chạy bị timeout, và kiểm chứng ngữ nghĩa tự động cho toàn bộ claim thay vì chỉ kiểm tra mẫu.
