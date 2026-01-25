'''
To kopia skryptu BD_FB_Scraper/skrypt_overseer.py zmieniona na potrzeby dobrania danych
Skrypt służy do adresatowania komentarzy oraz późniejszej anonimizacji ich oraz postów
'''

from utils import *

# do poprawy - komentarze z grup

comments_file = 'ostateczne_dobrane_komentarze2_bez_duplikatow.json'
first_target_file = 'ostateczne_dobrane_komentarze2_dodane_pole_adresat_usuniete_wzmianki.json'
# adresated_comments_file = "DobranieDanych1-styczeń/ostateczne_dobrane_komentarze_zaadresowane_gotowe_do_anonimizacji.json"

posts_file = "ostateczne_dobrane_posty2_z_komentarzami_noShares_gotowe_do_anonimizacji_naprawione_null_authors.json"
second_target_file = "ostateczne_dobrane_komentarze2_zaadresowane_gotowe_do_anonimizacji.json"

final_target_file = "finalne_dobrane_komentarze2_po_anonimizacji.json"

def prepare_comment_files(comments_file):
    # Adresowanie odpowiedzi
    if os.path.exists(comments_file):
        print("Rozpoczynam adresatowanie komentarzy.")
        algorithm_optimized(comments_file, first_target_file)
        print("Adresatowanie komentarzy zostało zakończone. Zasypianie na 5 sekund.")
        time.sleep(5)
        print("Koniec snu.")

    # Adresowanie oryginalnych komentarzy
    if os.path.exists(first_target_file) and os.path.exists(posts_file):
        print("Rozpoczynam uzupełnianie adresatów komentarzy oryginalnych.")
        comments_list = open_json_file(first_target_file)
        posts_list = open_json_file(posts_file)
        algorytm_uzupelniajacy_pola_adresat(comments_list, posts_list, second_target_file)
        print("Adresatowanie komentarzy zostało zakończone. Zasypianie na 5 sekund.")
        time.sleep(5)
        print("Koniec snu.")

    # Anonimizacja komentarzy
    if os.path.exists(second_target_file):
        print("Rozpoczynam anonimizowanie komentarzy.")
        algorytm_anonimizujacy_komentarze(second_target_file, final_target_file)
        print("Anonimizowanie komentarzy zostało zakończone.")
        print("Koniec skryptu.")

prepare_comment_files(comments_file)

anonymized_posts = algorytm_anonimizujacy_posty(posts_file)
save_list_to_json_file(anonymized_posts, "finalne_dobrane_posty2_po_anonimizacji.json")