import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

def open_browser(path_download):
    options = Options()
    options.add_argument("--start-maximized")
    prefs = {
        "download.default_directory": path_download,
        "download.directory_upgrade": True,
        "download.prompt_for_download": False,
        "disable-popup-blocking": True,
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": True  # Để Chrome tự động tải PDF
    }
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)
    return driver

def process_fpt_invoice(driver, url, ma_so_thue, ma_tra_cuu):
    driver.get(url)
    xpath_ma_so_thue = '//input[@placeholder="MST bên bán"]'
    driver.find_element(By.XPATH, xpath_ma_so_thue).send_keys(ma_so_thue)
    time.sleep(1)
    xpath_ma_tra_cuu = '//input[@placeholder="Mã tra cứu hóa đơn"]'
    driver.find_element(By.XPATH, xpath_ma_tra_cuu).send_keys(ma_tra_cuu)
    btn_tim_kiem = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Tra cứu")]'))
    )
    btn_tim_kiem.click()
    xpath_iframe = '//iframe[starts-with(@src, "blob:https://tracuuhoadon.fpt.com.vn/")]'
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, xpath_iframe))
    )
    iframe = driver.find_element(By.XPATH, xpath_iframe)
    blob_url = iframe.get_attribute("src")
    driver.execute_script("window.open(arguments[0]);", blob_url)
    time.sleep(3)
    print(f"Đã tải PDF cho {ma_so_thue} - {ma_tra_cuu}")

def process_me_invoice(driver, url, ma_so_thue, ma_tra_cuu):
    try:
        driver.get(url)
        
        input_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[placeholder="Nhập mã tra cứu hóa đơn"]'))
        )
        input_box.clear()
        input_box.send_keys(ma_tra_cuu)

        # Nhấn nút tìm kiếm
        nut_tim = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "btnSearchInvoice"))
        )
        nut_tim.click()
        nut_tai_hoa_don = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "span.download-invoice"))
        )
        nut_tai_hoa_don.click()
        btn_pdf = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.txt-download-pdf"))
        )
        btn_pdf.click()
        driver.save_screenshot(f"{ma_so_thue}_{ma_tra_cuu}.png")
        ghi_log(ma_so_thue, ma_tra_cuu, url, "SUCCESS")
    except TimeoutException:
        ghi_log(ma_so_thue, ma_tra_cuu, url, "NOT_FOUND", "Không tìm thấy hóa đơn hoặc không hiện popup")
    except Exception as e:
        ghi_log(ma_so_thue, ma_tra_cuu, url, "FAIL", f"Lỗi khác: {str(e)}")

def process_van_e_invoice(driver, url, ma_so_thue, ma_tra_cuu):
    driver.get(url)

    # Nhập mã tra cứu
    css_input = "#txtInvoiceCode"
    driver.find_element(By.CSS_SELECTOR, css_input).send_keys(ma_tra_cuu)

    # Nhấn nút tra cứu
    xpath_btn = '//*[@id="Button1"]'
    element_btn = driver.find_element(By.XPATH, xpath_btn)
    try:
        element_btn.click()
    except:
        driver.execute_script("arguments[0].click()", element_btn)

    time.sleep(2)

    # Chuyển sang frame chứa hóa đơn
    xpath_frame = '//*[@id="frameViewInvoice"]'
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, xpath_frame)))
    element_frame = driver.find_element(By.XPATH, xpath_frame)
    driver.switch_to.frame(element_frame)

    # Download PDF
    print()
    element_download = driver.find_element(By.XPATH, '//*[@id="btnDownload"]')
    try:
        driver.execute_script("arguments[0].click()", element_download)
    except:
        element_download.click()
    
    css_download_pdf = "#LinkDownPDF"
    element_download_pdf = driver.find_element(By.CSS_SELECTOR, css_download_pdf)
    try:
        driver.execute_script("arguments[0].click()", element_download_pdf)
    except:
        element_download_pdf.click()

def process_invoice(df):
    path_folder = "download"
    os.makedirs(path_folder, exist_ok=True)
    path_download = os.path.abspath(path_folder)
    driver = open_browser(path_download)

    for index, row in df.iterrows():
        ma_so_thue = str(row['Mã số thuế'])
        ma_tra_cuu = str(row['Mã tra cứu'])
        url = str(row['URL']) if 'URL' in row else None
        print(f" Đang xử lý: {ma_so_thue} - {ma_tra_cuu}")

        try:
            if "fpt" in url:
                process_fpt_invoice(driver, url, ma_so_thue, ma_tra_cuu)
                ghi_log(ma_so_thue, ma_tra_cuu, url, "SUCCESS")
            elif "meinvoice" in url:
                process_me_invoice(driver, url, ma_so_thue, ma_tra_cuu)
                # ghi_log đã được gọi trong process_me_invoice
            elif "van.ehoadon" in url:
                process_van_e_invoice(driver, url, ma_so_thue, ma_tra_cuu)
                # ghi_log đã được gọi trong process_van_e_invoice
            else:
                print(f"Không hỗ trợ URL: {url}")
                ghi_log(ma_so_thue, ma_tra_cuu, url, "NOT_SUPPORT", "URL không hỗ trợ")
        except Exception as e:
            print(f"Lỗi {ma_so_thue}: {e}")
            ghi_log(ma_so_thue, ma_tra_cuu, url, "FAIL", str(e))

        time.sleep(2)

    driver.quit()

def doc_input(file_path="input.xlsx"):
    df = pd.read_excel(file_path, dtype={"Mã số thuế": str, "Mã tra cứu": str})
    return df

def ghi_log(ma_so_thue, ma_tra_cuu, url, trang_thai, loi=""):
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(f"{ma_so_thue},{ma_tra_cuu},{url},{trang_thai},{loi}\n")

if _name_ == "_main_":
    df = doc_input()
    process_invoice(df)