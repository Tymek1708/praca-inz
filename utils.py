'''
To lekko zmieniona kopia skryptu BD_FB_Scraper/utils.py
Zmiany: 
    - Trzeba podać nazwę pliku, do którego chcemy zapisać zaadresowane komentarze
    - Trzeba podać nazwę pliku, do którego chcemy zapisać zanonimizowane komentarze
    - Dodano funkcjonalność skryptu "BD_FB_Scraper/uzupelnij_adresatow.ipynb" do adresowania komentarzy oryginalnych
    - Dodano anonimizację postów 
'''
import json
import os
import time
from hashlib import sha256
from tqdm import tqdm
import re

# do poprawy - komentarze z grup

### Funkcje pomocnicze
def open_json_file(input_file):
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

def merge_json_files(input_files, output_file):
    merged_data = []

    for file_path in input_files:
        if not os.path.exists(file_path):
            print(f"Warning: File '{file_path}' does not exist, skipping.")
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data=json.load(file)

            if isinstance(data, dict):
                data = [data]
            elif not isinstance(data, list):
                print(f"Warning: File '{file_path}' does not contain a list or object, skipping.")
                continue

            merged_data.extend(data)
        
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in file '{file_path}', skipping.")

    with open(output_file, 'w', encoding='utf-8') as out:
        json.dump(merged_data, out, ensure_ascii=False, indent=4)

    print(f"Done! Merged {len(merged_data)} objects into '{output_file}'.")

### Dodawanie pola adresat i usuwanie wzmianki
## Rozwiązanie Perplexity
# Budujemy indeksy do szybkiego dostępu
def build_indices(comments_list):
    comment_id_dict = {}
    parent_comment_dict = {}
    post_id_dict={}
    group_id_dict={}
    for comment in comments_list:
        comment_id_dict[comment["comment_id"]] = comment
        pid = comment.get("parent_comment_id")
        if pid is not None:
            parent_comment_dict.setdefault(pid, []).append(comment)
        post_id = comment.get("post_id")
        if post_id is not None:
            post_id_dict.setdefault(post_id, []).append(comment)
        group_id = comment.get("url")
        if group_id is not None:
            group_id_dict.setdefault(group_id.split("/")[3], []).append(comment)
    return comment_id_dict, parent_comment_dict, post_id_dict, group_id_dict

def get_wzmianka(comment):
    comment_content = comment['comment_text']
    # comment_content = comment['comment_text'].replace(",", "").replace(".","").replace("!", "").replace("?","")
    comment_content = re.sub("[,.!?]", "", comment_content) #usuwanie wszystkich znaków, które mogą psuć wzmiankę
    name_and_surname = comment_content.split()[:2]
    if len(name_and_surname) == 0:
        return "", ""
    name = name_and_surname[0]
    wzmianka = " ".join(name_and_surname)
    return name, wzmianka
    
def mention_is_valid(comment, related_comments_list):
    name, wzmianka = get_wzmianka(comment)
    list_of_full_names = set(comment['user_name'] for comment in related_comments_list)
    list_of_special_names = set(" ".join(full_name.split()[:2]) for full_name in list_of_full_names)
    list_of_first_names = set(full_name.split()[0] for full_name in list_of_full_names)
    if wzmianka in list_of_full_names or wzmianka in list_of_special_names or name in list_of_first_names:
        return True
    return False

def find_full_username(wzmianka, related_comments_list):
    # Szukamy dokładnego dopasowania wzmianki do pełnego imienia i nazwiska
    for comment in related_comments_list:
        full_name = comment['user_name']
        if wzmianka == full_name or wzmianka == ' '.join(full_name.split()[:2]):
            return full_name
    for comment in related_comments_list:
        """
        to jest przywilej tego, że szukamy po tym samym parent_comment_id, 
        wtedy możemy założyć, że gdy ktoś używa tylko czyjegoś imienia, to nawiązuje do osoby, z którą prowadzi rozmowę
        
        tak samo, gdy szukamy po tym samym poście,
        ale gdy szukamy po grupie, to jest już gorzej, wtedy gdy nie mamy exact match, to nie szukamy następnie tylko po imieniu, bo na pewno znajdziemy kogoś
        i prawie na pewno nie będzie to odpowiednia osoba (wiele osób w grupie ma to samo imię)
        """
        if wzmianka.split()[0] == full_name.split()[0]:
            return full_name
    return None

