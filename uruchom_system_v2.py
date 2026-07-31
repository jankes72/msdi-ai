#!/usr/bin/env python3
"""
PAMIĘĆ MODELI V2 - GŁÓWNY SKRYPT URUCHOMIENIOWY
==================================================

Skrypt CLI do uruchamiania Systemu Pamięci Modeli V2.

OPIS:
System Pamięci Modeli V2 to nadwarstwa nad istniejącym systemem SSI,
która dodaje:
- Model Level 1: Agregacja predykcji z 15 sieci SSI
- Model Level 2: Kalibrator uczący się zachowania Level 1
- Centralne repozytorium pamięci z wersjonowaniem

UŻYCIE:
    # Generuj predykcję dla pojedynczego meczu
    python uruchom_system_v2.py --mecz "Team A - Team B" --dane database_dzisiaj.csv

    # Generuj predykcje dla wielu meczów (batch)
    python uruchom_system_v2.py --batch database_dzisiaj.csv --wyjscie predykcje.csv

    # Trenuj kalibrator
    python uruchom_system_v2.py --trenuj

    # Monitoruj i ucz się na nowych meczach
    python uruchom_system_v2.py --monitor --dane database_dzisiaj.csv

    # Pełna analiza (predykcja + zapisz obserwacje + trenuj + wersjonuj)
    python uruchom_system_v2.py --pelny-cykl --dane database_dzisiaj.csv --wyniki wyniki.csv

    # Pokaz statystyki
    python uruchom_system_v2.py --statystyki

    # Pokaz wzorce zachowania
    python uruchom_system_v2.py --wzorce

    # Lista wersji pamięci
    python uruchom_system_v2.py --wersje

    # Załaduj konkretną wersję pamięci
    python uruchom_system_v2.py --zaladuj-wersje pamiec_v2_20260727_120000.json

ZASADY:
- Nie modyfikujemy istniejących plików SSI
- Każde uruchomienie tworzy nową wersję pamięci (nie nadpisujemy!)
- Podział danych: 50% trening, 10% walidacja, 40% obserwacja

Autor: MSDI AI v0.02
Data: 2026-07-27
"""

import argparse
import sys
import json
import csv
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import traceback

# Dodaj ścieżkę do pamiec_modeli_v2 do PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

# Import z modułów V2
from pamiec_modeli_v2.integration import (
    SystemPamieciV2,
    utworz_system,
    utworz_system_bez_inicjalizacji,
)
from pamiec_modeli_v2.schemas import waliduj_wynik, normalizuj_wynik
from pamiec_modeli_v2.pamiec.repozytorium import PamiecRepozytorium


# =============================================================================
# KONFIGURACJA DOMYŚLNA
# =============================================================================

DEFAULT_DANE_PATH = "dane/database_dzisiaj.csv"
DEFAULT_WYNIKI_PATH = "dane/wyniki_rzeczywiste.csv"
DEFAULT_OUTPUT_PATH = "dane/predykcje_v2.csv"
DEFAULT_ARCHIWUM_PATH = "pamiec_modeli_v2/archiwum"


# =============================================================================
# FUNKCJE POMOCNICZE
# =============================================================================

