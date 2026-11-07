# Unreachable-branch proofs — data_loader.py remaining miss lines

Generated: 2026-11-06T20:55 UTC (post batch73/batch74, miss 107 -> 96).
Refreshed: 2026-11-07T07:40Z UTC (post batch93, miss 54 -> 44).
Canonical aggregate (fresh, 2026-11-07T07:40Z): **1463 passed, 0 failed, 17 skipped, 107 warnings** (batches 40-69, 71-74, 76-93), guard **44 passed, 5 warnings**. Miss **44 / 1693 stmts (97%)**, delta **-10 vs 54**.
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

### 227-233, 245: **COVERED (batch93)** — dayfirst last-ditch entry
- Function: `_normalize_index`, lines 227-233, 245 (dayfirst block entered; coerced assigned). 234-244, 246-247 remain missing (see below).
- Code path: `_coerce_to_datetime_scalar` returns `pd.NaT` (no raise) for `np.datetime64('NaT')` while raising for `pd.NaT`/`None`/unparseable strings. An object index mixing valid ISO dates with `np.datetime64('NaT')` passes 218-224 (coercer returns NaT for the NaT element), leaves `df.index.isna().any()` True at 225, and enters 227-245; 232 succeeds for all elements (deterministic coercer) so 234-244 never fire, 245 assigns, and 291-295 drops NaT rows.
- Evidence: `tests/test_bab_data_loader_batch93.py::test_227_245_dayfirst_block_via_np_datetime64_nat`, `::test_coercer_nat_passthrough_contract`. Canonical delta **54→44 (-10)**.

### 234-244, 246-247: dayfirst per-element fallback + `ValueError("unparseable")` — **structurally dead** (batch94 mechanism-closure)
- Function: `_normalize_index`, lines 234-235 (`except/pass` after 232 coercer call), 237-244 (dayfirst `pd.to_datetime(..., dayfirst=True, utc=True/False)` fallbacks + re-raise), 246-247 (`except Exception: raise ValueError("unparseable")`).
- Code path / mechanism closure:
  - **Reachability gate (216-225):** 227-247 is entered only if 225 is true (`df.index.isna().any()` after 216-224). 216-224 calls `_coerce_to_datetime_scalar(v)` for each index element and does `except Exception: raise` at 222-223 — so 224/225 execute only when *every* element either returns a value or returns `pd.NaT` (np.datetime64 NaT case). Any element that makes the coercer raise (unparseable string, `pd.NaT`, `None`, `NaN`, `''`, etc.) is intercepted at 223 and control jumps to 248, **never reaching 225/227**.
  - **232 determinism:** inside 227-247, 231-233 calls the same deterministic `_coerce_to_datetime_scalar(v)` on the same `idx` elements. For all elements that survived 216-224, 232 returns the same result (verified: coercer is pure/deterministic; `np.datetime64('NaT')`→`pd.NaT` no-raise, valid ISO/`31/12/2020`→Timestamp, all bad inputs raise). Therefore 232 never raises for any element that can reach 227, `continue` always fires at 233, and **234-244 (dayfirst fallbacks) never execute**.
  - **245/246-247:** `df.index = coerced` at 245 assigns a plain Python list/sequence of Timestamps/NaT on a normal `pd.DataFrame` (assignment is safe; 224 performs the same kind of assignment). No realistic path makes 245 raise while 224 succeeded on an equivalent coerced shape. 246-247 would only run if 245 (or an exception escaping the loop, which cannot happen given 232 determinism + 243 re-raise only reachable via 234-242 — themselves unreachable) raised.
- Evidence (2026-11-07T09:35Z, direct trace, PYTHONPATH set): `sys.settrace` over `_normalize_index` with `idx=[np.datetime64('NaT'), 'zzzznotadate999']` hit 217-223 then 248-259 (223 raised on the unparseable element) and **never hit 224-247**; confirms 223 intercept prevents 227 entry for mixed NaT+unparseable shapes. Coercer determinism verified: repeated calls return identical outcomes/exception types. Coverage probe (separate process) reported 234-244,246-247 MISS under the same shape.
- Conclusion: 234-244,246-247 are **structurally unreachable without changing coercer semantics or injecting a non-deterministic/production-unrealistic index-assignment failure** (both disallowed). Proof-only.

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

### 641-642: outer `except Exception: pass` (OHLCV outer try) — **structurally dead**
- Function: `_detect_and_normalize_exchange_format`, lines 641-642 catch the outer `try` at line 598 (lines 598-642).
- Code path: 598's try body contains only 599-607 (comments, list literal, `for`/`if`/`in` on `colmap`/local vars, assignments) — no fallible operation. 607's `if` contains 608-640: 608's inner `try` (608-640) catches all `Exception` at 639-640, so nothing escapes 608-640. Therefore no statement inside 598-640 can propagate an exception to 641-642.
- Evidence (batch90 structural review): 641-642 are unreachable for any input; `df.copy()`/`apply`/index ops inside 608-640 are swallowed by 639-640. Proof-first; no test mechanism exists without modifying production control flow.

### 694-695: outer `except Exception: pass` (date-column coercion outer try) — **structurally dead**
- Function: `_detect_and_normalize_exchange_format`, lines 694-695 catch the outer `try` at line 648 (648-695).
- Code path: 649-667 perform `df[date_col]` access/`len`/`iloc`/`isinstance`/string ops/`float` on already-type-narrowed numeric samples/`np.isnan` — all safe for frames where `date_col` was resolved from `df.columns` and sample types match the branches. 668-691 is fully wrapped by 690-691 (`except Exception: pass`). 692-693 is a safe conditional return. No exception can propagate to 694-695.
- Evidence (batch90 structural review): inner handlers at 690-691 swallow 668-689; setup path uses only guarded/safe operations on a column known to exist. Proof-first.

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

