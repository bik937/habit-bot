import io
from datetime import date, timedelta

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
import numpy as np

import database as db

plt.rcParams["font.family"] = "DejaVu Sans"


async def generate_heatmap(days: int = 30) -> io.BytesIO | None:
    end = date.today()
    start = end - timedelta(days=days - 1)

    habits = await db.get_habits()
    if not habits:
        return None

    logs = await db.get_logs_range(str(start), str(end))
    log_dict: dict[tuple[int, str], bool] = {}
    for row in logs:
        if row["date"]:
            log_dict[(row["id"], row["date"])] = bool(row["done"])

    dates = [(start + timedelta(days=i)).isoformat() for i in range(days)]

    matrix = np.array([
        [1 if log_dict.get((h["id"], d), False) else 0 for d in dates]
        for h in habits
    ])
    labels = [h["name"] for h in habits]

    fig_h = max(4, len(habits) * 0.55 + 1.5)
    fig_w = max(10, days * 0.38)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    cmap = ListedColormap(["#ffcccc", "#90ee90"])
    ax.imshow(matrix, cmap=cmap, aspect="auto", vmin=0, vmax=1)

    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=9)

    step = max(1, days // 10)
    tick_positions = list(range(0, days, step))
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(
        [dates[i][5:] for i in tick_positions], rotation=45, ha="right", fontsize=8
    )

    ax.set_title(f"Тепловая карта привычек — {days} дней", fontsize=12, pad=10)

    red_patch = mpatches.Patch(color="#ffcccc", label="Не выполнено")
    green_patch = mpatches.Patch(color="#90ee90", label="Выполнено")
    ax.legend(handles=[green_patch, red_patch], loc="upper right")

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return buf


async def generate_trend(days: int = 30) -> io.BytesIO | None:
    end = date.today()
    start = end - timedelta(days=days - 1)

    habits = await db.get_habits()
    if not habits:
        return None

    logs = await db.get_logs_range(str(start), str(end))
    log_dict: dict[tuple[int, str], bool] = {}
    for row in logs:
        if row["date"]:
            log_dict[(row["id"], row["date"])] = bool(row["done"])

    date_list = [start + timedelta(days=i) for i in range(days)]
    pcts = [
        round(
            sum(1 for h in habits if log_dict.get((h["id"], d.isoformat()), False))
            / len(habits)
            * 100
        )
        for d in date_list
    ]

    fig, ax = plt.subplots(figsize=(12, 5))
    x = range(len(date_list))

    ax.plot(x, pcts, color="#4CAF50", linewidth=2, marker="o", markersize=4)
    ax.fill_between(x, pcts, alpha=0.15, color="#4CAF50")
    ax.axhline(y=80, color="orange", linestyle="--", alpha=0.6, label="Цель 80%")

    step = max(1, days // 10)
    ax.set_xticks(range(0, len(date_list), step))
    ax.set_xticklabels(
        [date_list[i].strftime("%d.%m") for i in range(0, len(date_list), step)],
        rotation=45,
    )
    ax.set_ylim(0, 110)
    ax.set_ylabel("% выполнения", fontsize=11)

    avg = sum(pcts) / len(pcts) if pcts else 0
    ax.set_title(f"Прогресс за {days} дней  |  Среднее: {avg:.0f}%", fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return buf


async def generate_top_habits(days: int = 30) -> io.BytesIO | None:
    end = date.today()
    start = end - timedelta(days=days - 1)

    habits = await db.get_habits()
    if not habits:
        return None

    logs = await db.get_logs_range(str(start), str(end))
    log_dict: dict[tuple[int, str], bool] = {}
    for row in logs:
        if row["date"]:
            log_dict[(row["id"], row["date"])] = bool(row["done"])

    dates = [(start + timedelta(days=i)).isoformat() for i in range(days)]
    habit_pcts = sorted(
        [
            (
                h["name"],
                round(
                    sum(1 for d in dates if log_dict.get((h["id"], d), False))
                    / days
                    * 100
                ),
            )
            for h in habits
        ],
        key=lambda x: x[1],
    )

    names = [h[0] for h in habit_pcts]
    pcts = [h[1] for h in habit_pcts]
    colors = [
        "#90ee90" if p >= 70 else "#ffcc44" if p >= 40 else "#ffaaaa"
        for p in pcts
    ]

    fig, ax = plt.subplots(figsize=(10, max(4, len(names) * 0.5 + 1.5)))
    bars = ax.barh(names, pcts, color=colors, edgecolor="white", height=0.6)

    for bar, pct in zip(bars, pcts):
        ax.text(
            bar.get_width() + 1,
            bar.get_y() + bar.get_height() / 2,
            f"{pct}%",
            va="center",
            fontsize=9,
        )

    ax.set_xlim(0, 115)
    ax.set_xlabel("% выполнения", fontsize=11)
    ax.set_title(f"Рейтинг привычек — {days} дней", fontsize=12)
    ax.axvline(x=80, color="orange", linestyle="--", alpha=0.6, label="Цель 80%")
    ax.legend()
    ax.grid(True, axis="x", alpha=0.3)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return buf
