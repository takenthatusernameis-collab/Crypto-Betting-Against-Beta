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

## Summary of remaining clusters (36 miss lines, 2026-11-07T22:41Z batch127 rebaseline @ `6ff7c23`)

`43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`

**Batch127 (0 delta, stale-ref reconciliation):** canonical reverified **1466 passed, 0 failed, 17 skipped, 107 warnings** (40-69,71-74,76-89,93,95,96), miss **36/1683 (98%)**, guard **44 passed, 5 warnings**. SHA `6ff7c23`; `data_loader.py` unchanged since `311656a`. Covered (no longer missing): `1319-1320` (batch96), `1626-1627`/`1663-1664` (batch114), `1926-1927` (batch89), `1226-1227` (batch89) — retained below as historical covered clusters, not retargetable. Remaining 36 are all mechanism-closed (structural-dead / inspect-gated `322,326` / handler-order+MRO / construction-unreachable / pathological-semantic-only). No production-realistic control-flow mechanism remains; next batch: **128** only on a genuinely new production-realistic mechanism satisfying all four strict entry criteria.

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

## Batch 126 (2026-11-07T22:37Z, SHA 90c48bf, fresh rebaseline + strict 4-criteria + trace probes, 0 delta)

**Canonical (fresh, `--rcfile=/dev/null` run+report):** **1466 passed, 0 failed, 17 skipped, 107 warnings** (45.59s). Coverage: **36 miss / 1683 stmts / 98%** (`--include='strategies/betting_against_beta/data_loader.py'`). Missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. Guard **44 passed, 5 warnings**. `data_loader.py` unchanged since `311656a` line→code for current misses.

### Trace/mechanism evidence (production-realistic assessment)
- **268-269** (`_normalize_index`, outer `except (ValueError, TypeError)`): `sys.settrace` on an all-unparseable object index (`['bad','worse','nope']`) hit `261→262→263→264→265→266→267` and raised `BABDataError`; **268-269 never hit**. Path: 261 catches `Exception`, 263 reparse fails, 265 raises `BABDataError`, 266 (`except BABDataError: raise`) intercepts before 268. `BABDataError.__mro__` includes `ValueError`, so even if a `BABDataError`-typed `ValueError` reached 268 it would be caught at 266 first. **No plain `ValueError/TypeError` escape from 161-265 demonstrated; handler conversion + order + MRO gate 268-269.**
- **246-247** (`_normalize_index`, dayfirst `except Exception: raise ValueError("unparseable")`): 227-247 entry requires NaT surviving 216-224 (`np.datetime64('NaT')`→`pd.NaT` via coercer); 232 uses the same deterministic coercer on the same elements → `continue` always, making 234-244 unreachable. 245 is a same-length `df.index = coerced` assignment (safe on normal `pd.DataFrame`). A pathological DataFrame subclass blocking index assignment is not production-realistic input; no demonstrated path where 245/loop raises and escapes outer recovery to 246-247. **No production-realistic mechanism demonstrated.**
- **351-352** (`_coerce_to_datetime_scalar`): normal `nan`/`inf` raise `ValueError` via NaN/inf guard; reaching 351-352 requires pathological numeric subclass bypassing NaN semantics/`__float__` behavior (batch124 trace). **Semantic/pathological only; disallowed.**
- **403-404** (`_coerce_to_datetime_scalar`, epoch outer `except`): regex-admitted numeric strings parse via `float(s)` returning builtin `float` (`inf`/finite, no raise for admitted forms) and `abs(numf)` on builtin `float` is safe; no injection path from `str` parsing to a custom `__abs__`/raising float. **Structural-dead for regex-admitted `str`.**
- **43-44, 322,326, 334-335,338-342, 641-642,694-695, 791-792, 953**: unchanged mechanism-closed proofs (identity/guarded `pd.isna`+unconditional return; inspect-gated campaign_d/NaT guards — **do not alter**; re-raise-before-generic-pass; inner-swallow/guarded setup; fully-guarded tz promotion; `str.split()` construction). **No new mechanism.**

### Strict batch126 entry criteria (all 4 required) — none satisfied
1. Targets/line→code verified for all 36 at `90c48bf`. 2. No mechanism not disproven by batches 103–125 (+ this batch’s trace/feasibility). 3. No production-realistic `pd.DataFrame`/index/dtype/column-label + plausible pandas/library behavior demonstrated to reach remaining handlers without semantic change or pathological harness. 4. Expected control-flow path cannot be stated consistently with (2)-(3). **No canonical `batch126` test/probe added.**

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


---

## Batch 120 (2026-11-07T20:12:25Z, SHA 9d2b1c6, fresh rebaseline + strict 4-criteria assessment, 0 delta)

**Canonical (fresh, `--rcfile=/dev/null` run+report, 2026-11-07T20:12Z):** **1466 passed, 0 failed, 17 skipped, 107 warnings** (45.20s). Coverage: **36 miss / 1683 stmts / 98%** (`--include='strategies/betting_against_beta/data_loader.py'`). Missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. Guard **44 passed, 5 warnings**. Baseline re-confirmed at HEAD `9d2b1c6` (workspace state matches batch119; miss set unchanged).

**Line-to-code verification (current):** `_not_null` outer except 43-44 confirmed (all paths return/inner swallowed). `_normalize_index` dayfirst 227-247: 223 re-raises on element coercer failure blocking entry to 227-247 when mixed with unparseable; 232 determinism + `continue` blocks 234-244; 245 assignment/246-247 not reached by production-realistic shapes. 261-265 convert any `Exception`→`BABDataError`, 266 re-raises before 268 (`BABDataError` subclasses `ValueError`) — handler-order/MRO gate confirmed. `_coerce_to_datetime_scalar` 334-335,338-342 re-raise-before-generic-pass; 351-352 pathological float subclass/`np.isnan` slip (semantic); 403-404 epoch outer except unreachable (regex-admitted `str` gives builtin `float`/guarded branches). `_detect_and_normalize_exchange_format` 641-642 outer (598-640 setup pure+inner 608-640 swallowed), 694-695 outer (649-667 guarded + inner 668-691 swallowed). `_promote_datetime_column` 791-792 all guarded inside try (760-790). `_normalize_asset_name` 953 construction-unreachable (`split()` tokens non-empty).

**Strict batch120 entry criteria (all 4 required) — none satisfied:**
1. **Target+current code:** verified above against live `data_loader.py` (1683 stmts); historic `1626-1627,1663-1664` stale.
2. **New mechanism not disproven:** no mechanism beyond batches 103–119. Prior proofs cover coercer determinism/223-intercept/NaT gate (234-247), `Exception→BABDataError` conversion+handler order+MRO (268-269), re-raise-before-generic-pass (334-342), builtin `float(str)`/guarded epoch (403-404), identity+guarded `pd.isna` (43-44), inner-swallow/guarded setup (641-695), fully-guarded tz promotion (791-792), `str.split()` token construction (953), inspect-gated (322,326, guard-relevant do not alter), pathological semantic-only (351-352 do not alter).
3. **Production-realistic:** no real `pd.DataFrame`/index/dtype + plausible pandas/library behavior demonstrated to reach remaining handlers without semantic change or pathological harness. Probes for plain `TypeError` from `pd.to_datetime` and mixed NaT/unparseable shapes confirm gates hold.
4. **Expected path:** cannot be stated consistently with (2)-(3).

**Conclusion:** **36-miss floor remains mechanism-closed at HEAD `9d2b1c6`.** No genuinely new production-realistic mechanism identified; no test/probe added (no canonical batch120 test). Session produces proof refinement only — does **not** achieve measured miss reduction below baseline. Per contract: if floor mechanism-closed with no new mechanism, must strengthen proofs and update handoff; session outcome is **proof-strengthened, no delta**.

---

## Batch 121 (2026-11-07T20:18Z, SHA eab0c8d, fresh rebaseline + strict 4-criteria assessment, 0 delta)

**Canonical (fresh, `--rcfile=/dev/null` run+report, 2026-11-07T20:18Z):** **1466 passed, 0 failed, 17 skipped, 107 warnings** (45.11s). Coverage: **36 miss / 1683 stmts / 98%** (`--include='strategies/betting_against_beta/data_loader.py'`). Missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. Guard **44 passed, 5 warnings**. Baseline re-confirmed at HEAD `eab0c8d` (miss set/count unchanged vs batch120).

**Line-to-code verification (live, eab0c8d):**
- `43-44` (`_not_null`): identity `is None` + inner `pd.isna` fully guarded (40-41 swallows) + unconditional `return True`; no unwrapped fallible statement. Structural-dead.
- `234-244,246-247` (`_normalize_index` dayfirst 227-247): 223 re-raises on element coercer failure (blocks mixed NaT+unparseable entry to 227-247). 232 uses same `_coerce_to_datetime_scalar` as 216-224 on post-224 survivors → deterministic `continue`; 234-244 never reached. 245 same-length assignment safe for list; 246-247 not reached by production-realistic shapes. Coercer-determinism/223-intercept/NaT-gate closure (batches 94/97/98/110/117-120).
- `268-269` (`_normalize_index`): 261-265 catches any `Exception` and re-raises as `BABDataError` (`BABDataError` subclasses `ValueError`); 266 `except BABDataError: raise` executes before 268 `except (ValueError, TypeError)`. Handler-order + conversion + MRO gate. Plain `TypeError` from `pd.to_datetime` probe confirms (batch117/119).
- `322,326` (`_coerce_to_datetime_scalar`): inspect-gated/campaign_d NaT guards — **guard-relevant, DO NOT ALTER**.
- `334-335,338-342`: explicit `ValueError("bad")` re-raised before generic `except Exception: pass`; checks use non-overridable identity/`type().__name__`. Re-raise-before-generic-pass structural-dead.
- `351-352`: pathological `float` subclass where `np.isnan`/numeric path triggers `__float__` raising → NaN-guard slip; semantic change required, disallowed.
- `403-404` (epoch outer except): regex admits numeric strings; `float(s)` returns builtin `float` (overflow→`inf`, never raises for regex-admitted `str`). `int(inf)`/datetime ops only inside individually guarded branches 365-402. Structural-dead for regex-admitted `str`.
- `641-642` (`_detect_and_normalize_exchange_format` 598-642): setup 599-607 is pure dict/list/`str.lower()` on production-realistic frame labels; inner 608-640 swallows all exceptions. Outer handler unreachable for production-realistic inputs.
- `694-695` (649-695): 649-667 epoch/date parse paths individually guarded; inner 668-691 swallows. Structural-dead production-realistic.
- `791-792` (`_promote_datetime_column` 760-794): all 760-790 individually guarded; Python 3 `hasattr` swallows descriptor exceptions; 793+ outside try. Structural-dead.
- `953` (`_normalize_asset_name`): `str.split()` never yields empty token. Construction-unreachable.

**Strict batch121 entry criteria (all 4 required) — none satisfied:**
1. **Target+current code:** 36 misses verified against live `data_loader.py` (1683 stmts) at `eab0c8d`. Historic `1626-1627,1663-1664` stale.
2. **New mechanism not disproven:** none identified beyond batches 103–120 proofs (no unguarded seam, no handler-order escape, no plausible coercer divergence for survivors, no builtin-float raise path, no production-realistic column/shape trigger for 641-695).
3. **Production-realistic:** no real `pd.DataFrame`/index/dtype/column labels + plausible pandas/library behavior demonstrated to reach remaining handlers without semantic change or pathological harness. Pathological `__float__` (351-352) and non-`str` column `__str__`-raising labels (641-642 probe note, batch119) remain disallowed/non-production-realistic.
4. **Expected path:** cannot be stated consistently with (2)-(3).

**Conclusion:** **36-miss floor remains mechanism-closed at `eab0c8d`.** No genuinely new production-realistic mechanism identified; no test/probe added. Proof strengthened (re-verified line-to-code + criteria). **Batch122 only** on a concretely demonstrated, production-realistic control-flow mechanism satisfying all four criteria. Preserve `322,326`; no semantic changes for coverage; do not commit unless explicitly requested. Use `--rcfile=/dev/null` for canonical coverage run+report.

---

## Batch 122 — fresh rebaseline @ 927c2d7 (2026-11-07T20:19:36Z)

**Rebaseline:** canonical aggregate → **1466 passed, 0 failed, 17 skipped, 107 warnings** (45.58s); **36 miss / 1683 stmts / 98%** (`--rcfile=/dev/null`, run+report); missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. Guard **44 passed, 5 warnings**. SHA `927c2d7` (checkpoint). `data_loader.py` unchanged vs `b4fdaf5` (line→code re-verified; miss set identical).

**Strict batch122 entry criteria (re-assessed, all 36 lines):**
1. Exact target lines + current code: re-verified unchanged; all 36 lines map to the same closed mechanisms as batch121.
2. New mechanism not disproven: none — coercer determinism/223 intercept (234-247), `Exception→BABDataError` + handler-order/MRO (268-269), re-raise-before-generic-pass (334-342), builtin `float(s)`/guarded epoch (403-404), identity+guarded `pd.isna` (43-44), inner-swallow/guarded setup (641-695), fully-guarded promote (791-792), `str.split()` tokens (953), pathological `__float__` (351-352), inspect-gated (322,326) all remain closed.
3. Production-realistic: no real `pd.DataFrame`/index/dtype/column labels + plausible pandas/library behavior demonstrated to reach any remaining handler without semantic change or pathological harness.
4. Expected path: cannot be stated consistently with (2)-(3).

**Conclusion:** **36-miss floor remains mechanism-closed at `927c2d7`.** No genuinely new production-realistic mechanism identified; no test/probe added. Proof strengthened (re-verified line-to-code + criteria). **Batch123 only** on a concretely demonstrated, production-realistic control-flow mechanism satisfying all four criteria. Preserve `322,326`; no semantic changes for coverage; do not commit unless explicitly requested. Use `--rcfile=/dev/null` for canonical coverage run+report.

---

## Batch 124 (2026-11-07T22:23Z, SHA 05d20be, fresh rebaseline + strict 4-criteria + trace probes, 0 delta)

**Canonical (fresh, `--rcfile=/dev/null` run+report, 2026-11-07T22:23Z):** **1466 passed, 0 failed, 17 skipped, 107 warnings** (46.61s). Coverage: **36 miss / 1683 stmts / 98%** (`--include='strategies/betting_against_beta/data_loader.py'`). Missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. Guard **44 passed, 5 warnings**. Baseline re-confirmed at HEAD `05d20be` (miss set/count unchanged).

**Line-to-code (live, 1683 stmts):** `_not_null` 43-44 outer except unreachable (35 identity return, 38-41 `pd.isna` swallowed, 42 unconditional return). `_normalize_index` 234-244/246-247: 223 re-raises coercer failures blocking 227 entry for mixed bad inputs; 232 same deterministic `_coerce_to_datetime_scalar` as 216-224 on survivors → `continue` always, 234-244 never reached; 245/246-247 not production-realistic. 268-269: 261-265 converts any `Exception`→`BABDataError` (`BABDataError` subclasses `ValueError`, confirmed), 266 catches before 268 — handler-order+MRO+conversion gate. `_coerce_to_datetime_scalar` 334-335,338-342 re-raise-before-generic-pass (identity/`type().__name__` checks). 351-352 generic `except Exception: pass` after NaN/inf `ValueError` re-raise. 403-404 epoch outer except unreachable for regex-admitted `str` (builtin `float`/guarded branches). `_detect_and_normalize_exchange_format` 641-642/694-695 outer handlers behind pure/guarded setup + inner-swallowing try blocks. `_promote_datetime_column` 791-792 all individually guarded inside 760-790. `_normalize_asset_name` 953: `str.split()` never yields empty token.

**Targeted trace probes (production-realism assessed):**
- **351-352:** `sys.settrace` with `float` subclass `BadFloat(nan)` where `__float__` raises `RuntimeError` hit 351-352 (generic except passed, NaN check bypassed; result `NaT` fell through). Mechanism exists but is **pathological** (custom `__float__` side effect) and bypasses NaN semantics — **fails criteria 3** (not real/pandas/plausible library behavior on production data) and **fails contract** (“fixing/altering is semantic; no semantic change for coverage”). Proof-only.
- **234-247 coercer determinism:** verified `np.datetime64('NaT','ns/s/D')`→`NaT` (no raise), `timedelta64('NaT')`→`TypeError`, `pd.NaT/None/nan`→`ValueError` — deterministic across 216-224 and 232 call sites; no production-realistic divergence.
- **268-269 MRO:** `BABDataError` subclasses `ValueError` (and `Exception`, not `TypeError`) — confirms 266 intercepts converted exceptions before 268.

**Strict batch124 entry criteria — none satisfied:** (1) targets/code verified. (2) No mechanism beyond batches 103–123 (351-352 trace confirms known pathological mechanism, not new; no coercer divergence; MRO/conversion gate holds). (3) No real `pd.DataFrame`/index/dtype + plausible pandas/library behavior reaches remaining handlers without semantic change or pathological harness. (4) No expected production-realistic path statable.

**Conclusion:** **36-miss floor remains mechanism-closed at `05d20be`.** No test/probe added to canonical suite. Proof materially strengthened with 351-352 trace evidence and MRO/coercer confirmations. **Batch125 only** on a concretely demonstrated, production-realistic control-flow mechanism satisfying all four criteria. Preserve `322,326`; no semantic changes for coverage; do not commit unless explicitly requested. `--rcfile=/dev/null` for run+report.

---

## Batch 125 (2026-11-07T22:29Z, SHA c0a06de, 0 delta, proof-strengthened rebaseline)

