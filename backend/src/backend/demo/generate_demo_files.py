from datetime import date, timedelta
from pathlib import Path
import pandas as pd

DEMO_DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "demo_data"
DEMO_DATA_DIR.mkdir(parents=True, exist_ok=True)

def generate_all_excel_files():
    today = date(2026, 10, 14)
    print(f"Generating demo Excel files in {DEMO_DATA_DIR}...")

    # =========================================================================
    # CASE A: CAFE AROMA (Initial Migration Scenario)
    # =========================================================================

    # 1. legacy_finances.xlsx
    finances = []
    for month_offset in [90, 60, 30, 2]:
        dt = today - timedelta(days=month_offset)
        finances.append({
            "Дата": (dt.replace(day=5)).strftime("%Y-%m-%d"),
            "Описание": "Аренда помещения кофейни (ул. Абая 45)",
            "Сумма": 650000,
            "Тип": "Расход",
            "Категория": "Аренда помещения"
        })
        finances.append({
            "Дата": (dt.replace(day=10)).strftime("%Y-%m-%d"),
            "Описание": "Аванс заработной платы бариста и смене",
            "Сумма": 425000,
            "Тип": "Расход",
            "Категория": "Фонд оплаты труда"
        })
        finances.append({
            "Дата": (dt.replace(day=25)).strftime("%Y-%m-%d"),
            "Описание": "Окончательный расчет по ЗП",
            "Сумма": 425000,
            "Тип": "Расход",
            "Категория": "Фонд оплаты труда"
        })
        finances.append({
            "Дата": (dt.replace(day=15)).strftime("%Y-%m-%d"),
            "Описание": "Коммунальные услуги и электроэнергия",
            "Сумма": 91500 + (month_offset % 3) * 2300,
            "Тип": "Расход",
            "Категория": "Коммунальные услуги"
        })
        finances.append({
            "Дата": (dt.replace(day=18)).strftime("%Y-%m-%d"),
            "Описание": "Техническое обслуживание и чистка эспрессо-машины Nuova Simonelli",
            "Сумма": 45000,
            "Тип": "Расход",
            "Категория": "Обслуживание оборудования"
        })

    # Coffee purchases in finances (Cafe Aroma)
    for days_ago in [85, 55, 28]:
        finances.append({
            "Дата": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Описание": "Закупка кофе в зернах Espresso Blend (25 кг)",
            "Сумма": 250000,
            "Тип": "Расход",
            "Категория": "Закупка кофе"
        })
    finances.append({
        "Дата": (today - timedelta(days=6)).strftime("%Y-%m-%d"),
        "Описание": "Закупка кофе в зернах Espresso Blend (25 кг по новой цене)",
        "Сумма": 287500,
        "Тип": "Расход",
        "Категория": "Закупка кофе"
    })

    for days_ago in [95, 80, 65, 50, 35, 20, 5]:
        finances.append({
            "Дата": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Описание": "Закупка ультрапастеризованного молока 3.2% (120 л)",
            "Сумма": 120 * 480,
            "Тип": "Расход",
            "Категория": "Закупка молока и продуктов"
        })

    for days_ago in [90, 60, 30, 8]:
        finances.append({
            "Дата": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Описание": "Заказ стаканов 350мл, крышек и барных салфеток",
            "Сумма": 78500,
            "Тип": "Расход",
            "Категория": "Расходные материалы"
        })

    for days_ago in [75, 40, 12]:
        finances.append({
            "Дата": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Описание": "Пополнение запаса сиропов (Ваниль, Карамель) и листового чая",
            "Сумма": 42000,
            "Тип": "Расход",
            "Категория": "Закупка молока и продуктов"
        })

    for i in range(15):
        dt = today - timedelta(days=i * 7 + 2)
        finances.append({
            "Дата": dt.strftime("%Y-%m-%d"),
            "Описание": "Выручка кофейни за неделю (касса + безналичный эквайринг)",
            "Сумма": 680000 + (i % 4) * 45000,
            "Тип": "Доход",
            "Категория": "Выручка / Продажи"
        })

    df_finances = pd.DataFrame(finances)
    df_finances["Дата"] = pd.to_datetime(df_finances["Дата"])
    df_finances = df_finances.sort_values("Дата").reset_index(drop=True)
    df_finances["Дата"] = df_finances["Дата"].dt.strftime("%Y-%m-%d")
    df_finances.to_excel(DEMO_DATA_DIR / "legacy_finances.xlsx", index=False)
    print(f"Created {DEMO_DATA_DIR / 'legacy_finances.xlsx'} with {len(df_finances)} rows.")

    # 2. legacy_purchases.xlsx
    purchases = []
    for days_ago, price in [(85, 10000.0), (55, 10000.0), (28, 10000.0), (6, 11500.0)]:
        purchases.append({
            "Дата закупки": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Наименование товара": "Кофе в зернах Espresso Blend 100% Арабика",
            "Поставщик": "Coffee Roasters Hub",
            "Количество": 25.0,
            "Единица": "кг",
            "Цена за единицу": price,
            "Итоговая сумма": 25.0 * price
        })

    for days_ago in [95, 80, 65, 50, 35, 20, 5]:
        purchases.append({
            "Дата закупки": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Наименование товара": "Молоко ультрапастеризованное 3.2%",
            "Поставщик": "Almaty Dairy Group",
            "Количество": 120.0,
            "Единица": "л",
            "Цена за единицу": 480.0,
            "Итоговая сумма": 120.0 * 480.0
        })

    for days_ago in [75, 40, 12]:
        purchases.append({
            "Дата закупки": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Наименование товара": "Сироп Ваниль 1л",
            "Поставщик": "Barista Pro Supplies",
            "Количество": 6.0,
            "Единица": "бут",
            "Цена за единицу": 3900.0,
            "Итоговая сумма": 23400.0
        })
        purchases.append({
            "Дата закупки": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Наименование товара": "Сироп Карамель 1л",
            "Поставщик": "Barista Pro Supplies",
            "Количество": 6.0,
            "Единица": "бут",
            "Цена за единицу": 3900.0,
            "Итоговая сумма": 23400.0
        })

    for days_ago in [90, 60, 30, 8]:
        purchases.append({
            "Дата закупки": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Наименование товара": "Стаканы бумажные двухслойные 350мл (50 шт)",
            "Поставщик": "EcoPack Kazakhstan",
            "Количество": 30.0,
            "Единица": "упак",
            "Цена за единицу": 1450.0,
            "Итоговая сумма": 43500.0
        })
        purchases.append({
            "Дата закупки": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Наименование товара": "Крышки для стаканов 80мм (100 шт)",
            "Поставщик": "EcoPack Kazakhstan",
            "Количество": 15.0,
            "Единица": "упак",
            "Цена за единицу": 980.0,
            "Итоговая сумма": 14700.0
        })
        purchases.append({
            "Дата закупки": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Наименование товара": "Салфетки барные 24x24 (400 шт)",
            "Поставщик": "EcoPack Kazakhstan",
            "Количество": 20.0,
            "Единица": "упак",
            "Цена за единицу": 750.0,
            "Итоговая сумма": 15000.0
        })

    for days_ago in [75, 20]:
        purchases.append({
            "Дата закупки": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Наименование товара": "Чай листовой черный Ассам",
            "Поставщик": "Barista Pro Supplies",
            "Количество": 4.0,
            "Единица": "кг",
            "Цена за единицу": 5200.0,
            "Итоговая сумма": 20800.0
        })

    df_purchases = pd.DataFrame(purchases)
    df_purchases["Дата закупки"] = pd.to_datetime(df_purchases["Дата закупки"])
    df_purchases = df_purchases.sort_values("Дата закупки").reset_index(drop=True)
    df_purchases["Дата закупки"] = df_purchases["Дата закупки"].dt.strftime("%Y-%m-%d")
    df_purchases.to_excel(DEMO_DATA_DIR / "legacy_purchases.xlsx", index=False)
    print(f"Created {DEMO_DATA_DIR / 'legacy_purchases.xlsx'} with {len(df_purchases)} rows.")

    # 3. legacy_inventory.xlsx
    inventory = [
        {"Наименование": "Кофе в зернах Espresso Blend 100% Арабика", "Категория": "Кофе", "Текущий остаток": 18.0, "Единица": "кг", "Минимальный остаток": 15.0},
        {"Наименование": "Молоко ультрапастеризованное 3.2%", "Категория": "Молочная продукция", "Текущий остаток": 12.0, "Единица": "л", "Минимальный остаток": 25.0},
        {"Наименование": "Сироп Ваниль 1л", "Категория": "Сиропы и топпинги", "Текущий остаток": 4.0, "Единица": "бут", "Минимальный остаток": 5.0},
        {"Наименование": "Сироп Карамель 1л", "Категория": "Сиропы и топпинги", "Текущий остаток": 7.0, "Единица": "бут", "Минимальный остаток": 5.0},
        {"Наименование": "Стаканы бумажные двухслойные 350мл (50 шт)", "Категория": "Упаковка и расходники", "Текущий остаток": 14.0, "Единица": "упак", "Минимальный остаток": 10.0},
        {"Наименование": "Крышки для стаканов 80мм (100 шт)", "Категория": "Упаковка и расходники", "Текущий остаток": 8.0, "Единица": "упак", "Минимальный остаток": 10.0},
        {"Наименование": "Салфетки барные 24x24 (400 шт)", "Категория": "Упаковка и расходники", "Текущий остаток": 12.0, "Единица": "упак", "Минимальный остаток": 8.0},
        {"Наименование": "Трубочки биоразлагаемые (200 шт)", "Категория": "Упаковка и расходники", "Текущий остаток": 9.0, "Единица": "упак", "Минимальный остаток": 5.0},
        {"Наименование": "Чай листовой черный Ассам", "Категория": "Чай", "Текущий остаток": 3.5, "Единица": "кг", "Минимальный остаток": 2.0},
        {"Наименование": "Чай зеленый Сенча", "Категория": "Чай", "Текущий остаток": 2.5, "Единица": "кг", "Минимальный остаток": 2.0}
    ]
    pd.DataFrame(inventory).to_excel(DEMO_DATA_DIR / "legacy_inventory.xlsx", index=False)
    print(f"Created {DEMO_DATA_DIR / 'legacy_inventory.xlsx'} with {len(inventory)} rows.")

    # 4. supplier_price_list.xlsx (Cafe Aroma)
    supplier_prices = [
        {"Поставщик": "Aroma Direct", "Товар": "Кофе в зернах Espresso Blend 100% Арабика", "Фасовка": 1.0, "Единица": "кг", "Цена": 10350.0, "Мин. заказ": 20.0, "Доставка": 0.0, "Дата обновления": (today - timedelta(days=2)).strftime("%Y-%m-%d")},
        {"Поставщик": "BeanTrade Almaty", "Товар": "Кофе в зернах Espresso Blend 100% Арабика", "Фасовка": 1.0, "Единица": "кг", "Цена": 10800.0, "Мин. заказ": 15.0, "Доставка": 1500.0, "Дата обновления": (today - timedelta(days=4)).strftime("%Y-%m-%d")},
        {"Поставщик": "Coffee Roasters Hub", "Товар": "Кофе в зернах Espresso Blend 100% Арабика", "Фасовка": 1.0, "Единица": "кг", "Цена": 11500.0, "Мин. заказ": 10.0, "Доставка": 2500.0, "Дата обновления": (today - timedelta(days=6)).strftime("%Y-%m-%d")},
        {"Поставщик": "Premium Coffee Express", "Товар": "Кофе в зернах Espresso Blend 100% Арабика", "Фасовка": 1.0, "Единица": "кг", "Цена": 12200.0, "Мин. заказ": 5.0, "Доставка": 0.0, "Дата обновления": (today - timedelta(days=1)).strftime("%Y-%m-%d")},
        {"Поставщик": "Qazaq Milk Line", "Товар": "Молоко ультрапастеризованное 3.2%", "Фасовка": 1.0, "Единица": "л", "Цена": 440.0, "Мин. заказ": 50.0, "Доставка": 0.0, "Дата обновления": (today - timedelta(days=3)).strftime("%Y-%m-%d")},
        {"Поставщик": "Almaty Dairy Group", "Товар": "Молоко ультрапастеризованное 3.2%", "Фасовка": 1.0, "Единица": "л", "Цена": 480.0, "Мин. заказ": 40.0, "Доставка": 1000.0, "Дата обновления": (today - timedelta(days=5)).strftime("%Y-%m-%d")},
        {"Поставщик": "Global Pack Almaty", "Товар": "Стаканы бумажные двухслойные 350мл (50 шт)", "Фасовка": 1.0, "Единица": "упак", "Цена": 1350.0, "Мин. заказ": 20.0, "Доставка": 1000.0, "Дата обновления": (today - timedelta(days=5)).strftime("%Y-%m-%d")},
        {"Поставщик": "EcoPack Kazakhstan", "Товар": "Стаканы бумажные двухслойные 350мл (50 шт)", "Фасовка": 1.0, "Единица": "упак", "Цена": 1450.0, "Мин. заказ": 10.0, "Доставка": 1800.0, "Дата обновления": (today - timedelta(days=7)).strftime("%Y-%m-%d")},
        {"Поставщик": "SweetSyrup Co", "Товар": "Сироп Ваниль 1л", "Фасовка": 1.0, "Единица": "бут", "Цена": 3650.0, "Мин. заказ": 4.0, "Доставка": 0.0, "Дата обновления": (today - timedelta(days=4)).strftime("%Y-%m-%d")},
        {"Поставщик": "Barista Pro Supplies", "Товар": "Сироп Ваниль 1л", "Фасовка": 1.0, "Единица": "бут", "Цена": 3900.0, "Мин. заказ": 4.0, "Доставка": 1200.0, "Дата обновления": (today - timedelta(days=8)).strftime("%Y-%m-%d")}
    ]
    pd.DataFrame(supplier_prices).to_excel(DEMO_DATA_DIR / "supplier_price_list.xlsx", index=False)
    print(f"Created {DEMO_DATA_DIR / 'supplier_price_list.xlsx'} with {len(supplier_prices)} rows.")

    # =========================================================================
    # CASE B: DAILY CUP (Regular Long-Time User Scenario)
    # =========================================================================

    # 5. dailycup_finances.xlsx (5 months history: June - Oct 2026)
    dc_finances = []
    for month_offset in [120, 90, 60, 30, 2]:
        dt = today - timedelta(days=month_offset)
        # Rent
        dc_finances.append({
            "Дата": (dt.replace(day=3)).strftime("%Y-%m-%d"),
            "Описание": "Аренда помещения Daily Cup To-Go (ул. Достык 89)",
            "Сумма": 850000,
            "Тип": "Расход",
            "Категория": "Аренда помещения"
        })
        # FOT (2 shifts)
        dc_finances.append({
            "Дата": (dt.replace(day=10)).strftime("%Y-%m-%d"),
            "Описание": "Аванс заработной платы смены бариста",
            "Сумма": 480000,
            "Тип": "Расход",
            "Категория": "Фонд оплаты труда"
        })
        dc_finances.append({
            "Дата": (dt.replace(day=25)).strftime("%Y-%m-%d"),
            "Описание": "Расчет заработной платы бариста и клининг",
            "Сумма": 480000,
            "Тип": "Расход",
            "Категория": "Фонд оплаты труда"
        })
        # Utilities
        dc_finances.append({
            "Дата": (dt.replace(day=14)).strftime("%Y-%m-%d"),
            "Описание": "Коммунальные платежи и охрана точки",
            "Сумма": 110000 + (month_offset % 4) * 3200,
            "Тип": "Расход",
            "Категория": "Коммунальные услуги"
        })

    # Packaging purchases (Kraft cups 250ml - Key story: price rise +18.3%)
    for days_ago, price in [(115, 1200.0), (85, 1200.0), (55, 1200.0), (25, 1200.0), (4, 1420.0)]:
        dc_finances.append({
            "Дата": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Описание": f"Закупка крафтовых стаканов 250мл (60 упак по {int(price)} ₸)",
            "Сумма": int(60 * price),
            "Тип": "Расход",
            "Категория": "Расходные материалы"
        })

    # Coffee Daily Blend
    for days_ago in [110, 80, 50, 20]:
        dc_finances.append({
            "Дата": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Описание": "Закупка кофе Daily Blend 80/20 (40 кг)",
            "Сумма": 40 * 8200,
            "Тип": "Расход",
            "Категория": "Закупка кофе"
        })

    # Milk & Dairy (Parmalat + Oat milk)
    for days_ago in [120, 105, 90, 75, 60, 45, 30, 15, 3]:
        dc_finances.append({
            "Дата": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Описание": "Поставка молока Parmalat Barista и овсяного молока",
            "Сумма": 88000,
            "Тип": "Расход",
            "Категория": "Закупка молока и продуктов"
        })

    # Weekly Incomes (to-go high traffic)
    for i in range(20):
        dt = today - timedelta(days=i * 7 + 1)
        dc_finances.append({
            "Дата": dt.strftime("%Y-%m-%d"),
            "Описание": "Еженедельная выручка точки Daily Cup Достык",
            "Сумма": 980000 + (i % 5) * 40000,
            "Тип": "Доход",
            "Категория": "Выручка / Продажи"
        })

    df_dc_finances = pd.DataFrame(dc_finances)
    df_dc_finances["Дата"] = pd.to_datetime(df_dc_finances["Дата"])
    df_dc_finances = df_dc_finances.sort_values("Дата").reset_index(drop=True)
    df_dc_finances["Дата"] = df_dc_finances["Дата"].dt.strftime("%Y-%m-%d")
    df_dc_finances.to_excel(DEMO_DATA_DIR / "dailycup_finances.xlsx", index=False)
    print(f"Created {DEMO_DATA_DIR / 'dailycup_finances.xlsx'} with {len(df_dc_finances)} rows.")

    # 6. dailycup_purchases.xlsx
    dc_purchases = []
    # Kraft cups 250ml
    for days_ago, price in [(115, 1200.0), (85, 1200.0), (55, 1200.0), (25, 1200.0), (4, 1420.0)]:
        dc_purchases.append({
            "Дата закупки": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Наименование товара": "Стаканы двухслойные 250мл Kraft (50 шт)",
            "Поставщик": "PackGroup Almaty",
            "Количество": 60.0,
            "Единица": "упак",
            "Цена за единицу": price,
            "Итоговая сумма": 60.0 * price
        })

    # Kraft cups 350ml
    for days_ago in [115, 75, 35]:
        dc_purchases.append({
            "Дата закупки": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Наименование товара": "Стаканы двухслойные 350мл Kraft (50 шт)",
            "Поставщик": "PackGroup Almaty",
            "Количество": 40.0,
            "Единица": "упак",
            "Цена за единицу": 1450.0,
            "Итоговая сумма": 58000.0
        })

    # Cup holders
    for days_ago in [100, 50, 10]:
        dc_purchases.append({
            "Дата закупки": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Наименование товара": "Держатели для 2 стаканов (100 шт)",
            "Поставщик": "PackGroup Almaty",
            "Количество": 20.0,
            "Единица": "упак",
            "Цена за единицу": 850.0,
            "Итоговая сумма": 17000.0
        })

    # Coffee Daily Blend
    for days_ago in [110, 80, 50, 20]:
        dc_purchases.append({
            "Дата закупки": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Наименование товара": "Кофе в зернах Daily Blend (80% Арабика, 20% Робуста)",
            "Поставщик": "Silk Road Coffee Trading",
            "Количество": 40.0,
            "Единица": "кг",
            "Цена за единицу": 8200.0,
            "Итоговая сумма": 328000.0
        })

    # Milk
    for days_ago in [120, 90, 60, 30, 5]:
        dc_purchases.append({
            "Дата закупки": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Наименование товара": "Молоко бариста 3.2% Parmalat",
            "Поставщик": "Parmalat Distribution KZ",
            "Количество": 150.0,
            "Единица": "л",
            "Цена за единицу": 520.0,
            "Итоговая сумма": 78000.0
        })

    # Oat milk
    for days_ago in [90, 45, 8]:
        dc_purchases.append({
            "Дата закупки": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Наименование товара": "Растительное овсяное молоко Alpro Barista",
            "Поставщик": "Healthy Drinks Almaty",
            "Количество": 20.0,
            "Единица": "л",
            "Цена за единицу": 1150.0,
            "Итоговая сумма": 23000.0
        })

    # Syrups
    for days_ago in [90, 30]:
        dc_purchases.append({
            "Дата закупки": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Наименование товара": "Сироп Соленая карамель 1л Monin",
            "Поставщик": "Syrup Master KZ",
            "Количество": 8.0,
            "Единица": "бут",
            "Цена за единицу": 4600.0,
            "Итоговая сумма": 36800.0
        })

    df_dc_purchases = pd.DataFrame(dc_purchases)
    df_dc_purchases["Дата закупки"] = pd.to_datetime(df_dc_purchases["Дата закупки"])
    df_dc_purchases = df_dc_purchases.sort_values("Дата закупки").reset_index(drop=True)
    df_dc_purchases["Дата закупки"] = df_dc_purchases["Дата закупки"].dt.strftime("%Y-%m-%d")
    df_dc_purchases.to_excel(DEMO_DATA_DIR / "dailycup_purchases.xlsx", index=False)
    print(f"Created {DEMO_DATA_DIR / 'dailycup_purchases.xlsx'} with {len(df_dc_purchases)} rows.")

    # 7. dailycup_inventory.xlsx
    dc_inventory = [
        {"Наименование": "Стаканы двухслойные 250мл Kraft (50 шт)", "Категория": "Упаковка и расходники", "Текущий остаток": 15.0, "Единица": "упак", "Минимальный остаток": 20.0},
        {"Наименование": "Стаканы двухслойные 350мл Kraft (50 шт)", "Категория": "Упаковка и расходники", "Текущий остаток": 25.0, "Единица": "упак", "Минимальный остаток": 20.0},
        {"Наименование": "Крышки черные для стаканов 80мм (100 шт)", "Категория": "Упаковка и расходники", "Текущий остаток": 18.0, "Единица": "упак", "Минимальный остаток": 15.0},
        {"Наименование": "Держатели для 2 стаканов (100 шт)", "Категория": "Упаковка и расходники", "Текущий остаток": 6.0, "Единица": "упак", "Минимальный остаток": 12.0},  # Critical!
        {"Наименование": "Кофе в зернах Daily Blend (80% Арабика, 20% Робуста)", "Категория": "Кофе", "Текущий остаток": 35.0, "Единица": "кг", "Минимальный остаток": 25.0},
        {"Наименование": "Молоко бариста 3.2% Parmalat", "Категория": "Молочная продукция", "Текущий остаток": 60.0, "Единица": "л", "Минимальный остаток": 40.0},
        {"Наименование": "Растительное овсяное молоко Alpro Barista", "Категория": "Молочная продукция", "Текущий остаток": 8.0, "Единица": "л", "Минимальный остаток": 15.0},  # Low!
        {"Наименование": "Сироп Соленая карамель 1л Monin", "Категория": "Сиропы и топпинги", "Текущий остаток": 3.0, "Единица": "бут", "Минимальный остаток": 5.0},  # Low!
        {"Наименование": "Сироп Лесной орех 1л Monin", "Категория": "Сиропы и топпинги", "Текущий остаток": 4.0, "Единица": "бут", "Минимальный остаток": 5.0},
        {"Наименование": "Печенье Американо шоколадное (шоу-бокс 24 шт)", "Категория": "Выпечка и десерты", "Текущий остаток": 5.0, "Единица": "бокс", "Минимальный остаток": 4.0}
    ]
    pd.DataFrame(dc_inventory).to_excel(DEMO_DATA_DIR / "dailycup_inventory.xlsx", index=False)
    print(f"Created {DEMO_DATA_DIR / 'dailycup_inventory.xlsx'} with {len(dc_inventory)} rows.")

    # 8. dailycup_supplier_prices.xlsx
    dc_supplier_prices = [
        {"Поставщик": "EcoTorg Kazakhstan", "Товар": "Стаканы двухслойные 250мл Kraft (50 шт)", "Фасовка": 1.0, "Единица": "упак", "Цена": 1230.0, "Мин. заказ": 30.0, "Доставка": 0.0, "Дата обновления": (today - timedelta(days=2)).strftime("%Y-%m-%d")},
        {"Поставщик": "Almaty HoReCa Box", "Товар": "Стаканы двухслойные 250мл Kraft (50 шт)", "Фасовка": 1.0, "Единица": "упак", "Цена": 1290.0, "Мин. заказ": 20.0, "Доставка": 1000.0, "Дата обновления": (today - timedelta(days=3)).strftime("%Y-%m-%d")},
        {"Поставщик": "PackGroup Almaty", "Товар": "Стаканы двухслойные 250мл Kraft (50 шт)", "Фасовка": 1.0, "Единица": "упак", "Цена": 1420.0, "Мин. заказ": 20.0, "Доставка": 1500.0, "Дата обновления": (today - timedelta(days=4)).strftime("%Y-%m-%d")},
        {"Поставщик": "EcoTorg Kazakhstan", "Товар": "Держатели для 2 стаканов (100 шт)", "Фасовка": 1.0, "Единица": "упак", "Цена": 790.0, "Мин. заказ": 10.0, "Доставка": 0.0, "Дата обновления": (today - timedelta(days=5)).strftime("%Y-%m-%d")},
        {"Поставщик": "PackGroup Almaty", "Товар": "Держатели для 2 стаканов (100 шт)", "Фасовка": 1.0, "Единица": "упак", "Цена": 850.0, "Мин. заказ": 10.0, "Доставка": 1500.0, "Дата обновления": (today - timedelta(days=6)).strftime("%Y-%m-%d")},
        {"Поставщик": "BioMilk Almaty", "Товар": "Растительное овсяное молоко Alpro Barista", "Фасовка": 1.0, "Единица": "л", "Цена": 1080.0, "Мин. заказ": 12.0, "Доставка": 0.0, "Дата обновления": (today - timedelta(days=2)).strftime("%Y-%m-%d")},
        {"Поставщик": "Healthy Drinks Almaty", "Товар": "Растительное овсяное молоко Alpro Barista", "Фасовка": 1.0, "Единица": "л", "Цена": 1150.0, "Мин. заказ": 10.0, "Доставка": 1200.0, "Дата обновления": (today - timedelta(days=7)).strftime("%Y-%m-%d")},
        {"Поставщик": "Syrup Direct", "Товар": "Сироп Соленая карамель 1л Monin", "Фасовка": 1.0, "Единица": "бут", "Цена": 4350.0, "Мин. заказ": 4.0, "Доставка": 0.0, "Дата обновления": (today - timedelta(days=4)).strftime("%Y-%m-%d")}
    ]
    pd.DataFrame(dc_supplier_prices).to_excel(DEMO_DATA_DIR / "dailycup_supplier_prices.xlsx", index=False)
    print(f"Created {DEMO_DATA_DIR / 'dailycup_supplier_prices.xlsx'} with {len(dc_supplier_prices)} rows.")

if __name__ == "__main__":
    generate_all_excel_files()