def czytaj_plik_csv(sciezka: str, delimiter: str = ";") -> List[Dict[str, Any]]:
    """Czyta plik CSV i zwraca listę słowników"""
    try:
        with open(sciezka, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            return list(reader)
    except Exception as e:
        print(f"Błąd odczytu pliku {sciezka}: {e}")
        return []


def czytaj_plik_wyniki(sciezka: str) -> Dict[str, str]:
    """Czyta plik z wynikami (mecz;wynik) i zwraca słownik {mecz: wynik}"""
    wyniki = {}
    try:
        with open(sciezka, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                mecz = row.get('mecz', row.get('id_meczu', ''))
                wynik = row.get('wynik', '')
                if mecz and wynik:
                    wyniki[mecz] = wynik
    except Exception as e:
        print(f"Błąd odczytu pliku wyników {sciezka}: {e}")
    return wyniki


def zapisz_predykcje_do_csv(predykcje: List[Dict[str, Any]], sciezka: str):
    """Zapisuje predykcje do pliku CSV"""
    try:
        if not predykcje:
            print("Brak predykcji do zapisania.")
            return
        
        # Określ nagłówki
        naglowki = [
            "id_meczu", "id_grupy", "wynik_predykcji", "confidence",
            "confidence_kalibrowana", "poprawka_kalibracji", "model",
            "timestamp", "trafienie", "wynik_rzeczywisty"
        ]
        
        with open(sciezka, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=naglowki, delimiter=';')
            writer.writeheader()
            
            for pred in predykcje:
                row = {
                    "id_meczu": pred.get('id_meczu', ''),
                    "id_grupy": pred.get('id_grupy', ''),
                    "wynik_predykcji": pred.get('wynik_predykcji', ''),
                    "confidence": pred.get('confidence', 0),
                    "confidence_kalibrowana": pred.get('confidence_kalibrowana', 0),
                    "poprawka_kalibracji": pred.get('poprawka_kalibracji', 0),
                    "model": pred.get('id_modelu', ''),
                    "timestamp": pred.get('timestamp', ''),
                    "trafienie": '',
                    "wynik_rzeczywisty": '',
                }
                writer.writerow(row)
        
        print(f"Predykcje zapisane do {sciezka}")
        
    except Exception as e:
        print(f"Błąd zapisu predykcji: {e}")


def wczytaj_dane_meczu(sciezka: str) -> List[Dict[str, Any]]:
    """Wczytuje dane meczów z pliku CSV"""
    dane = czytaj_plik_csv(sciezka)
    
    # Normalizuj klucze (zamień mecz -> id_meczu, itd.)
    for mecz in dane:
        if 'mecz' in mecz and 'id_meczu' not in mecz:
            mecz['id_meczu'] = mecz.pop('mecz')
        if 'grupa' in mecz and 'id_grupy' not in mecz:
            mecz['id_grupy'] = mecz.pop('grupa')
    
    return dane


def pobierz_aktualna_date() -> str:
    """Zwraca aktualną datę w formacie YYYY-MM-DD"""
    return datetime.now().strftime("%Y-%m-%d")


def pobierz_aktualny_czas() -> str:
    """Zwraca aktualny czas w formacie HH:MM:SS"""
    return datetime.now().strftime("%H:%M:%S")


# =============================================================================
# FUNKCJE GŁÓWNE (KOMENDY CLI)
# =============================================================================

def komenda_predykcja(args):
    """Generuje predykcję dla pojedynczego meczu"""
    print(f"\n[{pobierz_aktualny_czas()}] Generowanie predykcji...")
    
    # Wczytaj dane meczu
    if args.dane:
        mecze = wczytaj_dane_meczu(args.dane)
        # Znajdź mecz o podanej nazwie
        mecz_data = None
        for m in mecze:
            if m.get('id_meczu') == args.mecz:
                mecz_data = m
                break
        
        if mecz_data is None:
            print(f"Nie znaleziono meczu: {args.mecz}")
            return
    else:
        # Utwórz puste dane (użyj argumentów)
        mecz_data = {
            'id_meczu': args.mecz,
            'id_grupy': args.grupa if args.grupa else 'BRAK',
        }
    
    # Inicjalizuj system
    system = utworz_system()
    
    # Generuj predykcję
    pred_l1 = system.generuj_predykcje(mecz_data, args.mecz, mecz_data.get('id_grupy', 'BRAK'))
    
    if pred_l1 is None:
        print("Błąd generowania predykcji Level 1")
        return
    
    print(f"\nPredykcja Level 1:")
    print(f"  Mecz: {pred_l1.id_meczu}")
    print(f"  Wynik: {pred_l1.wynik_predykcji}")
    print(f"  Confidence: {pred_l1.confidence:.4f}")
    print(f"  Model: {pred_l1.id_modelu}")
    
    # Generuj kalibrowaną predykcję
    pred_kal = system.generuj_predykcje_kalibrowana(mecz_data, args.mecz, mecz_data.get('id_grupy', 'BRAK'))
    
    if pred_kal:
        print(f"\nPredykcja Level 2 (Kalibrowana):")
        print(f"  Wynik: {pred_kal.wynik_predykcji}")
        print(f"  Oryginalne confidence: {pred_kal.confidence:.4f}")
        print(f"  Kalibrowane confidence: {pred_kal.confidence_kalibrowana:.4f}")
        print(f"  Poprawka: {pred_kal.poprawka_kalibracji:+.4f}")
    
    # Jeśli podano wynik rzeczywisty, zapisz obserwację
    if args.wynik:
        obs = system.zapisz_obserwacje(
            mecz_id=args.mecz,
            wynik_rzeczywisty=args.wynik,
            id_modelu=pred_l1.id_modelu,
            id_grupy=pred_l1.id_grupy,
            confidence=pred_l1.confidence,
            wynik_predykcji=pred_l1.wynik_predykcji,
        )
        
        if obs:
            print(f"\nObserwacja zapisana:")
            print(f"  Trafienie: {obs.trafienie}")
            print(f"  Trafienie grupa: {obs.trafienie_grupa}")
            
            # Auto-trenuj kalibrator
            system.trenuj_kalibrator_auto()
            
            # Zapisz wersję pamięci
            if not args.no_save:
                system.zapisz_wersje_pamieci()
    
    print(f"\n[{pobierz_aktualny_czas()}] Zakończono.")


def komenda_batch(args):
    """Generuje predykcje dla wielu meczów (batch)"""
    print(f"\n[{pobierz_aktualny_czas()}] Generowanie predykcji batch...")
    
    # Wczytaj dane
    mecze = wczytaj_dane_meczu(args.dane)
    
    if not mecze:
        print(f"Brak danych w pliku: {args.dane}")
        return
    
    print(f"Wczytano {len(mecze)} meczów z {args.dane}")
    
    # Inicjalizuj system
    system = utworz_system()
    
    # Wczytaj wyniki rzeczywiste (jeśli podano)
    wyniki_rzeczywiste = {}
    if args.wyniki:
        wyniki_rzeczywiste = czytaj_plik_wyniki(args.wyniki)
        print(f"Wczytano {len(wyniki_rzeczywiste)} wyników rzeczywistych z {args.wyniki}")
    
    # Generuj predykcje batch
    if args.kalibrowane:
        predykcje = system.generuj_predykcje_kalibrowana_batch(mecze)
    else:
        predykcje_l1 = system.generuj_predykcje_batch(mecze)
        predykcje = [p.to_dict() for p in predykcje_l1]
    
    print(f"Wygenerowano {len(predykcje)} predykcji")
    
    # Jeśli podano wyniki, zapisz obserwacje
    if wyniki_rzeczywiste:
        for mecz_data in mecze:
            mecz_id = mecz_data.get('id_meczu', '')
            if mecz_id in wyniki_rzeczywiste:
                # Znajdź predykcję
                for pred in predykcje:
                    if pred.get('id_meczu') == mecz_id:
                        system.zapisz_obserwacje(
                            mecz_id=mecz_id,
                            wynik_rzeczywisty=wyniki_rzeczywiste[mecz_id],
                            id_modelu=pred.get('id_modelu', 'AGGREGATOR'),
                            id_grupy=pred.get('id_grupy', 'BRAK'),
                            confidence=pred.get('confidence', 0.5),
                            wynik_predykcji=pred.get('wynik_predykcji', '1:0'),
                        )
                        break
        
        # Trenuj kalibrator
        system.trenuj_kalibrator_auto()
        
        # Zapisz wersję pamięci
        if not args.no_save:
            system.zapisz_wersje_pamieci()
    
    # Zapisz predykcje do CSV (jeśli podano wyjście)
    if args.wyjscie:
        zapisz_predykcje_do_csv(predykcje, args.wyjscie)
    else:
        # Wyświetl wyniki
        print("\nWyniki:")
        for pred in predykcje[:10]:  # Pokaż pierwsze 10
            print(f"  {pred.get('id_meczu', 'N/A')}: {pred.get('wynik_predykcji', 'N/A')} "
                  f"(confidence: {pred.get('confidence', 0):.4f})")
        if len(predykcje) > 10:
            print(f"  ... i {len(predykcje) - 10} więcej")
    
    print(f"\n[{pobierz_aktualny_czas()}] Zakończono.")


def komenda_trenuj(args):
    """Trenuje kalibrator Level 2"""
    print(f"\n[{pobierz_aktualny_czas()}] Trenowanie kalibratora...")
    
    # Inicjalizuj system
    system = utworz_system()
    
    # Trenuj kalibrator
    success = system.trenuj_kalibrator(min_obserwacji=args.min_obs)
    
    if success:
        print("\nKalibrator wytrenowany pomyślnie!")
        print(f"  Metoda: {system.kalibrator.config.METODA_KALIBRACJI}")
        print(f"  Liczba obserwacji: {len(system.repozytorium.obserwacje)}")
        print(f"  Wzorce: {len(system.kalibrator.wzorce)}")
        
        # Zapisz model kalibratora
        kalibrator_path = system.kalibrator.zapisz_model()
        print(f"  Model kalibratora: {kalibrator_path}")
    else:
        print("\nBłąd trenowania kalibratora.")
        print(f"  Wymagane: {args.min_obs} obserwacji")
        print(f"  Dostępne: {len(system.repozytorium.obserwacje)} obserwacji")
    
    print(f"\n[{pobierz_aktualny_czas()}] Zakończono.")


def komenda_monitor(args):
    """Monitoruje plik danych i automatycznie przetwarza nowe mecze"""
    print(f"\n[{pobierz_aktualny_czas()}] Uruchamiam tryb monitorowania...")
    print(f"Plik danych: {args.dane}")
    print(f"Interwał: {args.interwal} sekund")
    
    # Inicjalizuj system
    system = utworz_system()
    
    # Śledź przetworzone mecze
    przetworzone_mecze = set()
    
    try:
        while True:
            # Wczytaj dane
            mecze = wczytaj_dane_meczu(args.dane)
            
            # Znajdź nowe mecze
            nowe_mecze = []
            for mecz in mecze:
                mecz_id = mecz.get('id_meczu', '')
                if mecz_id and mecz_id not in przetworzone_mecze:
                    nowe_mecze.append(mecz)
                    przetworzone_mecze.add(mecz_id)
            
            if nowe_mecze:
                print(f"\n[{pobierz_aktualny_czas()}] Znaleziono {len(nowe_mecze)} nowych meczów")
                
                # Generuj predykcje
                predykcje = system.generuj_predykcje_batch(nowe_mecze)
                
                print(f"Wygenerowano {len(predykcje)} predykcji:")
                for pred in predykcje:
                    print(f"  {pred.id_meczu}: {pred.wynik_predykcji} ({pred.confidence:.4f})")
                
                # Zapisz predykcje do CSV
                if args.wyjscie:
                    zapisz_predykcje_do_csv([p.to_dict() for p in predykcje], args.wyjscie)
            else:
                print(f"[{pobierz_aktualny_czas()}] Brak nowych meczów")
            
            # Czekaj na następny interwał
            time.sleep(args.interwal)
            
    except KeyboardInterrupt:
        print(f"\n[{pobierz_aktualny_czas()}] Monitorowanie zatrzymane.")


def komenda_pelny_cykl(args):
    """Wykonuje pełny cykl: predykcja + obserwacja + trenowanie + wersjonowanie"""
    print(f"\n[{pobierz_aktualny_czas()}] Pełny cykl systemu...")
    
    # Inicjalizuj system
    system = utworz_system()
    
    # Wczytaj dane
    mecze = wczytaj_dane_meczu(args.dane)
    
    if not mecze:
        print(f"Brak danych w pliku: {args.dane}")
        return
    
    print(f"Wczytano {len(mecze)} meczów")
    
    # Wczytaj wyniki rzeczywiste
    wyniki_rzeczywiste = {}
    if args.wyniki:
        wyniki_rzeczywiste = czytaj_plik_wyniki(args.wyniki)
        print(f"Wczytano {len(wyniki_rzeczywiste)} wyników rzeczywistych")
    
    # Wykonaj pełny cykl batch
    wyniki = system.pelny_cykl_batch(mecze, wyniki_rzeczywiste)
    
    print(f"\nPrzetworzono {len(wyniki)} meczów:")
    trafienia = 0
    trafienia_grupa = 0
    
    for wynik in wyniki:
        level1 = wynik.get('level1', {})
        level2 = wynik.get('level2', {})
        obs = wynik.get('obserwacja', {})
        
        if obs.get('trafienie'):
            trafienia += 1
        if obs.get('trafienie_grupa'):
            trafienia_grupa += 1
        
        print(f"  {wynik['mecz_id']}: "
              f"L1={level1.get('wynik_predykcji', 'N/A')}, "
              f"L2_conf={level2.get('confidence_kalibrowana', 0):.3f}, "
              f"trafienie={obs.get('trafienie', 'N/A')}, "
              f"trafienie_grupa={obs.get('trafienie_grupa', 'N/A')}")
    
    # Statystyki
    print(f"\nStatystyki:")
    print(f"  Trafienia dokładne: {trafienia}/{len(wyniki)} ({trafienia/len(wyniki)*100:.1f}%)")
    print(f"  Trafienia grupowe: {trafienia_grupa}/{len(wyniki)} ({trafienia_grupa/len(wyniki)*100:.1f}%)")
    
    # Zapisz wersję pamięci
    if not args.no_save:
        wersja_path = system.zapisz_wersje_pamieci()
        print(f"\nWersja pamięci zapisana: {wersja_path}")
    
    print(f"\n[{pobierz_aktualny_czas()}] Zakończono.")


def komenda_statystyki(args):
    """Pokazuje statystyki systemu"""
    print(f"\n[{pobierz_aktualny_czas()}] Statystyki systemu...")
    
    # Inicjalizuj system
    system = utworz_system()
    
    # Pobierz statystyki
    statystyki = system.pobierz_statystyki_systemu()
    
    print("\n" + "=" * 60)
    print("STATYSTYKI SYSTEMU PAMIĘCI MODELI V2")
    print("=" * 60)
    
    # System
    print("\n[SYSTEM]")
    print(f"  Wersja: {statystyki.get('system', {}).get('wersja', 'N/A')}")
    print(f"  Data utworzenia: {statystyki.get('system', {}).get('data_utworzenia', 'N/A')}")
    print(f"  Zainicjalizowany: {statystyki.get('system', {}).get('zainicjalizowany', False)}")
    
    # Pamięć
    pamiec = statystyki.get('pamiec', {})
    print("\n[PAMIĘĆ]")
    print(f"  Obserwacje: {pamiec.get('obserwacje', 0)}")
    print(f"  Klasy: {pamiec.get('klasy', 0)}")
    print(f"  Modele: {pamiec.get('modele', 0)}")
    print(f"  Skuteczność: {pamiec.get('skutecznosc', 0):.4f}")
    print(f"  Średni confidence: {pamiec.get('sredni_confidence', 0):.4f}")
    
    # Level 1
    level1 = statystyki.get('level1', {})
    print("\n[LEVEL 1 - AGREGATOR]")
    print(f"  Strategia: {level1.get('strategia', 'N/A')}")
    print(f"  Liczba sieci: {level1.get('liczba_sieci', 0)}")
    if level1.get('ostatnia_predykcja'):
        ostatnia = level1['ostatnia_predykcja']
        print(f"  Ostatnia predykcja: {ostatnia.get('mecz', 'N/A')} -> {ostatnia.get('wynik', 'N/A')} "
              f"(confidence: {ostatnia.get('confidence', 0):.4f})")
    
    # Level 2
    level2 = statystyki.get('level2', {})
    print("\n[LEVEL 2 - KALIBRATOR]")
    print(f"  Metoda: {level2.get('metoda', 'N/A')}")
    print(f"  ML dostępny: {level2.get('ml_dostepny', False)}")
    print(f"  Wytrenowany: {level2.get('wytrenowany', False)}")
    print(f"  Wzorce: {level2.get('wzorce', 0)}")
    
    # Statystyki kalibratora
    kalibrator_stats = level2.get('statystyki', {})
    if kalibrator_stats:
        print(f"\n  Statystyki kalibracji:")
        print(f"    Obserwacje: {kalibrator_stats.get('calkowita_liczba_obserwacji', 0)}")
        print(f"    Trafienia: {kalibrator_stats.get('trafienia', 0)}")
        print(f"    Skuteczność: {kalibrator_stats.get('skutecznosc', 0):.4f}")
    
    # Repozytorium - top klasy
    if system.repozytorium:
        print("\n[TOP KLASY (SKUTECZNOŚĆ)]")
        for klasa, skutecznosc in system.repozytorium.pobierz_top_klasy(10):
            print(f"  {klasa}: {skutecznosc:.4f}")
        
        print("\n[TOP MODELE (SKUTECZNOŚĆ)]")
        for model, skutecznosc in system.repozytorium.pobierz_top_modele(10):
            print(f"  {model}: {skutecznosc:.4f}")
    
    # Wersje pamięci
    wersje = system.lista_wersji_pamieci()
    print(f"\n[WERSJE PAMIĘCI]")
    print(f"  Dostępne wersje: {len(wersje)}")
    for wersja in wersje[:5]:
        print(f"  - {wersja.name}")
    if len(wersje) > 5:
        print(f"  ... i {len(wersje) - 5} więcej")
    
    print("\n" + "=" * 60)
    print(f"[{pobierz_aktualny_czas()}] Zakończono.")


def komenda_wzorce(args):
    """Pokazuje wykryte wzorce zachowania"""
    print(f"\n[{pobierz_aktualny_czas()}] Wzorce zachowania...")
    
    # Inicjalizuj system
    system = utworz_system()
    
    # Pobierz wzorce
    wzorce = system.pobierz_wzorce()
    
    print("\n" + "=" * 60)
    print("WYKRYTE WZORCE ZACHOWANIA LEVEL 1")
    print("=" * 60)
    
    if not wzorce:
        print("\nBrak wykrytych wzorców. Trenuj kalibrator z więcej danymi.")
    else:
        print(f"\nLiczba wzorców: {len(wzorce)}")
        print("\n[WZORCE]")
        
        # Grupuj wzorce po typie
        wzorce_po_typie = {}
        for wzor in wzorce:
            typ = wzor.cechy_charakterystyczne.get('typ', 'inny')
            if typ not in wzorce_po_typie:
                wzorce_po_typie[typ] = []
            wzorce_po_typie[typ].append(wzor)
        
        for typ, wzorce_typu in wzorce_po_typie.items():
            print(f"\n  [{typ.upper()}]")
            for wzor in wzorce_typu:
                print(f"    - {wzor.nazwa}")
                print(f"      Opis: {wzor.opis}")
                print(f"      Częstotliwość: {wzor.czestotliwosc}")
                if wzor.cechy_charakterystyczne:
                    print(f"      Cechy: {wzor.cechy_charakterystyczne}")
    
    print("\n" + "=" * 60)
    print(f"[{pobierz_aktualny_czas()}] Zakończono.")


def komenda_wersje(args):
    """Pokazuje listę wersji pamięci"""
    print(f"\n[{pobierz_aktualny_czas()}] Lista wersji pamięci...")
    
    # Inicjalizuj system
    system = utworz_system()
    
    # Pobierz listę wersji
    wersje = system.lista_wersji_pamieci()
    
    print("\n" + "=" * 60)
    print("DOSTĘPNE WERSJE PAMIĘCI")
    print("=" * 60)
    
    if not wersje:
        print("\nBrak dostępnych wersji pamięci.")
    else:
        print(f"\nLiczba wersji: {len(wersje)}")
        print("\n[LISTA WERSJI (od najnowszej)]")
        
        for i, wersja in enumerate(wersje, 1):
            stat = wersja.stat()
            print(f"  {i}. {wersja.name}")
            print(f"     Rozmiar: {stat.st_size:,} bajtów")
            print(f"     Data modyfikacji: {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Spróbuj wczytać metadane
            metadata_file = wersja.parent / f"system_metadata_{wersja.stem.split('pamiec_')[-1]}.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    print(f"     System: {metadata.get('system', 'N/A')}")
                    print(f"     Wersja: {metadata.get('wersja', 'N/A')}")
                except:
                    pass
            print()
    
    # Kalibrator wersje
    if system.kalibrator:
        kalibrator_wersje = system.kalibrator.lista_wersji()
        print(f"\n[WERSJE KALIBRATORA]")
        print(f"Liczba wersji: {len(kalibrator_wersje)}")
        for i, wersja in enumerate(kalibrator_wersje, 1):
            stat = wersja.stat()
            print(f"  {i}. {wersja.name} ({stat.st_size:,} bajtów)")
    
    print(f"\n[{pobierz_aktualny_czas()}] Zakończono.")


def komenda_zaladuj_wersje(args):
    """Ładuje konkretną wersję pamięci"""
    print(f"\n[{pobierz_aktualny_czas()}] Ładowanie wersji pamięci...")
    
    # Inicjalizuj system bez ładowania domyślnego
    system = SystemPamieciV2(auto_init=False)
    system.inicjalizuj()
    
    # Załaduj wersję
    success = system.zaladuj_wersje_pamieci(Path(args.plik))
    
    if success:
        print(f"\nWersja pamięci załadowana pomyślnie: {args.plik}")
        
        # Pokaz statystyki
        statystyki = system.repozytorium.pobierz_statystyki()
        print(f"  Obserwacje: {statystyki.calkowita_liczba_obserwacji}")
        print(f"  Klasy: {statystyki.liczba_klas}")
        print(f"  Modele: {statystyki.liczba_modeli}")
        print(f"  Skuteczność: {statystyki.srednia_skutecznosc:.4f}")
    else:
        print(f"\nBłąd ładowania wersji: {args.plik}")
    
    print(f"\n[{pobierz_aktualny_czas()}] Zakończono.")


def komenda_test(args):
    """Uruchamia testy systemu"""
    print(f"\n[{pobierz_aktualny_czas()}] Uruchamiam testy systemu...")
    
    all_tests_passed = True
    
    try:
        # Import modułu testowego
        from pamiec_modeli_v2 import integration
        
        # Uruchom testy
        print("\nTesty integracji...")
        try:
            integration.main()
        except Exception as e:
            print(f"  Błąd: {e}")
            all_tests_passed = False
        
        print("\nTesty kalibratora...")
        from pamiec_modeli_v2.level2 import kalibrator
        try:
            kalibrator.main()
        except Exception as e:
            print(f"  Błąd: {e}")
            all_tests_passed = False
        
        print("\nTesty agregatora...")
        from pamiec_modeli_v2.level1 import aggregator
        try:
            aggregator.main()
        except Exception as e:
            print(f"  Błąd: {e}")
            all_tests_passed = False
        
        print("\nTesty repozytorium...")
        from pamiec_modeli_v2.pamiec import repozytorium
        try:
            repozytorium.main()
        except Exception as e:
            print(f"  Błąd: {e}")
            all_tests_passed = False
        
        print("\nTesty schemas...")
        from pamiec_modeli_v2 import schemas
        try:
            schemas.main()
        except Exception as e:
            print(f"  Błąd: {e}")
            all_tests_passed = False
        
    except Exception as e:
        print(f"Błąd testów: {e}")
        traceback.print_exc()
        all_tests_passed = False
    
    print(f"\n[{pobierz_aktualny_czas()}] Zakończono.")
    
    if not all_tests_passed:
        sys.exit(1)


# =============================================================================
# KONFIGURACJA ARGUMENTÓW CLI
# =============================================================================

def konfiguruj_argumenty():
    """Konfiguruje argumenty wiersza poleceń"""
    parser = argparse.ArgumentParser(
        description="System Pamięci Modeli V2 - Predykcje piłkarskie z uczeniem się",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  # Generuj predykcję
  python uruchom_system_v2.py --mecz "Team A - Team B" --dane dane/database_dzisiaj.csv

  # Generuj predykcje batch
  python uruchom_system_v2.py --batch dane/database_dzisiaj.csv --wyjscie predykcje.csv

  # Trenuj kalibrator
  python uruchom_system_v2.py --trenuj

  # Pełny cykl
  python uruchom_system_v2.py --pelny-cykl --dane dane/database_dzisiaj.csv --wyniki wyniki.csv

  # Statystyki
  python uruchom_system_v2.py --statystyki

  # Wzorce
  python uruchom_system_v2.py --wzorce
        """
    )
    
    # Argumenty globalne
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Włącz tryb debug (więcej informacji)'
    )
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Nie zapisuj wersji pamięci'
    )
    
    # Podkomendy
    subparsers = parser.add_subparsers(
        dest='komenda',
        title='Dostępne komendy',
        description='Wybierz komendę do wykonania'
    )
    
    # Komenda: predykcja
    predykcja_parser = subparsers.add_parser(
        'predykcja',
        help='Generuj predykcję dla pojedynczego meczu',
        aliases=['p']
    )
    predykcja_parser.add_argument(
        '--mecz',
        type=str,
        required=True,
        help='Identyfikator meczu (np. "Team A - Team B")'
    )
    predykcja_parser.add_argument(
        '--dane',
        type=str,
        default=DEFAULT_DANE_PATH,
        help=f'Plik z danymi meczów (domyślnie: {DEFAULT_DANE_PATH})'
    )
    predykcja_parser.add_argument(
        '--grupa',
        type=str,
        default='BRAK',
        help='Identyfikator grupy świata'
    )
    predykcja_parser.add_argument(
        '--wynik',
        type=str,
        help='Rzeczywisty wynik (jeśli znany, zapisze obserwację)'
    )
    
    # Komenda: batch
    batch_parser = subparsers.add_parser(
        'batch',
        help='Generuj predykcje dla wielu meczów (batch)',
        aliases=['b']
    )
    batch_parser.add_argument(
        '--dane',
        type=str,
        default=DEFAULT_DANE_PATH,
        help=f'Plik z danymi meczów (domyślnie: {DEFAULT_DANE_PATH})'
    )
    batch_parser.add_argument(
        '--wyniki',
        type=str,
        default=DEFAULT_WYNIKI_PATH,
        help=f'Plik z wynikami rzeczywistymi (domyślnie: {DEFAULT_WYNIKI_PATH})'
    )
    batch_parser.add_argument(
        '--wyjscie',
        type=str,
        default=DEFAULT_OUTPUT_PATH,
        help=f'Plik wyjściowy z predykcjami (domyślnie: {DEFAULT_OUTPUT_PATH})'
    )
    batch_parser.add_argument(
        '--kalibrowane',
        action='store_true',
        help='Generuj kalibrowane predykcje (Level 2)'
    )
    
    # Komenda: trenuj
    trenuj_parser = subparsers.add_parser(
        'trenuj',
        help='Trenuj kalibrator Level 2',
        aliases=['t']
    )
    trenuj_parser.add_argument(
        '--min-obs',
        type=int,
        default=100,
        help='Minimalna liczba obserwacji do trenowania (domyślnie: 100)'
    )
    
    # Komenda: monitor
    monitor_parser = subparsers.add_parser(
        'monitor',
        help='Monitoruj plik danych i automatycznie przetwarzaj nowe mecze',
        aliases=['m']
    )
    monitor_parser.add_argument(
        '--dane',
        type=str,
        default=DEFAULT_DANE_PATH,
        help=f'Plik do monitorowania (domyślnie: {DEFAULT_DANE_PATH})'
    )
    monitor_parser.add_argument(
        '--wyjscie',
        type=str,
        help='Plik wyjściowy z predykcjami'
    )
    monitor_parser.add_argument(
        '--interwal',
        type=int,
        default=60,
        help='Interwał odświeżania w sekundach (domyślnie: 60)'
    )
    
    # Komenda: pelny-cykl
    pelny_cykl_parser = subparsers.add_parser(
        'pelny-cykl',
        help='Pełny cykl: predykcja + obserwacja + trenowanie + wersjonowanie',
        aliases=['c']
    )
    pelny_cykl_parser.add_argument(
        '--dane',
        type=str,
        default=DEFAULT_DANE_PATH,
        help=f'Plik z danymi meczów (domyślnie: {DEFAULT_DANE_PATH})'
    )
    pelny_cykl_parser.add_argument(
        '--wyniki',
        type=str,
        default=DEFAULT_WYNIKI_PATH,
        help=f'Plik z wynikami rzeczywistymi (domyślnie: {DEFAULT_WYNIKI_PATH})'
    )
    
    # Komenda: statystyki
    statystyki_parser = subparsers.add_parser(
        'statystyki',
        help='Pokaż statystyki systemu',
        aliases=['s']
    )
    
    # Komenda: wzorce
    wzorce_parser = subparsers.add_parser(
        'wzorce',
        help='Pokaż wykryte wzorce zachowania',
        aliases=['w']
    )
    
    # Komenda: wersje
    wersje_parser = subparsers.add_parser(
        'wersje',
        help='Pokaż listę wersji pamięci',
        aliases=['v']
    )
    
    # Komenda: zaladuj-wersje
    zaladuj_parser = subparsers.add_parser(
        'zaladuj-wersje',
        help='Załaduj konkretną wersję pamięci'
    )
    zaladuj_parser.add_argument(
        'plik',
        type=str,
        help='Ścieżka do pliku wersji pamięci'
    )
    
    # Komenda: test
    test_parser = subparsers.add_parser(
        'test',
        help='Uruchom testy systemu'
    )
    
    return parser


# =============================================================================
# GŁÓWNA FUNKCJA
# =============================================================================

def main():
    """Główna funkcja skryptu"""
    parser = konfiguruj_argumenty()
    args = parser.parse_args()
    
    # Jeśli nie podano komendy, pokaż pomoc
    if not args.komenda:
        parser.print_help()
        return
    
    # Obsługa debug
    if args.debug:
        print(f"[DEBUG] Argumenty: {args}")
    
    # Mapowanie komend na funkcje
    komendy = {
        'predykcja': komenda_predykcja,
        'p': komenda_predykcja,
        'batch': komenda_batch,
        'b': komenda_batch,
        'trenuj': komenda_trenuj,
        't': komenda_trenuj,
        'monitor': komenda_monitor,
        'm': komenda_monitor,
        'pelny-cykl': komenda_pelny_cykl,
        'c': komenda_pelny_cykl,
        'statystyki': komenda_statystyki,
        's': komenda_statystyki,
        'wzorce': komenda_wzorce,
        'w': komenda_wzorce,
        'wersje': komenda_wersje,
        'v': komenda_wersje,
        'zaladuj-wersje': komenda_zaladuj_wersje,
        'test': komenda_test,
    }
    
    # Wykonaj komendę
    try:
        func = komendy.get(args.komenda)
        if func:
            func(args)
        else:
            print(f"Nieznana komenda: {args.komenda}")
            parser.print_help()
    except Exception as e:
        print(f"\nBłąd: {e}")
        if args.debug:
            traceback.print_exc()
        sys.exit(1)


# =============================================================================
# URUCHOMIENIE
# =============================================================================

if __name__ == "__main__":
    main()
