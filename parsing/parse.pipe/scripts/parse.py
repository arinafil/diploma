import os
import argparse
import pandas as pd
from collections import defaultdict

def parse_hhr_file(file_path):
    """Парсинг одного .hhr файла и извлечение данных."""
    data = defaultdict(list)
    query = None
    database_type = os.path.basename(file_path).split('_')[-1].split('.')[0]  # Например, 'pdb' или 'cdd'
    with open(file_path, 'r', encoding='utf-8') as f:
        in_hits_section = False
        for line in f:
            line = line.strip()
            # Извлечение Query
            if line.startswith('Query'):
                query = line.split()[1] if len(line.split()) > 1 else "Unknown"
            # Начало секции с совпадениями
            elif line.startswith('No Hit'):
                in_hits_section = True
                continue
            # Конец секции с совпадениями
            elif in_hits_section and (line.startswith('No ') or line.startswith('>')):
                in_hits_section = False
                continue
            # Парсинг строк с совпадениями
            elif in_hits_section and line and not line.startswith('---'):
                parts = line.split()
                if len(parts) >= 2:  # Минимально номер и hit_id
                    try:
                        hit_no = int(parts[0].lstrip('-')) if parts[0].lstrip('-').isdigit() else None
                        hit_id = parts[1] if len(parts) > 1 else "Unknown"
                        # Поиск Probability (первый float после hit_id)
                        prob_idx = next((i for i, x in enumerate(parts[2:]) if is_floatable(x)), None)
                        prob = float(parts[prob_idx + 2]) if prob_idx is not None and prob_idx + 2 < len(parts) and is_floatable(parts[prob_idx + 2]) else None
                        evalue = float(parts[prob_idx + 3]) if prob_idx is not None and prob_idx + 3 < len(parts) and is_floatable(parts[prob_idx + 3]) else None
                        # Извлечение description
                        description_start = 2 if prob_idx is not None else 2
                        description_end = prob_idx + 2 if prob_idx is not None else len(parts)
                        description = ' '.join(parts[description_start:description_end]).rstrip(';') if description_end > description_start else "No description"
                        if query and hit_id:
                            data[query].append({
                                'hits_id': hit_id,
                                'probability': prob,
                                'evalue': evalue,
                                'description': description,
                                'database': database_type
                            })
                    except (IndexError, ValueError) as e:
                        print(f"Warning: Partial data extracted from malformed line due to {e}: {line} in {file_path}")
                        hit_id = parts[1] if len(parts) > 1 else "Unknown"
                        description = ' '.join(parts[2:]).rstrip(';') if len(parts) > 2 else "No description"
                        data[query].append({
                            'hits_id': hit_id,
                            'probability': None,
                            'evalue': None,
                            'description': description,
                            'database': database_type
                        })
    return data

def is_floatable(value):
    """Проверяет, можно ли преобразовать строку в float."""
    try:
        float(value)
        return True
    except ValueError:
        return False

def combine_annotations(hhr_files):
    """Объединение данных из всех .hhr файлов."""
    all_data = defaultdict(list)
    for hhr_file in hhr_files:
        file_data = parse_hhr_file(hhr_file)
        for query, entries in file_data.items():
            all_data[query].extend(entries)
    rows = []
    for query, entries in all_data.items():
        for entry in entries:
            row = {
                'protein_context_id': query,
                'hits_id': entry['hits_id'],
                'probability': entry['probability'],
                'evalue': entry['evalue'],
                'description': entry['description'],
                'database': entry['database']
            }
            rows.append(row)
    return pd.DataFrame(rows)

def main():
    parser = argparse.ArgumentParser(description='Parse hhsearch .hhr files and generate annotations.')
    parser.add_argument('--hhr-files', nargs='+', required=True, help='List of .hhr files to parse')
    parser.add_argument('--output', required=True, help='Output CSV file path')
    args = parser.parse_args()

    hhr_files = [f for f in args.hhr_files if os.path.isfile(f)]
    if not hhr_files:
        raise FileNotFoundError("No valid .hhr files found")

    df = combine_annotations(hhr_files)
    df.to_csv(args.output, index=False)
    print(f"Annotations saved to {args.output}")

if __name__ == '__main__':
    main()
