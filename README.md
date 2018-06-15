# bank balance

## Simply check the balance of your USAA account.

You can read the code in this file to ensure that I am not collecting your credentials. I cannot vouch for the security or privacy policies of project dependencies, however. Use this script at your own risk.

This script offers a simple way to check the balance of your USAA account in the background. It stores your credentials locally in a transparent config.json file. It will also store your responses to security questions in the same file. This allows you to control and understand how your data is being used.

### dependencies
- selenium
- pync _(optional, but recommended)_

### problems

Since this script is dependent on Selenium, changes to the USAA website may break it. If you are experiencing problems, please create a new issue here on GitHub.

### options

When you use the script for the first time, you will input your credentials and choose how verbose the script should be.

Further customization is available for those who are comfortable with editing code. The __BALANCE_ELEMENT_SELECTOR__ variable allows you to change the account for which the script returns a balance by changing the CSS selector of the element it looks for.
