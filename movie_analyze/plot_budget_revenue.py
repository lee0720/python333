CSV_PATH = Path(__file__).resolve().parent / "tmdb_5000_movies.csv"

df = pd.read_csv(CSV_PATH)
df = df[df["budget"] > 0]

plt.figure(figsize=(10, 6))
plt.scatter(df["budget"], df["revenue"], alpha=0.5)
plt.title("予算と興行収入の相関")
plt.tight_layout()

out = Path(__file__).resolve().parent / "budget_revenue_scatter.png"
plt.savefig(out, dpi=150)
print(f"保存しました: {out}")