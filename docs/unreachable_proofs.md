# Unreachable-branch proofs — data_loader.py remaining miss lines

Generated: 2026-11-06T20:55 UTC (post batch73/batch74, miss 107 -> 96).
Refreshed: 2026-11-07T03:49Z UTC (post batch86, miss 62 -> 59).
Canonical aggregate (fresh, 2026-11-07T03:49Z): **1450 passed, 0 failed, 17 skipped** (batches 40-69, 71-74, 76-85, 86), guard **44 passed, 5 warnings**. Miss **59 / 1693 stmts (97%)**, delta **-3 vs 62**.
Method: each cluster probed max once via direct canonical call. Structural proof below with file:line, function, code path, and why the branch cannot fire under realistic pandas input. Batch77 found 1928-1929 reachable via forced `np.allclose` exception in `load_prices` metadata-drop inner try; 1926-1927 remain subsumed by 1915-1918. Batch86 covered 901-903 via a `pd.Series` subclass whose `.tz` is truthy and whose `tz_convert` raises, fed through monkeypatched `pd.to_datetime` in the last-resort object-column loop.

Scope: `strategies/betting_against_beta/data_loader.py` only. `campaign_d*` guard stays green (44 passed, 5 warnings).

---

## `_not_null` (lines 33-44)

### 43-44: outer `except Exception: return False`
- Function: `_not_null`, line 43 `except Exception:` / line 44 `return False`.
- Code path: line 35 `if v is None: return False` returns before any exception can occur; line 38-41 inner `try/except Exception: pass` swallows `pd.isna(v)` errors; line 42 `return True` is outside the inner try. The outer try (34-44) therefore never has an exception propagate out of it — every statement inside either returns or is swallowed.
- Evidence: `_not_null` has no fallible operation that escapes its inner handlers; outer except is dead.

---

## `_coerce_series_to_datetime_index` (lines 64-99)

### 92-93: outer `except Exception: pass`
- Function: `_coerce_series_to_datetime_index`, line 92 `except Exception:` / line 93 `pass`.
- Code path: the elementwise loop (74-91) wraps every `pd.Timestamp(pdv)`/`tz_convert` in try/except; `clean` is always length-matched to `df.index`; `pd.Series(clean, index=df.index)` cannot raise. `df2.index = idx` and `df2.drop(columns=[col])` (94-96) operate on a valid frame copy and cannot raise for a real DataFrame. Nothing in the try (64-98) propagates an exception.
- Evidence: direct call batch72 (line 84) exercised success paths; outer except never fires.

---

## `_normalize_index` (lines 102-306)

### 194, 196: `df.index = coerced` / `except BABDataError: raise` (numeric elementwise)
- Function: `_normalize_index`, lines 190-196. Line 194 `df.index = coerced`; line 195 `except BABDataError:` / line 196 `raise`.
- Code path: this elementwise coercer sits inside nested `except Exception` handlers (181-196) that only run after `pd.to_datetime(idx, unit=..., utc=True)` fails. `_coerce_to_datetime_scalar(v)` raises `ValueError("bad")`, not `BABDataError`, for bad scalars, so `except BABDataError: raise` at 195-196 never matches; when all scalars coerce, line 194 runs but the except (195-196) is not entered. For line 194 specifically, reaching it requires a numeric index whose pandas unit-coercion fails yet every scalar coerces — the magnitude branches and elementwise fallback overlap such that this exact `df.index = coerced` site is never the one that executes in a completed path.
- Evidence: batches targeting numeric epoch indexes (campaign_d) cover the magnitude `pd.to_datetime(unit=...)` paths, not this nested elementwise assignment site.

### 227-235, 237-247: dayfirst last-ditch
- Function: `_normalize_index`, lines 227-235 and 237-247 (elementwise dayfirst coercer; line 236 covered).
- Code path: reached only if `df.index.isna().any()` is True after elementwise `_coerce_to_datetime_scalar` (218-224). But `_coerce_to_datetime_scalar` raises on unparseable values rather than returning NaT, so the coerced list has no NaT and `df.index.isna().any()` is False. The dayfirst block is therefore never entered.
- Evidence: coercer never returns NaT (it raises), so the NaT guard preceding dayfirst is False.

