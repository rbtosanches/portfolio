import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta


class PickupSalesGenerator:

    def __init__(
        self,
        total_sales=1000,
        error_rate=0.05,
        seed=42
    ):

        random.seed(seed)
        np.random.seed(seed)

        self.total_sales = total_sales
        self.error_rate = error_rate

        self.end_date = datetime.today()
        self.start_date = self.end_date - timedelta(days=365 * 4)

        # Produtos
        self.products = {
            "X1": 200000,
            "X2": 220000,
            "X3": 280000
        }

        # Vendedores
        self.salespeople = [
            "V1",
            "V2",
            "V3",
            "V4",
            "V5"
        ]

        # Meta mensal
        self.sales_targets = {
            "V1": 1500000,
            "V2": 1700000,
            "V3": 1900000,
            "V4": 2100000,
            "V5": 2300000
        }

        # Cidades
        self.cities = [
            "Cuiabá",
            "Várzea Grande",
            "Diamantino",
            "Nova Mutum"
        ]

        self.city_weights = [
            0.42,
            0.38,
            0.10,
            0.10
        ]

        self.installments = [1, 2, 3]

        self.discounts = [
            0,
            0.02,
            0.05
        ]

        self.gifts = {
            "K0": 0,
            "K1": 3000,
            "K2": 4500,
            "K3": 2000
        }

        # Frequência recompra
        self.repurchase_intervals = [
            365,
            730,
            912
        ]

        # Probabilidade de churn
        self.churn_rate = 0.15

        # Sazonalidade
        self.seasonality = {
            1: 1.0,
            2: 0.7,
            3: 1.3,
            4: 1.0,
            5: 1.0,
            6: 1.2,
            7: 0.75,
            8: 1.0,
            9: 1.25,
            10: 1.0,
            11: 1.1,
            12: 1.5
        }

    def create_customers(self):

        customer_count = int(
            self.total_sales * 0.5
        )

        customers = []

        for i in range(
            1,
            customer_count + 1
        ):

            customers.append({

                "customer_id":
                    f"C{i:03d}",

                "city":
                    np.random.choice(
                        self.cities,
                        p=self.city_weights
                    ),

                "repurchase_days":
                    random.choice(
                        self.repurchase_intervals
                    )
            })

        return customers

    def generate_weighted_date(self):

        while True:

            random_days = random.randint(
                0,
                365 * 4
            )

            date = (
                self.start_date +
                timedelta(
                    days=random_days
                )
            )

            factor = self.seasonality[
                date.month
            ]

            if random.random() <= (
                factor / 1.5
            ):

                return date

    def generate_gifts(self):

        first_gift = random.choice(
            list(
                self.gifts.keys()
            )
        )

        # Regra K0
        if first_gift == "K0":

            return "K0", 0

        qty = random.randint(
            1,
            3
        )

        options = [
            "K1",
            "K2",
            "K3"
        ]

        selected = random.sample(
            options,
            qty
        )

        total_cost = sum(
            self.gifts[g]
            for g in selected
        )

        return (
            ",".join(selected),
            total_cost
        )

    def generate_sales(self):

        customers = (
            self.create_customers()
        )

        sales = []

        for customer in customers:

            purchase_date = (
                self.generate_weighted_date()
            )

            while (
                purchase_date <=
                self.end_date
            ):

                # churn
                if random.random() < (
                    self.churn_rate
                ):
                    break

                model = random.choice(
                    list(
                        self.products.keys()
                    )
                )

                list_price = (
                    self.products[
                        model
                    ]
                )

                salesperson = (
                    random.choice(
                        self.salespeople
                    )
                )

                discount = (
                    random.choice(
                        self.discounts
                    )
                )

                discount_value = (
                    list_price *
                    discount
                )

                gifts, gift_cost = (
                    self.generate_gifts()
                )

                installments = (
                    random.choice(
                        self.installments
                    )
                )

                final_price = (
                    list_price -
                    discount_value
                )

                margin = (
                    final_price -
                    gift_cost
                )

                sales.append({

                    "sale_date":
                        purchase_date.date(),

                    "year":
                        purchase_date.year,

                    "month":
                        purchase_date.month,

                    "customer_id":
                        customer[
                            "customer_id"
                        ],

                    "city":
                        customer[
                            "city"
                        ],

                    "model":
                        model,

                    "list_price":
                        list_price,

                    "salesperson":
                        salesperson,

                    "sales_target":
                        self.sales_targets[
                            salesperson
                        ],

                    "installments":
                        installments,

                    "discount_pct":
                        discount,

                    "discount_value":
                        discount_value,

                    "gifts":
                        gifts,

                    "gift_cost":
                        gift_cost,

                    "gross_revenue":
                        final_price,

                    "net_margin":
                        margin
                })

                purchase_date += timedelta(
                    days=customer[
                        "repurchase_days"
                    ]
                )

        df = pd.DataFrame(
            sales
        )

        # Ajuste para quantidade exata
        if len(df) > self.total_sales:

            df = df.sample(
                self.total_sales,
                random_state=42
            )

        elif len(df) < self.total_sales:

            extra = df.sample(
                self.total_sales - len(df),
                replace=True,
                random_state=42
            )

            df = pd.concat(
                [df, extra]
            )

        df = df.reset_index(
            drop=True
        )

        return df

    def inject_errors(
        self,
        df
    ):

        error_rows = int(
            len(df) *
            self.error_rate
        )

        indexes = random.sample(
            list(df.index),
            error_rows
        )

        error_types = [

            ("sale_date", None),

            ("customer_id", None),

            ("city", None),

            ("model", None),

            ("gifts", None),

            ("list_price", 0),

            ("list_price", 999999),

            ("installments", "texto"),

            ("discount_pct", 0.99)
        ]

        for idx in indexes:

            col, value = random.choice(
                error_types
            )

            df.at[
                idx,
                col
            ] = value

        return df


if __name__ == "__main__":

    generator = (
        PickupSalesGenerator(
            total_sales=1000,
            error_rate=0.05
        )
    )

    df = generator.generate_sales()

    df = generator.inject_errors(
        df
    )

    file_name = (
        "pickup_sales_dataset.csv"
    )

    df.to_csv(
        file_name,
        index=False,
        sep=";"
    )

    print(
        f"Arquivo gerado: {file_name}"
    )

    print(
        f"Registros: {len(df)}"
    )

    print(
        df.head(10)
    )