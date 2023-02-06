import time
from kucoin.client import User # Ledger data stored accessed through User endpoint in API and its SDK
import credentials

from shared import db, cute
from schemas import Ledger, LedgerSecond
from ledger_entry import LedgerEntry
from pprint import pprint
from sqlalchemy.dialects.postgresql import insert

client = User(credentials.api_key, credentials.api_secret, credentials.api_passphrase) # Create User class called client


def parse_date(ca):
    extra_dates = {
        "utc": "DD/MM/YY",
        "fy": 0
    }
    
    if isinstance(ca, str):
        int_ca = int(ca)
    else:
        int_ca = ca
    
    if int_ca > 9999999999:
        int_ca = int(int_ca / 1000)
    
    extra_dates['utc'] = time.strftime('%d/%m/%Y', time.localtime(int_ca))
    month = time.strftime('%m', time.localtime(int_ca))
    year = time.strftime('%Y', time.localtime(int_ca))
    
    if int(month) >= 7:
        extra_dates['fy'] = int(year)
    elif int(month) < 7:
        extra_dates['fy'] = int(year) - 1
        
    return extra_dates


def get_order():
    oid = '60eaa6f32575430006ee3f39'
    ass_val = cute(db.select(Ledger.asset, Ledger.direction, db.func.sum(Ledger.size)).group_by(Ledger.asset, Ledger.direction)
             .filter(Ledger.order_id == oid))
    for a in ass_val:
        print(a)
    

def ledger_entry(id, order_id, date, acc_type, bizType, symbol, asset, direction, size, fee):
    insert_stmt = insert(Ledger).values(
        id=id,
        order_id=order_id,
        date=date,
        acc_type=acc_type,
        biz_type=bizType,
        symbol=symbol,
        asset=asset,
        direction=direction,
        size=size,
        fee=fee
    )

    do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['id'])
    cute(do_nothing_stmt)
    
    '''
    v = LedgerSecond(
        id=id,
        order_id=order_id,
        date=date,
        acc_type=acc_type,
        biz_type=bizType,
        symbol=symbol,
        asset=asset,
        direction=direction,
        size=size,
        fee=fee
    )
    
    insert(Ledger).values(
    id=id,
    order_id=order_id,
    date=date,
    acc_type=acc_type,
    biz_type=bizType,
    symbol=symbol,
    asset=asset,
    direction=direction,
    size=size,
    fee=fee
    )
    '''


def commit_entries():
    db.session.commit()


def ledger_test():
    start = 1619411442000
    end = start + 86400000
    ledger = client.get_account_ledger(startAt=start,endAt=end,pageSize=100,currency='USDT')
    print(f"total number : {ledger['totalNum']}")
    for i in ledger['items']:
        print(i['balance'])


def date_to_integer():
    s = cute(db.select(Ledger)).scalars().all()
    
    for i in s:
        date = int(int(i.date) / 1000)
        if i.direction == 'in':
            size = i.size
        else:
            size = 0 - i.size
        
        insert_stmt = insert(LedgerSecond).values(
        id=i.id,
        order_id=i.order_id,
        date=date,
        acc_type=i.acc_type,
        biz_type=i.biz_type,
        symbol=i.symbol,
        asset=i.asset,
        direction=i.direction,
        size=size,
        fee=i.fee
        )

        do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['id'])
        cute(do_nothing_stmt)
    
    db.session.commit()   
    
    
def unique_orders():
    orders = cute(db.select(db.distinct(Ledger.order_id))).scalars()


def balance_at_date(date, date_from):
    # 1593525600    1625061600  1656597600  1688133600
    utc = parse_date(date)
    utcFrom = parse_date(date_from)
    
    asset = 'BTC'
    assets = cute(db.select(db.distinct(LedgerSecond.asset)).filter(db.and_(LedgerSecond.date < date, LedgerSecond.date > date_from))).scalars().all()
    sizes = []
    
    for a in assets:
        size = cute(db.select(db.func.sum(LedgerSecond.size))
                .filter(db.and_(LedgerSecond.asset == a, LedgerSecond.date < date))).scalars().first()
        
        if a == 'BTC' and size > 0.0001:
            sizes.append([a, round(size,6)])
        elif a != 'BTC' and size > 0.01:
            sizes.append([a, round(size,3)])
    
        #fees = cute(db.select(db.func.sum(LedgerSecond.fee))
        #        .filter(db.and_(LedgerSecond.asset == asset, LedgerSecond.date < date))).scalars().first()
  
    return { 
            "assets": sizes,
            "utc": utc['utc'],
            "utcFrom": utcFrom['utc']
            }
   

