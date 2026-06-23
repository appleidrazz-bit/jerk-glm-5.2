"""Unit tests for the funding feed generator."""
from app.services.feed import FundingFeed, _gen_coins


def test_feed_generates_requested_count():
    feed = FundingFeed(count=520)
    snap = feed.snapshot()
    assert len(snap) == 520


def test_every_row_has_full_cell_coverage():
    from app.core.exchanges import EXCHANGE_IDS
    feed = FundingFeed(count=10)
    for row in feed.snapshot():
        for ex in EXCHANGE_IDS:
            assert ex in row.cells, f"{row.symbol} missing {ex}"


def test_best_long_is_min_and_best_short_is_max():
    feed = FundingFeed(count=25)
    for row in feed.snapshot():
        rates = {ex: c.rate or 0 for ex, c in row.cells.items()}
        assert rates[row.best_long] == min(rates.values())
        assert rates[row.best_short] == max(rates.values())


def test_spread_is_non_negative():
    feed = FundingFeed(count=40)
    for row in feed.snapshot():
        assert row.spread_pct >= 0


def test_coin_generation_is_stable():
    coins1 = _gen_coins(100)
    coins2 = _gen_coins(100)
    assert [c[0] for c in coins1] == [c[0] for c in coins2]