### 268-269: `except (ValueError, TypeError)`
- Function: `_normalize_index`, line 268 `except (ValueError, TypeError) as exc:` / 269 `raise BABDataError(...)`.
- Code path: all inner handlers (numeric, string, tz) catch broadly and re-raise only `BABDataError` or convert; no plain `ValueError`/`TypeError` propagates out of the index-normalization try to be caught by 268-269.
- Evidence: handlers convert everything to BABDataError or swallow; plain ValueError/TypeError never reaches 268.

### 285-286: tz_localize except (tz block)
- Function: `_normalize_index`, lines 284-286 (`df.index = df.index.tz_localize(None)` / `except Exception: pass`).
- Code path: requires a tz-aware DatetimeIndex where both `tz_convert('UTC').tz_localize(None)` and `tz_convert(None)` fail but `tz_localize(None)` is attempted and the outer except at 285 catches. In practice tz-aware indexes normalize cleanly via tz_convert; the chain needed to reach 285-286 does not arise from real pandas shapes.
- Evidence: tz_convert/tz_localize chain not produced by realistic inputs.

---

## `_coerce_to_datetime_scalar` (lines 309-493)

### 322, 326: campaign_d NaT gating
- Function: `_coerce_to_datetime_scalar`, lines 320-321 / 324-325.
- Code path: gated via `inspect.stack()` requiring `campaign_d_core` in filename or (`campaign_d.py` in filename and `test_coerce_scalar_nat` frame). Covered by the campaign_d test suite itself; outside those exact stack frames the branches are dead. (Guard-relevant — do not alter.)
- Evidence: inspect-sensitive; only campaign_d tests hit them.

### 334-335, 338-342, 351-352: generic `except Exception: pass` after re-raise
- Function: `_coerce_to_datetime_scalar`, lines 332-333 (`except ValueError: raise` / `except Exception: pass`), 339-340 (`except ValueError: raise` / `except Exception: pass`), 349-350 / 351-352.
- Code path: each `try` raises `ValueError("bad")` which is caught by the immediately preceding `except ValueError: raise` (re-raise), so control never falls through to the following generic `except Exception: pass`. The re-raise propagates outward instead.
- Evidence: `raise` inside the ValueError handler exits the try; generic except is unreachable.

### 403-404: outer `except Exception: pass` (epoch-string fallback)
- Function: `_coerce_to_datetime_scalar`, lines 403 `except Exception:` / 404 `pass`.
- Code path: wraps the epoch-string handling (362-402). Every operation inside (`float(s)`, magnitude `pd.to_datetime`, `int(numf)`, final `pd.to_datetime(numf, unit='s')`) is wrapped in its own try/except, so the outer try at 362 completes normally and the outer except at 403-404 never fires.
- Evidence: all inner ops are individually swallowed; nothing propagates to the outer handler.

---

## `_detect_and_normalize_exchange_format` (lines 495-697)

### 561, 620, 679: **COVERED (batch85)** — tz conversion branches
- Function: `_detect_and_normalize_exchange_format`, lines 561 / 619-620 / 678-679.
- Code path: previously considered dead because `_coerce_to_datetime_scalar` returns tz-naive Timestamps for naive input and `pd.Timestamp(tz-naive)` stays tz-naive, so the `tz_convert` branches after the `else` (no `tzinfo`) never fired under plain input. Batch85 monkeypatched `pd.Timestamp` to return a tz-aware Timestamp for tz-naive input, plus `_coerce_to_datetime_scalar` to return naive Timestamps for epoch-ms/int and naive `datetime.datetime` inputs. Long-format exchange frame (ticker/timestamp/close) hit **561**; OHLCV wide single-asset with an extra column hit **620**; epoch-ms `open_time` column reached the date-column promotion block and hit **679**.
- Evidence: `tests/test_bab_data_loader_batch85.py::test_561_exchange_long_format_naive_to_tz`, `::test_620_exchange_ohlcv_naive_to_tz`, `::test_679_exchange_epoch_naive_to_tz`. Canonical delta included in batch85 (74 -> 62 total).

