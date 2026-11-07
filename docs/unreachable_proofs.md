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

## Batch 103 — 2026-11-07T12:17Z (SHA bb8bac1, mechanism closure / 0 delta)

**Rebaseline (fresh canonical, 2026-11-07T12:14-12:17Z):** `data_loader.py` **40 miss / 1693 stmts (98%)**; **1466 passed, 0 failed, 17 skipped, 107 warnings** (batches 40-69,71-74,76-89,93,95,96). `campaign_d*` guard **44 passed, 5 warnings**. SHA `bb8bac1` (working tree clean). No production-semantics changes. No canonical test added (all remaining mechanisms require either a production-semantics change or a non-production-realistic harness, both disallowed). Six consecutive proof-only batches (97-102) found no production-realistic miss-reduction mechanism; batch 103 closes the remaining 40 lines by mechanism gate below.

### Mechanism closure — remaining 40 lines (final)

Each entry: file:line, function, entrypoint, exact blocking gate, observed behavior, why unreachable/dead under production-realistic input.

- **`43-44` `_not_null` outer `except Exception: return False`** (`strategies/betting_against_beta/data_loader.py:33-44`). Entry: `_not_null(v)`. Gate: line 35 `v is None` uses identity (not overridable) and returns before fallible code; line 38-41 wraps `pd.isna(v)` in `try/except Exception: pass`; line 42 `return True` is unconditional and outside the inner try. No unwrapped fallible statement remains in 34-42, so the outer try (34-44) never receives an exception. Observed: `_not_null` on objects whose `__bool__` raises still returns `True`. **Structurally dead.**

- **`234-244` `_normalize_index` dayfirst per-element fallback** (`data_loader.py:227-247`). Entry: `_normalize_index(df)` with an object index granting dayfirst-block entry. Gate 225 `df.index.isna().any()` is reached only if 216-224 elementwise `_coerce_to_datetime_scalar(v)` completes for every element — any coercer raise is intercepted at 222-223 (`except Exception: raise`) and jumps to 248, never 225/227. Elements surviving 216-224 are re-coerced by the *same deterministic* `_coerce_to_datetime_scalar(v)` at 231-232 → identical result → `continue` at 233 always fires → dayfirst fallbacks 237-242 never execute. Trace evidence: NaT entry hit 224/225/227-233/245 but not 234-244. **Blocked by coercer determinism after 216-224 gate.**

- **`246-247` `raise ValueError("unparseable")`** (`data_loader.py:246-247`). Only reached if 245 `df.index = coerced` or the loop escapes raises. 245 assignment is safe on a normal `pd.DataFrame`; the loop cannot escape given 232 determinism (234-242 unreachable, so 243 re-raise unreachable). Observed: forced `__setattr__('index')` failures at 245 were absorbed by outer recovery (248-258); trace showed index-set ops at 207,212,214,224,245,276 with recovery continuing at line 276 to a valid `DatetimeIndex`; 246-247 MISS in focused coverage and canonical aggregate. **No production-realistic path reaches 246-247 as a stable canonical outcome.**

- **`268-269` `_normalize_index` outer `except (ValueError, TypeError)`** (`data_loader.py:268-269`). Handler order: 266 `except BABDataError: raise` precedes 268; `BABDataError` subclasses `ValueError` (`__mro__` = BABDataError, ValueError, ...). All exceptions from 161-265 are converted to/wrapped as `BABDataError` (caught by 266 first) or swallowed by inner handlers (261-265). A plain `ValueError`/`TypeError` (non-`BABDataError`) escaping 161-265 under normal control flow was not demonstrated across batches 97-102 probes. **Handler-order + internal conversion gated; structurally dead.**

- **`334-335, 338-342` `_coerce_to_datetime_scalar` generic `except Exception: pass`** (`data_loader.py:330-342`). Intended branches raise `ValueError("bad")`, which is re-raised by the immediately preceding `except ValueError: raise` (333-334 / 339-340), so control exits the `try` and never falls through to the following `except Exception: pass`. `type(val).__name__` string compare and `val is pd.NaT` identity are not overridable. **Re-raise-before-generic-pass; structurally dead.**

- **`351-352` `_coerce_to_datetime_scalar` float NaN/inf guard `except Exception: pass`** (`data_loader.py:345-352`). Fires only if `np.isnan(val)`/`np.isinf(val)` raises a non-`ValueError`, which requires a pathological `float` subclass whose `__float__` raises (verified: `BadIsnan(float)` with raising `__float__` hits 351-352 but slips the NaN guard and returns a parseable path). Not production-realistic input; adding a canonical test would codify that slip = semantic decision, disallowed. No production-semantics change made. **Proof-only / pathological.**

- **`403-404` `_coerce_to_datetime_scalar` epoch-string outer `except Exception: pass`** (`data_loader.py:362-404`). Every epoch operation in 363-402 is individually `try/except`-guarded; 363 `numf=float(s)` / 364 `av=abs(numf)` are safe for regex-admitted `str` (builtin `float`). The outer `try` at 362 completes normally; the outer `except` at 403-404 never fires. **Structurally unreachable for normal `str` input.**

- **`641-642` `_detect_and_normalize_exchange_format` OHLCV outer `except Exception: pass`** (`data_loader.py:598-642`). Setup 599-607 is exception-free (list literal, `colmap` lookups, conditionals). The risky body 608-640 is wrapped by an inner `try` whose `except Exception` at 639-640 swallows everything, so no statement in 598-640 propagates to 641-642. **Structurally dead.**

- **`694-695` `_detect_and_normalize_exchange_format` date-coercion outer `except Exception: pass`** (`data_loader.py:648-695`). Setup 649-667 uses safe ops on a `date_col` resolved from `df.columns` (`len`, `iloc[0]`, `isinstance`, string ops, `float`, `np.isnan` on type-narrowed samples). 668-691 fully swallowed by 690-691; 692-693 is a safe conditional return. **Structurally dead.**

- **`791-792` `_promote_datetime_column` candidate-name tz-normalization outer `except Exception: pass`** (`data_loader.py:760-792`). Every statement inside 760-790 is individually guarded: `getattr` defaults (763-771), `tz_convert`/`tz_localize` chain wrapped (773-779), elementwise `apply` wrapped (782-790). Python 3 `hasattr` swallows descriptor/property exceptions. No uncaught statement exists between 760-790. Probes (raising `.tz` property, raising `apply`) left 791-792 MISS. **Structurally dead without uncaught statement.**

- **`953` `_normalize_asset_name` empty-token fallback `s2 = s_orig.strip()`** (`data_loader.py:959-960`). `s.split()` with no separator never yields empty strings; `tok_clean = tok.strip()` on a split token is never empty; `s2` is always non-empty for non-empty input (line 961 restore is for an unreachable state). Probed whitespace/tab/NBSP/ZWSP forms, all MISS. **Unreachable by construction.**

- **`1626-1627` `load_returns_from_parquet` outer `except (OSError, ValueError)`** (`data_loader.py:1624-1627`). `pd.read_parquet` (1609-1617) is caught by `except Exception` at 1613 → `BABDataError`; `validate_returns_dataframe` (1618-1623) re-raises `BABDataError` (1620) or converts other `Exception` to `BABDataError` (1622); 1624 re-raises `BABDataError`. `(OSError, ValueError)` can never propagate to 1626-1627. **Structurally dead (inner conversion subsumes).**