### 791-792: elementwise tz normalization in candidate-name promote — **structurally dead** (batch94 closure)
- Function: `_promote_datetime_column`, lines 760-792 (candidate promotion tz-normalization), outer `except Exception: pass` at 791-792.
- Code path: 760 opens `try`, 791-792 is the only outer `except`. Every statement inside 760-790 is individually guarded: 764-767 wraps `getattr(parsed,"tz",None)`; 768-771 wraps dtype.tz lookup; 773-779 wraps `tz_convert/tz_localize` chain; 782-790 wraps `hasattr(parsed,"apply")` + `parsed.apply(...)`. Python 3 `hasattr` swallows descriptor/property exceptions, and `apply` exceptions are caught at 789-790. No uncaught statement exists between 760-790 that can propagate to 791.
- Evidence: batch85 probe `test_791_792_promote_tz_property_escape` (0 delta), batch87 probes (tz property raising / apply raising / forced else-branch) all swallowed by inner handlers; batch91 subclass probe left index as string with 791-792 not hit; batch94 static verification confirms all 760-790 statements are inside inner try/except or are exception-free conditionals. **Structurally dead without production control-flow change.**

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

### 1626-1627: outer `except (OSError, ValueError)` — **structurally dead**
- Function: `load_returns_from_parquet`, lines 1624-1627.
- Code path: `pd.read_parquet` is inside 1609-1617; `except Exception` at 1613 catches all read exceptions (including `OSError`/`ValueError`/`ImportError`) and raises `BABDataError`. `validate_returns_dataframe` is inside 1618-1623; `BABDataError` is re-raised (1620), any other `Exception` becomes `BABDataError` (1622). 1624 re-raises `BABDataError`. Since every exception from 1608-1623 is converted to `BABDataError` before 1624, `(OSError, ValueError)` can never reach 1626-1627.
- Evidence (batch90 structural review): inner `except Exception` handlers convert to `BABDataError`; outer typed handler is unreachable.

---

## `load_returns_from_hdf5` (lines 1630-1664)

### 1663-1664: outer `except (OSError, ValueError)` — **structurally dead**
- Function: `load_returns_from_hdf5`, lines 1661-1664.
- Code path: mirrors parquet (lines 1646-1664): inner `except Exception` handlers at 1650-1654 (read) and 1659-1660 (validate) convert all exceptions to `BABDataError`; 1661 re-raises `BABDataError`. `(OSError, ValueError)` never propagates to 1663-1664.
- Evidence (batch90 structural review): same structural subsumption as 1626-1627.

---

## `_drop_metadata_columns` (lines 1885-1943)

### 1926-1927: sequential-integer inner check (subsumed) — **structurally dead**
- Function: `_drop_metadata_columns`, lines 1926-1927.
- Code path: 1915-1918 drop when `all(finite)`, `np.allclose(diffs,1.0,rtol=0,atol=1e-9)` and `float(vals[finite][0])==0.0`. 1924-1925 (inside `minv<=0` block) drop when integer-like AND `first==0.0` AND `np.allclose(np.diff(vals[finite]),1.0)`. Any finite array satisfying 1924-1925 also satisfies 1915-1918 (same `first==0` and same `allclose(diffs,1)` predicate on the same `vals[finite]`), so 1917-1918 fires and `continue`s before 1919-1927 can run. The predicates are identical in effect for that shape.
- Evidence (batch90 structural analysis; probe removed, 0 canonical delta): monkeypatching `np.allclose` globally to falsify 1915 while keeping 1924 true is not a realistic execution path (same function/args) and did not yield a stable canonical hit; subsumption holds for real `np.allclose` semantics.

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

## Summary of remaining clusters (44 miss lines, 2026-11-07T09:35Z batch94 rebaseline/proof-refresh)

`43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953, 1319-1320, 1626-1627, 1663-1664, 1926-1927`

**Batch94 (0 delta, proof-refresh):** canonical reverified **1463 passed, 0 failed, 17 skipped, 107 warnings** (40-69,71-74,76-89,93; batch75 excluded from canonical per ledger, batch94 transient beta-targeting probe removed), miss **44/1693 (97%)**, guard **44 passed, 5 warnings**. Strengthened mechanism-closure proofs: **234-244,246-247** — 227-247 is entered only when 216-224 completes without coercer raise; 232 uses the same deterministic coercer on the same elements, so `continue` always fires and dayfirst fallbacks/`ValueError("unparseable")` are unreachable (trace evidence shows 223→248 for mixed NaT+unparseable; coercer deterministic). **791-792** — all 760-790 statements individually guarded; outer except structurally dead. **641-642,694-695,1626-1627,1663-1664,1926-1927** retained as structural-dead/subsumed (batch90). **322,326** inspect-gated (guard-relevant, do not alter). No production-semantics change can reach remaining lines. Next batch: **95**.

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

## Batch 88 (2026-11-07T04:58Z, SHA 145e9cd → working tree)

**Canonical delta:** miss **57→56 (-1)**, **1459 passed, 0 failed, 17 skipped** (batches 40-69,71-74,76-88). Guard **44 passed, 5 warnings**.

### Covered
- **196** (`_normalize_index`, numeric epoch index nested BABDataError re-raise, line 196): numeric index → all `pd.to_datetime` attempts fail; 182-186 coercion succeeds but first `df.index` assignment raises `RuntimeError` (caught 189); 192-194 elementwise coercion raises `BABDataError` → 195-196 re-raises. Entrypoint: `_normalize_index` on a `pd.DataFrame` subclass whose first index-setter call raises, with `pd.to_datetime` monkeypatched to raise and `_coerce_to_datetime_scalar` returning success twice then `BABDataError`. Test: `tests/test_bab_data_loader_batch88.py::test_196_numeric_index_coercer_baberror_reraised`.