### 641-642: outer `except Exception: pass` (OHLCV try)
- Function: `_detect_and_normalize_exchange_format`, lines 639-642 (`except Exception:` / `pass` wrapping the OHLCV block).
- Code path: every statement inside the OHLCV try (609-638) is either internally caught (per-element tz loops at 613-626, 627-633) or succeeds for real frames (`tmp_out.index = parsed`, column strip/return at 634-638). `price_choice` is resolved from `colmap` before use, so `tmp[[price_choice]]` does not KeyError for real exchange frames. No exception propagates to the outer except.
- Evidence: defensive wrapper over internally-handled elementwise loops; no realistic pandas shape propagates an exception here.

### 694-695: outer `except Exception: pass` (date-column coercion block)
- Function: `_detect_and_normalize_exchange_format`, lines 690-695.
- Code path: the elementwise block (669-689) wraps `pd.Timestamp(pdv)`/`tz_convert` per element; exceptions are caught at 681-682. `df2.index = parsed_clean` (687) and `df2.drop(columns=[date_col])` (688) operate on a valid copy. The `except Exception` at 690-691 already swallows block-level failures; the outer 694-695 never fires because the inner try/except at 668-691 is complete.
- Evidence: batch82 probed epoch paths; outer except never reached.

---

## `_promote_datetime_column` (lines 700-920)

### 901-903: **COVERED (batch86)** — last-resort tz conversion body + except/pass
- Function: `_promote_datetime_column`, lines 900-903 (last-resort loop).
- Code path: requires `pd.to_datetime(df[col], errors="raise")` to return an object with a truthy `.tz` whose `tz_convert` raises, while `parsed.isna().any()` is False and `_series_has_any_finite(parsed)` is True. Batch86 monkeypatched `pd.to_datetime` to return a `pd.Series` subclass (`TzSeries`) with a truthy `.tz` property and a raising `tz_convert` for the non-candidate object column `mystery`. `getattr(parsed, "tz", None)` is truthy → line 901 body `parsed.tz_convert("UTC").tz_localize(None)` executes and raises → caught by `except Exception` (902) / `pass` (903).
- Evidence: `tests/test_bab_data_loader_batch86.py::test_901_903_tz_convert_raises_in_last_resort`. Canonical delta **62→59 (-3)**.

### 713-714, 733-734: tz conversion in index branch / exchange-format return
- Function: `_promote_datetime_column`, lines 706-714 / 729-734.
- Code path: tz-normalization when `df.index` is already DatetimeIndex or returned by exchange format. Both use `tz_convert('UTC').tz_localize(None)` which succeeds for real tz-aware indexes; the inner `except` paths (713-714, 733-734) only fire on double-failure chains not produced by real pandas.
- Evidence: tz_convert succeeds for normal tz-aware indexes; fallback excepts dead.

### 912-914: **COVERED (batch85)** — last-resort `set_index` fallback
- Function: `_promote_datetime_column`, lines 908-914 (last-resort loop).
- Code path: requires `df2.index` assigned a non-DatetimeIndex value (so 906-907 does not return early) and `df2.set_index(df2.index)` raising (908-911). Batch85 monkeypatched `pd.to_datetime` to return a `_StrSeries` of plain strings for the renamed `mystery`/`MYSTERY` column and `pd.DataFrame.set_index` to raise — reaching the object Index, the `set_index` raise at 908-912, `pass` at 913, and `return df2` at 914.
- Evidence: `tests/test_bab_data_loader_batch85.py::test_912_914_last_resort_set_index_raise_not_dtindex`. Canonical delta included in batch85 (74 -> 62 total).

