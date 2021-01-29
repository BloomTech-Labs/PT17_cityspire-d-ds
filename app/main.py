from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app import db, ml, viz

description = """
MISSION: Be a one-stop resource for users to receive the most accurate city information.


CITYSPIRE APP:
An app that analyzes data from cities such as populations, cost of living,\n
rental rates, crime rates, park (walk score), and many other social \n
and economic factors that are important in deciding where someone would like to live.\n
This app will present such important data in an intuitive and easy to understand interface.\n

Use data to find a place right for you to live.
"""

app = FastAPI(
    title='CITYSPIRE API',
    description=description,
    docs_url='/',
)

app.include_router(db.router, tags=['Database'])
app.include_router(ml.router, tags=['Machine Learning'])
app.include_router(viz.router, tags=['Visualization'])

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

if __name__ == '__main__':
    uvicorn.run(app)