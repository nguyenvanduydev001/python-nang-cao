from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time


# 1. Mở trình duyệt
def mo_trinh_duyet():
    options = Options()
    options.add_argument("--start-maximized")
    # Thêm cấu hình thư mục tải về nếu cần
    prefs = {"download.prompt_for_download": False}
    options.add_experimental_option("prefs", prefs)
    return webdriver.Chrome(options=options)


# 2. Đọc mã tra cứu từ file txt
def doc_ma_tra_cuu(file_path="ma_tra_cuu.txt"):
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


# 3. Nhập mã và nhấn tìm kiếm
def thuc_hien_tra_cuu(driver, ma):
    driver.get("https://www.meinvoice.vn/tra-cuu")

    try:
        input_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Nhập mã tra cứu hóa đơn"]'))
        )
        input_box.clear()
        input_box.send_keys(ma)

        nut_tim = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "btnSearchInvoice"))
        )
        nut_tim.click()
        return True
    except:
        return False


# 4. Xử lý kết quả và tải hóa đơn nếu có
def xu_ly_ket_qua(driver, ma):
    try:
        # Chờ có kết quả (có nút "Tải hóa đơn")
        nut_tai_hoa_don = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "span.download-invoice"))
        )
        nut_tai_hoa_don.click()  # ⚠️ Bước quan trọng: nhấn để hiện ra nút tải PDF/XML

        # Chờ và click nút tải PDF
        btn_pdf = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.txt-download-pdf"))
        )
        btn_pdf.click()

        ghi_log(ma, "✅ Tải thành công")
    except TimeoutException:
        ghi_log(ma, "❌ Không tìm thấy hóa đơn hoặc không hiện popup")
    except Exception as e:
        ghi_log(ma, f"⚠️ Lỗi khác: {str(e)}")


# 5. Ghi log kết quả
def ghi_log(ma, trang_thai):
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"{ma}: {trang_thai}\n")


# CHÍNH – quy trình chuẩn
def chinh():
    danh_sach_ma = doc_ma_tra_cuu()
    driver = mo_trinh_duyet()

    for ma in danh_sach_ma:
        print(f"🚀 Đang xử lý: {ma}")
        if thuc_hien_tra_cuu(driver, ma):
            xu_ly_ket_qua(driver, ma)
        else:
            ghi_log(ma, "❌ Không thể nhập mã hoặc nhấn tìm kiếm")

        time.sleep(2)

    driver.quit()
    print("🎉 Xong hết rồi học trò!")


if __name__ == "__main__":
    chinh()
