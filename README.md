# OngoingIssues
Reads emails from Yodlee

The python script can be found here: https://github.com/Chetsama/OngoingIssues

This script reads through the inbox folder of the gmail account above and exports individual yodlee bank issues to a CSV file. The script reads each email individually and does not perform any deletion, as such it is generally a good idea to delete the older emails periodically. The script takes longer to run the more emails it must read, it will easily handle 1000 but it’s much faster if it only needs to read 300.
Formatting for Output File
1.	Sort Newest to Oldest on Column A
2.	Remove duplicates on Bank, Column B
3.	Use filter to select “na” cells on Column C
4.	Once Filtered, ensure Full Container, Column L, does not contain “Banking” or “Credit Cards”
5.	Delete current selection (ctrl+-)
6.	Remove Filter
7.	Filter on Country Region (Column J), select all regions other than US, UK and Canada
8.	Delete current selection (ctrl+-)
9.	Remove filter
10.	Filter on Error Code(Column F) for “No Value”
11.	Delete cells in F leaving them blank (delete)

At line 111 in the script, a list of “Broken Banks” is declared. These are banks that contain a hyphen in the bank name. This breaks the logic and results in some empty fields. Currently the list is as follows.

Virgin - Credit Cards (UK)
BMO - Online Banking (Canada) - Bank
The Co-operative Bank (new) (UK) - Credit Card
Best Buy - Credit Cards
Mechanics Bank- credit card

This list can be extended simply by adding the name of the bank within the code. The list format in python is relatively self-explanatory.
	 
This method only works for bank names with a single hyphen. If an issue does occur and a bank does not format properly, a “#N/A” is placed in column H under Issue. With these banks, go to outlook and search for the Bank name and manually fill missing fields using most recent email. For consistency use the Alternative Bank Name from Column M.
 
