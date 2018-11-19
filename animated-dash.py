import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import matplotlib.image as mpimg
from iexfinance import Stock
from StockDatabase import msft_minute, msft_hundredDays
from get_article_info import getNewsInfo
from matplotlib.font_manager import FontProperties
img=mpimg.imread('mslogo.jpeg')

# choose a background style:
# ex: style.use('dark_background')
style.use('fivethirtyeight')

msft = Stock("MSFT")

# getting the stock values for 100 days from the API
sql_data, status = msft_hundredDays()

# function to plot the animated plot
def animate(i):
    price_data, times_data = msft_minute()
    box1.clear()
    box1.grid(color='k')
    box1.plot(times_data, price_data)

#create dashboard dimensions
dash = plt.figure(figsize=(12, 10))
dash.suptitle('Microsoft, NASDAQ: MSFT', fontsize=30, fontweight='bold')
box1=dash.add_axes([0.06,0.35,0.95,0.4]) # left, bottom, width, height (range 0 to 1)
box2=dash.add_axes([0.0,0,0.9,0.2])
box3=dash.add_axes([0.8,0,0.3,0.2])
box4=dash.add_axes([0.7,0.75,0.3,0.15])
box5=dash.add_axes([0.2,0.75,0.5,0.1])
box6=dash.add_axes([0,0.77,0.2,0.2])
box7=dash.add_axes([0.85,0.91,0.01,0.01])

# data generator for real-time stock price
def data_gen(t=0):
    cnt = 0
    while cnt < 1000:
        cnt += 1
        t += 1
        price = Stock("MSFT").get_price()
        yield t, float(price)

def run(data):
    t, y = data
    text.set_text(y)
    return text
    
# function to show the last update time
def run_title(data):
	t_last = msft_minute()[1][-1]
	out = 'Plot Last Refreshed at %s'%t_last
	text_title.set_text(out)
	return text_title

# Plot infos
box1.set_xlabel('Time')
box1.set_ylabel('Stock Value')
box1.set_title('Stock Graph')
box1.tick_params(axis='x', rotation=90, labelsize=10)
text = box4.text(0.5, 0.3, '', fontsize=25, ha='center')
text_title = box7.text(0,0,'', ha='center', fontsize=8, style='italic')

# Get info for the news articles
news_info = getNewsInfo()

# Plot table of top words
box2.axes.get_xaxis().set_visible(False)
box2.axes.get_yaxis().set_visible(False)
box2.set_title('Top 10 Words of the 3 Latest Articles', ha='center')

# Rw and Column headers for the table
row = ['Article 1', 'Article 2', 'Article 3']
col = ['Word 1', 'Word 2', 'Word 3', 'Word 4', 'Word 5', 'Word 6', 'Word 7','Word 8','Word 9','Word 10']

cellText = []

for val in news_info['TopWords_Articles'].values():
    cellText.append(val)

table = box2.table(cellText=cellText, 
                   rowLabels=row, 
                   colWidths=[0.03] * 10,
                   colLabels=col,
                   bbox=(0.1, 0.05, 0.75, 0.8),
                   loc='center')
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1, 1.5)

# Making the row headers and column headers bold
for (row, col), cell in table.get_celld().items():
  if (row == 0) or (col == -1):
    cell.set_text_props(fontproperties=FontProperties(weight='bold'))

# Plotting the Article Info section
box3.axes.get_xaxis().set_visible(False)
box3.axes.get_yaxis().set_visible(False)
box3.set_title('Article Info', ha='right')
box3.text(0.12,0.8,r'# Articles:', ha='left', weight='bold')
box3.text(0.45,0.8,news_info['NumArticles'], ha='left')          
box3.text(0.16,0.58,r'Source:', ha='left', weight='bold')
box3.text(0.39,0.58,news_info['Source'].title(), ha='left')
box3.text(0.09,0.34,r'Date Range:', ha='left', weight='bold')
box3.text(0.39,0.34,news_info['StartDate'], ha='left')
box3.text(0.47,0.21,r'to', ha='left')
box3.text(0.39,0.09,news_info['EndDate'], ha='left')

# Plotting the real-time stock price
box4.text(0.5,0.7, r'Real-Time Stock Price ($)', fontsize=16, ha='center')
box4.axes.get_xaxis().set_visible(False)
box4.axes.get_yaxis().set_visible(False)

# plotting the average 100 days stock values from the database 
box5.set_title('Avg Microsoft stock values for the past 100 days (SQLite): ')
sql_data_text = 'open: {0:3.1f}, high: {1:3.1f}, low: {2:3.1f}, close: {3:3.1f}'.format(*sql_data)
box5.text(0.25,0.5, sql_data_text, fontsize=15, ha='left', va='top')
box5.axes.get_xaxis().set_visible(False)
box5.axes.get_yaxis().set_visible(False)

box6.imshow(img)
box6.axes.get_xaxis().set_visible(False)
box6.axes.get_yaxis().set_visible(False)

box7.axes.get_xaxis().set_visible(False)
box7.axes.get_yaxis().set_visible(False)

ani = animation.FuncAnimation(dash, animate, interval=65000)
ani3 = animation.FuncAnimation(dash, run_title, interval=65000)
ani2 = animation.FuncAnimation(dash, run, data_gen, interval=1000)

mng = plt.get_current_fig_manager()
mng.window.showMaximized()
plt.show()

