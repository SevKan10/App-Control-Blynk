import tkinter as tk
import requests
import pygame.mixer

# Hàm để dừng âm thanh
#----------------------------------------------------------------------------------------------------------------------------------

# Hàm kết thúc cuộc gọi
def end_call():
    status_label.config(text="Nhấn nút để điều khiển thiết bị")
    sos_button.config(state="normal")  # Kích hoạt lại nút Gọi SOS

# Hàm gửi dữ liệu lên Blynk và thay đổi trạng thái bật/tắt
def toggleDevice(button, pin, value_on, value_off, i):
    # Nếu là nút 9, chỉ gửi tín hiệu điện một lần
    if i == 9:
        # Gửi giá trị 1 khi nhấn nút 9
        url = f"https://sgp1.blynk.cloud/external/api/update?token=uEoemYVMdj8HNX2i4Pa3cYGiMI-Brjhq&{pin}=1"
        response = requests.get(url)
        
        if response.status_code == 200:
            print("Đang gọi")
            status_label.config(text="Đang gọi")
            pygame.mixer.music.load("call.wav")
            pygame.mixer.music.play()
            sos_button.config(state="disabled")  # Vô hiệu hóa nút Gọi SOS
            
            # Kết thúc cuộc gọi sau 18 giây
            root.after(18000, end_call)  # Gọi hàm end_call sau 18 giây

        else:
            print("Có lỗi xảy ra:", response.status_code, response.text)
            status_label.config(text=f"Có lỗi xảy ra khi gửi tín hiệu: {response.status_code} {response.text}")
        return

    # Các thiết bị còn lại (1 đến 4) sẽ hoạt động như bình thường
    current_text = button.cget("text")
    if "Mở" in current_text:
        value = value_on
        new_text = f"Tắt thiết bị {i}"
        button.config(bg="green")  # Đổi màu sang xanh lá khi bật
    else:
        value = value_off
        new_text = f"Mở thiết bị {i}"
        button.config(bg="red")  # Đổi màu sang đỏ khi tắt
    
    # Gửi dữ liệu lên Blynk
    url = f"https://sgp1.blynk.cloud/external/api/update?token=uEoemYVMdj8HNX2i4Pa3cYGiMI-Brjhq&{pin}={value}"
    response = requests.get(url)
    
    if response.status_code == 200:
        print(f"Đèn {i} đã được {value}")
        if value == value_on:  # Nếu đèn được bật
            status_label.config(text=f"Đèn {i} đã được bật")
        elif value == value_off:  # Nếu đèn được tắt
            status_label.config(text=f"Đèn {i} đã được tắt")
        button.config(text=new_text)  # Cập nhật văn bản nút
        
        # Phát âm thanh cho các nút khác
        pygame.mixer.music.load("on.wav" if value == value_on else "off.wav")  # Âm thanh mặc định
        pygame.mixer.music.play()
    else:
        print("Có lỗi xảy ra:", response.status_code, response.text)
        status_label.config(text=f"Có lỗi xảy ra khi thay đổi đèn {i}: {response.status_code} {response.text}")

# Hàm đồng bộ giá trị từ Blynk cho các thiết bị 1 đến 4
def sync_device_states():
    for text, pin, value_on, value_off, i in devices[:-1]:  # Lấy các thiết bị 1 đến 4
        url = f"https://sgp1.blynk.cloud/external/api/get?token=uEoemYVMdj8HNX2i4Pa3cYGiMI-Brjhq&{pin}"
        response = requests.get(url)
        
        if response.status_code == 200:
            current_value = response.text  # Giá trị hiện tại
            if current_value == value_on:
                button_text = f"Tắt thiết bị {i}"
                button_color = "green"
            else:
                button_text = f"Mở thiết bị {i}"
                button_color = "red"

            # Cập nhật trạng thái của nút
            button = buttons[i - 1]  # Truy cập nút dựa trên chỉ số
            button.config(text=button_text, bg=button_color)
        else:
            print(f"Có lỗi xảy ra khi lấy giá trị thiết bị {i}: {response.status_code} {response.text}")

    # Gọi hàm này sau mỗi 5 giây
    root.after(5000, sync_device_states)

#----------------------------------------------------------------------------------------------------------------------------------

# Khởi tạo giao diện đồ họa
root = tk.Tk()
root.geometry("500x250")
root.title("Control Devices via Blynk")
root.configure(bg='#97CADB')  # Màu nền chính

status_label = tk.Label(root, text="Nhấn nút để điều khiển thiết bị", bg='#97CADB', font=('Helvetica', 12))
status_label.pack(pady=10)

#----------------------------------------------------------------------------------------------------------------------------------

# Tạo khung chứa các nút
button_frame = tk.Frame(root, bg='#97CADB')
button_frame.pack(pady=10)

# Danh sách các thiết bị
devices = [
    ("Mở thiết bị 1", "v1", "1", "0", 1),
    ("Mở thiết bị 2", "v2", "1", "0", 2),
    ("Mở thiết bị 3", "v3", "1", "0", 3),
    ("Mở thiết bị 4", "v4", "1", "0", 4),
    ("Gọi SOS", "v0", "", "", 9),
]

# Tạo danh sách để lưu các nút
buttons = []

# Tạo các nút theo bố cục 2 cột và nút 9 ở giữa
row = 0
col = 0

for text, pin, value_on, value_off, i in devices:
    # Khởi tạo nút
    button = tk.Button(button_frame, text=text, 
                       bg='red', fg='#D6E8EE', font=('Helvetica', 12, 'bold'), 
                       width=20, relief="raised", highlightthickness=2, highlightbackground="black")
    
    # Đặt command sau khi nút được tạo
    button.config(command=lambda b=button, p=pin, on=value_on, off=value_off, idx=i: toggleDevice(b, p, on, off, idx))
    
    # Sắp xếp nút vào giao diện
    if i == 9:  # Nút 9 nằm giữa
        sos_button = button  # Lưu nút Gọi SOS vào biến sos_button
        button.grid(row=row+2, column=0, columnspan=2, padx=10, pady=10)
    else:
        button.grid(row=row, column=col, padx=10, pady=10)
        buttons.append(button)  # Thêm nút vào danh sách buttons
    
        # Chuyển cột sau khi điền đủ 2 nút
        col += 1
        if col > 1:
            col = 0
            row += 1

# Đồng bộ hóa giá trị ban đầu từ Blynk
sync_device_states()

#----------------------------------------------------------------------------------------------------------------------------------

# Khởi tạo âm thanh
pygame.mixer.init()

#----------------------------------------------------------------------------------------------------------------------------------

root.mainloop()
