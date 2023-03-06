# pylint: skip-file
from pandera.typing.fastapi import UploadFile
from fastapi import FastAPI, File
from pandera.typing import DataFrame
from typing import Optional
from pydantic import BaseModel, Field

import pandera as pa

app = FastAPI()

class Transactions(pa.SchemaModel):
    id: pa.typing.Series[int]
    cost: pa.typing.Series[float] = pa.Field(ge=0, le=1000)

    class Config:
        coerce = True
        

class TransactionsOut(Transactions):
    id: pa.typing.Series[int]
    cost: pa.typing.Series[float]
    name: pa.typing.Series[str]


class TransactionsDictOut(TransactionsOut):
    class Config:
        to_format = "dict"
        to_format_kwargs = {"orient": "records"}




@app.post("/transactions/", response_model=DataFrame[TransactionsDictOut])
def create_transactions(transactions: DataFrame[Transactions]):
    output = transactions.assign(name="foo")
    ...  # do other stuff, e.g. update backend database with transactions
    return output


class TransactionsParquet(Transactions):
    class Config:
        from_format = "parquet"
        
class TransactionsJsonOut(TransactionsOut):
    class Config:
        to_format = "json"
        to_format_kwargs = {"orient": "records"}
        
class ResponseModel(BaseModel):
    filename: str
    df: pa.typing.DataFrame[TransactionsJsonOut]


@app.post("/file/", response_model=ResponseModel)
def create_upload_file(
    file: UploadFile[DataFrame[TransactionsParquet]] = File(...),
):
    return {
        "filename": file.filename,
        "df": file.data.assign(name="foo"),
    }