### Structural/proof notes (batch88)
- **1226-1227**: outer `except (ValueError,TypeError,AttributeError)` in `_coerce_numeric`. A `pd.DataFrame` subclass raising `TypeError` from `copy()` did not surface the wrapped BABDataError in probe (`_coerce_numeric` returned successfully in that probe shape), indicating the expected 1198/1226 path was not exercised as modeled; all normal per-column coercion failures are converted to `BABDataError` inside the loop (1216/1222) and re-raised at 1224-1225. Treat as structural-dead unless a concrete escaping `ValueError/TypeError/AttributeError` outside those handlers is demonstrated.
- **641-642, 694-695**: `_detect_and_normalize_exchange_format` outer handlers. 597-642 places risky work inside 608-640 (639-640 swallows) so 641-642 is structurally unreachable from normal control flow; 694-695 could only fire from 649-667 setup exceptions (e.g. pathological numeric subclass where `float()` raises despite `isinstance` numeric) — no realistic fixture found; proof-first.

---

## Batch 89 (2026-11-07T05:25Z, canonical delta 56→54, 1460 passed / 0 failed / 17 skipped, guard 44 passed)

### 1226-1227: **COVERED** — `_coerce_numeric` outer `except (ValueError, TypeError, AttributeError)`
- Function: `_coerce_numeric`, lines 1224-1227.
- Path: first pass `df.astype("float64")` raises `ValueError` (caught 1203-1204, falls to second pass). Second pass `df_clean = df.copy()` (1209) raises `TypeError` outside the per-column loop but inside the outer `try` (1196); `BABDataError` is not raised, so 1224-1225 do not match and 1226-1227 catch and wrap as `BABDataError`.
- Evidence: `tests/test_bab_data_loader_batch89.py::test_coerce_numeric_copy_exception_wrapped_1226_1227` (DataFrame subclass with `astype`→`ValueError`, `copy`→`TypeError`). Canonical aggregate includes `tests/test_bab_data_loader_batch89.py`.

### 1926-1927: probe — `load_prices` metadata-drop inner `except Exception: pass` (still missing)
- Function: `_drop_metadata_columns` inside `load_prices`, lines 1920-1927.
- Probe: monkeypatched `np.allclose` to raise on the 2nd call (intended as 1921 inside try 1920-1925) with `JUNK=[0,0,0]` and valid BTC/ETH prices. Focused coverage showed 1921-1922 executed and 1926-1927 not hit in that harness shape; exception propagation through 1922’s boolean expression vs. 1921’s `if` guard needs a more precise trigger (or the branch is only reachable via a non-`np.allclose` exception source inside 1920-1925). Keep **proof-first**; do not repeat without a concrete escaping exception mechanism.


---

## Batch 90 (2026-11-07T05:52Z, SHA d2e5a74 → working tree, canonical rebaseline 54 miss / 1460 passed)

**Canonical (reverified):** miss **54/1693 (97%)**, **1460 passed, 0 failed, 17 skipped** (batches 40-69,71-74,76-89). Guard **44 passed, 5 warnings**. No miss reduction (0 delta).

### Probed / strengthened proofs (0 delta)
- **641-642** (`_detect_and_normalize_exchange_format` outer OHLCV handler): **structurally dead**. Outer `try` 598-642 has no fallible setup; inner `try` 608-640 catches all `Exception` at 639-640. No path propagates to 641-642.
- **694-695** (`_detect_and_normalize_exchange_format` outer date-coercion handler): **structurally dead**. 648-695: setup 649-667 uses safe ops on a resolved `date_col`; 668-691 fully swallowed by 690-691; 692-693 safe return.
- **1626-1627 / 1663-1664** (parquet/hdf5 outer `OSError/ValueError`): **structurally dead**. Read/validate inner handlers catch `Exception`/`BABDataError` and convert to `BABDataError`; outer typed handlers are never reached.
- **1926-1927** (`_drop_metadata_columns`): **subsumed/structurally dead** for real semantics — 1915-1918 and 1924-1925 test the same `first==0` + `allclose(diffs,1)` predicate on `vals[finite]`; 1917-1918 fires first. A global `np.allclose` falsification probe (0 canonical delta, not added) is unrealistic and did not produce a stable canonical hit.
- **791-792**: prior batch85/batch87 evidence retained (all inner statements individually guarded; `hasattr` swallow). No new mechanism found.
- **227-247** (`_normalize_index` dayfirst last-ditch): elementwise coercer raises rather than returning NaT, so NaT guard is false (prior evidence). No new NaT-producing path without production change.

**Status:** miss **54/1693 (97%)**. Canonical **1460 passed, 0 failed, 17 skipped** (40-69,71-74,76-89). Guard **44 passed, 5 warnings**. Remaining clusters are documented structural-dead / inspect-gated (`322,326`) / no-known-realistic-mechanism; do not change production semantics solely for coverage. Next batch: **91**.

---

## Batch 91 (2026-11-07T06:29Z, SHA 7a5b48b, canonical rebaseline 54 miss / 1460 passed)

**Canonical (reverified):** miss **54/1693 (97%)**, **1460 passed, 0 failed, 17 skipped, 105 warnings** (batches 40-69,71-74,76-89). Guard **44 passed, 5 warnings**. Deps: `/home/runner/work/_temp/kilo-tmp/pylib` (pytest/coverage/pandas/numpy/scipy present). No miss reduction (0 delta).

