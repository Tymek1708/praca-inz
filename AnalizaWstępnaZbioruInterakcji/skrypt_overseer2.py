'''
13.01.2026
Skrypt powstał w celu ułatwienia tworzenia plików informacji dla grup

Niestety skrypt jest trochę ograniczony, więc trzeba go puszczać po kolei, odkomentarzowując po kolei każdą funkcję i odpalając odpowienio (jak w komentarzach)

'''
from utils_initial_data_analysis import *

## Uruchomienie: python3 skrypt_overseer2.py > PierwszaSeriaDanych/info_about_all_groups.txt
# info_about_groups(comments_file="PierwszaSeriaDanych/finalne_zmergowane_komentarze2_gotowe_do_tworzenia_sieci.json", posts_file="PierwszaSeriaDanych/finalne_zmergowane_posty2.json", all_groups=True)

## Uruchomienie: python3 skrypt_overseer2.py > PierwszaSeriaDanych/output_create_individual_files_for_all_groups.txt
# create_individual_files_for_all_groups("finalne_zmergowane_komentarze_gotowe_do_tworzenia_sieci.json", "finalne_zmergowane_posty.json")

## Uruchomienie: python3 skrypt_overseer2.py > PierwszaSeriaDanych/output_create_info_files_for_each_group.txt
# create_info_files_for_each_group("PierwszaSeriaDanych/PlikiDlaGrup/")

## Uruchomienie: python3 skrypt_overseer2.py > PierwszaSeriaDanych/output_create_hists_for_each_group.txt
create_hists_for_each_group("PierwszaSeriaDanych/PlikiDlaGrup/")