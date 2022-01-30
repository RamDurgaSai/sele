# Sele
Sele is a Web Scrapper that supports scraping information about favourite programs from media streaming paltforms like Destney+ Hotstar 

# How to Setup Sele
## 1. Setup Programs.json
    Create a programs.json file root dir
    add key as program name and value as program link to programs.json

## 2. Setup Config.json
    create config.json file in root dir
    add telegram json with api_id and api_key as keys and their value as values
    add pdisk json with api_key's (Optional)
    add selenium json with selenium user dirs (Optional)

## 3. Setup Channel json
    add all telegram channels as json file

## 3. Setup Vpn (Optional)
    Want to scrap other region content ... just with Nord VPN support
    Install Nord VPN desktop applicaiton and login 
    set vpn = True in main.py

## 4. Setup DB (Optional)
     Want to track work ... just create a SQLite db with programs as table 
     place it in root dir

# Start Sele 
     python3 main.py

## Notes
    1.Sele won't start automatically
    2.If you want to post updates daily ... Setup scheduler 


