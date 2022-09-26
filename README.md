# T1A3 - Create A Terminal Application

## Repository
[2w00fz Github](https://github.com/2w00fs/T1A3) - My Repo, T1A3

Coding style conventions:
In line with [PEP8](https://peps.python.org/pep-0008/).
Common styling includes:
- Limiting redundant white spaces
- 4 spaces per indent
- Limiting redundant operators
    ```
    #wrong
    if x == True
    #right
    if x
    ```
- Using specific Exception Handlers (Key Error, Type Error etc)
- Avoid using single letter variables that look similar to numerals
- Class Names using CamelCase
- Functions and variables using lower_case_with_underscores

## Three Features
### Pull Transaction Ledger From KuCoin
##### Use of Variables and Variable Scope
###### Requires recieving data that is stored in a dictionary.
- All the values are either recieved as strings and some need to be converted to integers and floats. One value contains another dictionary that needs to be deconstructed in order to parse it's values.

###### Loops and Conditional Control Structures
- Loops are required to fetch data day by day (as limited by the API)
- Loops also required to increase the page number if more than 500 entries are returned
- Loops required to retry the API call if an error is returned
- Conditions are required for changing behaviour based on error codes, or the code reaching the end of the days it has been fetching data for
- Conditons also required for checking that the Ledger Data does not already exist (a user can input data to be processed that has previously been fetched)

###### Error Handling
- Making sure that user supplied data is not empty
- Pausing the program if a Rate Limit has been reached with the API
- User supplied file name does not contain illegal characters

### Calculate Combined Profit and Loss for each Asset
##### Use of Variables and Variable Scope, Control Structures
###### Making Decisions about different Variables
- For each item processed only one asset is given
- It could either be the Asset that was traded for, or it could be the Base Asset used as the Currency
- To determine this the value will be passed to a different function to and compared with other data recieved to determine what it is.
- If it is a Base Asset it needs to be sent to another module to query the API for it's value in USDT (1 USDT = 1 USD, theoretically...)
- These details then need to be passed to an Order object and an Asset object to track the overall value and to create a list of orders that can be exported.

###### Error Handling
- The Rate Limit for fetching prices is very low so prices will be saved for a day ahead of what is required, and an exception will be printed with a countdown timer to retry when it happens
- Some assets may have changed symbol (or delisted) and will give a different error that will return a place holder value, and a log entry made so that it can be manually reviewed afterwards.
- Type errors are avoided by Type Converting numbers to strings and vice versa

## Export Results as a CSV
##### Use of Variables and Variable Scope, Control Structures
The values to be exported are Objects that are contained in within a dictionary. They write_csvs() function gets called from the ProccessOrders class by the executing function in the main program. A header is added first containing a string of the keys, which act as the first row in a spreadsheet (column names), then the returned values are destructured and restructed as a string, with formatting inline with CSV standards.
##### Error Handling
All data being written ends up in an fstring so the input data is largely agnostic about the data type, however the name provided by the user to save the file will be checked for illegal characters using regex, alerting them to any characters provided that are not allowed.

# INSTALLATION
## System Requirements
#### Hardware
##### Minimum
Raspberry Pi B+
512MB RAM
1GB Free Space
##### Preferential
2GB RAM
2GB Free Space

#### Software
Python 3.xx

## Installation Procedure
#### Dependencies
- Git
- [KuCoin Python SDK](https://github.com/Kucoin/kucoin-python-sdk)

#### Other Requirements
API Keys are required to fetch account data
These can be generated from the [API Managment](https://www.kucoin.com/account/api?spm=kcWeb.B1assets.person.8) section in your KuCoin profile.
Your API Key, API Secret and API Passphrase are required.

### Installation
##### Option 1
Create a file named run.sh and paste following code in to it

    #/bin/bash
    
    git clone "https://github.com/2w00fs/T1A3.git"
    cd T1A3
    pip install kucoin-python

    touch credentials.py
    echo Please input your API Key
    read api_key
    echo api_key= \"$api_key\" >> credentials.py
    echo Please input your API Secret
    read api_secret
    echo api_secret= \"$api_secret\" >> credentials.py
    echo Please input your API Passphrase
    read api_passphrase
    echo api_passphrase= \"$api_passphrase\" >> credentials.py

    python3 main.py

Open a terminal in the directory that contains the script, and that you would like to install it in and run "bash run.sh"
##### Option 2
- From the Command Line, run "git clone "https://github.com/2w00fs/T1A3.git" to download the repository.
- Run "pip install kucoin-python" to install the KuCoin SDK
- Create a file named "credentials.py" and store your API details in the following format:
    ```
    api_key=
    api_secret=
    api_passphrase=
    ```
- Run the program using "python3 main.py"

## Usage

When running using "python3 main.py" the only argument you will be prompted for is a File Name.
Naming Conventions are standard characters, however Spaces are not allowed.

Two Command Flags are optional:

    -ledger or --ledgername
eg. python3 main.py -ledger myfirstledger

or

    -prices --pricelist
eg. python3 main.py --pricelist savedprices

They can be used to specify data files that may have previously been downloaded by the program.
They can be found in the root directory with a file extension of .json
They can be used as an input and they will be updated with newer values if any are available.

Exported CSV files will be located in the root directory with the name provided, suffixed with _Assets or _Orders for the respective data.
A Log file will also be stored for any errors that may occur.