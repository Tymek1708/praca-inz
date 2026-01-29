from utils1 import *
import seaborn as sns
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
from statistics import median, mean
from pathlib import Path
import io
from contextlib import redirect_stdout
import numpy as np


'''
Moduł z funkcjami do wstępnej analizy danych
'''

# posts_file = "PierwszaSeriaDanych/finalne_posty_po_anonimizacji_pierwsza_seria_danych.json"

'''
Funkcja do tworzenia dwóch histogramów: Rozkład liczby postów w poszczególnych grupach oraz rozkład liczby postów na grupę
! dla wszystkich grup
'''
def create_hists1(posts_file: str) -> None:
    posts_list = open_json_file(posts_file)
    group_names_from_posts_list = [u['url'].split('/')[4] for u in posts_list]

    df = pd.DataFrame({'Grupa': group_names_from_posts_list})

    df_counts = df['Grupa'].value_counts()

    # ustawienie stylu
    sns.set_style("whitegrid")

    # figura z dwoma subplotami
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))


    ## Wykres 1
    # sns.histplot(data=df, x='Grupa', stat='count', discrete=True)
    sns.countplot(
        data=df,
        x="Grupa",
        order=df['Grupa'].value_counts().index,
        ax=axes[0]
    )

    axes[0].set_title("Liczba postów w poszczególnych grupach")
    axes[0].set_xlabel("Grupa")
    axes[0].set_ylabel("Liczba postów")
    axes[0].tick_params(axis='x', rotation=45)

    ## Wykres 2
    sns.histplot(
        df_counts, 
        bins='auto',
        ax=axes[1],
        kde=False
    )

    axes[1].set_title("Rozkład liczby postów na grupę")
    axes[1].set_xlabel("Liczba postów w grupie")
    axes[1].set_ylabel("Liczba grup")

    plt.tight_layout()
    plt.grid(alpha=0.7, linestyle='--', linewidth=0.5)
    plt.show()


'''
Funkcja do tworzenia histogramu: Rozkład liczby komentarzy na post (będzie używana dla x największych grup)
offset usuwa wartości odstające, czyli np. ogromą liczbę użytkowników z mała liczbą komentarzy
'''
def create_hists2(comments_file: str, offset: int | None = None, save_path: str | None = None) -> None:
    comments_list = open_json_file(comments_file)
    post_ids_from_comments_list = [u['post_id'] for u in comments_list]

    df = pd.DataFrame({'Post': post_ids_from_comments_list})


    df_counts = df['Post'].value_counts()
    if offset and isinstance(offset, int):
        df_counts = df_counts[df_counts >= offset]

    sns.set_style("whitegrid")

    sns.histplot(
        data=df_counts,
        bins='auto',
        kde=False
    )

    plt.title("Rozkład liczby komentarzy na post")
    plt.xlabel("Liczba komentarzy pod postem")
    plt.ylabel("Liczba postów")
    plt.tight_layout()
    plt.grid(alpha=0.7, linestyle='--', linewidth=0.5)
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


'''
Funkcja do tworzenia histogramu: Rozkład liczby komentarzy na grupę
! dla wszystkich grup
'''
def create_hists3(comments_file: str) -> None:
    comments_list = open_json_file(comments_file)
    group_names_from_comments_list = [u['url'].split('/')[4] for u in comments_list]

    df = pd.DataFrame({"Grupa": group_names_from_comments_list})

    df_counts = df['Grupa'].value_counts()
    
    sns.set_style("whitegrid")

    sns.histplot(
        data=df_counts,
        bins='auto',
        kde=False
    )

    plt.title("Rozkład liczby komentarzy na grupę")
    plt.xlabel("Liczba komentarzy w grupie")
    plt.ylabel("Liczba grup")
    plt.tight_layout()
    plt.grid(alpha=0.7, linestyle='--', linewidth=0.5)
    plt.show()


'''
Funkcja do tworzenia histogramu: Rozkład liczby komentarzy na użytkownika (aktywność użytkowników)
offset działa tak samo jak wyżej
'''
def create_hists4(comments_file: str, offset: int | None = None, save_path: str | None = None) -> None:
    comment_list = open_json_file(comments_file)
    user_names_from_comments_list = [u['user_name'] for u in comment_list]

    df = pd.DataFrame({"User": user_names_from_comments_list})

    df_counts = df['User'].value_counts()
    if offset and isinstance(offset, int):
        df_counts = df_counts[df_counts >= offset]

    sns.set_style("whitegrid")

    sns.histplot(
        data=df_counts,
        bins='auto',
        kde=False
    )

    plt.title("Rozkład liczby komentarzy na użytkownika")
    plt.xlabel("Liczba komentarzy użytkownika")
    plt.ylabel("Liczba użytkowników")
    plt.tight_layout()
    plt.grid(alpha=0.7, linestyle='--', linewidth=0.5)
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


