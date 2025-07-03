import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import hashlib
import xml.etree.ElementTree as ET

def open_browser(path_download):
    options = Options()
    options.add_argument("--start-maximized")
    prefs = {
        "download.default_directory": path_download,
        "download.directory_upgrade": True,
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": True,
        "profile.default_content_settings.popups": 0,
        "profile.default_content_setting_values.automatic_downloads": 1 
    }
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)
    return driver

def safe_click(driver, by, value):
    try:
        element = driver.find_element(by, value)
        try:
            element.click()
        except:
            driver.execute_script("arguments[0].click()", element)
        return True
    except Exception as e:
        return False

def process_fpt_invoice(driver, url, ma_so_thue, ma_tra_cuu):
    try:
        driver.get(url)
        driver.find_element(By.XPATH, '//input[@placeholder="MST bên bán"]').send_keys(ma_so_thue)
        time.sleep(1)
        driver.find_element(By.XPATH, '//input[@placeholder="Mã tra cứu hóa đơn"]').send_keys(ma_tra_cuu)

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
        time.sleep(2)
        try:
            nut_tai_xml = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"XML")]'))
            )
            nut_tai_xml.click()
            time.sleep(3)
        except Exception:
            try:
                driver.execute_script("""
                    document.querySelector('downloads-manager')
                        .shadowRoot.querySelector('#downloadsList downloads-item')
                        .shadowRoot.querySelector('#icon').click()
                """)
                time.sleep(3)
            except Exception:
                pass
    except Exception as e:
        pass

def process_me_invoice(driver, url, ma_so_thue, ma_tra_cuu):
    try:
        driver.get(url)
        input_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[placeholder="Nhập mã tra cứu hóa đơn"]'))
        )
        input_box.clear()
        input_box.send_keys(ma_tra_cuu)
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
        btn_xml = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.txt-download-xml"))
        )
        btn_xml.click()
        time.sleep(2)
    except TimeoutException:
        pass
    except Exception as e:
        pass

def process_van_e_invoice(driver, url, ma_so_thue, ma_tra_cuu):
    try:
        driver.get(url)
        driver.find_element(By.CSS_SELECTOR, "#txtInvoiceCode").send_keys(ma_tra_cuu)
        safe_click(driver, By.XPATH, '//*[@id="Button1"]')
        time.sleep(2)
        xpath_frame = '//*[@id="frameViewInvoice"]'
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, xpath_frame)))
        element_frame = driver.find_element(By.XPATH, xpath_frame)
        driver.switch_to.frame(element_frame)
        safe_click(driver, By.XPATH, '//*[@id="btnDownload"]')
        safe_click(driver, By.CSS_SELECTOR, "#LinkDownPDF")
        safe_click(driver, By.CSS_SELECTOR, "#LinkDownXML")
        time.sleep(2)
    except Exception as e:
        pass

def process_invoice(df):
    path_folder = "downloads"
    os.makedirs(path_folder, exist_ok=True)
    path_download = os.path.abspath(path_folder)
    driver = open_browser(path_download)

    for index, row in df.iterrows():
        ma_so_thue = str(row['Mã số thuế'])
        ma_tra_cuu = str(row['Mã tra cứu'])
        url = str(row['URL']) if 'URL' in row else None
        print(f"Đang xử lý: {ma_so_thue} - {ma_tra_cuu}")

        try:
            if url and "fpt" in url:
                process_fpt_invoice(driver, url, ma_so_thue, ma_tra_cuu)
            elif url and "meinvoice" in url:
                process_me_invoice(driver, url, ma_so_thue, ma_tra_cuu)
            elif url and "van.ehoadon" in url:
                process_van_e_invoice(driver, url, ma_so_thue, ma_tra_cuu)
            else:
                print(f"Không hỗ trợ URL: {url}")
        except Exception as e:
            print(f"Lỗi {ma_so_thue}: {e}")

        time.sleep(2)

    driver.quit()

def doc_input(file_path="input.xlsx"):
    df = pd.read_excel(file_path, dtype={"Mã số thuế": str, "Mã tra cứu": str})
    return df

def parse_invoice_xml(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Nếu có namespace thì lấy tự động
        ns = {}
        if '}' in root.tag:
            uri = root.tag[root.tag.find("{")+1:root.tag.find("}")]
            ns = {'ns': uri}
            def f(tag): return f'.//ns:{tag}'
        else:
            def f(tag): return f'.//{tag}'

        # Trích dữ liệu
        so_hoa_don = root.find(f('TTChung/SHDon'), ns)
        ten_ban_hang = root.find(f('NDHDon/NBan/Ten'), ns)
        dia_chi_ban = root.find(f('NDHDon/NBan/DChi'), ns)
        dien_thoai = root.find(f('NDHDon/NBan/SDThoai'), ns)
        so_tai_khoan_ban = root.find(f('NDHDon/NBan/STKNHang'), ns)

        ten_mua = root.find(f('NDHDon/NMua/Ten'), ns)
        dia_chi_mua = root.find(f('NDHDon/NMua/DChi'), ns)
        stk_mua = root.find(f('NDHDon/NMua/STKNHang'), ns)

        return {
            'Số hóa đơn': so_hoa_don.text if so_hoa_don is not None else '',
            'Đơn vị bán hàng': ten_ban_hang.text if ten_ban_hang is not None else '',
            'Địa chỉ': dia_chi_ban.text if dia_chi_ban is not None else '',
            'Điện thoại': dien_thoai.text if dien_thoai is not None else '',
            'Số tài khoản': so_tai_khoan_ban.text if so_tai_khoan_ban is not None else '',
            'Họ tên người mua hàng': ten_mua.text if ten_mua is not None else '',
            'Địa chỉ.1': dia_chi_mua.text if dia_chi_mua is not None else '',
            'Số tài khoản.1': stk_mua.text if stk_mua is not None else '',
            'status': 'đã tải thành công'
        }

    except Exception as e:
        return {
            'Số hóa đơn': '',
            'Đơn vị bán hàng': '',
            'Địa chỉ': '',
            'Điện thoại': '',
            'Số tài khoản': '',
            'Họ tên người mua hàng': '',
            'Địa chỉ.1': '',
            'Số tài khoản.1': '',
            'status': f'Lỗi: {str(e)}'
        }

def process_all_xml(folder='downloads'):
    data = []
    for file in os.listdir(folder):
        if file.endswith('.xml'):
            full_path = os.path.join(folder, file)
            row = parse_invoice_xml(full_path)
            data.append(row)
    return pd.DataFrame(data)

def save_to_excel(df, file_out='output.xlsx'):
    df.to_excel(file_out, index=False)

if __name__ == "__main__":
    df = doc_input()
    process_invoice(df)
    df = process_all_xml("downloads")
    save_to_excel(df, file_out='output.xlsx')