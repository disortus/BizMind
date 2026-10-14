from datetime import date, timedelta
from pathlib import Path
import pandas as pd

DEMO_DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "demo_data"
DEMO_DATA_DIR.mkdir(parents=True, exist_ok=True)

def generate_all_excel_files():
    today = date(2026, 10, 14)
    print(f"Generating demo Excel files in {DEMO_DATA_DIR}...")

    # 1. legacy_finances.xlsx
    finances = []
    # Generate ~80 financial transactions over 4 months (July - Oct 2026)
    categories_expenses = [
        ("Аренда помещения", 650000, 30),
        ("Фонд оплаты труда", 425000, 15),
        ("Фонд оплаты труда", 425000, 30),
        ("Коммунальные услуги", 92000, 20),
        ("Обслуживание оборудования", 45000, 45),
        ("Интернет и кассовое ПО", 18500, 30),
    ]

    # Purchases and regular costs
    start_date = today - timedelta(days=105)
    cur_date = start_date

    # Add monthly fixed expenses
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

    # Coffee purchases in finances
    # 3 past coffee purchases at 10,000/kg (25 kg each = 250,000)
    finances.append({
        "Дата": (today - timedelta(days=85)).strftime("%Y-%m-%d"),
        "Описание": "Закупка кофе в зернах Espresso Blend (25 кг)",
        "Сумма": 250000,
        "Тип": "Расход",
        "Категория": "Закупка кофе"
    })
    finances.append({
        "Дата": (today - timedelta(days=55)).strftime("%Y-%m-%d"),
        "Описание": "Закупка кофе в зернах Espresso Blend (25 кг)",
        "Сумма": 250000,
        "Тип": "Расход",
        "Категория": "Закупка кофе"
    })
    finances.append({
        "Дата": (today - timedelta(days=28)).strftime("%Y-%m-%d"),
        "Описание": "Закупка кофе в зернах Espresso Blend (25 кг)",
        "Сумма": 250000,
        "Тип": "Расход",
        "Категория": "Закупка кофе"
    })
    # Latest coffee purchase with price spike (11,500/kg * 25 = 287,500)
    finances.append({
        "Дата": (today - timedelta(days=6)).strftime("%Y-%m-%d"),
        "Описание": "Закупка кофе в зернах Espresso Blend (25 кг по новой цене)",
        "Сумма": 287500,
        "Тип": "Расход",
        "Категория": "Закупка кофе"
    })

    # Milk and dairy purchases
    for days_ago in [95, 80, 65, 50, 35, 20, 5]:
        finances.append({
            "Дата": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Описание": f"Закупка ультрапастеризованного молока 3.2% (120 л)",
            "Сумма": 120 * 480,
            "Тип": "Расход",
            "Категория": "Закупка молока и продуктов"
        })

    # Packaging and cups
    for days_ago in [90, 60, 30, 8]:
        finances.append({
            "Дата": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Описание": "Заказ стаканов 350мл, крышек и барных салфеток",
            "Сумма": 78500,
            "Тип": "Расход",
            "Категория": "Расходные материалы"
        })

    # Syrups and tea
    for days_ago in [75, 40, 12]:
        finances.append({
            "Дата": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Описание": "Пополнение запаса сиропов (Ваниль, Карамель) и листового чая",
            "Сумма": 42000,
            "Тип": "Расход",
            "Категория": "Закупка молока и продуктов"
        })

    # Revenues / Incomes (weekly sales records)
    for i in range(15):
        dt = today - timedelta(days=i * 7 + 2)
        finances.append({
            "Дата": dt.strftime("%Y-%m-%d"),
            "Описание": f"Выручка кофейни за неделю (касса + безналичный эквайринг)",
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
    # Coffee Purchases: 3 past at 10,000 and 1 latest at 11,500
    purchases.append({
        "Дата закупки": (today - timedelta(days=85)).strftime("%Y-%m-%d"),
        "Наименование товара": "Кофе в зернах Espresso Blend 100% Арабика",
        "Поставщик": "Coffee Roasters Hub",
        "Количество": 25.0,
        "Единица": "кг",
        "Цена за единицу": 10000.0,
        "Итоговая сумма": 250000.0
    })
    purchases.append({
        "Дата закупки": (today - timedelta(days=55)).strftime("%Y-%m-%d"),
        "Наименование товара": "Кофе в зернах Espresso Blend 100% Арабика",
        "Поставщик": "Coffee Roasters Hub",
        "Количество": 25.0,
        "Единица": "кг",
        "Цена за единицу": 10000.0,
        "Итоговая сумма": 250000.0
    })
    purchases.append({
        "Дата закупки": (today - timedelta(days=28)).strftime("%Y-%m-%d"),
        "Наименование товара": "Кофе в зернах Espresso Blend 100% Арабика",
        "Поставщик": "Coffee Roasters Hub",
        "Количество": 25.0,
        "Единица": "кг",
        "Цена за единицу": 10000.0,
        "Итоговая сумма": 250000.0
    })
    purchases.append({
        "Дата закупки": (today - timedelta(days=6)).strftime("%Y-%m-%d"),
        "Наименование товара": "Кофе в зернах Espresso Blend 100% Арабика",
        "Поставщик": "Coffee Roasters Hub",
        "Количество": 25.0,
        "Единица": "кг",
        "Цена за единицу": 11500.0,
        "Итоговая сумма": 287500.0
    })

    # Milk purchases
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

    # Syrups purchases
    for days_ago in [75, 40, 12]:
        purchases.append({
            "Дата закупки": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Наименование товара": "Сироп Ваниль 1л",
            "Поставщик": "Barista Pro Supplies",
            "Количество": 6.0,
            "Единица": "бут",
            "Цена за единицу": 3900.0,
            "Итоговая сумма": 6.0 * 3900.0
        })
        purchases.append({
            "Дата закупки": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Наименование товара": "Сироп Карамель 1л",
            "Поставщик": "Barista Pro Supplies",
            "Количество": 6.0,
            "Единица": "бут",
            "Цена за единицу": 3900.0,
            "Итоговая сумма": 6.0 * 3900.0
        })

    # Packaging purchases
    for days_ago in [90, 60, 30, 8]:
        purchases.append({
            "Дата закупки": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Наименование товара": "Стаканы бумажные двухслойные 350мл (50 шт)",
            "Поставщик": "EcoPack Kazakhstan",
            "Количество": 30.0,
            "Единица": "упак",
            "Цена за единицу": 1450.0,
            "Итоговая сумма": 30.0 * 1450.0
        })
        purchases.append({
            "Дата закупки": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Наименование товара": "Крышки для стаканов 80мм (100 шт)",
            "Поставщик": "EcoPack Kazakhstan",
            "Количество": 15.0,
            "Единица": "упак",
            "Цена за единицу": 980.0,
            "Итоговая сумма": 15.0 * 980.0
        })
        purchases.append({
            "Дата закупки": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Наименование товара": "Салфетки барные 24x24 (400 шт)",
            "Поставщик": "EcoPack Kazakhstan",
            "Количество": 20.0,
            "Единица": "упак",
            "Цена за единицу": 750.0,
            "Итоговая сумма": 20.0 * 750.0
        })

    # Tea purchases
    for days_ago in [75, 20]:
        purchases.append({
            "Дата закупки": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "Наименование товара": "Чай листовой черный Ассам",
            "Поставщик": "Barista Pro Supplies",
            "Количество": 4.0,
            "Единица": "кг",
            "Цена за единицу": 5200.0,
            "Итоговая сумма": 4.0 * 5200.0
        })

    df_purchases = pd.DataFrame(purchases)
    df_purchases["Дата закупки"] = pd.to_datetime(df_purchases["Дата закупки"])
    df_purchases = df_purchases.sort_values("Дата закупки").reset_index(drop=True)
    df_purchases["Дата закупки"] = df_purchases["Дата закупки"].dt.strftime("%Y-%m-%d")
    df_purchases.to_excel(DEMO_DATA_DIR / "legacy_purchases.xlsx", index=False)
    print(f"Created {DEMO_DATA_DIR / 'legacy_purchases.xlsx'} with {len(df_purchases)} rows.")

    # 3. legacy_inventory.xlsx
    inventory = [
        {
            "Наименование": "Кофе в зернах Espresso Blend 100% Арабика",
            "Категория": "Кофе",
            "Текущий остаток": 18.0,
            "Единица": "кг",
            "Минимальный остаток": 15.0
        },
        {
            "Наименование": "Молоко ультрапастеризованное 3.2%",
            "Категория": "Молочная продукция",
            "Текущий остаток": 12.0,  # Below minimum 25.0 -> Critical Alert!
            "Единица": "л",
            "Минимальный остаток": 25.0
        },
        {
            "Наименование": "Сироп Ваниль 1л",
            "Категория": "Сиропы и топпинги",
            "Текущий остаток": 4.0,  # Below minimum 5.0 -> Warning
            "Единица": "бут",
            "Минимальный остаток": 5.0
        },
        {
            "Наименование": "Сироп Карамель 1л",
            "Категория": "Сиропы и топпинги",
            "Текущий остаток": 7.0,
            "Единица": "бут",
            "Минимальный остаток": 5.0
        },
        {
            "Наименование": "Стаканы бумажные двухслойные 350мл (50 шт)",
            "Категория": "Упаковка и расходники",
            "Текущий остаток": 14.0,
            "Единица": "упак",
            "Минимальный остаток": 10.0
        },
        {
            "Наименование": "Крышки для стаканов 80мм (100 шт)",
            "Категория": "Упаковка и расходники",
            "Текущий остаток": 8.0,  # Below minimum 10.0 -> Warning
            "Единица": "упак",
            "Минимальный остаток": 10.0
        },
        {
            "Наименование": "Салфетки барные 24x24 (400 шт)",
            "Категория": "Упаковка и расходники",
            "Текущий остаток": 12.0,
            "Единица": "упак",
            "Минимальный остаток": 8.0
        },
        {
            "Наименование": "Трубочки биоразлагаемые (200 шт)",
            "Категория": "Упаковка и расходники",
            "Текущий остаток": 9.0,
            "Единица": "упак",
            "Минимальный остаток": 5.0
        },
        {
            "Наименование": "Чай листовой черный Ассам",
            "Категория": "Чай",
            "Текущий остаток": 3.5,
            "Единица": "кг",
            "Минимальный остаток": 2.0
        },
        {
            "Наименование": "Чай зеленый Сенча",
            "Категория": "Чай",
            "Текущий остаток": 2.5,
            "Единица": "кг",
            "Минимальный остаток": 2.0
        }
    ]
    df_inventory = pd.DataFrame(inventory)
    df_inventory.to_excel(DEMO_DATA_DIR / "legacy_inventory.xlsx", index=False)
    print(f"Created {DEMO_DATA_DIR / 'legacy_inventory.xlsx'} with {len(df_inventory)} rows.")

    # 4. supplier_price_list.xlsx
    supplier_prices = [
        # Coffee offers:
        {
            "Поставщик": "Aroma Direct",
            "Товар": "Кофе в зернах Espresso Blend 100% Арабика",
            "Фасовка": 1.0,
            "Единица": "кг",
            "Цена": 10350.0,
            "Мин. заказ": 20.0,
            "Доставка": 0.0,
            "Дата обновления": (today - timedelta(days=2)).strftime("%Y-%m-%d")
        },
        {
            "Поставщик": "BeanTrade Almaty",
            "Товар": "Кофе в зернах Espresso Blend 100% Арабика",
            "Фасовка": 1.0,
            "Единица": "кг",
            "Цена": 10800.0,
            "Мин. заказ": 15.0,
            "Доставка": 1500.0,
            "Дата обновления": (today - timedelta(days=4)).strftime("%Y-%m-%d")
        },
        {
            "Поставщик": "Coffee Roasters Hub",
            "Товар": "Кофе в зернах Espresso Blend 100% Арабика",
            "Фасовка": 1.0,
            "Единица": "кг",
            "Цена": 11500.0,
            "Мин. заказ": 10.0,
            "Доставка": 2500.0,
            "Дата обновления": (today - timedelta(days=6)).strftime("%Y-%m-%d")
        },
        {
            "Поставщик": "Premium Coffee Express",
            "Товар": "Кофе в зернах Espresso Blend 100% Арабика",
            "Фасовка": 1.0,
            "Единица": "кг",
            "Цена": 12200.0,
            "Мин. заказ": 5.0,
            "Доставка": 0.0,
            "Дата обновления": (today - timedelta(days=1)).strftime("%Y-%m-%d")
        },
        # Milk offers:
        {
            "Поставщик": "Qazaq Milk Line",
            "Товар": "Молоко ультрапастеризованное 3.2%",
            "Фасовка": 1.0,
            "Единица": "л",
            "Цена": 440.0,
            "Мин. заказ": 50.0,
            "Доставка": 0.0,
            "Дата обновления": (today - timedelta(days=3)).strftime("%Y-%m-%d")
        },
        {
            "Поставщик": "Almaty Dairy Group",
            "Товар": "Молоко ультрапастеризованное 3.2%",
            "Фасовка": 1.0,
            "Единица": "л",
            "Цена": 480.0,
            "Мин. заказ": 40.0,
            "Доставка": 1000.0,
            "Дата обновления": (today - timedelta(days=5)).strftime("%Y-%m-%d")
        },
        # Packaging:
        {
            "Поставщик": "Global Pack Almaty",
            "Товар": "Стаканы бумажные двухслойные 350мл (50 шт)",
            "Фасовка": 1.0,
            "Единица": "упак",
            "Цена": 1350.0,
            "Мин. заказ": 20.0,
            "Доставка": 1000.0,
            "Дата обновления": (today - timedelta(days=5)).strftime("%Y-%m-%d")
        },
        {
            "Поставщик": "EcoPack Kazakhstan",
            "Товар": "Стаканы бумажные двухслойные 350мл (50 шт)",
            "Фасовка": 1.0,
            "Единица": "упак",
            "Цена": 1450.0,
            "Мин. заказ": 10.0,
            "Доставка": 1800.0,
            "Дата обновления": (today - timedelta(days=7)).strftime("%Y-%m-%d")
        },
        # Syrups:
        {
            "Поставщик": "SweetSyrup Co",
            "Товар": "Сироп Ваниль 1л",
            "Фасовка": 1.0,
            "Единица": "бут",
            "Цена": 3650.0,
            "Мин. заказ": 4.0,
            "Доставка": 0.0,
            "Дата обновления": (today - timedelta(days=4)).strftime("%Y-%m-%d")
        },
        {
            "Поставщик": "Barista Pro Supplies",
            "Товар": "Сироп Ваниль 1л",
            "Фасовка": 1.0,
            "Единица": "бут",
            "Цена": 3900.0,
            "Мин. заказ": 4.0,
            "Доставка": 1200.0,
            "Дата обновления": (today - timedelta(days=8)).strftime("%Y-%m-%d")
        }
    ]
    df_supplier_prices = pd.DataFrame(supplier_prices)
    df_supplier_prices.to_excel(DEMO_DATA_DIR / "supplier_price_list.xlsx", index=False)
    print(f"Created {DEMO_DATA_DIR / 'supplier_price_list.xlsx'} with {len(df_supplier_prices)} rows.")

if __name__ == "__main__":
    generate_all_excel_files()