'''
Liczba postów na postującego użytkownika
!! Tylko dla otwartych grup internetowych
'''
def create_hists5(posts_file: str, offset: int | None = None, save_path: str | None = None) -> None:
    posts_list = open_json_file(posts_file)
    user_names_from_posts_list = [u['user_username_raw'] for u in posts_list]

    df = pd.DataFrame({"User": user_names_from_posts_list})

    df_counts = df['User'].value_counts()
    if offset and isinstance(offset, int):
        df_counts = df_counts[df_counts >= offset]

    sns.set_style("whitegrid")

    sns.histplot(
        data=df_counts,
        bins='auto',
        kde=False
    )

    plt.title("Rozkład liczby postów na postującego użytkownika")
    plt.xlabel("Liczba postów postującego użytkownika")
    plt.ylabel("Liczba postujących użytkowników")
    plt.tight_layout()
    plt.grid(alpha=0.7, linestyle='--', linewidth=0.5)
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


'''
Skrypt do zapisania wykresów dla każdej z grup osobno
'''
def create_hists_for_each_group(path: str | None = "PierwszaSeriaDanych/PlikiDlaGrup/") -> None:
    # hist2, hist4, hist5
    print("Początek skryptu 'create_hists_for_each_group'.\n")
    root = Path(path)

    for subfolder in tqdm(list(root.iterdir()), desc="Tworzenie histogramów dla grup", unit="grupa"):

        if not subfolder.is_dir():
            continue

        print(f"Folder: {subfolder}")
        

        files = list(subfolder.iterdir())

        try:
            comments_file = next(f for f in files if "komentarze" in f.name)
            posts_file = next(f for f in files if "posty" in f.name)
        except StopIteration:
            print("Brak pliku komentarze dla folderu: ", subfolder)
            continue
        
        print("Comments file: ", comments_file)
        print("Posts file: ", posts_file)

        group_name = comments_file.stem.split("_")[-1]

        hist_file2 = subfolder / f"histogram_liczby_komentarzy_na_post_{group_name}"
        hist_file4 = subfolder / f"histogram_liczby_komentarzy_na_użytkownika_{group_name}"
        hist_file5 = subfolder / f"histogram_liczby_postów_na_postującego_użyt_{group_name}"
        activity_time_barplot = subfolder / f"barplot_liczby_postów_i_komentarzy_w_czasie_{group_name}"
        print(f"Zapisuję histogramy do: {hist_file2}, {hist_file4}, {hist_file5}, {activity_time_barplot}")

        # Histogram aktywności komentarzy i postów w czasie
        posts_and_comments_in_time_barplot(comments_file=str(comments_file), posts_file=str(posts_file), save_path=str(activity_time_barplot))

        # Zapis histogramów z różnymi offsetami
        for i in range(11):
            create_hists2(comments_file=str(comments_file), offset=i, save_path=str(hist_file2)+f"_offset={i}.png")
            create_hists4(comments_file=str(comments_file), offset=i, save_path=str(hist_file4)+f"_offset={i}.png")
            create_hists5(posts_file=str(posts_file), offset=i, save_path=str(hist_file5)+f"_offset={i}.png")

        print(f"Histogramy zapisane: {hist_file2}, {hist_file4}, {hist_file5}, {activity_time_barplot}\n")
    
    print("Zakończenie działania skryptu.")

# create_hists_for_each_group("PierwszaSeriaDanych/PlikiDlaGrup/")