def ledger_running_sizes():
    asset = 'USDT'
    orders = cute(db.select(LedgerSecond.date, LedgerSecond.size)
                  .filter(LedgerSecond.asset == asset).order_by(LedgerSecond.date.asc()))
    
    order_no = 1
    order_vals = {}
    running_size = 0
    
    for i in orders:
        size = round(i.size, 3)
        
        if str(order_no) in order_vals.keys():
            order_vals[str(order_no)]['size'] += size
        else:
            order_vals.update({str(order_no): 
                { "size": size,
                  "date": i.date
                }
                })
        
        running_size += size
        
        if running_size >513.5 and running_size < 514.5:
            print(i.date, "514ish")

        if (running_size >= 0 and running_size <= 0.9) or (running_size <= 0 and running_size >= -0.9):
            print(f"{i.date} {round(running_size,3)}")   
            order_no += 1
    
    #for v in order_vals.values():
    #    print(f"{v['date']} {round(v['size'],3)}")
        

'''
Need to count number of items per acc_type and bizType,
Use the one with the most values
    or
if equal use most common values
'''

'''
GET UNIQUE VALUES
    Using SQLAlchemy Method
        osum = cute(db.select(Ledger.asset).filter(Ledger.order_id == "62d8971f0eac7e00018012af")).scalars()
        print(osum.unique().all())
    
    Using Postgres DISTINCT
        osum = cute(db.select(db.distinct(Ledger.asset)).filter(Ledger.order_id == "62d8971f0eac7e00018012af")).scalars()
        print(osum.all())
'''

'''
def get_job_by_id(id):
    # uses a JOIN query to select a customers data when their id is assigned to a job
    job_cust_info = cute(db.select(Customer.business_name, Customer.branch_name, Customer.contact_name,
                                   Customer.location, Jobcard.issue, Jobcard.comments, Jobcard.job_id)
                         .join_from(Customer, Jobcard).filter_by(job_id=id)).first()
    # deconstructs customer and job info returned from query
    bname, branch, cname, location, issue, comments, jid = job_cust_info

    # another JOIN query is made to get details about the equipment that is listed on the job card
    job_equip_info = cute(db.select(Equipment.serial_number, Equipment.make, Equipment.model,
                                    Equipment.manufacture_year, Equipment.cycle_count)
                          .join_from(Equipment, Jobcard).filter_by(job_id=id)).first()
    # deconstructs equipment info returned from query
    sn, make, model, mfy, cc = job_equip_info
    # pass all returned values in to very basic html to be displayed
    return update_card(jid, bname, branch, cname, make, mfy, sn, model, cc, issue)


def update_job(job_id, comments):
    print(comments)
    j = cute(db.select(Jobcard).filter(Jobcard.job_id == job_id)).scalar()
    print(j.issue)
    j.comments = comments
    j.completed = True
    db.session.commit()
    return f'<html style="background-color:black"><h1 style="color:white">Job Card Submitted!</h1> \
            {index_list()}</html>'


def new_card(cust_id, issue, machine, technician):
    tech = cute(db.select(Staff).filter(Staff.staff_id == technician)).scalar()
    cust = cute(db.select(Customer).filter(Customer.customer_id == cust_id)).scalar()
    equip = cute(db.select(Customer).filter(Equipment.serial_number == machine)).scalar()

    new_job = Jobcard(job_id=secrets.token_hex(3), issue=issue)

    tech.job_staff.extend([new_job])
    cust.job_customer.extend([new_job])
    equip.job_equipment.extend([new_job])
    db.session.commit()
    return f'<html style="background-color:black"><h1 style="color:white">Job Created</h1> \
            {index_list()}</html>'
            
            
bcrypt==4.0.1
certifi==2022.9.24
cffi==1.15.1
charset-normalizer==2.1.1
click==8.1.3
cryptography==38.0.3
Flask==2.2.2
Flask-Bcrypt==1.0.1
Flask-Dance==6.2.0
Flask-JWT-Extended==4.4.4
Flask-Login==0.6.2
flask-marshmallow==0.14.0
Flask-SQLAlchemy==3.0.2
greenlet==2.0.1
idna==3.4
itsdangerous==2.1.2
Jinja2==3.1.2
jsonify==0.5
MarkupSafe==2.1.1
marshmallow==3.18.0
marshmallow-sqlalchemy==0.28.1
oauthlib==3.2.2
packaging==21.3
psycopg2-binary==2.9.5
    pycparser==2.21
    PyJWT==2.6.0
    pyOpenSSL==22.1.0
    pyparsing==3.0.9
    python-dotenv==0.21.0
    requests==2.28.1
    requests-oauthlib==1.3.1
    six==1.16.0
SQLAlchemy==1.4.43
    - urllib3==1.26.12
    - URLObject==2.4.3
Werkzeug==2.2.2

'''