def find_full_username_from_related_comments_by_group(wzmianka, related_comments_list_by_group):
    for comment in related_comments_list_by_group:
        full_name = comment['user_name']
        if wzmianka == full_name or wzmianka == ' '.join(full_name.split()[:2]):
            return full_name
    return None

def algorithm_optimized(comments_file: str, target_file: str) -> None:
    start = time.time()
    comments_list = open_json_file(comments_file)
    initial_num_of_comments = len(comments_list)

    # Budujemy indeksy
    comment_id_dict, parent_comment_dict, post_id_dict, group_id_dict = build_indices(comments_list)

    num_valid_wzmianka = 0
    num_invalid_wzmianka = 0
    num_reply = 0
    num_non_reply = 0
    num_no_comment_text = 0

    for comment in tqdm(comments_list, desc="Adresatowanie komentarzy", unit="komentarz"):
        pid = comment.get('parent_comment_id')
        parent_post_id = comment.get('post_id')
        if pid is not None:
            related_comments = parent_comment_dict.get(pid, [])
            related_comments_by_post = post_id_dict.get(parent_post_id, [])
            related_comments_by_group = group_id_dict.get(comment.get('url').split('/')[3], [])
            # Dodajemy również komentarz, do którego id jest równy parent_comment_id
            parent_comment = comment_id_dict.get(pid)
            if parent_comment:
                related_comments = related_comments + [parent_comment]
            num_reply += 1

            if "comment_text" in comment:
                if mention_is_valid(comment, related_comments):
                    name, wzmianka = get_wzmianka(comment)
                    adresat_full_name = find_full_username(wzmianka, related_comments)
                    if adresat_full_name:
                        comment["adresat"] = adresat_full_name
                    else:
                        comment["adresat"] = wzmianka
                    # Usuwamy tylko pierwsze wystąpienie wzmianki na początku tekstu
                    comment['comment_text'] = comment['comment_text'][len(wzmianka):].lstrip()
                    num_valid_wzmianka += 1
                elif mention_is_valid(comment, related_comments_by_post): # wariant, kiedy sprawdzamy wszystkich użytkowników spod tego samego posta
                    name, wzmianka = get_wzmianka(comment)
                    adresat_full_name = find_full_username(wzmianka, related_comments_by_post)
                    if adresat_full_name:
                        comment["adresat"] = adresat_full_name
                    else:
                        comment["adresat"] = wzmianka
                    # Usuwamy tylko pierwsze wystąpienie wzmianki na początku tekstu
                    comment['comment_text'] = comment['comment_text'][len(wzmianka):].lstrip()
                    num_valid_wzmianka += 1
                elif mention_is_valid(comment, related_comments_by_group): # wariant, kiedy sprawdzamy wszsystkich użytkowników pochodzących z tej samej grupy
                    name, wzmianka = get_wzmianka(comment)
                    adresat_full_name = find_full_username_from_related_comments_by_group(wzmianka, related_comments_by_group)
                    if adresat_full_name:
                        comment["adresat"] = adresat_full_name
                    else:
                        comment["adresat"] = wzmianka
                    # Usuwamy tylko pierwsze wystąpienie wzmianki na początku tekstu
                    comment['comment_text'] = comment['comment_text'][len(wzmianka):].lstrip()
                    num_valid_wzmianka += 1
                else:
                    num_invalid_wzmianka += 1
            else:
                num_no_comment_text += 1
        else:
            num_non_reply += 1

    print("Czas działania: ", time.time() - start)
    print("Liczba komentarzy na wejściu: ", initial_num_of_comments)
    print("Liczba komentarzy bez tekstu: ", num_no_comment_text)
    print("Liczba odpowiedzi: ", num_reply)
    print("Liczba oryginalnych komentarzy: ", num_non_reply)
    print(f"Liczba valid wzmianek: {num_valid_wzmianka} (z {num_reply} odpowiedzi)")
    print(f"Liczba invalid wzmianek: {num_invalid_wzmianka} (z {num_reply} odpowiedzi)")
    save_list_to_json_file(comments_list, target_file=target_file)
    # save_list_to_json_file(comments_list, 'komentarze_dodane_pole_adresat_usuniete_wzmianki_pierwsza_seria_danych.json')


### Uzupełnianie pola adresat komentarzom oryginalnym
num_of_changes=0
# Funkcja pomocnicza do zbudowania indeksów z urlów postów w postaci:  url : autor
def build_indices2(posts_list: list) -> dict:
    post_id_dict = {}
    for post in posts_list:
        url = post.get("url").replace("https://web", "https://www")
        post_id_dict[url] = post['user_username_raw']
    return post_id_dict

