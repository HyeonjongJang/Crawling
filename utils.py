import csv

def load_csv(csv_file_path):
    data = []
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        header_skipped = False
        
        for row in reader:
            if not header_skipped:
                # Skip the first row (header)
                header_skipped = True
                continue
            
            data.append(row)
    
    return data