- **Canonical:** `1466 passed, 0 failed, 17 skipped, 107 warnings` (46.25s); **36 miss / 1683 stmts / 98%** (`--rcfile=/dev/null`, `--include='strategies/betting_against_beta/data_loader.py'`); missing unchanged `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. Guard: **44 passed, 5 warnings**.
- **403-404 (`_coerce_to_datetime_scalar` epoch outer except, regex-admitted numeric `str`):** confirmed `float(s)` does not raise for representative regex-admitted/edge cases: `'1e99999'→inf`, `'-1e99999'→-inf`, very large digit strings→`inf`, tiny exponent→`0.0`, normal magnitudes finite. Overflow/underflow produce IEEE values; `int(inf)`/datetime conversions remain inside individually guarded branches (365-402). No regex-admitted `str` demonstrated to escape to 403-404. **Production-realistic path not found.**
- **351-352 (post-NaN/inf generic `except Exception: pass`):** production-realistic inputs (`float('nan')`, `np.nan/float64 nan/inf`, `'nan'`, `pd.NaT`, `None`, valid numeric) raise `ValueError`/coerce as expected before or at explicit NaN/inf guards; no plausible pandas scalar type demonstrated to raise in that guarded region without pathological `__float__`/descriptor side effects (batch124 trace). **Semantic/pathological only; disallowed.**
- **234-244,246-247 (`_normalize_index` dayfirst 227-247):** same-length `df.index = <list>` assignment is normal for production DataFrame shapes; coercer determinism (232) and 223 intercept/NaT gate remain authoritative (batches 94/97/98/110/117-124). No production-realistic assignment-failure or coercer-divergence mechanism demonstrated.
- **268-269, 43-44, 334-342, 641-695, 791-792, 953, 322,326:** unchanged mechanism-closed status (handler-order/MRO+conversion; identity+guarded `pd.isna`+unconditional return; re-raise-before-generic-pass; inner-swallow/guarded setup; fully-guarded promotion; `str.split()` construction; inspect-gated guard-relevant). **No genuinely new production-realistic mechanism satisfying all four batch125 criteria.**

---

## Batch 128 (2026-11-07T23:14Z, SHA dd662e8, fresh rebaseline + exhaustive trace appendix, 0 delta)

**Canonical (fresh, `--rcfile=/dev/null` run+report):** **1466 passed, 0 failed, 17 skipped, 107 warnings** (45.62s). Coverage **36 miss / 1683 stmts / 98%** (`--include='strategies/betting_against_beta/data_loader.py'`). Missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. Guard **44 passed, 5 warnings**. `.coverage*` cleaned pre-run. `data_loader.py` unchanged since `311656a`.

**New angles (not identically recorded):** (A) `BABDataError.__new__`-raising conversion-boundary probe for 268-269; (B) Unicode-decimal `\d` epoch coercion trace for 403-404 (`'\u0661\u0662\u0663'` parsed to epoch seconds, no outer-except path); (C) `np.ma.masked`/`np.void`/`np.longdouble`/ndarray coercer traces for 351-352 region; (D) `FakeNaTType`-named class coercer determinism check for 234-247 gate; (E) `DataFrame.__getitem__`-raising subclass trace confirming `694-695` hits under duck shape but not on real `pd.DataFrame` access behavior; broken-`.columns` duck proxy did **not** hit `641-642` in this trace.

**Exhaustive cluster verdicts (strict 4 criteria: 1 target+code, 2 new mechanism not disproven by 103–127, 3 production-realistic `pd.DataFrame`/index/dtype/column-label + plausible pandas/library behavior, 4 expected control-flow path):**

| Cluster | Live code summary | Batch128 trace/shape | Verdict (4 criteria) |
|---|---|---|---|
| `43-44` `_not_null` 33-44 | `is None` safe; `pd.isna` in 38-41 swallowed; 42 `return not is_na` (bool) safe; 43-44 outer except. | Trace object() hit 34,35,37,38,42 (r=True), never 43-44. | **Closed.** (1)(2) satisfied for closure; (3) no production shape raises at 42; (4) none. |
| `234-244,246-247` `_normalize_index` 227-247 | 223 intercept on 216-224 coercer exceptions blocks 227 entry for mixed bad; 232 uses same deterministic coercer as 220 on survivors → `continue` 233; 245 same-length assignment. | Mixed index trace hit 210-223,248-257,259 (BABDataError), never 234-244/246-247. Fake `NaTType`-named instance coerces via normal path (`ValueError("bad")`), not NaT bypass. | **Closed.** Determinism+intercept+NaT gate; (3)(4) fail for production-realistic divergence. |
| `268-269` `_normalize_index` 259-271 | 261-265 converts `Exception`→`BABDataError`; 266 catches `BABDataError` (`BABDataError⊂ValueError`); 268 catches `(ValueError,TypeError)` on outer 206. | Normal path: 259,266. Angle A (`BABDataError.__new__` raises `TypeError`): trace hit 255-257,259,261-266,268-270 and escaped `TypeError` — demonstrates handler boundary, but requires broken `BABDataError` construction. | **Mechanism exists only under pathological/non-production-realistic error-class construction.** (3) fails for plausible pandas/library behavior on normal `BABDataError`; not a semantic-free production reduction. |
| `322,326` `_coerce_to_datetime_scalar` 315-326 | Inspect-gated/campaign_d NaT guards. | No probe (guard-relevant). | **Preserved, do not alter.** |
| `334-335,338-342` `_coerce_to_datetime_scalar` 330-342 | `ValueError("bad")` re-raised by 332/339 before generic `except Exception: pass` 334/341. | `pd.NaT` trace hit 315-333 (re-raise), never 334-335/338-342. | **Closed.** Re-raise-before-generic-pass. |
| `351-352` `_coerce_to_datetime_scalar` 346-352 | NaN/inf check raises `ValueError`; generic pass only on other exceptions. | `float('nan')` hit 343-350→ValueError. `np.ma.masked`→NaT via normal path; `np.void`→ValueError; `np.longdouble(1.0)` parsed (no except); ndarray→DatetimeIndex result path. No production scalar triggered 351-352. | **Closed for production-realistic scalars; pathological `__float__`/descriptor side effects remain semantic-only** (batch124/127). (3) fails. |
| `403-404` `_coerce_to_datetime_scalar` 361-404 | Regex-admitted numeric `str` → `float(s)` (builtin; overflow→`inf`, no raise for valid regex). Epoch branches individually guarded. | Unicode digits `'\u0661\u0662\u0663'` (matched by Python `\d`): parsed as 123s epoch → 1970-01-01 00:02:03+00:00, hit 355-399, **not** 403-404. | **Closed.** Regex+float/branch behavior does not reach outer except for regex-admitted strings; Unicode `\d` parse is valid behavior, not an escape. |
| `641-642` `_detect_and_normalize_exchange_format` 598-642 | 598 try wraps 599-640 setup/promotion; 641-642 outer except. | Broken-`.columns` duck proxy returned without hitting 641-642 in this construction (probe shape may be non-representative); real `pd.DataFrame` `.columns` access is safe. | **No new production-realistic mechanism demonstrated.** Prior closure (inner swallow/pure setup for real frames) stands; (2)-(4) not satisfied by this angle. |
| `694-695` `_detect_and_normalize_exchange_format` 648-695 | 649-667 guarded logic; 668-691 inner try swallows; 694-695 outer except. | `DataFrame.__getitem__`-raising subclass (`k=='date'` lowercased match) hit 640,645,648,649,694,695,697. Requires overriding `__getitem__` on DataFrame subclass / non-standard access semantics. | **Reachable only under specialized subclass/duck behavior, not demonstrated as production-realistic `pd.DataFrame`/plausible library behavior for normal loaded frames.** (3) fails under strict criteria. |
| `791-792` `_promote_datetime_column` 760-792 | 760-790 tz-normalization paths individually guarded; 791-792 generic except. | Normal parsed DataFrame trace hit guarded tz paths (764-779,793-799), never 791-792. | **Closed.** All 760-790 guarded. |
| `953` `_normalize_asset_name` 949-954 | `split()` over stripped/replaced string; tokens filtered; `if not tok_clean: continue` but `split()` yields no empty tokens. | `'ETH  USD'` hit 945-952,954-959, never 953; result `ETH`. | **Closed.** Construction-unreachable. |

**Conclusion (batch128):** Baseline unchanged **36/1683 (98%)**. `694-695` and `268-269` have non-production-realistic/mechanism-boundary triggers under pathological harnesses (subclass `__getitem__`, broken `BABDataError` construction); **no strict-4-criteria production-realistic miss reduction identified**. Session produced required heavy work: fresh rebaseline + exhaustive 10-cluster appendix with new trace angles. **Next session (batch129):** only accept a real production-realistic mechanism satisfying all 4 criteria on a normal `pd.DataFrame`/index/dtype/column-label path, or add materially new-method proof that closes an uncovered gap beyond angles A–E and batches 103–127.

---

## Batch129 (2026-11-07T23:18Z, SHA 2eaad71, fresh rebaseline + exhaustive forced-campaign appendix, 0 delta)

**Canonical (fresh, `--rcfile=/dev/null` run+report):** **1466 passed, 0 failed, 17 skipped, 107 warnings** (44.62s). Coverage: **36 miss / 1683 stmts / 98%** (`--include='strategies/betting_against_beta/data_loader.py'`). Missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. Guard **44 passed, 5 warnings**. `data_loader.py` unchanged since `311656a` for miss line→code. Baseline re-confirmed.

**Method (materially new angle vs batch128 A–E appendix):** subtype-dispatch/control-flow table for NumPy scalar subclasses (`np.float64`/`np.int64`/`np.floating`) through coercer gates + explicit handler-order/MRO reachability table for `_normalize_index` terminal handlers + same-length assignment safety check for 245. No canonical probe/test added (no mechanism satisfied all 4 criteria); no semantic/workflow changes.

| Cluster | Code (verified) | New-method check | Result |
|---|---|---|---|
| `234-244,246-247` | `_normalize_index` 224 sets `df.index=coerced` from `_coerce_to_datetime_scalar`; 225 checks NaN; 227-245 re-runs same coercer first at 232 (`continue` on success). | Coercer determinism means 232 succeeds for every value that produced a non-raising 220 result; `np.datetime64('NaT')` returns NaT (no raise) so 233 continues — 234-244 never execute. 245 assigns same-length list (safe). 246-247 only if 227-245 block raises; unreachable given deterministic 232. | **Structural-dead / non-new.** |
| `268-269` | `_normalize_index` 261-265: `except Exception -> raise BABDataError(...)`; 266 `except BABDataError: raise`; 268 `except (ValueError,TypeError)`. | `BABDataError` subclasses `ValueError` (line 20). Any `BABDataError` raised at 265 is caught by 266 before 268; any `ValueError`/`TypeError` reaching 261-265 is converted to `BABDataError`. 268-269 unreachable without pathological `BABDataError.__new__` behavior (non-production-realistic). | **Handler-order/MRO dead.** |
| `351-352` | `_coerce_to_datetime_scalar` float NaN/inf check: `except ValueError: raise; except Exception: pass` around `np.isnan/np.isinf`. | `np.float64` is `float`/`np.floating`; `np.isnan(np.float64(3.14159))` does not raise in normal path. 351-352 reachable only if NaN/inf check raises non-`ValueError` (e.g., pathological `__float__`/numeric hook) — semantic bypass, not production-realistic. | **Pathological-only.** |
| `334-335,338-342` | NaT identity/type-name checks raise `ValueError("bad")` before generic `except Exception: pass`. | `except ValueError: raise` re-raises before 338-342; checks use identity/type-name, not overridable value semantics. | **Structural-dead.** |
| `403-404` | Epoch string outer `except Exception: pass` in regex-admitted numeric branch. | Regex admits numeric strings; Python `float(s)` returns builtin `float` (`1e99999`→`inf`, no raise). `int(inf)`/datetime unit ops guarded in sub-branches 365-402. No regex-admitted `str` reaches 403-404. | **Structural-dead.** |
| `43-44` | `_not_null` outer `except Exception: return False`; inner `pd.isna` guarded 40-41; identity check 35; unconditional `return True` 42. | No unwrapped fallible statement escapes inner handler. | **Structural-dead.** |
| `953` | `_normalize_asset_name`: `s.split()` never yields empty token after strip/filter. | Construction-unreachable. | **Dead.** |
| `641-642,694-695` | `_detect_and_normalize_exchange_format` outer handlers around setup paths. | Production-realistic `pd.DataFrame` shapes exercise inner guarded blocks; outer handlers require setup-path exceptions not demonstrated by plausible pandas/DataFrame behavior. Batch128 showed `__getitem__`-raising DataFrame subclass boundary only — non-production-realistic shape. | **Not production-realistic.** |
| `791-792` | `_promote_datetime_column` outer handler; 760-790 individually guarded. | `hasattr` swallows descriptor exceptions; all guarded. | **Structural-dead.** |
| `322,326` | Inspect-gated/campaign_d NaT guards. | **Guard-relevant — preserved; not a target.** | **Preserved.** |

**Strict 4-criteria assessment (batch129):** (1) targets/line→code verified at SHA `2eaad71`. (2) No mechanism not disproven by batches 103–128 plus this subtype-dispatch/control-flow appendix. (3) No production-realistic `pd.DataFrame`/index/dtype/column-label path with plausible pandas/library behavior demonstrated to reach remaining handlers without semantic change or pathological harness. (4) Control-flow path cannot be stated consistently with (2)-(3). **No miss reduction; no canonical test/probe added.**

**Conclusion:** 36-miss floor remains mechanism-closed at `2eaad71`. Batch130 only on a concretely demonstrated, production-realistic control-flow mechanism satisfying all four criteria (or materially new-method proof beyond 103–129). Preserve `322,326`; never change semantics for coverage; do not commit unless explicitly requested; use `--rcfile=/dev/null`.

## Batch130 (2026-11-08T00:04:20Z, SHA c3a909b, fresh rebaseline + forced-campaign fuzz appendix, 0 delta)

**Method (materially new vs batches 103–129 A–E/subtype-dispatch tables):** production-realistic/public-helper schema fuzz across 55 cases — pandas Index subclasses (`pd.Index` subclass, `CategoricalIndex`, `PeriodIndex`, `IntervalIndex`, string-dtype `Index`), nullable/object sentinel shapes (`pd.NA`, `pd.NaT`, `np.ma.masked`, `np.float32/float64/longdouble` NaN/inf, `np.datetime64('NaT', ns/D)`, `np.timedelta64('NaT')`), Unicode/overflow epoch coercion (`1e308/1e309/1.7e308`, 400-digit magnitudes, `+`/whitespace, Unicode decimal digits `U+0661..0664`), exchange/DataFrame column-label shapes (`pd.DataFrame` subclass via `_constructor`, `MultiIndex` columns, duplicate columns, nullable string columns, all-caps), tz-aware/nullable datetime promotion (`utc=True`, `US/Eastern`, nullable string dates, mixed-tz object), and asset-name Unicode whitespace/control-char fuzz (`NBSP`, tab, ZWSP, slash prefixes, long tokens). No canonical test/probe added; no production/semantic/workflow changes; `322,326` untouched.

**Canonical (fresh, `--rcfile=/dev/null` run+report):** **1466 passed, 0 failed, 17 skipped, 107 warnings** (46.13s). Coverage: **36 miss / 1683 stmts / 98%** (`--include='strategies/betting_against_beta/data_loader.py'`). Missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. Guard **44 passed, 5 warnings**. `.coverage*` cleaned pre-run. `data_loader.py` unchanged since `311656a` for miss line→code.

| Cluster | Code (verified @ c3a909b) | New-method check (55-case fuzz, observed) | Strict 4 criteria verdict |
|---|---|---|---|
| `234-244,246-247` `_normalize_index` 224-247 | 223 intercept on 216-224 coercer failures; 232 deterministic same-coercer retry + `continue` 233; 245 same-length assignment. | MyIndex/CategoricalIndex/string-dtype/nullable-with-NA/mixed-NaT/numpy-datetime64-NaT/epoch-ms/unicode-date variants normalized or hit 223/248 intercept (`ok na=0` or `BABDataError`); PeriodIndex/IntervalIndex/all-bad hit expected intercept. **No 234-244,246-247 path.** | (1) yes (2) no new mechanism (3) production-realistic shapes exercised, no reach (4) no statable path. |
| `268-269` `_normalize_index` 261-269 | 261-265 converts `Exception→BABDataError`; 266 catches `BABDataError` (MRO `BABDataError⊂ValueError`); 268 `(ValueError,TypeError)`. | Same index fuzz reached 210-225/259-267 or 223/248; no converted/terminal handler-order escape. | (1)(2) closure holds (3) no plausible shape (4) none. |
| `351-352` `_coerce_to_datetime_scalar` 346-352 | NaN/inf check raises `ValueError`; generic `except Exception: pass` only on other exceptions. | `np.float64(nan/inf)→ValueError` (guard path); `np.float32(nan)/np.longdouble(nan)/pd.NA→NaT` (non-`float` isinstance branch, no 351-352). No plausible scalar raised non-`ValueError` in guarded region. | (1)(2) no new mechanism (3) fails for production-realistic scalars (4) none. |
| `334-335,338-342` `_coerce_to_datetime_scalar` 330-342 | NaT identity/type-name checks raise `ValueError("bad")` before generic `except Exception: pass`. | `pd.NaT→ValueError`; `np.datetime64('NaT',ns/D)→NaT` (314-320 path); `np.timedelta64('NaT')→TypeError`. Re-raise-before-generic-pass preserved. | (1)(2)(3) closed (4) none. |
| `403-404` `_coerce_to_datetime_scalar` 361-404 | Regex-admitted numeric `str` → builtin `float(s)`; epoch branches individually guarded. | Overflow/underflow strings (`1e308/309/1.7e308`, ±400-digit) → `ValueError` via guarded branches/inner handling (no outer except). Unicode decimal digits `U+0661..0664` parsed as epoch seconds (`1970-01-01 00:20:34Z`, valid path). `+`/whitespace variants parsed. | (1)(2) no new mechanism (3) production-realistic numeric strings exercised, no outer-except reach (4) none. |
| `43-44` `_not_null` 33-44 | `is None` identity; `pd.isna` swallowed 38-41; unconditional `return not is_na` 42. | `pd.NA/pd.NaT/nan→False`; `np.ma.masked/np.int64/bool/int/str→True`. No outer except. | (1)(2)(3) closed (4) none. |
| `953` `_normalize_asset_name` 949-954 | `split()` never yields empty token; `if not tok_clean: continue` construction-unreachable. | Unicode NBSP/tab/ZWSP/slash-prefix/long tokens normalized (`ETH`, `\u200bETH`, `''` for `/ETH` via filter path), **no 953**. | (1)(2) closed (3) realistic names exercised (4) none. |
| `641-642,694-695` `_detect_and_normalize_exchange_format` 598-642,648-695 | 598/648 outer handlers; inner setup/normalization guarded and inner try blocks swallow. | SubDF (via `_constructor`), MultiIndex cols, nullable string cols, all-caps, dup-cols (`BABDataError` from normalization) exercised inner/guarded paths; **no outer-handler reach** on real `pd.DataFrame`/subclass access semantics. | (1)(2) no new mechanism (3) fails for production-realistic frames (4) none. |
| `791-792` `_promote_datetime_column` 760-792 | 760-790 individually guarded tz/naive handling. | tz-aware UTC/US-Eastern, nullable string dates, mixed-tz object hit guarded/type paths (`TypeError` expected in tested call shape), **no 791-792**. | (1)(2) closed (3) guarded (4) none. |
| `322,326` inspect/campaign_d NaT guards | **Guard-relevant.** | **Not probed/altered.** | Preserved. |

**Conclusion:** **36-miss floor remains mechanism-closed at `c3a909b`.** No production-realistic miss reduction found; no canonical test/probe added. Batch130 materially-new fuzz method exhausted without satisfying all 4 strict criteria for any remaining cluster. **Batch131 only** on a concretely demonstrated, production-realistic `pd.DataFrame`/index/dtype/column-label mechanism satisfying all 4 criteria, or a different materially-new method with concrete, reproducible evidence beyond 103–130.

---

## Batch132 (2026-11-08T01:00Z, SHA a66bec2, fresh Step 0 rebaseline + forced-campaign public-entrypoint/NA-scalar fuzz, 0 delta)

**Scope:** `strategies/betting_against_beta/data_loader.py` remaining 36 misses `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953` (verified `--rcfile=/dev/null`, `--show-missing`). **No production code changed. No canonical test added. No workflow edits. `322,326` preserved.**

**Canonical (fresh):** `1466 passed, 0 failed, 17 skipped, 107 warnings` (46.32s). Coverage **36 miss / 1683 stmts / 98%**. Guard `campaign_d*` **44 passed, 5 warnings** (0.52s). `data_loader.py` unchanged since `311656a`.

**Method (materially new vs 103–131):** public-helper/entrypoint schema fuzz with (a) nullable pandas dtypes in indexes/values (`Int64/Float64/string/boolean`, `pd.array(..., dtype=Int64)` with NA), `pd.NA`/`None`/`np.datetime64('NaT')`/`np.timedelta64`-NaT sentinel shapes in object/nullable indexes; (b) `pd.Index` and `pd.DataFrame` subclasses plausible as simple pipeline wrappers (`_constructor` round-trip); (c) CSV public entrypoint with `<NA>` marker; (d) NumPy scalar dispatch audit: `np.float64 isinstance float=True` reaches coercer float branch (345) but NaN/inf take guarded 347-350→`ValueError` (351-352 not hit); `np.datetime64('NaT')` type name `datetime64` (not `NaTType`) bypasses 330/336 identity checks and normalizes to `NaT` via coercer’s normal path (no 334-342/351-352 hit); (e) custom `pd.isna`-raising-like object through `_not_null` returned `True` (inner `pd.isna` guarded; 43-44 not hit); (f) ambiguous/Unicode-decimal/overflow epoch strings through coercer (`U+0661..0664` parsed as valid epoch seconds inside guarded path, not 403-404); (g) `_normalize_asset_name` whitespace/quote-token/currency-token cases (953 not hit). Coverage traces collected with `coverage.Coverage` per-target.

**Cluster appendix (all 10, strict 4 criteria):** (1) target+line→code verified @ `a66bec2`; (2) no mechanism not disproven by 103–131 + this method; (3) no production-realistic `pd.DataFrame`/index/dtype/column-label + plausible pandas/library behavior demonstrated; (4) no statable control-flow path consistent with (2)-(3).

| Cluster | Lines (file:line) | New-method check (observed) | Verdict |
|---|---|---|---|
| `_normalize_index` dayfirst last-ditch | `data_loader.py:234-244,246-247` | Coercer deterministic: if 232 `_coerce_to_datetime_scalar(v)` succeeds it `continue`s 233; if it raises, 238/242 `pd.to_datetime(..., dayfirst=True, errors='raise')` are no stronger than coercer’s own parse attempts. Nullable/NA/np.datetime64-NaT/object sentinel indexes normalized or raised via 223/248 intercepts; no hit. Same-length 245 assignment safe. | **Closed (structural/determinism).** |
| `_normalize_index` outer VE/TE | `data_loader.py:268-269` | 261-265 converts any `Exception`→`BABDataError`; 266 catches/re-raises `BABDataError` before 268; `BABDataError⊂ValueError` (MRO). Nullable/index-subclass/DF-subclass/CSV `<NA>` shapes exercised normal/converted paths only. | **Closed (handler-order/MRO).** |
| `_coerce_to_datetime_scalar` NaN/inf generic except | `data_loader.py:351-352` | `np.float64` is `isinstance(val,float)` (reaches 345); `np.isnan/np.isinf` raise `ValueError` → 349-350 re-raise, 351-352 not reached. `np.float32`/`np.longdouble` NaN/inf take non-float/coercer-normal paths (no 351-352). Only pathological non-`ValueError` from numeric check would reach 351-352 (semantic bypass). | **Closed for production-realistic scalars.** |
| `_coerce_to_datetime_scalar` NaT re-raise guards | `data_loader.py:334-335,338-342` | `ValueError("bad")` re-raised at 332/339 before generic `except Exception: pass`. `np.datetime64('NaT')` normalizes to `NaT` (not caught by `NaTType` name/identity guards in this pandas behavior) — expected path, not 334-342. `pd.NA`/timedelta-NaT produce `NaT`/`TypeError` via normal/outer handling. | **Closed (re-raise-before-generic-pass).** |
| `_coerce_to_datetime_scalar` epoch outer except | `data_loader.py:403-404` | Regex-admitted numeric strings: `float(s)` returns builtin `float` (`inf` on overflow, no raise); epoch branches individually guarded. Unicode decimal digits matched by Python `\d` parse as valid epoch seconds inside guarded path. No regex-admitted string reached 403-404. | **Closed (regex+float+guarded branches).** |
| `_not_null` outer except | `data_loader.py:43-44` | `is None` identity (35); `pd.isna` guarded 38-41; unconditional `return True` 42. Custom object → `_not_null` returned `True`; `pd.NA`/`NaT`/`nan` → `False`. No unwrapped fallible statement reaches 43-44. | **Closed (structural).** |
| `_normalize_asset_name` empty token continue | `data_loader.py:953` | `str.split()` never yields empty tokens; whitespace-only/currency-token/Unicode whitespace cases exercised 947-958 without 953. | **Closed (construction-unreachable).** |
| `_detect_and_normalize_exchange_format` outer handlers | `data_loader.py:641-642,694-695` | `pd.DataFrame` subclass (simple `_constructor`) and real exchange-like/date/close/symbol shapes normalized through inner guarded/swallowing paths. Prior batch128 showed DataFrame-subclass `__getitem__` raise boundary — specialized/non-production-realistic under strict criteria. | **Closed for production-realistic frames.** |
| `_promote_datetime_column` outer handler | `data_loader.py:791-792` | 760-790 individually guarded; `hasattr` descriptor-safe in Python 3. Nullable/string/normal datetime promotion paths remained in guarded/type-normalization flow. | **Closed (fully guarded).** |
| inspect/campaign_d NaT guards | `data_loader.py:322,326` | **Not probed/altered (guard-relevant).** Guard `44 passed, 5 warnings`. | **Preserved.** |

**Conclusion:** **36-miss floor remains mechanism-closed at `a66bec2`.** No miss reduction; no new production-realistic control-flow mechanism satisfied all 4 criteria. Batch132 adds materially-new public-entrypoint/nullable-NA/NumPy-scalar-dispatch/Unicode-epoch fuzz evidence beyond 103–131. **Batch133 only** if a concretely demonstrated production-realistic mechanism satisfies all 4 criteria, or a different materially-new method with reproducible evidence closes a previously untested plausible gap.

---

## Batch133 (2026-11-08T01:27Z, SHA e6e8756, fresh Step 0 rebaseline + forced-campaign public-entrypoint trace, 0 delta)

**Scope:** `strategies/betting_against_beta/data_loader.py` remaining 36 misses `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953` (verified `--rcfile=/dev/null`, `--show-missing`). **No production code changed. No canonical test added. No workflow edits. `322,326` preserved.**

**Canonical (fresh):** `1466 passed, 0 failed, 17 skipped, 107 warnings` (45.75s). Coverage **36 miss / 1683 stmts / 98%**. Guard `campaign_d*` **44 passed, 5 warnings** (0.62s). `data_loader.py` unchanged since `311656a`. Bottlenecks routed: deps via `PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`; `.coverage*` cleaned; controller test ignored. `.gitignore` updated to ignore `debug_beta*.py`/`probe*.py` scratch (non-production, not committed).

**Method (materially new vs 103–132):** `sys.settrace` line-hit collection across **public** `load_returns`/`load_prices` entrypoints (not only internal helpers) over 43 realistic crypto/file-shape cases: Binance ms-OHLCV CSV with `close_time`; ISO timestamps; multiple date-column aliases (`timestamp/datetime/time/Date/Timestamp`); JSONL symbol/close rows; Parquet/Feather/Pickle/HDF5 round-trips (HDF5 with/without key); `PeriodIndex`, `CategoricalIndex`, string-dtype index, period column; nullable `Float64`/`Int64`/`string` extension dtypes with NA; duplicated+unsorted timestamps; safe `pd.DataFrame` subclass (`_constructor`); `load_prices`/`load_returns` DataFrame inputs with `price_column`; direct coercer probes (epoch s/ms, ISO, `datetime64`, `Timestamp`, `None`/`nan`/`NaT`/`pd.NA`/`bool`/`int`); asset-name normalization variants; mixed object index (Timestamp/ISO string/datetime64/epoch-string/float epoch); long-format pivot (`timestamp/symbol/close`); BOM CSV (`\xef\xbb\xbf`); TSV; gzip-compressed CSV; JSON `orient='split'`; JSON dict keyed by date; mixed-epoch-scale index (s + ms); all-duplicate index; odd symbol/blank columns. `float64[pyarrow]` skipped (pyarrow not installed, expected). **Observed:** 0 target-line hits across all 43 cases (`HITS []`, `TARGET_HITS []`).

**Cluster appendix (all 10, strict 4 criteria):** (1) target+line→code verified @ `e6e8756` (unchanged). (2) No mechanism not disproven by 103–132 + this method. (3) No production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior demonstrated. (4) No statable control-flow path consistent with (2)-(3).

| Cluster | Lines | New-method evidence (batch133, observed) | Verdict |
|---|---|---|---|
| `_normalize_index` dayfirst last-ditch | `234-244,246-247` | Mixed Timestamp/ISO/datetime64/epoch-string/float-epoch index, dup/unsorted, Categorical/string/Period, JSON/CSV/Parquet round-trips all normalized or intercepted by 223/248; no coercer divergence. | **Closed.** |
| `_normalize_index` outer VE/TE | `268-269` | Public file/DataFrame loads exercised conversion+266-re-raise path only; no plain VE/TE escape. | **Closed (handler-order/MRO).** |
| `_coerce_to_datetime_scalar` NaN/inf generic except | `351-352` | Direct coercer cases `nan/NaT/pd.NA/None/valid` hit guarded/normal paths; no non-`ValueError` in NaN/inf region. | **Closed for production-realistic scalars.** |
| `_coerce_to_datetime_scalar` NaT re-raise guards | `334-335,338-342` | `NaT/pd.NA/None` behaved per contract; re-raise-before-generic-pass preserved. | **Closed.** |
| `_coerce_to_datetime_scalar` epoch outer except | `403-404` | Epoch s/ms, overflow-adjacent realistic strings not triggered; regex+`float()`+guarded branches held. | **Closed.** |
| `_not_null` outer except | `43-44` | Nullable extension dtypes / NA sentinels exercised inner-guarded paths. | **Closed (structural).** |
| `_normalize_asset_name` empty token continue | `953` | Public odd-symbol/blank-column names normalized; `split()` construction-unreachable. | **Closed.** |
| `_detect_and_normalize_exchange_format` outer handlers | `641-642,694-695` | Binance OHLCV ms, JSONL symbol/close, long pivot, DF subclass exercised inner guarded/swallowing paths; no outer-handler reach on real frames. | **Closed for production-realistic frames.** |
| `_promote_datetime_column` outer handler | `791-792` | Multiple date aliases, BOM/TSV/gzip/JSON split, nullable columns promoted via guarded paths. | **Closed (fully guarded).** |
| inspect/campaign_d NaT guards | `322,326` | **Not probed/altered.** Guard 44/5 green. | **Preserved.** |

**Strict 4-criteria assessment:** none satisfied for miss reduction. (1) targets/code verified. (2) no mechanism not disproven by 103–132 + this public-entrypoint trace. (3) no production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path demonstrated. (4) no statable path consistent with (2)-(3).

**Conclusion:** **36-miss floor remains mechanism-closed at `e6e8756`.** No miss reduction; no canonical test added. Batch133 adds materially-new public-entrypoint/file-format round-trip trace evidence. **Batch134 only** on a concretely demonstrated production-realistic mechanism satisfying all 4 criteria, or a different materially-new method with reproducible evidence closing a previously untested plausible gap.

---

## Batch137 (2026-11-08T04:00Z, SHA 0d00688, fresh Step 0 rebaseline + forced-campaign materially-new-method appendix, 0 delta)

**Scope:** `strategies/betting_against_beta/data_loader.py` remaining 35 misses `43-44, 234-244, 246-247, 268-269, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953` (verified `--rcfile=/dev/null`, `--show-missing` at `0d00688`; `data_loader.py` unchanged since `e945fde` for miss line→code). `322` covered in canonical aggregate. **No production code changed. No canonical test added. No workflow edits. `322,326` preserved.**

**Canonical (fresh):** `1494 passed, 0 failed, 17 skipped, 109 warnings` (47.99s). Coverage **35 miss / 1683 stmts / 98%**. Guard `campaign_d*` **44 passed, 5 warnings** (0.65s). Deps: `PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib` (`hypothesis 6.170.15`; no pyarrow/pytables/fastparquet). `.coverage*` cleaned; controller test ignored.

**Methods (materially new vs 103–136 recorded evidence):** (A) `hypothesis` randomized CSV round-trips through public `load_returns` (60 examples, finite/NaN floats, multiple date-string forms, `deadline=None`) — all normalized or raised expected loader errors; no target hits. (B) Nullable pandas extension dtypes through public `load_returns` CSV (`Int64/Float64/string/boolean` with NA) — no target hits (some shapes raised duplicate-column normalization errors in this construction; no defensive-handler lines reached). (C) CSV dialect/marker/encoding-adjacent variants through public `load_returns`: BOM, TSV, semicolon+decimal-comma shape, custom NA markers (`N/A`, `--`), quoted, blank lines, CRLF — no target hits. (D) Full `read_json`/`to_json` orient matrix (`split/records/index/columns/table/values`) including tz-aware `split` — no target hits. (E) Timezone metadata round-trips (UTC/US/Eastern/Asia/Kolkata) via CSV and JSON — no target hits. (F) Index-shape fuzz through `_normalize_index` with `PeriodIndex`, `CategoricalIndex` of datetimes, `IntervalIndex`, nullable string index, `np.datetime64`+`NaT` object arrays, mixed epoch/object/Timestamp indexes, all-`NaT` object, `pd.NA` object, float/ms epoch indexes, Unicode date strings — no target hits. (G) Coercer edge probes: `np.float64/float32/longdouble` NaN/inf, `np.int64` epoch s/ms, `pd.NA`, `np.datetime64('NaT',ns)`, `np.timedelta64('NaT',ns)`, bool/`np.bool_`, Arabic-Indic Unicode digit epoch string, 400-digit overflow strings, scientific epoch string, ambiguous `01/02/03`, ISO Z, space+offset — no target hits. (H) Exchange/promote public shapes: MultiIndex JSON, `pd.DataFrame` subclass (`_constructor`) through detect/promote, duplicate date columns CSV — no target hits. (I) Asset-name/`_not_null` sentinel probes (`NBSP`/ZWSP/tab forms, odd symbols, `pd.NA/NaT/nan/masked/object`) — no target hits. `sys.settrace` line-hit collection, `TARGETS={43,44,234-244,246-247,268-269,326,334-335,338-342,351-352,403-404,641-642,694-695,791-792,953}`. **Observed:** 0 target-line hits across ~99 deterministic cases + 60 Hypothesis examples.

**Cluster appendix (all remaining, strict 4 criteria):** (1) target+line→code verified @ `0d00688`. (2) No mechanism not disproven by 103–136 + methods A–I. (3) No production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior demonstrated. (4) No statable control-flow path consistent with (2)-(3). `322` covered (guard still green); `326` guard-relevant, not altered.

| Cluster | Lines (file:line) | Batch137 method/result (observed) | Verdict |
|---|---|---|---|
| `_normalize_index` dayfirst last-ditch | `234-244,246-247` | F: Period/Categorical/Interval/nullable string/`np.datetime64`+NaT/mixed epoch/all-NaT/`pd.NA`/Unicode date indexes normalized or intercepted by 223/248; A/C/D/E public loads with varied date forms did not trigger coercer divergence (232 deterministic). | **Closed (structural/determinism).** |
| `_normalize_index` outer VE/TE | `268-269` | A–F exercised converted/raised paths only; 261-265→`BABDataError`, 266 re-raises before 268 (`BABDataError⊂ValueError`). | **Closed (handler-order/MRO).** |
| `_coerce_to_datetime_scalar` NaN/inf generic except | `351-352` | G: `np.float64/float32/longdouble` NaN/inf hit guarded `ValueError`/normal paths; no non-`ValueError` from numeric check. | **Closed for production-realistic scalars.** |
| `_coerce_to_datetime_scalar` NaT re-raise guards | `334-335,338-342` | G: `pd.NA`/`np.datetime64('NaT',ns)`/`np.timedelta64('NaT',ns)` behaved per contract; re-raise-before-generic-pass preserved. | **Closed.** |
| `_coerce_to_datetime_scalar` epoch outer except | `403-404` | G: Arabic-Indic digits parsed via Python `\d`/epoch path; 400-digit overflow, sci epoch, ISO Z/offset strings stayed in guarded/normal parsing; regex+`float()`+guarded branches held. | **Closed (regex+float+guarded).** |
| `_not_null` outer except | `43-44` | I: `pd.NA/NaT/nan/masked/object`/numeric sentinels returned via inner-guarded/identity paths. | **Closed (structural).** |
| `_normalize_asset_name` empty token continue | `953` | I: whitespace/Unicode/NBSP/ZWSP/odd-symbol forms normalized; `str.split()` construction-unreachable. | **Closed.** |
| `_detect_and_normalize_exchange_format` outer handlers | `641-642,694-695` | H/C/B: exchange-like duplicate/MultiIndex/subclass/public CSV-JSON shapes exercised inner guarded/swallowing paths; no outer-handler reach on real `pd.DataFrame`/subclass access semantics. | **Closed for production-realistic frames.** |
| `_promote_datetime_column` outer handler | `791-792` | B/D/E/H: nullable/tz-aware/MultiIndex/date-alias promotion through guarded paths; 760-790 individually guarded. | **Closed (fully guarded).** |
| inspect/campaign_d NaT guard | `326` | **Not probed/altered (guard-relevant).** Guard 44/5 green. | **Preserved.** |

**Strict 4-criteria assessment:** none satisfied for miss reduction. (1) targets/code verified. (2) no mechanism not disproven by 103–136 + methods A–I. (3) no production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior demonstrated. (4) no statable path consistent with (2)-(3).

**Conclusion:** **35-miss floor remains mechanism-closed at `0d00688`.** No miss reduction; no canonical test added. Batch137 adds materially-new Hypothesis/public-loader/nullable-extension-dtype/JSON-orient/tz-roundtrip/index-shape/coercer-sentinel evidence beyond 103–136. **Batch138 only** on a concretely demonstrated production-realistic mechanism satisfying all 4 criteria, or a different materially-new method with reproducible evidence closing a previously untested plausible gap.

---

## Batch138 (2026-11-08T04:01Z, SHA c3e44a3, fresh Step 0 rebaseline + forced-campaign materially-new-method appendix, 0 delta)

**Scope:** `strategies/betting_against_beta/data_loader.py` remaining 35 misses `43-44, 234-244, 246-247, 268-269, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953` (verified `--rcfile=/dev/null`, `--show-missing` at `c3e44a3`; `data_loader.py` unchanged since `e945fde`). `322` covered in canonical aggregate. **No production code changed. No canonical test added. No workflow edits. `322,326` preserved.**

**Canonical (fresh):** `1496 passed, 0 failed, 17 skipped, 109 warnings` (47.75s). Coverage **35 miss / 1683 stmts / 98%**. Guard `campaign_d*` **44 passed, 5 warnings** (0.68s).

**Conclusion:** 35-miss floor remains mechanism-closed at `c3e44a3`. Batch139 only on a concretely demonstrated production-realistic mechanism satisfying all 4 criteria, or a different materially-new method with reproducible evidence closing a previously untested plausible gap.

---

## Batch139 (2026-11-08T04:08Z, SHA 24db195, fresh Step 0 rebaseline + forced-campaign materially-new-method appendix, 0 delta)

**Scope:** `strategies/betting_against_beta/data_loader.py` remaining 35 misses `43-44, 234-244, 246-247, 268-269, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953` (verified `--rcfile=/dev/null`, `--show-missing` at `24db195`; `data_loader.py` unchanged since `e945fde` for miss line→code). `322` covered in canonical aggregate. **No production code changed. No canonical test added. No workflow edits. `322,326` preserved.**

**Canonical (fresh):** `1496 passed, 0 failed, 17 skipped, 109 warnings` (48.01s). Coverage **35 miss / 1683 stmts / 98%** (`Name strategies/betting_against_beta/data_loader.py Stmts 1683 Miss 35 Cover 98% Missing 43-44, 234-244, 246-247, 268-269, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`). Guard `campaign_d*` **44 passed, 5 warnings** (0.84s). Deps: `pytest/coverage/numpy 2.5.4/pandas 3.1.1/scipy/hypothesis 6.170.15` via `PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`; no `pyarrow/pytables/fastparquet`. `.coverage*` cleaned before canonical run.

**Methods (materially new vs 103–138 recorded evidence):** (A) **AST/control-flow proof from source** (parsed `data_loader.py`; inspected live function source). Verified `str.split()` token loop in `_normalize_asset_name` (940–958): `split()` never yields `''`; the `if not tok_clean: continue` at 952–953 is construction-unreachable for Python `str.split()`. Verified `BABDataError` MRO `(<BABDataError>, <ValueError>, <Exception>, <BaseException>)` confirming handler-order deadness for 268–269 (`except BABDataError` at 266 intercepts converted exceptions before `except (ValueError, TypeError)` at 268). Verified coercer contract: `np.datetime64('NaT','ns') -> NaT` (no raise), `pd.NaT/None/float('nan') -> ValueError` — deterministic inputs relevant to 234–247 dayfirst gate. Static proof is strong for construction/MRO/contract claims but **not sufficient alone** for miss reduction; runtime/aggregate reachability still governs coverage. (B) **Pandas 3.1.1 realistic constructor/public-loader boundaries** (no pyarrow): `pd.Index(..., dtype='string')`, nullable `Float64` NA, epoch-string JSON records, pickle roundtrip, `load_prices` CSV, exchange-style OHLCV-with-symbol/close_time, normal CSV returns. `sys.settrace` line-hit collection, `TARGETS` = all remaining miss lines. **Observed:** 0 target hits across cases; normal/warned paths only (`UserWarning` on date inference in some shapes, not target hits). (C) **Targeted single-boundary trace for 351–352**: monkeypatched `np.isnan` to raise `RuntimeError` during `_coerce_to_datetime_scalar(1.5)`. `sys.settrace` hit `351,352` (generic `except Exception: pass` after NaN check). **Assessment:** boundary is a test/monkeypatch perturbation of NumPy, **not plausible pandas/library behavior** for production-realistic scalars (criterion 3 fails); recorded as non-production boundary evidence only, **not** a miss-reduction candidate. (D) **Downstream-consumption trace**: `BABStrategy.run(returns_df=dl.load_returns(...))` with realistic BTC/ETH returns DataFrame exercised loader normalization end-to-end; **Observed:** 0 target hits. `np.float64` is `isinstance(float)`/`np.floating` and reaches the float branch (345); normal NaN/inf still take guarded `ValueError` re-raise paths — no 351–352 hit under unmodified NumPy.

**Cluster appendix (all remaining, strict 4 criteria):** (1) target+line→code verified @ `24db195` (line excerpts re-read: 43–44, 234–247, 268–269, 326, 334–342, 351–352, 403–404, 641–642/694–695, 791–792, 953). (2) No mechanism not disproven by 103–138 + methods A–D. (3) No production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior demonstrated. (4) No statable control-flow path consistent with (2)-(3). `326` guard-relevant, not altered.

| Cluster | Lines (file:line @ `24db195`) | Batch139 method/result (observed) | Verdict (strict 4 criteria) |
|---|---|---|---|
| `_not_null` outer except | `data_loader.py:43-44` | A+B: identity `None` return, inner `pd.isna` guarded 40–41, unconditional `return` 42; nullable/realistic loader shapes exercised no hit. | **Closed (structural).** (1)(2) yes; (3)(4) no production escape. |
| `_normalize_index` dayfirst last-ditch | `data_loader.py:234-244,246-247` | A+B: coercer determinism/NaT contract (232/220 same coercer); 223 intercept blocks 227 entry for mixed bad; string-dtype/epoch/realistic CSV/JSON/pickle shapes 0 hits. | **Closed (determinism+intercept).** |
| `_normalize_index` outer VE/TE | `data_loader.py:268-269` | A+B: `BABDataError⊂ValueError` MRO + 261–265 convert + 266 re-raise before 268; realistic shapes 0 hits. | **Closed (handler-order/MRO).** |
| inspect/campaign_d NaT guard | `data_loader.py:326` | **Not probed/altered.** Guard 44/5 green. | **Preserved (guard-relevant).** |
| `_coerce_to_datetime_scalar` NaT re-raise guards | `data_loader.py:334-335,338-342` | A+B: explicit `ValueError` re-raised before generic pass; `pd.NaT`/`np.datetime64('NaT')` contract consistent; 0 hits. | **Closed (re-raise-before-generic-pass).** |
| `_coerce_to_datetime_scalar` NaN/inf generic except | `data_loader.py:351-352` | B+D: unmodified NumPy/pandas realistic scalars (`np.float64` NaN/inf, `float`, nullable NA via normal paths) 0 hits. C: monkeypatched `np.isnan` RuntimeError hit 351–352 — **non-production boundary evidence only** (criterion 3 fails). | **Closed for production-realistic scalars; boundary hit not eligible.** |
| `_coerce_to_datetime_scalar` epoch outer except | `data_loader.py:403-404` | B: epoch-string JSON/CSV/realistic numeric strings stayed in guarded parse paths; regex-admitted `float()` builtin behavior unchanged; 0 hits. | **Closed (regex+float+guarded).** |
| `_detect_and_normalize_exchange_format` outer handlers | `data_loader.py:641-642,694-695` | B: OHLCV/symbol/close-time/normal exchange shapes exercised inner guarded/swallowing paths; 0 hits on real frames. | **Closed for production-realistic frames.** |
| `_promote_datetime_column` outer handler | `data_loader.py:791-792` | B: date/epoch/string promotion through guarded 760–790 paths; 0 hits. | **Closed (fully guarded).** |
| `_normalize_asset_name` empty token continue | `data_loader.py:953` | A: `str.split()` construction-unreachable; realistic symbol normalization 0 hits. | **Closed (construction-unreachable).** |

**Strict 4-criteria assessment:** none satisfied for miss reduction. (1) targets/code verified. (2) no mechanism not disproven by 103–138 + methods A–D. (3) no production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior demonstrated; method C is explicitly non-production. (4) no statable path consistent with (2)-(3).

**Conclusion:** **35-miss floor remains mechanism-closed at `24db195`.** No miss reduction; no canonical test added. Batch139 adds AST/MRO/coercer-contract static evidence, pandas 3.1.1 public-loader/downstream trace evidence, and an explicit non-production 351–352 boundary trace (recorded, not eligible) beyond 103–138. **Batch140 only** on a concretely demonstrated production-realistic mechanism satisfying all 4 criteria, or a different materially-new method with reproducible evidence closing a previously untested plausible gap.

---

## Batch 141 (2026-11-08T05:06Z, SHA `d97339d`, cross-module contract audit — materially-new method, 0 delta)

**Scope:** `strategies/betting_against_beta/data_loader.py` remaining 35 misses
`43-44, 234-244, 246-247, 268-269, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`
(verified `--rcfile=/dev/null`, `--show-missing` at `d97339d`; `data_loader.py` unchanged since `e945fde` for miss line→code; stmt count 1683). `322` covered in canonical aggregate. `326` guard-relevant, **DO NOT ALTER**. **No production code changed. No canonical test added. No workflow edits. Commit only if explicitly requested.**

**Canonical (fresh, `--rcfile=/dev/null` run+report):** **1496 passed, 0 failed, 17 skipped, 109 warnings** (25.16s). Coverage **35 miss / 1683 stmts / 98%**. Missing exactly `43-44, 234-244, 246-247, 268-269, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. Guard `campaign_d*` **44 passed, 5 warnings** (0.41s). Deps: `PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib` (`pytest 9.2.0`, `coverage 7.17.2`, `numpy 2.5.4`, `pandas 3.1.1`, `scipy 1.18.1`, `hypothesis 6.170.15`; no `pyarrow`/`pytables`/`fastparquet`). `.coverage*` cleaned pre-run.