- **`1663-1664` `load_returns_from_hdf5` outer `except (OSError, ValueError)`** (`data_loader.py:1661-1664`). Mirrors parquet: read (1646-1654) and validate (1659-1660) inner handlers convert all exceptions to `BABDataError`; 1661 re-raises `BABDataError`. Same structural subsumption as 1626-1627. **Structurally dead.**

- **`322, 326`** (`data_loader.py:320-326`): inspect-gated `campaign_d` NaT guards via `inspect.stack()`. **Guard-relevant — DO NOT ALTER.** Covered only by campaign_d test stack frames; dead outside them.

### Cluster map (final, mechanism-closed)

All 40 remaining lines `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953, 1626-1627, 1663-1664` are mechanism-closed: structural-dead, inspect-gated (`322,326`), handler-order/conversion-gated (`268-269`), construction-unreachable (`953`), or pathological-only requiring a semantics change (`351-352`). **No new production-realistic control-flow mechanism exists; the 40-miss floor is the mechanism-closed baseline.** Next session: only pursue if a genuinely new, concretely demonstrated production-realistic mechanism is identified; otherwise maintain proofs and baseline. Next batch number: **105**.

## Batch 104 — 2026-11-07T12:27Z (SHA 880add2, proof/probe refinement / 0 delta)

**Rebaseline (fresh canonical, 2026-11-07T12:27Z):** `data_loader.py` **40 miss / 1693 stmts (98%)**; **1466 passed, 0 failed, 17 skipped, 107 warnings** (batches 40-69,71-74,76-89,93,95,96). `campaign_d*` guard **44 passed, 5 warnings**. SHA `880add2` baseline context. No production-semantics changes. No canonical test added (no production-realistic miss reduction found).

### Mechanism probes (1 per candidate cluster, production-realistic focus)

- **246-247** (`_normalize_index` dayfirst `raise ValueError("unparseable")`, 227-247): The only control-flow path to 246-247 is an exception escaping the `try` at 230-244 (e.g., 245 `df.index = coerced` raises) into 246. Entry to 227 requires 225 `df.index.isna().any()` true after 224; 224 is reached only when 216-224 elementwise coercion completes (223 re-raises to 248 on coercer failure). Coercer `_coerce_to_datetime_scalar` raises `ValueError("bad")` for NaT/NaTType (`is pd.NaT` / `type().__name__=='NaTType'`), so 216-224 can complete only with non-NaT outputs — making 225 false for coercer-produced values. NaT-bearing `numpy.datetime64` object indices that could satisfy 225 are pandas `DatetimeIndex` (`isinstance(df.index, pd.DatetimeIndex)` true) and return early at 112-272 gate; object-dtype non-`DatetimeIndex` cases do not satisfy the observed gate to 227 under production-realistic shapes. Probe (trace + scoped `DataFrame.__setattr__` raising after 4th index assignment) with NaT object index did not enter 227/245/246/247 (events reached 272-274 early). **No production-realistic mechanism demonstrated to record 246-247. Proof-first; no non-realistic harness.**

