from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, List

# ENUM STAVŮ ZÁSILKY

class StavZasilky(str, Enum):
    NOVA = "nova"            # zásilka vytvořena
    PREVZATA = "prevzata"   # odesilatel ji odevzdal
    NA_CESTE = "na_ceste"   # jede k příjemci
    DORUCENA = "dorucena"   # doručena
    VRACENA = "vracena"     # vrácena zpět
    ZTRACENA = "ztracena"   # ztracena


# DATOVÉ TŘÍDY

@dataclass
class Osoba:
    """Reprezentuje odesílatele nebo příjemce zásilky."""
    jmeno: str
    adresa: str
    telefon: Optional[str] = None  # nepovinný

@dataclass
class Zaznam:
    """Jedna událost v historii zásilky."""
    cas: datetime
    stav: StavZasilky
    lokace: Optional[str] = None
    poznamka: Optional[str] = None


# HLAVNÍ TŘÍDA ZÁSILKA

@dataclass
class Zasilka:
    id_zasilky: str
    odesilatel: Osoba
    prijemce: Osoba
    cas_vytvoreni: datetime = field(default_factory=datetime.now)
    aktualni_stav: StavZasilky = StavZasilky.NOVA
    historie: List[Zaznam] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Automaticky přidá první záznam do historie při vytvoření zásilky."""
        self._pridej_zaznam(StavZasilky.NOVA, "Sklad")

    def _pridej_zaznam(
        self,
        stav: StavZasilky,
        lokace: Optional[str] = None,
        poznamka: Optional[str] = None
    ) -> None:
        """Přidá nový záznam do historie a aktualizuje stav zásilky."""
        self.aktualni_stav = stav
        self.historie.append(Zaznam(datetime.now(), stav, lokace, poznamka))

# METODY PRO ZMĚNU STAVU

    def prevzata(self, lokace: str) -> None:
        """Zásilka byla převzata od odesílatele."""
        if self.aktualni_stav == StavZasilky.ZTRACENA:
            raise ValueError("Zásilka je ztracená a nemůže být převzata.")
        self._pridej_zaznam(StavZasilky.PREVZATA, lokace)

    def na_ceste(self, lokace: str) -> None:
        """Zásilka je na cestě k příjemci."""
        if self.aktualni_stav == StavZasilky.ZTRACENA:
            raise ValueError("Zásilka je ztracená a nemůže být na cestě.")
        self._pridej_zaznam(StavZasilky.NA_CESTE, lokace)

    def dorucena(self, lokace: str) -> None:
        """Zásilka byla doručena příjemci."""
        if self.aktualni_stav == StavZasilky.ZTRACENA:
            raise ValueError("Zásilka je ztracená a nemůže být doručena.")
        self._pridej_zaznam(StavZasilky.DORUCENA, lokace)

    def vracena(self, lokace: str) -> None:
        """Zásilka byla vrácena zpět odesílateli."""
        if self.aktualni_stav == StavZasilky.ZTRACENA:
            raise ValueError("Zásilka je ztracená a nemůže být vrácena.")
        self._pridej_zaznam(StavZasilky.VRACENA, lokace)

    def ztracena(self, poznamka: str = "") -> None:
        """Označí zásilku jako ztracenou."""
        self._pridej_zaznam(StavZasilky.ZTRACENA, poznamka=poznamka)

    def historie_zasilky(self) -> List[Zaznam]:
        """Vrátí kompletní historii zásilky."""
        return self.historie

    def info(self) -> str:
        """Vrátí textový popis aktuálního stavu zásilky."""
        return (
            f"Zásilka {self.id_zasilky}\n"
            f"Odesílatel: {self.odesilatel.jmeno}\n"
            f"Příjemce: {self.prijemce.jmeno}\n"
            f"Stav: {self.aktualni_stav.value}"
        )


# SPRÁVCE ZÁSILEK

class EvidenceZasilek:
    """Správa všech zásilek ve slovníku pro rychlý přístup podle ID."""

    def __init__(self) -> None:
        self.zasilky: Dict[str, Zasilka] = {}

    def registruj_zasilku(
        self,
        id_zasilky: str,
        odesilatel: Osoba,
        prijemce: Osoba
    ) -> Zasilka:
        """Vytvoří novou zásilku a uloží ji do evidence."""
        zasilka = Zasilka(id_zasilky, odesilatel, prijemce)
        self.zasilky[id_zasilky] = zasilka
        return zasilka

    def get_zasilka(self, id_zasilky: str) -> Zasilka:
        """Vrátí zásilku podle ID."""
        return self.zasilky[id_zasilky]

    def vsechny(self) -> List[Zasilka]:
        """Vrátí seznam všech registrovaných zásilek."""
        return list(self.zasilky.values())

    def vyhledat_dle_odesilatele(self, jmeno: str) -> List[Zasilka]:
        """Vrátí seznam zásilek podle jména odesílatele."""
        return [z for z in self.zasilky.values() if z.odesilatel.jmeno == jmeno]

    def vyhledat_dle_prijemce(self, jmeno: str) -> List[Zasilka]:
        """Vrátí seznam zásilek podle jména příjemce."""
        return [z for z in self.zasilky.values() if z.prijemce.jmeno == jmeno]

    def filtrovat_historii(
        self,
        stav: Optional[StavZasilky] = None,
        od: Optional[datetime] = None,
        do: Optional[datetime] = None
    ) -> List[Zaznam]:
        """Vrátí seznam záznamů z historie dle filtru stavu a časového rozsahu."""
        vysledek: List[Zaznam] = []
        for z in self.zasilky.values():
            for zaznam in z.historie:
                if stav and zaznam.stav != stav:
                    continue
                if od and zaznam.cas < od:
                    continue
                if do and zaznam.cas > do:
                    continue
                vysledek.append(zaznam)
        return vysledek

    def statistika(self) -> Dict[StavZasilky, int]:
        """Vrátí počet zásilek v jednotlivých stavech."""
        stats: Dict[StavZasilky, int] = {}
        for z in self.zasilky.values():
            stats[z.aktualni_stav] = stats.get(z.aktualni_stav, 0) + 1
        return stats


# UKÁZKA POUŽITÍ

if __name__ == "__main__":
    evidence = EvidenceZasilek()

    odesilatel = Osoba("Jan", "Praha")
    prijemce = Osoba("Petr", "Brno")

    z = evidence.registruj_zasilku("1", odesilatel, prijemce)

    z.prevzata("Praha")
    z.na_ceste("D1")
    z.dorucena("Brno")

    print(z.info())

    print("\nHistorie:")
    for h in z.historie_zasilky():
        print(h.cas, h.stav.value, h.lokace)
