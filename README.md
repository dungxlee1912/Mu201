# Theo dõi MU201 tự động (miễn phí)

1. Đăng ký key miễn phí tại https://aviationstack.com (100 request/tháng).
2. Tạo repo GitHub mới (public), tải toàn bộ các file này lên (nhớ cả thư mục .github).
3. Repo > Settings > Secrets and variables > Actions > New repository secret
   Tên: AVIATIONSTACK_KEY, giá trị: key của bạn.
4. Repo > Settings > Pages > Source: Deploy from a branch > main > / (root).
5. Repo > Actions > "Cập nhật MU201" > Run workflow để chạy thử lần đầu.
6. Mở https://<tên-github>.github.io/<tên-repo>/ để xem.

Chạy 2 lần/ngày, khoảng 60 request/tháng, nằm trong hạn mức miễn phí.