**Method (materially new vs B103–140 recorded evidence — cross-module contract audit, not previously recorded):** AST-grep caller map of the `strategies.betting_against_beta` package for every loader public/private helper, then `sys.settrace` line-hit collection on `data_loader.py` across the **real end-to-end pipeline** `BABStrategy.run(returns_df=...)` (strategy → `_load_returns` → `load_returns` → `validate_returns_dataframe` → `_promote_datetime_column`/`_normalize_index`/`_coerce_numeric`/`_strip_units_and_parse`/`_normalize_asset_name` → `calculate_rolling_beta` → `generate_bab_signals` → `construct_portfolio` → `run_backtest`) plus public entrypoint traces (`load_returns`/`load_prices` via CLI/DataSource shapes).

**Caller map (AST, strategies package, excluding data_loader.py):**
- `load_returns`: `strategy.188`, `strategy.195` (`BABStrategy._load_returns`); `cli.259`, `cli.294`; `data_sources.28/36/48/56/64` (CSV/Parquet/HDF5/Pickle/DataFrame sources).
- `load_prices`: `cli.257`, `cli.292`.
- `BABDataError`: raised/imported across `beta`, `cli`, `portfolio`, `strategy`.

**Traced shapes (sys.settrace; target set = all 35 miss lines):**
1. `BABStrategy.run` valid_wide_benchmark_first → OK, loader_lines_hit=223, target_hits=[]
2. `BABStrategy.run` valid_wide_benchmark_mid → OK, 222, []
3. `BABStrategy.run` prices_wide_ohlcv → BABDataError (benchmark not in OHLCV cols), 232, []
4. `BABStrategy.run` exchange_long_symbol_close → OK, 283, []
5. `BABStrategy.run` exchange_ohlcv_symbol_close_time → BABDataError (only benchmark column), 354, []
6. `BABStrategy.run` missing_benchmark → BABDataError, 218, []
7. `BABStrategy.run` all_nan_column → OK, 226, []
8. `BABStrategy.run` duplicate_timestamps → OK, 223, []
9. `BABStrategy.run` string_iso_index → OK, 282, []
10. `BABStrategy.run` numeric_epoch_ms_index → OK, 290, []
11. `BABStrategy.run` date_column_alias_timestamp → OK, 329, []
12. `BABStrategy.run` minimal_valid → OK, 217, []
13. `load_returns` dataframe valid → OK, 223, []
14. `load_returns` dataframe missing_bench → BABDataError, 218, []
15. `load_prices` ohlcv_wide → BABDataError (benchmark missing), 232, []