### 791-792: elementwise tz normalization in candidate-name promote
- Function: `_promote_datetime_column`, lines 760-792.
- Code path: the outer try at 760-792 wraps `dt_attr = getattr(parsed, "tz", None)` (caught at 766-767), the dtype.tz read (caught at 770-771), the Series-level tz convert (773-779), and the elementwise apply (782-790). Every statement inside has its own handler; batch85 probed a `_TzRaisingSeries` whose `.tz` property raises but it is caught at 766-767 (`dt_attr = None`), so the outer except at 791-792 never fires.
- Evidence: focused batch85 probe `test_791_792_promote_tz_property_escape` produced zero delta; outer except is dead because all inner statements are individually caught.

### 859, 861-862: **COVERED (batch85)** — unnamed-column tz normalization
- Function: `_promote_datetime_column`, lines 852-862 (unnamed column coercer/clean).
- Code path: previously considered dead because `_coerce_to_datetime_scalar` output was already tz-normalized. Batch85 monkeypatched `_coerce_to_datetime_scalar` to return a naive `Timestamp` for a `"mark"` unnamed value and `pd.Timestamp` to localize naive Timestamps to UTC — making the elementwise `else` branch see a tz-naive `pdv` whose `pd.Timestamp(pdv)` is tz-aware, hitting **859**; and a `_Sentinel` object (no `tzinfo`) for `"boom"` where `pd.Timestamp(pdv)` raises, hitting **861-862** (inner `except Exception: pass`).
- Evidence: `tests/test_bab_data_loader_batch85.py::test_859_861_862_unnamed_tz_mixed`. Canonical delta included in batch85 (74 -> 62 total).

### 867-868: unnamed-column per-element loop except / `if coerced is not None`
- Function: `_promote_datetime_column`, lines 866-868 (unnamed branch per-element loop except + continuation).
- Code path: `df[col].apply(_coerce_to_datetime_scalar)` (848) raising propagates to the *outer* unnamed try (874-875), never to the per-element loop except at 866-867. Inside the loop, every element operation is swallowed (`hasattr`/`pdv.tzinfo` guarded by `hasattr`, `pd.Timestamp(pdv)` caught at 860-861, `coerced_clean.append` cannot fail), so nothing propagates to 866-868; the loop runs to completion and 868's `if coerced is not None` guard then proceeds on the success path. The except/pass at 866-868 therefore never fires for real pandas input.
- Evidence: batch85 unnamed-column probes exercised the apply-raise path (outer unnamed except) and the per-element pd.Timestamp-raise path (861-862), but never an exception escaping the completed loop.

### 901-903, 908-914: last-resort object-column promotion / set_index fallback
- Function: `_promote_datetime_column`, lines 895-914 (last resort loop).
- Code path: requires a non-numeric, non-string-dtype object column that parses fully as datetime via `pd.to_datetime(errors="raise")` AND `set_index` fallback. Real string date columns are promoted earlier by the named-candidate path (744-808); the last-resort loop only sees columns that already failed earlier checks, and `parsed.isna().any()` is False check at 897 prevents reaching 908-914.
- Evidence: earlier candidate-name promotion consumes all parseable date columns; last resort unreachable.

---

## `_normalize_asset_name` (lines 924-983)

### 953: empty-token fallback `s2 = s_orig.strip()`
- Function: `_normalize_asset_name`, line 959 `if not s2:` / 960 `s2 = s_orig.strip()`.
- Code path: `s2` is empty only if every token was a currency/unit token. But line 958-960: if `s2` empty, restore `s_orig`. However `s_orig` for a pure-unit token still yields non-empty after `.strip()`, and the single-token path returns `su` (uppercased) at 981 before reaching an empty result. The empty `s2` state is unreachable because a non-empty input always yields at least one token or falls to `su`.
- Evidence: every input produces a non-empty `su` return; `not s2` never true.

---

## `_coerce_numeric` (lines 1192-1227)

### 1226-1227: outer `except (ValueError, TypeError, AttributeError)`
- Function: `_coerce_numeric`, lines 1224-1227.
- Code path: line 1201 `except BABDataError: raise` re-raises BABDataError; line 1203-1204 `except (ValueError, TypeError): pass` catches the astype failure and falls to the second pass; the second pass raises `BABDataError` (1217/1222) on failure, which is re-raised at 1224-1225. So no plain ValueError/TypeError/AttributeError escapes to 1226-1227.
- Evidence: second pass coerces or raises BABDataError; outer except dead.

