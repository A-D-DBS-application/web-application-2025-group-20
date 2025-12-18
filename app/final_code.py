import requests
import re
from dataclasses import dataclass
from typing import List, Dict, Any

JWT_TOKEN = "eyJhbGciOiJSUzI1NiJ9.eyJ0ZWFtIjoxNTM5OTY1MTk3LCJpYXQiOjE3NjQ4NjEzODMsImlzcyI6ImJpenp5OnB1YmxpYy1hcGkiLCJzdWIiOiIxNTM5OTY1MTk3In0.U34ClDcN5YZzDbkNSxQlGcLLvfn-V0m8iAh-fJwMiml2FQpo9nb9elgxoA7Qg5yn6VDopyq9tqTUk-ezTjrn-m-ixJLxe4CHKMuRDk2sgo5jBLWrxQgTLwFqLKQyxraUcJnVYh6nI8l11nLZT-X2-p0Z1gf6LP1HWs1Y0SWlfd6-Ci8qro7wyAQSplj22KiJ2Aphmm695elV8A4Wii4DIG2AgWB_goXfbs0fWoAh4aQLZxgOsdkyo4IbQNP-SAdHb2J_CYaGqsqkF6amxSfGT8Y-OJOZaT-zqLbmMy6p5c-vAG9HkusypDoToNg5bUpl84bPKEWNystRoUSimnTgyA"  # <-- zet hier je echte token
BASE_URL = "https://api.bizzy.ai/v1/companies/BE/"

HEADERS = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Accept": "application/json"
}


def api_get(endpoint: str) -> Dict[str, Any]:
    response = requests.get(BASE_URL + endpoint, headers=HEADERS)

    if not response.ok:
        raise RuntimeError(
            f"API-fout ({response.status_code}): {response.text}"
        )

    return response.json()


def clean_vat_number(raw: str) -> str:
    digits = re.sub(r"\D", "", raw)

    # Belgische BTW: 10 cijfers waarvan eerste soms 0 -> strippen
    if len(digits) == 10 and digits.startswith("0"):
        digits = digits[1:]

    if len(digits) == 10 and digits.startswith("1"):
        return digits

    if len(digits) != 9:
        raise ValueError(f"BTW-nummer moet 9 cijfers hebben (nu {len(digits)}): {raw}")

    return digits

@dataclass
class CompanyDetails:
    name: str
    street: str
    zip_code: str
    city: str
    country: str

    def get(self, field: str) -> str:
        return getattr(self, field, "")


@dataclass
class AnnualAccount:
    year: int
    health_indicator: int = None

    # Profitability
    revenue: float = 0.0
    gross_margin: float = 0.0
    ebitda: float = 0.0
    ebit: float = 0.0
    net_profit: float = 0.0

    # Liquidity
    cash: float = 0.0
    cash_flow: float = 0.0
    nwc: float = 0.0
    nwcr: float = 0.0
    current_ratio: float = 0.0
    quick_ratio: float = 0.0

    # Solvency
    total_assets: float = 0.0
    equity: float = 0.0
    capital: float = 0.0
    retained_earnings: float = 0.0
    debt: float = 0.0
    long_term_debt: float = 0.0
    short_term_debt: float = 0.0

    # People
    employees: float = 0.0
    new_hires: int = 0
    male_ratio: float = 0.0
    female_ratio: float = 0.0

    def get(self, field_name: str):
        return getattr(self, field_name, '')

    def solvency_ratio(self) -> float:
        if self.total_assets == 0:
            return 0.0
        return self.equity / self.total_assets

    def __str__(self):
        return (
            f"Jaar {self.year} - Solvabiliteit: {self.solvency_ratio():.2f}"
        )

def parse_details(data: dict) -> CompanyDetails:
    identifier = data.get("identifier", {})
    addr = data.get("data", {}).get("address", {})

    street = addr.get("street")
    number = addr.get("number")
    street_full = f"{street} {number}" if street and number else street

    return CompanyDetails(
        name=identifier.get("name"),
        street=street_full,
        zip_code=addr.get("postalCode"),
        city=addr.get("place"),
        country=addr.get("country")
    )


def parse_financials(data: dict) -> List[AnnualAccount]:
    items = data.get("data", [])
    accounts = []

    for item in items:
        year = int(item.get("startDate", "0000-00-00")[:4])

        profitability = item.get("profitability", {})
        liquidity = item.get("liquidity", {})
        solvency = item.get("solvency", {})
        people = item.get("people", {})

        accounts.append(AnnualAccount(
            year=year,
            health_indicator=item.get("healthIndicator"),

            revenue=profitability.get("revenue", 0),
            gross_margin=profitability.get("grossMargin", 0),
            ebitda=profitability.get("ebitda", 0),
            ebit=profitability.get("ebit", 0),
            net_profit=profitability.get("netProfit", 0),

            cash=liquidity.get("cash", 0),
            cash_flow=liquidity.get("cashFlow", 0),
            nwc=liquidity.get("netWorkingCapital", 0),
            nwcr=liquidity.get("netWorkingCapitalRequirement", 0),
            current_ratio=liquidity.get("currentRatio", 0),
            quick_ratio=liquidity.get("quickRatio", 0),

            total_assets=solvency.get("totalAssets", 0),
            equity=solvency.get("equity", 0),
            capital=solvency.get("capital", 0),
            retained_earnings=solvency.get("retainedEarnings", 0),
            debt=solvency.get("debt", 0),
            long_term_debt=solvency.get("longTermDebt", 0),
            short_term_debt=solvency.get("shortTermDebt", 0),

            employees=people.get("employees", 0),
            new_hires=people.get("newHires", 0),
            male_ratio=people.get("employeeMaleRatio", 0),
            female_ratio=people.get("employeeFemaleRatio", 0)
        ))

    return accounts

def process_vat(nummer: str):
    try:
        nummer_clean = clean_vat_number(nummer)
    except ValueError as e:
        print(f"\nOngeldig BTW-nummer '{nummer}': {e}")
        return

    try:
        details_raw = api_get(f"{nummer_clean}")
    except Exception as e:
        print(f"\nDetails niet gevonden voor BE{nummer_clean}: {e}")
        return

    details = parse_details(details_raw)

    try:
        financials_raw = api_get(f"{nummer_clean}/financials")
    except Exception:
        print(f"\nGeen financiële gegevens gevonden voor {details.name}")
        financials_raw = {}

    accounts = parse_financials(financials_raw)

    print("\n" + "=" * 60)
    print(f"Bedrijf: {details.name}")
    print(f"Adres: {details.street}, {details.zip_code} {details.city}, {details.country}")
    print("=" * 60)

    if not accounts:
        print("Geen financiële cijfers beschikbaar.")
    else:
        print("\nFinanciële gegevens:")
        for acc in sorted(accounts, key=lambda x: x.year, reverse=True):
            print(" -", str(acc))


if __name__ == "__main__":
    raw_input_string = input("Geef één of meerdere BTW-nummers, gescheiden door komma’s: ")
    for nummer in [x.strip() for x in raw_input_string.split(",") if x.strip()]:
        process_vat(nummer)

#Test nummers: 0416375270,0403.199.702,BE5,770493071,0123456789,012345678