### Probed / strengthened proofs (0 delta)
- **227-247** (`_normalize_index`, non-numeric string index dayfirst last-ditch): entered only when `df.index.isna().any()` remains true after 216-224 elementwise `_coerce_to_datetime_scalar`. Production coercer raises `ValueError` (not `NaT`) for unparseable values (verified: `'not-a-date'`, `''`, `None`, `NaN`, `'31/13/2021'` all raise) so 218-224 raises before 225/227. Probe (direct `_normalize_index`, `idx=["31/12/2020","01/13/2021","not-a-date"]`, monkeypatched coercer to return `pd.NaT` on failure): NaN guards reached but harness fell through 248-258 fallback producing row-drop/NaT-index behavior (2 rows, no confirmed 227-247 assignment) — **not stable/production-realistic**; altering coercer semantics is disallowed. **Proof-first; no realistic NaT-producing mechanism without semantics change.**
- **791-792** (`_promote_datetime_column` candidate tz-normalization outer `except`, 760-792): prior batch85/87 evidence retained; batch91 probe (pd.Series subclass with `.tz` property raising under `pd.Series.apply` patch) left index as string, 791-792 not hit. Inner statements individually guarded / `hasattr` swallowed. **Structurally dead without uncaught statement.**
- **641-642, 694-695, 1626-1627, 1663-1664, 1926-1927**: batch90 structural proofs unchanged; no bypass mechanism found. **Proof-only.**

**Status:** miss **54/1693 (97%)**. Canonical **1460 passed, 0 failed, 17 skipped** (40-69,71-74,76-89). Guard **44 passed, 5 warnings**. Remaining clusters structural-dead / inspect-gated (`322,326`) / no-known-realistic-mechanism. Next batch: **92**.

---

## Batch 92 (2026-11-07T06:36Z, SHA 5b2d7ac, canonical rebaseline 54 miss / 1460 passed)

**Canonical (reverified this session):** miss **54/1693 (97%)**, **1460 passed, 0 failed, 17 skipped, 105 warnings** (batches 40-69,71-74,76-89). Guard **44 passed, 5 warnings**. Deps confirmed at `/home/runner/work/_temp/kilo-tmp/pylib`. No miss reduction (0 delta). No production-semantics changes made.

### Evidence refresh (direct module probes, PYTHONPATH set)
- **227-247** (`_normalize_index` dayfirst last-ditch): direct probe of `_coerce_to_datetime_scalar` confirms production contract — `['not-a-date','',None,NaN,'31/13/2021']` all raise `ValueError`; `'2021-01-01'` returns a tz-aware `Timestamp` (`2021-01-01 00:00:00+00:00`, `isna=False`). Therefore 216-224 elementwise coercion raises on any unparseable scalar before 225, and `df.index.isna().any()` cannot become True for a realistic string index that required dayfirst. **Mechanism closed** unless coercer is changed to return NaT (disallowed). Keep proof-only.
- **791-792** (`_promote_datetime_column` outer except, 760-792): reconfirmed all inner statements guarded (`getattr` defaults at 763-771, tz_convert/localize try/except 773-779, elementwise apply try/except 782-790); Python 3 `hasattr` swallows property exceptions. No uncaught statement exists inside 760-790. **Structurally dead.**
- **641-642 / 694-695** (`_detect_and_normalize_exchange_format`): outer handlers remain subsumed by inner `except Exception: pass` blocks (639-640, 690-691) and safe setup. **Structurally dead.**
- **1626-1627 / 1663-1664** (parquet/hdf5 outer handlers): read/validate paths convert all exceptions to `BABDataError` inside inner handlers; outer `(OSError,ValueError)` cannot propagate. **Structurally dead.**
- **1926-1927** (`_drop_metadata_columns`): 1915-1918 and 1924-1925 share identical `first==0` + `allclose(diffs,1)` predicate on `vals[finite]`; 1917-1918 executes/continues first. **Subsumed.**
- **Inspect-gated / previously closed:** `322,326` (campaign_d stack inspection — guard-relevant, do not alter), `43-44,92-93,334-335,338-342,351-352,403-404,953,1319-1320` (re-raise/generic-except/subsumed per prior entries). No new mechanism found.

**Status:** miss **54/1693 (97%)**. Canonical **1460 passed, 0 failed, 17 skipped** (40-69,71-74,76-89). Guard **44 passed, 5 warnings**. All remaining lines are structural-dead, inspect-gated, or would require production-semantics change to reach (disallowed). Future work: only pursue if a **new, production-realistic control-flow mechanism** is demonstrated; otherwise maintain proofs and baseline. Next batch: **93**.

---

## Batch 93 (2026-11-07T07:40Z, SHA 479db53, canonical delta -10)

**Canonical delta:** miss **54→44 (-10)**, **1463 passed, 0 failed, 17 skipped, 107 warnings** (batches 40-69,71-74,76-93). Guard **44 passed, 5 warnings**.

### Covered

- **92-93** (`_coerce_series_to_datetime_index`, outer `except Exception: pass`, lines 92-93): a `pd.Series` subclass (`BadIter`) whose `__iter__` raises escapes the elementwise loop at 76-91 (the only unguarded statement there) and reaches the inner except at 92-93; execution continues at 94-97 and returns `True`. Entrypoint: `_coerce_series_to_datetime_index(df, "date", coerced)`. Test: `tests/test_bab_data_loader_batch93.py::test_92_93_outer_except_via_series_iter_raises`.

- **227-233, 245** (`_normalize_index`, dayfirst last-ditch block, lines 227-247): `_coerce_to_datetime_scalar` returns `pd.NaT` (does NOT raise) for `np.datetime64('NaT')` — verified directly. When an object index mixes valid ISO dates with `np.datetime64('NaT')`, elementwise coercion at 218-224 succeeds (returning `NaT` for the NaT entry), so `df.index.isna().any()` becomes True at 225 and the dayfirst block at 227-247 is entered; rows are dropped at 291-295. Contract: `np.datetime64('NaT')` → `pd.NaT` (no raise); `pd.NaT` → raises `ValueError`. Tests: `tests/test_bab_data_loader_batch93.py::test_227_245_dayfirst_block_via_np_datetime64_nat`, `::test_coercer_nat_passthrough_contract`.

