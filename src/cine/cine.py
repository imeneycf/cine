import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import altair as alt

    return mo, pl


@app.cell
def _(mo):
    mo.md("""
    # Analysis of IMDb films and series
    Exploration of several hundred thousand titles: genres, runtimes, decades, top-rated series,
    plus a mini recommendation explorer.
    """)
    return


@app.cell
def _(pl):
    _basics = pl.scan_csv(
        "data/title.basics.tsv",
        separator="\t",
        null_values="\\N",
        quote_char=None,
        infer_schema=False,
    )
    _ratings = pl.scan_csv(
        "data/title.ratings.tsv",
        separator="\t",
        null_values="\\N",
        quote_char=None,
    )

    titles = (
        _basics
        .filter(pl.col("titleType").is_in(["movie", "tvSeries", "tvMiniSeries"]))
        .join(_ratings, on="tconst", how="inner")
        .with_columns(
            pl.col("startYear").cast(pl.Int32, strict=False),
            pl.col("endYear").cast(pl.Int32, strict=False),
            pl.col("runtimeMinutes").cast(pl.Int32, strict=False),
            pl.col("isAdult").cast(pl.Int8, strict=False),
            pl.col("genres").str.split(","),
        )
        .filter((pl.col("isAdult") == 0) & (pl.col("numVotes") >= 100))
        .select(
            "tconst", "titleType", "primaryTitle", "startYear", "endYear",
            "runtimeMinutes", "genres", "averageRating", "numVotes",
        )
        .collect()
    )
    titles
    return (titles,)


@app.cell
def _(mo, pl, titles):
    # Preview

    mo.hstack([
        mo.stat(label="Titres", value=f"{titles.height:,}".replace(",", " ")),
        mo.stat(label="Films", value=f"{titles.filter(pl.col('titleType') == 'movie').height:,}".replace(",", " ")),
        mo.stat(label="Séries", value=f"{titles.filter(pl.col('titleType') != 'movie').height:,}".replace(",", " ")),
        mo.stat(label="Note moyenne", value=f"{titles['averageRating'].mean():.2f}"),
    ])
    return


@app.cell
def _(titles):
    genres_df = (
        titles
        .explode("genres")
        .rename({"genres": "genre"})
        .drop_nulls("genre")
    )
    genres_df.head()
    return


@app.cell
def _(mo):
    min_votes_genre = mo.ui.slider(1_000, 200_000, step=1_000, value=25_000, label="Votes minimum", show_value=True)
    min_votes_genre
    return


if __name__ == "__main__":
    app.run()
