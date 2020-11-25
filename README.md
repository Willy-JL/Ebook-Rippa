# PearsonRipper
Rip ebooks from Pearson into .pdf format

### Why?
As of November 2020 Pearson is still using Flash for their ebooks (Flash EOL is in December 2020) and this tool helps you get a copy of your ebooks before flash goes out of business.

### Requirements:
- [Python 3](https://www.python.org/downloads/)
- [Chrome](https://www.google.com/intl/en_us/chrome/)
- Selenium (`pip install selenium`)
- Selenium-Wire (`pip install selenium-wire`)

## How to use?
- Open `PearsonRipper.py` with python
- Log in to Pearson
- Open your ebook
- When the cover page is fully loaded press [Enter] on the script
- If you are starting the rip enter 0, if you are continuing where you left off put the number of the last .png file in /dump/ +1
- When the rip is completed either select all .png files in the /dump/ folder, right click > print > microsoft print to pdf > save your output pdf where you want, OR place `PngToPdf.py` in the rip folder and run it (this is much slower)