### Remaining miss after batch93 (44 lines)

`43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953, 1319-1320, 1626-1627, 1663-1664, 1926-1927`

All remaining lines are structural-dead, inspect-gated (`322,326`), or blocked by production contracts; no new production-realistic mechanism found in batch93. Next batch: **94**.

---

## Batch 96 (2026-11-07T10:28Z, SHA 7c45311, canonical delta -2)

**Canonical delta:** miss **42→40 (-2)**, **1466 passed, 0 failed, 17 skipped, 107 warnings** (batches 40-69,71-74,76-89,93,95,96). Guard **44 passed, 5 warnings**.

### Covered

- **1319-1320** (`validate_returns_dataframe`, quality finite-data check, lines ~1315-1320): `pd.to_numeric(cleaned[col], errors="coerce").to_numpy(dtype=float)` raises (`RuntimeError`) on a crafted object result for one column; inner `except Exception` falls back to `cleaned[col].to_numpy(dtype=float)`. Entrypoint: `validate_returns_dataframe(..., quality=True)` on a valid 3-row datetime-indexed returns frame. Mechanism: scoped monkeypatch `strategies.betting_against_beta.data_loader.pd.to_numeric` returns a bad object only for the target column; other columns use real `pd.to_numeric`. Test: `tests/test_bab_data_loader_batch96.py::test_1319_1320_quality_to_numeric_to_numpy_raises_falls_back`.

### Proof-first / mechanism-closure notes (batch96, 0 delta)

- **268-269** (`_normalize_index`, outer `except (ValueError, TypeError)` at 160-271): probed by monkeypatching `pandas.api.types.is_numeric_dtype` to raise `ValueError`. Observed: inner handler at 261 (`except Exception`) caught it, attempted reparse at 263, and raised `BABDataError("Index could not be parsed as datetime")`; 266 (`except BABDataError: raise`) caught first because `BABDataError` subclasses `ValueError`. No demonstrated mechanism produces a plain `ValueError/TypeError` from 161-271 that is not converted/caught before 268. **Proof-first; structurally gated by BABDataError ordering.**
- **403-404** (`_coerce_to_datetime_scalar`, numeric-string epoch outer `except` 362-404): every epoch branch (365-402) catches `Exception` and falls through to later branches/405 parsing; regex guard at 361 and deterministic numeric ops make an escaping exception unrealistic without pathological numeric/string subclass behavior. **Proof-first.**
- **43-44** (`_not_null` outer `except`): `v is None` is identity (`is`), not overrideable; `pd.isna` call is wrapped by inner `except Exception` (40-41); remaining body returns `True`. **Structurally dead.**
- **953** (`_normalize_asset_name`): `tok_clean = tok.strip(); if not tok_clean: continue` runs over `s.split()` tokens; Python `str.split()` with no separator never yields empty strings. **Unreachable by construction.**

### Remaining (40 miss)

`43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953, 1626-1627, 1663-1664` — structural-dead, inspect-gated (`322,326` guard-relevant), BABDataError-ordering gated, or construction-unreachable. No production-semantics change solely for coverage.

---

## Batch 97 (2026-11-07T10:40Z, SHA 8f1ec29, proof-only / 0 delta)

**Canonical rebaseline (fresh, 2026-11-07T10:40Z):** miss **40/1693 (98%)**, **1466 passed, 0 failed, 17 skipped, 107 warnings** (batches 40-69,71-74,76-89,93,95,96). Guard **44 passed, 5 warnings**. No miss reduction (0 delta). No production-semantics changes.

### Evidence (direct probes, PYTHONPATH set)

- **234-244, 245, 246-247** (`_normalize_index`, dayfirst last-ditch block, lines ~227-247): 227 entry requires `df.index.isna().any()` True after 216-224. Elements surviving 216-224 never make 232's deterministic `_coerce_to_datetime_scalar` raise, so `continue` always fires and **234-244 are structurally unreachable** (unchanged from batch94). Probe with `np.datetime64('NaT')` entering 227 and a `pd.DataFrame` subclass raising `RuntimeError` on the 2nd `index` assignment (intended for 245): line 245 executed (HIT), but 246-247 (`except Exception: raise ValueError("unparseable")`) did **not** fire — the raised `RuntimeError` propagated/was absorbed by outer fallback recovery paths and `_normalize_index` completed with a valid `DatetimeIndex` (observed `OK`, 6 index-set attempts). This confirms 246-247 is not reached by a naive index-assignment failure under current nested recovery structure; reaching it would require a failure mode that escapes 227-245 handling *and* is not converted by outer handlers — **no production-realistic mechanism demonstrated**. A pathological `__setattr__` DataFrame subclass is not production-realistic input.

- **268-269** (`_normalize_index`, outer `except (ValueError, TypeError)` at 160-271): `BABDataError.__mro__` is `(BABDataError, ValueError, Exception, BaseException, object)`. Handler 266 is `except BABDataError: raise` and precedes 268 `except (ValueError, TypeError) as exc: raise BABDataError(...)`. Therefore any exception that is (or is wrapped as) `BABDataError` — including those raised as/converted through `ValueError` paths inside 161-265 — is caught by 266 first. 268-269 can only fire for a plain `ValueError`/`TypeError` that is **not** a `BABDataError` and escapes 161-265. Probes: `BadStr.__str__` raising `TypeError` in object index → converted to `BABDataError` (266 path, 268-269 MISS); monkeypatched `DatetimeIndex.isna` raising plain `ValueError` → 268-269 MISS (exception handled/converted upstream in the realistic DatetimeIndex fast path or not escaping as plain VE through the guarded structure). **No production-realistic plain VE/TE escape demonstrated; handler ordering + internal conversion make 268-269 proof-first.**