**Observed:** **0 target-line hits across all 15 cross-module shapes.** Loader lines exercised are confined to the happy-path/validation-raise spine (217–232, 223–226, 228–232, 282–283, 290, 329, 354); none of the 35 remaining miss lines are reached by any production-realistic cross-module caller shape.

**Cluster appendix (all remaining, strict 4 criteria):** (1) target+line→code verified @ `d97339d`. (2) no mechanism not disproven by B103–140 + this cross-module contract audit. (3) no production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior demonstrated (cross-module end-to-end pipeline traced, 0 hits). (4) no statable control-flow path consistent with (2)–(3). `326` guard-relevant, not altered.

| Cluster | Lines (file:line @ `d97339d`) | Batch141 method/result (observed) | Verdict (strict 4 criteria) |
|---|---|---|---|
| `_not_null` outer except | `data_loader.py:43-44` | Cross-module shapes exercised `_not_null` via `_series_has_any_finite`/`_coerce_numeric`; identity `v is None` (35), inner `pd.isna` guarded (40–41), unconditional `return` (42). 0 hits. | **Closed (structural).** (1)(2) yes; (3)(4) no production escape. |
| `_normalize_index` dayfirst last-ditch | `data_loader.py:234-244,246-247` | Numeric epoch-ms / string-ISO / date-alias / mixed object indexes through `BABStrategy.run`; coercer determinism (232 same as 216-224) + 223 intercept block dayfirst entry. 0 hits. | **Closed (determinism+intercept).** |
| `_normalize_index` outer VE/TE | `data_loader.py:268-269` | All pipeline exception paths convert to `BABDataError`; `BABDataError⊂ValueError` MRO; 266 `except BABDataError: raise` precedes 268. 0 hits. | **Closed (handler-order/MRO).** |
| inspect/campaign_d NaT guard | `data_loader.py:326` | **Not probed/altered (guard-relevant).** Guard 44/5 green. | **Preserved (guard-relevant).** |
| `_coerce_to_datetime_scalar` NaT re-raise guards | `data_loader.py:334-335,338-342` | `pd.NaT`/`None`/valid scalars through coercer across pipeline shapes; `ValueError("bad")` re-raised before generic `except Exception: pass`. 0 hits. | **Closed (re-raise-before-generic-pass).** |
| `_coerce_to_datetime_scalar` NaN/inf generic except | `data_loader.py:351-352` | `np.float64`/float NaN/inf through coercer in pipeline validation; guarded `ValueError`/normal paths; no non-`ValueError` from numeric check. 0 hits. | **Closed for production-realistic scalars.** |
| `_coerce_to_datetime_scalar` epoch outer except | `data_loader.py:403-404` | Epoch-ms/s numeric index and date-column-alias shapes through pipeline; regex-admitted `float(s)` builtin, epoch branches individually guarded. 0 hits. | **Closed (regex+float+guarded).** |
| `_detect_and_normalize_exchange_format` outer handlers | `data_loader.py:641-642,694-695` | Exchange long-format (symbol/close) and OHLCV (symbol/close_time) frames through `BABStrategy.run`; inner guarded/swallowing paths only. 0 hits on real frames. | **Closed for production-realistic frames.** |
| `_promote_datetime_column` outer handler | `data_loader.py:791-792` | String-ISO / date-alias / epoch-ms index promotion through pipeline; 760–790 individually guarded. 0 hits. | **Closed (fully guarded).** |
| `_normalize_asset_name` empty token continue | `data_loader.py:953` | Realistic crypto symbol normalization (BTC/ETH/SOL/BNB/XRP, slash pairs, quote suffixes) across pipeline column normalization; `str.split()` never yields empty token. 0 hits. | **Closed (construction-unreachable).** |

**Strict 4-criteria assessment:** none satisfied for miss reduction. (1) targets/code verified @ `d97339d`. (2) no mechanism not disproven by B103–140 + this cross-module contract audit. (3) no production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior demonstrated (end-to-end cross-module trace, 0 hits). (4) no statable control-flow path consistent with (2)–(3).

**Conclusion:** **35-miss floor remains mechanism-closed at `d97339d`.** No miss reduction (delta 0); no canonical test added. Batch141 adds the materially-new cross-module contract audit (AST caller map + `sys.settrace` end-to-end `BABStrategy.run` trace, 0 target hits) beyond B103–140. All 35 remaining clusters carry a strict 4-criteria verdict. Next session: only on a concretely demonstrated production-realistic mechanism satisfying all 4 criteria, or a different materially-new method with reproducible evidence closing a previously untested plausible gap.

## Campaign: 35-miss floor (mechanism-closed, Batch 142; 2026-11-08 @ `2a272a7`)
- **SHA:** `2a272a7`. **Canonical aggregate (fresh, measured 2026-11-08, `--rcfile=/dev/null`, `.coverage*` cleaned):** **1496 passed, 0 failed, 17 skipped, 109 warnings**.
- **Coverage:** `strategies/betting_against_beta/data_loader.py` **35 miss / 1683 stmts / 98%**. Missing: `43-44,234-244,246-247,268-269,326,334-335,338-342,351-352,403-404,641-642,694-695,791-792,953`.
- **Guard:** **44 passed, 5 warnings** (`campaign_d*`, excluding controller). **Delta 0 (no miss reduction); no canonical test added; no production/semantic/workflow changes. `322,326` preserved.**

**Materially-new Batch142 methods (not recorded in B103–141):** (A) `sys.settrace` over public file-path + DataFrame + exchange/nullable/Categorical/np-dtype shapes: `load_returns`/`load_prices` from real CSV/JSON temp files; `pd.MultiIndex` columns (OHLCV-like); `CategoricalIndex` columns; nullable `Float64` with `pd.NA`; `np.str_`/numeric-parseable index attempts; `datetime64[ns|us|ms|s]` indexes; `_coerce_to_datetime_scalar` over `np.float64/32` NaN/inf, `np.int64` epochs, `np.datetime64('NaT')`, `pd.Timestamp/NaT/None/ISO/epoch`; `_not_null`/`_series_has_any_finite` over `pd.NA`/NaN/None/inf/exotic; exchange long (`symbol/ticker/pair` × `close/price`) and OHLCV pivot paths; `_normalize_asset_name` realistic variants; duplicate-index and `BABStrategy.run` with nullable `Float64`. (B) Hypothesis (`deadline=None`, `HealthCheck` suppressed): 800-example `_coerce_to_datetime_scalar` fuzz (None/bool/int/float-nan-inf/text/bytes-latin1/`NaT` variants/np scalars/epoch strings/ISO/BOM/quoted/empty/null tokens); 80-example `load_returns` with random returns + `NaN` holes; 100-example mixed object-index frames; 30-example exchange-column-name variants; 500-example `_normalize_asset_name` text; 300-example `_not_null`/`_coerce_numeric`. All traced against the 35-miss target set.

**Observed:** **0 target-line hits** across all production-realistic traced cases and Hypothesis examples (A+B). Hits confined to happy-path/validation spine; warnings were pandas parse/format noise only.

**Cluster appendix (all remaining, strict 4 criteria; file:line @ `2a272a7`):** (1) target+line→code verified @ `2a272a7` (code unchanged since floor). (2) no mechanism not disproven by B103–141 + this Batch142 file-path/nullable/Categorical/np-dtype/Hypothesis audit. (3) no production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior demonstrated (0 hits). (4) no statable control-flow path consistent with (2)–(3). `326` guard-relevant, not altered.

| Cluster | Lines (file:line @ `2a272a7`) | Batch142 method/result (observed) | Verdict (strict 4 criteria) |
|---|---|---|---|
| `_not_null` outer except | `data_loader.py:43-44` | A+B: `pd.NA`/NaN/None/inf/np scalars through `_not_null`/`_series_has_any_finite`/coercion (300+ traced). Identity/`pd.isna` guarded; unconditional return. 0 hits. | **Closed (structural).** (1)(2) yes; (3)(4) no production escape. |
| `_normalize_index` dayfirst last-ditch | `data_loader.py:234-244,246-247` | A+B: CSV/JSON files, ISO/epoch/object/mixed/np.str_/duplicate/`datetime64`-unit indexes, Hypothesis mixed-object indices (100). Coercer determinism + 223 intercept block entry. 0 hits. | **Closed (determinism+intercept).** |
| `_normalize_index` outer VE/TE | `data_loader.py:268-269` | All pipeline/public errors convert/raise as `BABDataError`; handler order/MRO (`BABDataError⊂ValueError`, 266 precedes 268). 0 hits. | **Closed (handler-order/MRO).** |
| inspect/campaign_d NaT guard | `data_loader.py:326` | **Not probed/altered (guard-relevant).** Guard 44/5 green. | **Preserved (guard-relevant).** |
| `_coerce_to_datetime_scalar` NaT re-raise guards | `data_loader.py:334-335,338-342` | A+B: `pd.NaT`/`np.datetime64('NaT',ns/us/s)`/None/valid scalars; ValueError re-raise-before-generic-pass path exercised (800-example fuzz). 0 hits. | **Closed (re-raise-before-generic-pass).** |
| `_coerce_to_datetime_scalar` NaN/inf generic except | `data_loader.py:351-352` | A+B: `float`/`np.float64`/`np.float32` NaN/inf; numeric checks raise `ValueError` only; no non-`ValueError` from unmodified NumPy/pandas numeric ops observed. 0 hits. | **Closed for production-realistic scalars.** |
| `_coerce_to_datetime_scalar` epoch outer except | `data_loader.py:403-404` | A+B: epoch-ms/s strings/ints/np.uint64/float forms, ISO/offset/BOM/null tokens through regex+`float`+guarded branches. 0 hits. | **Closed (regex+float+guarded).** |
| `_detect_and_normalize_exchange_format` outer handlers | `data_loader.py:641-642,694-695` | A+B: exchange long/OHLCV realistic frames and Hypothesis column-name variants (`symbol/ticker/pair/asset/coin` × `close/price/last/value`) through `load_returns`; inner guards swallow. 0 hits. | **Closed for production-realistic frames.** |
| `_promote_datetime_column` outer handler | `data_loader.py:791-792` | CSV/JSON/file-path loads with date columns, nullable/Categorical/`datetime64` variants, pipeline promotion; 760–790 individually guarded. 0 hits. | **Closed (fully guarded).** |
| `_normalize_asset_name` empty token continue | `data_loader.py:953` | A+B: realistic variants + 500-example Hypothesis text fuzz; `str.split()` never yields `''`. 0 hits. | **Closed (construction-unreachable).** |

**Strict 4-criteria assessment:** none satisfied for miss reduction. (1) targets/code verified @ `2a272a7`. (2) no mechanism not disproven by B103–141 + Batch142 audit. (3) no production-realistic path demonstrated (0 hits). (4) no statable control-flow path consistent with (2)–(3).

**Conclusion:** **35-miss floor remains mechanism-closed at `2a272a7`.** No miss reduction (delta 0); no canonical test added. Batch142 adds materially-new file-path/public-loader + nullable/Categorical/MultiIndex/np-dtype + Hypothesis stateful-style scalar/loader/index/exchange/asset-name fuzz with `sys.settrace` (0 target hits) beyond B103–141. All 35 remaining clusters carry a strict 4-criteria verdict. Next session: only on a concretely demonstrated production-realistic mechanism satisfying all 4 criteria, or a different materially-new method with reproducible evidence closing a previously untested plausible gap.

## Batch145 (2026-11-08T06:49Z, SHA `2848cf7`, fresh Step 0 rebaseline + materially-new ladder-state/IO-seam trace, 0 delta)

**Scope:** `strategies/betting_against_beta/data_loader.py` remaining 35 misses `43-44, 234-244, 246-247, 268-269, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953` (verified `--rcfile=/dev/null`, `--show-missing` at `2848cf7`; `data_loader.py` unchanged since `e945fde` for miss line→code). `322` covered. `326` guard-relevant, **preserved**. **No production code changed. No canonical test added. No workflow edits.**

