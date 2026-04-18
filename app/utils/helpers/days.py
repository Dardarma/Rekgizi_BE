from datetime import date

def  mapping_hari(weekday: int) -> str:
    day = {
        0: 'senin',
        1: 'selasa',
        2: 'rabu',
        3: 'kamis',
        4: 'jumat',
        5: 'sabtu',
        6: 'minggu'
    }

    return day[weekday]