'''
Funkcja do wypisania informacji o grupach: 
    Liczba wszystkich grup (dla all_groups = True)
    Liczba wszystkich postów
    Liczba wszystkich komentarzy
    Liczba unikalnych użytkowników komentujących
    Liczba unikalnych użytkowników postujących
    Liczba unikalnych użytkowników w sumie
    Liczba odpowiedzi
    Liczba użytkowników odpowiadających
    Liczba użytkowników aktywnych w więcej niż jednej grupie (dla all_groups = True)
    Mediana komentarzy na użytkownika
    Średnia liczba komentarzy na użytkownika
    Liczba użytkowników postujących w więcej niż jednej grupie (dla all_groups = True)
    Mediana postów na postującego
    Średnia liczba postów na postującego
'''
def info_about_groups(comments_file: str, posts_file: str, all_groups: bool | None = None) -> None:
    comments_list = open_json_file(comments_file)
    posts_list = open_json_file(posts_file)
    if all_groups:

        # Liczba wszystkich grup
        all_groups_set_from_comments = set(comment['url'].split("/")[4] for comment in comments_list)

        # Liczba użytkowników odpowiadających w więcej niż jednej grupie
        users = defaultdict(set)
        for comment in comments_list:
            users[comment['user_name']].add(comment['url'].split("/")[4])
        users_active_in_more_than_one_group = sum(len(groups) > 1 for groups in users.values())

        # Liczba użytkowników postujących w więcej niż jednej grupie
        posters = defaultdict(set)
        for post in posts_list:
            posters[post['user_username_raw']].add(post['url'].split("/")[4])
        posters_active_in_more_than_one_group = sum(len(groups) > 1 for groups in posters.values())
        print("==== Wstępna analiza dla wszystkich grup razem ====")

    # Liczba unikalnych użytkowników komentujących
    unique_commenters_set = set(comment['user_name'] for comment in comments_list)

    # Liczba unikalnych użytkowników postujących
    unique_posters_set = set(post['user_username_raw'] for post in posts_list)

    # Liczba unikalnych użytkowników w sumie
    unique_users = unique_commenters_set.union(unique_posters_set)

    # Liczba odpowiedzi
    replies_list = [comment for comment in comments_list if comment['reply']]

    # Liczba użytkowników odpowiadających
    responders_set = set(comment['user_name'] for comment in replies_list)  

    # Mediana komentarzy na użytkownika
    commenters_list = [comment["user_name"] for comment in comments_list]
    comments_per_commenter_counter = Counter(commenters_list)
    comments_per_commenter_counter_values = list(comments_per_commenter_counter.values())
    median_num_of_comments_per_commenter = median(sorted(comments_per_commenter_counter_values))

    # Średnia liczba komentarzy na użytkownika
    average_num_of_comments_per_commenter = mean(sorted(comments_per_commenter_counter_values))
    
    # Mediana postów na użytkownika postującego
    posters_list = [post['user_username_raw'] for post in posts_list]
    post_per_poster_counter = Counter(posters_list)
    post_per_poster_counter_values = list(post_per_poster_counter.values())
    median_num_of_posts_per_poster = median(sorted(post_per_poster_counter_values))
    # Średnia liczba postów na użytkownika postującego
    average_num_of_posts_per_poster = mean(sorted(post_per_poster_counter_values))
    if all_groups:
        print("Liczba wszystkich grup: ", len(all_groups_set_from_comments))
        print("Liczba użytkowników aktywnych w więcej niż jednej grupie: ", users_active_in_more_than_one_group)
        print("Liczba użytkowników postujących w więcej niż jednej grupie: ", posters_active_in_more_than_one_group)
    print("Liczba wszystkich postów: ", len(posts_list))
    print("Liczba wszystkich komentarzy: ", len(comments_list))
    print("Liczba unikalnych użytkowników komentujących: ", len(unique_commenters_set))
    print("Liczba unikalnych użytkowników postujących: ", len(unique_posters_set))
    print("Liczba unikalnych użytkowników w sumie: ", len(unique_users))
    print("Liczba odpowiedzi: ", len(replies_list))
    print("Liczba użytkowników odpowiadających: ", len(responders_set))
    print("Mediana komentarzy na użytkownika: ", median_num_of_comments_per_commenter)
    print("Średnia liczba komentarzy na użytkownika: ", average_num_of_comments_per_commenter)
    print("Mediana postów na użytkownika postującego: ", median_num_of_posts_per_poster)
    print("Średnia liczba postów na użytkownika postującego: ", average_num_of_posts_per_poster)


# info_about_groups(comments_file="PierwszaSeriaDanych/finalne_komentarze_gotowe_do_tworzenia_sieci_pierwsza_seria_danych.json", posts_file="PierwszaSeriaDanych/finalne_posty_po_anonimizacji_pierwsza_seria_danych.json", all_groups=True)
# info_about_groups(comments_file="PierwszaSeriaDanych/finalne_zmergowane_komentarze_gotowe_do_tworzenia_sieci.json", posts_file="PierwszaSeriaDanych/finalne_zmergowane_posty.json", all_groups=True)

