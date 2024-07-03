


<!-- ABOUT THE PROJECT -->
## About The Project
PDF tool to extract tables 

<!-- GETTING STARTED -->
## Getting Started


### Installation
### Conda Environment

To set up the project environment, create a Conda environment using the provided `environment.yml` file:

```bash
conda env create -f environment.yml
conda activate pdf_parser
```

### Setup

1. Get free API credentials at [https://si3.bcentral.cl/Siete/en/Siete/API?respuesta=](BANCO CENTRAL CHILE API)
   
2. Enter your credentials in credentials.txt in the project folder
   ```js
   USER
   PASSWORD
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage



<!-- ROADMAP -->
## File organization
```kotlin
LV_PROJECT/
│
├── data/
│   ├── industrydata/...
│   └── macrodata/...
│   
├── drivers/
│   └── driver1.exe
│ 
├── industry/
│   ├── html_parser.py
│   ├── industry_data.py
│   ├── main_data.py
│   ├── parse_xbrl.py
│   ├── pdf_parser.py
│   ├── scrapping.py
│   └── empresas.json
│
├── macro/
│   ├── get_data.py
│   ├── plots_data.py
│   └── serie.json
│
├── utils/
│   ├── cchc_preprocess.py
│   ├── download_data.py
│   ├── excel_downloads.py
│   └── json_utils.py
│  
├── scripts/
│   ├── reports_plots.py
│   ├── model2.h5
│   └── ...
│ 
├── .gitignore
├── README.md
├── credentials.txt
└── environment.yml
```


```kotlin
data/
├── industrydata/
│   ├── industry1/
│   │   ├── raw/
│   │   │   ├── html/...
│   │   │   ├── pdf_financials/...
│   │   │   ├── pdf_razonados/...
│   │   │   └── xbrl/...
│   │   │
│   │   └── results/
│   │       ├── excel/...
│   │       └── csv/...
│   │
│   └── industry2/...
│
└── macrodata/
    ├── excel/...
    └── plots/...
```


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>




