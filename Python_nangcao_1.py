# Mình cần vài thứ từ thư viện của Python, nên mình "import" nó vào
import math   # Cái này để dùng các phép toán, như lấy căn bậc hai
import random # Cái này để tạo số ngẫu nhiên cho trò chơi đoán số
import time   # Cái này để lấy thời gian hệ thống, cũng cho trò đoán số

# Bài 1: Tìm số chia hết cho 3 (không phải số chính phương)

# Đầu tiên, mình viết một hàm nhỏ để kiểm tra xem một số có phải là số chính phương không.
# Số chính phương là số mà khi lấy căn bậc hai thì ra một số nguyên (ví dụ 9 là số chính phương vì căn của 9 là 3).
def kiem_tra_so_chinh_phuong(so_can_kiem_tra):
    """Hàm này nhận vào một số, trả về True nếu nó là số chính phương, False nếu không phải."""
    if so_can_kiem_tra < 0: # Số âm thì chắc chắn không phải rồi
        return False
    if so_can_kiem_tra == 0: # Số 0 cũng được coi là số chính phương (0*0=0)
        return True
    
    # Tính căn bậc hai của số đó
    can_bac_hai = math.sqrt(so_can_kiem_tra)
    
    # Kiểm tra xem căn bậc hai đó có phải là số nguyên không
    # Cách 1: Dùng math.isqrt (nếu Python 3.8 trở lên)
    # phan_nguyen_can_bac_hai = math.isqrt(so_can_kiem_tra) 
    # return phan_nguyen_can_bac_hai * phan_nguyen_can_bac_hai == so_can_kiem_tra

    # Cách 2: So sánh căn bậc hai với phần nguyên của nó (dễ hiểu hơn cho mọi phiên bản)
    # Ví dụ: căn của 9 là 3.0, phần nguyên của 3.0 là 3. 3.0 == 3 là True.
    # Ví dụ: căn của 8 là 2.828..., phần nguyên của nó là 2. 2.828... == 2 là False.
    if can_bac_hai == int(can_bac_hai):
        return True # Nếu bằng nhau, tức là số nguyên, vậy nó là số chính phương
    else:
        return False # Ngược lại thì không phải

def bai_1_tim_so():
    """Hàm chính cho Bài 1."""
    print("\n--- BÀI TẬP 1: TÌM SỐ ĐẶC BIỆT ---") 
    print("Chương trình sẽ tìm các số chia hết cho 3 nhưng không phải số chính phương.")

    # Mình cần người dùng nhập vào hai số a và b
    # Mình dùng vòng lặp `while True` để nếu người dùng nhập sai thì bắt nhập lại
    while True:
        print("\n--- Nhập khoảng số ---") 
        try:
            # input() sẽ trả về một chuỗi, mình cần đổi nó thành số nguyên bằng int()
            a_str = input("Nhập số bắt đầu (a): ")
            a = int(a_str)
            
            b_str = input("Nhập số kết thúc (b): ")
            b = int(b_str)

            # Kiểm tra điều kiện a < b
            if a >= b:
                print("Lỗi! Số 'a' phải nhỏ hơn số 'b'. Mời bạn nhập lại.")
                # continue sẽ bỏ qua phần còn lại của vòng lặp này và bắt đầu lại từ đầu
                continue 
            
            # Nếu mọi thứ ổn, mình thoát khỏi vòng lặp nhập liệu này
            break 
        except ValueError:
            # Nếu người dùng nhập chữ thay vì số, int() sẽ báo lỗi ValueError
            print("Lỗi! Bạn phải nhập số nguyên. Mời bạn nhập lại.")

    print(f"\nĐang tìm các số trong khoảng từ {a} đến {b}...")
    
    # Tạo một danh sách rỗng để lưu các số tìm được
    cac_so_tim_duoc = []

    # Dùng vòng lặp for để duyệt qua từng số từ a đến b
    # range(a, b + 1) sẽ tạo ra dãy số từ a, a+1, ..., b
    for so_hien_tai in range(a, b + 1):
        # Điều kiện 1: Số đó phải chia hết cho 3
        chia_het_cho_3 = (so_hien_tai % 3 == 0)
        
        # Điều kiện 2: Số đó không phải là số chính phương
        khong_phai_chinh_phuong = not kiem_tra_so_chinh_phuong(so_hien_tai)
        
        # Nếu cả hai điều kiện đều đúng thì mình thêm số đó vào danh sách
        if chia_het_cho_3 and khong_phai_chinh_phuong:
            # Mình thêm số đó dưới dạng chuỗi để lát nữa nối lại cho dễ
            cac_so_tim_duoc.append(str(so_hien_tai))
            
    # Sau khi duyệt hết, mình kiểm tra xem có tìm được số nào không
    if len(cac_so_tim_duoc) > 0:
        print("Các số thoả mãn điều kiện là:")
        # Dùng ",".join() để nối các số trong danh sách lại, cách nhau bằng dấu phẩy
        print(",".join(cac_so_tim_duoc))
    else:
        print(f"Không tìm thấy số nào trong khoảng [{a}, {b}] thoả mãn điều kiện.")

