import PyPDF2

import random

MAX_MESSAGE_LENGTH = 4096



def ConvertMealToMoney(meal: str) -> int:
    h = {
        "🍽 10 000 теңге": 10000,
        "🍽 25 000 теңге": 25000,
        "🍽 35 000 теңге": 35000,
        "🍽 45 000 теңге": 45000,
    }

class Generator:
    @staticmethod
    def generate_random_int(length=8):
        range_start = 10**(length-1)
        range_end = (10**length) - 1
        return random.randint(range_start, range_end)

class PDFReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file = None
        self.reader = None

    def open_pdf(self):
        self.file = open(self.file_path, 'rb')
        self.reader = PyPDF2.PdfReader(self.file)
    
    def close_pdf(self):
        if self.file:
            self.file.close()
    
    def get_number_of_pages(self):
        return len(self.reader.pages) if self.reader else 0
    
    def extract_text_from_page(self, page_num):
        if self.reader:
            page = self.reader.pages[page_num]
            return page.extract_text()
        return ""

    def determine_language(self):
        if self.reader:
            first_page_text = self.extract_text_from_page(0)
            if "Покупки" in first_page_text:
                return 'russian'
            elif "Счет на оплату" in first_page_text:
                return 'russian'
            elif "Сатып алғаным" in first_page_text:
                return 'kazakh'
            elif "Төлем шоты" in first_page_text:
                return 'kazakh'
        return 'unknown'
    
    def extract_specific_info(self):
        language = self.determine_language()
        if language == 'kazakh':
            specific_keywords = [
                "Төлем шоты", 
                "Төлем сәтті өтті", 
                "₸", 
                "Түбіртек №", 
                "БСН", 
                "Күні мен уақыты", 
                "Төлеушінің аты-жөні", 
                "Төленді", 
                "Мекенжай"
            ]
        elif language == 'russian':
            specific_keywords = [
                "Счет на оплату", 
                "Pharmacom", 
                "Платеж успешно совершен", 
                "₸", 
                "№ чека", 
                "БИН", 
                "Дата и время", 
                "ФИО плательщика", 
                "Оплачено с", 
                "Адрес"
            ]
        else:
            return ["Language not recognized."]

        result_lines = []
        number_of_pages = self.get_number_of_pages()
        for page_num in range(number_of_pages):
            text = self.extract_text_from_page(page_num)
            lines = text.split('\n')
            for line in lines:
                if any(keyword in line for keyword in specific_keywords):
                    result_lines.append(line)
        return result_lines

def convert_currency_to_int(currency_str):
    try:
        # Remove spaces and currency symbol
        clean_str = currency_str.replace(' ', '').replace('₸', '')
        # Convert the cleaned string to an integer
        return int(clean_str)
    except ValueError as e:
        print(f"Ошибка: не удалось преобразовать строку '{currency_str}' в целое число. {e}")
        return None


def split_message(text):
    """Splits a message into chunks not exceeding the maximum message length."""
    if len(text) <= MAX_MESSAGE_LENGTH:
        return [text]
    lines = text.split('\n')
    chunks = []
    chunk = ''
    for line in lines:
        if len(chunk) + len(line) + 1 > MAX_MESSAGE_LENGTH:
            chunks.append(chunk)
            chunk = line
        else:
            if chunk:
                chunk += '\n'
            chunk += line
    if chunk:
        chunks.append(chunk)
    return chunks

if __name__ == "__main__":
    #file_path = input("Enter the path to the PDF file: ")
    
    #pdf_reader = PDFReader(file_path)
    #pdf_reader.open_pdf()
    #pdf_reader.print_pdf_result()
    #pdf_reader.close_pdf()

    # Example usage
    currency_str = '500 000 ₸'
    converted_int = convert_currency_to_int(currency_str)
    print(converted_int)  # Output: 2000

