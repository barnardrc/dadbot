

import time
import regex as re

# Gets the filename generated for today's date that corresponds to 
# the most recent log
def file_name_formatter():
    unwanted_chars = '(),'
    localTime = time.localtime()[0:3]
    rgx = re.compile('[%s]' % unwanted_chars)
    localTime = rgx.sub('', str(time.localtime()[0:3])).replace(' ', '_')
    filename = localTime+' '+"dadbotlog.log"
    return filename

def file_name_report_formatter():
    unwanted_chars = '(),'
    localTime = time.localtime()[0:3]
    rgx = re.compile('[%s]' % unwanted_chars)
    localTime = rgx.sub('', str(time.localtime()[0:3])).replace(' ', '_')
    filename = localTime+' '+"report.log"
    return filename

def report_grab(filename):
    with open(filename, 'r') as f:
        file = f.readlines()
    return file

def write_to_file(filename, content):
    with open(filename, 'w') as f:
        f.write(content)

def time_calculator(file):
    searchExpression = r'\d*\D\d*'
    startTime = re.search(searchExpression, file[0])
    endTime = re.search(searchExpression, file[-1])
    return startTime.group(), endTime.group()


def profit_calculator(balanceData, avgSalePrice):
    normalProfit = 0
    salesCollected = 0
    
    for ind, item in enumerate(balanceData):
        if (
                ind > 0 and
                item - balanceData[ind - 1] > 0 and
                item - balanceData[ind - 1] < avgSalePrice
            ):
            
            difference = item - balanceData[ind - 1]
            
            # Debugging
            '''
            print(item)
            print(balanceData[ind - 1])
            print(difference)
            print("\n")
            '''
            
            salesCollected += 1
            normalProfit += difference
            avgProfit = normalProfit // salesCollected
            
    return normalProfit, salesCollected, avgProfit
        
def get_Avg(listOfNums):
    total = 0
    
    for item in listOfNums:
        total += item
        
    return total // len(listOfNums)
    
def report_generator(file):
    searchExpressionBalanceData = r'\d*\D\d*: Balance check: .*?(\d+)'
    searchExpressionSellPrice = r'\d*\D\d*: Selling for .*?(\d+)'
    amountSessions = 0
    salePriceList = []
    results = []
    balanceData = []
    for line in file:
        
        salePrice = re.search(searchExpressionSellPrice, line)
        nums = re.search(searchExpressionBalanceData, line)
        
        if salePrice is not None:
            salePriceList.append(int(salePrice.group(1)))
            
        if nums is not None:
            results.append(nums.group(1))
       
    
        if line[1:2] == '-':
            amountSessions += 1
    
    for ind, item in enumerate(results):
        if ( 
                item != results[ind - 1]
                and len(item) == 5
            ):
            
            balanceData.append(int(item))
            
    avgSalePrice = get_Avg(salePriceList)
    
    return amountSessions, balanceData, avgSalePrice

def main():
    file = report_grab(file_name_formatter())
    reportTime = time.asctime()
    amountSessions, balanceData, avgSalePrice = report_generator(file)        
    profit, salesCollected, avgProfit = profit_calculator(balanceData, avgSalePrice)
    
    #for balance in balanceData:
    #    print(balance)
    
    startTime, endTime = time_calculator(file)
    
    output = (f"""
Time of report:
{reportTime}
Start time: {startTime}
End time: {endTime}
Total Sessions: {amountSessions} Session(s)
Total sales collected: {salesCollected} Sales
Average Sale Price: {avgSalePrice} Gold
Average Profit: {avgProfit} Gold per Sale
Total normal profit, excluding outliers:\n
              {profit} Gold
        """)
    
    write_to_file(file_name_report_formatter(), output)

main()
