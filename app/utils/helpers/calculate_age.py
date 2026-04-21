from datetime import date

def hitung_usia(tanggal_lahir):
    today = date.today()
    return today.year - tanggal_lahir.year - (
        (today.month, today.day) < (tanggal_lahir.month, tanggal_lahir.day)
    )