import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
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

def retry_action(action_func, max_retries=2, *args, **kwargs):
    last_exception = None
    for attempt in range(max_retries):
        try:
            result = action_func(*args, **kwargs)
            return result
        except Exception as e:
            last_exception = e
            time.sleep(3)  # Wait before retry
    if last_exception is not None:
        raise Exception("All retries failed") from last_exception
    else:
        raise Exception("All retries failed with unknown error")

def process_fpt_invoice(driver, url, ma_so_thue, ma_tra_cuu):
    try:
        driver.get(url)
        time.sleep(2)
        # Điền mã số thuế
        mst_input = driver.find_element(By.XPATH, '//input[@placeholder="MST bên bán"]')
        mst_input.clear()
        mst_input.send_keys(ma_so_thue)
        time.sleep(1)
        # Điền mã tra cứu
        mtc_input = driver.find_element(By.XPATH, '//input[@placeholder="Mã tra cứu hóa đơn"]')
        mtc_input.clear()
        mtc_input.send_keys(ma_tra_cuu)
        # Bấm nút tra cứu
        btn_tim_kiem = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Tra cứu")]'))
        )
        btn_tim_kiem.click()
        # Chờ iframe kết quả xuất hiện
        xpath_iframe = '//iframe[starts-with(@src, "blob:https://tracuuhoadon.fpt.com.vn/")]'
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, xpath_iframe))
        )
        iframe = driver.find_element(By.XPATH, xpath_iframe)
        blob_url = iframe.get_attribute("src")
        driver.execute_script("window.open(arguments[0]);", blob_url)
        time.sleep(3)
        driver.switch_to.window(driver.window_handles[-1])
        nut_tai_xml = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"XML")]'))
        )
        nut_tai_xml.click()
        time.sleep(5)
        main_window = driver.window_handles[0]
        driver.close()  # Đóng tab blob
        driver.switch_to.window(main_window)
        return True, "success"
    except Exception as e:
        return False, f"fail: {type(e).__name__}: {str(e)}"

def process_me_invoice(driver, url, ma_so_thue, ma_tra_cuu):
    try:
        driver.get(url)
        time.sleep(2)
        input_box = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Nhập mã tra cứu hóa đơn"]'))
        )
        input_box.clear()
        input_box.send_keys(ma_tra_cuu)
        nut_tim = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "btnSearchInvoice"))
        )
        nut_tim.click()
        nut_tai_hoa_don = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "span.download-invoice"))
        )
        nut_tai_hoa_don.click()
        btn_xml = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.txt-download-xml"))
        )
        btn_xml.click()
        time.sleep(5)
        return True, "success"
    except Exception as e:
        return False, f"fail: {type(e).__name__}: {str(e)}"

def process_van_e_invoice(driver, url, ma_so_thue, ma_tra_cuu):
    try:
        driver.get(url)
        time.sleep(2)
        driver.find_element(By.CSS_SELECTOR, "#txtInvoiceCode").send_keys(ma_tra_cuu)
        driver.find_element(By.XPATH, '//*[@id="Button1"]').click()
        time.sleep(3)
        xpath_frame = '//*[@id="frameViewInvoice"]'
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, xpath_frame)))
        element_frame = driver.find_element(By.XPATH, xpath_frame)
        driver.switch_to.frame(element_frame)
        driver.find_element(By.XPATH, '//*[@id="btnDownload"]').click()
        driver.find_element(By.CSS_SELECTOR, "#LinkDownXML").click()
        time.sleep(5)
        driver.switch_to.default_content()
        return True, "success"
    except Exception as e:
        return False, f"fail: {type(e).__name__}: {str(e)}"

def process_invoice(df):
    path_folder = "downloads"
    os.makedirs(path_folder, exist_ok=True)
    path_download = os.path.abspath(path_folder)
    status_list = []
    for index, row in df.iterrows():
        driver = open_browser(path_download)  # Mở browser mới cho mỗi hóa đơn
        ma_so_thue = str(row['Mã số thuế']).replace("'", "").strip()
        if len(ma_so_thue) == 9:
            ma_so_thue = "0" + ma_so_thue
        ma_tra_cuu = str(row['Mã tra cứu']).strip()
        url = str(row['URL']).strip() if 'URL' in row else None

        if not ma_tra_cuu:
            status_list.append("fail: thiếu mã tra cứu")
            driver.quit()
            continue

        print(f"Đang xử lý: {ma_so_thue} - {ma_tra_cuu}")
        try:
            if url and "fpt" in url:
                ok, status = retry_action(process_fpt_invoice, 2, driver, url, ma_so_thue, ma_tra_cuu)
            elif url and "meinvoice" in url:
                ok, status = retry_action(process_me_invoice, 2, driver, url, ma_so_thue, ma_tra_cuu)
            elif url and "van.ehoadon" in url:
                ok, status = retry_action(process_van_e_invoice, 2, driver, url, ma_so_thue, ma_tra_cuu)
            else:
                ok, status = False, f"fail: Không hỗ trợ URL: {url}"
        except Exception as e:
            ok, status = False, f"fail: {type(e).__name__}: {str(e)}"
        if ok:
            status_list.append("success")
        else:
            # Nếu status rỗng thì gán fail mặc định
            status_list.append(status if status else "fail: unknown error")
        driver.quit()  # Đóng browser sau mỗi hóa đơn
        time.sleep(2)
    df['status'] = status_list
    return df

