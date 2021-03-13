import count
from pathlib import Path

def main():
    print("Generating augment data")
    file_paths = Path('robustqa/datasets/oodomain_train').glob('*')
    for file_path in file_paths:
        print("Processing: " + str(file_path))
        count.read(file_path)

if __name__ == '__main__':
    main()