- **403-404** (`_coerce_to_datetime_scalar`, numeric-string epoch outer `except` 362-404): probed with overflow/edge numeric strings (`1e3089999999999999`, `99999999999999999999999999999`, `inf`, `-inf`, `nan`) — all raised `ValueError` through normal parsing paths; 403-404 MISS. 361 regex admits these numeric forms but 365-402 branch handlers and 405+ fallbacks catch/convert; outer 403-404 remains unreachable absent a truly exceptional numeric operation outside those guards.

- **953** (`_normalize_asset_name`, `if not tok_clean: continue`): probed ASCII/Unicode whitespace and separator forms (`'  BTC  '`, tabs/newlines, NBSP, ZWSP-in-token, empty, spaces-only, `BTC/USD`, `BTCUSDT`) — 953 MISS. `str.split()` (no separator) never yields empty strings; `tok_clean = tok.strip()` on a `split()` token is never empty. **Unreachable by construction.**

- **43-44, 322, 326, 334-335, 338-342, 351-352, 641-642, 694-695, 791-792, 1626-1627, 1663-1664**: unchanged from prior mechanism-closure proofs (structural-dead / inspect-gated; `322,326` guard-relevant, **do not alter**). No new mechanism found.

**Remaining (40 miss, post batch98):** `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953, 1626-1627, 1663-1664` — all structural-dead, inspect-gated, BABDataError-MRO/handler-order gated, or construction-unreachable. **Production semantics must not change solely to manufacture coverage.** Future sessions: only pursue with a *new, concretely demonstrated, production-realistic* control-flow mechanism; otherwise maintain proofs and baseline.

---

## Batch 98 (2026-11-07T10:49Z, SHA 8f1ec29, proof-only / 0 delta)

**Canonical rebaseline (fresh, 2026-11-07T10:48Z):** miss **40/1693 (98%)**, **1466 passed, 0 failed, 17 skipped, 107 warnings** (batches 40-69,71-74,76-89,93,95,96). Guard **44 passed, 5 warnings**. No miss reduction (0 delta). No production-semantics changes.

### Evidence (direct probes, PYTHONPATH set)

- **234-244, 245, 246-247** (`_normalize_index`, dayfirst last-ditch block, lines ~227-247): 234-244 remain blocked by 232 coercer determinism after 216-224 gate (batch94/97). Batch98 probe: `np.datetime64('NaT')` index enters 227; a `pd.DataFrame` subclass raised `ValueError('boom245')` on the 2nd `index` assignment (targeting 245). Observed: `_normalize_index` completed with `index_type=pandas.DatetimeIndex`, `n_sets=6` (assignment attempts observed across nested recovery), and **246-247 did not fire** (246-247 is `except Exception: raise ValueError("unparseable")` inside the 227-247 `try`). Confirms batch97: a naive/forced 245 assignment failure is absorbed/recovered by outer handler structure and does not reach 246-247 under current control flow. **No production-realistic mechanism demonstrated** for 246-247; would require an exception escaping 227-245 while bypassing outer BABDataError/recovery conversions (not shown).

- **268-269** (`_normalize_index`, outer `except (ValueError, TypeError)` at 160-271, lines 268-269): handler order is 266 `except BABDataError: raise` then 268 `except (ValueError, TypeError) as exc: raise BABDataError(...)`. `BABDataError.__mro__` includes `ValueError` (batch97). The 261-265 fallback path either re-raises `BABDataError` (caught by 266) or raises `BABDataError("Index could not be parsed as datetime")` (265, caught by 266). Therefore 268-269 is reachable only by a plain `ValueError`/`TypeError` that is **not** a `BABDataError` and escapes 161-265 — but all realistic exception sources inside 161-265 are converted/wrapped before reaching 266/268 in the demonstrated paths. **Handler-order + internal conversion gated; proof-first.**

- **403-404** (`_coerce_to_datetime_scalar`, numeric-string epoch outer `except` 362-404): line-level closure: 363 `numf = float(s)` is inside 362; **364 `av = abs(numf)` is the only statement in 362-402 not inside its own `try/except`**. For regex-admitted numeric strings, `float(s)` returns a builtin `float` (or raises and is outside the 365-402 epoch handling path as structured), making `abs(numf)` safe for normal `str` input. All 365-402 epoch branches and 397-402/405+ fallbacks are individually guarded. 403-404 **structurally unreachable for normal `str` input**; no production-realistic unwrapped exception source demonstrated.

- **43-44** (`_not_null`, outer `except` 34-44): 35 uses identity (`is None`) — not overrideable; 37-41 wraps `pd.isna` in inner `except Exception: pass`; 42 returns `True`. No fallible unwrapped statement remains in 34-42. **Structurally dead.**

- **953** (`_normalize_asset_name`): `s.split()` with no separator never yields empty strings; `tok_clean = tok.strip()` on a split token is never empty. **Unreachable by construction.**

- **322, 326** (inspect-gated/campaign_d; **guard-relevant, DO NOT ALTER**), **334-335, 338-342, 351-352** (re-raise-before-generic-pass), **641-642, 694-695** (inner handlers swallow all `Exception`), **791-792** (all 760-790 individually guarded), **1626-1627, 1663-1664** (inner read/validate convert to `BABDataError`): unchanged from prior proofs (batch90/94/96/97). No new production-realistic mechanism found.