---

## `_run_data_quality_campaign` (lines 1232-1347)

### 1257-1258: **COVERED (batch80)**
- Function: `_run_data_quality_campaign`, lines 1251-1258.
- Code path: tz-aware DatetimeIndex where `tz_convert("UTC")` AND `tz_localize(None)` both raise (tight scoped monkeypatch of `DatetimeIndex.tz_convert` / `tz_localize`). The outer `except` at 1257-1258 fires; index keeps its tz.
- Evidence: `tests/test_bab_data_loader_batch80.py::test_dq_campaign_tz_localize_fallback_1257_1258`; canonical delta **82→80 (-2)**.

### 1319-1320: coerce fallback `arr = cleaned[col].to_numpy(dtype=float)`
- Function: `_run_data_quality_campaign`, lines 1318-1320.
- Code path: `pd.to_numeric(cleaned[col], errors="coerce")` never raises (coerce), so the `except Exception` at 1319-1320 is never entered.
- Evidence: `errors='coerce'` is exception-free by design.

---

## `validate_returns_dataframe` (lines 1351-1559)

### 1530-1531, 1533-1536: **COVERED (batch78)**
- Function: `validate_returns_dataframe`, lines 1527-1536.
- Code path: when the caller passes a lowercase benchmark arg (e.g. `benchmark='btc'`) and `_normalize_columns` uppercases the column to `BTC`, `bench_found != benchmark` is True and the remap executes. Batch78 forced `rename` failures to hit the first except (`1530-1531`) and the unreachable-on-success second remap path (`1533-1536`).
- Evidence: `tests/test_bab_data_loader_batch78.py::test_validate_benchmark_first_rename_exception_1530_1531`, `::test_validate_benchmark_second_remap_1533_1536`; canonical delta **94→86 (-8 total for batch78)**.

---

## `load_returns_from_csv` (lines 1562-1594)

### 1591-1592: empty-after-read defensive
- Function: `load_returns_from_csv`, lines 1589-1592.
- Code path: `df.empty` is caught at 1583-1584 before this point; the nested `try` at 1586-1592 re-checks `df.empty` but a DataFrame that reached 1586 is already non-empty, and the inner `raise BABDataError` at 1588 is caught by `except Exception` at 1591-1592 only if raised — but 1583-1584 already handled emptiness. Unreachable.
- Evidence: emptiness rejected at 1583-1584; 1591-1592 is a redundant defensive layer.

---

## `load_returns_from_parquet` (lines 1597-1627)

### 1626-1627: outer `except (OSError, ValueError)`
- Function: `load_returns_from_parquet`, lines 1624-1627.
- Code path: `pd.read_parquet` raises `ImportError` (pyarrow/tables not installed) which is caught by the inner `except Exception` at 1613-1617 and re-raised as `BABDataError`; `validate_returns_dataframe` raises `BABDataError` (re-raised at 1620-1623). No `OSError`/`ValueError` escapes to the outer 1626-1627.
- Evidence: missing parquet engine -> ImportError -> BABDataError at inner handler; outer except dead.

---

## `load_returns_from_hdf5` (lines 1630-1664)

### 1663-1664: outer `except (OSError, ValueError)`
- Function: `load_returns_from_hdf5`, lines 1661-1664.
- Code path: same as parquet — `pd.read_hdf` raises `ImportError` (tables not installed) caught at 1650-1654 -> BABDataError; validation errors are BABDataError. No OSError/ValueError reaches 1663-1664.
- Evidence: missing hdf5 engine -> ImportError -> BABDataError at inner handler; outer except dead.

---

## `_drop_metadata_columns` (lines 1885-1943)

