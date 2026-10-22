import io
from datetime import date, datetime
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.models.models import (
    FinancialTransaction,
    Purchase,
    Product,
    Supplier,
    SupplierOffer,
    ImportBatch,
)
from backend.schemas.schemas import (
    ImportPreviewResult,
    ImportExecuteResult,
    ImportBatchResponse,
)


class ImportService:
    @staticmethod
    def _read_dataframe(file_bytes: bytes, filename: str) -> pd.DataFrame:
        lower_name = filename.lower()
        if lower_name.endswith(".csv"):
            try:
                df = pd.read_csv(io.BytesIO(file_bytes), encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(io.BytesIO(file_bytes), encoding="cp1251")
        elif lower_name.endswith(".xlsx") or lower_name.endswith(".xls"):
            df = pd.read_excel(io.BytesIO(file_bytes))
        else:
            raise ValueError("Поддерживаются только форматы .xlsx, .xls и .csv")
        return df

    @staticmethod
    def preview_file(file_bytes: bytes, filename: str, import_type: str) -> ImportPreviewResult:
        try:
            df = ImportService._read_dataframe(file_bytes, filename)
            df = df.dropna(how="all")  # Drop completely blank rows
            total_rows = len(df)
            headers = [str(c).strip() for c in df.columns]

            # Generate sample preview rows (up to 5 rows)
            sample_df = df.head(5).fillna("")
            sample_rows = sample_df.to_dict(orient="records")
            # Format datetime columns to str in sample
            for row in sample_rows:
                for k, v in row.items():
                    if isinstance(v, (datetime, date)):
                        row[k] = v.strftime("%Y-%m-%d")

            is_valid, msg = ImportService._validate_headers(headers, import_type)

            return ImportPreviewResult(
                file_name=filename,
                import_type=import_type,
                headers_detected=headers,
                sample_rows=sample_rows,
                total_rows=total_rows,
                is_valid=is_valid,
                message=msg,
            )
        except Exception as e:
            return ImportPreviewResult(
                file_name=filename,
                import_type=import_type,
                headers_detected=[],
                sample_rows=[],
                total_rows=0,
                is_valid=False,
                message=f"Ошибка чтения файла: {str(e)}",
            )

    @staticmethod
    def _validate_headers(headers: List[str], import_type: str) -> Tuple[bool, str]:
        headers_lower = [h.lower() for h in headers]
        if import_type == "finances":
            has_date = any(h in ["дата", "date", "transaction_date"] for h in headers_lower)
            has_desc = any(h in ["описание", "description", "назначение"] for h in headers_lower)
            has_amount = any(h in ["сумма", "amount", "стоимость"] for h in headers_lower)
            if not (has_date and has_desc and has_amount):
                return False, "Не найдены обязательные колонки: Дата, Описание, Сумма"
            return True, "Структура файла финансовых операций корректна"

        elif import_type == "purchases":
            has_date = any(h in ["дата закупки", "дата", "date", "purchase_date"] for h in headers_lower)
            has_prod = any(h in ["наименование товара", "товар", "product", "product_name"] for h in headers_lower)
            has_supplier = any(h in ["поставщик", "supplier", "supplier_name"] for h in headers_lower)
            has_price = any(h in ["цена за единицу", "цена", "unit_price", "price"] for h in headers_lower)
            if not (has_date and has_prod and has_supplier and has_price):
                return False, "Не найдены обязательные колонки: Дата, Товар, Поставщик, Цена"
            return True, "Структура файла истории закупок корректна"

        elif import_type == "inventory":
            has_prod = any(h in ["наименование", "наименование товара", "товар", "product"] for h in headers_lower)
            has_stock = any(h in ["текущий остаток", "остаток", "stock", "current_stock"] for h in headers_lower)
            if not (has_prod and has_stock):
                return False, "Не найдены обязательные колонки: Наименование, Текущий остаток"
            return True, "Структура файла остатков корректна"

        elif import_type == "supplier_prices":
            has_sup = any(h in ["поставщик", "supplier"] for h in headers_lower)
            has_prod = any(h in ["товар", "наименование", "product"] for h in headers_lower)
            has_price = any(h in ["цена", "price", "стоимость"] for h in headers_lower)
            if not (has_sup and has_prod and has_price):
                return False, "Не найдены обязательные колонки: Поставщик, Товар, Цена"
            return True, "Структура прайс-листа поставщиков корректна"

        return True, "Формат распознан"

    @staticmethod
    def execute_import(
        db: Session,
        file_bytes: bytes,
        filename: str,
        import_type: str,
        organization_id: int = 1,
    ) -> ImportExecuteResult:
        try:
            df = ImportService._read_dataframe(file_bytes, filename)
            df = df.dropna(how="all")
            total_rows = len(df)
            if total_rows == 0:
                return ImportExecuteResult(
                    batch_id=0,
                    file_name=filename,
                    import_type=import_type,
                    status="failed",
                    rows_total=0,
                    rows_imported=0,
                    rows_skipped=0,
                    message="Файл не содержит строк данных",
                    errors=["Файл пустой"],
                )

            batch = ImportBatch(
                organization_id=organization_id,
                file_name=filename,
                import_type=import_type,
                status="processing",
                rows_total=total_rows,
                rows_imported=0,
                rows_skipped=0,
                created_at=datetime.utcnow(),
            )
            db.add(batch)
            db.flush()

            imported_count = 0
            skipped_count = 0
            errors: List[str] = []

            # Normalize column names mapping
            col_map = {str(c).strip().lower(): c for c in df.columns}

            def get_val(row, aliases, default=None):
                for alias in aliases:
                    if alias in col_map:
                        val = row[col_map[alias]]
                        if pd.notna(val):
                            return val
                return default

            if import_type == "finances":
                for idx, row in df.iterrows():
                    try:
                        raw_date = get_val(row, ["дата", "date", "transaction_date"])
                        desc = get_val(row, ["описание", "description", "назначение"])
                        amount = get_val(row, ["сумма", "amount", "стоимость"])
                        t_type = get_val(row, ["тип", "type"], "Расход")
                        category = get_val(row, ["категория", "category"])

                        if not raw_date or not desc or amount is None:
                            skipped_count += 1
                            continue

                        # Parse date
                        if isinstance(raw_date, (datetime, date)):
                            parsed_date = raw_date if isinstance(raw_date, date) else raw_date.date()
                        else:
                            parsed_date = pd.to_datetime(str(raw_date)).date()

                        amt = float(amount)
                        is_income = str(t_type).strip().lower() in ["доход", "income", "выручка"]
                        trans_type = "income" if is_income else "expense"

                        if not category or pd.isna(category):
                            # Default category inference
                            desc_lower = str(desc).lower()
                            if "кофе" in desc_lower:
                                category = "Закупка кофе"
                            elif any(w in desc_lower for w in ["молоко", "сироп", "сливки"]):
                                category = "Закупка молока и продуктов"
                            elif any(w in desc_lower for w in ["стакан", "крышк", "салфетк", "упаковк"]):
                                category = "Расходные материалы"
                            elif "аренд" in desc_lower:
                                category = "Аренда помещения"
                            elif "зарплат" in desc_lower or "зп" in desc_lower:
                                category = "Фонд оплаты труда"
                            elif "выручк" in desc_lower or "касс" in desc_lower:
                                category = "Выручка / Продажи"
                            else:
                                category = "Прочие расходы"

                        # Deduplication check
                        exists = db.query(FinancialTransaction).filter(
                            FinancialTransaction.organization_id == organization_id,
                            FinancialTransaction.transaction_date == parsed_date,
                            FinancialTransaction.description == str(desc).strip(),
                            FinancialTransaction.amount == abs(amt),
                        ).first()

                        if exists:
                            skipped_count += 1
                            continue

                        tx = FinancialTransaction(
                            organization_id=organization_id,
                            transaction_date=parsed_date,
                            description=str(desc).strip(),
                            category=str(category).strip(),
                            amount=abs(amt),
                            transaction_type=trans_type,
                            source=f"import:{filename}",
                            import_batch_id=batch.id,
                            created_at=datetime.utcnow(),
                        )
                        db.add(tx)
                        imported_count += 1
                    except Exception as err:
                        skipped_count += 1
                        errors.append(f"Строка {idx + 1}: {str(err)}")

            elif import_type == "purchases":
                for idx, row in df.iterrows():
                    try:
                        raw_date = get_val(row, ["дата закупки", "дата", "date", "purchase_date"])
                        prod_name = get_val(row, ["наименование товара", "товар", "product", "product_name"])
                        sup_name = get_val(row, ["поставщик", "supplier", "supplier_name"])
                        qty = get_val(row, ["количество", "qty", "quantity"], 1.0)
                        unit = get_val(row, ["единица", "ед. изм.", "unit"], "шт")
                        u_price = get_val(row, ["цена за единицу", "цена", "unit_price", "price"])
                        tot_price = get_val(row, ["итоговая сумма", "сумма", "total", "total_price"])

                        if not raw_date or not prod_name or not sup_name or u_price is None:
                            skipped_count += 1
                            continue

                        if isinstance(raw_date, (datetime, date)):
                            parsed_date = raw_date if isinstance(raw_date, date) else raw_date.date()
                        else:
                            parsed_date = pd.to_datetime(str(raw_date)).date()

                        qty = float(qty)
                        u_price = float(u_price)
                        tot_price = float(tot_price) if tot_price is not None else (qty * u_price)

                        # Find or create Product
                        product = db.query(Product).filter(
                            Product.organization_id == organization_id,
                            Product.name.ilike(str(prod_name).strip()),
                        ).first()
                        if not product:
                            product = Product(
                                organization_id=organization_id,
                                name=str(prod_name).strip(),
                                category="Прочее",
                                unit=str(unit).strip(),
                                current_stock=qty,
                                minimum_stock=5.0,
                            )
                            db.add(product)
                            db.flush()

                        # Find or create Supplier
                        supplier = db.query(Supplier).filter(
                            Supplier.organization_id == organization_id,
                            Supplier.name.ilike(str(sup_name).strip()),
                        ).first()
                        if not supplier:
                            supplier = Supplier(
                                organization_id=organization_id,
                                name=str(sup_name).strip(),
                                source_type="imported",
                                is_demo=False,
                            )
                            db.add(supplier)
                            db.flush()

                        # Deduplication check
                        exists = db.query(Purchase).filter(
                            Purchase.organization_id == organization_id,
                            Purchase.product_id == product.id,
                            Purchase.supplier_id == supplier.id,
                            Purchase.purchase_date == parsed_date,
                            Purchase.quantity == qty,
                            Purchase.unit_price == u_price,
                        ).first()

                        if exists:
                            skipped_count += 1
                            continue

                        purchase = Purchase(
                            organization_id=organization_id,
                            product_id=product.id,
                            supplier_id=supplier.id,
                            purchase_date=parsed_date,
                            quantity=qty,
                            unit=str(unit).strip(),
                            unit_price=u_price,
                            total_price=tot_price,
                            source=f"import:{filename}",
                            import_batch_id=batch.id,
                            created_at=datetime.utcnow(),
                        )
                        db.add(purchase)
                        imported_count += 1
                    except Exception as err:
                        skipped_count += 1
                        errors.append(f"Строка {idx + 1}: {str(err)}")

            elif import_type == "inventory":
                for idx, row in df.iterrows():
                    try:
                        prod_name = get_val(row, ["наименование", "наименование товара", "товар", "product"])
                        category = get_val(row, ["категория", "category"], "Склад")
                        stock = get_val(row, ["текущий остаток", "остаток", "stock", "current_stock"])
                        unit = get_val(row, ["единица", "unit"], "шт")
                        min_stock = get_val(row, ["минимальный остаток", "min_stock", "minimum_stock"], 5.0)

                        if not prod_name or stock is None:
                            skipped_count += 1
                            continue

                        product = db.query(Product).filter(
                            Product.organization_id == organization_id,
                            Product.name.ilike(str(prod_name).strip()),
                        ).first()

                        if product:
                            product.current_stock = float(stock)
                            product.minimum_stock = float(min_stock)
                            if category:
                                product.category = str(category).strip()
                            if unit:
                                product.unit = str(unit).strip()
                        else:
                            product = Product(
                                organization_id=organization_id,
                                name=str(prod_name).strip(),
                                category=str(category).strip(),
                                unit=str(unit).strip(),
                                current_stock=float(stock),
                                minimum_stock=float(min_stock),
                            )
                            db.add(product)

                        imported_count += 1
                    except Exception as err:
                        skipped_count += 1
                        errors.append(f"Строка {idx + 1}: {str(err)}")

            elif import_type == "supplier_prices":
                for idx, row in df.iterrows():
                    try:
                        sup_name = get_val(row, ["поставщик", "supplier"])
                        prod_name = get_val(row, ["товар", "наименование", "product"])
                        price = get_val(row, ["цена", "price", "стоимость"])
                        unit = get_val(row, ["единица", "unit"], "шт")
                        pkg_qty = get_val(row, ["фасовка", "package_quantity"], 1.0)
                        min_order = get_val(row, ["мин. заказ", "minimum_order"], 1.0)
                        delivery = get_val(row, ["доставка", "delivery_cost"], 0.0)

                        if not sup_name or not prod_name or price is None:
                            skipped_count += 1
                            continue

                        product = db.query(Product).filter(
                            Product.organization_id == organization_id,
                            Product.name.ilike(str(prod_name).strip()),
                        ).first()
                        if not product:
                            product = Product(
                                organization_id=organization_id,
                                name=str(prod_name).strip(),
                                category="Каталог",
                                unit=str(unit).strip(),
                                current_stock=0.0,
                                minimum_stock=5.0,
                            )
                            db.add(product)
                            db.flush()

                        supplier = db.query(Supplier).filter(
                            Supplier.organization_id == organization_id,
                            Supplier.name.ilike(str(sup_name).strip()),
                        ).first()
                        if not supplier:
                            supplier = Supplier(
                                organization_id=organization_id,
                                name=str(sup_name).strip(),
                                delivery_cost=float(delivery or 0),
                                minimum_order_amount=0.0,
                                source_type="price_list",
                                is_demo=False,
                            )
                            db.add(supplier)
                            db.flush()

                        offer = db.query(SupplierOffer).filter(
                            SupplierOffer.organization_id == organization_id,
                            SupplierOffer.product_id == product.id,
                            SupplierOffer.supplier_id == supplier.id,
                        ).first()

                        if offer:
                            offer.offered_price = float(price)
                            offer.unit = str(unit).strip()
                            offer.package_quantity = float(pkg_qty or 1.0)
                            offer.minimum_order_quantity = float(min_order or 1.0)
                            offer.delivery_cost = float(delivery or 0.0)
                            offer.updated_at = datetime.utcnow()
                        else:
                            offer = SupplierOffer(
                                organization_id=organization_id,
                                product_id=product.id,
                                supplier_id=supplier.id,
                                offered_price=float(price),
                                unit=str(unit).strip(),
                                package_quantity=float(pkg_qty or 1.0),
                                minimum_order_quantity=float(min_order or 1.0),
                                delivery_cost=float(delivery or 0.0),
                                updated_at=datetime.utcnow(),
                                source_type="import",
                                is_demo=False,
                            )
                            db.add(offer)

                        imported_count += 1
                    except Exception as err:
                        skipped_count += 1
                        errors.append(f"Строка {idx + 1}: {str(err)}")

            batch.rows_imported = imported_count
            batch.rows_skipped = skipped_count
            batch.status = "success" if errors == [] else ("partial" if imported_count > 0 else "failed")
            if errors:
                batch.error_summary = "; ".join(errors[:5])

            db.commit()

            return ImportExecuteResult(
                batch_id=batch.id,
                file_name=filename,
                import_type=import_type,
                status=batch.status,
                rows_total=total_rows,
                rows_imported=imported_count,
                rows_skipped=skipped_count,
                message=f"Импорт завершен: {imported_count} строк успешно сохранено в БД, {skipped_count} пропущено",
                errors=errors[:10],
            )

        except Exception as e:
            db.rollback()
            return ImportExecuteResult(
                batch_id=0,
                file_name=filename,
                import_type=import_type,
                status="failed",
                rows_total=0,
                rows_imported=0,
                rows_skipped=0,
                message=f"Критическая ошибка обработки файла: {str(e)}",
                errors=[str(e)],
            )

    @staticmethod
    def generate_template(import_type: str) -> bytes:
        if import_type == "finances":
            data = [
                {"Дата": "2026-10-15", "Описание": "Выручка за смену (бар)", "Сумма": 125000, "Тип": "Доход", "Категория": "Выручка / Продажи"},
                {"Дата": "2026-10-15", "Описание": "Закупка молока у поставщика", "Сумма": 21000, "Тип": "Расход", "Категория": "Закупка молока и продуктов"},
            ]
            sheet = "Финансовые операции"
        elif import_type == "purchases":
            data = [
                {"Дата закупки": "2026-10-15", "Наименование товара": "Кофе Espresso Blend", "Поставщик": "КофеОпт Астана", "Количество": 10, "Единица": "кг", "Цена за единицу": 8500, "Итоговая сумма": 85000},
            ]
            sheet = "История закупок"
        elif import_type == "inventory":
            data = [
                {"Наименование": "Кофе Espresso Blend", "Категория": "Кофе", "Текущий остаток": 18.5, "Единица": "кг", "Минимальный остаток": 10.0},
                {"Наименование": "Молоко 3.2%", "Категория": "Молочные продукты", "Текущий остаток": 25.0, "Единица": "л", "Минимальный остаток": 20.0},
            ]
            sheet = "Остатки склада"
        elif import_type == "supplier_prices":
            data = [
                {"Поставщик": "КофеОпт Астана", "Товар": "Кофе Espresso Blend", "Цена": 8200, "Единица": "кг", "Фасовка": 1, "Мин. заказ": 5, "Доставка": 2000},
                {"Поставщик": "Tasty Coffee B2B", "Товар": "Кофе Espresso Blend", "Цена": 7900, "Единица": "кг", "Фасовка": 1, "Мин. заказ": 10, "Доставка": 0},
            ]
            sheet = "Прайс-листы поставщиков"
        else:
            raise ValueError(f"Неизвестный тип шаблона: {import_type}")

        df = pd.DataFrame(data)
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=sheet)
        out.seek(0)
        return out.getvalue()

    @staticmethod
    def get_batches(db: Session, organization_id: int = 1) -> List[ImportBatchResponse]:
        batches = db.query(ImportBatch).filter(
            ImportBatch.organization_id == organization_id
        ).order_by(desc(ImportBatch.created_at)).all()
        return [ImportBatchResponse.model_validate(b) for b in batches]