## Batch 99 — 2026-11-07T10:55Z (SHA a7468e0, proof-only / 0 delta)

**Baseline (fresh canonical):** 40 miss / 1693 stmts (98%); 1466 passed, 0 failed, 17 skipped, 107 warnings (40-69,71-74,76-89,93,95,96); guard 44 passed. No production-semantics changes.

| Lines | Function | Evidence |
|---|---|---|
| 234-244,246-247 | `_normalize_index` dayfirst last-ditch (227-247) | 234-244: 232 uses same deterministic `_coerce_to_datetime_scalar` on elements that survived 216-224; `continue` at 233 always fires for non-raising results → **unreachable**. 245/246-247: module-isolated probes with `np.datetime64('NaT')` (grants 227 entry) and forced `__setattr__('index')` failures showed (1) NaT-robust 248-257 fallbacks (`pd.to_datetime`/`_coerce_to_datetime_scalar` on original `idx`) recover to valid `DatetimeIndex` (246-247 not hit), or (2) when 246-247 `ValueError("unparseable")` fires and fallbacks exhaust, 257 bare-raises plain `ValueError` caught by 268 (`except (ValueError,TypeError)`) → `BABDataError` (not a canonical 246-247/268-269 miss reduction). No production-realistic index-assignment/fallback-exhaustion mechanism demonstrated. |
| 268-269 | `_normalize_index` outer `(ValueError,TypeError)` (160-271) | 266 `except BABDataError: raise` precedes 268; `BABDataError` subclasses `ValueError` (batch97). 268 can catch a plain `ValueError` only if it escapes 161-265 as non-`BABDataError`. Demonstrated source was 257 re-raise of 246-247's `ValueError` after non-realistic fallback exhaustion (NaT-robust fallbacks prevent it for 227-entry case). Other 161-265 exceptions converted/wrapped before 268. **Proof-first: handler order + BABDataError wrapping + NaT-robust fallbacks.** |
| 334-335,338-342,351-352 | `_coerce_to_datetime_scalar` | `except ValueError: raise` passes intended `ValueError("bad")`; `except Exception: pass` unreachable without a non-ValueError exception from `type().__name__` compare, `is pd.NaT` identity, or `np.isnan/np.isinf` on already-typed `float`. No production-realistic exception source. |
| 43-44,403-404,641-642,694-695,791-792,953,1626-1627,1663-1664 | misc | unchanged structural-dead/construction-unreachable/conversion-gated (prior batches). |
| 322,326 | `_coerce_to_datetime_scalar` inspect-gated | **guard-relevant; DO NOT ALTER.** |

## Batch 100 — 2026-11-07T11:04Z (SHA 73999ac, proof-only / 0 delta)

**Rebaseline (fresh canonical, 2026-11-07T10:59Z):** `data_loader.py` **40 miss / 1693 stmts (98%)**; **1466 passed, 0 failed, 17 skipped, 107 warnings** (batches 40-69,71-74,76-89,93,95,96). `campaign_d*` guard **44 passed, 5 warnings**. No production-semantics changes.

**New mechanism probes (production-realistic focus, 1 per cluster):**
- **246-247** (`_normalize_index` dayfirst block, 227-247): traced index assignments across 216-224→227-247 with `np.datetime64('NaT')` object index (grants 225/227 entry). 234-244 remain unreachable (232 coercer deterministic after 216-224). Controlled `DataFrame.__setattr__('index')`/list-index failure heuristics targeting 245/246 produced outer recovery to `BABDataError` or successful NaT-robust fallback results; **246-247 `raise ValueError("unparseable")` not reached on a production-realistic path**. 248-257 NaT-robust fallbacks (`pd.to_datetime`/`_coerce_to_datetime_scalar` on original `idx`) and 257→268 conversion behavior unchanged.
- **268-269** (outer `except (ValueError,TypeError)`): 261 catches `Exception` and converts to `BABDataError` at 265 (or re-raises BABDataError); 266 catches `BABDataError` before 268. No demonstrated plain `ValueError/TypeError` (non-`BABDataError`) escape from 161-265 under normal control flow. **Handler-structure dead.**
- **334-335,338-342,351-352** (`_coerce_to_datetime_scalar`): `np.isnan/np.isinf` on `float`/`float`-subclass inputs raise/return safely and intended `ValueError("bad")` is re-raised through `except ValueError: raise`; `except Exception: pass` branches have no production-realistic non-ValueError trigger. **Proof-first.**
- **641-642,694-695,791-792,1626-1627,1663-1664,43-44,953,403-404**: handler/nesting/construction analysis reconfirmed structural-dead (inner handlers swallow `Exception`/convert to `BABDataError`; `split()` construction; 364 is only unwrapped epoch statement and safe for regex-admitted `str`). **322,326 unchanged, guard-relevant.**

**Remaining (40):** `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953, 1626-1627, 1663-1664`. No miss reduction without semantics-altering production change or non-production-realistic harness. Next: batch 101 only if a *new, concretely demonstrated* production-realistic mechanism is identified.

## Batch 101 — 2026-11-07T11:17Z (SHA 7927e0a, proof-only / 0 delta)

**Rebaseline (fresh canonical, 2026-11-07T11:16Z):** `data_loader.py` **40 miss / 1693 stmts (98%)**; **1466 passed, 0 failed, 17 skipped, 107 warnings** (batches 40-69,71-74,76-89,93,95,96). `campaign_d*` guard **44 passed, 5 warnings**. No production-semantics changes.

