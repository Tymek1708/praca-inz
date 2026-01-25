'''
Utilsy używane przez skrypt_overseer1.py
'''
import json
import os
from collections import Counter 
import pandas as pd
from tqdm import tqdm
import networkx as nx
import glob

## Funkcje pomocnicze
def open_json_file(input_file) -> list:
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        if isinstance(data, dict):
            data = [data]

        return data
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file '{input_file}', skipping.")
def save_list_to_json_file(said_list, target_file):
    if os.path.exists(target_file):
        answer = input(f"Plik o nazwie'{target_file}' już istnieje. Czy chcesz go nadpisać? (y/n): ").strip().lower()
        if answer != 'y':
            print(f"Zapis anulowany w celu uniknięcia nadpisania.")
            return
    try:
        with open(target_file, 'w', encoding='utf-8') as file:
            json.dump(said_list, file, ensure_ascii=False, indent=4)
        print(f"Zapisano {len(said_list)} obiektów do pliku: {target_file}")
    except Exception as e:
        print(f"Niespodziewany błąd: {e}")
def create_dir(dir_path: str) -> None:
    try:
        os.makedirs(dir_path)
        print(f"Nested directories {dir_path} created successfully.")
    except FileExistsError:
        print(f"One or more directories in '{dir_path}' already exist.")
    except PermissionError:
        print(f"Permission denied: Unable to create '{dir_path}'.")
    except Exception as e:
        print(f"An error occurred: {e}")



## Funkcje do tworzenia sieci
def build_indices(comments_list: list) -> dict:
    group_name_dict = {}
    for comment in comments_list:
        # group_name = comment['input']['url'].split('/')[3] # dla stron fb
        group_name = comment['input']['url'].split('/')[4] # dla grup fb
        group_name_dict.setdefault(group_name, []).append(comment)
    return group_name_dict

def create_network_file(comments_list, group_name):
    time_user_to_user_from_list = list(map(lambda comment: "{}_{}_{}".format(comment['date_created'], comment['user_name'], comment['adresat']), tqdm(comments_list, desc=f"Mapowanie komentarzy dla grupy {group_name}: ", unit="komentarz")))
    zliczone_interakcje = Counter(time_user_to_user_from_list)
    print("Tworzenie DataFrame.")
    pierwsza_seria_danych_DF = pd.DataFrame.from_dict(zliczone_interakcje, orient='index').reset_index()
    print("DataFrame stworzony.")
    pierwsza_seria_danych_DF = pierwsza_seria_danych_DF.rename(columns={'index':'interakcja', 0:'waga'})
    print(f"Operacje skończone. Zpisywanie do pliku test_file_{group_name}.csv")
    pierwsza_seria_danych_DF.to_csv(f'test_file_{group_name}.csv', index=False)
    print("Koniec.")

def create_network_file_per_group(comments_file):
    comments_list = open_json_file(comments_file)
    group_name_dict = build_indices(comments_list)
    for group in group_name_dict:
        print('==================================')
        print(f'Rozpoczynam tworzenie pliku dla grupy {group}.')
        comments_list = group_name_dict[group]
        print(f'Liczba komentarzy w grupie {group}: {len(comments_list)}')
        create_network_file(comments_list=comments_list, group_name=group)

# create_network_file_per_group("finalne_zmergowane_komentarze_gotowe_do_tworzenia_sieci.json")

## Funkcja do naprawienia plików sieci (ustawiania odpowiednich kolumn)
def correct_network_file(network_file):
    group_name = network_file.split('_')[2]
    group_name = group_name.split('.')[0]
    df = pd.read_csv(network_file)
    df[["time", "user_from", "user_to"]] = df.interakcja.str.split("_", expand=True)
    df = df.drop('interakcja', axis=1)
    df = df.iloc[:, [1, 2, 3, 0]]
    df.to_csv(f'NetworkFilesPierwszaSeria/Interakcje/interakcje_{group_name}.csv', index=False)

def correct_network_files(path_and_common_name: str) -> None:
    files = glob.glob(path_and_common_name)
    for file in tqdm(files, desc="Przetwarzanie plików sieci", unit="plik"):
        correct_network_file(file)

# correct_network_files("PierwszaSeriaDanych/test_file_*.csv")