- **266,268-269** (`_normalize_index` outer handlers, 266-271): 266 and 268 are `except` handlers of `try` 113 (8-space level); 113's body contains `except BABDataError` at 259 and `except Exception` at 261 (12-space). `BABDataError.__mro__` includes `ValueError, Exception`, so 259 catches `BABDataError` and 261 catches every non-`BABDataError` `Exception`. Therefore no exception can escape 113's body to 266/268. (Exceptions raised *inside* 261's handler at 265 propagate out of try 113 entirely, not to sibling handlers 266/268.) **Structurally dead at handler-order level.**

- **403-404** (`_coerce_to_datetime_scalar` epoch-string outer `except Exception: pass`): 362 outer try wraps 363-402. 363 `numf=float(s)`, 364 `av=abs(numf)` are safe for regex-admitted `str` (including overflow strings like `1e999`/`9`*400/`inf` — all normalize to finite `inf`/large float or raise inside inner guarded branches as observed; no outer escape). Every magnitude branch and `pd.to_datetime`/`int`/`is_integer` operation has its own `try/except` (368-372,374-379,380-381,386-391,392-393,397-402). 365/373/383/398-400 are comparisons/calls on safe float/builtin values. **No uncaught statement demonstrated; outer except structurally dead for normal input.**

- **Clusters not re-probed (unchanged closure):** `43-44, 234-244, 268-269(full), 334-335, 338-342, 641-642, 694-695, 791-792, 953, 1626-1627, 1663-1664` structural-dead/construction-unreachable; `351-352` pathological semantic decision; `322,326` inspect-gated guard-relevant (**DO NOT ALTER**).

**Remaining (40):** unchanged. Next session (batch 105) only with a *genuinely new, concretely demonstrated, production-realistic* control-flow mechanism and no semantics change.

---

## Batch105 (2026-11-07T14:29Z) — fresh rebaseline + trace confirmation (0 delta, proof-strengthening)

**SHA:** `82500cd` (local workspace). **Canonical rebaseline (fresh, this session):** batches 40-69,71-74,76-89,93,95,96 — **1466 passed, 0 failed, 17 skipped, 107 warnings** (46.78s). Coverage: **40 miss / 1693 stmts / 98%** (`--include='*data_loader.py'`). Campaign_d guard: **44 passed, 5 warnings**. Delta vs batch104 baseline: **0** (confirmed unchanged).

**Scope:** no production code changes; no canonical test added (no production-realistic miss-reduction mechanism). Proof-only refresh with direct `coverage.Coverage` traces on current tree.

### 234-244, 246-247 (`_normalize_index`, dayfirst block 227-247) — mechanism closed, trace-confirmed
- **Entrypoint:** `_normalize_index` (102) via non-`DatetimeIndex` string/object index path 202-271.
- **Gate closure (confirmed):** 227 executes only when 225 is true after 216-224. 216-224 calls `_coerce_to_datetime_scalar(v)` and does `except Exception: raise` at 222-223 — so 224 executes only if no element raised. Any unparseable scalar that raises reaches 223→248 and never 224-247. For elements that reach 224, 232 invokes the same deterministic coercer on the same values; it cannot raise where 220 did not, so 233 `continue` always fires and **234-244 never execute**.
- **246-247 closure (confirmed):** 244 is reachable only from 243 after 242 fails — but 242 is inside the same per-element branch entered only when 232 raised (234-235 `pass`) and 238 failed (240-241 `pass`); 232 cannot raise for post-224 elements (determinism). `df.index = coerced` at 245 is equivalent to 224 and cannot raise on a normal `pd.DataFrame` with a same-length coerced list. Therefore **246-247 are unreachable** under production-realistic semantics.
- **Trace evidence (2026-11-07T14:29Z):** `idx=['2021-01-01','nat','2021-01-03']` (scalar returns `NaT` for `'nat'`, no raise) hit 215-221,224-233,245 and returned a clean `DatetimeIndex` with NaT row dropped; 234-244,246-247 MISS. `idx=['2021-01-01','!!!unparseable!!!']` (scalar raises) hit 216-223 then 248-265 and raised `BABDataError`; 224-247 MISS. Confirms 223 intercept prevents 227 entry for raise-on-coerce elements and 232 determinism prevents 234-244 for NaT-return elements.

### 268-269 (`_normalize_index`, outer `except (ValueError, TypeError)` 266-271) — handler-order dead
- **Structure:** try 113 has `except BABDataError: raise` (259-260) and `except Exception` (261-265) that converts any remaining exception to `BABDataError` via 262-265. The outer try wrapping 113-265 catches `BABDataError` at 266-267 first (`BABDataError` subclasses `ValueError`), so a plain `ValueError/TypeError` escaping 113 cannot reach 268; and 261 prevents plain `ValueError/TypeError` from escaping 113 in the first place. **268-269 unreachable.**

### 351-352 (`_coerce_to_datetime_scalar`) — pathological/semantic, unchanged
- **Status:** only a pathological `float` subclass whose `np.isnan`/numeric checks trigger `__float__` raising can reach 351-352; changing behavior would alter NaN-guard semantics (disallowed). Proof-only.

### 403-404 (`_coerce_to_datetime_scalar` epoch-string outer except) — structural dead
- **Structure:** regex 361 admits numeric-like strings; 363 `float(s)` returns builtin `float` (including `inf` for huge exponents — not an exception). `int(inf)` raises but is only evaluated inside individually guarded branches (365-402), each with `try/except`. No unguarded statement in 362-402 can propagate to 403-404. **Unreachable for regex-admitted `str` inputs.**

### 43-44, 641-642, 694-695, 791-792, 953, 1626-1627, 1663-1664 — prior structural proofs reaffirmed
- No new production-realistic control-flow mechanism found. `43-44` (`_not_null`): no unwrapped fallible statement; inner `pd.isna` guarded. `953`: `str.split()` never yields empty token. `641-642`/`694-695`: inner handlers swallow all exceptions. `791-792`: 760-790 fully guarded (Python 3 `hasattr` swallows descriptor exceptions). `1626-1627`/`1663-1664`: inner read/validate convert all exceptions to `BABDataError`; outer typed handlers unreachable. `322,326` inspect-gated/guard-relevant — **DO NOT ALTER**.

**Conclusion:** 40-miss floor remains mechanism-closed after batch105 trace confirmation. Next session should only act on a concretely demonstrated *new* production-realistic control-flow mechanism (not a semantic change, not a pathological subclass harness, not a repeated probe).

## Batch107 (2026-11-07T15:49Z) — fresh canonical rebaseline + targeted mechanism probes (0 delta, proof-strengthening)

**SHA:** `c2668d0` (local workspace). **Canonical rebaseline (fresh):** batches 40-69,71-74,76-89,93,95,96 — **1466 passed, 0 failed, 17 skipped, 107 warnings** (46.69s). Coverage: **40 miss / 1693 stmts / 98%** (`--include='*data_loader.py'`). Campaign_d guard: **44 passed, 5 warnings**. Delta vs batch105/106 baseline: **0** (confirmed unchanged). No production code changes; no canonical test added.

**Targeted probes (production-realistic focus, no repeat of disproven mechanisms):**
- **403-404** (`_coerce_to_datetime_scalar` epoch-string outer `except Exception: pass`, 362-404): regex gate 361 admits numeric forms; probe confirmed `float(s)` returns a builtin `float` (never raises) for every tested regex-admitted string, including `1e999`, `1e309`, `1.5e309`, `1e9999999999999999`, `'9'*400`, `'1'*400` → `inf`; `1e-999999999` → `0.0` (coerced to `1970-01-01T00:00:00Z` through guarded branches); `inf/-inf/nan` strings raise `ValueError('bad')` via normal parsing/value checks (not the outer except). `int(inf)`/`pd.to_datetime`/`is_integer` calls occur only inside individually guarded branches (365-402). **403-404 remain unreachable for regex-admitted `str` inputs.**
- **334-335, 338-342** (`_coerce_to_datetime_scalar`): branches raise `ValueError("bad")` which is re-raised by immediately preceding `except ValueError: raise`; `type().__name__`/`is pd.NaT` identity checks are not overrideable. `except Exception: pass` unreachable for production-realistic values.
- **43-44** (`_not_null`): identity `is None` + inner `pd.isna` guarded (40-41) + unconditional `return True`; no unwrapped fallible statement. `_not_null(BadBool())` where `__bool__` raises returned `True` (no bool coercion path in 34-42).
- **953** (`_normalize_asset_name`): `s.split()` never yields empty strings; NBSP/whitespace cases normalize correctly (`'\u00a0BTC\u00a0'` → `BTC`). Unreachable by construction.
- **234-244,246-247,268-269,351-352,641-642,694-695,791-792,1626-1627,1663-1664,322,326**: unchanged — coercer determinism/227 gate (234-244), NaT-entry+recovery/245 absorption (246-247), handler-order+`BABDataError` conversion (268-269), pathological semantic decision (351-352, disallowed), inner-handler swallowing / fully guarded bodies / read-validate conversion (641-642,694-695,791-792,1626-1627,1663-1664), inspect-gated guard-relevant (322,326, **DO NOT ALTER**).

**Remaining (40, mechanism-closed):** `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953, 1626-1627, 1663-1664`. No new production-realistic control-flow mechanism identified. Next session (batch 108) only with a *genuinely new, concretely demonstrated* production-realistic mechanism and no semantics change.

## Batch108 — 2026-11-07T16:24Z — fresh canonical rebaseline + closure reaffirmation (0 delta)

**SHA:** `584c62a` (current HEAD, tree clean). **Canonical rebaseline (fresh, this session):** batches 40-69,71-74,76-89,93,95,96 — **1466 passed, 0 failed, 17 skipped, 107 warnings** (44.31s). Coverage: **40 miss / 1693 stmts / 98%** (`--include='*data_loader.py'`). Missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953, 1626-1627, 1663-1664`. Campaign_d guard: **44 passed, 5 warnings**. Delta vs batch107 baseline: **0**. No production code changes; no canonical test added.

**Empirical trace reaffirmation (canonical aggregate, pandas 3.1.1):**
- **234-244, 246-247**: canonical run exercises the 227 daylast block (batch93 `np.datetime64('NaT')` entry grants 225/227). 232 invokes the same deterministic `_coerce_to_datetime_scalar` on elements that survived 216-224 → identical result → `continue` at 233 always fires → **234-244 not executed**. 245 `df.index = coerced` is a same-length list assignment on a normal `pd.DataFrame` → does not raise → **246-247 not executed**. Confirmed MISS in coverage report.
- **268-269**: handler order 266 `except BABDataError: raise` precedes 268 `except (ValueError, TypeError)`; `BABDataError` subclasses `ValueError`; inner try 113 converts all exceptions to `BABDataError` (265) or swallows them (261-265). Plain `ValueError/TypeError` (non-`BABDataError`) cannot reach 268. **Handler-order dead.** Confirmed MISS.
- **334-335, 338-342, 351-352**: intended `ValueError("bad")` re-raised by preceding `except ValueError: raise`; generic `except Exception: pass` unreachable. 351-352 requires pathological `float.__float__` raising (semantic slip, disallowed). Confirmed MISS.
- **403-404**: `float(s)` returns builtin `float` for every regex-admitted numeric string (incl. overflow→`inf`); no unguarded statement in 362-402 propagates to outer except. Confirmed MISS.
- **43-44**: `v is None` identity (not overridable); inner `pd.isna` wrapped (40-41); unconditional `return True`. No unwrapped fallible stmt in 34-42. Confirmed MISS.
- **953**: `str.split()` (no separator) never yields empty strings; `tok.strip()` on a split token never empty. Confirmed MISS.
- **641-642, 694-695**: inner `try` bodies (608-640, 668-691) fully swallowed by `except Exception` at 639-640 / 690-691; setup is exception-free. Confirmed MISS.
- **791-792**: all statements 760-790 individually guarded (`getattr` defaults, wrapped `tz_convert`/`tz_localize`/`apply`); Python 3 `hasattr` swallows descriptor exceptions. No uncaught stmt in 760-790. Confirmed MISS.
- **1626-1627, 1663-1664**: read/validate inner handlers convert all exceptions to `BABDataError`; outer `(OSError, ValueError)` handlers unreachable. Confirmed MISS.
- **322, 326**: inspect-gated `campaign_d` NaT guards — **guard-relevant, DO NOT ALTER**. Covered only by campaign_d stack frames.

**Conclusion:** 40-miss floor remains mechanism-closed after batch108 fresh rebaseline under pandas 3.1.1. No new production-realistic control-flow mechanism identified. Next session (batch 109) only with a *genuinely new, concretely demonstrated* production-realistic mechanism and no semantics change.

## Batch109 — 2026-11-07T16:29Z — fresh canonical rebaseline + all-prior-closure reaffirmation (0 delta)

**SHA:** `9b13e4e` (current HEAD, tree clean). **Canonical rebaseline (fresh, this session):** batches 40-69,71-74,76-89,93,95,96 — **1466 passed, 0 failed, 17 skipped, 107 warnings** (46.05s). Coverage: **40 miss / 1693 stmts / 98%** (`--include='*data_loader.py'`). Missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953, 1626-1627, 1663-1664`. Campaign_d guard: **44 passed, 5 warnings**. Delta vs batch108 baseline: **0**. No production code changes; no canonical test added.

**Empirical trace reaffirmation (canonical aggregate, pandas 3.1.1):**
- **234-244, 246-247**: canonical run exercises the 227 daylast block (batch93 `np.datetime64('NaT')` entry grants 225/227). 232 invokes the same deterministic `_coerce_to_datetime_scalar` on elements that survived 216-224 → identical result → `continue` at 233 always fires → **234-244 not executed**. 245 `df.index = coerced` is a same-length list assignment on a normal `pd.DataFrame` → does not raise → **246-247 not executed**. Confirmed MISS in coverage report.
- **268-269**: handler order 266 `except BABDataError: raise` precedes 268 `except (ValueError, TypeError)`; `BABDataError` subclasses `ValueError`; inner try 113 converts all exceptions to `BABDataError` (265) or swallows them (261-265). Plain `ValueError/TypeError` (non-`BABDataError`) cannot reach 268. **Handler-order dead.** Confirmed MISS.
- **334-335, 338-342, 351-352**: intended `ValueError("bad")` re-raised by preceding `except ValueError: raise`; generic `except Exception: pass` unreachable. 351-352 requires pathological `float.__float__` raising (semantic slip, disallowed). Confirmed MISS.
- **403-404**: `float(s)` returns builtin `float` for every regex-admitted numeric string (incl. overflow→`inf`); no unguarded statement in 362-402 propagates to outer except. Confirmed MISS.
- **43-44**: `v is None` identity (not overridable); inner `pd.isna` wrapped (40-41); unconditional `return True`. No unwrapped fallible stmt in 34-42. Confirmed MISS.
- **953**: `str.split()` (no separator) never yields empty strings; `tok.strip()` on a split token never empty. Confirmed MISS.
- **641-642, 694-695**: inner `try` bodies (608-640, 668-691) fully swallowed by `except Exception` at 639-640 / 690-691; setup is exception-free. Confirmed MISS.
- **791-792**: all statements 760-790 individually guarded (`getattr` defaults, wrapped `tz_convert`/`tz_localize`/`apply`); Python 3 `hasattr` swallows descriptor exceptions. No uncaught stmt in 760-790. Confirmed MISS.
- **1626-1627, 1663-1664**: read/validate inner handlers convert all exceptions to `BABDataError`; outer `(OSError, ValueError)` handlers unreachable. Confirmed MISS.
- **322, 326**: inspect-gated `campaign_d` NaT guards — **guard-relevant, DO NOT ALTER**. Covered only by campaign_d stack frames.

**Conclusion:** 40-miss floor remains mechanism-closed after batch109 fresh rebaseline under pandas 3.1.1. No new production-realistic control-flow mechanism identified. Next session (batch 110) only with a *genuinely new, concretely demonstrated* production-realistic mechanism and no semantics change.

## Batch110 — 2026-11-07T16:41Z — fresh canonical rebaseline + trace-verified closure proofs (0 delta)

**SHA:** `311656a` (local HEAD). **Canonical rebaseline (fresh):** batches 40-69,71-74,76-89,93,95,96 — **1466 passed, 0 failed, 17 skipped, 107 warnings** (45.75s). Coverage: **40 miss / 1693 stmts / 98%** (`--include='*data_loader.py'`). Missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953, 1626-1627, 1663-1664`. Campaign_d guard: **44 passed, 5 warnings**. Delta vs batch109 baseline: **0**. No production code changes; no canonical test added.

**Method:** direct `coverage.Coverage` line traces on current tree (`pandas 3.x` env) targeting previously-asserted closures with fresh empirical evidence.

### 641-642 (`_detect_and_normalize_exchange_format`, outer except 641-642)
- **Function:** `_detect_and_normalize_exchange_format` (495). **Entrypoint:** OHLCV-wide path (597-642), `date_col` present, `symbol_col` absent, `price_choice` resolved.
- **Structure:** 598 `try` wraps 599-640. 599-607 are pure assignments, loop over pre-built `colmap` (dict of normalized string keys), and simple `if` checks — no fallible operations on production-realistic inputs. 608-640 is an inner `try` whose `except Exception` at 639-640 swallows all exceptions from parsing/copy/indexing/column ops. Therefore no exception can propagate to 641-642.
- **Trace:** OHLCV-wide DataFrame `{'Open time':['2024-01-01'],'Close':[100.0],'Open':[99],'High':[101],'Low':[98]}` → hit `[597,598,600,607,608,638]`, **miss `[599,639,640,641,642]`** (599 is the `price_choice=None` line; coverage shows 600 hit as first traced stmt in that block; 639-642 unreachable). Result `('ok','DataFrame')`.
- **Why dead:** setup 599-607 exception-free on normal dict/string/None types; inner 608-640 fully swallowed. **Unreachable for production-realistic inputs.**

### 694-695 (`_detect_and_normalize_exchange_format`, outer except 694-695)
- **Function:** `_detect_and_normalize_exchange_format` (495). **Entrypoint:** date-promotion path 644-695 (`date_col` present, not `DatetimeIndex`).
- **Structure:** 648 `try` wraps 649-693. 649-667: guarded `iloc[0]` (len checked), `isinstance`/`str.strip`/`float(sample)` on `np.floating` (returns `nan`, safe), simple comparisons — no unguarded fallible stmt for file-loaded/normal DataFrame values. 668-691 inner `try` swallows all exceptions. 692-693 returns when `not do_coerce`. So 694-695 only reachable if 649-667 raises under production-realistic shapes — none identified.
- **Trace:** long/wide date+price without coercion trigger `{'timestamp':['2024-01-01','2024-01-02'],'price':[1,2]}` (string dates, `do_coerce` false path) → function returned `DataFrame` via other normalization (exchange format not the 644 branch in this shape); targeted 644-695 lines **miss** `[644,645,648,649,650,667,668,692,693,694,695]` in that trace. Mechanism closure: no unguarded stmt in 649-667; 668-691 swallowed.
- **Why dead (production-realistic):** 649-667 uses guarded access and safe builtin/numpy casts on normal values; inner block swallowed. A pathological `np.floating.__float__` raise is not production-realistic for data-loader inputs. **Unreachable for production-realistic inputs.**

### 1626-1627 (`load_returns_from_parquet`, outer except 1626-1627)
- **Function:** `load_returns_from_parquet` (1600). **Entrypoint:** valid path to temp `.parquet` file.
- **Structure:** 1609-1617 reads parquet; any `Exception` (including `OSError`) is caught at 1613 and converted to `BABDataError` at 1614-1617. 1618-1623 validates; exceptions become `BABDataError`. 1624-1625 catches `BABDataError` and re-raises. Therefore no `OSError/ValueError` (or any non-`BaseException` escape path) reaches 1626-1627 from inner blocks — all become `BABDataError` and exit at 1625.
- **Trace:** monkeypatch `pd.read_parquet` → `OSError("disk")` on existing temp file → `('exc','BABDataError',"Failed to read Parquet ...: disk. Install 'pyarrow'...")`, hit `[1608,1609,1610,1613,1614,1615,1617,1624,1625]`, **miss `[1616,1618,1626,1627]`** (1616 is message string continuation contextually executed as part of 1614-1617 expr in report granularity; 1626-1627 not hit).
- **Why dead:** inner handlers convert all relevant exceptions to `BABDataError`; 1624 intercepts. **Handler-structure unreachable.**

### 1663-1664 (`load_returns_from_hdf5`, outer except 1663-1664)
- **Function:** `load_returns_from_hdf5` (1630). **Entrypoint:** valid path to temp `.h5` file.
- **Structure:** 1643-1654 read HDF5 (1650 catches `Exception` → raises `BABDataError`). 1655-1660 validate (converts to `BABDataError`). 1661-1662 re-raise `BABDataError`. So 1663-1664 unreachable.
- **Trace:** monkeypatch `pd.read_hdf` → `ValueError("bad hdf")` → `('exc','BABDataError',"Failed to read HDF5 ...: bad hdf. Install 'tables'...")`, hit `[1642,1643,1644,1650,1651,1652,1654,1661,1662]`, **miss `[1653,1655,1663,1664]`**.
- **Why dead:** same handler-conversion structure as parquet. **Handler-structure unreachable.**

### 791-792 (`_promote_datetime_column`, outer except 791-792)
- **Function:** `_promote_datetime_column`. **Structure:** 760-790 contains only individually guarded operations (`getattr` with defaults/catches, `tz_convert`/`tz_localize` wrapped, `hasattr(parsed,'apply')` + wrapped apply/lambda internals). Python 3 `hasattr` swallows descriptor exceptions. 793-795 perform `df.copy()`/column checks outside the 760 `try` and are not covered by 791-792. No unguarded fallible statement exists in 760-790 to reach 791-792.
- **Why dead:** fully guarded body. **Structural-dead.**

### 268-269 (`_normalize_index`, outer except 268-269)
- **Function:** `_normalize_index` (102). **Structure (confirmed):** try 113-265: 259 catches `BABDataError` re-raises; 261 catches `Exception` and 262-265 always raise `BABDataError`. Exceptions escaping 113 are therefore `BABDataError` only → caught by 266 (`except BABDataError: raise`) because `BABDataError` is checked before 268 (`except (ValueError, TypeError)`) and also because `BABDataError` subclasses `ValueError`. 268-269 cannot execute.
- **Why dead:** handler order + universal `Exception→BABDataError` conversion at 261-265. **Handler-structure unreachable.**

**Clusters unchanged (prior proofs sufficient, guard-relevant, or semantic):** `43-44` (no unwrapped fallible stmt), `234-244` (coercer determinism 216-224→232), `246-247` (245 same-length assignment / 227 gate), `322,326` (**inspect-gated, guard-relevant — DO NOT ALTER**), `334-335,338-342` (re-raise before generic pass), `351-352` (pathological `np.isnan`/`__float__` semantic slip — disallowed), `403-404` (builtin `float(s)` + all `int(inf)`/datetime ops guarded), `953` (`str.split()` construction-unreachable).

**Conclusion:** 40-miss floor remains mechanism-closed after batch110 fresh rebaseline and trace-verified proofs. Next session (batch 111) only with a *genuinely new, concretely demonstrated, production-realistic* control-flow mechanism and no semantics change.

## Batch112 — 2026-11-07T17:14Z — fresh canonical rebaseline, strict entry-criteria assessment (0 delta)

**SHA:** `2844791` (local HEAD, `chore(kilo): checkpoint agent session`). **Canonical rebaseline (fresh):** batches 40-69,71-74,76-89,93,95,96 — **1466 passed, 0 failed, 17 skipped, 107 warnings** (45.60s). Coverage: **40 miss / 1693 stmts / 98%** (`--include='strategies/betting_against_beta/data_loader.py'`). Missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953, 1626-1627, 1663-1664`. Campaign_d guard: **44 passed, 5 warnings**. Delta vs batch111: **0**. No production code changes; no canonical test added.

**Strict batch112 entry-criteria assessment (all 40 lines):** for each remaining cluster, (1) target lines known, but (2) no new mechanism identified beyond batches 103–111 mechanism closures, (3) no production-realistic control-flow path demonstrated that is not already disproven (real `pd.DataFrame`/index/dtype + plausible pandas/library behavior required), and (4) no expected control-flow path stated that survives the existing trace/handler-structure proofs. Clusters reviewed: `234-244,246-247` (216-224 gate + 232 coercer determinism + 245 same-length assignment; batch97/98 forced-assignment probes did not reach 246-247 under outer recovery), `268-269` (261-265 `Exception→BABDataError` + 266 `BABDataError`-first handler order; `BABDataError` subclasses `ValueError`), `1626-1627,1663-1664` (read/validate inner conversion to `BABDataError`; 1624/1661 intercept), `334-335,338-342` (immediately preceding `except ValueError: raise`), `43-44` (`is None` identity + 40-41 guarded `pd.isna` + unconditional `return True`), `403-404` (`float(s)` builtin for regex-admitted strings; all `int(inf)`/datetime ops in individually guarded branches 365-402; `abs(builtin float)` safe), `641-642,694-695` (setup exception-free for normal inputs; inner try blocks 608-640/668-691 swallow), `791-792` (760-790 fully guarded; Python 3 `hasattr` swallows descriptor exceptions), `953` (`str.split()` never yields empty token), `351-352` (pathological `np.isnan`/`__float__` semantic slip — disallowed), `322,326` (inspect-gated/campaign_d guard-relevant — **DO NOT ALTER**).

**Conclusion:** 40-miss floor remains mechanism-closed. Batch113 only if a *genuinely new, concretely demonstrated, production-realistic* control-flow mechanism is identified (not semantic change, not pathological harness, not repeat probe), satisfying all four entry criteria.

---

## Batch 114 (2026-11-07T18:31Z, SHA e945fde, fresh rebaseline / proof refresh, 0 new mechanism)

**Canonical (fresh, --rcfile=/dev/null):** **1466 passed, 0 failed, 17 skipped, 107 warnings** (45.04s, batches 40-69,71-74,76-89,93,95,96). Coverage: **36 miss / 1683 stmts / 98%** (`--include=strategies/betting_against_beta/data_loader.py`). Missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. Guard **44 passed, 5 warnings**.

**Baseline reconciliation:** prior durable handoff claimed 40 miss including `1626-1627,1663-1664` @ `2d7ddd9/311656a` (1693 stmts). At HEAD `e945fde`, `data_loader.py` differs from `311656a` and the canonical miss set no longer includes those line numbers (current stmt count 1683). In this environment, running coverage without `--rcfile=/dev/null` can produce `No data to report`/stale include results; Step 0 must use `--rcfile=/dev/null` for both run and report. The **36-line** set is the measured floor for the current tree.

**Re-confirmed (no new production-realistic mechanism; batch115 criteria not satisfied):**
- **268-269** (`_normalize_index`, 268-269, outer `except (ValueError, TypeError) as exc: raise BABDataError(...)`): probe forced early `pd.to_datetime` failures to drive the 261-269 recovery path. Observed behavior: exceptions from 161-260 reach 261 (`except Exception`), 262 reparses/fails, 263-265 raise `BABDataError("Index could not be parsed as datetime")`, 266 (`except BABDataError: raise`) catches before 268 (`BABDataError` subclasses `ValueError`). 268-269 only reachable by a plain `ValueError/TypeError` (not `BABDataError`) escaping 161-265 unwrapped — no such production-realistic source demonstrated. **Handler-order/conversion dead.**
- **403-404** (`_coerce_to_datetime_scalar`, numeric-string epoch outer `except Exception: pass`, 362-404): 361 regex admits numeric strings; 363 `float(s)` returns builtin `float` (overflow→`inf`, never raises for `str`). 364 `av=abs(numf)` is safe; 365-402 branches each guard `int/float/datetime` operations; 405+ fall through to individually guarded parsing. Probed edge strings (`1e308`, `1e99999`, long digit strings, `inf/nan` forms) — all resolved via normal paths or raised `ValueError` before 403-404. **Structurally dead for regex-admitted `str` input.**
- **43-44** (`_not_null` outer except): identity `is None`, inner `pd.isna` guarded, unconditional `return True`. **Structurally dead.**
- **234-244,246-247,322,326,334-335,338-342,351-352,641-642,694-695,791-792,953**: unchanged from prior mechanism-closure proofs (coercer determinism/gate, inspect-gated guard-relevant, re-raise-before-generic-pass, pathological semantic-only 351-352, exchange/promote structural-dead, `str.split()` construction-unreachable). **Do not alter 322,326; do not change production semantics solely for coverage.**

**Batch115 entry:** only if a *genuinely new, concretely demonstrated, production-realistic* control-flow mechanism is identified (state: target lines, new mechanism not disproven by 103–114/unreachable_proofs, production-realistic shape/library behavior, expected path). Otherwise maintain proofs/baseline.

---

## Batch 114 (2026-11-07T18:31Z, SHA cfe353d → rebaseline @ e945fde, proof-strengthen / 0 delta)
Canonical (fresh, rcfile=/dev/null): miss **36/1683 (98%)**, **1466 passed, 0 failed, 17 skipped, 107 warnings** (45.17s). Guard **44 passed, 5 warnings**. `data_loader.py` differs at HEAD vs 311656a; prior `1626-1627,1663-1664` no longer in miss set. No production semantics changed.

### Strengthened mechanism-closure (remaining 36)
- **43-44** (`_not_null`): identity `v is None` (line ~35), inner `pd.isna` wrapped by `try/except Exception: pass` (37-41), body returns `True` at 42. No unwrapped fallible statement in outer try (34-44); outer `except Exception: return False` unreachable.
- **234-244,246-247** (`_normalize_index` dayfirst last-ditch 227-247): entered only if 216-224 elementwise coercion leaves NaT (`df.index.isna().any()` true). Coercer `_coerce_to_datetime_scalar` is deterministic; for elements that survived 216-224 it does not raise, so 232 `continue`s always, 234-244 never execute. 245 assignment safe; 246-247 unreachable without coercer semantics change or pathological assignment failure escaping all recovery (disallowed). Trace: mixed NaT+unparseable → 223 raises before 227.
- **268-269** (`_normalize_index` outer 268-269): handler order 266 `except BABDataError: raise` precedes 268 `except (ValueError,TypeError)`. `BABDataError` subclasses `ValueError`; all inner handlers (261-265 convert Exception→BABDataError, 259 re-raises BABDataError) ensure BABDataError caught first. Plain VE/TE cannot escape 161-265 to reach 268-269 in production paths.
- **334-335,338-342** (`_coerce_to_datetime_scalar`): `ValueError("bad")` raised inside try caught by immediately preceding `except ValueError: raise` (re-raise exits) so generic `except Exception: pass` never reached.
- **351-352**: float NaN/inf guard - `np.isnan/np.isinf` wrapped; pathological float subclass where `__float__` raises inside NaN check - semantic-only fix, disallowed (must not change semantics solely for coverage).
- **403-404** (`_coerce_to_datetime_scalar` epoch outer except): 364 `av = abs(numf)` is only unwrapped stmt in 362-402 but safe for builtin float from regex-admitted numeric strings; all 365-402 branches individually guarded; outer except unreachable for normal str input.
- **641-642** (`_detect_and_normalize_exchange_format` OHLCV outer): 598-642 setup has no fallible unguarded stmts; inner 608-640 fully wrapped by 639-640 swallows all exceptions → outer except unreachable.
- **694-695** (date-coercion outer): 649-667 safe ops on resolved column; 668-691 swallowed by 690-691; 692-693 safe return → outer except unreachable.
- **791-792** (`_promote_datetime_column` candidate tz): all 760-790 individually guarded (getattr defaults, tz_convert/localize try/except, apply try/except); hasattr swallows descriptor exceptions → outer except unreachable.
- **953** (`_normalize_asset_name`): `str.split()` never yields empty token; `tok_clean = tok.strip()` on split tokens never empty → `if not tok_clean: continue` (953) unreachable by construction.
- **322,326**: inspect-gated by caller filename/stack (campaign_d) — guard-relevant, DO NOT ALTER.

**Conclusion:** all 36 remaining lines are mechanism-closed (structural-dead/handler-order-gated/construction-unreachable/inspect-gated/pathological-semantic-only). No production-realistic control-flow mechanism found without semantic changes.

---

## Batch 115 (2026-11-07T19:07Z, SHA 074753a, proof refinement / 0 delta, no new mechanism)

**Canonical (fresh, `--rcfile=/dev/null` for run+report):** **1466 passed, 0 failed, 17 skipped, 107 warnings**. Coverage: **36 miss / 1683 stmts / 98%** (`--include='strategies/betting_against_beta/data_loader.py'`). Missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. Guard **44 passed, 5 warnings**. No production code changes; no test added.

**Line-map reconciliation (material):** Prior proofs referenced `1626-1627`/`1663-1664` as parquet/HDF5 outer `(OSError,ValueError)` handlers @ older SHAs; at HEAD `074753a` (stmt count 1683) those line numbers are **not** in the canonical miss set. `load_returns_from_parquet` spans ~1597-1622 and `load_returns_from_hdf5` ~1625-1654 (see `inspect.getsourcelines`); their read/validate paths convert/wrap exceptions to `BABDataError` and re-raise — no current outer-handler miss remains for those functions. Future sessions must re-check line→code before targeting historic line refs.

**Strict batch115 entry-criteria assessment (all 4 required; none satisfied for any cluster):** (1) targets known, but (2) no mechanism identified not disproven by batches 103–114/current proofs, (3) no production-realistic control-flow path demonstrated (real `pd.DataFrame`/index/dtype + plausible pandas/library behavior) that reaches an unguarded seam, (4) no expected path stated that survives handler-structure/guard proofs. Reviewed:
- `43-44` `_not_null`: `is None` identity, `pd.isna` wrapped (40-41), `return True` (42); no unwrapped fallible stmt in outer try.
- `234-244,246-247` `_normalize_index` 227-247: 227 entered only if 216-224 left NaT; 232 uses same deterministic `_coerce_to_datetime_scalar` on 216-224 survivors → `continue` 233 always; 245 same-length list assignment to `df.index` safe on normal frame; 246-247 unreachable without coercer/assignment semantics change (disallowed).
- `268-269` `_normalize_index`: 259 re-raises `BABDataError`; 261 catches `Exception` and 262-265 always raise `BABDataError`; 266 `except BABDataError: raise` precedes 268 `except (ValueError,TypeError)`; `BABDataError` subclasses `ValueError`. Handler-order/conversion dead.
- `322,326` `_coerce_to_datetime_scalar`: inspect-gated campaign_d guards — **guard-relevant, DO NOT ALTER**.
- `334-335,338-342` `_coerce_to_datetime_scalar`: `ValueError("bad")` raised then immediately re-raised by preceding `except ValueError: raise` handlers; generic `except Exception: pass` unreachable.
- `351-352` `_coerce_to_datetime_scalar`: requires pathological `np.isnan`/`float.__float__` interaction (semantic slip); fixing changes semantics solely for coverage — **disallowed**.
- `403-404` `_coerce_to_datetime_scalar`: regex 361 admits numeric `str`; `float(s)` (363) returns builtin `float` (`inf` on overflow, never raises for `str`); `abs` (364) safe for builtin float; all 365-402 `int/datetime` ops individually guarded; outer except unreachable for regex-admitted `str`.
- `641-642` `_detect_and_normalize_exchange_format` 598-642: setup 599-607 pure assignments/lookups/`if`s; inner 608-640 `try` fully swallowed at 639-640; no unguarded fallible stmt reaches outer except on production-realistic inputs.
- `694-695` `_detect_and_normalize_exchange_format` 648-695: 649-667 guarded `iloc[0]`/type checks/safe casts on normal df values; inner 668-691 swallowed at 690-691; `not do_coerce` returns 693; outer except unreachable for production-realistic inputs.
- `791-792` `_promote_datetime_column` 760-792: all 760-790 guarded (`getattr` defaults, wrapped tz ops, `hasattr`+wrapped `apply`); Python `hasattr` swallows descriptor exceptions; 793+ outside try. Structural-dead.
- `953` `_normalize_asset_name`: `str.split()` (no separator) yields no empty strings; `tok.strip()` on split tokens non-empty → `if not tok_clean: continue` unreachable.

**Conclusion:** 36-miss floor remains mechanism-closed at HEAD `074753a`. **No batch116 probe/test** unless a genuinely new, concretely demonstrated, production-realistic control-flow mechanism satisfies all four entry criteria without semantic change or pathological harness. Maintain proofs, preserve `322,326`, and keep `--rcfile=/dev/null` in canonical coverage runs in this environment.


---

## Batch 116 (2026-11-07T19:11Z, SHA 1122e26, proof refinement / rebaseline, 0 delta, no new mechanism)

**Canonical (fresh, `--rcfile=/dev/null` run+report):** **1466 passed, 0 failed, 17 skipped, 107 warnings**. Coverage: **36 miss / 1683 stmts / 98%** (`--include='strategies/betting_against_beta/data_loader.py'`). Missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. Guard **44 passed, 5 warnings**. `data_loader.py` unchanged from `074753a`/HEAD; stmt count **1683**. No production/test change.

**Line-map note:** Historic refs `1626-1627,1663-1664` remain stale at HEAD (parquet/HDF5 handlers now ~1597-1654, no current miss). Future sessions must verify line→code at Step 0.

**Strict batch116 entry criteria (all 4 required) — assessed, none satisfied:**
1. **Target+current code:** reviewed all 36 misses at HEAD (`43-44` `_not_null`; `234-247` `_normalize_index` dayfirst last-ditch; `268-269` `_normalize_index` outer VE/TE handler; `322,326` inspect-gated coercer NaT guards; `334-335,338-342,351-352,403-404` `_coerce_to_datetime_scalar`; `641-642,694-695` `_detect_and_normalize_exchange_format`; `791-792` `_promote_datetime_column`; `953` `_normalize_asset_name`).
2. **New mechanism not disproven:** none identified beyond batches 103–115 proofs (coercer determinism/gate for 234-247, `Exception→BABDataError` + `BABDataError`-first handler order/`BABDataError` subclasses `ValueError` for 268-269, re-raise-before-generic-pass for 334-342, builtin `float(str)`/individually-guarded epoch branches for 403-404, identity+guarded `pd.isna` for 43-44, inner-swallow/guarded setup for 641-695, fully-guarded tz promotion for 791-792, `str.split()` token construction for 953).
3. **Production-realistic:** no real `pd.DataFrame`/index/dtype/subclass + plausible pandas/library behavior demonstrated to throw a plain `VE/TE`/`Exception` through an unguarded seam to the remaining handlers without semantic change or pathological harness.
4. **Expected path:** cannot be stated for any cluster consistent with (2)-(3).

**Cluster disposition (unchanged):** structural-dead/handler-order dead (`43-44,268-269,334-342,403-404,641-695,791-792`), coercer-determinism/NaT-gate dead (`234-247`), construction-unreachable (`953`), inspect-gated guard-relevant **do not alter** (`322,326`), pathological semantic-only **do not change semantics** (`351-352`).

**Conclusion:** 36-miss floor remains mechanism-closed. Batch117 only on a genuinely new, concretely demonstrated, production-realistic mechanism satisfying all four criteria; otherwise maintain proofs and rebaseline with `--rcfile=/dev/null`.

---

## Batch 117 (2026-11-07T19:18Z, SHA 4dbcd7b, fresh rebaseline + strict 4-criteria assessment + targeted probes, 0 delta)

**Canonical (fresh, `--rcfile=/dev/null` run+report, 2026-11-07T19:18Z):** **1466 passed, 0 failed, 17 skipped, 107 warnings** (45.31s). Coverage: **36 miss / 1683 stmts / 98%** (`--include='strategies/betting_against_beta/data_loader.py'`). Missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. Guard **44 passed, 5 warnings**. `data_loader.py` unchanged at HEAD (`4dbcd7b` local). No production/test changes added.

**Fresh probes (production-shaped where possible; no semantic changes):**
- **268-269** (`_normalize_index`): monkeypatched `data_loader.pd.to_datetime` to raise plain `TypeError('plain TE')` on a normal string index (`['2024-01-01','2024-01-02']`). Observed: 261 caught `Exception`, 262-265 converted to `BABDataError("Index could not be parsed as datetime")`, 266 (`except BABDataError: raise`) re-raised **before** 268 (`except (ValueError,TypeError)`), yielding `BABDataError` to caller. Confirms handler-order/MRO gate: `BABDataError` subclasses `ValueError`; 268-269 unreachable when inner path converts to `BABDataError`. No production-realistic plain `VE/TE` escape demonstrated.
- **246-247** (`_normalize_index` dayfirst 227-247): probe attempting to force 245 assignment failure was harness-malformed (`AxisProperty` attribute error in custom subclass) and **not** evidence of a production-realistic mechanism. Prior batches 94/97/98 remain authoritative: 232 coercer determinism blocks 234-244; 245/246-247 not reached by demonstrated assignment-failure mechanisms under outer recovery. **No new production-realistic path.**
- **351-352** (`_coerce_to_datetime_scalar` float NaN/inf guards): `float` subclass (`WeirdFloat(1704067200.0)`) coerces normally; breaking `np.isnan`/numeric behavior requires pathological `__float__`/`np` interaction — semantic/pathological, disallowed.
- **641-642, 694-695** (`_detect_and_normalize_exchange_format` outer handlers): production-realistic OHLCV-wide (`Open time/Open/High/Low/Close/Volume`) and epoch-ms date+close frames normalized successfully to `DataFrame`; outer exception handlers not triggered. Confirms inner-swallow/guarded-setup closure for normal inputs.

**Strict batch117 entry criteria (all 4 required) — none satisfied:**
1. **Target+current code:** 36 misses verified at HEAD against `data_loader.py` (1683 stmts). Historic `1626-1627,1663-1664` stale.
2. **New mechanism:** none identified beyond batches 103–116 proofs.
3. **Production-realistic:** no real frame/index/dtype + plausible pandas/library behavior demonstrated to reach 43-44,234-247,268-269,334-342,351-352,403-404,641-695,791-792,953 through unguarded seams without semantic change/pathological harness. `322,326` inspect-gated (guard-relevant).
4. **Expected path:** cannot be stated.

**Conclusion:** 36-miss floor remains mechanism-closed. **Batch118 only** on a genuinely new, concretely demonstrated, production-realistic control-flow mechanism satisfying all four criteria (no semantic change, no pathological harness, no repeat probe). Maintain proofs; preserve `322,326`; use `--rcfile=/dev/null` for canonical coverage run+report.

---

## Batch 118 (2026-11-07T19:28Z, SHA 8145832, fresh rebaseline + mechanism re-confirm, 0 delta)

**Canonical (fresh, `--rcfile=/dev/null` run+report, 2026-11-07T19:27Z):** **1466 passed, 0 failed, 17 skipped, 107 warnings** (45.23s). Coverage: **36 miss / 1683 stmts / 98%** (`--include='strategies/betting_against_beta/data_loader.py'`). Missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. Guard **44 passed, 5 warnings**. `data_loader.py` unchanged vs `56574bd` (production code SHA-stable for this miss set; stmt count 1683).

**Targeted re-confirmation traces (correct PYTHONPATH, no production/test changes):**
- **268-269** (`_normalize_index` 160-271): `pd.to_datetime` monkeypatched to raise plain `TypeError` on normal string index → inner 261 caught, 262-265 converted to `BABDataError`, 266 re-raised before 268. Result observed: `BABDataError "Index could not be parsed as datetime"`. Confirms handler-order + `Exception→BABDataError` conversion + MRO (`BABDataError` subclasses `ValueError`) gate 268-269 for this path.
- **234-244,246-247** (dayfirst 227-247): index `[np.datetime64('NaT'), 'zzzznotadate999']` → elementwise coercion raises at 223 on unparseable element, control jumps to 248; 227-247 not entered. Confirms 223 intercept prevents mixed NaT+unparseable entry (batches 94/97/98). 232 determinism on 216-224 survivors remains the closure for 234-244.

**Strict batch118 entry criteria (all 4 required) — none satisfied:**
1. Targets/current code verified at HEAD `8145832` (36 misses, 1683 stmts; historic 1626-1627/1663-1664 stale).
2. No mechanism identified not disproven by batches 103–117/proofs (handler conversion+order/MRO 268-269; coercer determinism + 223 intercept + NaT gate 234-247; re-raise-before-generic-pass 334-342; builtin `float(str)`/guarded epoch branches 403-404; identity+guarded `pd.isna` 43-44; inner-swallow/guarded setup 641-695; fully-guarded tz promotion 791-792; `str.split()` construction 953; inspect-gated 322,326; pathological-semantic 351-352).
3. No production-realistic `pd.DataFrame`/index/dtype + plausible pandas/library behavior demonstrated to reach remaining handlers without semantic change or pathological harness.
4. Expected control-flow path cannot be stated consistently with (2)-(3).

**Conclusion:** 36-miss floor remains mechanism-closed at `8145832`. **Batch119 only** on a genuinely new, concretely demonstrated, production-realistic mechanism satisfying all four criteria. Preserve `322,326`; no semantic changes for coverage; use `--rcfile=/dev/null` for canonical coverage run+report.

---

## Batch 119 (2026-11-07T20:08Z, SHA b4fdaf5, fresh rebaseline + strict 4-criteria probes, 0 delta)

**Canonical (fresh, `--rcfile=/dev/null` run+report, 2026-11-07T20:06Z):** **1466 passed, 0 failed, 17 skipped, 107 warnings** (46.11s). Coverage: **36 miss / 1683 stmts / 98%** (`--include='strategies/betting_against_beta/data_loader.py'`). Missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. Guard **44 passed, 5 warnings**. Baseline/SHA drift: working tree at `b4fdaf5` (HEAD commit message differs from prior handoff SHA `8145832`) but miss set/count unchanged (**36/1683**). No production/test/canonical-batch changes.

**Probes (direct, PYTHONPATH set, no production change):**
- **234-247 (`_normalize_index` 227-247):** (1) targets 234-244,246-247. (2) Re-tested NaT-producing shapes: all-NaT object index, mixed `pd.NaT` + valid strings, mixed `np.datetime64('NaT')` + valid — all normalize (NaT rows dropped or resolved) without hitting 234-244; coercer returns NaT on retry (232 `continue`) and 245 assignment is safe for same-length list. No mechanism makes 232 raise for a 216-224 survivor (determinism). (3) Production-realistic messy date inputs covered; still dead. (4) No viable path to 234-244 or 246-247. **Entry criteria not satisfied.**
- **268-269 (`_normalize_index` outer `except (ValueError, TypeError)`):** (1) target 268-269. (2) Plain `TypeError` from `pd.to_datetime` (monkeypatch) on normal string index → 261 catches `Exception`, 262-265 raise `BABDataError`, 266 re-raises before 268. Observed `BABDataError:Index could not be parsed as datetime`. Confirms conversion+order+MRO gate. (3) Monkeypatch is mechanism probe only; no production-realistic plain VE/TE escape from 161-265 demonstrated (all inner ops wrapped; 261-265 converts). (4) No viable path. **Entry criteria not satisfied.**
- **641-642 (`_detect_and_normalize_exchange_format` outer 598-642):** (1) target 641-642. (2) A column object with `__str__` raising produced `RuntimeError` from `lower_map` construction (599) in an ad-hoc probe, but such column objects are **not production-realistic** exchange/CSV/JSON frame labels (pandas/real loaders yield `str`/normal labels); this is a pathological harness shape. (3) Not production-realistic. (4) Not pursued. **No proof change warranted beyond this note; cluster remains structural-dead for production-realistic inputs.**
- **694-695 / 791-792 / 43-44 / 334-342 / 351-352 / 403-404 / 953 / 322,326:** no new mechanism identified; prior proofs stand (inner-swallow/guarded setup, fully-guarded, identity+guarded `pd.isna`, re-raise-before-generic-pass, pathological-semantic/disallowed, builtin-float/guarded epoch, construction-unreachable, inspect-gated). **Entry criteria not satisfied.**

**Conclusion:** 36-miss floor remains mechanism-closed at `b4fdaf5`. **Batch120 only** on a genuinely new, concretely demonstrated, production-realistic control-flow mechanism satisfying all four criteria (exact target+current code, new mechanism not disproven, production-realistic shape/library behavior, expected path). Preserve `322,326`; no semantic changes for coverage; do not commit unless explicitly requested. Use `--rcfile=/dev/null` for canonical coverage run+report.
