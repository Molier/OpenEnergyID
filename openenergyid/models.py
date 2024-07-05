"""Data models for the Open Energy ID."""

import datetime as dt
from typing import Optional, overload, Union

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

import pandas as pd
from pydantic import BaseModel


class TimeSeries(BaseModel):
    """Time series data."""

    index: list[dt.datetime]
    data: list[float]

    @classmethod
    def from_pandas(cls, data: pd.Series) -> "TimeSeries":
        """Create a MultiVariableRegressionInputFrame from a pandas TimeSeries."""
        return cls.model_validate(data.to_dict())

    def to_pandas(self, timezone: str = "UTC") -> pd.Series:
        """Convert the MultiVariableRegressionInputFrame to a pandas TimeSeries."""
        series = pd.Series(self.data, index=self.index)
        series.index = pd.to_datetime(series.index, utc=True)
        return series.tz_convert(timezone)

    @overload
    def to_json(self, path: None = None, **kwargs) -> str: ...

    @overload
    def to_json(self, path: str, **kwargs) -> None: ...

    def to_json(self, path: Optional[str] = None, **kwargs) -> Optional[str]:
        """Save the TimeSeries to a JSON file or return as string."""
        if path is None:
            return self.model_dump_json(**kwargs)
        else:
            encoding = kwargs.pop("encoding", "UTF-8")
            with open(path, "w", encoding=encoding) as file:
                file.write(self.model_dump_json(**kwargs))

    @overload
    @classmethod
    def from_json(cls, string: str, **kwargs) -> "TimeSeries": ...

    @overload
    @classmethod
    def from_json(cls, path: str, **kwargs) -> "TimeSeries": ...

    @classmethod
    def from_json(
        cls, string: Optional[str] = None, path: Optional[str] = None, **kwargs
    ) -> "TimeSeries":
        """Load the TimeSeries from a JSON file or string."""
        if string:
            return cls.model_validate_json(string, **kwargs)
        elif path:
            encoding = kwargs.pop("encoding", "UTF-8")
            with open(path, "r", encoding=encoding) as file:
                return cls.model_validate_json(file.read(), **kwargs)
        else:
            raise ValueError("Either string or path must be provided.")


class TimeSeriesCollection(BaseModel):
    """Time series data."""

    index: list[dt.datetime]

    @classmethod
    def from_pandas(cls, data: pd.DataFrame) -> "TimeSeriesCollection":
        """Create a MultiVariableRegressionInputFrame from a pandas DataFrame."""
        return cls.model_validate(data.to_dict(orient="split"))

    def to_pandas(self, timezone: str = "UTC") -> Union[pd.Series, pd.DataFrame]:
        """Convert to a Pandas Object."""
        raise NotImplementedError

    @overload
    def to_json(self, path: None = None, **kwargs) -> str: ...

    @overload
    def to_json(self, path: str, **kwargs) -> None: ...

    def to_json(self, path: Optional[str] = None, **kwargs) -> Optional[str]:
        """Dump to a JSON string or file."""
        if path is None:
            return self.model_dump_json(**kwargs)
        encoding = kwargs.pop("encoding", "UTF-8")
        with open(path, "w", encoding=encoding) as file:
            file.write(self.model_dump_json(**kwargs))
        return None

    @overload
    @classmethod
    def from_json(cls, string: str, **kwargs) -> "TimeSeriesCollection": ...

    @overload
    @classmethod
    def from_json(cls, path: str, **kwargs) -> "TimeSeriesCollection": ...

    @classmethod
    def from_json(
        cls, string: Optional[str] = None, path: Optional[str] = None, **kwargs
    ) -> "TimeSeriesCollection":
        """Load the TimeSeries from a JSON file or string."""
        if string:
            return cls.model_validate_json(string, **kwargs)
        if path:
            encoding = kwargs.pop("encoding", "UTF-8")
            with open(path, "r", encoding=encoding) as file:
                return cls.model_validate_json(file.read(), **kwargs)
        raise ValueError("Either string or path must be provided.")


class TimeSeries(TimeSeriesBase):
    """Time series data with a single column."""

    name: Union[str, None] = None
    data: list[float]

    @classmethod
    def from_pandas(cls, data: pd.Series) -> Self:
        """Create from a Pandas Series."""
        return cls.model_construct(name=data.name, data=data.tolist(), index=data.index.tolist())

    def to_pandas(self, timezone: str = "UTC") -> pd.Series:
        """Convert to a Pandas Series."""
        series = pd.Series(self.data, name=self.name, index=self.index)
        series.index = pd.to_datetime(series.index, utc=True)
        return series.tz_convert(timezone)


class TimeDataFrame(TimeSeriesBase):
    """Time series data with multiple columns."""

    columns: list[str]
    data: list[list[float]]

    @classmethod
    def from_pandas(cls, data: pd.DataFrame) -> Self:
        """Create from a Pandas DataFrame."""
        return cls.model_construct(
            columns=data.columns.tolist(), data=data.values.tolist(), index=data.index.tolist()
        )

    def to_pandas(self, timezone: str = "UTC") -> pd.DataFrame:
        """Convert to a Pandas DataFrame."""
        frame = pd.DataFrame(self.data, columns=self.columns, index=self.index)
        frame.index = pd.to_datetime(frame.index, utc=True)
        return frame.tz_convert(timezone)

    @classmethod
    def from_timeseries(cls, data: list[TimeSeries]) -> Self:
        """Create from a list of TimeSeries objects."""
        return cls.model_construct(
            columns=[series.name for series in data],
            data=[series.data for series in data],
            index=data[0].index,
        )

    def to_timeseries(self) -> list[TimeSeries]:
        """Convert to a list of TimeSeries objects."""
        return [
            TimeSeries(name=column, data=column_data, index=self.index)
            for column, column_data in zip(self.columns, self.data)
        ]