'''
Funkcja do podzielenia jednego pliku z komentarzami/postami na wiele, dla każdej grupy
'''
def create_individual_files_for_all_groups(comments_file: str, posts_file: str) -> None:
    comments_list = open_json_file(comments_file)
    posts_list = open_json_file(posts_file)

    # Stworzenie indeksów
    group_id_dict_comments = {}
    group_id_dict_posts = {}
    group_id_group_name_dict = {}
    for comment in comments_list:
       group_id = comment['url'].split("/")[4]
       group_id_dict_comments.setdefault(group_id, []).append(comment)
    for post in posts_list:
        group_id = post['url'].split("/")[4]
        group_id_dict_posts.setdefault(group_id, []).append(post)
        group_id_group_name_dict[group_id] = post['group_name']

    # Tworzenie folderów i zapis plików
    const_path_prefix = "PierwszaSeriaDanych/PlikiDlaGrup/"
    for group in group_id_dict_comments:
        groupname_groupid = "{}_{}".format(group_id_group_name_dict[group], group)
        full_path = const_path_prefix + groupname_groupid + "/"
        create_dir(full_path)
        save_list_to_json_file(group_id_dict_comments[group], full_path + f"komentarze_{group}.json")
        save_list_to_json_file(group_id_dict_posts[group], full_path + f"posty_{group}.json")

# create_individual_files_for_all_groups("finalne_zmergowane_komentarze_gotowe_do_tworzenia_sieci.json", "finalne_zmergowane_posty.json")

'''
Skrypt do zapisania informacji o każdej z grup osobno po podaniu ścieżki folderu z folderami grup 
    Puszczane komendą: python3 utils_initial_data_analysis.py > PierwszaSeriaDanych/terminal_output_create_info_files_for_each_group.txt
'''
def create_info_files_for_each_group(path: str | None = "PierwszaSeriaDanych/PlikiDlaGrup/") -> None:
    root = Path(path)

    for subfolder in root.iterdir():

        if subfolder.is_dir():
            print(f"Folder: {subfolder}")
            files = []

            for file in subfolder.iterdir():
                print(f"file: {file}\n")
                files.append(str(file))
                
            comments_file = next(u for u in files if "komentarze" in u)
            posts_file = next(u for u in files if "posty" in u)
            print("comments file: ", comments_file)
            print("posts file: ", posts_file, "\n")
            group_name = comments_file.split("_")[-1]

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                info_about_groups(comments_file = comments_file, posts_file = posts_file, all_groups = False)

            output = buffer.getvalue()
            output_file = subfolder / f"info_about_group_{group_name}.txt"
            output_file.write_text(output, encoding = "utf-8")
            print(f"Plik 'info_about_group_{group_name}.txt' zapisano w katalogu {output_file}.\n\n")
    
# create_info_files_for_each_group("PierwszaSeriaDanych/PlikiDlaGrup/")

'''
Posty w czasie i komentarze w czasie
'''
def posts_and_comments_in_time_barplot(comments_file: str, posts_file: str, save_path: str | None = None) -> None:
    comments_list = open_json_file(comments_file)
    posts_list = open_json_file(posts_file)

    posts_dates_list = [u['date_posted'] for u in posts_list]
    comments_dates_list = [u['date_created'] for u in comments_list]

    posts_dates_df = pd.DataFrame({"Data": pd.to_datetime(posts_dates_list)})
    comments_dates_df = pd.DataFrame({"Data": pd.to_datetime(comments_dates_list)})

    # Usunięcie z dat: godziny, minuty i sekundy
    posts_dates_df["Data"] = posts_dates_df["Data"].dt.date
    comments_dates_df["Data"] = comments_dates_df["Data"].dt.date
    # Usunięcie powyższych + dnia
    # posts_dates_df["Data"] = posts_dates_df["Data"].dt.to_period('M').dt.to_timestamp()
    # comments_dates_df["Data"] = comments_dates_df["Data"].dt.to_period('M').dt.to_timestamp()


    posts_per_day = posts_dates_df.groupby("Data").size()
    comments_per_day = comments_dates_df.groupby("Data").size()

    
    df = pd.DataFrame({
        "Posty": posts_per_day,
        "Komentarze": comments_per_day
    }).fillna(0)

    # Reset indeksu, aby Data była zwykłą kolumną
    df = df.reset_index().rename(columns={"index": "Data"})


    # Zamiana do formatu long (wymagane przez seaborn)
    df_long = df.melt(
        id_vars="Data",
        value_vars=["Posty", "Komentarze"],
        var_name="Rodzaj",
        value_name="Liczba"
    )

    # print(df_long)
    # Styl seaborn
    sns.set_style("whitegrid")

    # --- WYKRES SŁUPKOWY ---
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df_long, x="Data", y="Liczba", hue="Rodzaj")

    plt.title("Aktywność użytkowników w czasie – wykres słupkowy")
    plt.xlabel("Data")
    plt.ylabel("Liczba")
    plt.xticks(rotation=45)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()