# Funkcja pomocnicza do uzupełnienia pola adresat
def uzupelnij_adresat_field(comment, post_id_dict: dict):
    global num_of_changes
    if not comment['reply'] or (comment['reply'] and 'adresat' not in comment):
        comment['adresat'] = post_id_dict.get(comment['input']['url'].replace("https://web", "https://www"))
        num_of_changes+=1
    return comment

# Funkcja uzupełniająca pola adresat
def algorytm_uzupelniajacy_pola_adresat(comments_list: list, posts_list: list, target_file: str) -> None:
    start = time.time()
    global num_of_changes
    num_of_changes=0
    post_id_dict = build_indices2(posts_list)
    comments_replies_with_no_adresat = [u for u in comments_list if u["parent_comment_id"] is not None and "adresat" not in u]
    comments_list_with_uzupelnione_adresat_fields = [
        uzupelnij_adresat_field(comment, post_id_dict)
        for comment in tqdm(comments_list, desc="Uzupełnianie pola adresat w komentarzach", unit="komentarz")
    ]
    print("Liczba komentarzy-odpowiedzi z rodziami, ale bez pola adresat: ", len(comments_replies_with_no_adresat))
    print("Liczba komentarzy-nie-odpowiedzi, bez pola adresat (wszystkie z nich nie mają pola adresat): ", len([u for u in comments_list if not u['reply']]))
    print("Liczba zmienionych elementów: ", num_of_changes)
    print("Czas działania: ", time.time()-start, "sekund.")
    save_list_to_json_file(comments_list_with_uzupelnione_adresat_fields, target_file=target_file)
    # save_list_to_json_file(comments_list_with_uzupelnione_adresat_fields, "finalne_komentarze_gotowe_do_tworzenia_sieci_pierwsza_seria_danych.json")


### Anonimizacja komentarzy
## Funkcje pomocnicze do anonimizacji komentarzy
def anonimizuj_komentarz(comment):
    comment['user_name'] = sha256(comment['user_name'].encode('utf-8')).hexdigest()
    comment['user_id'] = sha256(comment['user_id'].encode('utf-8')).hexdigest()
    if 'user_url' in comment:
        del comment['user_url']
    if comment['commentator_profile'] != None:
        comment['commentator_profile'] = sha256(comment['commentator_profile'].encode('utf-8')).hexdigest()
    comment['comment_link'] = sha256(comment['comment_link'].encode('utf-8')).hexdigest()
    if "adresat" in comment:
        comment['adresat'] = sha256(comment['adresat'].encode('utf-8')).hexdigest()
    return comment # dla wariantu funkcyjnego map, bez pętli for / usuń dla wariantu z pętlą for

## Funkcja do anonimizacji komentarzy
def algorytm_anonimizujacy_komentarze(comments_file: str, target_file: str) -> None:
    start = time.time()
    comments_list = open_json_file(comments_file)
    # anonymized_comments_list = list(map(anonimizuj_komentarz, comments_list))
    anonymized_comments_list = [
        anonimizuj_komentarz(comment)
        for comment in tqdm(comments_list, desc="Anonimizacja komentarzy", unit="komentarz")
    ]
    print("Czas działania: ", time.time()-start, " sekund.")
    # return anonymized_comments_list
    save_list_to_json_file(anonymized_comments_list, target_file=target_file)
    # save_list_to_json_file(anonymized_comments_list, 'finalne_komentarze_po_dodaniu_pola_adresat_usunieciu_wzmianek_i_anonimizacji.json')

## Anonimizacja postów
def anonimizuj_post(post: dict) -> dict:
    if "user_url" in post:
        post['user_url'] = sha256(post['user_url'].encode('utf-8')).hexdigest()
    if post["user_username_raw"] != None:
        post['user_username_raw'] = sha256(post['user_username_raw'].encode('utf-8')).hexdigest()
    del post['user_is_verified']
    del post['avatar_image_url']
    if post['profile_id'] != None:
        post['profile_id'] = sha256(post['profile_id'].encode('utf-8')).hexdigest()
    del post['publisher_image_url']
    return post # dla wariantu funkcyjnego map, bez pętli for / usuń dla wariantu z pętlą for

def algorytm_anonimizujacy_posty(posts_file: str) -> list:
    start = time.time()
    posts_list = open_json_file(posts_file)
    anonymized_posts_list = list(map(anonimizuj_post, posts_list))
    print("Czas działania: ", time.time()-start, " sekund.")
    return anonymized_posts_list