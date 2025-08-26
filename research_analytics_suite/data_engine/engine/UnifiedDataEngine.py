"""
UnifiedDataEngine Module

Defines the UnifiedDataEngine class that combines functionalities from DaskData and TorchData
to provide a unified interface for handling data.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from __future__ import annotations

import csv
import json
import os
import uuid
import warnings
from typing import Dict, Tuple, Optional, Any, Union

import aiofiles
import dask.dataframe as dd
import numpy as np
import pandas as pd
from torch.utils.data import DataLoader

from research_analytics_suite.analytics.core.AnalyticsCore import AnalyticsCore
from research_analytics_suite.commands import command, link_class_commands
from research_analytics_suite.utils.Config import Config
from research_analytics_suite.data_engine.core.DaskData import DaskData
from research_analytics_suite.data_engine.memory.DataCache import DataCache
from research_analytics_suite.data_engine.core.TorchData import TorchData
from research_analytics_suite.data_engine.data_streams.BaseInput import BaseInput
from research_analytics_suite.utils.CustomLogger import CustomLogger

# ------- Helper Functions -------

@command
def flatten_json(y: Dict[str, any]) -> Dict[str, any]:
    """
    Flattens a nested JSON dictionary.

    Args:
        y (Dict[str, Any]): The JSON dictionary to flatten.

    Returns:
        Dict[str, Any]: The flattened JSON dictionary.
    """
    out = {}

    def flatten(x: Any, name: str = ''):
        if isinstance(x, dict):
            for a in x:
                flatten(x[a], name + a + '_')
        elif isinstance(x, list):
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

def _to_datetime_quiet(values, *, utc=False):
    """
    Try pandas >=2.0 fast path with format='mixed' (no warning).
    Fallback to a scoped suppression if the kw isn't supported.
    """
    try:
        return pd.to_datetime(values, errors="coerce", utc=utc, format="mixed")
    except TypeError:
        # Older pandas: silence only inside this call
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            return pd.to_datetime(values, errors="coerce", utc=utc)

def _is_numeric_like(s: pd.Series) -> float:
    """Share of cells that coerce to numbers."""
    return pd.to_numeric(s.astype(str).str.strip(), errors="coerce").notna().mean()

def _guess_header_depth(sample: pd.DataFrame, max_levels: int = 3) -> int:
    """
    Heuristic: up to the first `max_levels` rows can be header rows if:
      - those rows are mostly non-numeric, AND
      - the next row(s) are mostly numeric (data)
    DLC-friendly: if first col has ['scorer','bodyparts','coords'] in rows 0..2 → depth=3
    """
    CustomLogger().debug(f"[_guess_header_depth] start shape={sample.shape}")
    if sample.empty:
        return 0

    # DLC fast-path
    first_col = sample.iloc[:, 0].astype(str).str.lower().str.strip()
    tokens = first_col.head(3).tolist()
    if tokens[:3] == ["scorer", "bodyparts", "coords"]:
        CustomLogger().debug("[_guess_header_depth] DLC header detected -> depth=3")
        return 3

    # Generic heuristic
    # Consider k from max_levels..1 (prefer deeper if valid)
    for k in range(min(max_levels, len(sample)), 0, -1):
        header_block = sample.iloc[:k]
        # non-numeric share across header rows (mean over all cells)
        header_non_num = 1.0 - pd.to_numeric(
            header_block.stack().astype(str).str.strip(), errors="coerce"
        ).notna().mean()
        # data‐ish check on next 1–3 rows if present
        next_rows = sample.iloc[k:k+3] if len(sample) > k else pd.DataFrame()
        data_like = None
        if not next_rows.empty:
            data_like = pd.to_numeric(
                next_rows.stack().astype(str).str.strip(), errors="coerce"
            ).notna().mean()

        CustomLogger().debug(f"[_guess_header_depth] k={k} header_non_num={header_non_num:.2f} data_like={None if data_like is None else round(data_like,2)}")

        # thresholds: header rows are >70% non-numeric, and following rows >=60% numeric
        if header_non_num >= 0.7 and (data_like is None or data_like >= 0.6):
            CustomLogger().debug(f"[_guess_header_depth] chose depth={k}")
            return k

    CustomLogger().debug("[_guess_header_depth] depth=0")
    return 0

def _flatten_columns(cols: pd.Index) -> list[str]:
    """
    Flatten columns:
      - If MultiIndex: drop constant levels; join remaining with '_'.
      - Always return strings.
    """
    if isinstance(cols, pd.MultiIndex):
        levels = list(zip(*cols.tolist()))  # transpose tuples to level lists
        keep_level = []
        for i, level_vals in enumerate(levels):
            if len(set(level_vals)) > 1:
                keep_level.append(i)
        if not keep_level:
            # all levels constant — keep last one to avoid empty names
            keep_level = [len(cols.levels) - 1]
        flat = []
        for tup in cols:
            parts = [str(tup[i]).strip() for i in keep_level if str(tup[i]).strip() != ""]
            flat.append("_".join(parts) if parts else "col")
        return flat
    # Single-level
    return [str(c).strip() if str(c).strip() else "col" for c in cols]

def _looks_like_header_token(s: str) -> bool:
    s = str(s).strip()
    # heuristics: non-numeric, short-ish, no spaces, starts with letter
    return (
        s != "" and
        not s.replace(".", "", 1).isdigit() and
        len(s) <= 32 and
        (" " not in s) and
        s[0].isalpha()
    )

def _maybe_drop_inband_header(df: pd.DataFrame) -> pd.DataFrame:
    """
    If we accidentally read with header=None, drop a first row that looks like
    a header token (e.g., 'value', 'name', etc.) when the rest of the column/row
    is mostly numeric/bool/datetime.
    """
    if df.empty:
        return df

    # Single column: drop first row if it matches column name or looks like a header
    if df.shape[1] == 1:
        col = str(df.columns[0]).strip().lower()
        first = str(df.iloc[0, 0]).strip()
        first_l = first.lower()

        # condition A: first cell equals column name
        cond_equal = (first_l == col)

        # condition B: first cell looks like a header and the remainder is mostly convertible to numeric/datetime/bool
        rest = df.iloc[1:, 0].astype(str).str.strip()
        rest_num = pd.to_numeric(rest, errors="coerce")
        rest_dt = _to_datetime_quiet(rest, utc=False)
        rest_bool = rest.str.lower().isin(["true", "false"])

        cond_headerish = _looks_like_header_token(first) and any([
            rest_num.notna().mean() >= 0.6,
            rest_dt.notna().mean()  >= 0.6,
            rest_bool.mean()        >= 0.6,
        ])

        if cond_equal or cond_headerish:
            CustomLogger().debug(f"[_maybe_drop_inband_header] dropping first row: {first!r}")
            return df.iloc[1:].reset_index(drop=True)
        return df

    # Single row: symmetric case (rare, but safe)
    if df.shape[0] == 1:
        row = df.iloc[0].astype(str).str.strip()
        # if row equals the (cleaned) column names, treat as header row
        cols = pd.Index(df.columns).astype(str).str.strip()
        if row.str.lower().tolist() == cols.str.lower().tolist():
            CustomLogger().debug("[_maybe_drop_inband_header] dropping single header row")
            return pd.DataFrame(columns=df.columns)

    return df

def _strip_and_drop_empty(df: pd.DataFrame) -> pd.DataFrame:
    CustomLogger().debug(f"[_strip_and_drop_empty] start shape={df.shape}")
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].astype(str).str.strip()
    df = df.replace(r"^\s*$", np.nan, regex=True)
    df = df.dropna(how="all", axis=0)
    df = df.dropna(how="all", axis=1)
    CustomLogger().debug(f"[_strip_and_drop_empty] done shape={df.shape}")
    return df

def _dedupe_headers(cols):
    CustomLogger().debug(f"[_dedupe_headers] start n_cols={len(cols)}")
    seen = {}
    out = []
    for c in cols:
        base = str(c).strip() if c is not None else "col"
        name = base if base else "col"
        if name not in seen:
            seen[name] = 0
            out.append(name)
        else:
            seen[name] += 1
            out.append(f"{name}_{seen[name]}")
    CustomLogger().debug(f"[_dedupe_headers] done -> {out}")
    return out

def _coerce_scalar_value(x: Any):
    xs = str(x).strip()
    # numeric
    num = pd.to_numeric(pd.Series([xs]), errors="coerce").iloc[0]
    if pd.notna(num):
        CustomLogger().debug(f"[_coerce_scalar_value] numeric -> {num}")
        return float(num)
    # boolean
    low = xs.lower()
    if low in {"true", "false"}:
        val = (low == "true")
        CustomLogger().debug(f"[_coerce_scalar_value] bool -> {val}")
        return val
    # datetime
    dt = pd.to_datetime(pd.Series([xs]), errors="coerce", utc=False).iloc[0]
    if pd.notna(dt):
        CustomLogger().debug(f"[_coerce_scalar_value] datetime -> {dt}")
        return dt
    CustomLogger().debug(f"[_coerce_scalar_value] string -> {xs!r}")
    return xs

def _optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    CustomLogger().debug(f"[_optimize_dtypes] start dtypes={dict(df.dtypes)}")
    for c in df.columns:
        if df[c].dtype == object:
            low = df[c].str.lower()
            if low.isin(["true","false"]).mean() > 0.8:
                df[c] = low.map({"true": True, "false": False})
                continue
            num = pd.to_numeric(df[c], errors="coerce")
            if num.notna().mean() > 0.8:
                df[c] = num
                continue
            dt = _to_datetime_quiet(df[c], utc=False)
            if dt.notna().mean() > 0.7:
                df[c] = dt
                continue
    for c in df.columns:
        if df[c].dtype == object:
            uniq = df[c].nunique(dropna=True)
            if 0 < uniq <= max(10, int(len(df) * 0.05)):
                df[c] = df[c].astype("category")
    df = df.convert_dtypes()
    CustomLogger().debug(f"[_optimize_dtypes] done dtypes={dict(df.dtypes)}")
    return df

def _to_best_shape(df: pd.DataFrame,
                   dict_orient: str = "list") -> Union[dict, list, Any, pd.DataFrame]:
    r, c = df.shape
    CustomLogger().debug(f"[_to_best_shape] shape={r}x{c}, orient={dict_orient}")
    if r == 0 and c == 0:
        CustomLogger().debug("[_to_best_shape] -> {} (empty)")
        return {}
    if r == 1 and c == 1:
        val = _coerce_scalar_value(df.iloc[0, 0])
        CustomLogger().debug(f"[_to_best_shape] -> scalar {val!r}")
        return val
    if r == 1 and c >= 1:
        out = [_coerce_scalar_value(x) for x in df.iloc[0].to_list()]
        CustomLogger().debug(f"[_to_best_shape] -> list (single row) len={len(out)}")
        return out
    if c == 1 and r >= 1:
        out = [_coerce_scalar_value(x) for x in df.iloc[:, 0].to_list()]
        CustomLogger().debug(f"[_to_best_shape] -> list (single col) len={len(out)}")
        return out
    if dict_orient == "records":
        out = df.to_dict(orient="records")
        CustomLogger().debug(f"[_to_best_shape] -> records len={len(out)}")
        return out
    out = df.to_dict(orient="list")
    CustomLogger().debug(f"[_to_best_shape] -> dict(cols) ncols={len(out)}")
    return out

SAFE_DELIMS = {",", "\t", ";", "|"}

def _sniff_csv_header(path: str, sample_bytes: int = 32768) -> Tuple[bool, Optional[str]]:
    CustomLogger().debug(f"[_sniff_csv_header] start path={path}")
    with open(path, "r", newline="") as f:
        sample = f.read(sample_bytes)

    # Heuristic: if the sample has no safe delimiter at all, treat as single-cell/one-field rows
    if not any(d in sample for d in SAFE_DELIMS):
        CustomLogger().debug("[_sniff_csv_header] no safe delimiter in sample -> (has_header=False, delim=',')")
        return False, ","

    try:
        dialect = csv.Sniffer().sniff(sample)
        has_header = csv.Sniffer().has_header(sample)
        delim = dialect.delimiter

        # Guard: keep only safe delimiters that actually occur
        if delim not in SAFE_DELIMS or sample.count(delim) == 0:
            CustomLogger().debug(f"[_sniff_csv_header] unsafe/absent delim {repr(delim)} -> fallback ','")
            delim = ","

        CustomLogger().debug(f"[_sniff_csv_header] has_header={has_header}, delim={repr(delim)}")
        return has_header, delim
    except Exception as e:
        CustomLogger().debug(f"[_sniff_csv_header] sniff failed ({e}) -> fallback ','")
        return False, ","

def _read_csv_smart(path: str, use_dask: bool) -> pd.DataFrame:
    """
    Robust CSV reader:
      - Sniffs delimiter safely.
      - Detects header depth (0..3) from a small raw sample (handles DLC-style 3-row headers).
      - Reads full file:
          * pandas with header=[...] when multi-level headers are present (Dask can't do that)
          * Dask otherwise for large single-header/no-header files
      - Cleans cells/columns, flattens MultiIndex to user-friendly names,
        preserves in-band header rows if applicable, and optimizes dtypes.
    """
    CustomLogger().debug(f"[_read_csv_smart] start use_dask={use_dask}")

    # --- Quick path: treat truly single-cell files (no newline, no safe delimiter) as 1x1
    with open(path, "r", newline="") as f:
        raw = f.read(1024)
    if ("\n" not in raw) and (not any(d in raw for d in SAFE_DELIMS)):
        val = raw.strip()
        CustomLogger().debug(f"[_read_csv_smart] true single-cell detected -> [[{val!r}]]")
        return pd.DataFrame([[val]])

    # --- Sniff delimiter/header *safely*
    has_header, delim = _sniff_csv_header(path)

    # --- Build a small *raw* sample with header=None for header-depth detection
    #     (we purposely avoid inferring headers here)
    try:
        sample_raw = pd.read_csv(path, nrows=2000, dtype=str, sep=delim, header=None, engine="python")
    except Exception as e:
        CustomLogger().debug(f"[_read_csv_smart] raw sample read failed ({e}) -> trying default comma")
        sample_raw = pd.read_csv(path, nrows=2000, dtype=str, sep=",", header=None, engine="python")

    # Light clean before header-depth heuristics (keeps non-empty rows)
    sample_raw = _strip_and_drop_empty(sample_raw)

    # --- Decide header depth (0..3)
    header_depth = _guess_header_depth(sample_raw, max_levels=3)

    # --- If we guessed "no header", we also consider the sniffer's has_header flag
    #     (header_depth > 0 overrides has_header)
    header_arg = (list(range(header_depth)) if header_depth > 0
                  else (0 if has_header else None))

    # --- FULL READ PATHS ---
    # Use pandas when:
    #   * multi-level headers present (header_depth > 1), OR
    #   * dask isn't requested, OR
    #   * we want the most compatible path for header=[...].
    must_use_pandas = (header_depth > 1) or (not use_dask)

    if must_use_pandas:
        CustomLogger().debug(f"[_read_csv_smart] pandas full read (header_depth={header_depth}, has_header={has_header})")
        full = pd.read_csv(
            path,
            dtype="object",         # read as object first; we coerce later
            sep=delim,
            header=header_arg,
            engine="python"
        )
        # Clean up & normalize
        full = _strip_and_drop_empty(full)
        # Flatten columns if MultiIndex, otherwise dedupe/trim
        if isinstance(full.columns, pd.MultiIndex):
            full.columns = _flatten_columns(full.columns)
        else:
            full.columns = _dedupe_headers(full.columns)

        # --- DLC convenience: rename the first index-like column
        # Avoid ambiguous truthiness on pandas Index
        if len(full.columns) > 0:
            first = full.columns[0]
            # if MultiIndex somehow slipped through, normalize the tuple to our flattened name
            if isinstance(first, tuple):
                first = "_".join(str(p).strip() if p is not None else "" for p in first).strip("_")
            else:
                first = str(first)

            if first == "scorer_bodyparts_coords":
                full = full.rename(columns={"scorer_bodyparts_coords": "frame"})
                # best-effort numeric frame index
                full["frame"] = pd.to_numeric(full["frame"], errors="coerce")

        # Drop in-band header if we accidentally read header=None but the first row is a header-ish row
        full = _maybe_drop_inband_header(full)
        # Optimize dtypes (numeric, bool, datetime, category)
        out = _optimize_dtypes(full)
        CustomLogger().debug(f"[_read_csv_smart] pandas full done shape={out.shape}")
        return out

    # DASK path: only used for single-level header or no header
    CustomLogger().debug(f"[_read_csv_smart] dask full read (header_depth={header_depth}, has_header={has_header})")
    dask_header = (0 if (header_depth == 1 or has_header) else None)
    ddf = dd.read_csv(
        path,
        sep=delim,
        header=dask_header,
        dtype="object",
        assume_missing=True,
        blocksize="64MB",
    )
    ddf = ddf.map_partitions(lambda p: _strip_and_drop_empty(p))
    CustomLogger().debug("[_read_csv_smart] starting ddf.compute()")
    full = ddf.compute()
    CustomLogger().debug(f"[_read_csv_smart] ddf.compute() done shape={full.shape}")

    # Flatten/dedupe columns as needed
    if isinstance(full.columns, pd.MultiIndex):
        # Dask can't create MultiIndex columns from header=[...]; if we somehow land here,
        # just flatten to be safe.
        full.columns = _flatten_columns(full.columns)
    else:
        full.columns = _dedupe_headers(full.columns)

    # In-band header drop (no-op if not applicable)
    full = _maybe_drop_inband_header(full)

    # Final dtype optimization
    out = _optimize_dtypes(full)
    CustomLogger().debug(f"[_read_csv_smart] dask full done shape={out.shape}")
    return out


@link_class_commands
class UnifiedDataEngine:
    """
    A class that combines functionalities from DaskData and TorchData.

    Attributes:
        data: The data point.
        backend: The backend to use ('dask' or 'torch').
        dask_client: Dask client instance.
        analytics: AnalyticsCore instance for analytics operations.
        dask_data: DaskData instance for handling data with Dask.
        torch_data: TorchData instance for handling data with PyTorch.
        data_cache: DataCache instance for caching data.
        live_input_source: Live data input source instance.
    """
    _GENERATED_ID = None

    def __init__(self, backend='dask', dask_client=None, data=None, data_name=None):
        """
        Initializes the UnifiedDataEngine instance.

        Args:
            backend (str): The backend to use ('dask' or 'torch'). Default is 'dask'.
            dask_client: Dask client instance. Default is None.
            data: The data point. Default is None.
        """
        self._GENERATED_ID = uuid.uuid4()
        self.data = data
        self.data_name = f"{data_name}" if data_name else f"data_{uuid.uuid4().hex[:4]}"
        self.backend = backend
        self._logger = CustomLogger()
        self._config = Config()
        self.dask_client = dask_client  # Pointer to primary Dask client
        self.analytics = AnalyticsCore()  # Initialize AnalyticsCore Engine

        from research_analytics_suite.data_engine.Workspace import Workspace
        self._workspace = Workspace()

        self.dask_data = DaskData(data)
        self.torch_data = TorchData(data)
        self.data_cache = DataCache()  # Initialize DataCache
        self.live_input_source = None  # Initialize live input source
        self.engine_id = f"{uuid.uuid4()}"

    def __getstate__(self):
        state = self.__dict__.copy()
        state['_GENERATED_ID'] = None
        state['_logger'] = None
        state['_config'] = None
        state['data_cache'] = None
        state['dask_client'] = None
        state['live_input_source'] = None
        state['_cache'] = None
        state['analytics'] = None
        state['torch_data'] = None
        state['dask_data'] = None
        state['_workspace'] = None
        state['live_data_handler'] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._GENERATED_ID = uuid.uuid4()
        self._logger = CustomLogger()
        self._config = Config()
        # self.data_cache = DataCache()

        from research_analytics_suite.data_engine.Workspace import Workspace
        self._workspace = Workspace()

        self.live_input_source = None
        self.analytics = AnalyticsCore()
        self.torch_data = TorchData(self.data)
        self.dask_data = DaskData(self.data)

    @property
    def runtime_id(self) -> str:
        """
        Returns the runtime ID of the UnifiedDataEngine instance.

        Returns:
            str: The runtime ID.
        """
        return f"e-{self.engine_id[:4]}_{self._GENERATED_ID}"

    @property
    def short_id(self) -> str:
        """
        Returns the short ID of the UnifiedDataEngine instance.

        Returns:
            str: The short ID.
        """
        return f"{self.data_name}_{self.engine_id[:4]}"

    @command
    def detect_data_row(self, file_path, data_type):
        def is_numerical(_row):
            return all(self.is_number(_cell) for _cell in _row)

        if data_type == 'csv':
            with open(file_path, 'r') as f:
                for i, line in enumerate(f):
                    row = line.strip().split(',')
                    if is_numerical(row):
                        return i

        elif data_type == 'json':
            return 0

        elif data_type == 'parquet':
            return 0

        elif data_type == 'hdf5':
            return 0

        elif data_type == 'excel':
            xls = pd.ExcelFile(file_path)
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                for i, row in df.iterrows():
                    if is_numerical(row):
                        return i

        raise ValueError(f"Unsupported data type: {data_type}")

    @staticmethod
    @command
    def is_number(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    @command
    def load_data(self,
                  file_path: str,
                  return_type: str = "auto",
                  dict_orient: str = "list") -> Tuple[Union[dict, list, Any, pd.DataFrame], str]:
        file_path = os.path.normpath(file_path)
        if not os.path.exists(file_path):
            self._logger.error(FileNotFoundError(f"File not found: {file_path}"), self.__class__.__name__)
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower().lstrip(".")
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        use_dask = size_mb >= 50
        self._logger.info(f"Loading data from {file_path} as {ext}")
        self._logger.debug(
            f"[load_data] size_mb={size_mb:.2f}, use_dask={use_dask}, return_type={return_type}, dict_orient={dict_orient}")

        try:
            if ext in {"csv", "tsv", "psv"}:
                self._logger.debug("[load_data] path -> _read_csv_smart")
                df = _read_csv_smart(file_path, use_dask=use_dask)

            elif ext == "json":
                self._logger.debug("[load_data] path -> json")
                with open(file_path, "r") as f:
                    obj = json.load(f)
                if isinstance(obj, dict):
                    pdf = pd.DataFrame([flatten_json(obj)])
                elif isinstance(obj, list):
                    rows = []
                    for item in obj:
                        rows.append(flatten_json(item) if isinstance(item, dict) else {"value": item})
                    pdf = pd.DataFrame(rows)
                else:
                    pdf = pd.DataFrame([{"value": obj}])
                # df = _maybe_drop_inband_header(df)
                df = _optimize_dtypes(_strip_and_drop_empty(pdf))

            elif ext in {"parquet", "pq"}:
                self._logger.debug("[load_data] path -> parquet")
                df = dd.read_parquet(file_path).compute() if use_dask else pd.read_parquet(file_path)
                df = _maybe_drop_inband_header(df)
                df = _optimize_dtypes(_strip_and_drop_empty(df))

            elif ext in {"h5", "hdf5", "hdf"}:
                self._logger.debug("[load_data] path -> hdf")
                try:
                    df = pd.read_hdf(file_path, key="data")
                except Exception:
                    with pd.HDFStore(file_path) as store:
                        keys = store.keys()
                    if not keys:
                        df = pd.DataFrame()
                    else:
                        df = pd.read_hdf(file_path, key=keys[0])
                df = _maybe_drop_inband_header(df)
                df = _optimize_dtypes(_strip_and_drop_empty(df))

            elif ext in {"xls", "xlsx"}:
                self._logger.debug("[load_data] path -> excel (first sheet)")
                df = pd.read_excel(file_path, sheet_name=0, dtype=str)
                df.columns = _dedupe_headers(df.columns)
                df = _maybe_drop_inband_header(df)
                df = _optimize_dtypes(_strip_and_drop_empty(df))

            else:
                err = ValueError(f"Unsupported data type: {ext}")
                self._logger.error(err, self.__class__.__name__)
                raise err

            self._logger.debug(f"[load_data] df.shape={df.shape}, dtypes={dict(df.dtypes)}")

            # Decide return object
            if return_type == "dataframe":
                self._logger.debug("[load_data] return_type=dataframe")
                return df, ext

            if return_type == "dict":
                self._logger.debug(f"[load_data] return_type=dict orient={dict_orient}")
                return df.to_dict(orient=dict_orient if dict_orient in {"records"} else "list"), ext

            if return_type == "list":
                self._logger.debug("[load_data] return_type=list (best-effort)")
                if df.shape[0] == 1 or df.shape[1] == 1:
                    out = _to_best_shape(df, dict_orient)
                    self._logger.debug("[load_data] list path -> single-axis -> list/scalar")
                    return out, ext
                out = df.to_dict(orient="records")
                self._logger.debug("[load_data] list path -> records")
                return out, ext

            if return_type == "records":
                self._logger.debug("[load_data] return_type=records")
                return df.to_dict(orient="records"), ext

            # AUTO
            self._logger.debug("[load_data] return_type=auto -> _to_best_shape")
            out = _to_best_shape(df, dict_orient)
            return out, ext

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
            raise

    @command
    def save_data(self, file_path: str):
        """
        Saves data to the specified file path.

        Args:
            file_path (str): The path to the data file.
        """
        from research_analytics_suite.data_engine.data_streams.DataTypeDetector import detect_by_content
        data_type = detect_by_content(file_path)
        self._logger.info(f"Saving data to {file_path} as {data_type}")

        if data_type == 'csv':
            self.data.to_csv(file_path, single_file=True)
        elif data_type == 'json':
            self.data.to_json(file_path)
        elif data_type == 'parquet':
            self.data.to_parquet(file_path)
        elif data_type == 'hdf5':
            self.data.to_hdf(file_path, key='data')
        elif data_type == 'excel':
            pandas_df = self.data.compute() if isinstance(self.data, dd.DataFrame) else self.data
            pandas_df.to_excel(file_path)
        else:
            self._logger.error(ValueError(f"Unsupported data type: {data_type}"), self.__class__.__name__)
            return

        self._logger.debug("Data saved")

    @command
    async def save_engine(self, instance_path: str) -> None:
        """
        Saves the engine to the specified instance path.

        Args:
            instance_path (str): The path to the instance.
        """
        engine_path = os.path.join(instance_path, self._config.ENGINE_DIR, self.engine_id)
        os.makedirs(engine_path, exist_ok=True)
        data_path = os.path.join(instance_path, 'data')
        os.makedirs(data_path, exist_ok=True)
        data_file_path = os.path.join(data_path, f"{self.data_name}.joblib")

        self._logger.debug(f"Saving engine to {engine_path}")

        # Save data
        async with aiofiles.open(data_file_path, 'w') as data_file:
            await data_file.write(json.dumps(self.data, indent=4))

        # Save metadata
        metadata = {
            'data_name': self.data_name,
            'backend': self.backend,
            'engine_id': self.engine_id,
        }
        async with aiofiles.open(os.path.join(f"{engine_path}", "metadata.json"), 'w') as metadata_file:
            await metadata_file.write(json.dumps(metadata, indent=4))

        # Save a pickleable state of the engine
        engine_state = self.__getstate__()
        async with aiofiles.open(os.path.join(f"{engine_path}", 'engine_state.joblib'), 'w') as state_file:
            await state_file.write(json.dumps(engine_state, indent=4))

        self._logger.debug(f"Engine saved to {instance_path}")

    @staticmethod
    @command
    async def load_engine(instance_path: str, engine_id: str) -> UnifiedDataEngine:
        """
        Loads an engine from the specified instance path and engine ID.

        Args:
            instance_path (str): The path to the instance.
            engine_id (str): The ID of the engine to load.

        Returns:
            UnifiedDataEngine: The loaded engine.
        """
        engine_path = os.path.join(instance_path, engine_id)

        # Load metadata
        async with aiofiles.open(os.path.join(f"{engine_path}", 'metadata.json'), 'r') as metadata_file:
            try:
                metadata = json.loads(await metadata_file.read())
            except Exception as e:
                # Return an empty engine if metadata is not found
                return UnifiedDataEngine()

        data_path = os.path.normpath(os.path.join(instance_path, '../data', f"{metadata['data_name']}.joblib"))

        # Load data
        async with aiofiles.open(data_path, 'r') as data_file:
            try:
                data = json.loads(await data_file.read())
            except Exception as e:
                data = {}

        # Load engine state
        async with aiofiles.open(os.path.normpath(
                os.path.join(f"{engine_path}", 'engine_state.joblib')), 'r') as state_file:
            try:
                engine_state = json.loads(await state_file.read())
            except Exception as e:
                CustomLogger().debug(f"Failed to load engine state: {e}")
                engine_state = {}

        engine = UnifiedDataEngine()
        if engine_state:
            engine.__setstate__(engine_state)
        engine.data = data

        return engine

    @command
    def set_backend(self, backend):
        """
        Sets the backend for the data engine.

        Args:
            backend (str): The backend to set ('dask' or 'torch').
        """
        if backend not in ['dask', 'torch']:
            self._logger.error(ValueError("Backend must be either 'dask' or 'torch'"), self.__class__.__name__)
        self.backend = backend

    @command
    def apply(self, action):
        """
        Applies a function to the data.

        Args:
            action (function): The function to apply to the data.
        """
        if self.backend == 'dask':
            self.dask_data.apply(action)
        elif self.backend == 'torch':
            self.torch_data = TorchData(action(self.torch_data.get_data()))

    @command
    def compute(self):
        """
        Computes the result for the data.

        Returns:
            The computed result.
        """
        if self.backend == 'dask':
            return self.dask_data.compute()
        elif self.backend == 'torch':
            return self.torch_data.get_data()

    @command
    def get_torch_loader(self, batch_size: int = 32, shuffle: bool = True) -> DataLoader:
        """
        Gets a PyTorch DataLoader for the data.

        Args:
            batch_size (int): The batch size for the DataLoader. Default is 32.
            shuffle (bool): Whether to shuffle the data. Default is True.

        Returns:
            DataLoader: The PyTorch DataLoader for the data.
        """
        if self.backend == 'torch':
            return DataLoader(self.torch_data, batch_size=batch_size, shuffle=shuffle)
        else:
            self._logger.error(
                RuntimeError("DataLoader is only available for 'torch' backend"), self.__class__.__name__)

    @command
    def get_pickleable_data(self) -> Dict[str, any]:
        """
        Gets the data in a pickleable format.

        Returns:
            The data in a pickleable format.
        """
        data = self.__dict__.copy()
        data.pop('_logger', None)
        data.pop('dask_client', None)
        data.pop('live_input_source', None)
        return data

    def cache_data(self, key, data):
        """
        Caches the given data with the specified key.

        Args:
            key (str): The key to associate with the cached data.
            data: The data to cache.
        """
        self.data_cache.set(key, data)

    def get_cached_data(self, key):
        """
        Retrieves cached data by key.

        Args:
            key (str): The key associated with the cached data.

        Returns:
            The cached data or None if the key is not found.
        """
        return self.data_cache.get_key(key)

    @command
    def clear_cache(self):
        """
        Clears all cached data.
        """
        self.data_cache.clear()

    @command
    def set_live_input(self, live_input: BaseInput):
        """
        Sets the live input source.

        Args:
            live_input (BaseInput): The live input source to set.
        """
        self.live_input_source = live_input

    @command
    def read_live_data(self):
        """
        Reads data from the live input source.

        Returns:
            The data read from the live input source.
        """
        if self.live_input_source:
            return self.live_input_source.read_data()
        return None

    @command
    def close_live_input(self):
        """
        Closes the live input source.
        """
        if self.live_input_source:
            self.live_input_source.close()