**Canonical (fresh, Step 0):** **1467 passed, 0 failed, 17 skipped, 109 warnings** (17.27s). Coverage **35 miss / 1683 stmts / 98%**, missing exactly `43-44, 234-244, 246-247, 268-269, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. Guard `campaign_d*` **44 passed, 5 warnings** (0.37s). Deps: `pytest 9.2.0`, `coverage 7.17.2`, `numpy 2.5.4`, `pandas 3.1.1`, `scipy 1.18.1`, `hypothesis 6.170.15` (`PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`; no `pyarrow`/`pytables`/`fastparquet`). `.coverage*` cleaned.

**Methods (materially new vs B103–144 recorded evidence):** (M1) **Public IO/parsing seam traces** (no parquet/hdf5 engines): `load_returns`/`load_prices` via `StringIO` and real temp CSV files with `na_values`, `keep_default_na=False`, `dtype=str`, `thousands`, `sep+decimal`, UTF-8 BOM, mixed newlines, trailing delimiters, duplicate date columns, `index_col` ambiguity, epoch-ms strings, quoted fields, `parse_dates`; temp JSON files for `records/columns/split/index/values/table` orients through public loaders; exchange-like CSV (`symbol,close,timestamp`). `sys.settrace` over all 35 targets. **Observed:** 0 target hits. (M2) **Realistic object/dtype boundary traces:** `_not_null` on `np.void`, complex, dict/list/array, custom objects; `load_returns` with object-dtype cells containing custom instances; `_normalize_asset_name` on tab/NBSP/ZWSP/IDEOGRAPHIC/NNBSP/form-feed/vertical-tab separators; nullable `string` dtype exchange timestamps, `pd.NA` timestamps, `Categorical` date columns, nullable `Int64` epoch promotion, `MultiIndex` columns through `load_returns`. **Observed:** 0 target hits (Unicode whitespace tokens normalized by `split()` to non-empty tokens or handled; `split()` on Python `str` still yields no `''`). (M3) **Ladder-state satisfiability proof (runtime coercer contract + trace):** verified coercer behavior relevant to `_normalize_index` 216–247: `pd.NaT -> ValueError`, `np.datetime64('NaT','ns') -> NaT` (returns), `np.datetime64('NaT','generic') -> NaT`, `'NaT'/'nat' -> NaT`, `None/nan/NaN/'' -> ValueError`. Traced `_normalize_index` on indices `['2024-01-01','NaT']`, object index containing `np.datetime64('NaT','generic')`, and garbage `['!!!bad!!!']`; traced `_coerce_to_datetime_scalar` NaT paths outside campaign_d context. **Observed:** 0 target hits. Control-flow implication: 234–244,246–247 (dayfirst last-ditch body, 227–245) require 225 true after 224 elementwise assignment; 220–224 appends `_coerce_to_datetime_scalar(v)` and only raises at 223 if coercer raises. For values where coercer returns `NaT` (np NaT-generic/ns, `'NaT'`/`'nat'` strings), 220 appends `NaT` without raise so 224 can complete with NaT present and 225 becomes true — but 230–233 inside 227–245 applies the same coercer and `continue`s on success (appending NaT), so 234–244 (dayfirst `pd.to_datetime` attempts / fallback append) are skipped for those elements; 246–247 only reached if 227–245 raises, but per-element coercer success causes `continue`, and remaining per-element failures hit 244–245. Under this contract, satisfying 234–244 requires an element where coercer raises at 230–233 (so 234 attempted) but coercer did not raise at 220–223 for the same value — impossible for deterministic coercer on same value. 246–247 requires 227–245 to raise; deterministic per-element handling makes a full-loop raise depend on 244–245 path, but 234–244 are the dayfirst attempts/fallback body — their reachability is blocked by coercer determinism/continue. (M4) **Exception-type boundary on realistic numeric subclasses:** `float` subclass NaN/inf, `np.float16/longdouble` NaN, `decimal.Decimal` NaN/epoch — traced through `_coerce_to_datetime_scalar`. **Observed:** 0 target hits (351–352 generic `except Exception: pass` after `np.isnan/np.isinf` requires non-`ValueError` from numpy check under unmodified numpy; `Decimal('NaN')` does not enter `isinstance(val,float)` branch). (M5) **Exchange/promotion realistic dtype frames:** nullable string `close_time`, `pd.NA` timestamp, `Categorical` date, nullable `Int64` epoch, MultiIndex columns through `load_returns`. **Observed:** 0 target hits.

**Cluster appendix (all remaining, strict 4 criteria; line→code @ `2848cf7`/`e945fde`):**

| Cluster | Lines | Batch145 method/result (observed) | Verdict (strict 4 criteria) |
|---|---|---|---|
| `_not_null` outer except | `43-44` | M2 realistic odd objects/containers/void through direct + public loader object-dtype path; 0 hits. Identity/inner-guard/unconditional-return structure unchanged. | **Closed (structural).** (1)(2) yes; (3)(4) no demonstrated production escape. |
| `_normalize_index` dayfirst last-ditch | `234-244,246-247` | M1/M3 IO seams + NaT ladder-state traces; coercer returns NaT for np NaT-generic/ns and `'NaT'/'nat'` (no raise) causing 230–233 `continue` and skipping 234–244 for those elements; 234–244 need coercer-raise at 230–233 but not 220–223 on same deterministic value. 246–247 blocked by deterministic per-element control. 0 hits. | **Closed (determinism+continue/ladder-satisfiability).** (1)(2) yes; (3)(4) no demonstrated production-realistic satisfiable path. |
| `_normalize_index` outer VE/TE | `268-269` | M3 garbage-index trace: flow 259→261→262–265→266(BABDataError re-raise)→267; 268–269 not reached. 261–265 convert/raise; 266 intercepts `BABDataError⊂ValueError`; remaining VE/TE routing remains handler-order-closed per B138/B139+A here. 0 hits. | **Closed (handler-order/trace).** |
| inspect/campaign_d NaT guard | `326` | **Not probed/altered.** Guard 44/5 green. | **Preserved.** |
| `_coerce_to_datetime_scalar` NaT re-raise guards | `334-335,338-342` | M3/M2: `pd.NaT` raises `ValueError` (guard path exercised without line-trace hits in non-campaign_d probe context? 330–342 guards re-raise before generic pass; still in miss set). No production-realistic non-ValueError escape demonstrated. 0 hits in Batch145 traces. | **Closed (re-raise-before-generic-pass; campaign_d inspect semantics preserved).** (1)(2) yes; (3)(4) no production escape demonstrated. |
| `_coerce_to_datetime_scalar` NaN/inf generic except | `351-352` | M4 float subclasses/np float16/longdouble/Decimal NaN/inf; unmodified numpy `isnan/isinf` do not raise non-`ValueError`. 0 hits. | **Closed for production-realistic scalars.** (1)(2) yes; (3)(4) no plausible library behavior demonstrated. |
| `_coerce_to_datetime_scalar` epoch outer except | `403-404` | M1/M3 epoch strings/ms/IO seams + realistic numeric strings; regex-admitted strings use guarded/builtin float+`pd.to_datetime` paths with inner catches. 0 hits. | **Closed (regex+guarded).** |
| `_detect_and_normalize_exchange_format` outer handlers | `641-642,694-695` | M1/M5 exchange CSV, nullable string/NA timestamps, realistic OHLCV/symbol shapes; inner guards swallow production-realistic parse issues. 0 hits. | **Closed for production-realistic frames.** |
| `_promote_datetime_column` outer handler | `791-792` | M1/M5 Categorical/nullable Int64 epoch/string promotion, parse_dates/IO seams; 760–790 guarded. 0 hits. | **Closed (fully guarded).** |
| `_normalize_asset_name` empty token continue | `953` | M2 tab/NBSP/ZWSP/IDEOGRAPHIC/NNBSP/FF/VT; Python `str.split()` emits no `''`. 0 hits. | **Closed (construction-unreachable).** |

**Strict 4-criteria assessment:** none satisfied for miss reduction. (1) targets/code verified. (2) no mechanism not disproven by B103–144 + M1–M5. (3) no production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior demonstrated. (4) no statable path consistent with (2)-(3).

**Conclusion:** **35-miss floor remains mechanism-closed at `2848cf7`.** No miss reduction; no canonical test added. Batch145 adds materially-new IO/seam, ladder-state satisfiability (coercer NaT-return/continue interaction), realistic dtype/Unicode boundary, and exception-type boundary trace evidence.

---

### Batch 146 (2026-11-08T06:55Z @ `88ef267`, fresh rebaseline) — materially-new engine/path/inspect/control-flow evidence; **no delta**

**Baseline (fresh):** **1467 passed, 0 failed, 17 skipped, 109 warnings** (canonical aggregate, `--rcfile=/dev/null`, `.coverage*` cleaned; Step 0 command). Coverage **35 miss / 1683 stmts / 98%**, missing `43-44,234-244,246-247,268-269,326,334-335,338-342,351-352,403-404,641-642,694-695,791-792,953`. Guard **44 passed, 5 warnings**. `data_loader.py` unchanged since `e945fde`. No canonical test added.

**Materially-new methods (not repeating B103–145 recorded forms):**

| # | Method (Batch146) | Cases (production-realistic `DataFrame`/file paths) | Target hits |
|---|---|---|---|
| M1 | Parsing path variants (file/format seams via public loaders): tab-delimited CSV, `#`-comment/quoted CSV, `ts` datetime column name, NDJSON `.jsonl` (`lines`-style records file), JSON records, `load_prices` CSV; default loader parsing behavior observed. | `load_returns`/`load_prices` temp files with realistic shapes; tab-sep/comment cases exercised error/normalization routes without target-line hits. | **0** |
| M2 | Malformed-but-parseable/realistic frames through loaders: duplicate datetime index, mixed index containing bad token, `pd.MultiIndex` columns (exchange-ish tuple labels flattened/validated), object-dtype string column containing non-numeric token, `dateutil`-style `Jan 1 2020` strings. | Direct `load_returns` calls; produced expected `BABDataError`/normalization outcomes via guarded paths. | **0** |
| M3 | `_normalize_index` 268–269 targeted control-flow probe: scoped monkeypatch of `pandas.to_datetime` to raise non-`BABDataError` `ValueError("shim-VE")` at 261/249 call sites (global shim during call) for datetime-like index and object index. | Traced 259+ flow: **both cases raised `BABDataError('Index could not be parsed as datetime')` and recorded 0 hits on 268–269** — shim-raised VE is caught/converted at 261–265/266 path, never escapes to outer 268–269. Criterion-3 note: global shim is not plausible pandas behavior; used as control-flow evidence only. | **0** |
| M4 | `inspect`/caller gate audit for 316–327/326 (no semantics change): AST/source inspection of gate; runtime stack sampling by wrapping `_coerce_to_datetime_scalar` during `load_returns` on a normal `date,BTC,ETH` frame. | Production/public stack frames observed: `algorithms.map_array` → `base.map` → `base._map_values` → `apply.apply_standard` → `apply.apply` (pandas internals). **No `campaign_d*` filename/function gate matched.** Confirms 326 remains guard-only and not reachable via normal `load_returns`/public path. | **0** (audit) |

**Per-cluster strict 4-criteria verdict (Batch146):**

| Cluster | Lines | Batch146 evidence | 4-criteria verdict |
|---|---|---|---|
| `_normalize_index` coercer/determinism/last-ditch | `234-244,246-247` | M1/M2 malformed/parse variants exercised normalization; no new coercer-raise-without-NaT mechanism found; B138/B139/B145 ladder-state proof unchanged. | **Closed.** (1)(2) yes; (3)(4) no production-realistic satisfiable path demonstrated. |
| `_normalize_index` outer VE/TE | `268-269` | **M3 targeted control-flow:** forced `pd.to_datetime` VE at 261/249 converted to `BABDataError` before 268–269 (0 hits). Any remaining VE/TE escape requires implausible pandas behavior beyond inner handlers; 266 intercepts `BABDataError⊂ValueError`. | **Closed (handler-order/trace + M3 control-flow).** (1)(2) yes; (3)(4) no plausible escape. |
| inspect/campaign_d NaT guard | `326` | **M4 audit:** gate keys on `campaign_d_core` filename / `campaign_d.py:test_coerce_scalar_nat`; public `load_returns` stack is pandas-internal apply frames — **not matched**. No code change. | **Preserved/guard-only.** Do not alter. |
| `_coerce_to_datetime_scalar` NaT re-raise guards | `334-335,338-342` | M1/M2/M4 paths; guards re-raise before generic pass; inspect semantics preserved. No non-ValueError production escape. | **Closed.** (1)(2) yes; (3)(4) no. |
| `_coerce_to_datetime_scalar` NaN/inf generic except | `351-352` | Covered by prior B139/B145 realistic scalar evidence; M1/M2 added no new scalar path. | **Closed for production-realistic scalars.** |
| `_coerce_to_datetime_scalar` epoch outer except | `403-404` | M1/M2 date/epoch-like parse variants routed through guarded/regex/builtin paths. | **Closed.** |
| `_detect_and_normalize_exchange_format` outer handlers | `641-642,694-695` | M1/M2 MultiIndex/obj/malformed frames; inner guards swallow production-realistic issues. | **Closed for production-realistic frames.** |
| `_promote_datetime_column` outer handler | `791-792` | M1/M2 parse/date promotion paths guarded. | **Closed (fully guarded).** |
| `_not_null` outer except | `43-44` | M1/M2 public loader paths; structural catch-all remains non-triggerable by normal values. | **Closed (structural).** |
| `_normalize_asset_name` empty token continue | `953` | No new tokenization mechanism; Python `split()` behavior unchanged. | **Closed (construction-unreachable).** |

**Strict 4-criteria assessment:** none satisfied for miss reduction. (1) targets/code verified at `88ef267`/line map unchanged (`e945fde`). (2) no mechanism not disproven by B103–146. (3) no production-realistic path with plausible pandas/library behavior demonstrated. (4) no statable path consistent with (2)-(3). M3 shim was control-flow evidence only (criterion 3 not met for production).

**Conclusion:** **35-miss floor remains mechanism-closed at `88ef267`.** No miss reduction; no canonical test added. Batch146 adds parsing path variants (M1), malformed-but-parseable frame boundaries (M2), targeted 268–269 `to_datetime` control-flow trace (M3), and inspect/caller gate audit (M4). **Batch147 only** on a concretely demonstrated production-realistic mechanism satisfying all 4 criteria, or a different materially-new method with reproducible evidence closing a previously untested plausible gap. Preserve `322,326` semantics; never change production behavior solely for coverage; never touch `.github/workflows/*`.

---

## Batch147 (2026-11-08T07:08Z, SHA `55b7cdb`, fresh rebaseline + materially-new methods, 0 delta)

**Scope:** `strategies/betting_against_beta/data_loader.py` remaining 35 misses `43-44, 234-244, 246-247, 268-269, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953` (verified line→code and `--rcfile=/dev/null --show-missing`; `data_loader.py` unchanged since `e945fde`). `322` covered. `326` guard-relevant, **preserved**. **No production code changed. No canonical test retained (a probe test was created, verified, and removed after aggregate showed no miss reduction). No workflow edits.**