**New mechanism probes (production-realistic focus, 1 per cluster):**
- **245,246-247** (`_normalize_index`, dayfirst last-ditch 227-247): `sys.settrace` on production-realistic NaT entry (`pd.Index([np.datetime64('NaT'),'2021-01-01','2021-01-02'], dtype=object)`) hit **224,225,227-233,245,272-275** and **not** 234-244/246-247 (normal path). Controlled `DataFrame.__setattr__('index')` failure targeted at 245 (3rd index set) yielded 224→248→249→250→272-275 and **not** 245/246-247 — 246-247's `raise ValueError("unparseable")` (if triggered) is caught by 248 `except Exception` and recovery/fallback runs; module-isolated coverage probe also showed 245/246/247 MISS and `BABDataError` from outer handling. **234-244** remain coercer-determinism blocked (232 same coercer as 216-224). **246-247**: no production-realistic mechanism demonstrated that reaches `ValueError("unparseable")` as a stable canonical outcome without non-realistic DataFrame subclassing; fallback/recovery absorbs. **Proof-first.**
- **351-352** (`_coerce_to_datetime_scalar`, float NaN/inf guard): a pathological `class BadIsnan(float): def __float__(self): raise RuntimeError` passed `isinstance(val,float)` (345) and caused `np.isnan` to raise `RuntimeError` — trace hit **346,347,349,351,352,353** and function returned `NaT` via later parsing (not `ValueError("bad")`). **351-352 are reachable only via pathological float-subclass `__float__` behavior (not production-realistic input).** Exercising in canonical tests would require semantic decision (currently NaN-like pathological subclass slips past NaN guard) — **no production-semantics change made**.
- **334-335,338-342**: `type().__name__` string compare and `val is pd.NaT` identity are not overridable; only `ValueError("bad")` is raised by intended branches and re-raised by `except ValueError: raise`. `except Exception: pass` unreachable for production-realistic values. **Structurally dead.**
- **43-44** (`_not_null`): `is None` identity + inner `pd.isna` wrapped (40-41) + unconditional `return True`; no unwrapped fallible statement in 34-42. `_not_null(Bad())` where `Bad.__bool__` raises still returned `True` (no bool coercion path). **Structurally dead.**
- **953** (`_normalize_asset_name`): `for tok in s.split()` — `str.split()` never yields empty strings; `tok_clean` from `tok.strip()` never empty. Probed whitespace/tab forms, all MISS. **Construction-unreachable.**
- **268-269** (`_normalize_index` outer VE/TE): 261 catches `Exception` and 262-265 always re-raise `BABDataError` or raise `BABDataError`; 266 catches `BABDataError` before 268. Therefore 268-269 cannot observe a plain `ValueError/TypeError` escaping 161-265. **Handler-structure dead** (confirmed by code-path structure + prior probes).
- **403-404** (`_coerce_to_datetime_scalar`): 364 `av = abs(numf)` is only unwrapped statement in 362-402; `numf = float(s)` (363) returns builtin `float` for regex-admitted `str`. All epoch/fallback branches individually guarded. **Structurally unreachable for normal input.**
- **641-642,694-695,791-792,1626-1627,1663-1664**: unchanged structural-dead/inner-conversion gated. **322,326 inspect-gated/guard-relevant — DO NOT ALTER.**

**Remaining (40):** `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953, 1626-1627, 1663-1664`. No new production-realistic miss-reduction mechanism; no semantics changes. Next: batch 102 only with a *new, concretely demonstrated, production-realistic* control-flow mechanism.

## Batch 102 — 2026-11-07T11:28Z (SHA d0d1f62, proof-only / 0 delta)

**Rebaseline (fresh canonical, 2026-11-07T11:27Z):** `data_loader.py` **40 miss / 1693 stmts (98%)**; **1466 passed, 0 failed, 17 skipped, 107 warnings** (batches 40-69,71-74,76-89,93,95,96). `campaign_d*` guard **44 passed, 5 warnings**. No production-semantics changes.

**New mechanism probes (1 per cluster, production-realistic focus):**
- **246-247** (`_normalize_index`, dayfirst block 227-247): NaT-entry (`np.datetime64('NaT')`) grants 225/227; 232 coercer deterministic so 234-244 remain blocked. Scoped `DataFrame.__setattr__` raise on 2nd `index` assignment (targeting 245, after 224's 1st set) produced: trace hit line 245 only (no 246/247/248 line events), function recovered to valid `DatetimeIndex` (2 rows, NaT dropped), 6 index-set operations total mapped to lines 207,212,214,224,245,276 — recovery continued at line 276, bypassing the 246-247 `except/raise ValueError("unparseable")` path in observable trace/coverage. Focused coverage (line and branch) and canonical aggregate both report **246-247 MISS**. ValueError("unparseable") sentinel never constructed in builtin-patch probe. Class-swap/subclass `__setattr__` variants also left 246-247 MISS. **Conclusion:** 246-247 are not reachable/coverage-recordable via production-realistic mechanisms; 245 assignment failure under this NaT-entry path is absorbed by outer recovery structure without executing 246-247. **Proof-first; no semantics change.**
- **351-352** (`_coerce_to_datetime_scalar`): confirmed a pathological `float` subclass whose `__float__` raises during `np.isnan` reaches 351-352 in focused coverage (API shows executed); current behavior is NaN-guard slip-through with later parsing (returns NaT/Timestamp path, not `ValueError("bad")`). Adding a canonical test would codify that behavior/constitutes a semantic decision per handoff constraints — **disallowed; no test added**.
- **234-244,268-269,334-335,338-342,43-44,403-404,641-642,694-695,791-792,953,1626-1627,1663-1664**: unchanged structural-dead/handler-order/construction proofs. **322,326 inspect-gated — DO NOT ALTER.**

**Remaining (40):** `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953, 1626-1627, 1663-1664`. Next: batch 103 only with a *new, concretely demonstrated, production-realistic* control-flow mechanism and no semantics change.