def doc_input(file_path="input.xlsx"):
    df = pd.read_excel(file_path, dtype=str)
    return df

def parse_invoice_xml(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        ns = {}
        if '}' in root.tag:
            uri = root.tag[root.tag.find("{")+1:root.tag.find("}")]
            ns = {'ns': uri}
            def f(tag): return f'.//ns:{tag}'
        else:
            def f(tag): return f'.//{tag}'
        # Trích xuất đủ 8 trường
        so_hoa_don = root.find(f('TTChung/SHDon'), ns)
        ten_ban_hang = root.find(f('NDHDon/NBan/Ten'), ns)
        ma_so_thue_ban = root.find(f('NDHDon/NBan/MST'), ns)
        dia_chi_ban = root.find(f('NDHDon/NBan/DChi'), ns)
        so_tai_khoan_ban = root.find(f('NDHDon/NBan/STKNHang'), ns)
        ten_mua = root.find(f('NDHDon/NMua/Ten'), ns)
        dia_chi_mua = root.find(f('NDHDon/NMua/DChi'), ns)
        ma_so_thue_mua = root.find(f('NDHDon/NMua/MST'), ns)
        return {
            'Số hóa đơn': so_hoa_don.text if so_hoa_don is not None else '',
            'Đơn vị bán hàng': ten_ban_hang.text if ten_ban_hang is not None else '',
            'Mã số thuế bán': ma_so_thue_ban.text if ma_so_thue_ban is not None else '',
            'Địa chỉ bán': dia_chi_ban.text if dia_chi_ban is not None else '',
            'Số tài khoản bán': so_tai_khoan_ban.text if so_tai_khoan_ban is not None else '',
            'Họ tên người mua hàng': ten_mua.text if ten_mua is not None else '',
            'Địa chỉ mua': dia_chi_mua.text if dia_chi_mua is not None else '',
            'Mã số thuế mua': ma_so_thue_mua.text if ma_so_thue_mua is not None else '',
            'status_extract': 'success'
        }
    except Exception as e:
        return {
            'Số hóa đơn': '',
            'Đơn vị bán hàng': '',
            'Mã số thuế bán': '',
            'Địa chỉ bán': '',
            'Số tài khoản bán': '',
            'Họ tên người mua hàng': '',
            'Địa chỉ mua': '',
            'Mã số thuế mua': '',
            'status_extract': f'fail: {str(e)}'
        }

def process_all_xml(folder='downloads'):
    data = []
    files = [f for f in os.listdir(folder) if f.endswith('.xml')]
    for file in files:
        full_path = os.path.join(folder, file)
        row = parse_invoice_xml(full_path)
        row['xml_file'] = file
        data.append(row)
    return pd.DataFrame(data)

def merge_input_output(input_df, output_df):
    # Gắn thông tin XML vào input theo thứ tự (nếu số lượng khớp)
    if len(input_df) == len(output_df):
        merged = pd.concat([input_df.reset_index(drop=True), output_df.reset_index(drop=True)], axis=1)
    else:
        # Nếu không khớp, merge theo thứ tự và điền thiếu nếu cần
        merged = input_df.copy()
        for col in output_df.columns:
            merged[col] = output_df[col] if col in output_df else ''
    return merged

def save_to_excel(df, file_out='output.xlsx'):
    # Xóa cột 'status_extract' nếu có
    if 'status_extract' in df.columns:
        df = df.drop(columns=['status_extract'])
    df.to_excel(file_out, index=False)

if __name__ == "__main__":
    input_df = doc_input()
    download_status_df = process_invoice(input_df)
    output_df = process_all_xml("downloads")
    final_df = merge_input_output(download_status_df, output_df)
    save_to_excel(final_df, file_out='output.xlsx')