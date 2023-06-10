from fastapi import FastAPI,Body
import enum
from starlette.responses import RedirectResponse
from typing import Optional
from pydantic import BaseModel, Field
import uvicorn
import datetime as dt
from fastapi_pagination import Page, add_pagination, paginate
class TradeDetails(BaseModel):
    buySellIndicator: str = Field(description="A value of BUY for buys, SELL for sells.")

    price: float = Field(description="The price of the Trade.")

    quantity: int = Field(description="The amount of units traded.")


class Trade(BaseModel):
    asset_class: Optional[str] = Field(alias="assetClass", default=None, description="The asset class of the instrument traded. E.g. Bond, Equity, FX...etc")

    counterparty: Optional[str] = Field(default=None, description="The counterparty the trade was executed with. May not always be available")

    instrument_id: str = Field(alias="instrumentId", description="The ISIN/ID of the instrument traded. E.g. TSLA, AAPL, AMZN...etc")

    instrument_name: str = Field(alias="instrumentName", description="The name of the instrument traded.")

    trade_date_time: dt.datetime = Field(alias="tradeDateTime", description="The date-time the Trade was executed")

    trade_details: TradeDetails = Field(alias="tradeDetails", description="The details of the trade, i.e. price, quantity")

    trade_id: str = Field(alias="tradeId", default=None, description="The unique ID of the trade")

    trader: str = Field(description="The name of the Trader")

raw_trade = [
    {
    "assetClass": "Bond",
    "counterparty": "Hastiin",
    "instrumentId": "GHJD",
    "instrumentName": "Debentures",
    "tradeDateTime": "2024-07-04 00:02:35.520788",
    "tradeDetails": {
        "buySellIndicator": "BUY",
        "price": 9.36,
        "quantity": 42
    },
    "tradeId": "8c8f9d65-ef45-43cc-9253-badac16bdba9",
    "trader": "Akash"
    },
    {
        "assetClass": "Bond",
        "counterparty": "Masamba",
        "instrumentId": "TSWQ",
        "instrumentName": "Debentures",
        "tradeDateTime": "2021-02-03 00:03:35.520788",
        "tradeDetails": {
            "buySellIndicator": "SELL",
            "price": 1.36,
            "quantity": 32
        },
        "tradeId": "f0aed2de-d4d2-4213-bed1-60bd6fb1d2b0",
        "trader": "Otar"
    },
    {
        "assetClass": "Equity",
        "counterparty": "Fyokla",
        "instrumentId": "TSEW",
        "instrumentName": "Preference Shares",
        "tradeDateTime": "2022-12-03 00:03:35.520788",
        "tradeDetails": {
            "buySellIndicator": "BUY",
            "price": 2.36,
            "quantity": 12
        },
        "tradeId": "8ae396c4-94e3-400b-b44a-ebfc06ef131c",
        "trader": "Koba"
    },
    {
        "assetClass": "Equity",
        "counterparty": "Isokrates",
        "instrumentId": "DAWD",
        "instrumentName": "Mutual Funds",
        "tradeDateTime": "2023-10-03 00:06:35.520788",
        "tradeDetails": {
            "buySellIndicator": "SELL",
            "price": 5.36,
            "quantity": 22
        },
        "tradeId": "a3fff395-d13f-4faf-80d6-71b291d43cf0",
        "trader": "Jaycee"
    }
]


app = FastAPI()

class OrderEnum(str, enum.Enum):
    ASC = 'ASC'
    DESC = 'DESC'

@app.get("/")
async def main():
    return RedirectResponse(url="/docs/")
@app.post("/write")
async def entre_the_data(*,Trade_Details:TradeDetails,Trades:Trade,spousal_status: str ):
    return {"name":Trade_Details, "name2":Trades,"spousal_status":spousal_status}

@app.get("/trading")
async def list_of_Trades() -> dict:
    results =[]
    for trade in raw_trade:
        results.append(trade)
    return results

#@app.get("/hello/{name}")
#async def say_hello(name: str):
@app.get("/trades/{trade_id}")
async def  retrieving_a_single_Trade_by_ID(*, trade_id: str) -> dict:
    result = []
    for trade in raw_trade:
        if trade["tradeId"] == trade_id:
            result.append(trade)
    if result:
        return result[0]
@app.get("/trade",status_code=200, response_model=Page[Trade])
async def searching_against_Trades(*, search: str) -> list:
    result = []
    for trade in raw_trade:
        if search.lower() in trade["counterparty"].lower() | search.lower() in trade["instrumentId"].lower() | search.lower() in trade["instrumentName"].lower() | search.lower() in trade["trader"].lower():
            result.append(trade)

    return paginate(result)


@app.get("/trades", status_code=200, response_model=Page[Trade])
async def filtering_Trades(*, assetClass: str, maxPrice: float , minPrice: float ,tradeType: str , end: dt.datetime,start:dt.datetime) -> list:

    results = []
    for trade in raw_trade:
        flagAssetClass = True
        flagTradeType = True
        flagMinPrice = True
        flagMaxPrice = True
        flagStart = True
        flagEnd = True

        if assetClass != None:
            flagAssetClass = False
        if tradeType != None:
            flagTradeType = False
        if minPrice != None:
            flagMinPrice = False
        if maxPrice != None:
            flagMaxPrice = False
        if start != None:
            flagStart = False
        if end != None:
            flagEnd = False

        if assetClass != None:
            if assetClass.lower() in trade["assetClass"].lower():
                flagAssetClass = True
        if tradeType != None:
            if tradeType.lower() in trade["tradeDetails"]["buySellIndicator"].lower():
                flagTradeType = True

        if minPrice != None:
            if trade["tradeDetails"]["price"] >= minPrice:
                flagMinPrice = True

        if maxPrice != None:
            if maxPrice != None:
                if trade["tradeDetails"]["price"] <= maxPrice:
                    flagMaxPrice = True

        if start != None:
            if str(start) >= trade["tradeDateTime"]:
                flagStart = True
        if end != None:
            if str(end) <= trade["tradeDateTime"]:
                flagEnd = True

        if flagAssetClass and flagTradeType and flagMinPrice and flagMaxPrice and flagStart and flagEnd:
            results.append(trade)

    return paginate(results)


add_pagination(app)

if __name__ == "__main__":
    uvicorn.run("app:app", port=9000, reload=True)