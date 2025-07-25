import pandas as pd

FILE_ID = "1K1XDOwUcrfbYr6QW0mOk_no1vzoCIygBwXc6qvSyqXM"
SHEET_IDS = {
    "log_hrana": 0,
    "log_teza": 1237121504,
    "log_drugo": 1362862141,
    "vrste_hrana": 54176045,
    "vrste_drugo": 1556951560,
}


def get_df_from_google_sheets(sheet_id: int) -> pd.DataFrame:
    url = (
        "https://docs.google.com/spreadsheets/d/"
        + FILE_ID
        + "/export?format=csv"
        + "&gid="
        + str(sheet_id)
    )
    return pd.read_csv(url, decimal=",")


def get_data() -> dict[pd.DataFrame]:
    log_hrana = get_df_from_google_sheets(SHEET_IDS["log_hrana"])[
        ["cas", "vrsta", "pojedel_g"]
    ]
    log_teza = get_df_from_google_sheets(SHEET_IDS["log_teza"])[["cas", "teza_g"]]
    log_drugo = get_df_from_google_sheets(SHEET_IDS["log_drugo"])[
        ["cas", "vrsta", "kolicina"]
    ]
    for df in [log_hrana, log_teza, log_drugo]:
        df["cas"] = pd.to_datetime(df["cas"], format="%Y-%m-%d %H:%M")

    vrste_hrana = get_df_from_google_sheets(SHEET_IDS["vrste_hrana"])[
        ["vrsta", "tip", "kcal_per_g"]
    ]
    vrste_drugo = get_df_from_google_sheets(SHEET_IDS["vrste_drugo"])[["vrsta", "tip"]]

    return {
        "log_hrana": log_hrana,
        "log_teza": log_teza,
        "log_drugo": log_drugo,
        "vrste_hrana": vrste_hrana,
        "vrste_drugo": vrste_drugo,
    }
