import os
import argparse

def select_longest_sequence(input_file, output_file):
    longest_seq = ""
    longest_id = ""
    current_id = ""
    current_seq = ""

    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if current_seq and len(current_seq) > len(longest_seq):
                    longest_seq = current_seq
                    longest_id = current_id
                current_id = line[1:] 
                current_seq = ""
            else:
                current_seq += line

    if current_seq and len(current_seq) > len(longest_seq):
        longest_seq = current_seq
        longest_id = current_id

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as out_f:
        out_f.write(f">{longest_id}\n{longest_seq}\n")

    print(f"Обработан {input_file}. Самая длинная последовательность сохранена в {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Select the longest sequence from a single FASTA file.')
    parser.add_argument('--input', required=True, help='Input FASTA file')
    parser.add_argument('--output', required=True, help='Output FASTA file for the longest sequence')
    args = parser.parse_args()

    select_longest_sequence(args.input, args.output)

if __name__ == "__main__":
    main()
