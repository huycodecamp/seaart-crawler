from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import argparse
import time  # Thêm thư viện time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import os
import concurrent.futures
from functools import partial

def scroll_to_bottom(driver):
    # Scroll xuống dưới cùng của trang web bằng cách thực thi mã JavaScript
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Chờ một chút để cho trang web cuộn xuống và dữ liệu mới hiển thị
def slow_scroll(driver, distance, delay):
    # Lặp lại cuộn theo khoảng cách và chờ một khoảng thời gian
    for _ in range(0, distance, 10):  # Cuộn 10 pixel mỗi lần
        driver.execute_script("window.scrollBy(0, 100);")
        time.sleep(delay)  # Chờ một khoảng thời gian
def scroll_by_pixels(driver, pixels):
    # Cuộn xuống một số pixel cụ thể
    driver.execute_script(f"window.scrollBy(0, {pixels});")
    time.sleep(2)  # Chờ một chút để cho trang web cuộn xuống và dữ liệu mới hiển thị

def download_image_in_a_tag(a_element, a_link, keyword, subword):
    img_tag = a_element.find_element(By.TAG_NAME, 'img')
    img_src = img_tag.get_attribute("src")
    #Link ảnh
    img_quality_link = img_src.replace("_low.webp", ".png")
    # Ten file
    file_name = a_link.split("/")[-1] + '.png';
    # Tạo đường dẫn đầy đủ để lưu tệp
    save_path = os.path.join("downloads",keyword,subword,file_name)
    try:

        # Tải ảnh từ URL
        response = requests.get(img_quality_link)

        # Kiểm tra xem yêu cầu tải ảnh có thành công không (status code 200)
        if response.status_code == 200:
            # Lưu ảnh vào thư mục /downloads/{keyword}
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb") as img_file:
                img_file.write(response.content)
            print(f"Đã tải và lưu: {save_path}")
        else:
            print(f"Lỗi tải ảnh từ: {img_quality_link}")
    except Exception:
        print("Error while download")
# Hàm để xử lý một link cụ thể
def process_link(link, keyword):
    # Tạo một Selenium Chrome Driver mới
    subword = link.split("/")[-1]
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--force-device-scale-factor=0.25")
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    
    try:
        # Mở URL và in tiêu đề trang
        driver.get(link)
        print("Link:", link)
        collected_links = []
        while True:
            scroll_by_pixels(driver, 1000)
           
            # Thu thập các liên kết sau mỗi lần cuộn
            links = driver.find_elements(
                By.XPATH, '//a[contains(@class, "waterfall-item")]'
            )
            for link in links:
                img_link = link.get_attribute("href")
                if img_link not in collected_links:
                    collected_links.append(img_link)
                    download_image_in_a_tag(link, img_link, keyword, subword)
            # Kiểm tra xem có thẻ div có class là 'at-bottom' xuất hiện không
            at_bottom_div = driver.find_elements(By.XPATH, '//div[@class="at-bottom"]')
            if at_bottom_div:
                break  # Nếu có, thoát khỏi vòng lặp
    finally:
        # Đóng trình duyệt và giải phóng tài nguyên
        driver.quit()


def main(keyword):
    # Khởi tạo trình duyệt (sử dụng Chrome)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--force-device-scale-factor=0.25")
    driver = webdriver.Chrome(options=chrome_options)
    # Phóng to trình duyệt ra full màn hình
    driver.maximize_window()

    # Điều hướng đến trang https://seaart.ai/explore
    driver.get("https://seaart.ai/explore")

    try:
        # Trong thẻ div 'el-input', tìm ô input bằng class name 'el-input__inner'
        search_input = driver.find_element(
            By.XPATH,
            '//*[@id="app"]/section/header/div/div[2]/div/div/div[1]/div[2]/input',
        )

        # Gửi keyword vào ô tìm kiếm
        search_input.send_keys(keyword)
        # Chờ một chút trước khi gửi Enter
        time.sleep(2)
        search_input.send_keys(Keys.RETURN)
        # Chờ một chút trước khi gửi Enter
        time.sleep(2)

        collected_links = []
        while True:
            scroll_by_pixels(driver, 1000)
           
            # Thu thập các liên kết sau mỗi lần cuộn
            links = driver.find_elements(
                By.XPATH, '//a[contains(@class, "waterfall-item")]'
            )
            for link in links:
                img_link = link.get_attribute("href")
                if img_link not in collected_links:
                    collected_links.append(img_link)
            # Kiểm tra xem có thẻ div có class là 'at-bottom' xuất hiện không
            at_bottom_div = driver.find_elements(By.XPATH, '//div[@class="at-bottom"]')
            if at_bottom_div:
                break  # Nếu có, thoát khỏi vòng lặp

        # In ra danh sách các liên kết hình ảnh
        print("Danh sách các liên kết hình ảnh:")
        for link in collected_links:
            print(link)
        # Số luồng bạn muốn sử dụng
        num_threads = 10
        # Tạo một phiên bản mới của hàm process_link với tham số keyword đã cung cấp
        process_link_with_keyword = partial(process_link, keyword=keyword)
        # Sử dụng ThreadPoolExecutor để xử lý các link đồng thời
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            executor.map(process_link_with_keyword, collected_links)
         # Để trình duyệt mở để bạn kiểm tra
        input("Nhấn Enter để kết thúc...")

    finally:
        # Cuối cùng, đóng trình duyệt
        # driver.quit()
        print("OK")


if __name__ == "__main__":
    # Sử dụng argparse để chấp nhận keyword thông qua tham số -k
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--keyword", required=True, help="Keyword for search")
    args = parser.parse_args()

    # Gọi hàm main với keyword từ tham số
    main(args.keyword)