# Bài 2: Game đoán số

# Hàm này để tạo ra một số bí mật cho trò chơi
def tao_so_bi_mat():
    """Hàm này tạo một số ngẫu nhiên từ 1 đến 999."""
    # Yêu cầu là "sinh từ phần miligiây của thời gian hệ thống hiện tại"
    # time.time() trả về số giây tính từ một thời điểm gốc, có cả phần thập phân (miligiây)
    # Ví dụ: 1678886400.123456
    # Mình nhân với 1000 để đưa phần miligiây lên trước dấu chấm: 1678886400123.456
    # Rồi lấy phần nguyên: 1678886400123
    # Đây sẽ là "hạt giống" (seed) cho việc tạo số ngẫu nhiên, để mỗi lần chạy có thể khác nhau
    # một chút theo thời gian.
    hat_giong = int(time.time() * 1000)
    random.seed(hat_giong) # "Gieo hạt" cho bộ tạo số ngẫu nhiên
    
    so_ngau_nhien = random.randint(1, 999) # Tạo số nguyên ngẫu nhiên từ 1 đến 999
    return so_ngau_nhien

def bai_2_tro_choi_doan_so():
    """Hàm chính cho Bài 2."""
    print("\n--- BÀI TẬP 2: TRÒ CHƠI ĐOÁN SỐ (1-999) ---") 
    print("Chào mừng bạn đến với trò chơi Đoán Số!")
    print("Máy tính đã chọn một số bí mật từ 1 đến 999. Bạn hãy thử đoán xem!")

    # Máy tính tạo ra một số bí mật
    so_bi_mat = tao_so_bi_mat()
    # Nếu bạn muốn xem trước số bí mật để dễ kiểm tra code, bỏ dấu # ở dòng dưới:
    # print(f"(Máy tính nói nhỏ: Số bí mật là {so_bi_mat} đó nha!)") 
    
    so_lan_doan_sai_lien_tiep = 0
    so_lan_doan_sai_toi_da = 5 # Sau 5 lần sai thì đổi số
    
    # Vòng lặp chính của trò chơi, lặp cho đến khi người chơi đoán đúng
    while True:
        print("-----------------------------------------") # Vạch kẻ cho dễ nhìn
        try:
            # Yêu cầu người chơi nhập số đoán
            chuoi_nguoi_doan = input(f"Mời bạn đoán số (còn {so_lan_doan_sai_toi_da - so_lan_doan_sai_lien_tiep} lần sai trước khi đổi số): ")
            so_nguoi_doan = int(chuoi_nguoi_doan)

            # Kiểm tra xem số đoán có hợp lệ không (từ 1 đến 999)
            if not (1 <= so_nguoi_doan <= 999):
                print("Ối! Bạn phải đoán một số từ 1 đến 999 thôi. Thử lại nhé!")
                continue # Quay lại đầu vòng lặp để người chơi nhập lại

            # So sánh số người đoán với số bí mật
            if so_nguoi_doan == so_bi_mat:
                print(f"HOAN HÔ! Bạn đã dự đoán chính xác số {so_bi_mat}! Bạn thật giỏi!")
                break # Thoát khỏi vòng lặp, kết thúc trò chơi
            else:
                # Nếu đoán sai
                so_lan_doan_sai_lien_tiep = so_lan_doan_sai_lien_tiep + 1
                print(f"Tiếc quá, sai rồi! Bạn đã trả lời sai {so_lan_doan_sai_lien_tiep} lần.")

                # Kiểm tra xem đã sai 5 lần chưa
                if so_lan_doan_sai_lien_tiep >= so_lan_doan_sai_toi_da:
                    print("Bạn đoán trật tất cả năm lần, kết quả đã thay đổi.")
                    so_bi_mat = tao_so_bi_mat() # Tạo số bí mật mới
                    # print(f"(Máy tính nói nhỏ: Số bí mật MỚI là {so_bi_mat} đó nha!)")
                    so_lan_doan_sai_lien_tiep = 0 # Reset số lần đoán sai
                    print("Mời bạn đoán lại từ đầu với số mới!")
                # Nếu chưa sai 5 lần, kiểm tra xem có gần đúng không
                elif abs(so_nguoi_doan - so_bi_mat) <= 10:
                    # abs() là hàm lấy giá trị tuyệt đối (khoảng cách)
                    # Nếu khoảng cách từ số đoán đến số bí mật nhỏ hơn hoặc bằng 10
                    print("Bạn đoán gần đúng rồi đó! Cố lên!")
                    
        except ValueError:
            # Nếu người chơi nhập chữ thay vì số
            print("Huhu, bạn phải nhập một số nguyên cơ. Thử lại nào!")

# Chạy các bài tập
# Code trong khối if __name__ == "__main__": chỉ chạy khi file này được thực thi trực tiếp.
if __name__ == "__main__":
    # Chạy Bài 1 trước
    bai_1_tim_so()
    
    # In một dòng ngăn cách cho đẹp
    print("\n\n========================================\n")
    
    # Sau đó chạy Bài 2
    bai_2_tro_choi_doan_so()

    print("\nCảm ơn bạn đã sử dụng chương trình!")
