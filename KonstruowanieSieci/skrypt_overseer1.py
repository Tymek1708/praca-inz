'''
13.01.2026
Skrypt powstał w celu ułatwienia tworzenia plików interakcji dla grup
Po uruchomieniu skryptu, w NDPS/Interakcje/ pojawią się odpowiednie pliki interakcji, ale bez folderów, więc trzeba następnie puścić w tamtej lokalizacji skrypt przenies_interakcje.py
Należy również usunąć na koniec wszystkie potworzone pliki test_file_*.csv, dla czystości 

Następnie można przejść do skrypt_overseer2.py
'''
from utils1 import *
import time

## Tworzy pliki interakcji dla każdej grupy oddzielnie
create_network_file_per_group("finalne_zmergowane_komentarze2_gotowe_do_tworzenia_sieci.json")

print("zasypianie na 5 sekund")
time.sleep(5)
print("Koniec snu")

## Poprawia pliki interakcji i przenosi je do NDPS/Interakcje/
correct_network_files("test_file_*.csv")

