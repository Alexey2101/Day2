import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


CHARTS_DIR = "charts"


def format_tenge(value: int | float) -> str:
    """Форматирует сумму в тенге с разделителем разрядов пробелом."""
    return f"{int(value):,}".replace(",", " ") + " тенге"


def show_if_interactive() -> None:
    """Показывает график, если используется интерактивный бэкенд matplotlib."""
    if plt.get_backend().lower() != "agg":
        plt.show()


def load_sales(db_path: str = "shop.db") -> pd.DataFrame:
    """Загружает таблицу sales из базы данных SQLite в DataFrame."""
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query("SELECT * FROM sales", conn)
    finally:
        conn.close()
    return df


def save_bar_chart(
    series: pd.Series,
    title: str,
    xlabel: str,
    ylabel: str,
    output_path: str,
    color: str = "#2b6cb0",
) -> None:
    """Строит столбчатую диаграмму, сохраняет её в PNG и отображает на экране."""
    sorted_series = series.sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(12, 6))
    sorted_series.plot(kind="bar", ax=ax, color=color, edgecolor="black", alpha=0.88)

    ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.ticklabel_format(style="plain", axis="y")
    ax.grid(axis="y", linestyle="--", alpha=0.45)
    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    show_if_interactive()
    plt.close(fig)


def save_category_pie_chart(categories: pd.Series, output_path: str) -> None:
    """Строит круговую диаграмму распределения выручки по категориям."""
    sorted_categories = categories.sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(8, 8))
    sorted_categories.plot(
        kind="pie",
        ax=ax,
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.8,
        wedgeprops={"edgecolor": "white", "linewidth": 1.2},
    )

    ax.set_title("Доля категорий в общей выручке", fontsize=14, fontweight="bold", pad=12)
    ax.set_ylabel("")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    show_if_interactive()
    plt.close(fig)


def main() -> None:
    os.makedirs(CHARTS_DIR, exist_ok=True)

    df = load_sales("shop.db")
    print("=== Первые 5 записей таблицы sales ===")
    print(df.head())

    df["revenue"] = df["price"] * df["quantity"]
    print("\n=== Выручка по каждой продаже ===")
    print(df[["product", "revenue"]].to_string(index=False))

    total_revenue = int(df["revenue"].sum())
    print(f"\nОбщая выручка магазина: {format_tenge(total_revenue)}")

    total_quantity = int(df["quantity"].sum())
    print(f"Общее количество проданных единиц: {total_quantity} шт.")

    products_revenue = df.groupby("product")["revenue"].sum()
    print("\n=== Выручка по товарам ===")
    print(products_revenue.sort_values(ascending=False))

    top3_products = products_revenue.sort_values(ascending=False).head(3)
    print("\nТри товара с максимальной выручкой:")
    for rank, (product_name, rev) in enumerate(top3_products.items(), start=1):
        share = rev / total_revenue * 100
        print(f"  {rank}. {product_name}: {format_tenge(rev)} ({share:.1f}%)")

    categories_revenue = df.groupby("category")["revenue"].sum()
    products_quantity = df.groupby("product")["quantity"].sum()

    revenue_chart_path = os.path.join(CHARTS_DIR, "revenue_by_product.png")
    save_bar_chart(
        products_revenue,
        title="Выручка по товарам",
        xlabel="Товар",
        ylabel="Выручка, тенге",
        output_path=revenue_chart_path,
        color="#2b6cb0",
    )

    category_chart_path = os.path.join(CHARTS_DIR, "revenue_by_category.png")
    save_category_pie_chart(categories_revenue, output_path=category_chart_path)

    quantity_chart_path = os.path.join(CHARTS_DIR, "quantity_by_product.png")
    save_bar_chart(
        products_quantity,
        title="Количество проданных товаров",
        xlabel="Товар",
        ylabel="Количество, шт.",
        output_path=quantity_chart_path,
        color="#2f855a",
    )

    top_category = categories_revenue.idxmax()
    top_category_share = categories_revenue.max() / total_revenue * 100
    top3_share = top3_products.sum() / total_revenue * 100
    top_qty_product = products_quantity.idxmax()
    top_qty_value = int(products_quantity.max())
    top_rev_product = top3_products.index[0]

    print("\n=== Выводы по полученным результатам ===")
    print(
        f"1. Лидер по выручке — категория «{top_category}» ({top_category_share:.1f}% общей выручки, "
        f"{format_tenge(categories_revenue.max())})."
    )
    print(
        f"2. Высокая концентрация продаж: три товара-лидера ({', '.join(top3_products.index)}) "
        f"приносят {top3_share:.1f}% всей выручки магазина."
    )
    print(
        f"3. Лидерство по штукам и по деньгам не совпадает: больше всего единиц продано у товара "
        f"«{top_qty_product}» ({top_qty_value} шт.), тогда как максимальную выручку дал товар "
        f"«{top_rev_product}» ({format_tenge(top3_products.iloc[0])})."
    )
    print(f"\nГрафики сохранены в папку '{CHARTS_DIR}':")
    print(f" - {revenue_chart_path}")
    print(f" - {category_chart_path}")
    print(f" - {quantity_chart_path}")


if __name__ == "__main__":
    main()
