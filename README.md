# compta

## Installation

### Linux or Mac

cd to the project directory and run :

```
chmod +x install_scripts/install.sh
./install_scripts/install.sh
```

You might need to provide your sudo password at some time.

### Windows

Install Linux, then refer to previous section.

### Link to Google Drive

You wll need to create a Google Spreadsheet following the model "compta_template.xlsx".

One file per year, in each file you can have one sheet per month.
Those sheets must be named according to the french months names to be detected:
  * Janvier
  * Fevrier
  * Mars
  * Avril
  * Mai
  * Juin
  * Juillet
  * Août
  * Septembre
  * Octobre
  * Novembre
  * Décembre
  
Then, you will need to create a service account on GCP on a dedicated project with "Project Edit" rights, and activate the "Google Drive" API and "Google Sheets" API.

You can follow the tutorial here https://blog.coupler.io/python-to-google-sheets/#Connect_Python_to_Google_Sheets.

Watch out, it is a bit outdated and GCP web pages changed a bit.

Create and download the json credentials, you will need to provide it later.

## Usage

After having ran the install script, a new desktop should have appeared. Just click it to launch.