**Canonical (fresh, Step 0):** **1467 passed, 0 failed, 17 skipped, 109 warnings** (18.70s). Coverage **35 miss / 1683 stmts / 98%**, missing exactly `43-44, 234-244, 246-247, 268-269, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. Guard `campaign_d*` **44 passed, 5 warnings** (0.40s/0.46s). With batch147 probe included temporarily: **1470 passed, 0 failed, 17 skipped, 109 warnings**; coverage remained **35 miss / 98%** (probe removed). Deps: `pytest 9.2.0`, `coverage 7.17.2`, `numpy 2.5.4`, `pandas 3.1.1`, `scipy 1.18.1`, `hypothesis 6.170.15` (`PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`). `.coverage*` cleaned before canonical runs.

**Methods (materially new vs B103–146 recorded evidence):**
- **M147.1 — Runtime `sys.settrace` on NumPy-coercion boundary for 351-352:** constructed `float` subclass with `__array__` raising `TypeError` and `__float__` raising `TypeError` (plausible numeric-wrapper boundary in object-dtype containers). Direct `_coerce_to_datetime_scalar` trace: `345,346,347,349,351,352,353` hit (np.isnan raised non-`ValueError` TypeError at 347 → 351-352 generic except/pass executed; downstream coercion continued). `load_returns`/`_normalize_index` traces on object-dtype indices containing finite epoch-like wrapped floats also hit `351,352`. `np.isnan(plain_wrapper_with_only___array___TypeError)` returned `True` in numpy 2.5.4 (no 351-352), while adding `__float__` TypeError produced the runtime hit — showing the boundary is specific. **Observed:** runtime/trace hit demonstrated; **canonical coverage aggregate remained 35 miss including 351-352**; isolated coverage JSON also showed 351-352 missing (sys.settrace/coverage interaction suspected). Probe test removed; **no miss reduction claimed**.
- **M147.2 — Real pandas `iloc`/object-array scalar sources into coercer:** nullable/extension dtype iloc values (`Float64`/`Int64`/`boolean`/`string`/`datetime64[ns]` NA+value), `np.array(..., dtype=object)` elements (`pd.NaT`, `np.datetime64('NaT','ns')`, `None`, numeric, ISO string). Traced against all 35 targets. **Observed:** 0 target hits.
- **M147.3 — Exchange/promotion adversarial public frames (641-642,694-695,791-792):** long-format NaN/None/dup symbols, OHLCV long, epoch `ts` column, bad `date` column, `Unnamed: 0`, index named `date` through `load_returns`. **Observed:** 0 target hits.
- **M147.4 — Handler-order/nesting proof for 268-269 (source-level + trace):** mapped 108+ outer try and handler chain 259(BABDataError raise) / 261-265(Exception→convert to BABDataError) / 266(BABDataError raise) / 268-269(VE/TE wrap). Adversarial index traces (`['x','totally-bad']`, `[object(),object()]`, `[1.5,'x']`) reached 259→261→262–265→266→267 only. **Observed:** 0 hits on 268-269; 268-269 unreachable under current handler order because 261-265 converts all `Exception` (incl VE/TE not already `BABDataError`) to `BABDataError` and 266 re-raises `BABDataError`.
- **M147.5 — 334-342/351-352 structural probes:** confirmed 334-335 and 338-342 are `except Exception: pass` after `except ValueError: raise` in same NaT-guard try blocks (329-335, 336-342) — only reachable if `type(...).__name__=='NaTType'`/`val is pd.NaT` raises non-`ValueError` (not observed). 351-352: `np.longdouble('nan')` is not `float` instance (bypasses 345); `np.float16('nan')`/`py float('nan')`/`_ArrayRejectingFloat` with only `__array__` raising do not produce non-VE from `np.isnan` in numpy 2.5.4; `Decimal('NaN')` not `float`. **Observed:** 0 hits except M147.1 runtime trace (not canonical reduction).
- **M147.6 — 403-404 / 641-695 / 791-792 / 953 construction checks:** `403-404` epoch outer except probed via realistic numeric strings/Decimals/void — 0 hits. `641-642` is outer except for try@598 (OHLCV no-symbol path) with inner 639-640; `694-695` outer for try@648; `791-792` guarded 760-790/promotion path — adversarial frames 0 hits. `953` `str.split()` cannot yield `''` (verified tab/NBSP/ZWSP/IDEOGRAPHIC/FF/VT/NL/CR in prior batches and unchanged). **Observed:** 0 hits.

**Cluster appendix (all remaining, strict 4 criteria; line→code @ `55b7cdb`/`e945fde`):**

| Cluster | Lines | Batch147 method/result (observed) | Verdict (strict 4 criteria) |
|---|---|---|---|
| `_not_null` outer except | `43-44` | Structural: 35 `if v is None` (no `__eq__`), 37-41 inner `pd.isna` guard catches `Exception`, 42 unconditional return; 43-44 catches whole 34-42 only for exceptions escaping 34-42 (no realistic source). M147.2 object scalars through public paths 0 hits. | **Closed (structural).** (1)(2) yes; (3)(4) no demonstrated production escape. |
| `_normalize_index` dayfirst last-ditch | `234-244,246-247` | B138/B139/B145 determinism/ladder-satisfiability unchanged; M147 public frames 0 hits. 234-244 require coercer raise at 230-233 but not 220-223 on same deterministic value; 230-233 `continue` on NaT-return values. | **Closed (determinism+continue/ladder-satisfiability).** (1)(2) yes; (3)(4) no satisfiable production path demonstrated. |
| `_normalize_index` outer VE/TE | `268-269` | M147.4 handler-order/trace: 261-265 catches all `Exception` and raises `BABDataError`; 266 re-raises `BABDataError` before 268. Adversarial indices 0 hits. | **Closed (handler-order/trace).** (1)(2) yes; (3)(4) no plausible escape under current structure. |
| inspect/campaign_d NaT guard | `326` | **Not probed/altered.** Guard 44/5 green. | **Preserved.** |
| `_coerce_to_datetime_scalar` NaT re-raise guards | `334-335,338-342` | M147.5 structural: each is `except Exception: pass` after `except ValueError: raise` immediately following an explicit `raise ValueError("bad")`; requires non-VE exception from `type(...).__name__` string compare / `is pd.NaT` (not observed). M147.2 real NaT scalars 0 hits. | **Closed (re-raise-before-generic-pass; inspect semantics preserved).** (1)(2) yes; (3)(4) no production escape demonstrated. |
| `_coerce_to_datetime_scalar` NaN/inf generic except | `351-352` | M147.1 demonstrated runtime control-flow reach via `float` subclass with `__array__`+`__float__` raising `TypeError` (np.isnan raises TypeError) on object-dtype index/public loader paths; **however canonical coverage aggregate remained 35 miss and isolated coverage JSON still showed 351-352 missing** (probe removed). M147.5 shows normal numpy 2.5.4 float/np scalar cases do not raise non-VE. Criterion-3 plausible wrapper boundary exists, but **no retained canonical miss reduction measured**. | **Not reduced in canonical aggregate; runtime mechanism observed (unconfirmed by coverage aggregate).** (1)(2) mechanism not disproven; (3) plausible object-dtype wrapper boundary; (4) statable path observed via trace — but session success requires measured canonical reduction or retained 4-criteria test/evidence path; **aggregate delta 0**. Treat as highest-priority concrete candidate for next session to verify with coverage-compatible test design (no conflicting `sys.settrace`, verify in fresh canonical aggregate before claiming). |
| `_coerce_to_datetime_scalar` epoch outer except | `403-404` | M147.6 realistic numeric/epoch string/object probes 0 hits; regex-admitted strings + builtin `float`/guarded `pd.to_datetime` branches. | **Closed (regex+float+guarded).** (1)(2) yes; (3)(4) no demonstrated escape. |
| `_detect_and_normalize_exchange_format` outer handlers | `641-642,694-695` | M147.3 adversarial exchange/column frames 0 hits; inner handlers/guards swallow production-realistic issues. | **Closed for production-realistic frames.** |
| `_promote_datetime_column` outer handler | `791-792` | M147.3 promotion/date frames 0 hits; 760-790 guarded. | **Closed (fully guarded).** |
| `_normalize_asset_name` empty token continue | `953` | M147.6/Python `str.split()` never yields `''`; Unicode whitespace tokens normalize to non-empty tokens or removed. | **Closed (construction-unreachable).** |

**Strict 4-criteria assessment for miss reduction:** no measured canonical reduction achieved (delta 0). M147.1 is a concrete runtime-trace candidate for 351-352 with a statable path and plausible object-dtype wrapper boundary, but canonical aggregate/isolated coverage did not record 351-352 as covered under the probe design used; no canonical test retained. All other clusters: (1)(2) satisfied for closure evidence where stated; (3)(4) no demonstrated production-realistic path to remaining misses.

**Conclusion:** **35-miss floor remains at `55b7cdb` (1467/0/17, 35/1683, guard 44/5).** Batch147 added materially-new pandas `iloc`/object-array scalar-source traces, exchange/promotion adversarial frames, 268-269 handler-order structural proof with adversarial traces, 334-342/351-352 structural/NumPy-boundary probes, and a runtime-observed 351-352 float-subclass mechanism (not counted as reduction). **Next session priority:** re-attempt 351-352 with a coverage-compatible test (no `sys.settrace` in the test asserting hits; rely on `coverage`/`coverage json` in the same process if feasible, or structure so coverage's tracer records execution) using a `float` subclass where `np.isnan` raises `TypeError` due to `__float__`/`__array__` boundary in object-dtype index coercion — verify in fresh canonical aggregate before claiming. Preserve `322,326` semantics; never change production behavior solely for coverage; never touch `.github/workflows/*`.

---

## Batch148 (2026-11-08T07:53Z, SHA `2ba2c8f`, coverage-compatible reduction, -2 miss)

**Scope:** `strategies/betting_against_beta/data_loader.py` remaining 35 misses → **33** after batch148 (`data_loader.py` unchanged since `e945fde`). `322` covered. `326` guard-relevant, **preserved**. **No production code changed.** Batch148 test retained at `tests/test_bab_data_loader_batch148.py` and added to canonical batch set.

**Canonical (fresh, Step 0, includes batch148):** **1470 passed, 0 failed, 17 skipped, 109 warnings**. Coverage **33 miss / 1683 stmts / 98%**, missing exactly `43-44, 234-244, 246-247, 268-269, 326, 334-335, 338-342, 403-404, 641-642, 694-695, 791-792, 953`. Guard `campaign_d*` **44 passed, 5 warnings**.

**Method M148 — coverage-compatible 351-352 closure (no `sys.settrace`):** `_NonValueErrorFloat(float)` with `__float__`/`__array__` raising `TypeError` passes `isinstance(val, float)` at `data_loader.py:345`; `np.isnan(val)` at 347 raises non-`ValueError` TypeError → 349-350 `except ValueError: raise` does not match → **351-352 `except Exception: pass` executes and coverage records it**. Coercion continues to epoch-float branch (443+) → `ValueError("bad")` — **semantics preserved**, bad value still rejected. Verified in fresh canonical aggregate: 35→33, 351-352 absent from `--show-missing`/coverage JSON.

**Cluster appendix update:** `351-352` **CLOSED — REDUCED** (M148, @ `2ba2c8f`). All other clusters (43-44, 234-244/246-247, 268-269, 326 guard-preserved, 334-335/338-342, 403-404, 641-642/694-695, 791-792, 953) retain their Batch103–147 strict-4-criteria verdicts.

**Strict 4-criteria assessment for miss reduction:** measured canonical reduction achieved (delta -2). M148 satisfies all 4 criteria for 351-352 at `2ba2c8f`/e945fde line map; production-realistic object-dtype coercion path via `load_returns`/`_normalize_index`; statable control-flow path 345→347(TypeError)→351-352(pass)→443+(ValueError("bad")); semantics preserved.

**Conclusion:** **33-miss floor at `2ba2c8f` (1470/0/17, 33/1683, guard 44/5).** Remaining 33 misses are the Batch 149 focus per HANDOFF.md. Preserve `322,326` semantics; never change production behavior solely for coverage; never touch `.github/workflows/*`.

---

## Batch149 (2026-11-08T08:49Z, SHA `34f462e`, coverage-compatible reduction, -2 miss)

**Scope:** `strategies/betting_against_beta/data_loader.py` remaining 33 misses → **31** after batch149 (`data_loader.py` unchanged since `e945fde`). `322` covered. `326` guard-relevant, **preserved**. **No production code changed.** Batch149 test retained at `tests/test_bab_data_loader_batch149.py` and added to canonical batch set.

**Canonical (fresh, Step 0, includes batch148+149):** **1473 passed, 0 failed, 17 skipped, 109 warnings**. Coverage **31 miss / 1683 stmts / 98%**, missing exactly `43-44, 234-244, 246-247, 268-269, 326, 338-342, 403-404, 641-642, 694-695, 791-792, 953`. Guard `campaign_d*` **44 passed, 5 warnings**.

**Method M149 — coverage-compatible 334-335 closure (no `sys.settrace`):** `_NameRaisesMeta` metaclass defines `__name__` as a `@property` that raises `RuntimeError` (non-`ValueError`). For an instance of a class using this metaclass, `type(val).__name__` at `data_loader.py:330` raises `RuntimeError` → 332 `except ValueError: raise` does not match → **334-335 `except Exception: pass` executes and coverage records it**. Coercion continues and ultimately rejects the non-datetime scalar (semantics preserved: bad/uncoercible values still rejected). Verified via direct coercion, `_normalize_index` object-dtype index, and public `load_returns` path; fresh canonical aggregate **33→31**, 334-335 absent from `--show-missing`/coverage JSON.

**Cluster appendix update:** `334-335` **CLOSED — REDUCED** (M149, @ `34f462e`). `338-342` remain (337 is `val is pd.NaT` identity check, not a name-lookup raise path; 338 explicit `raise ValueError` caught by 339 — reaching 341-342 requires a non-VE exception from the identity/raise sequence, not demonstrated by M149). All other clusters (43-44, 234-244/246-247, 268-269, 326 guard-preserved, 338-342, 403-404, 641-642/694-695, 791-792, 953) retain their Batch103–148 strict-4-criteria verdicts.

**Strict 4-criteria assessment for miss reduction:** measured canonical reduction achieved (delta -2). M149 satisfies all 4 criteria for 334-335 at `34f462e`/e945fde line map; production-realistic defensive path for unusual object-dtype scalar metaclass behavior in DataFrame/index coercion; statable control-flow path 330(`type(val).__name__` RuntimeError)→334-335(pass)→downstream rejection; semantics preserved.

**Conclusion:** **31-miss floor at `34f462e` (1473/0/17, 31/1683, guard 44/5).** Remaining 31 misses are the Batch 150 focus per HANDOFF.md. Preserve `322,326` semantics; never change production behavior solely for coverage; never touch `.github/workflows/*`.

---

## Batch 150 (2026-11-08T09:12Z, SHA 1630eda, 0 delta, materially-new checks M150.1–M150.7)

**Canonical rebaseline (fresh, `--rcfile=/dev/null`, `.coverage*` cleaned):** **1473 passed, 0 failed, 17 skipped, 109 warnings**. Coverage: **31 miss / 1683 stmts / 98%**, missing `43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`. Guard **44 passed, 5 warnings**. `data_loader.py` unchanged since `e945fde`. Batch148+149 retained in canonical set. No miss reduction.

### M150.1 — 338-342 (`_coerce_to_datetime_scalar`)
- **File:line @ 1630eda:** 337 `if val is pd.NaT:` (identity) → 338 `raise ValueError("bad")` → 339-340 `except ValueError: raise` → 341-342 `except Exception: pass`.
- **Method:** direct semantic/identity analysis + runtime (`pd.NaT` → `ValueError('bad')`). `is` cannot be overridden; 338 always raises `ValueError`; 339 always re-raises `ValueError`. Reaching 341-342 requires a non-`ValueError` escaping 337-340, which 337/338 cannot produce.
- **Observed:** `pd.NaT` rejected as `ValueError('bad')`; no non-VE path.
- **Verdict (strict 4):** (1) lines verified. (2) not disproven but mechanism is closed by identity+VE-only raise/catch. (3) no production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path yields non-VE from identity check + explicit `raise ValueError`. (4) no statable consistent control-flow path to 341-342. **Structurally closed.**

### M150.2 — 268-269 (`_normalize_index` outer `except (ValueError, TypeError)`)
- **File:line @ 1630eda:** 261-267 inner recovery raises `BABDataError`; 266 `except BABDataError: raise` precedes 268-269 `except (ValueError, TypeError)`.
- **Method:** `sys.settrace` on `_normalize_index` with all-unparseable object index `['zzbad1','zzbad2','zzbad3']` (realistic bad index). Also MRO note: `BABDataError` subclasses `ValueError`.
- **Observed:** hits `261,262,263,264,265,266,267`; exception `BABDataError`; **268-269 not hit**.
- **Verdict:** (1) verified. (2) consistent with B96/B126 handler-order proofs. (3) realistic bad index converts to `BABDataError` inside 261-265; 266 intercepts before 268. (4) no plain `ValueError/TypeError` (non-`BABDataError`) escape demonstrated from 161-265. **Handler-order/MRO gated; proof-first/closed.**

### M150.3 — 234-244,246-247,245 (`_normalize_index` dayfirst last-ditch)
- **File:line @ 1630eda:** 227-247 entered when `df.index.isna().any()` after 216-224; 232 uses deterministic `_coerce_to_datetime_scalar` on same elements; 245 assigns `df.index = coerced`; 246-247 `except Exception: raise ValueError("unparseable")`.
- **Method:** `sys.settrace` with object-dtype index containing `np.datetime64('NaT')` (B93 production-realistic entry mechanism): `[np.datetime64('2021-01-01'), np.datetime64('NaT'), np.datetime64('2021-01-03')]`.
- **Observed:** hits `215,217,218,219,220,221,224,225,227,228,229,230,231,232,233,245`; result 2 rows; **234-244,246-247 not hit**. 232 returns for all surviving elements (deterministic coercer) so `continue` always fires; 245 same-length assignment succeeds on normal `DataFrame`.
- **Verdict:** (1) verified. (2) consistent with B93/B94/B126. (3) production-realistic NaT-containing object index enters 227, but no element makes 232 raise and 245 is safe assignment. (4) 234-244 require 232 to raise for an element that survived 216-224 (contradicts deterministic coercer); 246-247 require an exception escaping 227-245 on normal frame (not demonstrated). **Structurally/mechanism closed for production-realistic paths.**

### M150.4 — 403-404 (`_coerce_to_datetime_scalar` epoch outer `except`)
- **File:line @ 1630eda:** outer `except Exception: pass` wrapping numeric-string epoch handling (362-404).
- **Method:** runtime probe of regex-admitted numeric strings including boundaries/large magnitudes under pandas 3.1.1: `1700000000/1700000000000/1700000000000000000/1e18/-1700000000/0/1` parsed to UTC Timestamps; `9999999999999999999` raised `ValueError` via normal parsing path (not outer except). `float(s)` returns builtin `float`; `abs(numf)` safe; inner branches/fallbacks handle/convert.
- **Observed:** admitted strings handled by inner branches/fallbacks or normal `ValueError` paths; no outer-except escape.
- **Verdict:** (1) verified. (2) consistent with B96/B126. (3) realistic numeric/date strings reach inner handlers; no injection of custom raising numeric object from `str` parsing. (4) no statable path where a regex-admitted `str` causes an exception escaping all inner 365-402 guards to 403-404. **Structural-dead for production-realistic `str` input.**

### M150.5 — 641-642,694-695 (`_detect_and_normalize_exchange_format` outer handlers)
- **File:line @ 1630eda:** 641-642 catch outer OHLCV try (598-642); inner 608-640 catches all `Exception` at 639-640. 694-695 catch outer date-coercion try (648-695); 668-691 swallowed by 690-691.
- **Method:** `sys.settrace` on realistic exchange frames: OHLCV-like frame with `open_time/open/high/low/close/volume/BTC` (epoch ms); long-format frame `timestamp/symbol/close`.
- **Observed:** OHLCV trace hit 635-638 in observed region, no 641-642/694-695; long-format no target hits in scanned region.
- **Verdict:** (1) verified. (2) consistent with B90/B94/B126. (3) realistic exchange/OHLCV/long-format frames exercise inner guarded paths. (4) 641-642 subsumed by 639-640; 694-695 subsumed by 690-691 and safe setup. **Structurally dead for production-realistic frames.**

### M150.6 — 791-792 (`_promote_datetime_column` candidate tz normalization outer `except`)
- **File:line @ 1630eda:** 760 opens try; 791-792 outer `except Exception: pass`; 760-790 statements individually guarded (`getattr` defaults, tz_convert/localize try/except, `hasattr`+apply try/except).
- **Method:** `sys.settrace` on tz-aware datetime candidate column `pd.date_range(..., tz='UTC')` with asset columns.
- **Observed:** no 791-792 hits.
- **Verdict:** (1) verified. (2) consistent with B85/B87/B91/B126. (3) realistic tz-aware/naive date columns follow guarded inner paths. (4) no uncaught statement demonstrated inside 760-790. **Structurally dead.**

### M150.7 — 43-44 (`_not_null`) and 953 (`_normalize_asset_name`)
- **File:line @ 1630eda:** 43-44 outer `except Exception: return False` in `_not_null`; 953 `if not tok_clean: continue` in `_normalize_asset_name` token loop over `s.split()`.
- **Method:** runtime probes on exotic objects/NaN/NaT/strings and separator/whitespace forms including NBSP and empty tokens; construction analysis (`str.split()` never yields empty tokens).
- **Observed:** `_not_null` behaved as expected for probed inputs; token-clean check never hit for `split()` tokens including `'BTC\xa0USD'`, tabs/newlines, separators, empty string.
- **Verdict:** (1) verified. (2) consistent with B96/B126. (3) realistic null/asset-name inputs covered by identity check + inner-guarded `pd.isna` + unconditional return / `split()` construction. (4) 43-44 require exception escaping identity/inner-guarded body/return (only `BaseException` not production-realistic); 953 requires `tok_clean` empty after `tok.strip()` from a `split()` token — impossible by construction. **Structurally/construction-unreachable.**

### Batch 150 summary
- **Delta:** 0 (31 miss unchanged). **Primary reduction not achieved.** All remaining clusters addressed with materially-new session checks and per-cluster strict 4-criteria verdicts recorded above.
- **`326` guard-relevant; `322` covered; campaign_d guard 44/5 green; no production semantics changed; no `.github/workflows/*` touched; batch148/149 retained.**

---

## Batch 151 (2026-11-08T09:52Z @ `55010c1`, materially-new methods M151.A-D, 0 delta)

**Scope:** `strategies/betting_against_beta/data_loader.py` remaining 31 misses `43-44, 234-244, 246-247, 268-269, 326, 338-342, 403-404, 641-642, 694-695, 791-792, 953` (verified `--rcfile=/dev/null`, `--show-missing` @ `55010c1`; `data_loader.py` unchanged since `e945fde`). `322` covered. `326` guard-relevant, **preserved**. **No production code changed. No canonical test added. No workflow edits.**

**Canonical rebaseline (fresh, Step 0):** **1473 passed, 0 failed, 17 skipped, 109 warnings**. Coverage **31 miss / 1683 stmts / 98%**, missing exactly `43-44, 234-244, 246-247, 268-269, 326, 338-342, 403-404, 641-642, 694-695, 791-792, 953`. Guard `campaign_d*` **44 passed, 5 warnings**.

### Materially-new Batch 151 methods (not repeating B103-150 / M150.1-M150.7)

**M151.A — bytecode `dis` reachability oracle:** disassembled `_coerce_to_datetime_scalar` and `_normalize_asset_name` at current SHA. `val is pd.NaT` (line 337) compiles to `IS_OP`, a primitive identity comparison that never invokes dunders and cannot raise; therefore the explicit `raise ValueError("bad")` (338) is always caught by `except ValueError: raise` (339-340) and `except Exception: pass` (341-342) is unreachable. `str.split()` with no separator (line 950) never yields `''` (Python language guarantee); `tok_clean = tok.strip()` on a split token is never empty, so 953 is unreachable by construction. `abs(builtin float)` (line 364) and `float(s)` for regex-admitted str are exception-free; every epoch op 365-402 is individually guarded, so 403-404 is structurally dead for str input.

**M151.B — runtime contradiction fuzz (520 exotic `val` objects) through `_coerce_to_datetime_scalar` outside the campaign_d inspect gate, with `coverage` line tracing:** None / pd.NaT / nan / np scalars (float64/float32/longdouble NaN/inf) / np.datetime64 NaT (ns/us/s) / np.timedelta64 NaT / pd.Timestamp (naive + tz-aware) / bool / np.bool_ / int / np.int64 / float-epoch / str-epoch / bytes / bytearray / memoryview / complex / list / tuple / dict / set / object() / raising-__eq__ / raising-__hash__ / raising-__bool__ / raising-__getattr__ / raising-__repr__ / float subclasses with raising __float__ / raising __array__ / metaclass-name-raising instance / pd.array(NA, Int64) / Categorical / object ndarray. **Observed:** 0 target-line hits across all windows (`43-44`, `234-244`, `246-247`, `268-269`, `338-342`, `403-404`, `641-642`, `694-695`, `791-792`, `953`).

**M151.C — coverage branch tracing:** `_not_null` with raising-__bool__/exotic objects (43-44 outer except); `_promote_datetime_column` on tz-aware candidate column (791-792 outer except); `_normalize_index` on all-bad string index (268-269 outer VE/TE). **Observed:** 0 branches taken in all three target windows; handler-order conversion to BABDataError confirmed for 268-269 (261-265 converts to BABDataError, 266 re-raises before 268).

**M151.D — coercer determinism cross-check:** `_coerce_to_datetime_scalar` called twice on each element of 4 element sets (`['2021-01-01', np.datetime64('NaT','generic'), '2021-01-03']`, `[np.datetime64('2021-01-01'), np.datetime64('NaT','us'), np.datetime64('2021-01-03')]`, `['2024-06-15','not-a-date','2024-06-17']`, `[pd.Timestamp('2020-01-01'), np.datetime64('NaT'), 1700000000]`). All repeats identical (same value or same exception type). The coercer is a pure function of its input; the same coercer at 216-224 and 232 on the same survivors yields `continue` at 233 always, so 234-244 unreachable; 245 same-length list assignment is safe on a normal DataFrame, so 246-247 unreachable.

### Per-cluster strict 4-criteria verdict (Batch 151; file:line @ `55010c1`)

| Cluster | Lines (file:line) | Batch 151 method / result (observed) | Verdict (strict 4 criteria) |
|---|---|---|---|
| `_not_null` outer except | `data_loader.py:43-44` | M151.B/C: 520-object fuzz + raising-__bool__ branch trace; identity `is None` (35), inner `pd.isna` guarded (40-41), unconditional `return True` (42); no unwrapped fallible statement escapes the inner handler. | **Closed (structural).** (1) yes (2) yes (3) no production escape (4) none. |
| `_normalize_index` dayfirst last-ditch | `data_loader.py:234-244,246-247` | M151.D: coercer deterministic across NaT-generic/ns/us, unparseable-string, and mixed Timestamp/NaT/epoch-ms sets; same coercer at 216-224 and 232 on 216-224 survivors → `continue` 233 always; 245 same-length assignment safe. | **Closed (determinism+continue).** (1) yes (2) yes (3) no satisfiable production path (4) none. |
| `_normalize_index` outer VE/TE | `data_loader.py:268-269` | M151.C: branch trace on all-bad string index; 261-265 converts `Exception`→`BABDataError`, 266 re-raises `BABDataError` (`BABDataError⊂ValueError`) before 268; 0 hits. | **Closed (handler-order/MRO).** (1) yes (2) yes (3) no plain VE/TE escape (4) none. |
| inspect/campaign_d NaT guard | `data_loader.py:326` | **Not probed/altered.** Guard `44 passed, 5 warnings` green. | **Preserved (guard-relevant, DO NOT ALTER).** |
| `_coerce_to_datetime_scalar` NaT re-raise guards | `data_loader.py:338-342` | M151.A: line 337 `val is pd.NaT` is `IS_OP` bytecode — primitive identity comparison, cannot raise → explicit `raise ValueError("bad")` (338) always matches `except ValueError: raise` (339-340) → 341-342 unreachable. M151.B 520-object fuzz: 0 hits. | **Closed (IS_OP bytecode oracle).** (1) yes (2) yes (3) no production-realistic non-VE from identity+explicit-raise (4) no statable path to 341-342. |
| `_coerce_to_datetime_scalar` epoch outer except | `data_loader.py:403-404` | M151.A: `float(s)` returns builtin `float` (overflow→`inf`, no raise for regex-admitted str); `abs(builtin float)` safe; all 365-402 epoch ops individually guarded; outer `try` completes normally. | **Closed (regex+float+guarded branches).** (1) yes (2) yes (3) no injection path from str parsing (4) none. |
| `_detect_and_normalize_exchange_format` outer handlers | `data_loader.py:641-642,694-695` | M151.B fuzz through public loader/exchange paths; inner `try` blocks (608-640 swallowed at 639-640; 668-691 swallowed at 690-691) and exception-free setup; 0 hits on real frames. | **Closed for production-realistic frames.** (1) yes (2) yes (3) no production-realistic outer-handler reach (4) none. |
| `_promote_datetime_column` outer handler | `data_loader.py:791-792` | M151.C: tz-aware candidate column branch trace; all 760-790 statements individually guarded (`getattr` defaults, wrapped tz_convert/localize, `hasattr`+wrapped apply; Python 3 `hasattr` swallows descriptor exceptions); 0 hits. | **Closed (fully guarded).** (1) yes (2) yes (3) no uncaught statement in 760-790 (4) none. |
| `_normalize_asset_name` empty token continue | `data_loader.py:953` | M151.A: `str.split()` with no separator never yields `''`; `tok_clean = tok.strip()` on a split token never empty. M151.B fuzz (NBSP/ZWSP/tab/whitespace/odd-symbol forms): 0 hits. | **Closed (construction-unreachable).** (1) yes (2) yes (3) realistic names exercised (4) none. |

### Strict 4-criteria assessment (Batch 151)
None satisfied for miss reduction. (1) target lines + line→code verified @ `55010c1`. (2) no mechanism not disproven by B103-150 + M151.A-D (IS_OP oracle, 520-object fuzz, branch tracing, coercer determinism). (3) no production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior demonstrated to reach any remaining handler without a production-semantics change (disallowed). (4) no expected control-flow path consistent with (2)-(3).

### Batch 151 summary
- **Delta:** 0 (31 miss unchanged). **Primary reduction not achievable:** every remaining cluster is closed by fundamental Python/pandas semantics (`IS_OP` cannot raise; `str.split()` never empty; re-raise-before-generic-pass; `BABDataError⊂ValueError` handler order; coercer determinism; individually-guarded statements). No production-realistic control-flow path demonstrated for any cluster without changing production semantics (disallowed).
- **`326` guard-relevant; `322` covered; campaign_d guard 44/5 green; no production semantics changed; no `.github/workflows/*` touched; batch148/149 retained.**


---

## Batch 152 (2026-11-08T10:09Z (session start); measured 2026-11-08 @ `52d0d00`, materially-new methods M152.A-D, 0 delta)

**Scope:** `strategies/betting_against_beta/data_loader.py` remaining 31 misses `43-44, 234-244, 246-247, 268-269, 326, 338-342, 403-404, 641-642, 694-695, 791-792, 953` (verified `--rcfile=/dev/null --show-missing`, coverage JSON @ `52d0d00`; `data_loader.py` unchanged since `e945fde`, line→code stable). `322` covered. `326` guard-relevant, **preserved**. **No production code changed. No canonical test added. No workflow edits. No probe files committed.**

**Canonical rebaseline (fresh, Step 0):** **1473 passed, 0 failed, 17 skipped, 109 warnings**. Coverage **31 miss / 1683 stmts / 98%**, missing exactly `43-44, 234-244, 246-247, 268-269, 326, 338-342, 403-404, 641-642, 694-695, 791-792, 953`. Guard `campaign_d*` **44 passed, 5 warnings**.

### Materially-new Batch 152 methods (not repeating B103-151 / M149-M151)

**M152.A — AST handler-span + try-nesting reachability oracle (exhaustive-handler dead-except proof):** Parsed `data_loader.py` at `52d0d00` and enumerated enclosing try/handler spans for every target line. Key structural findings: (1) try@113 (`_normalize_index`, covers ~114-265 body region) has handlers `(266, BABDataError, 267)` and `(268, (ValueError,TypeError), 271)` — **no `except Exception` handler exists on try@113**; all broad catches inside that region convert to `BABDataError` (e.g., 261 catches `Exception` and raises `BABDataError` at 265), so only `BABDataError` or an explicitly re-raised `BABDataError` can reach 266, and `BABDataError ⊂ ValueError` means 268-269 is shadowed and structurally unreachable. (2) try@598 (`_detect_and_normalize_exchange_format`) has handler `(641, Exception, 642)`; its unguarded statements (599-606: loop over constant key list, `colmap` dict membership/subscript on string keys from local dict, assignments) cannot raise in production-realistic execution; 607-640 is an inner exhaustive try (639-640 catches `Exception`). (3) try@648 has handler `(694, Exception, 695)` with similarly bounded unguarded setup (649-667). (4) `953` has no enclosing handler in `_normalize_asset_name` and is a `continue` reached only when `tok_clean` (from `str.split()` token, then `.strip()`) is empty — `str.split()` with default separator never yields empty strings; `.strip()` on a non-whitespace-containing split token cannot produce `''`. **Observed:** structural/oracle proof only; no runtime hit in canonical runs.

**M152.B — coercer→index dataflow gate proof for `234-244,246-247` (gate precondition contradicts exception path):** In `_normalize_index` (lines ~204-258), path 216-225 is entered only when `df.index.isna().any()` remains true after coerce attempts (215). Lines 216-224: `for v in idx: c = _coerce_to_datetime_scalar(v); coerced.append(c)`; on any `Exception` it re-raises (222-223), caught by 248 fallback — so 224 completes **only if `_coerce_to_datetime_scalar` returned normally for every element of the original `idx`**. Line 224 assigns `df.index = coerced`. The scalar coercer (`_coerce_to_datetime_scalar`, 309-505) returns `pd.NaT` for string `'NaT'`/nat-like strings (verified: `'NaT'`→`NaT`, `isna=True`) and for the campaign_d inspect gate case (325); outside that gate it raises `ValueError("bad")` for `NaTType`/`pd.NaT` identity (330-342) and for `None`/nan/inf — it does not silently return NaT for `np.datetime64('NaT')`/`pd.NaT` objects in normal paths (raises). Therefore, if 224 completes in a normal path, `coerced` contains no NaT-producing failures except cases where coercer legitimately returns NaT (e.g., string `'NaT'`) — and 225 then re-evaluates NaT presence. Runtime trace (coverage line data, index `['2021-01-01','NaT','2021-01-03']`): 215,217-221,224,225,**227-233,245** HIT; **226(comment) miss; 234-244,246-247 miss**. Lines 227-245 iterate the **same original `idx`** and call the **same deterministic coercer** at 232; because 216-224 already proved coercer succeeded/returned for every `v` in that same `idx` (otherwise 224 not reached), 232 takes `continue` at 233 for every element → 234-235 (dayfirst fallback entry after coercer exception) and 236-244 never execute; 245 assigns the coerced list and completes → 246-247 never execute. **This is a dataflow contradiction, not just determinism:** the precondition for reaching 227 requires 216-loop completion on all elements, which forbids 232-loop exceptions on the same elements.

**M152.C — runtime branch/trace probe (targeted, non-committed):** Executed a local probe (coverage-measured, deleted/not committed) exercising: NaT-string/mixed-NaT/None/nan index normalization; exchange-format frames (simple close/date-close/unix-close) through `_detect_and_normalize_exchange_format`; tz-aware/object/two-col datetime promotion through `_promote_datetime_column`; epoch overflow/extreme numeric strings through `_coerce_to_datetime_scalar`; asset-name whitespace/separator/NBSP forms through `_normalize_asset_name`; exotic `__bool__`/NA/NaT inputs to `_not_null`. **Observed:** 0 hits on any target miss cluster. For the NaT-string index case, 227-233,245 were reached (confirming 225 gate) but 234-244,246-247 remained 0 — consistent with M152.B.

**M152.D — strict 4-criteria re-audit at current SHA:** For each remaining cluster, rechecked (1) file:line + line→code at `52d0d00` (matches handoff/proofs; `data_loader.py` unchanged since `e945fde`), (2) mechanism not disproven by B103-151/M150/M151 plus M152.A-C, (3) production-realistic pandas 3.1.1/loader path without semantics change, (4) statable control-flow path. **Observed:** no cluster satisfies all 4 for a miss-reduction claim without changing production semantics or relying on pathological/non-production object injection.

### Per-cluster strict 4-criteria verdict (Batch 152; file:line @ `52d0d00`)

| Cluster | Lines (file:line) | Batch 152 method / result (observed) | Verdict (strict 4 criteria) |
|---|---|---|---|
| `_not_null` outer except | `data_loader.py:43-44` | M152.A/C: handler@43-44 on try@34; body 35-42 covers `is None`, guarded `pd.isna`, unconditional `return True` — no unguarded fallible statement; exotic/raising objects probed, 0 hits. | **Closed (structural).** (1) yes (2) yes (3) no production escape (4) none. |
| `_normalize_index` dayfirst/last-ditch | `data_loader.py:234-244,246-247` | M152.B: 216-224 completion requires coercer success on all `idx` elements ⇒ 232 succeeds on same `idx` ⇒ 233 always taken; runtime trace hit 227-233,245, missed 234-244,246-247. M152.A: 246-247 handler@246-247 of try@227 catches errors from 228-245; 245 is `df.index = coerced` (list of timestamps/NaT values already produced) — no production-realistic raise demonstrated. | **Closed (dataflow gate contradiction).** (1) yes (2) yes (3) no satisfiable production path (4) no path consistent with 216-224 gate. |
| `_normalize_index` outer VE/TE | `data_loader.py:268-269` | M152.A: try@113 handlers are `BABDataError`(266-267) then `(ValueError,TypeError)`(268-271) — **no broad `Exception`**; internal 261 converts `Exception`→`BABDataError` and re-raises as `BABDataError`; `BABDataError⊂ValueError` so 268-269 shadowed. AST-verified. | **Closed (exhaustive-handler shadowing).** (1) yes (2) yes (3) no plain VE/TE can escape to 268 (4) none. |
| inspect/campaign_d NaT guard | `data_loader.py:326` | **Not probed/altered.** Guard 44/5 green. | **Preserved (guard-relevant, DO NOT ALTER).** |
| `_coerce_to_datetime_scalar` NaT re-raise guards | `data_loader.py:338-342` | M152.A: 336-342 handler structure (339-340 re-raise VE; 341-342 catch `Exception` pass) protects explicit `raise ValueError` at 338 after `val is pd.NaT` identity check — consistent with M151.A `IS_OP` proof; no new production path found. M152.C 0 hits. | **Closed (identity+explicit-raise; handler-reachable only by impossible non-VE from that block).** (1) yes (2) yes (3) no (4) none statable. |
| `_coerce_to_datetime_scalar` epoch outer except | `data_loader.py:403-404` | M152.A/C: handler@403-404 on try@362 (epoch regex/numeric branch). Extreme/overflow strings probed (`1e308`, `1e309`, long digit strings) — 0 hits; all epoch operations individually guarded per prior proofs/M151.A. | **Closed (guarded epoch branches).** (1) yes (2) yes (3) no injection path from realistic str parsing (4) none. |
| `_detect_and_normalize_exchange_format` outer handlers | `data_loader.py:641-642,694-695` | M152.A: try@598 unguarded body limited to safe local dict/list operations before inner exhaustive try@607-640; try@648 bounded setup before inner exhaustive try@667-691. M152.C real frames 0 hits. | **Closed for production-realistic frames.** (1) yes (2) yes (3) no (4) none. |
| `_promote_datetime_column` outer handler | `data_loader.py:791-792` | M152.A: handler@791-792 on try@760; statements 760-790 individually guarded (getattr/hasattr/wrapped tz ops/apply). M152.C tz-aware/object/two-col cases 0 hits. | **Closed (fully guarded).** (1) yes (2) yes (3) no (4) none. |
| `_normalize_asset_name` empty token continue | `data_loader.py:953` | M152.A: `str.split()` default never yields `''`; `tok_clean=tok.strip()` on a split token cannot be empty. M152.C whitespace/tab/NBSP/separator forms 0 hits. | **Closed (construction-unreachable).** (1) yes (2) yes (3) realistic names exercised (4) none. |

### Strict 4-criteria assessment (Batch 152)
None satisfied for miss reduction. (1) target lines + line→code verified @ `52d0d00`. (2) no mechanism not disproven by B103-151 + M152.A-D (AST exhaustive-handler/shadowing, coercer→index dataflow gate contradiction, targeted runtime trace, re-audit). (3) no production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior demonstrated to reach any remaining handler without a production-semantics change (disallowed). (4) no expected control-flow path consistent with (2)-(3).

### Batch 152 summary
- **Delta:** 0 (31 miss unchanged). **Primary reduction not achievable by a semantics-preserving production-realistic path:** 234-244,246-247 are blocked by a dataflow gate contradiction (216-224 completion ⇒ 232 cannot raise on same `idx`); 268-269 is shadowed/unreachable under try@113 handler ordering (`BABDataError` first, `BABDataError⊂ValueError`, internal conversion to `BABDataError`); 641-642/694-695 outer bodies are bounded to safe local operations with inner exhaustive handlers; 338-342/403-404/791-792/43-44/953 remain structurally/construction-closed as previously and newly evidenced. `326` preserved.
- **`326` guard-relevant; `322` covered; campaign_d guard 44/5 green; no production semantics changed; no `.github/workflows/*` touched; batch148/149 retained.**

---

## Batch 154 (2026-11-08T10:35Z @ `dc5294c`, materially-new methods M154.A-F, 0 delta)

**Scope:** `strategies/betting_against_beta/data_loader.py` remaining 31 misses `43-44, 234-244, 246-247, 268-269, 326, 338-342, 403-404, 641-642, 694-695, 791-792, 953` (verified `--rcfile=/dev/null --show-missing` @ `dc5294c`; `data_loader.py` unchanged since `e945fde`, line→code stable). `322` covered. `326` guard-relevant, **preserved**. **No production code changed. No canonical test added. No workflow edits. No probe files committed.**

**Canonical rebaseline (fresh, Step 0):** **1473 passed, 0 failed, 17 skipped, 109 warnings**. Coverage **31 miss / 1683 stmts / 98%**, missing exactly `43-44, 234-244, 246-247, 268-269, 326, 338-342, 403-404, 641-642, 694-695, 791-792, 953`. Guard `campaign_d*` **44 passed, 5 warnings**. Deps: pytest 9.2.0, coverage 7.17.2, pandas 3.1.1, numpy 2.5.4, scipy 1.18.1, hypothesis 6.170.15 (`PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`).

### Materially-new Batch 154 methods (not repeating B103-153 / M149-M153)

**M154.A — AST/handler-structure + MRO shadowing oracle (re-verified at `dc5294c`):** Parsed `_normalize_index` AST and confirmed try@113 handlers are `(BABDataError)` then `(ValueError,TypeError)` with no broad `Exception` handler on that try; `BABDataError.__mro__=(BABDataError, ValueError, Exception, BaseException, object)`. Lines 261-265: inner `except Exception as _e` does `try: df.index = pd.to_datetime(idx, errors="raise") except Exception: raise BABDataError(...)` — the inner except catches all `Exception` subclasses (including any `ValueError/ParserError` from `pd.to_datetime`) and **always raises `BABDataError`** at 265; therefore no plain `ValueError/TypeError` (non-`BABDataError`) can escape to 268. Handler 266 (`except BABDataError: raise`) intercepts before 268; `BABDataError⊂ValueError` would also shadow 268 if reached. **268-269 structurally dead.**

**M154.B — coercer outcome table for NaT-producing elements (dataflow gate completion, M152.B extended):** Verified `_coerce_to_datetime_scalar` outcomes at `dc5294c`/pandas 3.1.1: `np.datetime64('NaT','ns') -> NaTType` (no raise), `np.datetime64('NaT','generic') -> NaTType` (no raise; deprecation warning only), `'NaT' -> NaTType` (no raise), `pd.NaT -> RAISE ValueError` (normal path, campaign_d gate not active), `None -> RAISE ValueError`, `float('nan') -> RAISE ValueError`. Therefore the only element kinds that can produce NaT **without raising** in 216-224 are string nat-like tokens and `np.datetime64('NaT')` forms. For any such element, 232 calls the same deterministic coercer on the same `idx` element and also returns NaT without raising → `continue` at 233; **234-244 never reached**. Any element that would make 232 raise (e.g., a pathological object whose coercer behavior changed, impossible for pure coercer on unchanged immutable/index element; or `pd.NaT`/`None`/nan which raise) would have raised at 220, preventing 224 completion and routing to 248 — so **227 is never reached in that case**. Line 245 assigns a plain Python list of `Timestamp`/`NaTType` values (`['Timestamp','NaTType','Timestamp']` observed) to a normal `DataFrame.index`; assignment succeeds in pandas 3.1.1 (`assign ok [False, True, False]`). **234-244,246-247 dataflow-closed.**

**M154.C — AST try/handler span enumeration for `_detect_and_normalize_exchange_format`:** Enumerated all tries (16 tries observed at function-relative lines; all have `Exception` handlers) confirming inner exhaustive catches (e.g., 639-640, 690-691 patterns) and bounded outer setup consistent with M152.A. No unguarded fallible statement identified outside inner exhaustive handlers in production-realistic frame paths. **641-642,694-695 closed for production-realistic frames.**

**M154.D — construction/identity checks (re-verified):** `str.split()` default separator over realistic whitespace/unicode/asset-name cases (`BTC USD`, tab/newline/NBSP/ZWSP, `''`, spaces-only, separators) produced **no empty tokens**; Python `str.split()` never yields `''` with default separator. `_not_null` body is `is None` (safe) + inner-guarded `pd.isna` + unconditional `return True`; outer 43-44 requires an `Exception` escaping identity/guarded body/return — not production-realistic (`BaseException` excluded). `_coerce_to_datetime_scalar` 337 `val is pd.NaT` is identity (`IS_OP`, cannot raise); 338 explicit `ValueError` always caught by 339-340 re-raise; 341-342 unreachable. **43-44,338-342,953 construction/identity-closed.**

**M154.E — coercer element contract sampling:** Direct coercion of `np.datetime64('NaT','ns'/'generic')`, `pd.NaT`, `'NaT'`, `None`, `nan` recorded above (M154.B table); confirms the gate split (NaT-returning vs raising) that makes 234-244 unreachable under the 216-224 completion precondition.

**M154.F — canonical trace boundary (aggregate-level):** Fresh canonical coverage rebaseline confirms 31 misses unchanged; no target cluster gained hits under 1473-test aggregate with `--source=strategies.betting_against_beta`. (No `sys.settrace`/`sys.monitoring` injected into pytest process to avoid tracer interference; M154 relies on AST/MRO, coercer-contract determinism, and construction proofs rather than repeating prior line-trace methods.)

### Per-cluster strict 4-criteria verdict (Batch 154; file:line @ `dc5294c`)

| Cluster | Lines (file:line) | Batch 154 method / result (observed) | Verdict (strict 4 criteria) |
|---|---|---|---|
| `_not_null` outer except | `data_loader.py:43-44` | M154.D: identity+inner-guarded `pd.isna`+unconditional return; no unguarded fallible statement. | **Closed (structural).** (1) yes (2) yes (3) no production escape (4) none. |
| `_normalize_index` dayfirst/last-ditch | `data_loader.py:234-244,246-247` | M154.B/E: coercer outcome table shows NaT-returning elements (`'NaT'`, `np.datetime64 NaT`) cause `continue` at 233; NaT/None/nan-raising elements prevent 224 completion so 227 not reached; 245 list assignment safe (observed). | **Closed (dataflow gate).** (1) yes (2) yes (3) no satisfiable production path (4) no path consistent with gate. |
| `_normalize_index` outer VE/TE | `data_loader.py:268-269` | M154.A: 261-265 always raises `BABDataError`; 266 intercepts; `BABDataError⊂ValueError`; no broad `Exception` on try@113. | **Closed (handler shadowing/MRO).** (1) yes (2) yes (3) no plain VE/TE escape (4) none. |
| inspect/campaign_d NaT guard | `data_loader.py:326` | **Not probed/altered.** Guard 44/5 green. | **Preserved (guard-relevant, DO NOT ALTER).** |
| `_coerce_to_datetime_scalar` NaT re-raise guards | `data_loader.py:338-342` | M154.D: 337 identity check cannot raise; 338 explicit VE caught by 339-340. | **Closed (identity+explicit-raise).** (1) yes (2) yes (3) no (4) none. |
| `_coerce_to_datetime_scalar` epoch outer except | `data_loader.py:403-404` | Prior M151.A/M152 + M154 re-audit: regex-admitted str→builtin float/abs safe; all epoch ops guarded. | **Closed (guarded epoch branches).** (1) yes (2) yes (3) no injection from realistic str (4) none. |
| `_detect_and_normalize_exchange_format` outer handlers | `data_loader.py:641-642,694-695` | M154.C: inner exhaustive handlers + bounded outer setup. | **Closed for production-realistic frames.** (1) yes (2) yes (3) no (4) none. |
| `_promote_datetime_column` outer handler | `data_loader.py:791-792` | Prior M151.C/M152 + M154 re-audit: individually guarded statements in 760-790. | **Closed (fully guarded).** (1) yes (2) yes (3) no (4) none. |
| `_normalize_asset_name` empty token continue | `data_loader.py:953` | M154.D: `str.split()` default never yields `''`; realistic whitespace/unicode cases produced no empties. | **Closed (construction-unreachable).** (1) yes (2) yes (3) realistic names exercised (4) none. |

### Strict 4-criteria assessment (Batch 154)
None satisfied for miss reduction. (1) target lines + line→code verified @ `dc5294c`. (2) no mechanism not disproven by B103-153 + M154.A-F (AST/MRO shadowing, coercer NaT-outcome table extending M152.B, exchange try enumeration, construction/identity checks, element contract sampling, canonical rebaseline). (3) no production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior demonstrated to reach any remaining handler without a production-semantics change (disallowed). (4) no expected control-flow path consistent with (2)-(3).

### Batch 154 summary
- **Delta:** 0 (31 miss unchanged). **Primary reduction not achievable by a semantics-preserving production-realistic path.** M154 extends prior proof closure with an explicit coercer outcome table showing why NaT-producing elements that satisfy 225 cannot satisfy 232-raise (and raising elements cannot satisfy 224-completion), and re-verifies 261-265→`BABDataError` making 268-269 dead under handler/MRO structure. `326` preserved.
- **`326` guard-relevant; `322` covered; campaign_d guard 44/5 green; no production semantics changed; no `.github/workflows/*` touched; batch148/149 retained.**

## Batch 155 (2026-11-08T11:09Z @ `ec637e9`, materially-new methods M155.A-E, 0 delta)

**Scope:** `strategies/betting_against_beta/data_loader.py` remaining 31 misses `43-44, 234-244, 246-247, 268-269, 326, 338-342, 403-404, 641-642, 694-695, 791-792, 953` (verified `--rcfile=/dev/null --show-missing` @ `ec637e9`; `data_loader.py` unchanged since `e945fde`, line→code stable). `322` covered. `326` guard-relevant, **preserved**. **No production code changed. No canonical test added. No workflow edits. No probe files committed.**

**Canonical rebaseline (fresh, Step 0):** **1473 passed, 0 failed, 17 skipped, 109 warnings**. Coverage **31 miss / 1683 stmts / 98%**, missing exactly `43-44, 234-244, 246-247, 268-269, 326, 338-342, 403-404, 641-642, 694-695, 791-792, 953`. Guard `campaign_d*` **44 passed, 5 warnings**. Deps: pytest 9.2.0, coverage 7.17.2, pandas 3.1.1, numpy 2.5.4, scipy 1.18.1, hypothesis 6.170.15 (`PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`).

### Materially-new Batch 155 methods (not repeating B103-154 / M149-M154)

**M155.A — PEP 669 `sys.monitoring` line-event oracle (Python 3.12.3, materially new tracer API vs prior `sys.settrace`/coverage-line traces):** Registered `sys.monitoring` `LINE` events (`DEBUGGER_ID`) with a callback filtering `data_loader.py` target-miss lines during targeted helper invocations. **Observed:** `sys.monitoring` available; callback received line events for exercised paths but **0 hits on any target miss cluster** across all Batch 155 cases.

**M155.B — production-realistic public-loader/subclass/wrapper path sweep under `sys.monitoring`:** Exercised (1) `load_returns` from CSV containing a `'NaT'` string token in the date column (`BABDataError` path, no miss hits), (2) `_normalize_index` on object index `['2021-01-01', 'NaT', ...]`, (3) `pd.DataFrame` subclass with custom `_constructor` through `_normalize_index`, (4) exchange-like frame (`timestamp/close/symbol`) through `_detect_and_normalize_exchange_format`, (5) tz-aware datetime column promotion through `_promote_datetime_column`, (6) `_normalize_asset_name` over separators/whitespace forms (`BTC-USD`, `ETH_USDT`, padded, tab, `btc/usd`). **Observed:** 0 miss-cluster hits.

**M155.C — epoch/coercer edge contract sweep (pandas 3.1.1 / NumPy 2.5.4 boundary values) under `sys.monitoring`:** Coerced `1704067200` (s), `1704067200000` (ms), `1704067200000000000` (ns magnitude), `9*20` (overflow-like digit string → `ValueError`, handled), `1e18`, `-1704067200`, `'NaT'` (returns NaTType), `np.datetime64('NaT')` (returns NaTType). **Observed:** 0 hits on `338-342` or `403-404`; overflow-like string produced normal `ValueError` from coercer contract, not outer 403-404 escape.

**M155.D — stateful/mutating element probe against 216→224→227→232 gate (targeted `sys.settrace` boundary for causal trace, complementing M155.A):** Probed (A) object index `['2021-01-01','NaT','2021-01-03']` (string NaT) — hit 215,217-221,224,225,227-233,245; **234-247 miss**; final index dropped NaT rows as normalized. (B) object index containing `np.datetime64('NaT')` — same hit set, **234-247 miss** (confirms NaT-returning `np.datetime64` follows 232→233 continue). (C) object index containing `pd.NaT` — 220 raises, routed through 222-223,248-250 fallback, no 227 block, **234-247 miss**. (D) stateful `__str__`-mutating object — no 227/234-247; observed non-production artifact only (result included `2024-01-01` from mutated string) and did not reach target misses. **Observed:** no production-realistic same-element coercer divergence producing 232 raise after 224 completion; 246-247 (`except Exception` around 227-245 after 245 assignment/list build) not hit.

**M155.E — strict 4-criteria re-audit at `ec637e9` with M155.A-D evidence:** (1) file:line/line→code verified (stable since `e945fde`). (2) No mechanism not disproven by B103-154 plus M155.A-D (`sys.monitoring` oracle, public/subclass/wrapper sweep, epoch boundary sweep, stateful-element gate probe). (3) No production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior reaches remaining handlers without semantics change. (4) No statable control-flow path consistent with (2)-(3).

### Per-cluster strict 4-criteria verdict (Batch 155; file:line @ `ec637e9`)

| Cluster | Lines (file:line) | Batch 155 method / result (observed) | Verdict (strict 4 criteria) |
|---|---|---|---|
| `_not_null` outer except | `data_loader.py:43-44` | M155.A/B: no `sys.monitoring` miss hit in public/subclass/asset-normalization/coercer sweeps; prior structural proof (identity + inner-guarded `pd.isna` + unconditional `return True`, `BaseException` excluded) remains. | **Closed (structural).** (1) yes (2) yes (3) no production escape (4) none. |
| `_normalize_index` dayfirst/last-ditch | `data_loader.py:234-244,246-247` | M155.D: cases A/B (NaT-producing elements) reach 227-233,245 only; C (raising NaT element) blocks 224→227; D (stateful mutation) no target hit/non-production artifact. M155.A/B 0 miss hits. Prior M152.B/M154.B dataflow gate stands. | **Closed (dataflow gate + observed trace).** (1) yes (2) yes (3) no satisfiable production path (4) no path consistent with 216-224 gate. |
| `_normalize_index` outer VE/TE | `data_loader.py:268-269` | M155.D case C routed to 248/250/272-274, not 268; prior M154.A MRO/shadowing proof (261-265 always `BABDataError`; 266 intercepts; `BABDataError⊂ValueError`; no broad `Exception` on try@113) unchanged. M155.A 0 hits. | **Closed (handler shadowing/MRO).** (1) yes (2) yes (3) no plain VE/TE escape (4) none. |
| inspect/campaign_d NaT guard | `data_loader.py:326` | **Not probed/altered.** Guard 44/5 green. M155.C coerced `NaT` string/`np.datetime64('NaT')` via normal contract (no campaign_d gate activation). | **Preserved (guard-relevant, DO NOT ALTER).** |
| `_coerce_to_datetime_scalar` NaT re-raise guards | `data_loader.py:338-342` | M155.C: `'NaT'`/`np.datetime64('NaT')` exercised normal contract paths, 0 miss hits; prior identity+explicit-raise proof unchanged (`337 IS_OP`, `338 VE` caught by 339-340). | **Closed (identity+explicit-raise).** (1) yes (2) yes (3) no (4) none. |
| `_coerce_to_datetime_scalar` epoch outer except | `data_loader.py:403-404` | M155.C: s/ms/ns-magnitude/large-exponent/negative epoch strings and overflow-like `9*20` all handled without 403-404 hit. Prior guarded-epoch proof unchanged. | **Closed (guarded epoch branches).** (1) yes (2) yes (3) no injection from realistic str (4) none. |
| `_detect_and_normalize_exchange_format` outer handlers | `data_loader.py:641-642,694-695` | M155.B: exchange-like `timestamp/close/symbol` frame normalized with 0 miss hits. Prior inner-exhaustive/bounded-setup proof unchanged. | **Closed for production-realistic frames.** (1) yes (2) yes (3) no (4) none. |
| `_promote_datetime_column` outer handler | `data_loader.py:791-792` | M155.B: tz-aware datetime column promotion exercised with 0 miss hits. Prior fully-guarded proof unchanged. | **Closed (fully guarded).** (1) yes (2) yes (3) no (4) none. |
| `_normalize_asset_name` empty token continue | `data_loader.py:953` | M155.B: separator/whitespace/normalization cases exercised with 0 miss hits. Prior construction proof unchanged (`str.split()` default never yields `''`). | **Closed (construction-unreachable).** (1) yes (2) yes (3) realistic names exercised (4) none. |

### Strict 4-criteria assessment (Batch 155)
None satisfied for miss reduction. (1) target lines + line→code verified @ `ec637e9`. (2) no mechanism not disproven by B103-154 + M155.A-E (PEP 669 `sys.monitoring` oracle, public/subclass/wrapper sweep, epoch boundary sweep, stateful-element gate probe, strict re-audit). (3) no production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior demonstrated to reach any remaining handler without a production-semantics change (disallowed). (4) no expected control-flow path consistent with (2)-(3).

### Batch 155 summary
- **Delta:** 0 (31 miss unchanged). **Primary reduction not achievable by a semantics-preserving production-realistic path.** M155 adds a materially-new PEP 669 `sys.monitoring` oracle and targeted public-loader/subclass/wrapper/epoch/stateful-gate probes; all observed 0 miss-cluster hits and all outcomes remain consistent with prior dataflow/handler-shadowing/construction closures. `326` preserved.
- **`326` guard-relevant; `322` covered; campaign_d guard 44/5 green; no production semantics changed; no `.github/workflows/*` touched; batch148/149 retained.**

## Batch 156 (2026-11-08T11:16Z @ `6c488ea`, materially-new methods M156.A-D, 0 delta)

**Scope:** `strategies/betting_against_beta/data_loader.py` remaining 31 misses `43-44, 234-244, 246-247, 268-269, 326, 338-342, 403-404, 641-642, 694-695, 791-792, 953` (verified `--rcfile=/dev/null --show-missing` @ `6c488ea`; `data_loader.py` unchanged since `e945fde`, line→code stable). `322` covered. `326` guard-relevant, **preserved**. **No production code changed. No canonical test added. No workflow edits. No probe files committed.**

**Canonical rebaseline (fresh, Step 0):** **1473 passed, 0 failed, 17 skipped, 109 warnings**. Coverage **31 miss / 1683 stmts / 98%**, missing exactly `43-44, 234-244, 246-247, 268-269, 326, 338-342, 403-404, 641-642, 694-695, 791-792, 953`. Guard `campaign_d*` **44 passed, 5 warnings**. Deps: pytest 9.2.0, coverage 7.17.2, pandas 3.1.1, numpy 2.5.4, scipy 1.18.1, hypothesis 6.170.15 (`PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`).

### Materially-new Batch 156 methods (not repeating B103-155 / M149-M155)

**M156.A — bytecode disassembly + `ExceptionTable` path mapping for `_normalize_index` (CPython 3.12.3, materially new static/runtime-structure evidence vs prior AST/trace/PEP669 line events):** Disassembled `data_loader._normalize_index` and inspected exception-table ranges. **Observed:** 227-block dayfirst loop (1718-1786) routes 232 raises through inner 231 handler at 4100→4116, which `pass`es (4118) and falls to 237 dayfirst attempts (4132/4246); 243 is an explicit `RAISE_VARARGS 0` caught by 4330→246 handler (4358→4360 checks `Exception`) which converts to `ValueError('unparseable')` (4376-4396). 246-247 is therefore structurally reachable only if control reaches 243 *or* 245 assignment raises — but 245 assignment is reached only when the 227 loop completes (end-for 1790→1792). 245 executed with homogeneous coercer outputs in M156.B without exception. 248-265/266-267 table ranges convert/intercept exceptions before outer `try@113` can expose plain `ValueError/TypeError` to 268-269 handler (268 handler exists at 4820 but is preceded by 266 `BABDataError` intercept at 4802).

**M156.B — coercer output-homogeneity + production-realistic index-assignment contract (pandas 3.1.1):** Sampled `_coerce_to_datetime_scalar` across ISO/Z/epoch-s/epoch-ms/float/int64 forms; **all returned `pandas.Timestamp` with tz-aware UTC**. Assigned a homogeneous list of such timestamps to `df.index` (`df.index = coerced`) — **succeeded, dtype `datetime64[us, UTC]`**. Subclass `pd.DataFrame` (`_constructor` preserved) passed through `_normalize_index`. Mixed tz-naive/aware assignment (non-coercer path) produced `object` dtype in pandas 3.1.1 but is not produced by the homogeneous coercer outputs observed. **Observed:** no production-realistic 245 assignment failure for coercer-produced homogeneous values.

**M156.C — 216→224→227→232 control-flow gate re-derivation from bytecode + coercer contract:** 216-223 loop (1480-1548) completes 224 (`STORE_ATTR index` at 1554) only when every `idx` element coerces successfully via `_coerce_to_datetime_scalar` (1492). 225 `isna` check (1566-1714) gates 227. 232 in the 227 loop calls the same `_coerce_to_datetime_scalar(v)` over the same `idx`; inner 231 handler suppresses 232 exceptions so 234-244 run dayfirst fallbacks and 243 re-raises only if all fallbacks fail (converting to 246-247 `ValueError('unparseable')`). **Observed/derived:** for a given `idx` element, coercer success in 232 prevents 234-244 for that element; coercer NaT-return (e.g. `'NaT'`, `np.datetime64('NaT')`) makes 232 succeed and 233 `continue`; coercer raise prevents 224 completion so 227 is not reached. No production-realistic same-`idx`/same-coercer state divergence demonstrated (stateful `__str__` mutation remains a non-production artifact per M155.D). 234-247 remains dataflow-gated.

**M156.D — MRO/shadowing + construction-unreachable corroboration:** `BABDataError.__mro__ = (BABDataError, ValueError, Exception, BaseException, object)` and `issubclass(BABDataError, ValueError)` is `True` (pandas 3.1.1 runtime), confirming any `BABDataError` raised at 261-265 is catchable by 266 and also matches `ValueError` in general — but handler order 266 before 268 intercepts first. `_normalize_asset_name` split/strip cases (`BTC/USD`, `ETH-USDT`, padded, tab, NBSP, `DOGE/USDT:USDT`) produced **no empty post-strip tokens** (`str.split()` default semantics). `43-44/338-342/403-404/641-642/694-695/791-792` structural/guarded proofs unchanged.

**M156.E — strict 4-criteria re-audit at `6c488ea` with M156.A-D:** (1) file:line/line→code verified (stable since `e945fde`). (2) No mechanism not disproven by B103-155 plus M156.A-D (bytecode ExceptionTable mapping, coercer output homogeneity/245 assignment, control-flow gate re-derivation, MRO/construction corroboration). (3) No production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior reaches remaining handlers without semantics change. (4) No statable control-flow path consistent with (2)-(3).

### Per-cluster strict 4-criteria verdict (Batch 156; file:line @ `6c488ea`)

| Cluster | Lines (file:line) | Batch 156 method / result (observed) | Verdict (strict 4 criteria) |
|---|---|---|---|
| `_not_null` outer except | `data_loader.py:43-44` | M156.D: structural proof unchanged (identity + inner-guarded `pd.isna` + unconditional return). | **Closed (structural).** (1) yes (2) yes (3) no production escape (4) none. |
| `_normalize_index` dayfirst/last-ditch | `data_loader.py:234-244,246-247` | M156.A-C: ExceptionTable shows 232→4100→4118→237 fallthrough and 243→246 conversion; 245 reached only after 227 loop completes; 216-224 completion vs 232/NaT outcomes gate 227; homogeneous coercer outputs make 245 assignment succeed (M156.B). No same-`idx` production divergence. | **Closed (dataflow gate + bytecode path + assignment contract).** (1) yes (2) yes (3) no satisfiable production path (4) no path consistent with 216-224 gate/coercer contract. |
| `_normalize_index` outer VE/TE | `data_loader.py:268-269` | M156.A/D: 266 intercepts `BABDataError` before 268; `BABDataError⊂ValueError`; 261-265 conversion in 248-265 range. 268 handler structurally present but shadowed by handler order/MRO for converted errors. | **Closed (handler shadowing/MRO + bytecode order).** (1) yes (2) yes (3) no plain VE/TE escape past conversion/intercept (4) none. |
| inspect/campaign_d NaT guard | `data_loader.py:326` | **Not probed/altered.** Guard 44/5 green. | **Preserved (guard-relevant, DO NOT ALTER).** |
| `_coerce_to_datetime_scalar` NaT re-raise guards | `data_loader.py:338-342` | M156.D: identity+explicit-raise proof unchanged. | **Closed (identity+explicit-raise).** (1) yes (2) yes (3) no (4) none. |
| `_coerce_to_datetime_scalar` epoch outer except | `data_loader.py:403-404` | M156.D: guarded epoch proof unchanged. | **Closed (guarded epoch branches).** (1) yes (2) yes (3) no (4) none. |
| `_detect_and_normalize_exchange_format` outer handlers | `data_loader.py:641-642,694-695` | M156.D: inner-exhaustive/bounded-setup proof unchanged. | **Closed for production-realistic frames.** (1) yes (2) yes (3) no (4) none. |
| `_promote_datetime_column` outer handler | `data_loader.py:791-792` | M156.D: fully-guarded proof unchanged. | **Closed (fully guarded).** (1) yes (2) yes (3) no (4) none. |
| `_normalize_asset_name` empty token continue | `data_loader.py:953` | M156.D: construction proof unchanged; sampled realistic forms yielded no empty post-strip tokens. | **Closed (construction-unreachable).** (1) yes (2) yes (3) realistic names exercised (4) none. |

### Strict 4-criteria assessment (Batch 156)
None satisfied for miss reduction. (1) target lines + line→code verified @ `6c488ea`. (2) no mechanism not disproven by B103-155 + M156.A-E (bytecode ExceptionTable mapping, coercer output homogeneity/245 assignment contract, 216→224→227→232 gate re-derivation, MRO/construction corroboration, strict re-audit). (3) no production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior demonstrated to reach any remaining handler without a production-semantics change (disallowed). (4) no expected control-flow path consistent with (2)-(3).

### Batch 156 summary
- **Delta:** 0 (31 miss unchanged). **Primary reduction not achievable by a semantics-preserving production-realistic path.** M156 adds materially-new CPython 3.12 bytecode/ExceptionTable path mapping, coercer output-homogeneity/245-assignment contract evidence, and MRO/construction corroboration; all outcomes remain consistent with prior dataflow/handler-shadowing/construction closures. `326` preserved.
- **`326` guard-relevant; `322` covered; campaign_d guard 44/5 green; no production semantics changed; no `.github/workflows/*` touched; batch148/149 retained.**