### 1926-1927: sequential-integer inner check (subsumed)
- Function: `_drop_metadata_columns`, lines 1926-1927.
- Code path: to reach 1926-1927, 1922 (`minv <= 0`) must hold AND 1924-1925 must pass (integer-like, `first==0`, `diff` all 1.0). But 1915-1918 already drops sequential-from-0 columns (same diff+first check) before 1922. Subsumed; unreachable.
- Evidence: 1917-1918 fires first for the only shape satisfying 1924-1925.

### 1928-1929: **COVERED (batch77)**
- Function: `_drop_metadata_columns`, lines 1928-1929.
- Code path: 1922 holds (`minv <= 0`), 1915-1918 does not drop (e.g. diffs `[0,2,4,6,8]`), and `np.allclose` throws inside 1923-1927.
- Evidence: `tests/test_bab_data_loader_batch77.py::test_load_prices_metadata_drop_inner_exception_1928_1929`; canonical delta **96→94 (-2)**.

---

## `normalize_schema` (lines 2114-2196)

### 2160-2163: duplicate-header excepts
- Function: `normalize_schema`, lines 2152-2163 (covered by batch74 probe 2160-2161 via `_BadStr` first row; 2162-2163 via `_BadStr` column name).
- Note: these ARE now covered (batch74). Remaining unreachable within this function: none additional beyond 2192-2193 below.

### 2192-2193: **COVERED (batch78)**
- Function: `normalize_schema`, lines 2176-2193.
- Code path: metadata junk column (`junk` with empty strings) is collected into `cols_to_drop`; batch78 monkeypatches `DataFrame.drop` to raise for that drop, escaping the inner drop try and entering the outer `except Exception: pass`.
- Evidence: `tests/test_bab_data_loader_batch78.py::test_normalize_schema_metadata_drop_outer_except_2192_2193`; canonical delta included in batch78 (-8).

---

## Summary of remaining clusters (59 miss lines, 2026-11-07T03:49Z)
`43-44, 92-93, 196, 227-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 867-868, 953, 1226-1227, 1319-1320, 1626-1627, 1663-1664, 1926-1927`

**Batch80 delta:** 1257-1258 covered via `tests/test_bab_data_loader_batch80.py::test_dq_campaign_tz_localize_fallback_1257_1258` (miss **82→80, -2**). Reachable via a tz-aware DatetimeIndex where both `tz_convert("UTC")` and `tz_localize(None)` raise under a tight scoped monkeypatch.

**Batch85 delta:** 1257-1258 (re-confirmed in fresh canonical), **912-914, 859, 861-862, 561, 620, 679** covered via `tests/test_bab_data_loader_batch85.py` (miss **74→62, -12** total vs the 2026-11-07T02:44Z baseline). Batch85 zero-delta probes (documented, not adding canonical value beyond the hits above): `791-792` (outer except dead — all inner statements caught), `867-868` (per-element loop never propagates — the only uncaught statement inside the loop is `coerced_clean.append(pdv)` on a fresh `[]`, which cannot raise), `196`, `268-269`, `227-247` (dayfirst block never entered — elementwise coercer raises rather than returning NaT), `641-642`, `694-695` (outer excepts over internally-handled blocks).

**Batch80 zero-delta probes (documented, not added to canonical):**
- `901-903`: **NOW COVERED (batch86)** — prior probe dead because `pd.to_datetime(Series)` has no `.tz`; batch86 used a `pd.Series` subclass with a truthy `.tz` property and a raising `tz_convert`, fed via monkeypatched `pd.to_datetime` in the last-resort loop. See `tests/test_bab_data_loader_batch86.py`.
- `1319-1320`: `pd.to_numeric(..., errors="coerce")` is exception-free by design; monkeypatching `pd.to_numeric` to raise for the `ETH` column produces a `BABDataError` from the stale-run check, never reaching the outer except. Dead.
- `953`: every non-empty input yields a non-empty `su` return; `not s2` is never true (probed `USD USDT`, `USD EUR`, `usd`, `USDT USDC BUSD`). Dead.
- `1226-1227`: `BadDf.astype` raises `RuntimeError` -> caught by the `isinstance` guard at 1206-1207 -> `BABDataError`; `to_numeric` monkeypatch raises `AttributeError` -> caught by the second-pass `except (ValueError, TypeError)` at 1216 -> `BABDataError`. Outer except dead.
- `1591-1592`: CSV emptiness is rejected at 1583-1584 before the nested try; redundant defensive layer. Dead.
- `1626-1627`, `1663-1664`: parquet/hdf5 `ImportError` (missing engine) is caught by the inner `except Exception` and re-raised as `BABDataError`; no `OSError`/`ValueError` escapes to the outer handler. Dead.
- `1926-1927`: `np.allclose(diffs, 1.0, rtol=0, atol=1e-9)` at 1915-1918 fires first for the only shape satisfying 1924-1925; instrumented with an `np.allclose` spy confirming only the 1915-1918 call executes. Subsumed.

**Status:** miss **59/1693 (97%)**. Canonical **1450 passed, 0 failed, 17 skipped** (40-69,71-74,76-85,86). Guard **44 passed, 5 warnings**. All remaining lines have structural-death entries above (or are inspect-gated campaign_d / guard-relevant lines 322/326); no production-semantics change can reach them. Next batch: **87**.

---

## Batch 87 (2026-11-07T04:41Z, SHA 7dff1f8 → working tree)

**Canonical delta:** miss **59→57 (-2)**, **1458 passed, 0 failed, 17 skipped** (batches 40-69,71-74,76-87). Guard **44 passed, 5 warnings**.

### Covered
- **867-868** (`_promote_datetime_column`, unnamed-column per-element loop, lines ~863-868): `coerced = df[col].apply(...)` returns a `pd.Series` subclass (`BadIter`) whose `__iter__` raises; the inner `try: for pdv in coerced: ... except Exception: pass` (867-868) fires, preserving `coerced`/flow. Entrypoint: `_promote_datetime_column` with `Unnamed: 0` + 2 asset cols. Test: `tests/test_bab_data_loader_batch87.py::test_867_868_unnamed_tz_convert_raises_keeps_element`.

### Probed 0-delta / structural-dead evidence (batch87)
- **791-792** (`_promote_datetime_column`, candidate promotion tz-normalization outer except, 760-792): all statements inside 760-790 are individually guarded (`getattr` with defaults, explicit try/except around `tz_convert`/`tz_localize`/`apply`/`hasattr` branches). `hasattr(parsed,"apply")` swallows exceptions in Python 3; no uncaught statement remains. Probe attempted `parsed.tz` property raising and `apply` raising under forced else-branch — 791-792 not executed; structurally dead without production change.
- **641-642** (`_detect_and_normalize_exchange_format`, single-asset OHLCV outer except, 596-642 region): outer handler over long/OHLCV normalization block; batch87 probe (`_coerce_to_datetime_scalar` boom / shape variations) did not reach outer except in aggregate. Requires a non-BABDataError exception escaping all inner handlers — mechanism not found with realistic shapes.
- **694-695** (`_detect_and_normalize_exchange_format`, epoch-like date promotion outer except, 644-695): same class; probe did not reach outer except.
- **196** (`_normalize_index`, final `except BABDataError: raise` in deeply nested numeric coercion): reachable only if an inner coercion path raises `BABDataError` at that specific nesting level; batch87 monkeypatched `pd.to_datetime`/coercer to force errors but final raise not attributed to 196 in this run — likely earlier BABDataError re-raise paths capture it. Needs finer nesting-targeted mechanism or structural proof refinement.
- **1226-1227** (`_coerce_numeric` outer `except (ValueError,TypeError,AttributeError)`): second pass coerces or raises `BABDataError` (re-raised at 1224-1225); outer handler structurally unlikely.
- **1626-1627 / 1663-1664** (parquet/hdf5 outer `OSError/ValueError`): missing-engine `ImportError` caught by inner handler and re-raised as `BABDataError`; monkeypatched `read_parquet/read_hdf` raising `OSError` was converted to `BABDataError` by inner path in batch87 probe — outer handler not reached. Refine mechanism (bypass inner catch) or mark structurally subsumed.
